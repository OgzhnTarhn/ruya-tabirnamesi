"""JSONL okuma ve yazma.

Büyük dosyalar önce hedefin yanındaki geçici bir dosyaya yazılır, sonra tek seferde
hedefe taşınır; böylece bir çökme yarım dosya bırakmaz.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


def jsonl_oku(yol: Path, sema: type[M]) -> Iterator[M]:
    """Her satırı şemaya göre doğrulayarak okur. Hatalı satırda satır numarasıyla hata verir."""
    with yol.open(encoding="utf-8") as dosya:
        for no, satir in enumerate(dosya, start=1):
            if not satir.strip():
                continue
            try:
                yield sema.model_validate_json(satir)
            except ValueError as hata:
                raise ValueError(f"{yol}:{no}: {hata}") from hata


def jsonl_yaz(kayitlar: Iterable[BaseModel], yol: Path) -> int:
    """Kayıtları yerel bir geçici dosyaya yazar, sonra hedefe taşır.

    Yazılan satır sayısını döndürür."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    sayi = 0
    tanitici, gecici = tempfile.mkstemp(suffix=".jsonl")
    try:
        with os.fdopen(tanitici, "w", encoding="utf-8") as dosya:
            for kayit in kayitlar:
                dosya.write(kayit.model_dump_json(exclude_none=False) + "\n")
                sayi += 1
        shutil.move(gecici, yol)
    except BaseException:
        Path(gecici).unlink(missing_ok=True)
        raise
    return sayi


def jsonl_ekle(kayit: dict, yol: Path) -> None:
    """Tek bir satırı dosyanın sonuna ekler (loglar için)."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    with yol.open("a", encoding="utf-8") as dosya:
        dosya.write(json.dumps(kayit, ensure_ascii=False) + "\n")
