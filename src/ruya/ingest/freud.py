"""Freud, The Interpretation of Dreams (Brill 1913, Gutenberg #66048). Takvim: Hafta 7.

Sembol sözlüğü değil, "yöntem" katmanı: paragraf paragraf bölünür, sembol ataması
yalnızca açıkça bir sembolden söz eden paragraflara yapılır.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ruya.schemas import Madde


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    raise NotImplementedError("Hafta 7: ingest/freud.py (docs/08)")
