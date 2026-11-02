"""Değerlendirme çalıştırıcısının testi: boru hattı sahteyle değiştirilir, API çağrılmaz.

Rapor ``bag.ayar.rapor_klasoru`` altına yazılır; testler geçici bir veri klasörü kurar.
Kişisel (özel) örneklerin işareti ``TestOrnegi.notlar`` alanındadır: notlarında "özel"
geçen örneğin rüya metni ne rapora ne de ekrana yazılır.
"""

import datetime as dt
import json
from pathlib import Path

import pytest

from ruya.config import Ayarlar
from ruya.degerlendirme.calistir import degerlendir
from ruya.etik import UYARI_METNI
from ruya.hatalar import ModelReddetti
from ruya.pipeline import run
from ruya.schemas import (
    AdimOlcumu,
    CikarimSonucu,
    Eslesme,
    Kullanim,
    RuyaGirdisi,
    Sembol,
    SorguKaydi,
    Yorum,
    YorumBolumu,
)

KULLANIM = Kullanim(model="deepseek-v4.1-flash", girdi_token=100, cikti_token=50, maliyet_usd=0.0)
# İki adım × (100 + 50) token = 300 token; 1,5 + 0,5 = 2,0 saniye.
TOPLAM_TOKEN = 300
TOPLAM_SURE = 2.0

ORNEKLER = [
    {
        "id": "r001",
        "metin": "Rüyamda denize girdim, sudan siyah bir yılan çıktı.",
        "beklenen_semboller": ["deniz", "yilan"],
        "beklenen_nitelikler": {"yilan": ["siyah"]},
        "notlar": "sıradan örnek",
    },
    {
        "id": "r002",
        "metin": "Yılan görmedim ama çok korktum.",
        "beklenen_semboller": [],
        "olmamasi_gerekenler": ["yilan"],
        "notlar": "olumsuzlama testi",
    },
    {
        "id": "r003",
        "metin": "Ölmüş babamı gördüm.",
        "beklenen_semboller": ["olmus_baba"],
        "notlar": "çok kelimeli sembol",
    },
]


def _kayit(girdi: RuyaGirdisi) -> SorguKaydi:
    sembol = Sembol(yalin="yilan", ham_ifade="yılan")
    return SorguKaydi(
        zaman=dt.datetime.now(dt.UTC),
        girdi=girdi,
        cikarim=CikarimSonucu(semboller=[sembol]),
        eslesmeler=[Eslesme(sembol=sembol, symbol_id="yilan", yontem="birebir", guven=1.0)],
        getirilenler={},
        yorum=Yorum(bolumler=[YorumBolumu(metin="Yorum metni.")], uyari=UYARI_METNI),
        olcumler=[
            AdimOlcumu(adim="cikarim", sure_sn=1.5, kullanim=KULLANIM, talimat="cikarim_v1"),
            AdimOlcumu(adim="sentez", sure_sn=0.5, kullanim=KULLANIM, talimat="sentez_v1"),
        ],
    )


@pytest.fixture
def bag(tmp_path: Path) -> run.Bagimliliklar:
    return run.Bagimliliklar(
        istemci=None, varyantlar={}, depo=None, ayar=Ayarlar(data_dir=tmp_path)
    )


@pytest.fixture
def veri_seti(tmp_path: Path) -> Path:
    yol = tmp_path / "ruyalar_test.jsonl"
    yol.write_text(
        "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in ORNEKLER), encoding="utf-8"
    )
    return yol


@pytest.fixture
def sahte_yorumla(monkeypatch):
    """``run.yorumla`` yerine geçer; çağrılan rüyaları kaydeder."""
    cagrilar: list[RuyaGirdisi] = []

    def yorumla(girdi: RuyaGirdisi, bag: run.Bagimliliklar) -> SorguKaydi:
        cagrilar.append(girdi)
        return _kayit(girdi)

    monkeypatch.setattr(run, "yorumla", yorumla)
    return cagrilar


