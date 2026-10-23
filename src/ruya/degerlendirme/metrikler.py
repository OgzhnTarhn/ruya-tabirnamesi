"""Ölçütler (docs/06, bölüm 2). Her işlev saf: SorguKaydi + TestOrnegi → sayı.

Ragas ya da DeepEval kullanılmaz (TK-10); ölçütleri kendin yazmak neyin neden
ölçüldüğünü öğretir. Takvim: Hafta 5.
"""

from __future__ import annotations

from ruya.schemas import SorguKaydi, TestOrnegi


def sembol_recall(kayit: SorguKaydi, ornek: TestOrnegi) -> float | None:
    """Bulunan beklenen sembol / beklenen semboller. Beklenen yoksa None."""
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def sembol_precision(kayit: SorguKaydi, ornek: TestOrnegi) -> float | None:
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def olumsuzlama_hatalari(kayit: SorguKaydi, ornek: TestOrnegi) -> int:
    """``olmamasi_gerekenler`` listesinden yine de eşlenen sembol sayısı."""
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def esleme_dogrulugu(kayit: SorguKaydi, ornek: TestOrnegi) -> float | None:
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def recall_at_k(kayit: SorguKaydi, ornek: TestOrnegi, k: int = 5) -> float | None:
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def kaynak_cesitliligi(kayit: SorguKaydi) -> float | None:
    """Maddesi olan semboller için ortalama farklı kaynak sayısı."""
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def atif_kapsami(kayit: SorguKaydi) -> float | None:
    """Atıf taşıyan yorum bölümleri / bütün yorum bölümleri."""
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")


def yasak_ifadeler(metin: str) -> list[str]:
    """Metinde geçen etik.YASAK_IFADELER (Türkçe küçük harfle karşılaştırılır)."""
    raise NotImplementedError("Hafta 5: degerlendirme/metrikler.py (docs/08)")
