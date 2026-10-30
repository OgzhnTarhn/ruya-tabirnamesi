"""Test setini çalıştırır ve raporu Drive'a yazar (docs/06, bölüm 3).

Colab'de notebooks/06_degerlendirme.ipynb çağırır::

    python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl --etiket asama1-opus

Her çalıştırma ücretlidir. Geliştirme sırasında LLM disk önbelleği açık kalır;
burada ayrıca rüya içeren istekler için sorgu önbelleği açılır (docs/03, 5.2).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ruya.config import ayarlar
from ruya.degerlendirme.calistir import degerlendir
from ruya.pipeline.run import varsayilan_bagimliliklar


def main(argv: list[str] | None = None) -> None:
    ayristirici = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ayristirici.add_argument("--dataset", type=Path, required=True)
    ayristirici.add_argument("--etiket", required=True, help="ör. asama1-opus")
    args = ayristirici.parse_args(argv)
    # Test setindeki rüyalar zaten repoda; aynı ölçüm ikinci kez ücret ödetmesin (docs/03, 5.2).
    ayar = ayarlar().model_copy(update={"sorgu_onbellegi": True})
    rapor = degerlendir(args.dataset, args.etiket, varsayilan_bagimliliklar(ayar))
    print(f"Rapor: {rapor}")


if __name__ == "__main__":
    main()
