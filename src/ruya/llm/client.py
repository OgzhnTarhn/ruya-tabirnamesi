"""EVREN LLM geçidi (OpenAI uyumlu /v1/chat/completions) sarmalayıcısı.

Disk önbelleği, yeniden deneme ve ölçüm burada toplanır (docs/03, bölüm 5.2).
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from ruya import config
from ruya.config import FIYATLAR, Ayarlar, ayarlar
from ruya.hatalar import (
    ApiAnahtariYok,
    LLMHatasi,
    ModelReddetti,
    RuyaHatasi,
    YanitBozuk,
    YanitKesildi,
)
from ruya.schemas import Kullanim

YENIDEN_DENEME_SAYISI = 4
YENIDEN_DENENEN_DURUMLAR = frozenset({429, 502, 503, 504})
EN_UZUN_RETRY_AFTER = 30.0  # üstünde günlük kota sayılır, yeniden denenmez
ISLENIYOR_BEKLEME_SN = 20.0  # 409: geçit isteği hâlâ işliyor, bu kadar bekle
ISLENIYOR_EN_FAZLA = 30  # 409 yoklamalarının üst sınırı (YENIDEN_DENEME_SAYISI'ndan bağımsız)


def onbellek_anahtari(istek: dict[str, Any]) -> str:
    """İstek gövdesinin SHA-256 özeti. Anahtarların sırası sonucu değiştirmez."""
    kanonik = json.dumps(istek, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(kanonik.encode("utf-8")).hexdigest()


def maliyet_hesapla(
    model: str,
    girdi_token: int,
    cikti_token: int,
    onbellek_okuma_token: int = 0,
) -> float:
    """Bir çağrının tutarı. ``girdi_token`` önbelleğe girmemiş istem tokenlarıdır.

    Model fiyat tablosunda yoksa KeyError verir.
    """
    fiyat = FIYATLAR[model]
    okuma_fiyati = fiyat.girdi if fiyat.onbellek_okuma is None else fiyat.onbellek_okuma
    return (
        girdi_token * fiyat.girdi + cikti_token * fiyat.cikti + onbellek_okuma_token * okuma_fiyati
    ) / 1_000_000


def _kullanim(govde: dict[str, Any], istek: dict[str, Any], disk_onbelleginden: bool) -> Kullanim:
    """Yanıt gövdesinden Kullanim üretir; iki yol da (ağ, önbellek) bunu kullanır."""
    kullanim = govde.get("usage") or {}
    ayrinti = kullanim.get("prompt_tokens_details") or {}
    onbellek = ayrinti.get("cached_tokens") or 0
    girdi = (kullanim.get("prompt_tokens") or 0) - onbellek
    cikti = kullanim.get("completion_tokens") or 0
    model = govde.get("model") or istek["model"]
    if model not in FIYATLAR:
        # Geçit "sağlayıcı/model" gibi ön ekli bir ad döndürebilir; fiyat isteğin modelinden.
        model = istek["model"]
    maliyet = 0.0 if disk_onbelleginden else maliyet_hesapla(model, girdi, cikti, onbellek)
    return Kullanim(
        model=model,
        girdi_token=girdi,
        cikti_token=cikti,
        onbellek_okuma_token=onbellek,
        maliyet_usd=maliyet,
        disk_onbelleginden=disk_onbelleginden,
    )


def _hata_mesaji(yanit: httpx.Response) -> str:
    """Gövdedeki ``error.message``; yoksa metnin ilk 300 karakteri."""
    try:
        govde = yanit.json()
    except ValueError:
        govde = None
    if isinstance(govde, dict):
        hata = govde.get("error")
        if isinstance(hata, dict) and hata.get("message"):
            return str(hata["message"])
    return yanit.text[:300]


def _retry_after(yanit: httpx.Response) -> float | None:
    """Retry-After başlığı saniye cinsinden; yoksa ya da okunamıyorsa None."""
    deger = yanit.headers.get("Retry-After")
    if deger is None:
        return None
    try:
        return float(deger)
    except ValueError:
        return None


@dataclass
class LLMYaniti:
    """Bir LLM yanıtı ve kullanım bilgisi. ``mesaj`` geçidin döndürdüğü JSON gövdesidir."""

    mesaj: dict[str, Any]
    kullanim: Kullanim

    @property
    def icerik(self) -> str:
        """İlk seçimin metni."""
        return self.mesaj["choices"][0]["message"].get("content") or ""

    def json(self) -> Any:
        """İçeriği JSON olarak ayrıştırır; bozuksa YanitBozuk verir."""
        try:
            return json.loads(self.icerik)
        except json.JSONDecodeError as hata:
            raise YanitBozuk(f"Yanıt JSON değil: {self.icerik[:200]}") from hata


class LLMIstemcisi:
    """Bütün LLM çağrılarının geçtiği tek kapı."""

    def __init__(
        self,
        ayar: Ayarlar | None = None,
        http: httpx.Client | None = None,
        bekle: Callable[[float], None] = time.sleep,
    ) -> None:
        self.ayar = ayar or ayarlar()
        self._http = http
        self.bekle = bekle
        self._kilit = threading.Lock()

    def _istemci(self) -> httpx.Client:
        """HTTP istemcisini ilk çağrıda kurar (testler kendi istemcisini verir)."""
        with self._kilit:
            if self._http is None:
                self._http = httpx.Client(timeout=httpx.Timeout(900.0, connect=10.0))
            return self._http

    def mesaj(self, istek: dict[str, Any], ruya_icerir: bool = False) -> LLMYaniti:
        """Sohbet tamamlama çağrısı (önbellekli). Hafta 4.

        ``ruya_icerir`` True ise disk önbelleği yalnızca ``self.ayar.sorgu_onbellegi``
        True olduğunda okunur/yazılır; böylece rüya geçmişi kapalıyken rüyalar
        data/ altında birikmez (docs/03 bölüm 5.2). False ise yalnızca
        ``self.ayar.llm_cache`` geçerlidir.
        """
        onbellek = self.ayar.llm_cache and (not ruya_icerir or self.ayar.sorgu_onbellegi)
        yol = self.ayar.llm_onbellek_klasoru / f"{onbellek_anahtari(istek)}.json"
        if onbellek and yol.exists():
            govde = json.loads(yol.read_text(encoding="utf-8"))
            return LLMYaniti(govde, _kullanim(govde, istek, disk_onbelleginden=True))

        anahtar = os.environ.get(config.LLM_ANAHTAR_DEGISKENI, "").strip()
        if not anahtar:
            raise ApiAnahtariYok(
                f"{config.LLM_ANAHTAR_DEGISKENI} tanımlı değil; anahtarı ortam değişkenine "
                "ekleyin (docs/10, adım 1)."
            )

        govde = self._gonder(istek, anahtar)
        secim = (govde.get("choices") or [{}])[0]
        if secim.get("finish_reason") == "length":
            raise YanitKesildi("Yanıt max_tokens sınırında kesildi; isteği küçültün.")
        if (secim.get("message") or {}).get("refusal"):
            raise ModelReddetti("Model isteği reddetti.")
        if onbellek:
            self._onbellege_yaz(yol, govde)
        return LLMYaniti(govde, _kullanim(govde, istek, disk_onbelleginden=False))

    def _gonder(self, istek: dict[str, Any], anahtar: str) -> dict[str, Any]:
        """İsteği yeniden denemelerle gönderir; başarılı gövdeyi döndürür."""
        basliklar = {
            "Authorization": f"Bearer {anahtar}",
            "Idempotency-Key": str(uuid.uuid4()),
        }
        adres = f"{config.LLM_ADRESI}/v1/chat/completions"
        deneme = 0
        isleniyor = 0  # 409 yoklamalarının kendi sayacı
        while deneme < YENIDEN_DENEME_SAYISI:
            son_deneme = deneme == YENIDEN_DENEME_SAYISI - 1
            try:
                yanit = self._istemci().post(adres, json=istek, headers=basliklar)
            except httpx.ReadTimeout as hata:
                if isleniyor:
                    # 409 sonrası okuma zaman aşımı: geçit isteği hâlâ işliyor sayılır.
                    isleniyor += 1
                    if isleniyor > ISLENIYOR_EN_FAZLA:
                        raise LLMHatasi(
                            f"EVREN isteği hâlâ işliyor (409): {type(hata).__name__}", durum=409
                        ) from hata
                    self.bekle(ISLENIYOR_BEKLEME_SN)
                    continue
                # Bağlantı kurulamadı, koptu ya da zaman aşımı. Idempotency-Key aynı kaldığı için
                # geçit isteği iki kez çalıştırmaz; yeniden denemek güvenli.
                if son_deneme:
                    raise LLMHatasi(f"EVREN geçidine ulaşılamadı: {type(hata).__name__}") from hata
                self.bekle(min(8.0, 0.5 * 2**deneme))
                deneme += 1
                continue
            except httpx.TransportError as hata:
                # Bağlantı kurulamadı, koptu ya da zaman aşımı. Idempotency-Key aynı kaldığı için
                # geçit isteği iki kez çalıştırmaz; yeniden denemek güvenli.
                if son_deneme:
                    raise LLMHatasi(f"EVREN geçidine ulaşılamadı: {type(hata).__name__}") from hata
                self.bekle(min(8.0, 0.5 * 2**deneme))
                deneme += 1
                continue

            if yanit.status_code == 200:
                try:
                    return yanit.json()
                except ValueError as hata:
                    raise LLMHatasi("EVREN yanıtı JSON değil", durum=200) from hata

            if yanit.status_code == 409:
                # Özgün istek hâlâ işleniyor: aynı Idempotency-Key ile bekleyip yeniden gönder.
                isleniyor += 1
                if isleniyor > ISLENIYOR_EN_FAZLA:
                    raise LLMHatasi(f"EVREN 409: {_hata_mesaji(yanit)}", durum=409)
                self.bekle(ISLENIYOR_BEKLEME_SN)
                continue

            if yanit.status_code not in YENIDEN_DENENEN_DURUMLAR:
                raise LLMHatasi(
                    f"EVREN {yanit.status_code}: {_hata_mesaji(yanit)}", durum=yanit.status_code
                )

            bekleme = _retry_after(yanit)
            if bekleme is not None and bekleme > EN_UZUN_RETRY_AFTER:
                # Günlük kota: beklemek anlamsız.
                raise LLMHatasi(
                    f"EVREN {yanit.status_code}: {_hata_mesaji(yanit)}", durum=yanit.status_code
                )
            if son_deneme:
                raise LLMHatasi(
                    f"EVREN {yanit.status_code}: {_hata_mesaji(yanit)}", durum=yanit.status_code
                )
            self.bekle(bekleme if bekleme is not None else min(8.0, 0.5 * 2**deneme))
            deneme += 1
        raise AssertionError("ulaşılamaz")  # döngü her yolda döner ya da hata verir

    def _onbellege_yaz(self, yol: Path, govde: dict[str, Any]) -> None:
        """Gövdeyi geçici dosyaya yazıp hedefe taşır; yarım dosya kalmaz."""
        yol.parent.mkdir(parents=True, exist_ok=True)
        tanitici, gecici = tempfile.mkstemp(dir=yol.parent, suffix=".json")
        try:
            with os.fdopen(tanitici, "w", encoding="utf-8") as dosya:
                json.dump(govde, dosya, ensure_ascii=False)
            os.replace(gecici, yol)
        except BaseException:
            Path(gecici).unlink(missing_ok=True)
            raise

    def toplu(
        self, istekler: dict[str, dict[str, Any]], eszamanli: int = 4
    ) -> dict[str, LLMYaniti | RuyaHatasi]:
        """İstekleri eşzamanlı gönderir; Batch API'nin yerini alır.

        Her istek ``mesaj`` üzerinden geçtiği için önbellek işi yeniden başlatılabilir kılar:
        yarıda kesilen iş önbellek sayesinde kaldığı yerden devam eder. Projeye özgü hatalar
        (``RuyaHatasi``) o anahtarın değeri olarak döner; diğer hatalar yükselir.
        """

        def calistir(istek: dict[str, Any]) -> LLMYaniti | RuyaHatasi:
            try:
                return self.mesaj(istek)
            except RuyaHatasi as hata:
                return hata

        with ThreadPoolExecutor(max_workers=eszamanli) as havuz:
            sonuclar = list(havuz.map(calistir, istekler.values()))
        return dict(zip(istekler, sonuclar, strict=True))
