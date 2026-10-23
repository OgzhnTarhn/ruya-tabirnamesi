"""Claude API sarmalayıcısı: disk önbelleği, maliyet hesabı, hata yönetimi (docs/03, bölüm 5.2).

Takvim: Hafta 4. Önbellek anahtarı ve maliyet hesabı şimdiden hazır; çünkü bunlar
sözleşmenin parçası (önbellek dosyalarının adı ve SorguKaydi'ndaki maliyet bunlara bağlı).

Uygulanırken uyulacaklar:
- İstek gövdesi bir ``dict`` olarak kurulur (model, system, messages, max_tokens,
  output_config…). Önbellek anahtarı bu gövdeden üretilir.
- Önbellek: Drive'da ``cache/llm/<anahtar>.json``; istek başına bir dosya, SQLite yok.
  ``Ayarlar.llm_cache`` False ise atlanır.
- Opus 5.5: düşünme kapatılamaz, ``output_config.effort`` açıkça verilir;
  ``temperature``/``top_p``/``top_k`` gönderilmez (400 verir).
- Reddetmeye karşı sunucu tarafı yedek model: ``fallbacks="default"`` ve
  ``server-side-fallback-2026-07-01`` beta başlığı.
- Yanıtta önce ``stop_reason`` okunur: ``refusal`` → ModelReddetti,
  ``max_tokens`` → YanitKesildi.
- Hatalar sınıf sınıf yakalanır; 429 ve 5xx'i SDK kendisi yeniden dener, 400 tekrarlanmaz.
- Prompt önbelleğinin çalıştığı ``usage.cache_read_input_tokens`` ile doğrulanır.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from ruya.config import BATCH_INDIRIMI, FIYATLAR, Ayarlar, ayarlar
from ruya.schemas import Kullanim

ONBELLEK_YAZMA_CARPANI = 1.25  # 5 dakikalık prompt önbelleğine yazma, girdi fiyatının 1,25 katı


def onbellek_anahtari(istek: dict[str, Any]) -> str:
    """İstek gövdesinin SHA-256 özeti. Anahtarların sırası sonucu değiştirmez."""
    kanonik = json.dumps(istek, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(kanonik.encode("utf-8")).hexdigest()


def maliyet_hesapla(
    model: str,
    girdi_token: int,
    cikti_token: int,
    onbellek_okuma_token: int = 0,
    onbellek_yazma_token: int = 0,
    batch: bool = False,
) -> float:
    """Bir çağrının dolar cinsinden tutarı. Model fiyat tablosunda yoksa KeyError verir."""
    fiyat = FIYATLAR[model]
    okuma_fiyati = fiyat.girdi if fiyat.onbellek_okuma is None else fiyat.onbellek_okuma
    tutar = (
        girdi_token * fiyat.girdi
        + cikti_token * fiyat.cikti
        + onbellek_okuma_token * okuma_fiyati
        + onbellek_yazma_token * fiyat.girdi * ONBELLEK_YAZMA_CARPANI
    ) / 1_000_000
    return tutar * BATCH_INDIRIMI if batch else tutar


@dataclass
class LLMYaniti:
    """Bir Claude yanıtı ve kullanım bilgisi. ``mesaj``, SDK yanıtının ``model_dump()`` hâlidir;
    disk önbelleğine olduğu gibi yazılabilsin diye sözlük olarak tutulur."""

    mesaj: dict[str, Any]
    kullanim: Kullanim


class LLMIstemcisi:
    """Bütün Claude çağrılarının geçtiği tek kapı."""

    def __init__(self, ayar: Ayarlar | None = None) -> None:
        self.ayar = ayar or ayarlar()
        self._sdk: Any = None  # anthropic.Anthropic; ilk çağrıda kurulur

    def mesaj(self, istek: dict[str, Any]) -> LLMYaniti:
        """Messages API çağrısı (önbellekli). Hafta 4."""
        raise NotImplementedError("Hafta 4: llm/client.py (docs/08)")

    def batch_gonder(self, istekler: dict[str, dict[str, Any]], etiket: str) -> str:
        """{custom_id: istek} sözlüğünü Message Batches API'ye gönderir, batch kimliğini
        Drive'da ``cache/batch/<etiket>.json`` dosyasına yazar ve döndürür. Hafta 3."""
        raise NotImplementedError("Hafta 3: enrich/translate.py ile birlikte (docs/08)")

    def batch_sonuclari(self, batch_id: str) -> dict[str, LLMYaniti]:
        """Bitmiş bir batch'in sonuçlarını {custom_id: yanıt} olarak döndürür.
        Sonuçlar sırasız gelir; her zaman custom_id ile eşlenir. Hafta 3."""
        raise NotImplementedError("Hafta 3: enrich/translate.py ile birlikte (docs/08)")
