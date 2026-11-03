"""Bağlamlı parçalara ayırma birim testleri (docs/13, bölüm 3).

`ruya.index.parcalar`: her madde, en çok 1.000 karakterlik örtüşen pencerelere
bölünür; her parça künye önekini (`eser · yazar. Sembol: … Bölüm: …`) taşır.
"""

import itertools
from dataclasses import FrozenInstanceError

import pytest

from ruya.index.parcalar import Parca, parcala
from ruya.schemas import Madde

PENCERE = 1000
ORTUSME = 150


def _madde(
    entry_id: str,
    *,
    metin_tr: str | None = None,
    eser: str = "Test Eseri",
    yazar: str = "Test Yazarı",
    sembol_tr: str | None = None,
    baslik_asli: str | None = None,
    ust_madde_id: str | None = None,
    bab: str | None = None,
) -> Madde:
    """Testte kullanılacak en küçük geçerli Madde."""
    return Madde(
        entry_id=entry_id,
        kaynak=entry_id.split(":")[0],
        eser=eser,
        yazar=yazar,
        gelenek="islami_klasik",
        dil="tr",
        lisans="PD",
        konum={"satir": 1, "bab": bab},
        baslik_asli=baslik_asli,
        sembol_tr=sembol_tr,
        ust_madde_id=ust_madde_id,
        metin_asli="(asıl metin)",
        metin_tr=metin_tr,
    )


def _onek(
    eser: str = "Test Eseri",
    yazar: str = "Test Yazarı",
    sembol: str | None = None,
    bab: str | None = None,
) -> str:
    """Beklenen künye öneki: cümleler yalnızca veri varsa eklenir."""
    metin = f"{eser} · {yazar}."
    if sembol is not None:
        metin += f" Sembol: {sembol}."
    if bab is not None:
        metin += f" Bölüm: {bab}."
    return metin


def _pencereler(parcalar: list[Parca], tam_metin: str) -> list[tuple[int, int]]:
    """Parçaların tam metindeki (başlangıç, bitiş) aralıkları."""
    araliklar = []
    for parca in parcalar:
        bas = tam_metin.find(parca.metin)
        assert bas != -1, f"parça metnin içinde bulunamadı: {parca.metin[:40]!r}"
        araliklar.append((bas, bas + len(parca.metin)))
    return araliklar


# --- Parça nesnesi ----------------------------------------------------------


def test_parca_dondurulmus_veri_sinifidir():
    parca = Parca(
        parca_id="nablusi:000001#0",
        entry_id="nablusi:000001",
        metin="yılan görmek",
        baglamli_metin="Test Eseri · Test Yazarı.\nyılan görmek",
    )

    with pytest.raises(FrozenInstanceError):
        parca.metin = "başka"  # type: ignore[misc]


# --- Boş ve kısa metinler ---------------------------------------------------


def test_bos_liste_bos_sonuc_verir():
    assert parcala([]) == []


def test_metin_tr_none_ise_parca_uretilmez():
    assert parcala([_madde("nablusi:000001", metin_tr=None)]) == []


def test_metin_tr_bos_ise_parca_uretilmez():
    assert parcala([_madde("nablusi:000001", metin_tr="")]) == []


def test_kisa_metin_tek_parca_ve_tam_metin():
    madde = _madde("nablusi:000001", metin_tr="Yılan görmek hayra yorulur.")

    parcalar = parcala([madde])

    assert len(parcalar) == 1
    parca = parcalar[0]
    assert parca.parca_id == "nablusi:000001#0"
    assert parca.entry_id == "nablusi:000001"
    assert parca.metin == "Yılan görmek hayra yorulur."
    assert parca.baglamli_metin == _onek() + "\nYılan görmek hayra yorulur."


def test_tam_1000_karakter_tek_parca():
    metin = "a" * PENCERE

    parcalar = parcala([_madde("nablusi:000001", metin_tr=metin)])

    assert len(parcalar) == 1
    assert parcalar[0].metin == metin


