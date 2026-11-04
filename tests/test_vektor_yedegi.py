"""Vektör yedeği testleri: ``HibritVektorArayici`` (docs/13-hibrit-getirme.md).

Sahte indeks ve sahte LLM istemcisi ile ağa çıkmadan çalışır.
"""

import pytest

from ruya.hatalar import LLMHatasi
from ruya.pipeline.hibrit import HibritVektorArayici

# --- Yardımcılar ------------------------------------------------------------


class SahteIstemci:
    """LLMIstemcisi'nin yalnızca ``gom`` yöntemi; çağrıları kaydeder."""

    def __init__(self, *, gom_hatasi: bool = False) -> None:
        self._gom_hatasi = gom_hatasi
        self.gom_cagrilari: list[tuple[list[str], bool]] = []

    def gom(self, metinler: list[str], ruya_icerir: bool = False) -> list[list[float]]:
        self.gom_cagrilari.append((list(metinler), ruya_icerir))
        if self._gom_hatasi:
            raise LLMHatasi("gömme geçidi hatası", durum=500)
        return [[0.1, 0.2, 0.3] for _ in metinler]


class SahteIndeks:
    """HibritIndeks'in yalnızca ``en_yakin_semboller_vektorle`` yöntemi."""

    def __init__(self, sonuclar: list[tuple[str, float]] | None = None) -> None:
        self.sonuclar = sonuclar if sonuclar is not None else [("yilan", 0.9), ("su", 0.5)]
        self.cagrilar: list[tuple[list[float], int]] = []

    def en_yakin_semboller_vektorle(self, sorgu, k: int = 3) -> list[tuple[str, float]]:
        self.cagrilar.append(([float(deger) for deger in sorgu], k))
        return list(self.sonuclar[:k])


# --- en_yakin_semboller -----------------------------------------------------


def test_ifade_gomulur_ve_vektorle_aranir():
    istemci = SahteIstemci()
    indeks = SahteIndeks()
    arayici = HibritVektorArayici(indeks, istemci)

    arayici.en_yakin_semboller("rüyada yılan görmek", k=2)

    assert istemci.gom_cagrilari == [(["rüyada yılan görmek"], True)]
    assert len(indeks.cagrilar) == 1
    vektor, k = indeks.cagrilar[0]
    assert vektor == pytest.approx([0.1, 0.2, 0.3])
    assert k == 2


def test_indeksin_sonucu_aynen_doner():
    istemci = SahteIstemci()
    indeks = SahteIndeks([("yilan", 0.9), ("su", 0.5)])
    arayici = HibritVektorArayici(indeks, istemci)

    sonuc = arayici.en_yakin_semboller("yılan", k=2)

    assert sonuc == [("yilan", 0.9), ("su", 0.5)]


def test_varsayilan_k_uc():
    istemci = SahteIstemci()
    indeks = SahteIndeks()
    arayici = HibritVektorArayici(indeks, istemci)

    arayici.en_yakin_semboller("yılan")

    assert indeks.cagrilar[0][1] == 3


def test_gom_hatasinda_bos_liste_doner():
    istemci = SahteIstemci(gom_hatasi=True)
    indeks = SahteIndeks()
    arayici = HibritVektorArayici(indeks, istemci)

    sonuc = arayici.en_yakin_semboller("yılan", k=3)

    assert sonuc == []
    assert indeks.cagrilar == []
