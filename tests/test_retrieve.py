"""BellekDeposu ve retrieve birim testleri (docs/03, Adım 3)."""

import pytest

from ruya.index.store import BellekDeposu
from ruya.pipeline.retrieve import retrieve
from ruya.schemas import Eslesme, Madde, Sembol


def _madde(
    entry_id: str,
    kaynak: str,
    symbol_ids: list[str],
    *,
    metin_tr: str | None = None,
    gelenek: str = "islami_klasik",
    ust_madde_id: str | None = None,
) -> Madde:
    """Testte kullanılacak en küçük geçerli Madde."""
    return Madde(
        entry_id=entry_id,
        kaynak=kaynak,
        eser="Test Eseri",
        yazar="Test Yazarı",
        gelenek=gelenek,
        dil="tr",
        lisans="PD",
        konum={"satir": 1},
        ust_madde_id=ust_madde_id,
        symbol_ids=symbol_ids,
        metin_asli="(asıl metin)",
        metin_tr=metin_tr,
    )


def _eslesme(
    symbol_id: str | None,
    yontem: str = "birebir",
    nitelikler: list[str] | None = None,
) -> Eslesme:
    return Eslesme(
        sembol=Sembol(yalin="yılan", nitelikler=nitelikler or [], ham_ifade="yılan"),
        symbol_id=symbol_id,
        yontem=yontem,
        guven=1.0,
    )


# --- BellekDeposu -----------------------------------------------------------


def test_sembolun_maddeleri_yalnizca_o_sembolu_dondurur():
    yilan = _madde("nablusi:000001", "nablusi", ["yilan"])
    at = _madde("nablusi:000002", "nablusi", ["at"])
    depo = BellekDeposu([yilan, at])

    assert depo.sembolun_maddeleri("yilan") == [yilan]
    assert depo.sembolun_maddeleri("at") == [at]


def test_sembolun_maddeleri_bilinmeyen_sembol_icin_bos_liste():
    depo = BellekDeposu([_madde("nablusi:000001", "nablusi", ["yilan"])])

    assert depo.sembolun_maddeleri("ejderha") == []


def test_madde_entry_id_ile_doner():
    yilan = _madde("nablusi:000001", "nablusi", ["yilan"])
    depo = BellekDeposu([yilan])

    assert depo.madde("nablusi:000001") is yilan


def test_madde_bilinmeyen_entry_id_icin_keyerror():
    depo = BellekDeposu([_madde("nablusi:000001", "nablusi", ["yilan"])])

    with pytest.raises(KeyError):
        depo.madde("nablusi:999999")


# --- retrieve: anahtarlar ve filtreler --------------------------------------


def test_sonuc_eslesen_sembollerin_symbol_id_si_ile_anahtarlanir():
    yilan = _madde("nablusi:000001", "nablusi", ["yilan"])
    at = _madde("miller:000001", "miller", ["at"], gelenek="bati_halk")
    depo = BellekDeposu([yilan, at])

    sonuc = retrieve([_eslesme("yilan"), _eslesme("at")], depo)

    assert set(sonuc) == {"yilan", "at"}
    assert [a.madde for a in sonuc["yilan"]] == [yilan]
    assert [a.madde for a in sonuc["at"]] == [at]


def test_yontem_yok_olan_eslesme_atlanir():
    yilan = _madde("nablusi:000001", "nablusi", ["yilan"])
    depo = BellekDeposu([yilan])

    sonuc = retrieve([_eslesme(None, yontem="yok"), _eslesme("yilan")], depo)

    assert set(sonuc) == {"yilan"}


def test_maddesi_olmayan_sembol_icin_bos_liste():
    depo = BellekDeposu([_madde("nablusi:000001", "nablusi", ["yilan"])])

    sonuc = retrieve([_eslesme("ejderha")], depo)

    assert sonuc["ejderha"] == []


def test_her_kaynaktan_en_fazla_n_madde():
    maddeler = [
        _madde("nablusi:000001", "nablusi", ["yilan"]),
        _madde("nablusi:000002", "nablusi", ["yilan"]),
        _madde("nablusi:000003", "nablusi", ["yilan"]),
        _madde("miller:000001", "miller", ["yilan"], gelenek="bati_halk"),
        _madde("miller:000002", "miller", ["yilan"], gelenek="bati_halk"),
    ]
    depo = BellekDeposu(maddeler)

    sonuc = retrieve([_eslesme("yilan")], depo, n=2)

    adaylar = sonuc["yilan"]
    assert len(adaylar) == 4
    assert sum(1 for a in adaylar if a.madde.kaynak == "nablusi") == 2
    assert sum(1 for a in adaylar if a.madde.kaynak == "miller") == 2


