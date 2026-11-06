"""Adım 1 · Sembol çıkarımı (LLM, yapılandırılmış JSON çıktı). Takvim: Hafta 4.

- ``response_format`` ile JSON şeması (``json_schema``, ``strict: true``; CikarimSonucu).
- Semboller yalın ve küçük harfle, **belirginlik sırasıyla** döner; run.py ilk
  ``en_fazla_sembol`` tanesini işler.
- Olumsuzlanan semboller ``olumsuz=True`` (İG-12); çok kelimeli semboller tek sembol (İG-13).
- Getirme çıkarımın sonucuna bağlı olduğu için çıkarım ve sentez ayrı çağrılardır.
- İstek ``istemci.mesaj(istek, ruya_icerir=True)`` ile gönderilir (rüya metni
  içerir; docs/03 bölüm 5.2).
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from ruya.config import MODEL_CIKARIM, SOHBET_EK_ALANLARI
from ruya.hatalar import YanitBozuk
from ruya.llm.client import LLMIstemcisi
from ruya.llm.talimatlar import talimat_oku
from ruya.schemas import CikarimSonucu, Kullanim, RuyaGirdisi

TALIMAT = "cikarim_v4"

# Modelin düşünme tokenları da bu sınıra dahildir.
EN_UZUN_CIKTI_TOKEN = 8000


def _istek_kur(girdi: RuyaGirdisi) -> dict[str, Any]:
    """OpenAI uyumlu sohbet gövdesi: sabit sistem talimatı başta, rüya metni sonda."""
    return {
        **SOHBET_EK_ALANLARI,
        "model": MODEL_CIKARIM,
        "max_tokens": EN_UZUN_CIKTI_TOKEN,
        "messages": [
            {"role": "system", "content": talimat_oku(TALIMAT)},
            {"role": "user", "content": girdi.metin},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "cikarim",
                "schema": CikarimSonucu.model_json_schema(),
                "strict": True,
            },
        },
    }


def extract(girdi: RuyaGirdisi, istemci: LLMIstemcisi) -> tuple[CikarimSonucu, Kullanim]:
    """Rüya metninden sembolleri çıkarır; sonucu ve çağrının kullanımını döndürür."""
    yanit = istemci.mesaj(_istek_kur(girdi), ruya_icerir=True)
    try:
        cikarim = CikarimSonucu.model_validate(yanit.json())
    except ValidationError as hata:
        raise YanitBozuk(f"Çıkarım yanıtı şemaya uymuyor: {hata}") from hata
    return cikarim, yanit.kullanim
