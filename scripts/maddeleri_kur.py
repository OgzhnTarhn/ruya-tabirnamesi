"""Ham kaynakları ayrıştırıp çevirilerle birleştirerek maddeleri kurar.

Her kaynak için sırayla:

1. ``Ayarlar().ham_klasoru/<kaynak>.txt`` ayrıştırılır (``ruya.ingest.<kaynak>.ayristir``).
2. Maddeler ``Ayarlar().ara_klasoru/<kaynak>.jsonl`` dosyasına yazılır.
3. ``Ayarlar().ara_klasoru/ceviri/<kaynak>`` altındaki çeviri parçaları okunur
   (``ceviri_oku``) ve maddelere işlenir (``ceviriyi_uygula``).
4. Sözlük yüklenir (``sozlugu_yukle``), varyant tablosu kurulur (``varyant_tablosu``) ve
   bütün maddelere ``symbol_ids`` atanır (``sembol_ata``).
5. Koşullu yorumlar kural tabanlı çıkarılır (``maddelere_uygula``, docs/13).
6. Bütün maddeler ``Ayarlar().maddeler_dosyasi`` dosyasına yazılır.

Çeviri kimlikleri maddelerle uyuşmazsa ``ceviriyi_uygula`` ``ValueError`` yükseltir ve
betik durur. Bilgisayarda çalışır, veri gerektirir::

    uv run python scripts/maddeleri_kur.py
"""

from __future__ import annotations

from ruya.config import CEVIRI_MODEL_ETIKETI, CEVIRI_TARIHI, Ayarlar
from ruya.dosya import jsonl_yaz
from ruya.enrich.ceviri_birlestir import ceviri_oku, ceviriyi_uygula
from ruya.enrich.kosul_kurallari import maddelere_uygula
from ruya.enrich.sembol_ata import sembol_ata
from ruya.index.build_symbols import sozlugu_yukle, sozluk_maddeler_tutarliligi, varyant_tablosu
from ruya.ingest import freud, ibn_sirin, miller, nablusi
from ruya.schemas import Madde

KAYNAKLAR = (nablusi, miller, ibn_sirin, freud)


def main() -> None:
    ayarlar = Ayarlar()
    butun_maddeler: list[Madde] = []
    sayilar: dict[str, int] = {}

    for modul in KAYNAKLAR:
        kaynak = modul.__name__.rsplit(".", 1)[-1]
        ham_dosya = ayarlar.ham_klasoru / f"{kaynak}.txt"
        maddeler = list(modul.ayristir(ham_dosya))
        jsonl_yaz(maddeler, ayarlar.ara_klasoru / f"{kaynak}.jsonl")

        ceviriler = ceviri_oku(ayarlar.ara_klasoru / "ceviri" / kaynak)
        maddeler = ceviriyi_uygula(
            maddeler,
            ceviriler,
            model=CEVIRI_MODEL_ETIKETI,
            tarih=CEVIRI_TARIHI,
        )
        butun_maddeler.extend(maddeler)
        sayilar[kaynak] = len(maddeler)

    sozluk = sozlugu_yukle()
    butun_maddeler = sembol_ata(butun_maddeler, varyant_tablosu(sozluk))
    butun_maddeler = maddelere_uygula(butun_maddeler)

    jsonl_yaz(butun_maddeler, ayarlar.maddeler_dosyasi)

    for kaynak, sayi in sayilar.items():
        print(f"{kaynak}: {sayi} madde")
    print(f"toplam: {len(butun_maddeler)} madde, dosya: {ayarlar.maddeler_dosyasi}")

    sembollu = sum(1 for m in butun_maddeler if m.symbol_ids)
    print(f"sembol atanan: {sembollu} madde")

    kosullu = sum(1 for m in butun_maddeler if m.kosullar)
    print(f"koşul çıkarılan: {kosullu} madde")

    sorunlar = sozluk_maddeler_tutarliligi(sozluk, butun_maddeler)
    if sorunlar:
        print(f"sözlük tutarsızlıkları ({len(sorunlar)}):")
        for sorun in sorunlar:
            print(f"  - {sorun}")
    else:
        print("sözlük tutarlı")


if __name__ == "__main__":
    main()
