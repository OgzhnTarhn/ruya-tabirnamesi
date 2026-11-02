"""Freud, The Interpretation of Dreams (Brill 1913, Gutenberg #66048). Takvim: Hafta 7.

Sembol sözlüğü değil, "yöntem" katmanı: paragraf paragraf bölünür, sembol ataması
yalnızca açıkça bir sembolden söz eden paragraflara yapılır.

Kural kaynağı: ``data/interim/ceviri/_betikler/parcala2.py`` içindeki ``freud()``;
``entry_id`` ve metin onunla birebir aynıdır (``freud:<6 haneli satır no>``).

- Yalnızca ``ARALIKLAR`` içindeki satırlar okunur; boş satırlar paragrafı ayırır,
  paragrafın satırları tek boşlukla birleştirilir.
- Bölüm (bab): en çok iki satır, ilk satır beş boşlukla girintili, tamamı büyük harf
  ve en az bir harf içeren paragraf. Bölüm paragrafı hem ``konum.bab`` olur hem de
  kendi maddesi olarak yazılır.
- ``Footnote A:`` gibi tek başına kalan dipnot satırı sonraki paragrafla birleştirilir;
  madde ilk satırın kimliğini ve babını korur.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from ruya.ingest.kaynaklar import KAYNAKLAR
from ruya.schemas import Konum, Madde

# Gutenberg #66048 dosyasında (kaynaklar.KAYNAKLAR["freud"].sha256 ile sabitlenmiş sürüm)
# madde sayılan satır aralıkları. İçindekiler, edebiyat dizini ve dizin bu aralıkların
# dışında kalır; aralıklar o dosyaya özgüdür, başka bir sürümde kayar.
ARALIKLAR: tuple[tuple[int, int], ...] = ((62, 275), (303, 17624))

_DIPNOT = re.compile(r"Footnote \w+:")


def ayristir(
    ham_dosya: Path, araliklar: tuple[tuple[int, int], ...] = ARALIKLAR
) -> Iterator[Madde]:
    satirlar = ham_dosya.read_text(encoding="utf-8").splitlines()
    maddeler: list[dict[str, object]] = []
    bolum: str | None = None
    for ilk, son in araliklar:
        i = ilk - 1
        while i < son:
            if not satirlar[i].strip():
                i += 1
                continue
            j = i
            while j < son and satirlar[j].strip():
                j += 1
            ham_par = satirlar[i:j]
            metin = re.sub(r"\s+", " ", " ".join(ham_par)).strip()
            girintili_buyuk = (
                len(ham_par) <= 2
                and ham_par[0].startswith("     ")
                and metin.upper() == metin
                and re.search("[A-Z]", metin) is not None
            )
            if girintili_buyuk:
                bolum = metin
            maddeler.append(
                {"entry_id": f"freud:{i + 1:06d}", "bolum": bolum, "metin": metin, "satir": i + 1}
            )
            i = j

    # "Footnote A:" satırını sonraki paragrafla birleştir.
    birlesik: list[dict[str, object]] = []
    for madde in maddeler:
        if birlesik and _DIPNOT.fullmatch(str(birlesik[-1]["metin"])):
            birlesik[-1]["metin"] = f"{birlesik[-1]['metin']} {madde['metin']}"
        else:
            birlesik.append(madde)

    kunye = KAYNAKLAR["freud"]
    for madde in birlesik:
        yield Madde(
            entry_id=str(madde["entry_id"]),
            kaynak=kunye.kaynak,
            eser=kunye.eser,
            yazar=kunye.yazar,
            gelenek=kunye.gelenek,
            dil=kunye.dil,
            lisans=kunye.lisans,
            atif_notu=kunye.atif_notu,
            konum=Konum(bab=madde["bolum"], satir=int(madde["satir"])),
            metin_asli=str(madde["metin"]),
        )
