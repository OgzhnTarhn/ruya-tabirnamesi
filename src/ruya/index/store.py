"""Madde deposu ve vektör arayıcı arayüzleri.

Boru hattı somut sınıfları değil bu arayüzleri bilir; böylece MVP'de bellekteki depo,
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


class VektorArayici(Protocol):
    def en_yakin_semboller(self, ifade: str, k: int = 3) -> list[tuple[str, float]]:
        """Sözlükte bulunamayan bir ifade için en yakın sembolleri (symbol_id, benzerlik)
        olarak döndürür, benzerliği yüksekten düşüğe (İG-21, Aşama 2)."""
        ...


class BellekDeposu:
    """entries.jsonl'den bellekte kurulan depo (MVP). Takvim: Hafta 4."""

    def __init__(self, maddeler: list[Madde]) -> None:
        raise NotImplementedError("Hafta 4: pipeline/retrieve.py ile birlikte (docs/08)")

    def sembolun_maddeleri(self, symbol_id: str) -> list[Madde]:
        raise NotImplementedError

    def madde(self, entry_id: str) -> Madde:
        raise NotImplementedError
