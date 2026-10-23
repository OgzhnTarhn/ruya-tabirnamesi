"""Türkçeye özgü metin işlemleri (TK-08). Takvim: Hafta 2.

Python'un ``str.lower()`` işlevi Türkçeye uygun değildir: ``"I".lower()`` "i" verir,
oysa doğrusu "ı"; ``"İ".lower()`` ise "i̇" (i + birleşen nokta) verir.
"""

from __future__ import annotations


def kucuk_harf(metin: str) -> str:
    """Türkçe kurallarına göre küçük harfe çevirir: I → ı, İ → i."""
    raise NotImplementedError("Hafta 2: text/turkce.py (docs/08)")


def normallestir(metin: str) -> str:
    """Eşleme için anahtar üretir: Türkçe küçük harf, baştaki/sondaki noktalama ve
    fazla boşluk temizliği. ``"  Yılanlar! "`` → ``"yılanlar"``"""
    raise NotImplementedError("Hafta 2: text/turkce.py (docs/08)")


def kokler(kelime: str) -> list[str]:
    """zeyrek ile kelimenin olası yalın biçimlerini döndürür: ``"yılanlar"`` → ``["yılan"]``.

    zeyrek alfa aşamasında (R10); hata verirse boş liste döner, eşleme bir sonraki yola geçer.
    zeyrek ağır bir analizör yüklediği için içe aktarma işlevin içinde yapılır.
    """
    raise NotImplementedError("Hafta 4: pipeline/map.py ile birlikte (docs/08)")
