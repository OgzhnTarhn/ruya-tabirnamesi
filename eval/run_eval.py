"""Test setini çalıştırır ve raporu Drive'a yazar (docs/06, bölüm 3).

Colab'de notebooks/06_degerlendirme.ipynb çağırır::

    python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl --etiket asama1-opus

Her çalıştırma ücretlidir. Geliştirme sırasında LLM disk önbelleği açık kalır.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ruya.degerlendirme.calistir import degerlendir
from ruya.pipeline.run import varsayilan_bagimliliklar


def main(argv: list[str] | None = None) -> None:
    ayristirici = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ayristirici.add_argument("--dataset", type=Path, required=True)
    ayristirici.add_argument("--etiket", required=True, help="ör. asama1-opus")
    args = ayristirici.parse_args(argv)
    rapor = degerlendir(args.dataset, args.etiket, varsayilan_bagimliliklar())
    print(f"Rapor: {rapor}")


if __name__ == "__main__":
    main()
