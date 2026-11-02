"""Bir rüyayı uçtan uca boru hattından geçirip her adımın çıktısını ekrana yazar.

Gerçek bağımlılıklarla (sözlük, ``data/`` maddeleri, LLM istemcisi) çalışır; bu yüzden
API anahtarı ve veri gerekir. Çıktı UTF-8'e ayarlanır (Windows konsolu Türkçe karakterleri
bozmasın). Yorum üretilemezse ya da yorumda hiç doğrulanmış atıf yoksa betik sıfırdan
farklı kodla çıkar. Bilgisayarda çalışır::

    uv run python scripts/ruya_dene.py "Rüyamda denizde yüzerken büyük siyah bir yılan gördüm."
"""

from __future__ import annotations

import sys

from ruya.pipeline import run
from ruya.schemas import RuyaGirdisi


def _yaz(baslik: str, deger: object = "") -> None:
    print(f"{baslik}: {deger}" if deger != "" else baslik)


def main() -> int:
    if len(sys.argv) < 2:
        print('Kullanım: uv run python scripts/ruya_dene.py "<rüya metni>"', file=sys.stderr)
        return 2

    girdi = RuyaGirdisi(metin=sys.argv[1])
    bag = run.varsayilan_bagimliliklar()
    kayit = run.yorumla(girdi, bag)

    _yaz("=== Semboller ===")
    if kayit.cikarim is None:
        _yaz("(çıkarım yok)")
    else:
        for sembol in kayit.cikarim.semboller:
            _yaz(
                f"- {sembol.yalin}",
                f"nitelikler={sembol.nitelikler} eylem={sembol.eylem} "
                f"duygu={sembol.duygu} olumsuz={sembol.olumsuz}",
            )
        if kayit.atlanan_semboller:
            _yaz("Atlanan semboller", ", ".join(kayit.atlanan_semboller))

    print()
    _yaz("=== Eşleşmeler ===")
    if not kayit.eslesmeler:
        _yaz("(eşleşme yok)")
    for eslesme in kayit.eslesmeler:
        _yaz(
            f"- {eslesme.sembol.yalin}",
            f"symbol_id={eslesme.symbol_id} yöntem={eslesme.yontem} güven={eslesme.guven:.2f}",
        )

    print()
    _yaz("=== Aday maddeler ===")
    if not kayit.getirilenler:
        _yaz("(aday yok)")
    for symbol_id, adaylar in kayit.getirilenler.items():
        _yaz(f"- {symbol_id}", ", ".join(a.madde.entry_id for a in adaylar) or "(aday yok)")

    print()
    _yaz("=== Yorum ===")
    if kayit.mesaj:
        _yaz("Mesaj", kayit.mesaj)
    if kayit.yorum is None:
        _yaz("(yorum yok)")
    else:
        if kayit.yorum.guvenlik_notu:
            _yaz(kayit.yorum.guvenlik_notu)
        for bolum in kayit.yorum.bolumler:
            _yaz(bolum.metin)
            for atif in bolum.atiflar:
                _yaz(f"  [{atif.entry_id}] {atif.baslik}", atif.alinti)
        print()
        _yaz("Bulunamayanlar", ", ".join(kayit.yorum.bulunamayanlar) or "(yok)")
        _yaz("Uyarı", kayit.yorum.uyari)

    atif_sayisi = sum(len(bolum.atiflar) for bolum in kayit.yorum.bolumler) if kayit.yorum else 0
    if kayit.yorum is None:
        print("HATA: yorum üretilmedi.", file=sys.stderr)
        return 1
    if atif_sayisi == 0:
        print("HATA: yorumda doğrulanmış atıf yok.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
