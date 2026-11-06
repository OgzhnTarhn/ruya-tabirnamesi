"""Adım 2 · Eşleme testleri: sembol → symbol_id (docs/03, Adım 2).

zeyrek ağır bir analizör olduğu için ``ruya.pipeline.map.kokler`` sahtesiyle değiştirilir;
testler gerçek analizöre bağlı değildir.
"""

import pytest

from ruya.pipeline import map as map_mod
from ruya.schemas import Eslesme, Sembol
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


def _eslesme(yalin: str, symbol_id: str | None) -> Eslesme:
    return Eslesme(
        sembol=_sembol(yalin),
        symbol_id=symbol_id,
        yontem="birebir" if symbol_id else "yok",
        guven=1.0 if symbol_id else 0.0,
    )


@pytest.mark.parametrize("yalin", ["kullanmak", "yapmak", "  Gitmek ", "görmek", "almak"])
def test_eslesmeyen_genel_fiil_elenir(yalin: str):
    assert map_mod.genel_fiilleri_ele([_eslesme(yalin, None)]) == []


def test_sozluge_eslesen_fiil_kalir():
    eslesmeler = [_eslesme("almak", "almak")]

    assert map_mod.genel_fiilleri_ele(eslesmeler) == eslesmeler


@pytest.mark.parametrize("yalin", ["binmek", "uçmak", "bilgisayar", "ev yapmak"])
def test_anlam_tasiyan_eslesmeyen_sembol_kalir(yalin: str):
    eslesmeler = [_eslesme(yalin, None)]

    assert map_mod.genel_fiilleri_ele(eslesmeler) == eslesmeler


def test_genel_fiil_elenince_sira_korunur():
    eslesmeler = [_eslesme("gemi", "gemi"), _eslesme("kullanmak", None), _eslesme("binmek", None)]

    sonuc = map_mod.genel_fiilleri_ele(eslesmeler)

    assert [e.sembol.yalin for e in sonuc] == ["gemi", "binmek"]


def test_tekrarlari_ele_ayni_symbol_id_ilk_kalir():
    eslesmeler = [
        _eslesme("ölüm haberi", "olum"),
        _eslesme("baba", "baba"),
        _eslesme("ölüm", "olum"),
    ]

    sonuc = map_mod.tekrarlari_ele(eslesmeler)

    assert [e.sembol.yalin for e in sonuc] == ["ölüm haberi", "baba"]


def test_tekrarlari_ele_eslesmeyenler_normallestirilerek_elenir():
    eslesmeler = [_eslesme("köprü", None), _eslesme("Köprü", None)]

    sonuc = map_mod.tekrarlari_ele(eslesmeler)

    assert len(sonuc) == 1
    assert sonuc[0].sembol.yalin == "köprü"


def test_tekrarlari_ele_farkli_eslesmeyenler_kalir():
    eslesmeler = [_eslesme("köprü", None), _eslesme("nehir", None)]

    sonuc = map_mod.tekrarlari_ele(eslesmeler)

    assert [e.sembol.yalin for e in sonuc] == ["köprü", "nehir"]


def test_tekrarlari_ele_eslesen_ve_eslesmeyen_birbirini_silmez():
    eslesmeler = [_eslesme("köprü", "kopru"), _eslesme("köprü", None)]

    sonuc = map_mod.tekrarlari_ele(eslesmeler)

    assert [e.sembol.yalin for e in sonuc] == ["köprü", "köprü"]
    assert [e.symbol_id for e in sonuc] == ["kopru", None]


def test_tekrarlari_ele_sira_korunur():
    eslesmeler = [
        _eslesme("baba", "baba"),
        _eslesme("ölüm", "olum"),
        _eslesme("nehir", None),
        _eslesme("ölüm haberi", "olum"),
        _eslesme("Nehir", None),
    ]

    sonuc = map_mod.tekrarlari_ele(eslesmeler)

    assert [e.sembol.yalin for e in sonuc] == ["baba", "ölüm", "nehir"]


def test_tekrarlari_ele_bos_girdi_bos_cikti():
    assert map_mod.tekrarlari_ele([]) == []


def test_ascii_katlanmis_eslesme(kok_yok):
    eslesmeler = map_mod.map_symbols([_sembol("tas")], {"taş": "tas"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "tas"
    assert eslesme.yontem == "birebir"
    assert eslesme.guven == map_mod.ASCII_GUVENI


def test_ascii_katlanmis_eslesme_belirsizse_yok(kok_yok):
    eslesmeler = map_mod.map_symbols([_sembol("kus")], {"kuş": "kus", "küs": "kusmek"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id is None
    assert eslesme.yontem == "yok"


def test_dogrudan_eslesme_ascii_katlamadan_once_gelir(kok_yok):
    eslesmeler = map_mod.map_symbols([_sembol("kil")], {"kıl": "kil_a", "kil": "kil_b"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "kil_b"
    assert eslesme.guven == 1.0


def test_ascii_katlama_kokten_sonra_gelir(monkeypatch):
    monkeypatch.setattr(map_mod, "kokler", lambda kelime: ["taş"], raising=False)

    eslesmeler = map_mod.map_symbols([_sembol("tas")], {"taş": "tas"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "tas"
    assert eslesme.yontem == "kok"


def test_cok_kelimeli_ifade_sondan_basa_anahtar(kok_yok):
    eslesmeler = map_mod.map_symbols(
        [_sembol("gümüş anahtar")], {"gümüş": "gumus", "anahtar": "anahtar"}
    )

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "anahtar"
    assert eslesme.yontem == "parca"


def test_cok_kelimeli_ifade_iyelik_ekliyse_bastan_sona(monkeypatch):
    monkeypatch.setattr(
        map_mod, "kokler", lambda kelime: ["çocuk"] if kelime == "çocuğu" else [], raising=False
    )

    eslesmeler = map_mod.map_symbols([_sembol("kız çocuğu")], {"kız": "kiz", "çocuk": "bebek"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "kiz"
    assert eslesme.yontem == "parca"


def test_cok_kelimeli_ifade_iyelik_ekliyse_ilk_kelime(kok_yok):
    eslesmeler = map_mod.map_symbols([_sembol("deniz kenarı")], {"deniz": "deniz"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "deniz"
    assert eslesme.yontem == "parca"


def test_cok_kelimeli_ifade_iyelik_ekliyse_mevcut_davranis(kok_yok):
    eslesmeler = map_mod.map_symbols([_sembol("güvercin sürüsü")], {"güvercin": "guvercin"})

    assert len(eslesmeler) == 1
    eslesme = eslesmeler[0]
    assert eslesme.symbol_id == "guvercin"
    assert eslesme.yontem == "parca"
