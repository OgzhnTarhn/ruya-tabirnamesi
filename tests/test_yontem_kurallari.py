"""Kural tabanlı yöntem etiketi çıkarma testleri (enrich/yontem_kurallari.py).

``yontemleri_cikar`` metinde tanınan anlam türetme yollarını (ayet, hadis, mesel, zit, kok,
ebced) sabit sırayla ve her biri en fazla bir kez döndürür. ``maddelere_uygula`` maddelerin
kopyalarını üretip ``yontem`` alanını doldurur, başka hiçbir alanı değiştirmez.
"""

from __future__ import annotations

import pytest

from ruya.enrich.yontem_kurallari import maddelere_uygula, yontemleri_cikar
from ruya.schemas import Madde


def _madde(entry_id: str, metin_tr: str | None = None) -> Madde:
    kaynak = entry_id.split(":", 1)[0]
    return Madde.model_validate(
        {
            "entry_id": entry_id,
            "kaynak": kaynak,
            "eser": "Örnek eser",
            "yazar": "Örnek yazar",
            "gelenek": "islami_klasik",
            "dil": "ar",
            "lisans": "CC-BY-NC-SA-4.0",
            "konum": {"satir": 1},
            "metin_asli": "(asıl metin)",
            "metin_tr": metin_tr,
        }
    )


# --- Ayet -------------------------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Allah Teâlâ şöyle buyurmuştur: sabredenlerle beraberdir.",
        "Allah teala buyurur ki sabır güzeldir.",
        "Bu rüya âyette geçer.",
        "Ayette buna işaret vardır.",
        "Âyeti okumak hayırdır.",
        "Ayetinde bu anlatılır.",
    ],
)
def test_ayet_etiketi(metin):
    assert yontemleri_cikar(metin) == ["ayet"]


def test_ayet_buyur_ayni_cumlede_olmali():
    assert yontemleri_cikar("Allah Teâlâ böyle buyurmuştur. Bu başka bir cümledir.") == ["ayet"]
    assert yontemleri_cikar("Allah Teâlâ vardır. Sonra buyurmuştur.") == []


# --- Hadis ------------------------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Hadiste bu böyle geçer.",
        "Hadisinde bu anlatılır.",
        "Bu hadisi şerifte geçer.",
        "Hadis-i kudsîde buyurulur.",
        "Peygamber buyurdu ki rüya müjdedir.",
        "Resûlullah şöyle buyurmuştur.",
        "Resulullah buyurdu.",
    ],
)
def test_hadis_etiketi(metin):
    assert yontemleri_cikar(metin) == ["hadis"]


def test_hadis_buyur_ayni_cumlede_olmali():
    assert yontemleri_cikar("Peygamber vardır. Sonra buyurmuştur.") == []


# --- Mesel ------------------------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Mesel şöyledir.",
        "Meselde böyle denir.",
        "Meselinde bu anlatılır.",
        "Atasözü bunu söyler.",
        "Atasözünde geçer.",
    ],
)
def test_mesel_etiketi(metin):
    assert yontemleri_cikar(metin) == ["mesel"]


# --- Zıt --------------------------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Bu, zıddıyla tabir edilir.",
        "Ağlamak zıddıdır.",
        "Ölüm zıddına işarettir.",
        "Bu tersine yorumlanır.",
    ],
)
def test_zit_etiketi(metin):
    assert yontemleri_cikar(metin) == ["zit"]


# --- Kök --------------------------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Lafzından bu anlaşılır.",
        "Kelimesinden türetilmiştir.",
        "İsminden türemiştir.",
    ],
)
def test_kok_etiketi(metin):
    assert yontemleri_cikar(metin) == ["kok"]


# --- Ebced ------------------------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Ebced hesabıyla bulunur.",
        "Ebcedle hesaplanır.",
    ],
)
def test_ebced_etiketi(metin):
    assert yontemleri_cikar(metin) == ["ebced"]


# --- Sıra ve tekrar ---------------------------------------------------------


def test_sabit_sira_ve_her_etiket_bir_kez():
    metin = (
        "Ebced hesabıyla bulunur. Kelimesinden türetilmiştir. Zıddıyla tabir edilir. "
        "Meselde denir. Hadiste geçer. Ayette geçer. Yine ayette ve hadiste geçer."
    )

    assert yontemleri_cikar(metin) == ["ayet", "hadis", "mesel", "zit", "kok", "ebced"]


def test_ayni_etiket_tek_kez_doner():
    assert yontemleri_cikar("Ayette geçer. Yine ayette geçer.") == ["ayet"]


# --- Eşleşmeyen metinler ----------------------------------------------------


@pytest.mark.parametrize(
    "metin",
    [
        "Rüyada hadis okumak ilimdir.",
        "Kur'an okumak hayırdır.",
        "Peygamberi görmek müjdedir.",
        "Zıt görüşlü biriyle tartışır.",
    ],
)
def test_eslesmeyen_metinler_bos_doner(metin):
    assert yontemleri_cikar(metin) == []


# --- Boş girdi --------------------------------------------------------------


def test_bos_metin_bos_liste():
    assert yontemleri_cikar("") == []


def test_none_bos_liste():
    assert yontemleri_cikar(None) == []


def test_bosluk_metin_bos_liste():
    assert yontemleri_cikar("   \n\t ") == []


# --- maddelere_uygula -------------------------------------------------------


def test_maddelere_uygula_yontemi_doldurur():
    maddeler = [_madde("nablusi:004310", metin_tr="Bu rüya âyette geçer.")]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0].yontem == ["ayet"]


def test_maddelere_uygula_etiketsiz_maddede_none_birakir():
    maddeler = [_madde("nablusi:004310", metin_tr="Rüyada hadis okumak ilimdir.")]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0].yontem is None


def test_maddelere_uygula_metin_tr_none_olan_maddede_none_birakir():
    maddeler = [_madde("nablusi:004310", metin_tr=None)]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0].yontem is None


def test_maddelere_uygula_girdiyi_degistirmez():
    maddeler = [_madde("nablusi:004310", metin_tr="Bu rüya âyette geçer.")]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0] is not maddeler[0]
    assert maddeler[0].yontem is None


def test_maddelere_uygula_diger_alanlari_degistirmez():
    madde = _madde("nablusi:004310", metin_tr="Bu rüya âyette geçer.")

    sonuc = maddelere_uygula([madde])

    assert sonuc[0].model_dump(exclude={"yontem"}) == madde.model_dump(exclude={"yontem"})


def test_maddelere_uygula_sira_korunur():
    maddeler = [
        _madde("miller:018710", metin_tr="Hadiste geçer."),
        _madde("nablusi:004310", metin_tr="Rüyada hadis okumak ilimdir."),
        _madde("nablusi:004314", metin_tr="Ebced hesabıyla bulunur."),
    ]

    sonuc = maddelere_uygula(maddeler)

    assert [m.entry_id for m in sonuc] == [
        "miller:018710",
        "nablusi:004310",
        "nablusi:004314",
    ]
    assert [m.yontem for m in sonuc] == [["hadis"], None, ["ebced"]]


def test_maddelere_uygula_bos_liste_bos_liste_dondurur():
    assert maddelere_uygula([]) == []
