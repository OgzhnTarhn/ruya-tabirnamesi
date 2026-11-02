"""varyant_tablosu ve sozluk_maddeler_tutarliligi davranışları (docs/02 bölüm 4.2)."""

import pytest

from ruya.hatalar import SozlukHatasi
from ruya.index.build_symbols import sozluk_maddeler_tutarliligi, varyant_tablosu
from ruya.schemas import Konum, Madde, SymbolKaydi


def _madde(entry_id: str, symbol_ids: list[str]) -> Madde:
    kaynak = entry_id.split(":")[0]
    return Madde(
        entry_id=entry_id,
        kaynak=kaynak,
        eser="Örnek eser",
        yazar="Örnek yazar",
        gelenek="islami_klasik",
        dil="tr",
        lisans="PD",
        konum=Konum(satir=1),
        symbol_ids=symbol_ids,
        metin_asli="(örnek metin)",
    )


# --- varyant_tablosu --------------------------------------------------------


def test_varyant_tablosu_ad_ve_varyantlari_normallestirir():
    sozluk = {
        "yilan": SymbolKaydi(
            ad_tr="Yılan", varyantlar_tr=["Engerek", "  Yılanlar! "], gozden_gecirildi=True
        ),
    }

    tablo = varyant_tablosu(sozluk)

    assert tablo["yılan"] == "yilan"
    assert tablo["engerek"] == "yilan"
    assert tablo["yılanlar"] == "yilan"


def test_varyant_tablosu_ayni_varyant_iki_sembolde_hata_verir():
    sozluk = {
        "yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True),
        "ejderha": SymbolKaydi(ad_tr="ejderha", varyantlar_tr=["Yılan"], gozden_gecirildi=True),
    }

    with pytest.raises(SozlukHatasi):
        varyant_tablosu(sozluk)


def test_varyant_tablosu_ayni_sembol_icinde_tekrar_sorun_degil():
    sozluk = {
        "yilan": SymbolKaydi(
            ad_tr="yılan", varyantlar_tr=["yılan", "Yılan"], gozden_gecirildi=True
        ),
    }

    tablo = varyant_tablosu(sozluk)

    assert tablo == {"yılan": "yilan"}


def test_varyant_tablosu_onaysizlari_atlar():
    sozluk = {
        "yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True),
        "ejderha": SymbolKaydi(ad_tr="ejderha", gozden_gecirildi=False),
    }

    tablo = varyant_tablosu(sozluk)

    assert tablo == {"yılan": "yilan"}


def test_varyant_tablosu_onaysizlari_dahil_eder():
    sozluk = {
        "yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True),
        "ejderha": SymbolKaydi(ad_tr="ejderha", gozden_gecirildi=False),
    }

    tablo = varyant_tablosu(sozluk, yalniz_onaylilar=False)

    assert tablo == {"yılan": "yilan", "ejderha": "ejderha"}


# --- sozluk_maddeler_tutarliligi -------------------------------------------


def test_tutarlilik_bos_liste_doner():
    sozluk = {"yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True)}
    maddeler = [_madde("nablusi:0001", ["yilan"])]

    assert sozluk_maddeler_tutarliligi(sozluk, maddeler) == []


def test_tutarlilik_bilinmeyen_symbol_id_bildirir():
    sozluk = {"yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True)}
    maddeler = [
        _madde("nablusi:0001", ["yilan"]),
        _madde("nablusi:0002", ["ejderha"]),
    ]

    sorunlar = sozluk_maddeler_tutarliligi(sozluk, maddeler)

    assert len(sorunlar) == 1
    assert isinstance(sorunlar[0], str)
    assert "ejderha" in sorunlar[0]


def test_tutarlilik_maddesiz_onayli_sembol_bildirir():
    sozluk = {
        "yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True),
        "ejderha": SymbolKaydi(ad_tr="ejderha", gozden_gecirildi=True),
    }
    maddeler = [_madde("nablusi:0001", ["yilan"])]

    sorunlar = sozluk_maddeler_tutarliligi(sozluk, maddeler)

    assert len(sorunlar) == 1
    assert isinstance(sorunlar[0], str)
    assert "ejderha" in sorunlar[0]


def test_tutarlilik_maddesiz_onaysiz_sembolu_bildirmez():
    sozluk = {
        "yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True),
        "ejderha": SymbolKaydi(ad_tr="ejderha", gozden_gecirildi=False),
    }
    maddeler = [_madde("nablusi:0001", ["yilan"])]

    assert sozluk_maddeler_tutarliligi(sozluk, maddeler) == []


def test_tutarlilik_her_sorun_icin_ayri_dize_doner():
    sozluk = {
        "yilan": SymbolKaydi(ad_tr="yılan", gozden_gecirildi=True),
        "ejderha": SymbolKaydi(ad_tr="ejderha", gozden_gecirildi=True),
    }
    maddeler = [_madde("nablusi:0001", ["anka"])]

    sorunlar = sozluk_maddeler_tutarliligi(sozluk, maddeler)

    assert len(sorunlar) == 3
    assert all(isinstance(s, str) for s in sorunlar)
    assert any("anka" in s for s in sorunlar)
    assert any("yilan" in s for s in sorunlar)
    assert any("ejderha" in s for s in sorunlar)
