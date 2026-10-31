"""EVREN LLM geçidi (OpenAI uyumlu /v1/chat/completions) sarmalayıcısı.

Disk önbelleği, yeniden deneme ve ölçüm burada toplanır (docs/03, bölüm 5.2).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from ruya.config import FIYATLAR, Ayarlar, ayarlar
from ruya.schemas import Kullanim


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


@dataclass
class LLMYaniti:
    """Bir LLM yanıtı ve kullanım bilgisi. ``mesaj`` geçidin döndürdüğü JSON gövdesidir."""

    mesaj: dict[str, Any]
    kullanim: Kullanim


class LLMIstemcisi:
    """Bütün LLM çağrılarının geçtiği tek kapı."""

    def __init__(self, ayar: Ayarlar | None = None) -> None:
        self.ayar = ayar or ayarlar()

    def mesaj(self, istek: dict[str, Any], ruya_icerir: bool = False) -> LLMYaniti:
        """Sohbet tamamlama çağrısı (önbellekli). Hafta 4.

        ``ruya_icerir`` True ise disk önbelleği yalnızca ``self.ayar.sorgu_onbellegi``
        True olduğunda okunur/yazılır; böylece rüya geçmişi kapalıyken rüyalar
        data/ altında birikmez (docs/03 bölüm 5.2). False ise yalnızca
        ``self.ayar.llm_cache`` geçerlidir.
        """
        raise NotImplementedError("Hafta 4: llm/client.py (docs/08)")
