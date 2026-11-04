"""Görselden rüya okuma (OCR) yardımcısı ve hata ayıklama izleri.

Sunucu açılmaz, Gradio çağrılmaz; istemci küçük bir sahte nesneyle değiştirilir.
"""

import datetime as dt
import sys
from pathlib import Path

import pytest

from ruya.hatalar import LLMHatasi
from ruya.schemas import (
    Aday,
    CikarimSonucu,
    Konum,
    Madde,
    RuyaGirdisi,
    SorguKaydi,
)

# app/ bir paket değil; testler repo kökünden içe aktarır.
KOK = Path(__file__).resolve().parents[1]
if str(KOK) not in sys.path:
    sys.path.insert(0, str(KOK))

from app import gradio_app  # noqa: E402

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


class _SahteIstemci:
    """ocr çağrılarını kaydeden, yanıtı ya da hatayı döndüren küçük sahte."""

    def __init__(self, yanit: str = "", hata: BaseException | None = None) -> None:
        self.yanit = yanit
        self.hata = hata
        self.cagrilar: list[tuple[bytes, str]] = []

    def ocr(self, veri: bytes, mime: str) -> str:
        self.cagrilar.append((veri, mime))
        if self.hata is not None:
            raise self.hata
        return self.yanit


def _kayit(adaylar: list[Aday]) -> SorguKaydi:
    return SorguKaydi(
        zaman=dt.datetime(2026, 11, 2, 12, 0, tzinfo=dt.UTC),
        girdi=RuyaGirdisi(metin="Rüyamda siyah bir yılan gördüm."),
        cikarim=CikarimSonucu(semboller=[]),
        getirilenler={"yilan": adaylar},
    )


# --- gorselden_ruya ---------------------------------------------------------


def test_gorselden_ruya_dosyayi_okur_ve_mime_tahmin_eder(tmp_path):
    yol = tmp_path / "ruya.png"
    yol.write_bytes(b"\x89PNG sahte goruntu")
    istemci = _SahteIstemci(yanit="  Rüyamda bir yılan gördüm.  ")

    metin = gradio_app.gorselden_ruya(str(yol), istemci)

    assert metin == "Rüyamda bir yılan gördüm."
    assert len(istemci.cagrilar) == 1
    veri, mime = istemci.cagrilar[0]
    assert veri == b"\x89PNG sahte goruntu"
    assert mime == "image/png"


@pytest.mark.parametrize(
    ("uzanti", "mime"),
    [(".jpg", "image/jpeg"), (".jpeg", "image/jpeg"), (".webp", "image/webp")],
)
def test_gorselden_ruya_uzantidan_mime_tahmin_eder(tmp_path, uzanti, mime):
    yol = tmp_path / f"ruya{uzanti}"
    yol.write_bytes(b"veri")
    istemci = _SahteIstemci(yanit="metin")

    gradio_app.gorselden_ruya(str(yol), istemci)

    assert istemci.cagrilar[0][1] == mime


def test_gorselden_ruya_metni_3000_karaktere_kirpar(tmp_path):
    yol = tmp_path / "uzun.png"
    yol.write_bytes(b"veri")
    istemci = _SahteIstemci(yanit="a" * 5000)

    metin = gradio_app.gorselden_ruya(str(yol), istemci)

    assert len(metin) == 3000
    assert metin == "a" * 3000


def test_gorselden_ruya_yol_yoksa_bos_doner():
    istemci = _SahteIstemci(yanit="metin")

    assert gradio_app.gorselden_ruya(None, istemci) == ""
    assert istemci.cagrilar == []


def test_gorselden_ruya_llm_hatasini_mesaja_cevirir(tmp_path):
    yol = tmp_path / "ruya.png"
    yol.write_bytes(b"veri")
    istemci = _SahteIstemci(hata=LLMHatasi("geçit hatası", durum=500))

    metin = gradio_app.gorselden_ruya(str(yol), istemci)

    assert isinstance(metin, str)
    assert metin == gradio_app.hata_mesaji(LLMHatasi("geçit hatası", durum=500))
    assert "LLMHatasi" not in metin


def test_gorselden_ruya_desteklenmeyen_uzanti_ocr_cagirmaz(tmp_path):
    yol = tmp_path / "ruya.txt"
    yol.write_text("düz metin", encoding="utf-8")
    istemci = _SahteIstemci(yanit="metin")

    metin = gradio_app.gorselden_ruya(str(yol), istemci)

    assert isinstance(metin, str)
    assert metin.strip()
    assert istemci.cagrilar == []


# --- hata_ayiklama: getirilen adayların gerekçe ve pasajı -------------------


def test_hata_ayiklama_gerekce_ve_pasaji_tasir():
    aday = Aday(
        madde=MADDE,
        skor=0.9,
        gerekceler=["nitelik:siyah", "baslikli"],
        pasaj="Yılan görmek, düşmanla karşılaşmaya işarettir.",
    )

    ayiklama = gradio_app.hata_ayiklama(_kayit([aday]))

    getirilen = ayiklama["getirilenler"][0]
    assert getirilen["symbol_id"] == "yilan"
    assert getirilen["entry_id"] == "nablusi:0412"
    assert getirilen["gerekceler"] == ["nitelik:siyah", "baslikli"]
    assert getirilen["pasaj"] == "Yılan görmek, düşmanla karşılaşmaya işarettir."


def test_hata_ayiklama_pasaj_yoksa_none_tasir():
    aday = Aday(madde=MADDE, skor=0.5, gerekceler=[])

    ayiklama = gradio_app.hata_ayiklama(_kayit([aday]))

    getirilen = ayiklama["getirilenler"][0]
    assert getirilen["gerekceler"] == []
    assert getirilen["pasaj"] is None
