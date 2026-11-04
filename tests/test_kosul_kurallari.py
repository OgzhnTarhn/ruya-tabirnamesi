"""Kural tabanlı koşul çıkarma testleri (enrich/kosul_kurallari.py).

``kosullari_cikar`` metni cümlelere böler (. ! ?) ve her cümlede tanınan koşul için
bir ``Kosul`` döndürür; ``yorum_tr`` o cümlenin kırpılmış hâlidir. ``maddelere_uygula``
maddelerin kopyalarını üretip ``kosullar`` alanını doldurur, başka hiçbir alanı değiştirmez.
"""

from __future__ import annotations

import pytest

from ruya.enrich.kosul_kurallari import kosullari_cikar, maddelere_uygula
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


def _kosullar(metin: str) -> list[dict[str, str]]:
    return [k.kosul for k in kosullari_cikar(metin)]


# --- Cinsiyet ---------------------------------------------------------------


def test_kadin_kosulu():
    metin = "Genç bir kadının yılan görmesi hileye işarettir."

    sonuc = kosullari_cikar(metin)

    assert len(sonuc) == 1
    assert sonuc[0].kosul == {"cinsiyet": "kadin"}
    assert sonuc[0].yorum_tr == metin


def test_kadin_gorurse_kosulu():
    assert _kosullar("Kadın görürse evlenir.") == [{"cinsiyet": "kadin"}]


def test_erkek_gorurse_kosulu():
    assert _kosullar("Erkek görürse mal bulur.") == [{"cinsiyet": "erkek"}]


def test_adam_kosulu_erkek_sayilir():
    assert _kosullar("Bir adamın bunu görmesi rızıktır.") == [{"cinsiyet": "erkek"}]


@pytest.mark.parametrize(
    "metin",
    [
        "Bir kadına iftira eder.",
        "Dünya alçak kadına işaret eder.",
        "Hıristiyan bir kadınla evlendiğini görür.",
        "Ağaçtan badem alan, cimri bir adamdan çekişme ile mal elde eder.",
        "Bir keler yakaladığını görürse, böyle bir adama rastlar.",
        "Onu yediğini görürse, o adam tanınan biri ise bu onun sermayesidir.",
        "Bir kadının saçını taradığını görmek hayırdır.",
        "Yüce bir adamın hizmetine yaklaşır.",
    ],
)
def test_nesne_konumundaki_cinsiyet_kosul_sayilmaz(metin):
    assert [k for k in _kosullar(metin) if "cinsiyet" in k] == []


@pytest.mark.parametrize(
    "metin",
    [
        "Genç bir kadının yılan görmesi hileye işarettir.",
        "Kadın görürse evlenir.",
        "Bir kadın ilkbaharda gül alırsa sevgilisi olur.",
        "Genç bir kadının bir oyuna gittiğini görmesi iyidir.",
        "Kadına gelince, bu çocuktur.",
        "Kadın için hayırlıdır.",
    ],
)
def test_kadin_kosulu_doner(metin):
    assert {"cinsiyet": "kadin"} in _kosullar(metin)


@pytest.mark.parametrize(
    "metin",
    [
        "Erkek görürse mal bulur.",
        "Bir adamın bunu görmesi rızıktır.",
        "Erkek memesinde süt görürse zenginleşir.",
        "Erkeğe gelince, bu oğuldur.",
    ],
)
def test_erkek_kosulu_doner(metin):
    assert {"cinsiyet": "erkek"} in _kosullar(metin)


# --- Medeni hâl -------------------------------------------------------------


def test_evli_kosulu():
    assert _kosullar("Evli biri görürse ayrılık olur.") == [{"medeni_hal": "evli"}]


def test_evli_ise_kosulu():
    assert _kosullar("Evli ise hayırdır.") == [{"medeni_hal": "evli"}]


def test_bekar_kosulu():
    assert _kosullar("Bekâr görürse evlenir.") == [{"medeni_hal": "bekar"}]


def test_bekar_sade_yazimla_kosulu():
    assert _kosullar("Bekar ise evlenir.") == [{"medeni_hal": "bekar"}]


@pytest.mark.parametrize(
    "metin",
    [
        "Evli değilse çocuğu olur.",
        "Bu, evli olmayan için hayırlıdır.",
        "Bekârın evlenmesine işaret eder.",
    ],
)
def test_evli_olmayan_bekar_kosulu_doner(metin):
    kosullar = _kosullar(metin)
    assert {"medeni_hal": "bekar"} in kosullar
    assert {"medeni_hal": "evli"} not in kosullar


# --- Mevsim -----------------------------------------------------------------


def test_kis_kosulu():
    assert _kosullar("Kışın görülürse iyidir.") == [{"mevsim": "kis"}]


def test_yaz_kosulu():
    assert _kosullar("Yazın görmek nimettir.") == [{"mevsim": "yaz"}]


def test_ilkbahar_kosulu():
    assert _kosullar("İlkbaharda görülürse hayırdır.") == [{"mevsim": "ilkbahar"}]


def test_sonbahar_kosulu():
    assert _kosullar("Sonbaharda görülürse iyidir.") == [{"mevsim": "sonbahar"}]


