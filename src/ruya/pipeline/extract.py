"""Adım 1 · Sembol çıkarımı (Claude, yapılandırılmış JSON çıktı). Takvim: Hafta 4.

- ``output_config.format`` ile JSON şeması (CikarimSonucu); effort: config.EFFORT_CIKARIM.
- Semboller yalın ve küçük harfle, **belirginlik sırasıyla** döner; run.py ilk
  ``en_fazla_sembol`` tanesini işler.
- Olumsuzlanan semboller ``olumsuz=True`` (İG-12); çok kelimeli semboller tek sembol (İG-13).
- Atıf (citations) ile yapılandırılmış çıktı aynı istekte kullanılamaz; bu yüzden
  çıkarım ve sentez ayrı çağrılardır.
"""

from __future__ import annotations

from ruya.llm.client import LLMIstemcisi
from ruya.schemas import CikarimSonucu, Kullanim, RuyaGirdisi

TALIMAT = "cikarim_v1"


def extract(girdi: RuyaGirdisi, istemci: LLMIstemcisi) -> tuple[CikarimSonucu, Kullanim]:
    raise NotImplementedError("Hafta 4: pipeline/extract.py (docs/08)")
