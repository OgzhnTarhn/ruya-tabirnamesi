"""İlerleme raporunun verisini repodaki belgelerden ve testlerden üretir.

Kaynaklar (tek doğru kaynak her zaman repodaki belgedir):

- Görevler ve kilometre taşları: docs/08-yol-haritasi-takvim.md (``- [x]`` = tamam,
  kilometre taşı satırında ✅ = tamam)
- Benchmark hedefleri ve ölçümler: docs/olcumler.md
- Kod sağlığı: pytest sonucu, src/ruya içindeki hazır ve iskelet işlevler, commit sayısı

Çıktı: docs/rapor/veri/*.json. Kod sağlığı geçmişi birikir (gün başına bir satır).
Bilgisayarda çalışır, veri gerektirmez::

    uv run python scripts/rapor_verisi.py
"""

from __future__ import annotations

import ast
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
CIKTI = KOK / "docs" / "rapor" / "veri"
YOL_HARITASI = KOK / "docs" / "08-yol-haritasi-takvim.md"
OLCUMLER = KOK / "docs" / "olcumler.md"
PAKET = KOK / "src" / "ruya"

HAFTA_0 = (dt.date(2026, 10, 21), dt.date(2026, 10, 25))
HAFTA_1_BASI = dt.date(2026, 10, 26)
AYLAR = {
    "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
    "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12,
}  # fmt: skip

# olcumler.md sütunu → ölçütün katmanı (docs/06, bölüm 2)
KATMANLAR = {
    "Sembol recall": "Çıkarım",
    "Sembol precision": "Çıkarım",
    "Olumsuzlama hatası": "Çıkarım",
    "Eşleme doğruluğu": "Eşleme",
    "Recall@5": "Getirme",
    "Kaynak çeşitliliği": "Getirme",
    "Atıf kapsamı": "Sentez",
    "Sadakat ihlali (elle)": "Sentez",
    '"Bulunamadı"': "Sentez",
    "Etik ihlal": "Sentez",
    "Medyan süre (sn)": "İşletim",
    "Ort. maliyet ($)": "İşletim",
}
KIMLIK_SUTUNLARI = ["Tarih", "Etiket", "Commit", "Test seti", "Talimatlar"]


def sade(metin: str) -> str:
    """Markdown işaretlerini atar: bağlantılar, `kod`, **kalın**."""
    metin = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", metin)
    return re.sub(r"[`*]", "", metin).strip()


def hafta_tarihleri(hafta: int) -> tuple[dt.date, dt.date]:
    if hafta == 0:
        return HAFTA_0
    basi = HAFTA_1_BASI + dt.timedelta(days=7 * (hafta - 1))
    return basi, basi + dt.timedelta(days=6)


def gorevler(bugun: dt.date) -> list[dict]:
    satirlar, hafta, baslik, asama, sira = [], None, "", "", 0
    for satir in YOL_HARITASI.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^### Hafta (\d+) · [^·]+ · (.+)$", satir):
            hafta, sira = int(m.group(1)), 0
            baslik = sade(re.sub(r"\s*[✅→].*$", "", m.group(2)))
            if a := re.search(r"Aşama (\d)", m.group(2)):
                asama = f"Aşama {a.group(1)}"
            else:
                asama = "Tampon" if "Tampon" in m.group(2) else "Hazırlık"
            continue
        if satir.startswith("## "):
            hafta = None
        m = re.match(r"^- \[( |x)\] (.+)$", satir)
        if hafta is None or not m:
            continue
        sira += 1
        basi, sonu = hafta_tarihleri(hafta)
        if m.group(1) == "x":
            durum = "tamam"
        elif sonu < bugun:
            durum = "gecikti"
        elif basi <= bugun:
            durum = "suruyor"
        else:
            durum = "bekliyor"
        satirlar.append(
            {
                "id": f"h{hafta:02d}-{sira:02d}",
                "hafta": hafta,
                "baslangic": basi.isoformat(),
                "bitis": sonu.isoformat(),
                "asama": asama,
                "baslik": baslik,
                "gorev": sade(m.group(2)),
                "durum": durum,
            }
        )
    return satirlar


def kilometre_taslari() -> list[dict]:
    satirlar = []
    for satir in YOL_HARITASI.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| \*\*(\d+) (\S+) (\d{4})\*\* \| (.+?) \| (.+) \|$", satir)
        if not m:
            continue
        gun, ay, yil, tas, olcut = m.groups()
        satirlar.append(
            {
                "kod": sade(tas).split(" · ")[0],
                "ad": sade(tas).replace("✅", "").strip(),
                "tarih": dt.date(int(yil), AYLAR[ay], int(gun)).isoformat(),
                "olcut": sade(olcut),
                "durum": "tamam" if "✅" in tas else "bekliyor",
            }
        )
    return satirlar


def _tablo(yol: Path) -> tuple[list[str], list[list[str]]]:
    satirlar = [s for s in yol.read_text(encoding="utf-8").splitlines() if s.startswith("|")]
    hucreler = [[h.strip() for h in s.strip("|").split("|")] for s in satirlar]
    return hucreler[0], [h for h in hucreler[2:] if any(h)]


def _sayi(metin: str) -> float | None:
    metin = metin.replace("≥", "").replace("≤", "").replace(" ", "")
    if not metin or not re.search(r"\d", metin):
        return None
    oran = metin.startswith("%")
    deger = float(metin.lstrip("%").replace(",", "."))
    return deger / 100 if oran else deger


