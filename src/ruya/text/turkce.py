"""Türkçeye özgü metin işlemleri (TK-08). Takvim: Hafta 2.

Python'un ``str.lower()`` işlevi Türkçeye uygun değildir: ``"I".lower()`` "i" verir,
oysa doğrusu "ı"; ``"İ".lower()`` ise "i̇" (i + birleşen nokta) verir.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from ruya.config import ayarlar

_log = logging.getLogger(__name__)

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


@lru_cache(maxsize=1)
def _cozumleyici() -> Any:
    """zeyrek analizörünü bir kez kurar ve önbelleğe alır.

    zeyrek ağır bir analizör yüklediği için içe aktarma işlevin içinde yapılır (docs/12).
    """
    import nltk
    import zeyrek

    # zeyrek cümle bölücüsü için NLTK punkt verisi ister: scripts/nltk_kur.py
    nltk.data.path.insert(0, str(ayarlar().data_dir / "nltk_data"))

    return zeyrek.MorphAnalyzer()


def kokler(kelime: str) -> list[str]:
    """zeyrek ile kelimenin olası yalın biçimlerini döndürür: ``"yılanlar"`` → ``["yılan"]``.

    zeyrek alfa aşamasında (R10); hata verirse boş liste döner, eşleme bir sonraki yola geçer.
    zeyrek ağır bir analizör yüklediği için içe aktarma işlevin içinde yapılır.
    """
    try:
        analizler = _cozumleyici().analyze(kelime)
    except Exception as hata:  # zeyrek alfa; her hata eşlemede "kök yok" demektir
        # Kelime rüya metninin parçası olabilir; loga yalnızca hata türü yazılır.
        _log.warning("Kök bulunamadı: %s", type(hata).__name__)
        return []

    girdi = kucuk_harf(kelime)
    kok_listesi: list[str] = []
    for cozumlemeler in analizler:
        for cozumleme in cozumlemeler:
            kok = kucuk_harf(cozumleme.lemma)
            if kok and kok not in kok_listesi:
                kok_listesi.append(kok)

    # Kelimenin kendisi yalın biçimse ve başka kök de varsa listeden çıkarılır; tek sonuç
    # kendisiyse korunur (eşleme yine de birebir aramada bulur).
    if len(kok_listesi) > 1 and girdi in kok_listesi:
        kok_listesi.remove(girdi)

    return kok_listesi
