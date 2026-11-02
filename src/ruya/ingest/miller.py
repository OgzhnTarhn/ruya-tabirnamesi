r"""Miller, Ten Thousand Dreams Interpreted (Gutenberg #926) ayrıştırıcısı. Takvim: Hafta 2.

Gerçek veride görülenler (docs/02, bölüm 2):
- Asıl metin ``*** START/END OF THE PROJECT GUTENBERG EBOOK ***`` arasında;
  Gutenberg başlık ve dipnotları silinir (V5).
- ~1.540. satıra kadar önsöz ve kuram bölümü: madde değil, ayıklanır.
- 2.256 madde başlığı: ``^_[^_]+_\.(\[\d+\])?$`` (köşeli parantez dipnot işareti).
- ``entry_id`` başlığın satır numarasından türetilir: ``miller:018710``.

Kural kaynağı: ``data/interim/ceviri/_betikler/nb_hucre5.py`` içindeki
``miller_maddeleri()``; ``entry_id`` ve metin onunla birebir aynıdır. Ek kurallar:

- Boş satır paragrafı ayırır, paragrafın satır kaymaları tek boşlukla birleşir;
  paragraflar ``\n\n`` ile birleşir.
- Metindeki ``[12]`` gibi dipnot işaretleri silinir.
- Tek büyük harf ve noktadan oluşan paragraf (``S.``) alfabetik bölüm harfidir:
  madde orada biter, sonraki başlığa kadar olan satırlar atılır.
- ``INDEX`` satırında ayrıştırma tamamen durur (dizin maddeleri okunmaz).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from ruya.ingest.kaynaklar import KAYNAKLAR
from ruya.schemas import Konum, Madde

BASLIK_DESENI = re.compile(r"^_([^_]+)_\.(\[\d+\])?$")
DIPNOT_ISARETI = re.compile(r"\[\d+\]")
BOLUM_HARFI = re.compile(r"^[A-Z]\.$")
INDEX_SATIRI = "INDEX"


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    satirlar = ham_dosya.read_text(encoding="utf-8").splitlines()
    basla = 0
    for i, satir in enumerate(satirlar):
        if satir.startswith("*** START OF"):
            basla = i + 1
            break
    son = len(satirlar)
    for i in range(basla, len(satirlar)):
        if satirlar[i].startswith("*** END OF"):
            son = i
            break

    maddeler: list[dict[str, object]] = []
    baslik: str | None = None
    satir_no = 0
    paragraflar: list[str] = []
    tampon: list[str] = []
    kesildi = False  # bölüm harfinden sonraki satırlar atılır

    def _paragraf_kapat() -> None:
        if tampon:
            paragraflar.append(" ".join(tampon))
            tampon.clear()

    def _madde_kapat() -> None:
        _paragraf_kapat()
        if baslik is not None:
            govde = "\n\n".join(paragraflar)
            govde = DIPNOT_ISARETI.sub("", govde)
            govde = re.sub(r"[ \t]{2,}", " ", govde).strip()
            maddeler.append({"baslik": baslik, "metin": govde, "satir": satir_no})

    for i in range(basla, son):
        satir = satirlar[i]
        if satir.strip() == INDEX_SATIRI:
            break
        eslesme = BASLIK_DESENI.match(satir.strip())
        if eslesme:
            _madde_kapat()
            baslik = eslesme.group(1)
            satir_no = i + 1
            paragraflar = []
            tampon = []
            kesildi = False
            continue
        if baslik is None or kesildi:
            continue  # ilk başlıktan önceki satırlar ve bölüm harfi sonrası atılır
        if not satir.strip():
            _paragraf_kapat()
        elif BOLUM_HARFI.match(satir.strip()):
            _paragraf_kapat()
            kesildi = True
        else:
            tampon.append(satir.strip())
    _madde_kapat()

    kunye = KAYNAKLAR["miller"]
    for madde in maddeler:
        yield Madde(
            entry_id=f"miller:{int(madde['satir']):06d}",
            kaynak=kunye.kaynak,
            eser=kunye.eser,
            yazar=kunye.yazar,
            gelenek=kunye.gelenek,
            dil=kunye.dil,
            lisans=kunye.lisans,
            atif_notu=kunye.atif_notu,
            konum=Konum(satir=int(madde["satir"])),
            baslik_asli=str(madde["baslik"]),
            metin_asli=str(madde["metin"]),
        )
