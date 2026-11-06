"""Adım 2 · Eşleme: sembol → symbol_id (deterministik). Takvim: Hafta 4.

Sıra (docs/03, Adım 2):
1. text.turkce.normallestir
2. Varyant tablosunda doğrudan arama → yontem="birebir"
3. text.turkce.kokler ile kök bulup yeniden arama → yontem="kok"
4. ASCII katlamalı arama: anahtar Türkçe harflerden arındırılıp varyant anahtarlarıyla
   karşılaştırılır; birden çok symbol_id'ye düşen katlanmış anahtarlar belirsiz sayılır
   → yontem="birebir"
5. Çok kelimeli ifadeyi kelimelere bölüp her kelimeyi (birebir, sonra kök) arama
   → yontem="parca". Son kelime iyelik ekiyle bitiyorsa (ı/i/u/ü) kelimeler baştan
   sona, aksi halde sondan başa denenir.
"""

from __future__ import annotations

from ruya.schemas import Eslesme, Sembol
from ruya.text.turkce import kokler, normallestir

KOK_GUVENI = 0.9

PARCA_GUVENI = 0.8

ASCII_GUVENI = 0.95

_ASCII_TABLOSU = str.maketrans(
    {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
        "â": "a",
        "î": "i",
        "û": "u",
    }
)


def _ascii_katla(metin: str) -> str:
    """Türkçe harfleri ASCII karşılıklarına indirger."""
    return metin.translate(_ASCII_TABLOSU)


# Tek başına bir imge taşımayan fiiller; "kullanmak" araması rastgele maddeler getiriyor
# ("allık kullanmak"). Liste bilinçli olarak dardır: "binmek", "uçmak" gibi fiiller kalır.
GENEL_FIILLER = frozenset(
    {
        "almak",
        "anlamak",
        "bakmak",
        "başlamak",
        "bilmek",
        "bulmak",
        "demek",
        "durmak",
        "düşünmek",
        "etmek",
        "gelmek",
        "getirmek",
        "gitmek",
        "götürmek",
        "görmek",
        "hissetmek",
        "istemek",
        "izlemek",
        "kalmak",
        "koymak",
        "kullanmak",
        "olmak",
        "sanmak",
        "söylemek",
        "tutmak",
        "vermek",
        "yapmak",
    }
)


def genel_fiilleri_ele(eslesmeler: list[Eslesme]) -> list[Eslesme]:
    """Sözlüğe eşleşmeyen genel fiilleri atar; sözlükte karşılığı olan fiiller kalır."""
    return [
        eslesme
        for eslesme in eslesmeler
        if eslesme.symbol_id is not None
        or normallestir(eslesme.sembol.yalin) not in GENEL_FIILLER
    ]


def tekrarlari_ele(eslesmeler: list[Eslesme]) -> list[Eslesme]:
    """Aynı symbol_id'yi ya da aynı normalleştirilmiş metni paylaşan tekrarları atar."""
    gorulen: set[str] = set()
    sonuc: list[Eslesme] = []
    for eslesme in eslesmeler:
        if eslesme.symbol_id is not None:
            anahtar = f"id:{eslesme.symbol_id}"
        else:
            anahtar = f"metin:{normallestir(eslesme.sembol.yalin)}"
        if anahtar in gorulen:
            continue
        gorulen.add(anahtar)
        sonuc.append(eslesme)
    return sonuc


def map_symbols(
    semboller: list[Sembol],
    varyantlar: dict[str, str],
) -> list[Eslesme]:
    """Her sembol için tam olarak bir Eslesme döndürür (eşleşmeyenler yontem="yok")."""
    katlanmis: dict[str, str] = {}
    belirsiz: set[str] = set()
    for varyant, symbol_id in varyantlar.items():
        katlanmis_anahtar = _ascii_katla(varyant)
        if katlanmis_anahtar in katlanmis and katlanmis[katlanmis_anahtar] != symbol_id:
            belirsiz.add(katlanmis_anahtar)
        else:
            katlanmis[katlanmis_anahtar] = symbol_id
    for anahtar in belirsiz:
        katlanmis.pop(anahtar, None)

    eslesmeler: list[Eslesme] = []
    for sembol in semboller:
        anahtar = normallestir(sembol.yalin)

        if anahtar in varyantlar:
            eslesmeler.append(
                Eslesme(sembol=sembol, symbol_id=varyantlar[anahtar], yontem="birebir", guven=1.0)
            )
            continue

        kok_eslesmesi = next((k for k in kokler(anahtar) if k in varyantlar), None)
        if kok_eslesmesi is not None:
            eslesmeler.append(
                Eslesme(
                    sembol=sembol,
                    symbol_id=varyantlar[kok_eslesmesi],
                    yontem="kok",
                    guven=KOK_GUVENI,
                )
            )
            continue

        katlanmis_eslesme = katlanmis.get(_ascii_katla(anahtar))
        if katlanmis_eslesme is not None:
            eslesmeler.append(
                Eslesme(
                    sembol=sembol,
                    symbol_id=katlanmis_eslesme,
                    yontem="birebir",
                    guven=ASCII_GUVENI,
                )
            )
            continue

        parca_eslesmesi = None
        kelimeler = anahtar.split()
        if len(kelimeler) > 1:
            if kelimeler[-1][-1] not in "ıiuü":
                kelimeler = list(reversed(kelimeler))
            for kelime in kelimeler:
                if kelime in varyantlar:
                    parca_eslesmesi = varyantlar[kelime]
                    break
                kelime_koku = next((k for k in kokler(kelime) if k in varyantlar), None)
                if kelime_koku is not None:
                    parca_eslesmesi = varyantlar[kelime_koku]
                    break
        if parca_eslesmesi is not None:
            eslesmeler.append(
                Eslesme(
                    sembol=sembol,
                    symbol_id=parca_eslesmesi,
                    yontem="parca",
                    guven=PARCA_GUVENI,
                )
            )
            continue

        eslesmeler.append(Eslesme(sembol=sembol, symbol_id=None, yontem="yok", guven=0.0))

    return eslesmeler
