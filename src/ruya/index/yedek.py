"""Chroma indeksinin Drive'a zip olarak yedeklenmesi ve geri yüklenmesi (docs/11, bölüm 4).

Oturum başında: data/index/chroma.zip → /content/calisma/chroma/
İndeks yeniden kurulduysa oturum sonunda: tersi. Takvim: Hafta 6.
"""

from __future__ import annotations

from ruya.config import Ayarlar


def indeksi_geri_yukle(ayar: Ayarlar) -> bool:
    """Yedek varsa açar ve True döndürür; yoksa False."""
    raise NotImplementedError("Hafta 6: index/yedek.py (docs/08)")


def indeksi_yedekle(ayar: Ayarlar) -> None:
    raise NotImplementedError("Hafta 6: index/yedek.py (docs/08)")
