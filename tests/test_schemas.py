import datetime as dt
import json

import pytest
from pydantic import ValidationError

from conftest import jsonl_oku
from ruya.schemas import (
    Aday,
    AdimOlcumu,
    CikarimSonucu,
    Eslesme,
    Kullanim,
    Madde,
    RuyaGirdisi,
    Sembol,
    SorguKaydi,
    SozlukDosyasi,
    TestOrnegi,
    Yorum,
    YorumBolumu,
    getirme_anahtari,
)


def test_ornek_maddeler_semaya_uyar(ornek_maddeler):
    maddeler = [Madde.model_validate(m) for m in ornek_maddeler]
    assert maddeler[0].baslikli_mi
    assert not maddeler[1].baslikli_mi


@pytest.mark.parametrize("lisans", ["", "   "])
def test_lisans_bos_olamaz(ornek_maddeler, lisans):
    with pytest.raises(ValidationError):
        Madde.model_validate({**ornek_maddeler[0], "lisans": lisans})


def test_lisans_alani_zorunlu(ornek_maddeler):
    kayit = dict(ornek_maddeler[0])
    del kayit["lisans"]
    with pytest.raises(ValidationError):
        Madde.model_validate(kayit)


def test_entry_id_kaynakla_baslamali(ornek_maddeler):
    with pytest.raises(ValidationError):
        Madde.model_validate({**ornek_maddeler[0], "entry_id": "miller:004310"})


def test_ust_madde_ayni_kaynaktan(ornek_maddeler):
    with pytest.raises(ValidationError):
        Madde.model_validate({**ornek_maddeler[1], "ust_madde_id": "miller:018710"})


@pytest.mark.parametrize("symbol_id", ["yılan", "Yilan", "olmus baba", "_yilan"])
def test_symbol_id_ascii_kucuk_harf(ornek_maddeler, symbol_id):
    with pytest.raises(ValidationError):
        Madde.model_validate({**ornek_maddeler[0], "symbol_ids": [symbol_id]})


def test_sembol_adlari_varsayilan_ve_deger_alir(ornek_maddeler):
    madde = Madde.model_validate(ornek_maddeler[0])
    assert madde.sembol_ar is None
    assert madde.sembol_tr is None
    madde = Madde.model_validate({**ornek_maddeler[0], "sembol_ar": "حية", "sembol_tr": "yılan"})
    assert madde.sembol_ar == "حية"
    assert madde.sembol_tr == "yılan"


def test_bilinmeyen_alan_reddedilir(ornek_maddeler):
    with pytest.raises(ValidationError):
        Madde.model_validate({**ornek_maddeler[0], "ceviri_tr": "eski alan adı"})


def test_ornek_sozluk_semaya_uyar(fixtures):
    sozluk = SozlukDosyasi.model_validate_json((fixtures / "symbols_ornek.json").read_bytes())
    assert sozluk.root["yilan"].gozden_gecirildi
    assert not sozluk.root["deniz"].gozden_gecirildi


def test_ornek_test_seti_semaya_uyar(fixtures):
    for kayit in jsonl_oku(fixtures / "ruyalar_ornek.jsonl"):
        TestOrnegi.model_validate(kayit)


def test_ruya_metni_sinirli():
    with pytest.raises(ValidationError):
        RuyaGirdisi(metin="a" * 3001)
    with pytest.raises(ValidationError):
        RuyaGirdisi(metin="")


def test_olumsuz_semboller_gecmez():
    cikarim = CikarimSonucu(
        semboller=[
            Sembol(yalin="yılan", olumsuz=True, ham_ifade="yılan görmedim"),
            Sembol(yalin="deniz", ham_ifade="denize"),
        ]
    )
    assert [s.yalin for s in cikarim.gecerli_semboller] == ["deniz"]


def test_eslesme_yontemi_ve_kimlik_tutarli():
    sembol = Sembol(yalin="uzay gemisi", ham_ifade="uzay gemisi")
    Eslesme(sembol=sembol, symbol_id=None, yontem="yok", guven=0.0)
    with pytest.raises(ValidationError):
        Eslesme(sembol=sembol, symbol_id=None, yontem="birebir", guven=1.0)
    with pytest.raises(ValidationError):
        Eslesme(sembol=sembol, symbol_id="uzay_gemisi", yontem="yok", guven=0.0)


