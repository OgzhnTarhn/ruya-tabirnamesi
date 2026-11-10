"""Getirme deneyi: D1 (vektör kolu) ve D2 (reranker) ölçümü (docs/15, K3–K5).

Her rüya için çıkarım bir kez yapılır, dört getirme çeşidi (G0–G3) aynı eşleşmeler
üzerinde koşar ve sıralamalar JSONL olarak yazılır. Etiketler TREC usulü havuzlamayla
toplanır: bütün çeşitlerin ilk ``k`` sonucu birleştirilir, kullanıcı yalnız bu havuzu
işaretler. Havuz ``entry_id``'ye göre artan sırada yazılır; böylece etiketler hangi
çeşidin bir maddeyi bulduğuna göre yanlı tutulmaz.

Bu modül hiçbir yolu kendiliğinden seçmez: satırlar yalnız çağıranın verdiği yolun
altına yazılır (``data/`` altındaki yerleri ``eval/`` betiği belirler). Rüya metni
hiçbir zaman loglanmaz (İOG-07); yalnız etiket dosyasına, kullanıcının işaretlemesi
için yazılır.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TextIO

from ruya.hatalar import RuyaHatasi
from ruya.index.store import MaddeDeposu
from ruya.pipeline import extract, hibrit
from ruya.pipeline import map as esleme
from ruya.pipeline.run import Bagimliliklar
from ruya.schemas import Eslesme, RuyaGirdisi, TestOrnegi, getirme_anahtari

# Getirme çeşitleri (docs/15, K3–K4): ad → (kollar, reranker açık mı).
CESITLER: dict[str, tuple[frozenset[str], bool]] = {
    "G0": (frozenset({"sozluk", "bm25", "vektor", "hyde"}), True),
    "G1": (frozenset({"sozluk", "bm25", "vektor", "hyde"}), False),
    "G2": (frozenset({"sozluk", "bm25"}), True),
    "G3": (frozenset({"sozluk", "bm25", "vektor"}), True),
}

# Etiket dosyasında bir madde metninin en fazla karakter sayısı.
METIN_SINIRI = 300

Satir = dict[str, Any]


def havuz(satirlar: list[Satir], k: int = 5) -> dict[tuple[str, str], list[str]]:
    """Her (rüya, anahtar) için çeşitlerin ilk ``k`` sonucunun birleşimi.

    Tekrarlar birleşir ve kimlikler artan sırada döner; böylece etiket dosyasındaki
    sıra hiçbir çeşidi kayırmaz (docs/15, K5).
    """
    birlesim: dict[tuple[str, str], set[str]] = {}
    for satir in satirlar:
        anahtar = (satir["ornek_id"], satir["anahtar"])
        kimlikler = birlesim.setdefault(anahtar, set())
        for entry_id, _skor in satir["sirali"][:k]:
            kimlikler.add(entry_id)
    return {anahtar: sorted(kimlikler) for anahtar, kimlikler in birlesim.items()}


def _sembol_adlari(satirlar: list[Satir]) -> dict[tuple[str, str], str]:
    """(rüya, anahtar) → görünen sembol adı; satırlardaki ilk ad kullanılır."""
    adlar: dict[tuple[str, str], str] = {}
    for satir in satirlar:
        adlar.setdefault((satir["ornek_id"], satir["anahtar"]), satir["sembol"])
    return adlar


def _madde_metni(depo: MaddeDeposu, entry_id: str) -> str:
    """Etiket satırı için tek satırlık, kırpılmış madde metni."""
    try:
        madde = depo.madde(entry_id)
    except KeyError:
        return "(madde bulunamadı)"
    metin = madde.metin_tr or madde.metin_asli
    return " ".join(metin.split())[:METIN_SINIRI]


def etiket_dosyasi_yaz(
    havuz: dict[tuple[str, str], list[str]],
    satirlar: list[Satir],
    metinler: dict[str, str],
    depo: MaddeDeposu,
    yol: Path,
) -> Path:
    """Havuzu işaretlemeye hazır Markdown dosyası olarak yazar.

    Bölümler anahtara göre sıralanır, maddeler artan ``entry_id`` sırasıyla yazılır;
    hangi çeşidin bulduğu görünmez. Rüya metni yalnız bu dosyaya, alıntı olarak girer.
    """
    adlar = _sembol_adlari(satirlar)
    ornek_sirasi: list[str] = []
    anahtarlar: dict[str, list[str]] = {}
    for ornek_id, anahtar in havuz:
        if ornek_id not in anahtarlar:
            ornek_sirasi.append(ornek_id)
            anahtarlar[ornek_id] = []
        anahtarlar[ornek_id].append(anahtar)

    parcalar: list[str] = []
    for ornek_id in ornek_sirasi:
        parcalar.append(f"## {ornek_id}")
        parcalar.append(f"> {metinler.get(ornek_id, '')}")
        parcalar.append("")
        for anahtar in sorted(anahtarlar[ornek_id]):
            sembol = adlar.get((ornek_id, anahtar), anahtar)
            parcalar.append(f"### {sembol} ({anahtar})")
            for entry_id in havuz[(ornek_id, anahtar)]:
                parcalar.append(f"- [ ] {entry_id} — {_madde_metni(depo, entry_id)}")
            parcalar.append("")

    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text("\n".join(parcalar), encoding="utf-8")
    return yol


def etiketleri_oku(yol: Path) -> dict[tuple[str, str], set[str]]:
    """İşaretli etiket dosyasını okur: (rüya, anahtar) → ilgili ``entry_id`` kümesi.

    Yalnız ``- [x]`` / ``- [X]`` satırları ilgili sayılır; işaretsiz satırlar atlanır.
    """
    etiketler: dict[tuple[str, str], set[str]] = {}
    ornek_id: str | None = None
    anahtar: str | None = None
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if satir.startswith("## "):
            ornek_id = satir[3:].strip()
            anahtar = None
        elif satir.startswith("### ") and ornek_id is not None:
            baslik = satir[4:].strip()
            anahtar = baslik[baslik.rfind("(") + 1 : baslik.rfind(")")].strip()
            etiketler.setdefault((ornek_id, anahtar), set())
        elif (
            satir.startswith(("- [x] ", "- [X] "))
            and ornek_id is not None
            and anahtar is not None
        ):
            entry_id = satir[6:].split(" — ", 1)[0].strip()
            etiketler[(ornek_id, anahtar)].add(entry_id)
    return etiketler


def recall_at_k(sirali: list[str], ilgili: set[str], k: int = 5) -> float | None:
    """İlk ``k`` sonuçta bulunan ilgili maddeler / ``min(k, |ilgili|)``. İlgili yoksa None."""
    if not ilgili:
        return None
    bulunan = len(set(sirali[:k]) & ilgili)
    return bulunan / min(k, len(ilgili))


def mrr(sirali: list[str], ilgili: set[str]) -> float | None:
    """İlk ilgili maddenin sırasının tersi; hiçbiri yoksa 0.0, ilgili kümesi boşsa None."""
    if not ilgili:
        return None
    for sira, entry_id in enumerate(sirali, start=1):
        if entry_id in ilgili:
            return 1.0 / sira
    return 0.0


def _ortalama(degerler: list[float]) -> float | None:
    if not degerler:
        return None
    return sum(degerler) / len(degerler)


def ozet(
    satirlar: list[Satir],
    etiketler: dict[tuple[str, str], set[str]],
    k: int = 5,
) -> dict[str, dict[str, float | int | None]]:
    """Çeşit başına ortalama Recall@k ve MRR ile kullanılan anahtar sayısı (``n``).

    Etiketi boş ya da hiç etiketlenmemiş anahtarlar hesaba katılmaz.
    """
    recall_degerleri: dict[str, list[float]] = {cesit: [] for cesit in CESITLER}
    mrr_degerleri: dict[str, list[float]] = {cesit: [] for cesit in CESITLER}
    for satir in satirlar:
        ilgili = etiketler.get((satir["ornek_id"], satir["anahtar"]))
        if not ilgili:
            continue
        sirali = [entry_id for entry_id, _skor in satir["sirali"]]
        cesit = satir["cesit"]
        recall = recall_at_k(sirali, ilgili, k)
        if recall is not None:
            recall_degerleri.setdefault(cesit, []).append(recall)
        mrr_degeri = mrr(sirali, ilgili)
        if mrr_degeri is not None:
            mrr_degerleri.setdefault(cesit, []).append(mrr_degeri)

    sonuc: dict[str, dict[str, float | int | None]] = {}
    for cesit in set(recall_degerleri) | set(mrr_degerleri):
        sonuc[cesit] = {
            "recall": _ortalama(recall_degerleri.get(cesit, [])),
            "mrr": _ortalama(mrr_degerleri.get(cesit, [])),
            "n": len(recall_degerleri.get(cesit, [])),
        }
    return sonuc


def _satir_yaz(dosya: TextIO, satir: Satir) -> None:
    dosya.write(json.dumps(satir, ensure_ascii=False) + "\n")


def deney_kos(
    ornekler: list[TestOrnegi],
    bag: Bagimliliklar,
    cikti: Path,
    cesitler: dict[str, tuple[frozenset[str], bool]] = CESITLER,
    k: int = 10,
    ilerleme: Callable[[str], None] | None = None,
) -> Path:
    """Her rüya için çıkarımı bir kez yapar, çeşitleri koşar ve sıralamaları yazar.

    Bir rüya hata verirse satır ``{"ornek_id", "hata"}`` olarak yazılır ve sonraki rüyaya
    geçilir. Hibrit indeks yoksa hiçbir çağrı yapılmadan ``ValueError`` verilir.
    """
    if bag.hibrit is None:
        raise ValueError("Getirme deneyi hibrit indeks ister; bag.hibrit None")

    cikti.parent.mkdir(parents=True, exist_ok=True)
    with cikti.open("w", encoding="utf-8") as dosya:
        for ornek in ornekler:
            try:
                girdi = RuyaGirdisi(metin=ornek.metin, baglam=ornek.baglam)
                cikarim, _kullanim = extract.extract(girdi, bag.istemci)
                eslesmeler = esleme.map_symbols(cikarim.gecerli_semboller, bag.varyantlar)
                # Boru hattıyla aynı ayıklama (run.yorumla); sembol sınırı uygulanmaz.
                eslesmeler = esleme.tekrarlari_ele(esleme.genel_fiilleri_ele(eslesmeler))
                _ornek_satirlari(dosya, ornek, eslesmeler, bag, cesitler, k)
            except RuyaHatasi as hata:
                _satir_yaz(dosya, {"ornek_id": ornek.id, "hata": f"{type(hata).__name__}: {hata}"})
            if ilerleme is not None:
                ilerleme(ornek.id)
    return cikti


def _ornek_satirlari(
    dosya: TextIO,
    ornek: TestOrnegi,
    eslesmeler: list[Eslesme],
    bag: Bagimliliklar,
    cesitler: dict[str, tuple[frozenset[str], bool]],
    k: int,
) -> None:
    """Bir rüyanın bütün çeşitleri için sıralama satırlarını yazar."""
    # Aynı anahtara düşen eşleşmeler tek satırda birleşir.
    benzersiz: dict[str, Eslesme] = {}
    for es in eslesmeler:
        benzersiz.setdefault(getirme_anahtari(es), es)

    for cesit, (kollar, rerank) in cesitler.items():
        sonuclar = hibrit.siralama(
            eslesmeler,
            bag.depo,
            bag.hibrit,
            bag.istemci,
            gelenekler=None,
            kollar=kollar,
            rerank=rerank,
            k=k,
        )
        for anahtar, es in benzersiz.items():
            sirali = sonuclar.get(anahtar, [])
            _satir_yaz(
                dosya,
                {
                    "ornek_id": ornek.id,
                    "cesit": cesit,
                    "anahtar": anahtar,
                    "sembol": es.sembol.yalin,
                    "sirali": [[entry_id, skor] for entry_id, skor in sirali],
                },
            )


def satirlari_oku(yol: Path) -> list[Satir]:
    """Sıralama dosyasını okur; hata satırlarını ve boş satırları atlar."""
    satirlar: list[Satir] = []
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if not satir.strip():
            continue
        kayit = json.loads(satir)
        if "hata" in kayit:
            continue
        satirlar.append(kayit)
    return satirlar
