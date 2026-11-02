"""Ölçütler (docs/06, bölüm 2). Her işlev saf: SorguKaydi + TestOrnegi → sayı.

Ragas ya da DeepEval kullanılmaz (TK-10); ölçütleri kendin yazmak neyin neden
ölçüldüğünü öğretir. Takvim: Hafta 5.
"""

from __future__ import annotations

from ruya.etik import YASAK_IFADELER
from ruya.schemas import SorguKaydi, TestOrnegi
from ruya.text.turkce import kucuk_harf


def _eslenen_kimlikler(kayit: SorguKaydi) -> list[str]:
    """Eşlenen (symbol_id'si dolu) sembollerin kimlikleri."""
    return [e.symbol_id for e in kayit.eslesmeler if e.symbol_id is not None]


def sembol_recall(kayit: SorguKaydi, ornek: TestOrnegi) -> float | None:
    """Bulunan beklenen sembol / beklenen semboller. Beklenen yoksa None."""
    if not ornek.beklenen_semboller:
        return None
    bulunan = set(_eslenen_kimlikler(kayit))
    dogru = sum(1 for sid in ornek.beklenen_semboller if sid in bulunan)
    return dogru / len(ornek.beklenen_semboller)


def sembol_precision(kayit: SorguKaydi, ornek: TestOrnegi) -> float | None:
    """Doğru semboller / eşlenen semboller. Eşlenen sembol yoksa None."""
    eslenen = _eslenen_kimlikler(kayit)
    if not eslenen:
        return None
    beklenen = set(ornek.beklenen_semboller)
    dogru = sum(1 for sid in eslenen if sid in beklenen)
    return dogru / len(eslenen)


def olumsuzlama_hatalari(kayit: SorguKaydi, ornek: TestOrnegi) -> int:
    """``olmamasi_gerekenler`` listesinden yine de eşlenen sembol sayısı."""
    yasak = set(ornek.olmamasi_gerekenler)
    return sum(1 for sid in _eslenen_kimlikler(kayit) if sid in yasak)


def esleme_dogrulugu(kayit: SorguKaydi, ornek: TestOrnegi) -> float | None:
    """Doğru ``symbol_id`` / eşlenen semboller. Eşlenen sembol yoksa None."""
    eslenen = _eslenen_kimlikler(kayit)
    if not eslenen:
        return None
    beklenen = set(ornek.beklenen_semboller)
    dogru = sum(1 for sid in eslenen if sid in beklenen)
    return dogru / len(eslenen)


def recall_at_k(kayit: SorguKaydi, ornek: TestOrnegi, k: int = 5) -> float | None:
    """İlk ``k`` adayda bulunan beklenen maddeler / bütün beklenen maddeler."""
    beklenen = [(sid, entry_id) for sid, ids in ornek.beklenen_maddeler.items() for entry_id in ids]
    if not beklenen:
        return None
    bulunan = 0
    for sid, entry_id in beklenen:
        ilk_k = [aday.madde.entry_id for aday in kayit.getirilenler.get(sid, [])[:k]]
        if entry_id in ilk_k:
            bulunan += 1
    return bulunan / len(beklenen)


def kaynak_cesitliligi(kayit: SorguKaydi) -> float | None:
    """Maddesi olan semboller için ortalama farklı kaynak sayısı."""
    kaynak_sayilari = [
        len({aday.madde.kaynak for aday in adaylar})
        for adaylar in kayit.getirilenler.values()
        if adaylar
    ]
    if not kaynak_sayilari:
        return None
    return sum(kaynak_sayilari) / len(kaynak_sayilari)


def _baslik_mi(metin: str) -> bool:
    """Bölümün bütün dolu satırları ``#`` ile başlıyorsa başlık bölümüdür."""
    satirlar = [satir.strip() for satir in metin.splitlines() if satir.strip()]
    return bool(satirlar) and all(satir.startswith("#") for satir in satirlar)


def atif_kapsami(kayit: SorguKaydi) -> float | None:
    """Atıf taşıyan iddia bölümleri / bütün iddia bölümleri. Başlık bölümleri ve harf
    içermeyen bölümler sayılmaz (docs/06, bölüm 2). İddia bölümü yoksa None."""
    if kayit.yorum is None:
        return None
    iddialar = [
        bolum
        for bolum in kayit.yorum.bolumler
        if not _baslik_mi(bolum.metin) and any(harf.isalpha() for harf in bolum.metin)
    ]
    if not iddialar:
        return None
    atifli = sum(1 for bolum in iddialar if bolum.atiflar)
    return atifli / len(iddialar)


def yasak_ifadeler(metin: str) -> list[str]:
    """Metinde geçen etik.YASAK_IFADELER (Türkçe küçük harfle karşılaştırılır)."""
    kucuk = kucuk_harf(metin)
    return [ifade for ifade in YASAK_IFADELER if ifade in kucuk]
