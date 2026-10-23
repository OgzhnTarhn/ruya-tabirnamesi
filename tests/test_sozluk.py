"""Repodaki elle onaylanan sözlük dosyası her zaman şemaya uymalı."""

import pytest

from ruya.config import SOZLUK_DOSYASI
from ruya.hatalar import SozlukHatasi
from ruya.index.build_symbols import sozlugu_yukle


def test_repodaki_sozluk_gecerli():
    sozlugu_yukle(SOZLUK_DOSYASI)


def test_ornek_sozluk_yuklenir(fixtures):
    sozluk = sozlugu_yukle(fixtures / "symbols_ornek.json")
    assert sozluk["yilan"].ad_tr == "yılan"


def test_bozuk_sozluk_anlasilir_hata_verir(tmp_path):
    yol = tmp_path / "symbols.json"
    yol.write_text('{"Yılan": {"ad_tr": "yılan"}}', encoding="utf-8")
    with pytest.raises(SozlukHatasi):
        sozlugu_yukle(yol)
