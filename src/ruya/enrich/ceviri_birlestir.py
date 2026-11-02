"""Çeviri parçalarını maddelere işleme.

Çeviri LLM'e parça parça yaptırılır; her parça
``data/interim/ceviri/<kaynak>/parca_NNNN.jsonl`` dosyasına yazılır ve her satır
``entry_id``, ``sembol_ar``, ``sembol_tr`` ve ``metin_tr`` alanlarını taşır.
Bu modül parçaları ``entry_id`` ile birleştirir ve maddelerin çeviri alanlarını
doldurur; asıl metin (``metin_asli``) hiçbir zaman değişmez.

Yönergeler: docs/02, bölüm 5 · talimat: prompts/ceviri_v1.md
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from ruya.schemas import CeviriBilgisi, Madde

PARCA_DESENI = "parca_*.jsonl"


def ceviri_oku(klasor: Path) -> dict[str, dict[str, Any]]:
    """Klasördeki bütün ``parca_*.jsonl`` dosyalarını ``entry_id`` ile birleştirir.

    Boş satırlar atlanır; parça desenine uymayan dosyalar yok sayılır. Aynı
    ``entry_id`` birden çok parçada geçerse son okunan kayıt geçerlidir.
    """
    ceviriler: dict[str, dict[str, Any]] = {}
    for yol in sorted(klasor.glob(PARCA_DESENI)):
        for satir in yol.read_text(encoding="utf-8").splitlines():
            if not satir.strip():
                continue
            kayit = json.loads(satir)
            ceviriler[kayit["entry_id"]] = kayit
    return ceviriler


def ceviriyi_uygula(
    maddeler: list[Madde],
    ceviriler: dict[str, dict[str, Any]],
    *,
    model: str,
    tarih: dt.date,
) -> list[Madde]:
    """Çevirileri maddelere işler; girdi listesini değiştirmez, yeni liste döndürür.

    Her maddenin çevirisi olmalı ve her çevirinin bir maddesi olmalı; eksik ya da
    fazla kayıt varsa kimliğiyle birlikte ``ValueError`` yükseltilir.
    """
    maddelerin_idleri = {m.entry_id for m in maddeler}
    cevirisi_olmayanlar = [m.entry_id for m in maddeler if m.entry_id not in ceviriler]
    if cevirisi_olmayanlar:
        raise ValueError(f"çevirisi olmayan maddeler: {', '.join(cevirisi_olmayanlar)}")
    maddesi_olmayanlar = sorted(set(ceviriler) - maddelerin_idleri)
    if maddesi_olmayanlar:
        raise ValueError(f"maddesi olmayan çeviriler: {', '.join(maddesi_olmayanlar)}")

    bilgi = CeviriBilgisi(yontem="llm", model=model, tarih=tarih, gozden_gecirildi=False)
    sonuc: list[Madde] = []
    for madde in maddeler:
        kayit = ceviriler[madde.entry_id]
        sonuc.append(
            madde.model_copy(
                update={
                    "metin_tr": kayit.get("metin_tr"),
                    "sembol_ar": kayit.get("sembol_ar"),
                    "sembol_tr": kayit.get("sembol_tr"),
                    "ceviri": bilgi,
                }
            )
        )
    return sonuc
