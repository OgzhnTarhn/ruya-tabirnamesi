"""İbn Sîrîn'e atfedilen Muntahab (OpenITI, Shamela0021615). Takvim: Hafta 8.

Bab (konu) düzeninde. Her kayda ``atif_notu`` olarak kaynaklar.OPENITI_ATIF_NOTU yazılır
(İG-34, docs/07 D6).
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ruya.schemas import Madde


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    raise NotImplementedError("Hafta 8: ingest/ibn_sirin.py (docs/08)")
