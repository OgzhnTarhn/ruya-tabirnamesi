"""Gradio arayüzünü yerelde açar (İG-40).

``app/`` bir paket değildir; bu yüzden önce repo kökü ``sys.path``'e eklenir ve
``app.gradio_app`` kökten içe aktarılır. Sonra gerçek bağımlılıklar (sözlük, ``data/``
maddeleri, LLM istemcisi) kurulup arayüz başlatılır; sunucu yalnızca ``127.0.0.1``'de
dinler. Veri ve API anahtarı gerekir::

    uv run python scripts/arayuz_ac.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    """Repo kökünü yola ekleyip arayüzü varsayılan bağımlılıklarla başlatır."""
    kok = Path(__file__).resolve().parents[1]
    if str(kok) not in sys.path:
        sys.path.insert(0, str(kok))

    from app.gradio_app import baslat

    from ruya.pipeline.run import varsayilan_bagimliliklar

    baslat(varsayilan_bagimliliklar())


if __name__ == "__main__":
    main()
