"""Test setini çalıştırır, data/raporlar/ altına rapor yazar (docs/06, bölüm 3). Takvim: Hafta 5.

Rapor: ``raporlar/<tarih>_<etiket>.md``: ölçüt tablosu, başarısız örnekler, toplam
maliyet ve elle doldurulacak sadakat kontrol listesi. Özet satır docs/olcumler.md'ye
elle eklenip commit edilir.
"""

from __future__ import annotations

from pathlib import Path

from ruya.pipeline.run import Bagimliliklar


def degerlendir(veri_seti: Path, etiket: str, bag: Bagimliliklar) -> Path:
    """Raporun data/raporlar/ altındaki yolunu döndürür.

    Her çalıştırma ücretlidir (~0,10 $ × rüya sayısı)."""
    raise NotImplementedError("Hafta 5: degerlendirme/calistir.py (docs/08)")
