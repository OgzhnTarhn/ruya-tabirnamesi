"""Adım 3 · Getirme: symbol_id ile madde getirme ve sıralama (deterministik). Takvim: Hafta 4.

- Her sembol için her kaynaktan en fazla ``n`` madde (İG-22).
- ``gelenekler`` verilmişse yalnızca o geleneklerin maddeleri (İG-03).
- Sıralama: nitelik eşleşmesi → bağlam koşulu (Aşama 3) → başlıklı madde önce.
  Skora katkı yapan her şey ``Aday.gerekceler``'e yazılır (hata ayıklama sekmesi, İG-42).
- (Aşama 2) Bir sembolün maddesi n'den fazlaysa bge-reranker ile yeniden sıralama.
"""

from __future__ import annotations

from ruya.index.store import MaddeDeposu
from ruya.schemas import Baglam, Eslesme, Gelenek, Getirilenler


def retrieve(
    eslesmeler: list[Eslesme],
    depo: MaddeDeposu,
    baglam: Baglam | None = None,
    gelenekler: list[Gelenek] | None = None,
    n: int = 2,
) -> Getirilenler:
    """Eşlenen (symbol_id'si dolu) her sembol için sıralı aday listesi.
    Maddesi olmayan sembol için boş liste döner; sentez onu "bulunamadı" olarak yazar."""
    raise NotImplementedError("Hafta 4: pipeline/retrieve.py (docs/08)")
