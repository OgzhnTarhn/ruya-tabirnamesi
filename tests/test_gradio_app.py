"""Arayüzün saf yardımcıları (docs/03, bölüm 5.4). Sunucu açılmaz, Gradio çağrılmaz."""

import datetime as dt
import sys
import threading
from pathlib import Path

import pytest

from ruya.etik import GUVENLIK_NOTU, REDDEDILDI_MESAJI, UYARI_METNI
from ruya.hatalar import ApiAnahtariYok, LLMHatasi, ModelReddetti, YanitKesildi
from ruya.schemas import (
    Aday,
    AdimOlcumu,
    Atif,
    CikarimSonucu,
    Eslesme,
    Konum,
    Kullanim,
    Madde,
    RuyaGirdisi,
    Sembol,
    SorguKaydi,
    Yorum,
    YorumBolumu,
)

# app/ bir paket değil; testler repo kökünden içe aktarır.
KOK = Path(__file__).resolve().parents[1]
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

from app import gradio_app, sunum  # noqa: E402

MADDE = Madde(
    entry_id="nablusi:0412",
    kaynak="nablusi",
    eser="Ta'birname",
    yazar="Nablusi",
    gelenek="islami_klasik",
    dil="ar",
    lisans="kamu_mali",
    konum=Konum(bab="yılan", satir=412),
    metin_asli="رأى حية ففسرها بعدو",
    metin_tr="Yılan görmek, düşmanla karşılaşmaya işarettir.",
)

ATIF = Atif(
    entry_id="nablusi:0412",
    baslik="Nablusi · حية (yılan)",
    alinti="رأى حية ففسرها بعدو",
)

KULLANIM = Kullanim(model="test-model", girdi_token=100, cikti_token=50, maliyet_usd=0.002)


def _kayit(yorum: Yorum | None = None, mesaj: str | None = None) -> SorguKaydi:
    sembol = Sembol(yalin="yılan", nitelikler=["siyah"], ham_ifade="yılan")
    return SorguKaydi(
        zaman=dt.datetime(2026, 11, 2, 12, 0, tzinfo=dt.UTC),
        girdi=RuyaGirdisi(metin="Rüyamda siyah bir yılan gördüm."),
        cikarim=CikarimSonucu(semboller=[sembol]),
        eslesmeler=[Eslesme(sembol=sembol, symbol_id="yilan", yontem="birebir", guven=0.95)],
        getirilenler={"yilan": [Aday(madde=MADDE, skor=0.9, gerekceler=["nitelik:siyah"])]},
        yorum=yorum,
        mesaj=mesaj,
        olcumler=[
            AdimOlcumu(adim="cikarim", sure_sn=0.5, kullanim=KULLANIM, talimat="cikarim_v1"),
            AdimOlcumu(adim="esleme", sure_sn=0.25),
        ],
    )


@pytest.fixture
def yorum() -> Yorum:
    return Yorum(
        bolumler=[
            YorumBolumu(metin="Yılan düşmanla karşılaşmaya işarettir.", atiflar=[ATIF]),
            YorumBolumu(
                metin="Siyah olması kaygıyı artırır.",
                atiflar=[Atif(entry_id="miller:007", baslik="Miller · Yılan", alinti="...")],
            ),
        ],
        bulunamayanlar=["deniz"],
        guvenlik_notu=GUVENLIK_NOTU,
        uyari=UYARI_METNI,
    )


# --- hata_ayiklama ----------------------------------------------------------


def test_hata_ayiklama_butun_izleri_tasir():
    ayiklama = gradio_app.hata_ayiklama(_kayit())
    assert isinstance(ayiklama, dict)
    assert {"semboller", "eslesmeler", "getirilenler", "olcumler"} <= set(ayiklama)

    assert "yılan" in str(ayiklama["semboller"])

    eslesmeler = str(ayiklama["eslesmeler"])
    assert "birebir" in eslesmeler
    assert "0.95" in eslesmeler

    getirilenler = str(ayiklama["getirilenler"])
    assert "nablusi:0412" in getirilenler
    assert "0.9" in getirilenler

    olcumler = str(ayiklama["olcumler"])
    assert "cikarim" in olcumler
    assert "0.5" in olcumler
    assert "100" in olcumler
    assert "50" in olcumler


