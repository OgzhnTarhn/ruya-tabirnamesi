"""Adım 2 · Eşleme: sembol → symbol_id (deterministik). Takvim: Hafta 4.

Sıra (docs/03, Adım 2):
1. text.turkce.normallestir
2. Varyant tablosunda doğrudan arama → yontem="birebir"
3. text.turkce.kokler ile kök bulup yeniden arama → yontem="kok"
4. (Aşama 2) VektorArayici; benzerlik ``esik`` altındaysa → yontem="yok"
"""

from __future__ import annotations

from ruya.index.store import VektorArayici
from ruya.schemas import Eslesme, Sembol

VARSAYILAN_ESIK = 0.80  # Hafta 6'da test setiyle ayarlanacak


def map_symbols(
    semboller: list[Sembol],
    varyantlar: dict[str, str],
    vektor: VektorArayici | None = None,
    esik: float = VARSAYILAN_ESIK,
) -> list[Eslesme]:
    """Her sembol için tam olarak bir Eslesme döndürür (eşleşmeyenler yontem="yok")."""
    raise NotImplementedError("Hafta 4: pipeline/map.py (docs/08)")
