"""Taranmış kaynak görsellerini OCR ile metne çevirir.

Verilen klasördeki her ``.png``, ``.jpg``, ``.jpeg`` ve ``.webp`` dosyası ada göre
sıralanır ve ``LLMIstemcisi(ayarlar()).ocr`` ile okunur; metin
``ayarlar().veri("interim", "ocr", "<klasör adı>", "<dosya adı>.txt")`` dosyasına
yazılır. Hedef dosya zaten varsa görsel atlanır, böylece yarıda kesilen iş
kaldığı yerden devam eder. İlerleme ``flush=True`` ile ekrana yazılır.

Taranmış kaynaklar içindir; API anahtarı ve görseller gerekir, yalnızca ``data/``
altına yazar. Bilgisayarda çalışır::

    uv run python scripts/belge_ocr.py <klasor>
"""

from __future__ import annotations

import sys
from pathlib import Path

from ruya.config import ayarlar
from ruya.llm.client import LLMIstemcisi

GORSELLER = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def main(klasor: Path) -> int:
    ayar = ayarlar()
    if not klasor.is_dir():
        print(f"klasör bulunamadı: {klasor}", file=sys.stderr)
        return 2

    gorseller = sorted(
        (yol for yol in klasor.iterdir() if yol.is_file() and yol.suffix.lower() in GORSELLER),
        key=lambda yol: yol.name,
    )
    if not gorseller:
        print(f"görsel yok: {klasor}", flush=True)
        return 0

    cikti_klasoru = ayar.veri("interim", "ocr", klasor.name)
    istemci = LLMIstemcisi(ayar)
    atlanan = 0
    okunan = 0

    for sira, yol in enumerate(gorseller, start=1):
        hedef = cikti_klasoru / f"{yol.stem}.txt"
        if hedef.exists():
            atlanan += 1
            print(f"[{sira}/{len(gorseller)}] atlandı (var): {yol.name}", flush=True)
            continue
        print(f"[{sira}/{len(gorseller)}] okunuyor: {yol.name}", flush=True)
        metin = istemci.ocr(yol.read_bytes(), GORSELLER[yol.suffix.lower()])
        hedef.parent.mkdir(parents=True, exist_ok=True)
        hedef.write_text(metin, encoding="utf-8")
        okunan += 1
        print(f"[{sira}/{len(gorseller)}] yazıldı: {hedef}", flush=True)

    print(f"bitti: okunan {okunan}, atlanan {atlanan}, klasör: {cikti_klasoru}", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: uv run python scripts/belge_ocr.py <klasor>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
