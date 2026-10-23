"""Kanonik sembol sözlüğü (sozluk/symbols.json) ve ondan türetilen arama tabloları.

Sözlük git'te durur ve elle onaylanır; bu modül onu yükler, doğrular ve sorgu anında
kullanılan tabloları **bellekte** kurar. Drive'a ayrı bir sembol dosyası yazılmaz.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from ruya.config import SOZLUK_DOSYASI
from ruya.hatalar import SozlukHatasi
from ruya.schemas import Madde, SozlukDosyasi, SymbolKaydi


def sozlugu_yukle(yol: Path = SOZLUK_DOSYASI) -> dict[str, SymbolKaydi]:
    """symbols.json dosyasını okur ve şemaya göre doğrular."""
    try:
        return SozlukDosyasi.model_validate_json(yol.read_bytes()).root
    except (OSError, ValidationError) as hata:
        raise SozlukHatasi(f"{yol} okunamadı: {hata}") from hata


def varyant_tablosu(
    sozluk: dict[str, SymbolKaydi], yalniz_onaylilar: bool = True
) -> dict[str, str]:
    """Normalleştirilmiş Türkçe ad ve varyantlardan symbol_id'ye tablo.

    ``{"yılan": "yilan", "engerek": "yilan", …}``. Aynı varyant iki sembolde geçiyorsa
    SozlukHatasi verir. ``yalniz_onaylilar`` True ise gozden_gecirildi=False semboller
    atlanır (MVP kuralı, docs/02 bölüm 4.2). Takvim: Hafta 4.
    """
    raise NotImplementedError("Hafta 4: pipeline/map.py ile birlikte (docs/08)")


def sozluk_maddeler_tutarliligi(sozluk: dict[str, SymbolKaydi], maddeler: list[Madde]) -> list[str]:
    """Sorun listesi döndürür: sözlükte olmayan symbol_id'ler, hiç maddesi olmayan
    onaylı semboller. Boş liste = tutarlı. Takvim: Hafta 3."""
    raise NotImplementedError("Hafta 3: enrich/assign_symbols.py ile birlikte (docs/08)")
