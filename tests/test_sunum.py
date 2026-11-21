"""Sunum katmanının saf yardımcıları (docs/16). Sunucu açılmaz, Gradio çağrılmaz."""

import datetime as dt
import re
import sys
from pathlib import Path

import pytest

from ruya.etik import GUVENLIK_NOTU, SEMBOL_YOK_MESAJI, UYARI_METNI
from ruya.index.store import BellekDeposu
from ruya.schemas import (
    Atif,
    CikarimSonucu,
    Eslesme,
    Konum,
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

from app import sunum  # noqa: E402

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

ZAMAN = dt.datetime(2026, 11, 2, 12, 0, tzinfo=dt.UTC)


def _kayit(yorum: Yorum | None = None, mesaj: str | None = None) -> SorguKaydi:
    sembol = Sembol(yalin="yılan", nitelikler=["siyah"], ham_ifade="yılan")
    return SorguKaydi(
        zaman=ZAMAN,
        girdi=RuyaGirdisi(metin="Rüyamda siyah bir yılan gördüm."),
        cikarim=CikarimSonucu(semboller=[sembol]),
        eslesmeler=[Eslesme(sembol=sembol, symbol_id="yilan", yontem="birebir", guven=0.95)],
        yorum=yorum,
        mesaj=mesaj,
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


@pytest.fixture
def depo() -> BellekDeposu:
    return BellekDeposu([MADDE])


# --- Metin sabitleri --------------------------------------------------------


@pytest.mark.parametrize(
    "ad",
    [
        "BASLIK",
        "ALT_BASLIK",
        "NASIL_CALISIR",
        "RUYA_IPUCU",
        "GELENEK_ACIKLAMASI",
        "BAGLAM_ACIKLAMASI",
        "FOTO_ACIKLAMASI",
        "BEKLEME_NOTU",
        "BULUNAMAYAN_ACIKLAMASI",
    ],
)
def test_metin_sabitleri_bos_degil(ad):
    deger = getattr(sunum, ad)
    assert isinstance(deger, str)
    assert deger.strip()


def test_baslik_beklenen_metin():
    assert sunum.BASLIK == "Rüya Tabirnamesi"


def test_ornek_ruyalar_uc_dolu_metin():
    assert isinstance(sunum.ORNEK_RUYALAR, list)
    assert len(sunum.ORNEK_RUYALAR) == 3
    for ruya in sunum.ORNEK_RUYALAR:
        assert isinstance(ruya, str)
        assert ruya.strip()


def test_gelenek_aciklamasi_freudu_anar_hepsi_demez():
    assert "Freud" in sunum.GELENEK_ACIKLAMASI
    assert "hepsi" not in sunum.GELENEK_ACIKLAMASI


# --- Seçenek listeleri ------------------------------------------------------


@pytest.mark.parametrize(
    "ad,degerler,etiketler",
    [
        ("CINSIYET_SECENEKLERI", ["kadin", "erkek"], ["Kadın", "Erkek"]),
        ("MEDENI_HAL_SECENEKLERI", ["evli", "bekar"], ["Evli", "Bekâr"]),
        (
            "MEVSIM_SECENEKLERI",
            ["ilkbahar", "yaz", "sonbahar", "kis"],
            ["İlkbahar", "Yaz", "Sonbahar", "Kış"],
        ),
        ("GURBET_SECENEKLERI", ["evet", "hayır"], ["Evet", "Hayır"]),
    ],
)
def test_baglam_secenekleri_etiket_ve_deger(ad, degerler, etiketler):
    secenekler = getattr(sunum, ad)
    assert [deger for _, deger in secenekler] == degerler
    assert [etiket for etiket, _ in secenekler] == etiketler


def test_gelenekler_degerleri_ve_etiketleri():
    assert [deger for _, deger in sunum.GELENEKLER] == [
        "islami_klasik",
        "bati_halk",
        "psikanalitik",
    ]
    etiketler = [etiket for etiket, _ in sunum.GELENEKLER]
    assert "Nablusi" in etiketler[0]
    assert "Miller" in etiketler[1]
    assert "Freud" in etiketler[2]


# --- bolum_basligi ----------------------------------------------------------


def test_bolum_basligi_ilk_iki_noktadan_boler():
    baslik, govde = sunum.bolum_basligi(
        "Yılan (siyah): Nablusi'nin tabirnamesine göre düşmanla karşılaşmaya işarettir."
    )
    assert baslik == "Yılan (siyah)"
    assert govde == "Nablusi'nin tabirnamesine göre düşmanla karşılaşmaya işarettir."


def test_bolum_basligi_iki_nokta_yoksa_bolmez():
    metin = "Yılan düşmanla karşılaşmaya işarettir."
    assert sunum.bolum_basligi(metin) == (None, metin)


def test_bolum_basligi_uzun_onek_bolmez():
    metin = "a" * 61 + ": gövde"
    assert sunum.bolum_basligi(metin) == (None, metin)


def test_bolum_basligi_noktali_onek_bolmez():
    metin = "Yılan. Siyah: gövde"
    assert sunum.bolum_basligi(metin) == (None, metin)


# --- yorum_html -------------------------------------------------------------


def test_yorum_html_yorum_yoksa_mesaji_gosterir():
    html = sunum.yorum_html(_kayit(yorum=None, mesaj="Özel mesaj."))
    assert "Özel mesaj." in html


def test_yorum_html_yorum_yoksa_sembol_yok_mesajini_gosterir():
    html = sunum.yorum_html(_kayit(yorum=None, mesaj=None))
    assert SEMBOL_YOK_MESAJI in html


def test_yorum_html_bolum_metinlerini_ve_numarali_atiflari_yazar(yorum):
    html = sunum.yorum_html(_kayit(yorum=yorum))
    for bolum in yorum.bolumler:
        assert bolum.metin in html
    assert "[1]" in html
    assert "[2]" in html
    assert ATIF.baslik in html
    assert "Miller · Yılan" in html


def test_yorum_html_bolum_basligini_h3_olarak_yazar():
    yorum = Yorum(
        bolumler=[
            YorumBolumu(
                metin=(
                    "Yılan (siyah): Nablusi'nin tabirnamesine göre düşmanla karşılaşmaya işarettir."
                ),
                atiflar=[ATIF],
            )
        ],
        uyari=UYARI_METNI,
    )
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert "Nablusi'nin tabirnamesine göre düşmanla karşılaşmaya işarettir." in html
    assert re.search(r"<h3[^>]*>Yılan \(siyah\)</h3>", html)


def test_yorum_html_kaynaklari_details_olarak_yazar(yorum):
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert html.count("<details") == 2


def test_yorum_html_depo_verilince_ceviri_ve_asli_gosterir(yorum, depo):
    html = sunum.yorum_html(_kayit(yorum=yorum), depo)
    assert MADDE.metin_tr in html
    assert MADDE.metin_asli in html


def test_yorum_html_depo_yoksa_alintiyi_gosterir(yorum):
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert ATIF.alinti in html


def test_yorum_html_depoda_olmayan_kayit_yine_cizilir(yorum, depo):
    html = sunum.yorum_html(_kayit(yorum=yorum), depo)
    assert "Miller · Yılan" in html


def test_yorum_html_genel_yorumu_gosterir(yorum):
    yorum.genel_yorum = "Gelenekte bu rüya genel olarak hayra yorulur."
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert yorum.genel_yorum in html


def test_yorum_html_guvenlik_notunu_gosterir(yorum):
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert GUVENLIK_NOTU in html


def test_yorum_html_bulunamayanlari_ve_aciklamasini_gosterir(yorum):
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert "deniz" in html
    assert sunum.BULUNAMAYAN_ACIKLAMASI in html


def test_yorum_html_uyari_metnini_yazmaz(yorum):
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert UYARI_METNI not in html


def test_yorum_html_metni_kacar():
    yorum = Yorum(
        bolumler=[YorumBolumu(metin="Başlık: <script>alert(1)</script>", atiflar=[])],
        uyari=UYARI_METNI,
    )
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert "&lt;script&gt;" in html
    assert "<script>" not in html


# --- semboller_html ---------------------------------------------------------


def test_semboller_html_eslesen_sembolleri_yazar():
    html = sunum.semboller_html(_kayit())
    assert "yılan" in html


def test_semboller_html_olumsuz_sembolu_isaretler():
    sembol = Sembol(yalin="yılan", olumsuz=True, ham_ifade="yılan görmedim")
    kayit = SorguKaydi(
        zaman=ZAMAN,
        girdi=RuyaGirdisi(metin="Rüyamda yılan görmedim."),
        cikarim=CikarimSonucu(semboller=[sembol]),
    )
    html = sunum.semboller_html(kayit)
    assert "ruya-rozet--olumsuz" in html
    assert "yılan" in html


def test_semboller_html_bos_kayitta_bos_doner():
    kayit = SorguKaydi(zaman=ZAMAN, girdi=RuyaGirdisi(metin="Rüyamda bir şey gördüm."))
    assert sunum.semboller_html(kayit) == ""


# --- ilerleme_html ----------------------------------------------------------


@pytest.mark.parametrize(
    "asama,durumlar",
    [
        ("baslangic", ("suruyor", "bekliyor", "bekliyor")),
        ("esleme", ("tamam", "suruyor", "bekliyor")),
        ("getirme", ("tamam", "tamam", "suruyor")),
        ("sentez", ("tamam", "tamam", "suruyor")),
        ("bitti", ("tamam", "tamam", "tamam")),
        ("bilinmeyen", ("suruyor", "bekliyor", "bekliyor")),
    ],
)
def test_ilerleme_html_adim_durumlari(asama, durumlar):
    html = sunum.ilerleme_html(asama)
    for etiket in ("Semboller", "Kaynaklar", "Yorum"):
        assert etiket in html
    assert html.count("ruya-adim--") == 3
    for durum in ("tamam", "suruyor", "bekliyor"):
        assert html.count(f"ruya-adim--{durum}") == durumlar.count(durum)


@pytest.mark.parametrize("asama", ["baslangic", "esleme", "getirme", "sentez", "bilinmeyen"])
def test_ilerleme_html_bekleme_notunu_yazar(asama):
    assert sunum.BEKLEME_NOTU in sunum.ilerleme_html(asama)


def test_ilerleme_html_bitti_asamasinda_bekleme_notu_yok():
    assert sunum.BEKLEME_NOTU not in sunum.ilerleme_html("bitti")


# --- akis_html --------------------------------------------------------------


def test_akis_html_ilerleme_ile_baslar_ve_sembolleri_yazar(yorum):
    kayit = _kayit(yorum=yorum)
    html = sunum.akis_html("esleme", kayit)
    assert html.startswith(sunum.ilerleme_html("esleme"))
    assert "yılan" in html


def test_akis_html_sentez_asamasinda_bolumleri_yazar(yorum):
    kayit = _kayit(yorum=yorum)
    html = sunum.akis_html("sentez", kayit)
    for bolum in yorum.bolumler:
        assert bolum.metin in html


def test_yorum_html_yildizli_eser_adini_italik_yapar_ve_kacirir():
    yorum = Yorum(
        bolumler=[YorumBolumu(metin="Yılan: *Muntahab*'a göre <b>düşman</b>.", atiflar=[])],
        uyari=UYARI_METNI,
    )
    html = sunum.yorum_html(_kayit(yorum=yorum))
    assert "<em>Muntahab</em>" in html
    assert "&lt;b&gt;düşman&lt;/b&gt;" in html


def test_akis_html_yorum_yokken_sembol_yok_mesaji_gostermez():
    html = sunum.akis_html("esleme", _kayit())
    assert SEMBOL_YOK_MESAJI not in html
    assert "yılan" in html


def test_akis_html_bitti_asamasinda_sembolleri_ve_yorumu_birlikte_yazar(yorum):
    kayit = _kayit(yorum=yorum)
    html = sunum.akis_html("bitti", kayit)
    assert "ruya-rozet" in html
    assert "ruya-bolum" in html
    assert sunum.BEKLEME_NOTU not in html


# --- hata_html --------------------------------------------------------------


def test_hata_html_mesaji_kacar_ve_sinifi_tasir():
    html = sunum.hata_html("<b>bozuk</b>")
    assert "ruya-hata" in html
    assert "&lt;b&gt;bozuk&lt;/b&gt;" in html
    assert "<b>bozuk</b>" not in html
