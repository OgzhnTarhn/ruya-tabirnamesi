"""Koşul ayrıştırma: ``kosullar``, ``yontem`` ve ``kapsam`` alanları (LLM). Takvim: Hafta 8.

Koşul türleri ve değerleri: docs/05, Katman 3 ve 4. 20 madde elle kontrol edilir.
"""

from __future__ import annotations

from typing import Any

from ruya.llm.client import LLMYaniti
from ruya.schemas import Madde

TALIMAT = "kosul_v1"


def batch_istekleri(maddeler: list[Madde]) -> dict[str, dict[str, Any]]:
    raise NotImplementedError("Hafta 8: enrich/conditions.py (docs/08)")


def sonuclari_uygula(maddeler: list[Madde], yanitlar: dict[str, LLMYaniti]) -> list[Madde]:
    raise NotImplementedError("Hafta 8: enrich/conditions.py (docs/08)")