def test_n_bir_ise_her_kaynaktan_tek_madde():
    maddeler = [
        _madde("nablusi:000001", "nablusi", ["yilan"]),
        _madde("nablusi:000002", "nablusi", ["yilan"]),
        _madde("miller:000001", "miller", ["yilan"], gelenek="bati_halk"),
    ]
    depo = BellekDeposu(maddeler)

    sonuc = retrieve([_eslesme("yilan")], depo, n=1)

    assert len(sonuc["yilan"]) == 2
    assert {a.madde.kaynak for a in sonuc["yilan"]} == {"nablusi", "miller"}


def test_gelenekler_yalnizca_secili_gelenegin_maddelerini_getirir():
    islami = _madde("nablusi:000001", "nablusi", ["yilan"])
    bati = _madde("miller:000001", "miller", ["yilan"], gelenek="bati_halk")
    depo = BellekDeposu([islami, bati])

    sonuc = retrieve([_eslesme("yilan")], depo, gelenekler=["bati_halk"])

    assert [a.madde for a in sonuc["yilan"]] == [bati]


# --- retrieve: skor ve sıralama ---------------------------------------------


def test_nitelik_eslesmesi_her_nitelik_icin_iki_puan_verir():
    madde = _madde(
        "nablusi:000001",
        "nablusi",
        ["yilan"],
        metin_tr="Rüyada siyah ve büyük bir yılan görmek.",
        ust_madde_id="nablusi:000000",
    )
    depo = BellekDeposu([madde])

    sonuc = retrieve([_eslesme("yilan", nitelikler=["siyah", "büyük", "küçük"])], depo)

    aday = sonuc["yilan"][0]
    assert aday.skor == 4
    assert "nitelik:siyah" in aday.gerekceler
    assert "nitelik:büyük" in aday.gerekceler
    assert "nitelik:küçük" not in aday.gerekceler


def test_nitelik_eslesmesi_kucuk_harf_ile_yapilir():
    madde = _madde(
        "nablusi:000001",
        "nablusi",
        ["yilan"],
        metin_tr="Rüyada SİYAH bir yılan görmek.",
        ust_madde_id="nablusi:000000",
    )
    depo = BellekDeposu([madde])

    sonuc = retrieve([_eslesme("yilan", nitelikler=["Siyah"])], depo)

    aday = sonuc["yilan"][0]
    assert aday.skor == 2
    assert [g.lower() for g in aday.gerekceler] == ["nitelik:siyah"]


def test_baslikli_madde_bir_puan_alir():
    baslikli = _madde("nablusi:000001", "nablusi", ["yilan"], metin_tr="yılan")
    alt = _madde(
        "nablusi:000002",
        "nablusi",
        ["yilan"],
        metin_tr="yılan",
        ust_madde_id="nablusi:000001",
    )
    depo = BellekDeposu([baslikli, alt])

    sonuc = retrieve([_eslesme("yilan")], depo)

    skorlar = {a.madde.entry_id: a.skor for a in sonuc["yilan"]}
    assert skorlar["nablusi:000001"] == 1
    assert skorlar["nablusi:000002"] == 0
    assert "baslikli" in sonuc["yilan"][0].gerekceler


def test_adaylar_skora_gore_azalan_siralanir():
    dusuk = _madde(
        "nablusi:000001",
        "nablusi",
        ["yilan"],
        metin_tr="yılan",
        ust_madde_id="nablusi:000000",
    )
    orta = _madde("nablusi:000002", "nablusi", ["yilan"], metin_tr="yılan")
    yuksek = _madde(
        "nablusi:000003",
        "nablusi",
        ["yilan"],
        metin_tr="siyah yılan",
        ust_madde_id="nablusi:000000",
    )
    depo = BellekDeposu([dusuk, orta, yuksek])

    sonuc = retrieve([_eslesme("yilan", nitelikler=["siyah"])], depo, n=10)

    assert [a.madde.entry_id for a in sonuc["yilan"]] == [
        "nablusi:000003",
        "nablusi:000002",
        "nablusi:000001",
    ]


def test_esit_skorda_entry_id_ile_siralanir():
    ikinci = _madde(
        "nablusi:000002",
        "nablusi",
        ["yilan"],
        metin_tr="yılan",
        ust_madde_id="nablusi:000000",
    )
    birinci = _madde(
        "nablusi:000001",
        "nablusi",
        ["yilan"],
        metin_tr="yılan",
        ust_madde_id="nablusi:000000",
    )
    depo = BellekDeposu([ikinci, birinci])

    sonuc = retrieve([_eslesme("yilan")], depo, n=10)

    assert [a.madde.entry_id for a in sonuc["yilan"]] == [
        "nablusi:000001",
        "nablusi:000002",
    ]


def test_aday_madde_ozgun_nesnedir():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    depo = BellekDeposu([madde])

    sonuc = retrieve([_eslesme("yilan")], depo)

    assert sonuc["yilan"][0].madde is madde
