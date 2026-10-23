"""Sürümlü sistem talimatlarını ``prompts/`` klasöründen okur.

Adlandırma: ``<is>_v<n>.md`` (ör. ``sentez_v1.md``). Bir ölçüm raporunda kullanılmış bir
sürüm bir daha değiştirilmez; değişiklik yeni bir sürüm dosyasıyla yapılır.
"""

from __future__ import annotations

import re
from pathlib import Path

from ruya.config import TALIMAT_KLASORU

TALIMAT_ADI_DESENI = r"^[a-z_]+_v\d+$"


def talimat_oku(ad: str, klasor: Path = TALIMAT_KLASORU) -> str:
    """``talimat_oku("sentez_v1")`` → ``prompts/sentez_v1.md`` dosyasının metni."""
    if not re.fullmatch(TALIMAT_ADI_DESENI, ad):
        raise ValueError(f"talimat adı '<is>_v<n>' biçiminde olmalı: {ad!r}")
    yol = klasor / f"{ad}.md"
    if not yol.is_file():
        raise FileNotFoundError(f"talimat dosyası yok: {yol}")
    return yol.read_text(encoding="utf-8").strip()