# --- hata_mesaji ------------------------------------------------------------


def test_hata_mesaji_reddedilme_metni():
    assert gradio_app.hata_mesaji(ModelReddetti()) == REDDEDILDI_MESAJI


@pytest.mark.parametrize(
    "hata",
    [
        ApiAnahtariYok(),
        YanitKesildi(),
        LLMHatasi("geçit hatası", durum=500),
    ],
    ids=["api_anahtari_yok", "yanit_kesildi", "llm_hatasi"],
)
def test_hata_mesaji_turkce_ve_bos_degil(hata):
    mesaj = gradio_app.hata_mesaji(hata)
    assert isinstance(mesaj, str)
    assert mesaj.strip()
    assert type(hata).__name__ not in mesaj


def test_hata_mesaji_siniflara_gore_farkli():
    mesajlar = {
        gradio_app.hata_mesaji(ApiAnahtariYok()),
        gradio_app.hata_mesaji(ModelReddetti()),
        gradio_app.hata_mesaji(YanitKesildi()),
        gradio_app.hata_mesaji(LLMHatasi("geçit hatası", durum=500)),
    }
    assert len(mesajlar) == 4


# --- baslat -----------------------------------------------------------------


class _SahteDemo:
    def __init__(self) -> None:
        self.cagrilar: list[dict] = []

    def launch(self, **kwargs):
        self.cagrilar.append(kwargs)


def test_baslat_yerel_ve_paylasimsiz_acar(monkeypatch):
    demo = _SahteDemo()
    monkeypatch.setattr(gradio_app, "arayuz_kur", lambda bag: demo)

    sonuc = gradio_app.baslat(bag=None)

    assert sonuc is demo
    assert len(demo.cagrilar) == 1
    assert demo.cagrilar[0]["share"] is False
    assert demo.cagrilar[0]["server_name"] == "127.0.0.1"


# --- yorum_akisi ------------------------------------------------------------


def test_yorum_akisi_ara_ve_son_metinleri_sirayla_yayar(monkeypatch, yorum):
    k1 = _kayit()
    k2 = _kayit(yorum=yorum)
    final = _kayit(yorum=yorum)
    ana_ident = threading.get_ident()

    def sahte(girdi, bag, ilerleme=None):
        assert threading.get_ident() != ana_ident
        ilerleme("esleme", k1)
        ilerleme("sentez", k2)
        return final

    monkeypatch.setattr(gradio_app, "yorumla", sahte)

    parcalar = list(gradio_app.yorum_akisi(RuyaGirdisi(metin="rüya"), bag=None))

    assert parcalar == [
        (sunum.ilerleme_html("baslangic"), None),
        (sunum.akis_html("esleme", k1), None),
        (sunum.akis_html("sentez", k2), None),
        (sunum.akis_html("bitti", final), final),
    ]


def test_yorum_akisi_hata_mesajini_yayar_ve_bitirir(monkeypatch):
    k1 = _kayit()
    ana_ident = threading.get_ident()

    def sahte(girdi, bag, ilerleme=None):
        assert threading.get_ident() != ana_ident
        ilerleme("esleme", k1)
        raise LLMHatasi("x")

    monkeypatch.setattr(gradio_app, "yorumla", sahte)

    parcalar = list(gradio_app.yorum_akisi(RuyaGirdisi(metin="rüya"), bag=None))

    assert parcalar[0] == (sunum.ilerleme_html("baslangic"), None)
    assert parcalar[1] == (sunum.akis_html("esleme", k1), None)
    assert parcalar[-1] == (sunum.hata_html(gradio_app.hata_mesaji(LLMHatasi("x"))), None)
