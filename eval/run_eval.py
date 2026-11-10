"""Test setini çalıştırır ve raporu data/raporlar/ altına yazar (docs/06, bölüm 3).

Bilgisayarda::

    uv run python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl --etiket asama1-deepseek

Alt küme ve kaynak sayısı (D3)::

    uv run python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl \\
        --alt-kume eval/dataset/alt_kume_15.txt --n 2 --etiket d3-n2

Rakip sentez modeli (D4)::

    uv run python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl \\
        --sentez-modeli d4 --etiket d4-mimo

Her çalıştırma ücretlidir. Geliştirme sırasında LLM disk önbelleği açık kalır;
burada ayrıca rüya içeren istekler için sorgu önbelleği açılır (docs/03, 5.2).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ruya import config
from ruya.config import ayarlar
from ruya.degerlendirme.calistir import degerlendir
from ruya.pipeline import synthesize
from ruya.pipeline.run import varsayilan_bagimliliklar


def _alt_kume(yol: Path) -> set[str]:
    """Alt küme dosyasındaki kimlikler (satır başına bir tane)."""
    satirlar = yol.read_text(encoding="utf-8").splitlines()
    return {satir.strip() for satir in satirlar if satir.strip()}


def main(argv: list[str] | None = None) -> None:
    ayristirici = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ayristirici.add_argument("--dataset", type=Path, required=True)
    ayristirici.add_argument("--etiket", required=True, help="ör. asama1-deepseek")
    ayristirici.add_argument("--alt-kume", type=Path, help="yalnız bu kimlikler çalıştırılır")
    ayristirici.add_argument("--n", type=int, help="kaynak başına madde sayısı")
    ayristirici.add_argument(
        "--sentez-modeli",
        choices=("varsayilan", "d4"),
        default="varsayilan",
        help="d4: D4 deneyinin rakip sentez modeli (docs/15, K7)",
    )
    args = ayristirici.parse_args(argv)
    # Test setindeki rüyalar zaten repoda; aynı ölçüm ikinci kez ücret ödetmesin (docs/03, 5.2).
    guncelleme: dict = {"sorgu_onbellegi": True}
    if args.n is not None:
        guncelleme["kaynak_basina_n"] = args.n
    ayar = ayarlar().model_copy(update=guncelleme)
    kimlikler = _alt_kume(args.alt_kume) if args.alt_kume is not None else None
    onceki_model = synthesize.MODEL_SENTEZ
    if args.sentez_modeli == "d4":
        synthesize.MODEL_SENTEZ = config.MODEL_SENTEZ_D4
    try:
        rapor = degerlendir(
            args.dataset,
            args.etiket,
            varsayilan_bagimliliklar(ayar),
            kimlikler=kimlikler,
        )
    finally:
        synthesize.MODEL_SENTEZ = onceki_model
    print(f"Rapor: {rapor}")


if __name__ == "__main__":
    main()
