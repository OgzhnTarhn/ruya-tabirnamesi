"""Nablusi, Ta'tîrü'l-enâm (OpenITI mARkdown) ayrıştırıcısı. Takvim: Hafta 2.

Gerçek veride görülenler (docs/02, bölüm 2):
- ``#META#`` satırları künye; ``### | باب …`` satırları 29 bölüm (bab).
- Her paragraf ``# - (`` ile başlar: ~2.400 başlıklı madde, ~3.300 alt paragraf
  (``(ومن رأى)`` gibi). Alt paragraflar ``ust_madde_id`` ile başlığa bağlanır;
  hangi sembole ait oldukları ``enrich/assign_symbols.py`` ile bulunur.
- Temizlenecek gürültü: ``~~`` satır devamları, ``# PageV01P009`` sayfa işaretleri
  (``konum.sayfa`` için saklanır), ``ms008`` kilometre taşları.
- ``entry_id`` paragrafın başladığı satır numarasından türetilir: ``nablusi:004310``.

Kural kaynağı: ``data/interim/ceviri/_betikler/nb_hucre5.py`` içindeki
``nablusi_paragraflari`` ve ``nablusi_devam.py`` içindeki birleştirme kuralı;
``entry_id`` ve metin onlarla birebir aynıdır.

- ``#META#Header#End#`` satırına kadar olan satırlar atılır.
- ``### |`` bab başlığı ``konum.bab`` olur, kendi başına madde üretmez ve açık
  paragrafı kapatır.
- Yalnızca sayfa işaretinden oluşan satır paragraf başlatmaz; ``# `` ile başlayan
  satır yeni paragraf, ``~~`` ile başlayan satır açık paragrafın devamıdır.
- Paragraf, kendisinden sonra görülen ilk sayfa işaretinin sayfasını alır
  (satır içi işaret de sayılır); OpenITI'de işaret sayfayı kapatır.
- Başlıklı madde (``(حية)``) ile alt paragraf (``(ومن رأى)``) ayrılır; alt
  paragrafın ``baslik_asli`` alanı boş kalır ve ``ust_madde_id`` son başlıklı
  maddeyi gösterir.
- Başlıksız paragraf, bir önceki madde varsa onun metnine eklenir (bab başlığı
  geçse de); yoksa kendi maddesi olur.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

from ruya.ingest.kaynaklar import KAYNAKLAR
from ruya.schemas import Konum, Madde

SAYFA_DESENI = re.compile(r"PageV(\d+)P(\d+)")
SAYFA_SATIRI = re.compile(r"PageV\d+P\d+")
MS_DESENI = re.compile(r"\bms\d+\b")
BASLIK_DESENI = re.compile(r"^\(([^)]*)\)")
BAB_DESENI = re.compile(r"^###\s*\|+\s*")
ALT_ISARETLERI = ("رأى", "رآ", "رؤية")


def _metin_temizle(ham_satirlar: list[str]) -> str:
    """Paragrafın ham satırlarını tek satırlık temiz metne çevirir."""
    parcalar = []
    for satir in ham_satirlar:
        s = satir[1:] if satir.startswith("#") else satir
        s = s.strip()
        if s.startswith("- "):
            s = s[2:]
        parcalar.append(s)
    metin = " ".join(parcalar)
    metin = metin.replace("~~", " ")
    metin = SAYFA_DESENI.sub(" ", metin)
    metin = MS_DESENI.sub(" ", metin)
    return " ".join(metin.split())


def _paragraflar(satirlar: list[str]) -> list[dict[str, object]]:
    """Ham satırları bab, tür, başlık, sayfa ve metinle paragraflara böler."""
    basla = 0
    for i, satir in enumerate(satirlar):
        if "#META#Header#End#" in satir:
            basla = i + 1
            break

    paragraflar: list[dict[str, object]] = []
    bab: str | None = None
    acik: list[str] | None = None
    for i in range(basla, len(satirlar)):
        satir = satirlar[i]
        if BAB_DESENI.match(satir):
            bab = BAB_DESENI.sub("", satir).strip()
            acik = None
            continue
        if SAYFA_SATIRI.fullmatch(satir.strip().lstrip("#").strip()):
            continue  # yalnızca sayfa işareti: paragraf başlatmaz
        if satir.startswith("# "):
            acik = [satir]
            paragraflar.append({"bab": bab, "satir": i + 1, "ham": acik})
            continue
        if satir.startswith("~~") and acik is not None:
            acik.append(satir)

    # OpenITI'de işaret sayfayı kapatır: paragraf, kendisinden sonra görülen ilk
    # işaretin sayfasını alır (satır içi işaret de sayılır).
    isaretler: list[tuple[int, str]] = []
    for i in range(basla, len(satirlar)):
        eslesme = SAYFA_DESENI.search(satirlar[i])
        if eslesme:
            isaretler.append((i, f"V{eslesme.group(1)}P{eslesme.group(2)}"))

    sonuc: list[dict[str, object]] = []
    for p in paragraflar:
        metin = _metin_temizle(p["ham"])  # type: ignore[arg-type]
        baslik_eslesmesi = BASLIK_DESENI.match(metin)
        baslik = baslik_eslesmesi.group(1) if baslik_eslesmesi else None
        if baslik is None:
            tur = "diger"
        elif any(isaret in baslik for isaret in ALT_ISARETLERI):
            tur = "alt"
        else:
            tur = "baslikli"
        satir_no = int(p["satir"])  # type: ignore[arg-type]
        sayfa = next((s for i, s in isaretler if i >= satir_no - 1), None)
        sonuc.append(
            {
                "bab": p["bab"],
                "tur": tur,
                "baslik": baslik,
                "sayfa": sayfa,
                "satir": satir_no,
                "metin": metin,
            }
        )
    return sonuc


def ayristir(ham_dosya: Path) -> Iterator[Madde]:
    satirlar = ham_dosya.read_text(encoding="utf-8").splitlines()
    kunye = KAYNAKLAR["nablusi"]

    # nablusi_devam.py: başlıklı ve alt paragraflar kendi maddesi olur; başlıksız
    # paragraf önceki maddeye eklenir, önceki madde yoksa kendi maddesi olur.
    maddeler: list[dict[str, object]] = []
    son: dict[str, object] | None = None
    ust: str | None = None
    for p in _paragraflar(satirlar):
        tur = p["tur"]
        satir_no = int(p["satir"])  # type: ignore[arg-type]
        if tur in ("baslikli", "alt"):
            entry_id = f"nablusi:{satir_no:06d}"
            madde: dict[str, object] = {
                "entry_id": entry_id,
                "bab": p["bab"],
                "sayfa": p["sayfa"],
                "satir": satir_no,
                "baslik": p["baslik"] if tur == "baslikli" else None,
                "ust": ust if tur == "alt" else None,
                "metin": p["metin"],
            }
            maddeler.append(madde)
            son = madde
            if tur == "baslikli":
                ust = entry_id
        elif son is None:
            maddeler.append(
                {
                    "entry_id": f"nablusi:{satir_no:06d}",
                    "bab": p["bab"],
                    "sayfa": p["sayfa"],
                    "satir": satir_no,
                    "baslik": None,
                    "ust": None,
                    "metin": p["metin"],
                }
            )
        else:
            son["metin"] = f"{son['metin']} {p['metin']}"

    for madde in maddeler:
        yield Madde(
            entry_id=str(madde["entry_id"]),
            kaynak=kunye.kaynak,
            eser=kunye.eser,
            yazar=kunye.yazar,
            gelenek=kunye.gelenek,
            dil=kunye.dil,
            lisans=kunye.lisans,
            atif_notu=kunye.atif_notu,
            konum=Konum(
                bab=madde["bab"],  # type: ignore[arg-type]
                sayfa=madde["sayfa"],  # type: ignore[arg-type]
                satir=int(madde["satir"]),  # type: ignore[arg-type]
            ),
            baslik_asli=madde["baslik"],  # type: ignore[arg-type]
            ust_madde_id=madde["ust"],  # type: ignore[arg-type]
            metin_asli=str(madde["metin"]),
        )
