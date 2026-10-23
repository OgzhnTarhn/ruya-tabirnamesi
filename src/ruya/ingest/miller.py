r"""Miller, Ten Thousand Dreams Interpreted (Gutenberg #926) ayrıştırıcısı. Takvim: Hafta 2.

Gerçek veride görülenler (docs/02, bölüm 2):
- Asıl metin ``*** START/END OF THE PROJECT GUTENBERG EBOOK ***`` arasında;
  Gutenberg başlık ve dipnotları silinir (V5).
- ~1.540. satıra kadar önsöz ve kuram bölümü: madde değil, ayıklanır.
- 2.256 madde başlığı: ``^_[^_]+_\.(\[\d+\])?$`` (köşeli parantez dipnot işareti).
- ``entry_id`` başlığın satır numarasından türetilir: ``miller:018710``.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ruya.schemas import Madde


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    raise NotImplementedError("Hafta 2: ingest/miller.py (docs/08)")
