"""Arapça ve İngilizce maddelerin Türkçe çevirisi (LLM). Takvim: Hafta 3.

Aslı ``metin_asli``'da korunur; çeviri ``metin_tr``'ye, bilgisi ``ceviri``'ye yazılır.
Yönergeler: docs/02, bölüm 5 · terimler: docs/terimler.md · talimat: prompts/ceviri_v1.md
"""

from __future__ import annotations

from typing import Any

from ruya.llm.client import LLMYaniti
from ruya.schemas import Madde

TALIMAT = "ceviri_v1"


def istekler(maddeler: list[Madde]) -> dict[str, dict[str, Any]]:
    raise NotImplementedError("Hafta 3: enrich/translate.py (docs/08)")


def sonuclari_uygula(maddeler: list[Madde], yanitlar: dict[str, LLMYaniti]) -> list[Madde]:
    raise NotImplementedError("Hafta 3: enrich/translate.py (docs/08)")
