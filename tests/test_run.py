"""Orkestrasyonun testi: dört adım sahteleriyle değiştirilir, API çağrılmaz."""

import pytest

from ruya.config import Ayarlar
from ruya.etik import SEMBOL_YOK_MESAJI, UYARI_METNI
from ruya.pipeline import extract, retrieve, run, synthesize
from ruya.pipeline import map as esleme
from ruya.schemas import (
    CikarimSonucu,
    Eslesme,
    Kullanim,
    RuyaGirdisi,
    Sembol,
    Yorum,
)

KULLANIM = Kullanim(model="deepseek-v4.1-flash", girdi_token=100, cikti_token=50, maliyet_usd=0.002)


@pytest.fixture
def bag():
    return run.Bagimliliklar(
        istemci=None, varyantlar={}, depo=None, ayar=Ayarlar(en_fazla_sembol=2)
    )


@pytest.fixture
def sahte_adimlar(monkeypatch):
    cagrilar = {}

    def sahte_extract(girdi, istemci):
        semboller = [Sembol(yalin=k, ham_ifade=k) for k in girdi.metin.split()]
        return CikarimSonucu(semboller=semboller), KULLANIM

    def sahte_map(semboller, varyantlar, vektor):
        cagrilar["esleme"] = [s.yalin for s in semboller]
        return [
            Eslesme(sembol=s, symbol_id=s.yalin, yontem="birebir", guven=1.0) for s in semboller
        ]

    def sahte_retrieve(eslesmeler, depo, baglam, gelenekler, n):
        cagrilar["n"] = n
        return {e.symbol_id: [] for e in eslesmeler}

    def sahte_synthesize(cikarim, eslesmeler, getirilenler, baglam, istemci):
        return Yorum(bolumler=[], bulunamayanlar=list(getirilenler), uyari=UYARI_METNI), KULLANIM

    monkeypatch.setattr(extract, "extract", sahte_extract)
    monkeypatch.setattr(esleme, "map_symbols", sahte_map)
    monkeypatch.setattr(retrieve, "retrieve", sahte_retrieve)
    monkeypatch.setattr(synthesize, "synthesize", sahte_synthesize)
    return cagrilar


def test_dort_adim_sirayla_izlenir(bag, sahte_adimlar):
    kayit = run.yorumla(RuyaGirdisi(metin="deniz yilan"), bag)
    assert [o.adim for o in kayit.olcumler] == ["cikarim", "esleme", "getirme", "sentez"]
    assert kayit.yorum.uyari == UYARI_METNI
    assert kayit.toplam_maliyet_usd == pytest.approx(0.004)
    assert kayit.olcumler[0].talimat == extract.TALIMAT
    assert sahte_adimlar["n"] == 1


def test_fazla_sembol_atlanir(bag, sahte_adimlar):
    kayit = run.yorumla(RuyaGirdisi(metin="deniz yilan kus ev"), bag)
    assert sahte_adimlar["esleme"] == ["deniz", "yilan"]
    assert kayit.atlanan_semboller == ["kus", "ev"]


def test_sembol_yoksa_erken_doner(bag, sahte_adimlar, monkeypatch):
    monkeypatch.setattr(
        extract, "extract", lambda girdi, istemci: (CikarimSonucu(semboller=[]), KULLANIM)
    )
    kayit = run.yorumla(RuyaGirdisi(metin="hiçbir şey"), bag)
    assert kayit.mesaj == SEMBOL_YOK_MESAJI
    assert kayit.yorum is None
    assert [o.adim for o in kayit.olcumler] == ["cikarim"]
