"""Adım 2 · Eşleme testleri: sembol → symbol_id (docs/03, Adım 2).

zeyrek ağır bir analizör olduğu için ``ruya.pipeline.map.kokler`` sahtesiyle değiştirilir;
testler gerçek analizöre bağlı değildir.
"""

import pytest

from ruya.pipeline import map as map_mod
from ruya.schemas import Sembol
from ruya.text import turkce


def _sembol(yalin: str) -> Sembol:
    return Sembol(yalin=yalin, ham_ifade=yalin)


@pytest.fixture
def kok_yok(monkeypatch):
    """Kök bulunamayan analizör sahtesi."""
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)


def test_birebir_eslesme(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("yılan")], {"yılan": "yilan"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "yilan"
    assert eslesme.yontem == "birebir"
    assert eslesme.guven == 1.0


def test_birebir_eslesme_normallestirir(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("  Yılanlar! ")], {"yılanlar": "yilan"})

    assert eslesmeler[0].symbol_id == "yilan"
    assert eslesmeler[0].yontem == "birebir"
    assert eslesmeler[0].guven == 1.0


def test_kok_eslesmesi(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: ["yılan"], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("yılanlar")], {"yılan": "yilan"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "yilan"
    assert eslesme.yontem == "kok"
    assert eslesme.guven == 0.9


def test_eslesme_yok(kok_yok):
    eslesmeler = map_mod.map_symbols([_sembol("bilinmeyen")], {"yılan": "yilan"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id is None
    assert eslesme.yontem == "yok"
    assert eslesme.guven == 0.0


def test_her_sembol_icin_bir_eslesme_ve_sira_korunur(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)
    semboller = [_sembol("yılan"), _sembol("bilinmeyen"), _sembol("deve")]

    eslesmeler = map_mod.map_symbols(semboller, {"yılan": "yilan", "deve": "deve"})

    assert len(eslesmeler) == len(semboller)
    assert [e.sembol.yalin for e in eslesmeler] == ["yılan", "bilinmeyen", "deve"]
    assert [e.yontem for e in eslesmeler] == ["birebir", "yok", "birebir"]


def test_bos_girdi_bos_cikti(kok_yok):
    assert map_mod.map_symbols([], {"yılan": "yilan"}) == []


def test_cok_kelimeli_ifade_parca_eslesmesi(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("güvercin sürüsü")], {"güvercin": "guvercin"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "guvercin"
    assert eslesme.yontem == "parca"
    assert eslesme.guven == 0.8


def test_cok_kelimeli_ifade_kok_ile_parca(monkeypatch):
    monkeypatch.setattr(
        map_mod, "kokler", lambda kelime: ["namaz"] if kelime == "namazı" else [], raising=False
    )

    eslesmeler = map_mod.map_symbols([_sembol("sabah namazı")], {"namaz": "namaz"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "namaz"
    assert eslesme.yontem == "parca"


def test_cok_kelimeli_ifade_ilk_kelimeyi_gecer_sonra_durur(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols(
        [_sembol("deniz kenarı")], {"deniz": "deniz", "kenar": "kenar"}
    )

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "deniz"
    assert eslesme.yontem == "parca"


def test_cok_kelimeli_ifade_hicbir_kelime_eslesmezse_yok(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("hastane koridoru")], {"yılan": "yilan"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id is None
    assert eslesme.yontem == "yok"
    assert eslesme.guven == 0.0


def test_tek_kelime_parca_kullanmaz(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("sürüsü")], {"sürü": "suru"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id is None
    assert eslesme.yontem == "yok"


def test_tam_ifade_birebir_parcalardan_once_gelir(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: [], raising=False)

    eslesmeler = map_mod.map_symbols(
        [_sembol("güvercin sürüsü")],
        {"güvercin sürüsü": "guvercin_surusu", "güvercin": "guvercin"},
    )

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "guvercin_surusu"
    assert eslesme.yontem == "birebir"
    assert eslesme.guven == 1.0


def test_kokler_analizor_hata_verirse_bos_liste(monkeypatch):
    def _patlat() -> None:
        raise RuntimeError("zeyrek yüklenemedi")

    monkeypatch.setattr(turkce, "_cozumleyici", _patlat, raising=False)

    assert turkce.kokler("yılanlar") == []
