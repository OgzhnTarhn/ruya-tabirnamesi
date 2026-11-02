"""Türkçeye özgü metin işlemlerinin testleri: küçük harf ve eşleme anahtarı (TK-08)."""

import pytest

from ruya.text.turkce import kucuk_harf, normallestir


@pytest.mark.parametrize(
    ("metin", "beklenen"),
    [
        ("I", "ı"),
        ("İ", "i"),
        ("YILAN", "yılan"),
        ("İDRİS", "idris"),
        ("IŞIK", "ışık"),
        ("İstanbul", "istanbul"),
        ("rüya", "rüya"),
        ("", ""),
    ],
)
def test_kucuk_harf_turkce(metin, beklenen):
    assert kucuk_harf(metin) == beklenen


def test_kucuk_harf_birlesen_nokta_birakmaz():
    # "İ".lower() "i" + U+0307 (birleşen nokta) verir; Türkçe kuralında bu olmamalı.
    assert kucuk_harf("İ") == "i"
    assert "\u0307" not in kucuk_harf("İDRİS")


def test_kucuk_harf_arapca_ve_rakamlari_degistirmez():
    assert kucuk_harf("يوسف 123") == "يوسف 123"
    assert kucuk_harf("2026") == "2026"


@pytest.mark.parametrize(
    ("metin", "beklenen"),
    [
        ("  Yılanlar! ", "yılanlar"),
        ("erkek   deve", "erkek deve"),
        ("Kur'an", "kur'an"),
        ("peygamber (s.a.v.)", "peygamber (s.a.v.)"),
        ("...", ""),
        ("!?«»", ""),
        ("", ""),
    ],
)
def test_normallestir(metin, beklenen):
    assert normallestir(metin) == beklenen


@pytest.mark.parametrize("noktalama", [".", ",", ";", ":", "!", "?", "«", "»", "'", '"'])
def test_normallestir_bastaki_sondaki_noktalama_silinir(noktalama):
    assert normallestir(f"{noktalama}yılan{noktalama}") == "yılan"


def test_normallestir_ic_noktalama_korunur():
    assert normallestir("Kur'an") == "kur'an"
    assert normallestir("peygamber (s.a.v.)") == "peygamber (s.a.v.)"


def test_normallestir_bosluk_ve_noktalama_birlikte():
    assert normallestir("  «Erkek   Deve!»  ") == "erkek deve"
