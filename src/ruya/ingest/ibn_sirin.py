"""İbn Sîrîn'e atfedilen Muntahab (OpenITI, Shamela0021615). Takvim: Hafta 8.

Bab (konu) düzeninde. Kurallar ``data/interim/ceviri/_betikler/parcala2.py`` içindeki
``ibn_sirin()`` işlevinden birebir taşınmıştır; ``entry_id`` ve metinler onunla aynıdır:

- ``#META#Header#End#`` satırından sonrası okunur; öncesi atlanır.
- ``###`` satırı babı belirler (``# |`` ve ``msNNN`` temizlenir).
- ``~~`` satırı önceki paragrafı sürdürür.
- ``# Page…`` işaretinden sonraki ilk ``# `` satırı özel bir kalıpla (``-``, ``(``, ``[``,
  ``ومن رأى``, ``من رأى``, ``فصل``) başlamıyorsa önceki paragrafa eklenir.
- ``msNNN`` kilometre taşları silinir, çoklu boşluk tek boşluğa iner; temizlikten sonra
  boş kalan maddeler atılır.
- ``entry_id`` paragrafın başladığı satır numarasından türetilir: ``ibn_sirin:000003``.
- ``konum.sayfa`` paragraf satırında ya da sonrasındaki ilk ``# Page…`` işaretidir
  (``V01P001`` biçiminde); yoksa ``None``.

Her kayda ``atif_notu`` olarak kaynaklar.OPENITI_ATIF_NOTU yazılır (İG-34, docs/07 D6).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from ruya.ingest.kaynaklar import KAYNAKLAR
from ruya.schemas import Konum, Madde

_YENI_BASLAR = re.compile(r"^(-|\(|\[|ومن رأى|من رأى|فصل)")


def _temiz(metin: str) -> str:
    """``msNNN`` kilometre taşlarını siler, boşlukları tekler ve kırpar."""
    return re.sub(r"\s+", " ", re.sub(r"\bms\d+\b", " ", metin)).strip()


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    bilgi = KAYNAKLAR["ibn_sirin"]
    satirlar = ham_dosya.read_text(encoding="utf-8").splitlines()
    bas = satirlar.index("#META#Header#End#") + 1

    # Sayfa işaretleri: (satır numarası, "V01P001" biçimindeki kimlik).
    sayfalar = [
        (no, s[len("# Page") :].strip())
        for no, s in enumerate(satirlar[bas:], bas + 1)
        if s.startswith("# Page")
    ]

    maddeler: list[dict[str, object]] = []
    bab: str | None = None
    sayfa_basi = False
    for no, s in enumerate(satirlar[bas:], bas + 1):
        if s.startswith("# Page"):
            sayfa_basi = True
        elif s.startswith("###"):
            bab = _temiz(s.lstrip("# |"))
            sayfa_basi = False
        elif s.startswith("~~") and maddeler:
            maddeler[-1]["metin"] = f"{maddeler[-1]['metin']} {_temiz(s[2:])}"
        elif s.startswith("# "):
            metin = _temiz(s[2:])
            if sayfa_basi and maddeler and not _YENI_BASLAR.match(metin):
                maddeler[-1]["metin"] = f"{maddeler[-1]['metin']} {metin}"
            else:
                maddeler.append(
                    {
                        "entry_id": f"ibn_sirin:{no:06d}",
                        "bab": bab,
                        "satir": no,
                        "metin": metin.lstrip("- "),
                    }
                )
            sayfa_basi = False

    for madde in maddeler:
        metin = str(madde["metin"])
        if not metin.strip():
            continue
        satir = int(madde["satir"])
        sayfa = next((kimlik for no, kimlik in sayfalar if no >= satir), None)
        yield Madde(
            entry_id=str(madde["entry_id"]),
            kaynak=bilgi.kaynak,
            eser=bilgi.eser,
            yazar=bilgi.yazar,
            gelenek=bilgi.gelenek,
            dil=bilgi.dil,
            lisans=bilgi.lisans,
            atif_notu=bilgi.atif_notu,
            konum=Konum(bab=madde["bab"], sayfa=sayfa, satir=satir),
            metin_asli=metin,
        )
