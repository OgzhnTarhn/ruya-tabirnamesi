"""Sorgu logu ve isteğe bağlı rüya geçmişi (docs/03, bölüm 5.3).

- ``logs/sorgular.jsonl``: her sorguda bir satır, **rüya metni olmadan** (SorguKaydi.log_kaydi).
- ``gecmis/``: yalnızca ``RUYA_GECMIS=on`` ise; rüyanın tamamı data/ altında saklanır.
"""

from __future__ import annotations

from pathlib import Path

from ruya.config import Ayarlar
from ruya.dosya import jsonl_ekle
from ruya.schemas import SorguKaydi


def sorgu_logla(kayit: SorguKaydi, ayar: Ayarlar) -> Path:
    yol = ayar.log_klasoru / "sorgular.jsonl"
    jsonl_ekle(kayit.log_kaydi(), yol)
    return yol


def gecmise_yaz(kayit: SorguKaydi, ayar: Ayarlar) -> Path | None:
    """Rüya geçmişi kapalıysa hiçbir şey yazmaz ve None döndürür."""
    if not ayar.gecmis:
        return None
    yol = ayar.gecmis_klasoru / f"{kayit.zaman:%Y-%m}.jsonl"
    jsonl_ekle(kayit.model_dump(mode="json"), yol)
    return yol
