"""Türkçeye özgü metin işlemleri (TK-08). Takvim: Hafta 2.

Python'un ``str.lower()`` işlevi Türkçeye uygun değildir: ``"I".lower()`` "i" verir,
oysa doğrusu "ı"; ``"İ".lower()`` ise "i̇" (i + birleşen nokta) verir.
"""

from __future__ import annotations

# Türkçe büyük harflerin küçük karşılıkları. ``str.lower()`` bunları yanlış çevirir.
_KUCUK_HARF_TABLOSU = str.maketrans({"I": "ı", "İ": "i"})

# Anahtarın başından ve sonundan temizlenen noktalama işaretleri. Parantezler
# bilinçli olarak dışarıda: "peygamber (s.a.v.)" gibi ifadeler korunur.
_NOKTALAMA = ".,;:!?«»'\""


def kucuk_harf(metin: str) -> str:
    """Türkçe kurallarına göre küçük harfe çevirir: I → ı, İ → i."""
    return metin.translate(_KUCUK_HARF_TABLOSU).lower()


def normallestir(metin: str) -> str:
    """Eşleme için anahtar üretir: Türkçe küçük harf, baştaki/sondaki noktalama ve
    fazla boşluk temizliği. ``"  Yılanlar! "`` → ``"yılanlar"``"""
    metin = kucuk_harf(metin)
    metin = " ".join(metin.split())
    return metin.strip(_NOKTALAMA + " ")


def kokler(kelime: str) -> list[str]:
    """zeyrek ile kelimenin olası yalın biçimlerini döndürür: ``"yılanlar"`` → ``["yılan"]``.

    zeyrek alfa aşamasında (R10); hata verirse boş liste döner, eşleme bir sonraki yola geçer.
    zeyrek ağır bir analizör yüklediği için içe aktarma işlevin içinde yapılır.
    """
    raise NotImplementedError("Hafta 4: pipeline/map.py ile birlikte (docs/08)")