def test_log_kaydinda_ruya_metni_yok(ornek_maddeler):
    gizli = "GİZLİRÜYAMETNİ"
    sembol = Sembol(yalin="yılan", nitelikler=["siyah"], ham_ifade=f"{gizli} yılan")
    kayit = SorguKaydi(
        zaman=dt.datetime(2026, 11, 20, 21, 0),
        girdi=RuyaGirdisi(metin=f"Rüyamda {gizli} gördüm"),
        cikarim=CikarimSonucu(semboller=[sembol]),
        eslesmeler=[Eslesme(sembol=sembol, symbol_id="yilan", yontem="birebir", guven=1.0)],
        getirilenler={"yilan": [Aday(madde=Madde.model_validate(ornek_maddeler[0]), skor=1.0)]},
        olcumler=[
            AdimOlcumu(
                adim="cikarim",
                sure_sn=1.5,
                kullanim=Kullanim(model="deepseek-v4.1-flash", maliyet_usd=0.01),
            ),
            AdimOlcumu(adim="esleme", sure_sn=0.01),
        ],
    )
    satir = json.dumps(kayit.log_kaydi(), ensure_ascii=False)
    assert gizli not in satir
    assert "siyah" not in satir
    assert kayit.log_kaydi()["eslesmeler"][0]["symbol_id"] == "yilan"
    assert kayit.toplam_maliyet_usd == pytest.approx(0.01)


def test_hyde_yalnizca_aramada_kullanilir():
    sembol = Sembol(yalin="yılan", ham_ifade="yılan")
    assert sembol.hyde is None
    sembol = Sembol(
        yalin="yılan",
        ham_ifade="yılan",
        hyde="Rüyada siyah yılan görmek, gizli ve güçlü bir düşmana işaret eder.",
    )
    assert sembol.hyde.startswith("Rüyada siyah yılan görmek")


def test_aday_pasaji(ornek_maddeler):
    aday = Aday(madde=Madde.model_validate(ornek_maddeler[0]), skor=1.0)
    assert aday.pasaj is None
    aday = Aday(
        madde=Madde.model_validate(ornek_maddeler[0]),
        skor=1.0,
        pasaj="Nablusi · حية (yılan). Sokarsa ayıp bulur.",
    )
    assert aday.pasaj == "Nablusi · حية (yılan). Sokarsa ayıp bulur."


def test_getirilenler_serbest_anahtar_alir(ornek_maddeler):
    aday = Aday(madde=Madde.model_validate(ornek_maddeler[0]), skor=0.5)
    kayit = SorguKaydi(
        zaman=dt.datetime(2026, 11, 20, 21, 0),
        girdi=RuyaGirdisi(metin="Rüyamda baba gördüm"),
        getirilenler={"yilan": [aday], "serbest:baba": [aday]},
    )
    assert kayit.log_kaydi()["madde_sayilari"] == {"yilan": 1, "serbest:baba": 1}


def test_getirme_anahtari():
    sembol = Sembol(yalin="yılan", ham_ifade="yılan")
    eslesme = Eslesme(sembol=sembol, symbol_id="yilan", yontem="birebir", guven=1.0)
    assert getirme_anahtari(eslesme) == "yilan"

    serbest = Sembol(yalin="baba", ham_ifade="baba")
    eslesme = Eslesme(sembol=serbest, symbol_id=None, yontem="yok", guven=0.0)
    assert getirme_anahtari(eslesme) == "serbest:baba"


def test_yorum_genel_yorum_varsayilan_none():
    yorum = Yorum(bolumler=[], uyari="u")
    assert yorum.genel_yorum is None


def test_yorum_metni_genel_yorumla_baslar():
    yorum = Yorum(
        bolumler=[YorumBolumu(metin="Yılan: x")],
        genel_yorum="Genel.",
        uyari="u",
    )
    assert yorum.metin.startswith("Genel.")
    assert "Genel." in yorum.metin
    assert "Yılan: x" in yorum.metin


def test_yorum_metni_genel_yorum_yoksa_bolumleri_birlestirir():
    yorum = Yorum(
        bolumler=[YorumBolumu(metin="Yılan: x"), YorumBolumu(metin="Deniz: y")],
        uyari="u",
    )
    assert yorum.metin == "Yılan: xDeniz: y"
