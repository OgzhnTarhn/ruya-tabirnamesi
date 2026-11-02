"""zeyrek'in istediği NLTK punkt verisini data/nltk_data altına indirir.

Bilgisayarda bir kez çalıştırılır::

    uv run python scripts/nltk_kur.py
"""

from __future__ import annotations

import nltk

from ruya.config import ayarlar


def main() -> None:
    klasor = ayarlar().data_dir / "nltk_data"
    klasor.mkdir(parents=True, exist_ok=True)
    for kaynak in ("punkt", "punkt_tab"):
        if not nltk.download(kaynak, download_dir=str(klasor), quiet=True):
            raise SystemExit(f"İndirilemedi: {kaynak}")
    print(f"Hazır: {klasor}")


if __name__ == "__main__":
    main()