# --- Önek -------------------------------------------------------------------


def test_onek_eser_yazar_sembol_ve_bolum_icerir():
    madde = _madde(
        "nablusi:000001",
        metin_tr="Yılan görmek.",
        eser="Tactir Anam",
        yazar="Nablusi",
        sembol_tr="yılan",
        bab="Yılanlar",
    )

    parca = parcala([madde])[0]

    assert parca.baglamli_metin == (
        "Tactir Anam · Nablusi. Sembol: yılan. Bölüm: Yılanlar.\nYılan görmek."
    )


def test_bab_none_ise_bolum_cumlesi_yok():
    madde = _madde("nablusi:000001", metin_tr="Yılan görmek.", sembol_tr="yılan", bab=None)

    parca = parcala([madde])[0]

    assert parca.baglamli_metin == "Test Eseri · Test Yazarı. Sembol: yılan.\nYılan görmek."
    assert "Bölüm:" not in parca.baglamli_metin


def test_sembol_yoksa_sembol_cumlesi_yok():
    madde = _madde("nablusi:000001", metin_tr="Yılan görmek.", bab="Yılanlar")

    parca = parcala([madde])[0]

    assert parca.baglamli_metin == "Test Eseri · Test Yazarı. Bölüm: Yılanlar.\nYılan görmek."
    assert "Sembol:" not in parca.baglamli_metin


def test_ne_sembol_ne_bab_varsa_yalnizca_kunye():
    madde = _madde("nablusi:000001", metin_tr="Yılan görmek.")

    parca = parcala([madde])[0]

    assert parca.baglamli_metin == "Test Eseri · Test Yazarı.\nYılan görmek."


# --- Sembol mirası ----------------------------------------------------------


def test_alt_paragraf_ust_maddenin_sembolunu_miras_alir():
    ust = _madde("nablusi:000001", metin_tr="Yılan babı.", sembol_tr="yılan")
    alt = _madde(
        "nablusi:000002",
        metin_tr="Onu sokarsa ayıp bulur.",
        ust_madde_id="nablusi:000001",
    )

    parcalar = parcala([ust, alt])

    assert parcalar[1].baglamli_metin == (
        "Test Eseri · Test Yazarı. Sembol: yılan.\nOnu sokarsa ayıp bulur."
    )


def test_alt_paragrafin_kendi_sembolu_ustunkine_tercih_edilir():
    ust = _madde("nablusi:000001", metin_tr="Yılan babı.", sembol_tr="yılan")
    alt = _madde(
        "nablusi:000002",
        metin_tr="Ejderha da geçer.",
        sembol_tr="ejderha",
        ust_madde_id="nablusi:000001",
    )

    parcalar = parcala([ust, alt])

    assert "Sembol: ejderha." in parcalar[1].baglamli_metin
    assert "Sembol: yılan." not in parcalar[1].baglamli_metin


def test_ust_madde_listede_yoksa_baslik_asli_kullanilir():
    alt = _madde(
        "nablusi:000002",
        metin_tr="Onu sokarsa ayıp bulur.",
        baslik_asli="حية",
        ust_madde_id="nablusi:000001",
    )

    parca = parcala([alt])[0]

    assert parca.baglamli_metin == (
        "Test Eseri · Test Yazarı. Sembol: حية.\nOnu sokarsa ayıp bulur."
    )


def test_sembol_ve_baslik_yoksa_sembol_cumlesi_atlanir():
    alt = _madde(
        "nablusi:000002",
        metin_tr="Onu sokarsa ayıp bulur.",
        ust_madde_id="nablusi:000001",
    )

    parca = parcala([alt])[0]

    assert parca.baglamli_metin == "Test Eseri · Test Yazarı.\nOnu sokarsa ayıp bulur."


# --- Uzun metin: pencereler -------------------------------------------------


