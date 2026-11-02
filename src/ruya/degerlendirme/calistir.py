"""Test setini çalıştırır, data/raporlar/ altına rapor yazar (docs/06, bölüm 3). Takvim: Hafta 5.

Rapor: ``raporlar/<tarih>_<etiket>.md``: ölçüt tablosu, başarısız örnekler, toplam
maliyet ve elle doldurulacak sadakat kontrol listesi. Özet satır docs/olcumler.md'ye
elle eklenip commit edilir.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from ruya.degerlendirme import metrikler
from ruya.dosya import jsonl_oku
from ruya.hatalar import RuyaHatasi
from ruya.pipeline import run
from ruya.pipeline.run import Bagimliliklar
from ruya.schemas import RuyaGirdisi, SorguKaydi, TestOrnegi

# (ölçüt adı, yüzde olarak mı gösterilsin)
OLCUTLER: tuple[tuple[str, bool], ...] = (
    ("Sembol recall", True),
    ("Sembol precision", True),
    ("Eşleme doğruluğu", True),
    ("Recall@5", True),
    ("Kaynak çeşitliliği", False),
    ("Atıf kapsamı", True),
)

SADAKAT_LISTESI: tuple[str, ...] = (
    "Her yorum cümlesi dayandığı maddenin söylediğiyle uyuşuyor mu?",
    "Kaynağın söylemediği bir şey eklenmiş mi?",
    "Uyarı metni her yanıtın altında mı?",
    "Kaynaklarda olmayan sembol için uydurma yapılmış mı?",
)


def _ortalama(degerler: list[float | None]) -> float | None:
    gecerli = [deger for deger in degerler if deger is not None]
    if not gecerli:
        return None
    return sum(gecerli) / len(gecerli)


def _bicimle(deger: float | None, yuzde: bool) -> str:
    if deger is None:
        return "—"
    if yuzde:
        return f"%{deger * 100:.0f}"
    return f"{deger:.1f}".replace(".", ",")


def _ornek_olcumleri(kayit: SorguKaydi, ornek: TestOrnegi) -> dict[str, float | None]:
    return {
        "Sembol recall": metrikler.sembol_recall(kayit, ornek),
        "Sembol precision": metrikler.sembol_precision(kayit, ornek),
        "Eşleme doğruluğu": metrikler.esleme_dogrulugu(kayit, ornek),
        "Recall@5": metrikler.recall_at_k(kayit, ornek),
        "Kaynak çeşitliliği": metrikler.kaynak_cesitliligi(kayit),
        "Atıf kapsamı": metrikler.atif_kapsami(kayit),
    }


def _rapor_metni(
    etiket: str,
    tarih: dt.date,
    ornekler: list[TestOrnegi],
    kayitlar: list[tuple[TestOrnegi, SorguKaydi]],
    hatalar: list[tuple[str, str]],
) -> str:
    satirlar = [
        f"# Değerlendirme raporu · {etiket} · {tarih.isoformat()}",
        "",
        f"- Örnek sayısı: {len(ornekler)}",
        f"- Başarılı: {len(kayitlar)}",
        f"- Başarısız: {len(hatalar)}",
        "",
        "## Ölçüt tablosu",
        "",
        "| Ölçüt | Değer |",
        "|---|---|",
    ]

    olcumler = [_ornek_olcumleri(kayit, ornek) for ornek, kayit in kayitlar]
    for ad, yuzde in OLCUTLER:
        deger = _ortalama([olcum[ad] for olcum in olcumler])
        satirlar.append(f"| {ad} | {_bicimle(deger, yuzde)} |")

    olumsuzlama = sum(metrikler.olumsuzlama_hatalari(kayit, ornek) for ornek, kayit in kayitlar)
    yasak = sum(
        len(metrikler.yasak_ifadeler(kayit.yorum.metin))
        for _, kayit in kayitlar
        if kayit.yorum is not None
    )
    satirlar.append(f"| Olumsuzlama hataları | {olumsuzlama} |")
    satirlar.append(f"| Yasak ifade | {yasak} |")

    toplam_token = sum(
        (olcum.kullanim.girdi_token + olcum.kullanim.cikti_token)
        for _, kayit in kayitlar
        for olcum in kayit.olcumler
        if olcum.kullanim is not None
    )
    toplam_sure = sum(kayit.toplam_sure_sn for _, kayit in kayitlar)
    toplam_maliyet = sum(kayit.toplam_maliyet_usd for _, kayit in kayitlar)
    sayi = len(kayitlar) or 1

    satirlar += [
        "",
        "## Toplamlar",
        "",
        f"- Toplam token: {toplam_token}",
        f"- Rüya başına ortalama token: {toplam_token / sayi:.0f}",
        f"- Toplam süre: {f'{toplam_sure:.1f}'.replace('.', ',')} saniye",
        f"- Rüya başına ortalama süre: {f'{toplam_sure / sayi:.1f}'.replace('.', ',')} saniye",
        f"- Toplam maliyet: {f'{toplam_maliyet:.2f}'.replace('.', ',')} $",
        f"- Rüya başına ortalama maliyet: {f'{toplam_maliyet / sayi:.2f}'.replace('.', ',')} $",
        "",
        "## Başarısız örnekler",
        "",
    ]
    if hatalar:
        satirlar += [f"- {ornek_id}: {mesaj}" for ornek_id, mesaj in hatalar]
    else:
        satirlar.append("- Yok.")

    satirlar += [
        "",
        "## Sadakat kontrol listesi (elle doldurulur)",
        "",
    ]
    satirlar += [f"- [ ] {madde}" for madde in SADAKAT_LISTESI]
    satirlar.append("")
    return "\n".join(satirlar)


def degerlendir(veri_seti: Path, etiket: str, bag: Bagimliliklar) -> Path:
    """Raporun data/raporlar/ altındaki yolunu döndürür.

    EVREN 1 Aralık 2026'ya kadar ücretsizdir; her rüya dakikalar sürer."""
    ornekler = list(jsonl_oku(veri_seti, TestOrnegi))
    kayitlar: list[tuple[TestOrnegi, SorguKaydi]] = []
    hatalar: list[tuple[str, str]] = []

    for sira, ornek in enumerate(ornekler, start=1):
        print(f"[{sira}/{len(ornekler)}] {ornek.id}")
        girdi = RuyaGirdisi(metin=ornek.metin, baglam=ornek.baglam)
        try:
            kayitlar.append((ornek, run.yorumla(girdi, bag)))
        except RuyaHatasi as hata:
            hatalar.append((ornek.id, f"{type(hata).__name__}: {hata}"))

    tarih = dt.date.today()
    rapor = bag.ayar.rapor_klasoru / f"{tarih.isoformat()}_{etiket}.md"
    rapor.parent.mkdir(parents=True, exist_ok=True)
    rapor.write_text(_rapor_metni(etiket, tarih, ornekler, kayitlar, hatalar), encoding="utf-8")
    return rapor