def test_rapor_yolu_ve_adi(bag, veri_seti, sahte_yorumla):
    rapor = degerlendir(veri_seti, "asama1-test", bag)

    beklenen = bag.ayar.rapor_klasoru / f"{dt.date.today().isoformat()}_asama1-test.md"
    assert rapor == beklenen
    assert rapor.is_file()


def test_her_ornek_bir_kez_calistirilir(bag, veri_seti, sahte_yorumla):
    degerlendir(veri_seti, "asama1-test", bag)

    assert [g.metin for g in sahte_yorumla] == [o["metin"] for o in ORNEKLER]
    assert sahte_yorumla[0].baglam is None


def test_rapor_olcut_tablosu_icerir(bag, veri_seti, sahte_yorumla):
    rapor = degerlendir(veri_seti, "asama1-test", bag)
    metin = rapor.read_text(encoding="utf-8")

    assert "|---" in metin  # markdown tablosu
    kucuk = metin.lower()
    assert "recall" in kucuk
    assert "precision" in kucuk


def test_toplam_token_ve_sure_yazilir(bag, veri_seti, sahte_yorumla):
    rapor = degerlendir(veri_seti, "asama1-test", bag)
    metin = rapor.read_text(encoding="utf-8")

    assert str(TOPLAM_TOKEN) in metin
    sure_bicimleri = {
        f"{TOPLAM_SURE:.1f}",
        f"{TOPLAM_SURE:.2f}",
        f"{TOPLAM_SURE:.1f}".replace(".", ","),
        f"{TOPLAM_SURE:.2f}".replace(".", ","),
    }
    assert any(bicim in metin for bicim in sure_bicimleri)
    assert "token" in metin.lower()


def test_sadakat_kontrol_listesi_bos_gelir(bag, veri_seti, sahte_yorumla):
    rapor = degerlendir(veri_seti, "asama1-test", bag)
    metin = rapor.read_text(encoding="utf-8")

    assert "sadakat" in metin.lower()
    assert metin.count("- [ ]") >= 3
    assert "- [x]" not in metin.lower()


def test_ruya_hatasi_basarisiz_olarak_kaydedilir_ve_kosu_surer(bag, veri_seti, monkeypatch):
    cagrilar: list[str] = []

    def yorumla(girdi: RuyaGirdisi, bag: run.Bagimliliklar) -> SorguKaydi:
        cagrilar.append(girdi.metin)
        if girdi.metin == ORNEKLER[1]["metin"]:
            raise ModelReddetti("model isteği reddetti")
        return _kayit(girdi)

    monkeypatch.setattr(run, "yorumla", yorumla)

    rapor = degerlendir(veri_seti, "asama1-test", bag)
    metin = rapor.read_text(encoding="utf-8")

    assert len(cagrilar) == len(ORNEKLER)  # koşu devam etti
    assert "r002" in metin
    assert "model isteği reddetti" in metin
    assert "başarısız" in metin.lower()


def test_ozel_ornegin_metni_yazilmaz(bag, tmp_path, monkeypatch, capsys):
    ozel_metin = "GİZLİ RÜYA METNİ: kimsede görünmemeli"
    ornekler = [
        {"id": "r001", "metin": "Rüyamda deniz gördüm.", "notlar": "sıradan"},
        {"id": "r002", "metin": ozel_metin, "notlar": "özel: kişisel rüya"},
    ]
    veri_seti = tmp_path / "ruyalar_test.jsonl"
    veri_seti.write_text(
        "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in ornekler), encoding="utf-8"
    )

    cagrilar: list[str] = []

    def yorumla(girdi: RuyaGirdisi, bag: run.Bagimliliklar) -> SorguKaydi:
        cagrilar.append(girdi.metin)
        return _kayit(girdi)

    monkeypatch.setattr(run, "yorumla", yorumla)

    rapor = degerlendir(veri_seti, "asama1-test", bag)
    metin = rapor.read_text(encoding="utf-8")
    cikti = capsys.readouterr()

    assert len(cagrilar) == 2  # özel örnek de çalıştırılır
    assert ozel_metin not in metin
    assert ozel_metin not in cikti.out
    assert ozel_metin not in cikti.err
