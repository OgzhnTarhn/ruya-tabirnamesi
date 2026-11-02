"""Sembol kimliklerini maddelere atama testleri (enrich/sembol_ata.py).

``sembol_ata`` sözlükten gelen ``{normalleştirilmiş ad: symbol_id}`` eşlemesini kullanır:
eşleşen madde kimliği alır, eşleşmeyen alt paragraf üst maddesinin kimliğini devralır.
"""

from __future__ import annotations

from ruya.enrich.sembol_ata import sembol_ata
from ruya.schemas import Madde


def _madde(
    entry_id: str,
    sembol_tr: str | None = None,
    ust_madde_id: str | None = None,
) -> Madde:
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
            "sembol_tr": sembol_tr,
            "ust_madde_id": ust_madde_id,
            "metin_asli": "(asıl metin)",
        }
    )


# --- Doğrudan eşleşme -------------------------------------------------------


def test_eslesen_madde_kimligi_alir():
    maddeler = [_madde("nablusi:004310", sembol_tr="yılan")]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == ["yilan"]


def test_eslesme_normallestirilmis_anahtarla_yapilir():
    maddeler = [_madde("nablusi:004310", sembol_tr="  Yılanlar! ")]

    sonuc = sembol_ata(maddeler, {"yılanlar": "yilan"})

    assert sonuc[0].symbol_ids == ["yilan"]


def test_eslesmeyen_madde_bos_kimlikle_kalir():
    maddeler = [_madde("nablusi:004310", sembol_tr="ejderha")]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == []


def test_sembol_tr_none_olan_madde_guvenli():
    maddeler = [_madde("nablusi:004310", sembol_tr=None)]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == []


def test_bos_varyantlarla_butun_kimlikler_bos():
    maddeler = [_madde("nablusi:004310", sembol_tr="yılan")]

    sonuc = sembol_ata(maddeler, {})

    assert sonuc[0].symbol_ids == []


# --- Üst maddeden devralma --------------------------------------------------


def test_eslesmeyen_alt_paragraf_ust_maddenin_kimligini_devralir():
    maddeler = [
        _madde("nablusi:004310", sembol_tr="yılan"),
        _madde("nablusi:004314", sembol_tr=None, ust_madde_id="nablusi:004310"),
    ]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == ["yilan"]
    assert sonuc[1].symbol_ids == ["yilan"]


def test_ust_madde_sonradan_gelse_de_devralma_calisir():
    maddeler = [
        _madde("nablusi:004314", sembol_tr=None, ust_madde_id="nablusi:004310"),
        _madde("nablusi:004310", sembol_tr="yılan"),
    ]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == ["yilan"]
    assert sonuc[1].symbol_ids == ["yilan"]


def test_ust_maddesi_eslesmeyen_alt_paragraf_bos_kalir():
    maddeler = [
        _madde("nablusi:004310", sembol_tr="ejderha"),
        _madde("nablusi:004314", sembol_tr=None, ust_madde_id="nablusi:004310"),
    ]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == []
    assert sonuc[1].symbol_ids == []


def test_ust_maddesi_listede_olmayan_alt_paragraf_bos_kalir():
    maddeler = [_madde("nablusi:004314", sembol_tr=None, ust_madde_id="nablusi:004310")]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0].symbol_ids == []


def test_alt_paragraf_kendi_eslesmesini_ust_maddeye_tercih_eder():
    maddeler = [
        _madde("nablusi:004310", sembol_tr="yılan"),
        _madde("nablusi:004314", sembol_tr="su", ust_madde_id="nablusi:004310"),
    ]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan", "su": "su"})

    assert sonuc[0].symbol_ids == ["yilan"]
    assert sonuc[1].symbol_ids == ["su"]


# --- Girdi ve sıra ----------------------------------------------------------


def test_girdi_nesneleri_degistirilmez():
    maddeler = [
        _madde("nablusi:004310", sembol_tr="yılan"),
        _madde("nablusi:004314", sembol_tr=None, ust_madde_id="nablusi:004310"),
    ]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan"})

    assert sonuc[0] is not maddeler[0]
    assert sonuc[1] is not maddeler[1]
    assert maddeler[0].symbol_ids == []
    assert maddeler[1].symbol_ids == []


def test_sira_korunur():
    maddeler = [
        _madde("miller:018710", sembol_tr="yılanlar"),
        _madde("nablusi:004310", sembol_tr="yılan"),
        _madde("nablusi:004314", sembol_tr=None, ust_madde_id="nablusi:004310"),
    ]

    sonuc = sembol_ata(maddeler, {"yılan": "yilan", "yılanlar": "yilan"})

    assert [m.entry_id for m in sonuc] == [
        "miller:018710",
        "nablusi:004310",
        "nablusi:004314",
    ]
    assert [m.symbol_ids for m in sonuc] == [["yilan"], ["yilan"], ["yilan"]]


def test_bos_liste_bos_liste_dondurur():
    assert sembol_ata([], {"yılan": "yilan"}) == []
