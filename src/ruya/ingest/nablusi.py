"""Nablusi, Ta'tîrü'l-enâm (OpenITI mARkdown) ayrıştırıcısı. Takvim: Hafta 2.

Gerçek veride görülenler (docs/02, bölüm 2):
- ``#META#`` satırları künye; ``### | باب …`` satırları 29 bölüm (bab).
- Her paragraf ``# - (`` ile başlar: ~2.400 başlıklı madde, ~3.300 alt paragraf
  (``(ومن رأى)`` gibi). Alt paragraflar ``ust_madde_id`` ile başlığa bağlanır;
  hangi sembole ait oldukları ``enrich/assign_symbols.py`` ile bulunur.
- Temizlenecek gürültü: ``~~`` satır devamları, ``# PageV01P009`` sayfa işaretleri
  (``konum.sayfa`` için saklanır), ``ms008`` kilometre taşları.
- ``entry_id`` paragrafın başladığı satır numarasından türetilir: ``nablusi:004310``.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ruya.schemas import Madde


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    raise NotImplementedError("Hafta 2: ingest/nablusi.py (docs/08)")
