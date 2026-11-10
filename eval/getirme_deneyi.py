"""Getirme deneyi (D1/D2) betiği: sıralamaları üret, etiket dosyasını yaz, özeti bas.

Bilgisayarda::

    uv run python eval/getirme_deneyi.py kos --dataset eval/dataset/ruyalar_v1.jsonl \\
        --alt-kume eval/dataset/alt_kume_15.txt
    uv run python eval/getirme_deneyi.py etiket
    uv run python eval/getirme_deneyi.py ozet --k 5

``kos`` her rüyanın çıkarımını bir kez yapar ve dört çeşidin sıralamasını
``data/deneyler/getirme/siralamalar.jsonl`` altına yazar. ``etiket`` bu sıralamalardan
TREC usulü havuzu çıkarıp işaretlemeye hazır Markdown dosyası yazar; var olan dosyanın
üstüne ancak ``--uzerine-yaz`` ile yazılır, böylece işaretler kaybolmaz. ``ozet``
işaretli dosyayı okuyup çeşit başına Recall@k ve MRR tablosunu basar.

Her çalıştırma ücretlidir; rüya içeren istekler için sorgu önbelleği açılır (docs/03, 5.2).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ruya.config import ayarlar
from ruya.degerlendirme.getirme_deneyi import (
    CESITLER,
    deney_kos,
    etiket_dosyasi_yaz,
    etiketleri_oku,
    havuz,
    ozet,
    satirlari_oku,
)
from ruya.dosya import jsonl_oku
from ruya.pipeline.run import varsayilan_bagimliliklar
from ruya.schemas import TestOrnegi


def _alt_kume(yol: Path) -> set[str]:
    """Alt küme dosyasındaki kimlikler (satır başına bir tane)."""
    satirlar = yol.read_text(encoding="utf-8").splitlines()
    return {satir.strip() for satir in satirlar if satir.strip()}


def _ornekler(dataset: Path, alt_kume: Path) -> list[TestOrnegi]:
    """Test setinden yalnız alt kümedeki rüyaları, dosya sırasıyla döndürür."""
    kimlikler = _alt_kume(alt_kume)
    return [ornek for ornek in jsonl_oku(dataset, TestOrnegi) if ornek.id in kimlikler]


def _kos(args: argparse.Namespace) -> None:
    ayar = ayarlar().model_copy(update={"sorgu_onbellegi": True})
    cikti = args.cikti or ayar.veri("deneyler", "getirme", "siralamalar.jsonl")
    bag = varsayilan_bagimliliklar(ayar)
    ornekler = _ornekler(args.dataset, args.alt_kume)
    deney_kos(ornekler, bag, cikti, ilerleme=lambda ornek_id: print(ornek_id, flush=True))
    print(f"Sıralamalar: {cikti}")


def _etiket(args: argparse.Namespace) -> None:
    ayar = ayarlar()
    siralamalar = args.siralamalar or ayar.veri("deneyler", "getirme", "siralamalar.jsonl")
    cikti = args.cikti or ayar.veri("deneyler", "getirme", "etiketler.md")
    if cikti.exists() and not args.uzerine_yaz:
        raise SystemExit(f"{cikti} zaten var; işaretleri korumak için --uzerine-yaz gerekli")

    satirlar = satirlari_oku(siralamalar)
    metinler = {ornek.id: ornek.metin for ornek in jsonl_oku(args.dataset, TestOrnegi)}
    bag = varsayilan_bagimliliklar(ayar)
    etiket_dosyasi_yaz(havuz(satirlar, k=args.k), satirlar, metinler, bag.depo, cikti)
    print(f"Etiket dosyası: {cikti}")


def _bicimle(deger: float | int | None) -> str:
    if deger is None:
        return "—"
    if isinstance(deger, int):
        return str(deger)
    return f"{deger:.3f}".replace(".", ",")


def _ozet(args: argparse.Namespace) -> None:
    ayar = ayarlar()
    siralamalar = args.siralamalar or ayar.veri("deneyler", "getirme", "siralamalar.jsonl")
    etiketler = args.etiketler or ayar.veri("deneyler", "getirme", "etiketler.md")
    sonuc = ozet(satirlari_oku(siralamalar), etiketleri_oku(etiketler), k=args.k)

    print(f"| Çeşit | Recall@{args.k} | MRR | n |")
    print("|---|---|---|---|")
    for cesit in sorted(sonuc, key=lambda ad: (ad not in CESITLER, ad)):
        satir = sonuc[cesit]
        print(
            f"| {cesit} | {_bicimle(satir['recall'])} | {_bicimle(satir['mrr'])} "
            f"| {_bicimle(satir['n'])} |"
        )


def main(argv: list[str] | None = None) -> None:
    ayristirici = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    alt = ayristirici.add_subparsers(dest="komut", required=True)

    kos = alt.add_parser("kos", help="çıkarımı yap, dört çeşidi koş, sıralamaları yaz")
    kos.add_argument("--dataset", type=Path, default=Path("eval/dataset/ruyalar_v1.jsonl"))
    kos.add_argument("--alt-kume", type=Path, default=Path("eval/dataset/alt_kume_15.txt"))
    kos.add_argument("--cikti", type=Path)
    kos.set_defaults(islev=_kos)

    etiket = alt.add_parser("etiket", help="havuzu işaretlemeye hazır Markdown olarak yaz")
    etiket.add_argument("--siralamalar", type=Path)
    etiket.add_argument("--cikti", type=Path)
    etiket.add_argument("--dataset", type=Path, default=Path("eval/dataset/ruyalar_v1.jsonl"))
    etiket.add_argument("--k", type=int, default=5)
    etiket.add_argument("--uzerine-yaz", action="store_true", help="var olan dosyanın üstüne yaz")
    etiket.set_defaults(islev=_etiket)

    ozet_komut = alt.add_parser("ozet", help="çeşit başına Recall@k ve MRR tablosu")
    ozet_komut.add_argument("--siralamalar", type=Path)
    ozet_komut.add_argument("--etiketler", type=Path)
    ozet_komut.add_argument("--k", type=int, default=5)
    ozet_komut.set_defaults(islev=_ozet)

    args = ayristirici.parse_args(argv)
    args.islev(args)


if __name__ == "__main__":
    main()