def test_1001_karakter_iki_parcaya_bolunur():
    metin = "a" * 1001

    parcalar = parcala([_madde("nablusi:000001", metin_tr=metin)])

    assert len(parcalar) == 2
    assert [p.parca_id for p in parcalar] == ["nablusi:000001#0", "nablusi:000001#1"]
    assert all(len(p.metin) <= PENCERE for p in parcalar)
    assert parcalar[0].metin == metin[:PENCERE]
    assert parcalar[1].metin == metin[PENCERE - ORTUSME :]


def test_uzun_metin_butun_metni_kapsar_ve_150_karakter_ortusur():
    metin = "".join(f"{i:05d}" for i in range(500))  # 2.500 karakter, benzersiz bloklar

    parcalar = parcala([_madde("nablusi:000001", metin_tr=metin)])
    araliklar = _pencereler(parcalar, metin)

    assert len(parcalar) == 3
    assert all(len(p.metin) <= PENCERE for p in parcalar)
    assert araliklar[0][0] == 0
    assert araliklar[-1][1] == len(metin)
    for (_, onceki_son), (sonraki_bas, _) in itertools.pairwise(araliklar):
        assert sonraki_bas <= onceki_son, "pencereler arasında boşluk olmamalı"
        assert onceki_son - sonraki_bas == ORTUSME


def test_bosluksuz_uzun_metinde_sonsuz_donguye_girilmez():
    metin = "".join(f"{i:05d}" for i in range(1000))  # 5.000 karakter, boşluksuz

    parcalar = parcala([_madde("nablusi:000001", metin_tr=metin)])
    araliklar = _pencereler(parcalar, metin)

    assert len(parcalar) == 6
    assert all(len(p.metin) <= PENCERE for p in parcalar)
    assert araliklar[0][0] == 0
    assert araliklar[-1][1] == len(metin)
    for (_, onceki_son), (sonraki_bas, _) in itertools.pairwise(araliklar):
        assert sonraki_bas <= onceki_son


def test_pencere_mumkun_oldugunda_bosluktan_kesilir():
    kelimeler = [f"kelime{i:04d}" for i in range(400)]  # 10 karakterlik kelimeler
    metin = " ".join(kelimeler)

    parcalar = parcala([_madde("nablusi:000001", metin_tr=metin)])
    araliklar = _pencereler(parcalar, metin)

    assert len(parcalar) > 1
    assert all(len(p.metin) <= PENCERE for p in parcalar)
    assert araliklar[0][0] == 0
    assert araliklar[-1][1] == len(metin)
    for parca, (_, son) in zip(parcalar, araliklar, strict=True):
        if son < len(metin):
            # Pencere sonu kelime ortasında kalmamalı: ya boşlukta biter ya da
            # metnin sonraki karakteri boşluktur.
            assert parca.metin.endswith(" ") or metin[son] == " ", (
                f"pencere kelimeyi böldü: {parca.metin[-20:]!r}"
            )


def test_her_parca_kendi_onekini_tasir():
    metin = "a" * 1500
    madde = _madde("nablusi:000001", metin_tr=metin, sembol_tr="yılan", bab="Yılanlar")

    parcalar = parcala([madde])

    assert len(parcalar) == 2
    for parca in parcalar:
        assert parca.baglamli_metin == _onek(sembol="yılan", bab="Yılanlar") + "\n" + parca.metin


# --- Sıra ve kimlikler ------------------------------------------------------


def test_parcalar_madde_sirasini_korur():
    maddeler = [
        _madde("nablusi:000001", metin_tr="Birinci madde."),
        _madde("nablusi:000002", metin_tr="İkinci madde."),
        _madde("nablusi:000003", metin_tr=None),
        _madde("nablusi:000004", metin_tr="Dördüncü madde."),
    ]

    parcalar = parcala(maddeler)

    assert [p.entry_id for p in parcalar] == [
        "nablusi:000001",
        "nablusi:000002",
        "nablusi:000004",
    ]
    assert [p.parca_id for p in parcalar] == [
        "nablusi:000001#0",
        "nablusi:000002#0",
        "nablusi:000004#0",
    ]
