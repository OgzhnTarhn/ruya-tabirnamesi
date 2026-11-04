"""Arama terimleri testleri: ``arama_terimleri`` (docs/12, bölüm 5b).

zeyrek ağır bir analizör olduğu için ``ruya.text.turkce.kokler`` sahtesiyle değiştirilir;
testler gerçek analizöre bağlı değildir. Önbellek testler arasında sızmasın diye her test
kendine özgü kelimeler kullanır.
"""

import pytest

from ruya.text import turkce


@pytest.fixture(autouse=True)
def _onbellegi_temizle():
    """Başka testlerin gerçek kokler ile doldurduğu önbellek buraya sızmasın."""
    turkce._terim_koku.cache_clear()
    yield
    turkce._terim_koku.cache_clear()


@pytest.fixture
def sahte_kokler(monkeypatch):
    """Sözlükten kök döndüren sahte ``kokler``; kaç kez çağrıldığını da sayar."""

    def _kur(sozluk: dict[str, list[str]] | None = None):
        sozluk = sozluk or {}
        cagrilar: list[str] = []

        def _kokler(kelime: str) -> list[str]:
            cagrilar.append(kelime)
            return sozluk.get(kelime, [])

        monkeypatch.setattr(turkce, "kokler", _kokler, raising=False)
        return cagrilar

    return _kur


def test_bos_metin_bos_liste(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("") == []


def test_turkce_kucuk_harf(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("IŞIK İDRİS") == ["ışık", "idris"]


def test_harf_ve_rakam_disi_her_seyde_boler(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("yılan,deve!kuş;at?") == ["yılan", "deve", "kuş"]


def test_saf_rakamlar_atilir(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("123 yılan 2026") == ["yılan"]


def test_tek_harfli_kelimeler_atilir(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("a yılan b") == ["yılan"]


def test_turkce_durak_kelimeleri_atilir(sahte_kokler):
    sahte_kokler()
    metin = "ve ile bir bu şu o da de için gibi ya veya ki ne olarak olan yılan"
    assert turkce.arama_terimleri(metin) == ["yılan"]


def test_durak_kelimeleri_buyuk_harfle_de_atilir(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("VE İLE BİR YILAN") == ["yılan"]


def test_tekrarlar_ve_sira_korunur(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("yılan deve yılan kuş") == ["yılan", "deve", "yılan", "kuş"]


def test_kok_varsa_ilk_kok_kullanilir(sahte_kokler):
    sahte_kokler({"yılanlar": ["yılan"], "develer": ["deve", "deve"]})
    assert turkce.arama_terimleri("yılanlar develer") == ["yılan", "deve"]


def test_kok_yoksa_ilk_bes_karakter(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("kelebekler") == ["keleb"]


def test_kisa_kelime_oldugu_gibi_kalir(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("kuş") == ["kuş"]


def test_bes_karakterli_kelime_oldugu_gibi_kalir(sahte_kokler):
    sahte_kokler()
    assert turkce.arama_terimleri("deniz") == ["deniz"]


def test_ayni_kelime_icin_kokler_bir_kez_cagrilir(sahte_kokler):
    cagrilar = sahte_kokler({"zürafalar": ["zürafa"]})

    assert turkce.arama_terimleri("zürafalar") == ["zürafa"]
    assert turkce.arama_terimleri("zürafalar") == ["zürafa"]

    assert cagrilar.count("zürafalar") == 1
