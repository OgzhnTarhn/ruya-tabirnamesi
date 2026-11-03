"""Bağlamlı parçalara ayırma (docs/13-hibrit-getirme.md, bölüm 3).

Her madde, en çok 1.000 karakterlik örtüşen pencerelere bölünür (150 karakter
örtüşme). Her parça, arama için künye önekini taşır::

    eser · yazar. Sembol: … Bölüm: …
    <pencere metni>

Önek LLM ile değil, maddenin künyesinden ve üst maddesinden kodla kurulur. Alt
paragraf, üst maddenin sembolünü miras alır; kendi sembolü varsa o tercih edilir.
Önek yalnızca arama içindir; atıf ve alıntı doğrulaması yine ``metin_tr`` üzerindedir.

Yalnızca standart kütüphane ve ``ruya.schemas`` kullanılır.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ruya.schemas import Madde

PENCERE = 1000
ORTUSME = 150


@dataclass(frozen=True)
class Parca:
    """Bir maddenin bağlamlı penceresi: arama ve atıf birimi."""

    parca_id: str  # "<entry_id>#<sıra>", ör. nablusi:000001#0
    entry_id: str
    metin: str  # pencerenin ham metni (metin_tr'den)
    baglamli_metin: str  # künye öneki + "\n" + metin


def parcala(maddeler: Iterable[Madde]) -> list[Parca]:
    """Maddeleri sırayı koruyarak bağlamlı parçalara böler.

    ``metin_tr`` boş ya da None olan maddeler atlanır.
    """
    maddeler = list(maddeler)
    ust_maddeler = {m.entry_id: m for m in maddeler}

    parcalar: list[Parca] = []
    for madde in maddeler:
        metin = madde.metin_tr
        if not metin:
            continue
        onek = _onek(madde, ust_maddeler)
        for sira, pencere in enumerate(_pencereler(metin)):
            parcalar.append(
                Parca(
                    parca_id=f"{madde.entry_id}#{sira}",
                    entry_id=madde.entry_id,
                    metin=pencere,
                    baglamli_metin=f"{onek}\n{pencere}",
                )
            )
    return parcalar


def _onek(madde: Madde, ust_maddeler: dict[str, Madde]) -> str:
    """Künye öneki: cümleler yalnızca veri varsa eklenir."""
    metin = f"{madde.eser} · {madde.yazar}."
    sembol = _sembol(madde, ust_maddeler)
    if sembol is not None:
        metin += f" Sembol: {sembol}."
    bab = madde.konum.bab
    if bab is not None:
        metin += f" Bölüm: {bab}."
    return metin


def _sembol(madde: Madde, ust_maddeler: dict[str, Madde]) -> str | None:
    """Kendi sembolü, yoksa üst maddenin sembolü, yoksa alt paragrafın asıl başlığı."""
    if madde.sembol_tr is not None:
        return madde.sembol_tr
    if madde.ust_madde_id is None:
        return None
    ust = ust_maddeler.get(madde.ust_madde_id)
    if ust is not None and ust.sembol_tr is not None:
        return ust.sembol_tr
    return madde.baslik_asli


def _pencereler(metin: str) -> list[str]:
    """Metni en çok ``PENCERE`` karakterlik, ``ORTUSME`` kadar örtüşen pencerelere böler.

    Pencere sonu mümkünse boşluktan kesilir; boşluk yoksa pencere düz kesilir.
    Her adımda en az bir karakter ilerlenir, böylece boşluksuz metinde sonsuz
    döngüye girilmez.
    """
    pencereler: list[str] = []
    bas = 0
    while bas < len(metin):
        son = min(bas + PENCERE, len(metin))
        if son < len(metin):
            kesim = metin.rfind(" ", bas, son)
            if kesim > bas:
                son = kesim + 1  # boşluk parçanın sonunda kalsın
        pencereler.append(metin[bas:son])
        if son >= len(metin):
            break
        bas = max(son - ORTUSME, bas + 1)
    return pencereler
