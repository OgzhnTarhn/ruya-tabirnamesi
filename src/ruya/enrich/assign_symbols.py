"""Alt paragraflara ve başlıklı maddelere ``symbol_ids`` atama (LLM). Takvim: Hafta 3.

Yalnızca sözlükte ``gozden_gecirildi: true`` olan semboller atanabilir. Sözlükte olmayan
ama sık geçen semboller ayrı bir öneri listesine yazılır (bkz. docs/12, sembol yaşam döngüsü).
Denemedeki doğruluk %80'in altındaysa R2 devreye girer.
"""

from __future__ import annotations

from typing import Any

from ruya.llm.client import LLMYaniti
from ruya.schemas import Madde, SymbolKaydi

TALIMAT = "sembol_atama_v1"


def istekler(maddeler: list[Madde], sozluk: dict[str, SymbolKaydi]) -> dict[str, dict[str, Any]]:
    raise NotImplementedError("Hafta 3: enrich/assign_symbols.py (docs/08)")


def sonuclari_uygula(maddeler: list[Madde], yanitlar: dict[str, LLMYaniti]) -> list[Madde]:
    raise NotImplementedError("Hafta 3: enrich/assign_symbols.py (docs/08)")
