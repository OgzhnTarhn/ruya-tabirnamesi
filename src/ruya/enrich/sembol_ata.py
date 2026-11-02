"""Maddelere sözlükten ``symbol_ids`` atama (LLM'siz, deterministik). Takvim: Hafta 3.

Çevirinin önerdiği ham sembol adı (``sembol_tr``) Türkçe kurallarına göre
normalleştirilir ve ``varyant_tablosu``nun ürettiği ``{normalleştirilmiş ad: symbol_id}``
eşlemesinde aranır. Eşleşen madde kimliği alır; eşleşmeyen alt paragraf (``ust_madde_id``
dolu) üst maddesinin kimliğini devralır. Freud maddelerinde ``sembol_tr`` yoktur, bu yüzden
kimlik almazlar.

Bu modül LLM çağırmaz ve yalnızca ``ruya.schemas`` ile ``ruya.text.turkce`` birimlerini
içe aktarır (docs/12, bölüm 1).
"""

from __future__ import annotations

from ruya.schemas import Madde
from ruya.text.turkce import normallestir


def sembol_ata(maddeler: list[Madde], varyantlar: dict[str, str]) -> list[Madde]:
    """Maddelerin kopyalarını, ``symbol_ids`` doldurulmuş olarak döndürür.

    ``varyantlar`` normalleştirilmiş ad → ``symbol_id`` tablosudur (``varyant_tablosu``).
    Girdi nesneleri değiştirilmez, sıra korunur.
    """
    dogrudan: dict[str, list[str]] = {}
    for madde in maddeler:
        if madde.sembol_tr is None:
            continue
        symbol_id = varyantlar.get(normallestir(madde.sembol_tr))
        if symbol_id is not None:
            dogrudan[madde.entry_id] = [symbol_id]

    maddeler_by_id = {m.entry_id: m for m in maddeler}

    def _kimlikler(madde: Madde) -> list[str]:
        """Kendi eşleşmesi yoksa üst maddeler zincirinde ilk eşleşmeyi arar."""
        simdiki: Madde | None = madde
        gorulen: set[str] = set()
        while simdiki is not None and simdiki.entry_id not in gorulen:
            if simdiki.entry_id in dogrudan:
                return list(dogrudan[simdiki.entry_id])
            gorulen.add(simdiki.entry_id)
            simdiki = maddeler_by_id.get(simdiki.ust_madde_id) if simdiki.ust_madde_id else None
        return []

    return [m.model_copy(update={"symbol_ids": _kimlikler(m)}) for m in maddeler]
