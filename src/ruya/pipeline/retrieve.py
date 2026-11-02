"""Adım 3 · Getirme: symbol_id ile madde getirme ve sıralama (deterministik). Takvim: Hafta 4.

- Her sembol için her kaynaktan en fazla ``n`` madde (İG-22).
- ``gelenekler`` verilmişse yalnızca o geleneklerin maddeleri (İG-03).
- Sıralama: nitelik eşleşmesi → bağlam koşulu (Aşama 3) → başlıklı madde önce.
  Skora katkı yapan her şey ``Aday.gerekceler``'e yazılır (hata ayıklama sekmesi, İG-42).
- (Aşama 2) Bir sembolün maddesi n'den fazlaysa bge-reranker ile yeniden sıralama.
"""

from __future__ import annotations

from ruya.index.store import MaddeDeposu
from ruya.schemas import Aday, Baglam, Eslesme, Gelenek, Getirilenler, Madde
from ruya.text.turkce import kucuk_harf

NITELIK_PUANI = 2
BASLIKLI_PUANI = 1


def _skorla(madde: Madde, nitelikler: list[str]) -> Aday:
    """Bir maddenin skorunu ve gerekçelerini hesaplar."""
    skor = 0
    gerekceler: list[str] = []

    metin = kucuk_harf(madde.metin_tr or "")
    for nitelik in nitelikler:
        if kucuk_harf(nitelik) in metin:
            skor += NITELIK_PUANI
            gerekceler.append(f"nitelik:{nitelik}")

    if madde.baslikli_mi:
        skor += BASLIKLI_PUANI
        gerekceler.append("baslikli")

    return Aday(madde=madde, skor=skor, gerekceler=gerekceler)


def retrieve(
    eslesmeler: list[Eslesme],
    depo: MaddeDeposu,
    baglam: Baglam | None = None,
    gelenekler: list[Gelenek] | None = None,
    n: int = 2,
) -> Getirilenler:
    """Eşlenen (symbol_id'si dolu) her sembol için sıralı aday listesi.
    Maddesi olmayan sembol için boş liste döner; sentez onu "bulunamadı" olarak yazar."""
    # baglam şimdilik kullanılmıyor; bağlam koşulu puanlaması Aşama 3'te eklenecek.
    sonuc: Getirilenler = {}
    for eslesme in eslesmeler:
        if eslesme.yontem == "yok" or eslesme.symbol_id is None:
            continue

        maddeler = depo.sembolun_maddeleri(eslesme.symbol_id)
        if gelenekler is not None:
            maddeler = [m for m in maddeler if m.gelenek in gelenekler]

        adaylar = [_skorla(m, eslesme.sembol.nitelikler) for m in maddeler]
        adaylar.sort(key=lambda a: (-a.skor, a.madde.entry_id))

        # Her kaynaktan en fazla n madde (İG-22): skora göre ilk n tanesi kalır.
        secilen: list[Aday] = []
        kaynak_sayaci: dict[str, int] = {}
        for aday in adaylar:
            kaynak = aday.madde.kaynak
            if kaynak_sayaci.get(kaynak, 0) >= n:
                continue
            kaynak_sayaci[kaynak] = kaynak_sayaci.get(kaynak, 0) + 1
            secilen.append(aday)

        sonuc[eslesme.symbol_id] = secilen

    return sonuc
