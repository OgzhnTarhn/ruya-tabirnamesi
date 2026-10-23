"""Adım 4 · Sentez: kaynaklı Türkçe yorum (Claude, search_result atıfları). Takvim: Hafta 5.

- Her aday bir ``search_result`` bloğu olur: source=entry_id, title="Nablusi · حية (yılan)",
  content=metin_tr + metin_asli, citations etkin. Atıflar ``Atif`` nesnelerine çevrilir.
- Sistem talimatı ``prompts/sentez_v<n>.md``; kurallar docs/05 bölüm 3 ve docs/07.
  Sabit talimat prompt önbelleğine alınır.
- Eşleşmeyen ya da maddesi olmayan semboller ``Yorum.bulunamayanlar``'a (İG-31).
- ``cikarim.hassas_icerik`` ise ``Yorum.guvenlik_notu = etik.GUVENLIK_NOTU``.
- ``Yorum.uyari`` her zaman ``etik.UYARI_METNI`` (İG-36).
"""

from __future__ import annotations

from ruya.llm.client import LLMIstemcisi
from ruya.schemas import Baglam, CikarimSonucu, Eslesme, Getirilenler, Kullanim, Yorum

TALIMAT = "sentez_v1"


def synthesize(
    cikarim: CikarimSonucu,
    eslesmeler: list[Eslesme],
    getirilenler: Getirilenler,
    baglam: Baglam | None,
    istemci: LLMIstemcisi,
) -> tuple[Yorum, Kullanim]:
    raise NotImplementedError("Hafta 5: pipeline/synthesize.py (docs/08)")
