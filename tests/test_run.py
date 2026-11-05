"""Orkestrasyonun testi: dört adım sahteleriyle değiştirilir, API çağrılmaz."""

import pytest

from ruya.config import Ayarlar
from ruya.etik import SEMBOL_YOK_MESAJI, UYARI_METNI
from ruya.pipeline import extract, hibrit, retrieve, run, synthesize
from ruya.pipeline import map as esleme
from ruya.schemas import (
    Baglam,
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
    cagrilar = {"eslenmeyen": set()}

    def sahte_extract(girdi, istemci):
        semboller = [Sembol(yalin=k, ham_ifade=k) for k in girdi.metin.split()]
        return CikarimSonucu(semboller=semboller), KULLANIM

    def sahte_map(semboller, varyantlar):
        cagrilar["esleme"] = [s.yalin for s in semboller]
        return [
            Eslesme(
                sembol=s,
                symbol_id=None if s.yalin in cagrilar["eslenmeyen"] else s.yalin,
                yontem="yok" if s.yalin in cagrilar["eslenmeyen"] else "birebir",
                guven=0.0 if s.yalin in cagrilar["eslenmeyen"] else 1.0,
            )
            for s in semboller
        ]

    def sahte_retrieve(eslesmeler, depo, baglam, gelenekler, n):
        cagrilar["n"] = n
        return {e.symbol_id: [] for e in eslesmeler}

    def sahte_synthesize(cikarim, eslesmeler, getirilenler, baglam, istemci):
        bulunamayanlar = [sid for sid in getirilenler if sid is not None]
        return Yorum(bolumler=[], bulunamayanlar=bulunamayanlar, uyari=UYARI_METNI), KULLANIM

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


def test_eslenmeyen_sembol_siniri_kullanmaz(bag, sahte_adimlar):
    sahte_adimlar["eslenmeyen"] = {"a"}
    kayit = run.yorumla(RuyaGirdisi(metin="a b c d"), bag)
    assert sahte_adimlar["esleme"] == ["a", "b", "c", "d"]
    assert [e.sembol.yalin for e in kayit.eslesmeler] == ["a", "b", "c"]
    assert kayit.atlanan_semboller == ["d"]


@pytest.fixture
def sahte_hibrit(monkeypatch):
    """``hibrit.hibrit_getir`` sahtesi: çağrının argümanlarını kaydeder."""
    cagrilar: dict[str, object] = {}

    def sahte_hibrit_getir(*argumanlar, **anahtar_kelimeler):
        cagrilar["argumanlar"] = argumanlar
        cagrilar["anahtar_kelimeler"] = anahtar_kelimeler
        return {}

    monkeypatch.setattr(hibrit, "hibrit_getir", sahte_hibrit_getir)
    return cagrilar


def _hibrit_degerleri(cagrilar: dict[str, object]) -> list[object]:
    return list(cagrilar.get("argumanlar", ())) + list(
        cagrilar.get("anahtar_kelimeler", {}).values()
    )


def test_hibrit_bagimliligi_varsa_hibrit_getir_kullanilir(sahte_adimlar, sahte_hibrit, monkeypatch):
    def patlat(*argumanlar, **anahtar_kelimeler):
        raise AssertionError("hibrit varken retrieve.retrieve çağrılmamalı")

    monkeypatch.setattr(retrieve, "retrieve", patlat)
    indeks = object()
    bag = run.Bagimliliklar(
        istemci=None, varyantlar={}, depo=None, ayar=Ayarlar(en_fazla_sembol=2), hibrit=indeks
    )
    girdi = RuyaGirdisi(
        metin="deniz yilan", baglam=Baglam(mevsim="yaz"), gelenekler=["islami_klasik"]
    )

    kayit = run.yorumla(girdi, bag)

    assert [o.adim for o in kayit.olcumler] == ["cikarim", "esleme", "getirme", "sentez"]
    degerler = _hibrit_degerleri(sahte_hibrit)
    assert indeks in degerler
    assert bag.ayar.kaynak_basina_n in degerler
    assert girdi.baglam in degerler
    assert girdi.gelenekler in degerler


def test_hibrit_bagimliligi_yoksa_retrieve_kullanilir(bag, sahte_adimlar, sahte_hibrit):
    run.yorumla(RuyaGirdisi(metin="deniz yilan"), bag)

    assert sahte_hibrit == {}
    assert sahte_adimlar["n"] == bag.ayar.kaynak_basina_n


def test_sembol_yoksa_erken_doner(bag, sahte_adimlar, monkeypatch):
    monkeypatch.setattr(
        extract, "extract", lambda girdi, istemci: (CikarimSonucu(semboller=[]), KULLANIM)
    )
    kayit = run.yorumla(RuyaGirdisi(metin="hiçbir şey"), bag)
    assert kayit.mesaj == SEMBOL_YOK_MESAJI
    assert kayit.yorum is None
    assert [o.adim for o in kayit.olcumler] == ["cikarim"]


def test_eslesmeyen_genel_fiil_getirmeye_gitmez(bag, sahte_adimlar):
    sahte_adimlar["eslenmeyen"] = {"kullanmak"}

    kayit = run.yorumla(RuyaGirdisi(metin="deniz kullanmak"), bag)

    assert [e.sembol.yalin for e in kayit.eslesmeler] == ["deniz"]
    assert "kullanmak" not in kayit.yorum.bulunamayanlar


def test_yalniz_genel_fiil_varsa_sembol_yok_mesaji_doner(bag, sahte_adimlar):
    sahte_adimlar["eslenmeyen"] = {"kullanmak"}

    kayit = run.yorumla(RuyaGirdisi(metin="kullanmak"), bag)

    assert kayit.mesaj == SEMBOL_YOK_MESAJI
    assert kayit.yorum is None
    assert [o.adim for o in kayit.olcumler] == ["cikarim", "esleme"]