def olcumler() -> tuple[list[dict], list[dict]]:
    """(hedefler, ölçümler) döndürür. Hedef satırları ilk hücresi *hedef …* olanlardır."""
    baslik, satirlar = _tablo(OLCUMLER)
    olcutler = [b for b in baslik if b not in KIMLIK_SUTUNLARI]
    hedef = {
        s[0].strip("*").replace("hedef ", ""): dict(zip(baslik, s, strict=True))
        for s in satirlar
        if s[0].startswith("*")
    }
    hedefler = []
    for sira, ad in enumerate(olcutler):
        mvp, a3 = hedef["MVP"][ad], hedef["A3"][ad]
        isaret = mvp + a3
        if "≤" in isaret:
            yon = "dusuk"
        elif "≥" in isaret or _sayi(a3) == 1.0:
            yon = "yuksek"
        else:
            yon = "dusuk"  # 0 hedefli sayımlar
        hedefler.append(
            {
                "sira": sira + 1,
                "olcut": ad,
                "katman": KATMANLAR.get(ad, ""),
                "hedef_mvp": _sayi(mvp),
                "hedef_a3": _sayi(a3),
                "hedef_mvp_metin": mvp,
                "hedef_a3_metin": a3,
                "yon": yon,
                "oran": "%" in isaret,
            }
        )
    olcumler_ = []
    for s in satirlar:
        if s[0].startswith("*"):
            continue
        kayit = dict(zip(baslik, s, strict=True))
        for ad in olcutler:
            if (deger := _sayi(kayit[ad])) is not None:
                olcumler_.append(
                    {
                        "tarih": kayit["Tarih"],
                        "etiket": kayit["Etiket"],
                        "commit": kayit["Commit"],
                        "test_seti": kayit["Test seti"],
                        "talimatlar": kayit["Talimatlar"],
                        "olcut": ad,
                        "deger": deger,
                    }
                )
    return hedefler, olcumler_


def islevler() -> list[dict]:
    satirlar = []
    for yol in sorted(PAKET.rglob("*.py")):
        agac = ast.parse(yol.read_text(encoding="utf-8"))
        modul = yol.relative_to(PAKET).as_posix()
        dosya_haftasi = None
        for dugum in ast.walk(agac):
            if not isinstance(dugum, ast.FunctionDef):
                continue
            if dugum.name.startswith("_") and dugum.name != "__init__":
                continue
            kaynak = ast.get_source_segment(yol.read_text(encoding="utf-8"), dugum) or ""
            iskelet = "raise NotImplementedError" in kaynak
            hafta = None
            if m := re.search(r"Hafta (\d+)", kaynak):
                hafta = int(m.group(1))
                dosya_haftasi = dosya_haftasi or hafta
            if dugum.name == "__init__" and not iskelet:
                continue
            satirlar.append(
                {
                    "modul": modul,
                    "islev": dugum.name,
                    "birim": modul.split("/")[0].removesuffix(".py"),
                    "durum": "iskelet" if iskelet else "hazir",
                    "hafta": hafta if hafta is not None else (dosya_haftasi if iskelet else None),
                }
            )
    return satirlar


def test_sonucu() -> dict[str, int]:
    sonuc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        cwd=KOK,
        capture_output=True,
        text=True,
    )
    son = sonuc.stdout.strip().splitlines()[-1] if sonuc.stdout.strip() else ""
    sayilar = {"passed": 0, "skipped": 0, "failed": 0, "error": 0}
    for sayi, tur in re.findall(r"(\d+) (passed|skipped|failed|errors?)", son):
        sayilar["error" if tur.startswith("error") else tur] += int(sayi)
    return sayilar


def commit_sayisi() -> int:
    cikti = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"], cwd=KOK, capture_output=True, text=True
    ).stdout
    return int(cikti.strip() or 0)


def yaz(ad: str, veri: list[dict]) -> None:
    (CIKTI / f"{ad}.json").write_text(
        json.dumps(veri, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{ad}.json: {len(veri)} satır")


def main() -> None:
    bugun = dt.date.today()
    CIKTI.mkdir(parents=True, exist_ok=True)
    gorev = gorevler(bugun)
    hedefler, olcum = olcumler()
    islev = islevler()
    test = test_sonucu()

    gecmis_yolu = CIKTI / "kod_sagligi.json"
    gecmis = json.loads(gecmis_yolu.read_text(encoding="utf-8")) if gecmis_yolu.exists() else []
    gecmis = [g for g in gecmis if g["tarih"] != bugun.isoformat()]
    gecmis.append(
        {
            "tarih": bugun.isoformat(),
            "commit_sayisi": commit_sayisi(),
            "gecen_test": test["passed"],
            "atlanan_test": test["skipped"],
            "basarisiz_test": test["failed"] + test["error"],
            "hazir_islev": sum(i["durum"] == "hazir" for i in islev),
            "iskelet_islev": sum(i["durum"] == "iskelet" for i in islev),
            "tamam_gorev": sum(g["durum"] == "tamam" for g in gorev),
            "toplam_gorev": len(gorev),
        }
    )

    yaz("gorevler", gorev)
    yaz("kilometre_taslari", kilometre_taslari())
    yaz("hedefler", hedefler)
    yaz("olcumler", olcum)
    yaz("islevler", islev)
    yaz("kod_sagligi", sorted(gecmis, key=lambda g: g["tarih"]))


if __name__ == "__main__":
    main()
