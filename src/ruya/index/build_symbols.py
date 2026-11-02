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
from ruya.text.turkce import normallestir


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
    tablo: dict[str, str] = {}
    kaynaklar: dict[str, str] = {}
    for symbol_id, kayit in sozluk.items():
        if yalniz_onaylilar and not kayit.gozden_gecirildi:
            continue
        for ad in [kayit.ad_tr, *kayit.varyantlar_tr]:
            anahtar = normallestir(ad)
            if not anahtar:
                continue
            onceki = kaynaklar.get(anahtar)
            if onceki is not None and onceki != symbol_id:
                raise SozlukHatasi(
                    f"'{anahtar}' varyantı iki sembolde geçiyor: {onceki} ve {symbol_id}"
                )
            kaynaklar[anahtar] = symbol_id
            tablo[anahtar] = symbol_id
    return tablo


def sozluk_maddeler_tutarliligi(sozluk: dict[str, SymbolKaydi], maddeler: list[Madde]) -> list[str]:
    """Sorun listesi döndürür: sözlükte olmayan symbol_id'ler, hiç maddesi olmayan
    onaylı semboller. Boş liste = tutarlı. Takvim: Hafta 3."""
    sorunlar: list[str] = []

    kullanilan: set[str] = set()
    bilinmeyenler: list[str] = []
    for madde in maddeler:
        for symbol_id in madde.symbol_ids:
            kullanilan.add(symbol_id)
            if symbol_id not in sozluk and symbol_id not in bilinmeyenler:
                bilinmeyenler.append(symbol_id)
    for symbol_id in bilinmeyenler:
        sorunlar.append(f"sözlükte olmayan symbol_id: {symbol_id}")

    for symbol_id, kayit in sozluk.items():
        if kayit.gozden_gecirildi and symbol_id not in kullanilan:
            sorunlar.append(f"hiç maddesi olmayan onaylı sembol: {symbol_id}")

    return sorunlar
