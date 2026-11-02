"""Adım 2 · Eşleme: sembol → symbol_id (deterministik). Takvim: Hafta 4.

Sıra (docs/03, Adım 2):
1. text.turkce.normallestir
2. Varyant tablosunda doğrudan arama → yontem="birebir"
3. text.turkce.kokler ile kök bulup yeniden arama → yontem="kok"
4. Çok kelimeli ifadeyi kelimelere bölüp her kelimeyi (birebir, sonra kök) arama
   → yontem="parca"
5. (Aşama 2) VektorArayici; benzerlik ``esik`` altındaysa → yontem="yok"
"""

from __future__ import annotations

from ruya.index.store import VektorArayici
from ruya.schemas import Eslesme, Sembol
from ruya.text.turkce import kokler, normallestir

VARSAYILAN_ESIK = 0.80  # Hafta 6'da test setiyle ayarlanacak

KOK_GUVENI = 0.9

PARCA_GUVENI = 0.8


def map_symbols(
    semboller: list[Sembol],
    varyantlar: dict[str, str],
    vektor: VektorArayici | None = None,
    esik: float = VARSAYILAN_ESIK,
) -> list[Eslesme]:
    """Her sembol için tam olarak bir Eslesme döndürür (eşleşmeyenler yontem="yok")."""
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

        parca_eslesmesi = None
        kelimeler = anahtar.split()
        if len(kelimeler) > 1:
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

        if vektor is not None:
            sonuclar = vektor.en_yakin_semboller(anahtar)
            if sonuclar and sonuclar[0][1] >= esik:
                symbol_id, benzerlik = sonuclar[0]
                eslesmeler.append(
                    Eslesme(sembol=sembol, symbol_id=symbol_id, yontem="vektor", guven=benzerlik)
                )
                continue

        eslesmeler.append(Eslesme(sembol=sembol, symbol_id=None, yontem="yok", guven=0.0))

    return eslesmeler