@pytest.mark.parametrize(
    "metin",
    [
        "Örümcek düşerse bu, kışın şiddetine delildir.",
        "İlkbaharın yaklaştığını görmek iyidir.",
    ],
)
def test_nesne_konumundaki_mevsim_kosul_sayilmaz(metin):
    assert [k for k in _kosullar(metin) if "mevsim" in k] == []


def test_kisin_turna_gormek_kis_kosulu():
    assert {"mevsim": "kis"} in _kosullar("Kim kışın turna görürse kötüdür.")


# --- Eşleşmeyen metinler ----------------------------------------------------


def test_kosulsuz_cumleler_bos_doner():
    for metin in [
        "Rüyada kadın görmek dünyaya işarettir.",
        "Yazı yazmak bilgidir.",
        "Kışlık erzak bolluktur.",
        "Evlilik hayırdır.",
    ]:
        assert kosullari_cikar(metin) == [], metin


# --- Boş girdi --------------------------------------------------------------


def test_bos_metin_bos_liste():
    assert kosullari_cikar("") == []


def test_none_bos_liste():
    assert kosullari_cikar(None) == []


def test_bosluk_metin_bos_liste():
    assert kosullari_cikar("   \n\t ") == []


# --- Cümlelere bölme ve sıra ------------------------------------------------


def test_cumleler_noktalama_isaretlerinden_bolunur():
    metin = "Kadın görürse evlenir. Erkek görürse mal bulur! Evli ise hayırdır?"

    sonuc = kosullari_cikar(metin)

    assert [k.kosul for k in sonuc] == [
        {"cinsiyet": "kadin"},
        {"cinsiyet": "erkek"},
        {"medeni_hal": "evli"},
    ]
    assert [k.yorum_tr for k in sonuc] == [
        "Kadın görürse evlenir.",
        "Erkek görürse mal bulur!",
        "Evli ise hayırdır?",
    ]


def test_yorum_tr_cumlenin_kirpilmis_halidir():
    sonuc = kosullari_cikar("  Kadın görürse evlenir.  ")

    assert len(sonuc) == 1
    assert sonuc[0].yorum_tr == "Kadın görürse evlenir."


def test_kosulsuz_cumle_atlanir_sirali_kalanlar_doner():
    metin = "Yazı yazmak bilgidir. Kadın görürse evlenir. Kışlık erzak bolluktur."

    sonuc = kosullari_cikar(metin)

    assert len(sonuc) == 1
    assert sonuc[0].kosul == {"cinsiyet": "kadin"}
    assert sonuc[0].yorum_tr == "Kadın görürse evlenir."


def test_bir_cumle_iki_kosul_verebilir():
    metin = "Evli bir kadın görürse ayrılık olur."

    sonuc = kosullari_cikar(metin)

    assert len(sonuc) == 2
    assert {frozenset(k.kosul.items()) for k in sonuc} == {
        frozenset({("cinsiyet", "kadin")}),
        frozenset({("medeni_hal", "evli")}),
    }
    assert all(k.yorum_tr == metin for k in sonuc)


def test_otorite_bos_kalir():
    sonuc = kosullari_cikar("Kadın görürse evlenir.")

    assert sonuc[0].otorite is None


# --- maddelere_uygula -------------------------------------------------------


def test_maddelere_uygula_kosullari_doldurur():
    maddeler = [_madde("nablusi:004310", metin_tr="Kadın görürse evlenir.")]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0].kosullar is not None
    assert [k.kosul for k in sonuc[0].kosullar] == [{"cinsiyet": "kadin"}]
    assert sonuc[0].kosullar[0].yorum_tr == "Kadın görürse evlenir."


def test_maddelere_uygula_kosulsuz_maddede_none_birakir():
    maddeler = [_madde("nablusi:004310", metin_tr="Yazı yazmak bilgidir.")]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0].kosullar is None


def test_maddelere_uygula_metin_tr_none_olan_maddede_none_birakir():
    maddeler = [_madde("nablusi:004310", metin_tr=None)]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0].kosullar is None


def test_maddelere_uygula_girdiyi_degistirmez():
    maddeler = [_madde("nablusi:004310", metin_tr="Kadın görürse evlenir.")]

    sonuc = maddelere_uygula(maddeler)

    assert sonuc[0] is not maddeler[0]
    assert maddeler[0].kosullar is None


def test_maddelere_uygula_diger_alanlari_degistirmez():
    madde = _madde("nablusi:004310", metin_tr="Kadın görürse evlenir.")

    sonuc = maddelere_uygula([madde])

    assert sonuc[0].model_dump(exclude={"kosullar"}) == madde.model_dump(exclude={"kosullar"})


def test_maddelere_uygula_sira_korunur():
    maddeler = [
        _madde("miller:018710", metin_tr="Erkek görürse mal bulur."),
        _madde("nablusi:004310", metin_tr="Yazı yazmak bilgidir."),
        _madde("nablusi:004314", metin_tr="Kışın görülürse iyidir."),
    ]

    sonuc = maddelere_uygula(maddeler)

    assert [m.entry_id for m in sonuc] == [
        "miller:018710",
        "nablusi:004310",
        "nablusi:004314",
    ]
    assert [m.kosullar[0].kosul if m.kosullar else None for m in sonuc] == [
        {"cinsiyet": "erkek"},
        None,
        {"mevsim": "kis"},
    ]


def test_maddelere_uygula_bos_liste_bos_liste_dondurur():
    assert maddelere_uygula([]) == []
