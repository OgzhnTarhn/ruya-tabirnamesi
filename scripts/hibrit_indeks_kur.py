"""Hibrit vektör indeksini kurar (docs/13-hibrit-getirme.md, bölüm 4).

Maddeler ``Ayarlar().maddeler_dosyasi`` dosyasından, sembol sözlüğü
``sozlugu_yukle`` ile okunur; gömücü olarak ``LLMIstemcisi.gom`` kullanılır ve indeks
``Ayarlar().veri("index", "hibrit")`` klasörüne yazılır. Gömme uzun sürer ve API'ye
istek atar; bilgisayarda çalışır, veri ve API anahtarı gerektirir::

    uv run python scripts/hibrit_indeks_kur.py
"""

from __future__ import annotations

import json

from ruya.config import MODEL_EMBEDDING, ayarlar
from ruya.dosya import jsonl_oku
from ruya.index.build_vectors import MANIFEST_DOSYASI, hibrit_indeks_kur
from ruya.llm.client import LLMIstemcisi
from ruya.schemas import Madde


def main() -> None:
    ayar = ayarlar()
    klasor = ayar.veri("index", "hibrit")

    print(f"maddeler okunuyor: {ayar.maddeler_dosyasi}", flush=True)
    maddeler = list(jsonl_oku(ayar.maddeler_dosyasi, Madde))
    print(f"madde: {len(maddeler)}", flush=True)

    istemci = LLMIstemcisi(ayar)
    print(f"indeks kuruluyor: {klasor} (model: {MODEL_EMBEDDING})", flush=True)
    hibrit_indeks_kur(
        maddeler,
        gomucu=istemci.gom,
        model=MODEL_EMBEDDING,
        klasor=klasor,
    )

    manifest = json.loads((klasor / MANIFEST_DOSYASI).read_text(encoding="utf-8"))
    print(f"parça: {manifest['parca_sayisi']}, boyut: {manifest['boyut']}", flush=True)
    print(f"bitti: {klasor}", flush=True)


if __name__ == "__main__":
    main()
