"""Madde deposu arayüzü.

Boru hattı somut sınıfları değil bu arayüzü bilir; böylece MVP'de bellekteki depo,
Aşama 2'de Chroma, testlerde sahte (fake) bir depo kullanılabilir.
"""

from __future__ import annotations

from typing import Protocol

from ruya.schemas import Madde


class MaddeDeposu(Protocol):
    def sembolun_maddeleri(self, symbol_id: str) -> list[Madde]:
        """Bir sembole atanmış bütün maddeler (sırasız)."""
        ...

    def madde(self, entry_id: str) -> Madde:
        """Tek bir madde; atıf tıklanınca aslı ve çevirisi gösterilir (İG-41)."""
        ...


class BellekDeposu:
    """entries.jsonl'den bellekte kurulan depo (MVP). Takvim: Hafta 4."""

    def __init__(self, maddeler: list[Madde]) -> None:
        self._maddeler: dict[str, Madde] = {m.entry_id: m for m in maddeler}
        self._sembol_indeksi: dict[str, list[Madde]] = {}
        for madde in maddeler:
            for symbol_id in madde.symbol_ids:
                self._sembol_indeksi.setdefault(symbol_id, []).append(madde)

    def sembolun_maddeleri(self, symbol_id: str) -> list[Madde]:
        return list(self._sembol_indeksi.get(symbol_id, []))

    def madde(self, entry_id: str) -> Madde:
        return self._maddeler[entry_id]
