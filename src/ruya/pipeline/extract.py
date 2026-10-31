"""Adım 1 · Sembol çıkarımı (LLM, yapılandırılmış JSON çıktı). Takvim: Hafta 4.

- ``response_format`` ile JSON şeması (``json_schema``, ``strict: true``; CikarimSonucu).
- Semboller yalın ve küçük harfle, **belirginlik sırasıyla** döner; run.py ilk
  ``en_fazla_sembol`` tanesini işler.
- Olumsuzlanan semboller ``olumsuz=True`` (İG-12); çok kelimeli semboller tek sembol (İG-13).
- Getirme çıkarımın sonucuna bağlı olduğu için çıkarım ve sentez ayrı çağrılardır.
- İstek ``istemci.mesaj(istek, ruya_icerir=True)`` ile gönderilir (rüya metni
  içerir; docs/03 bölüm 5.2).
"""

from __future__ import annotations

from ruya.llm.client import LLMIstemcisi
from ruya.schemas import CikarimSonucu, Kullanim, RuyaGirdisi

TALIMAT = "cikarim_v1"


def extract(girdi: RuyaGirdisi, istemci: LLMIstemcisi) -> tuple[CikarimSonucu, Kullanim]:
    raise NotImplementedError("Hafta 4: pipeline/extract.py (docs/08)")
