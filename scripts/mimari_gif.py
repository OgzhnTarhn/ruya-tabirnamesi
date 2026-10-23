"""Mimari animasyonunu üretir: docs/gorseller/mimari.gif (+ son karenin PNG kopyası).

Mimari değişince yeniden çalıştır:

    uvx --with pillow python scripts/mimari_gif.py docs/gorseller/mimari.gif

Pillow projenin bağımlılığı değildir; yalnızca bu betik için geçici kurulur.
Yazı tipleri Windows'un Segoe UI ailesidir.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 680
OLCEK = 2  # kenar yumuşatma için büyük çiz, sonra küçült
FONT = "C:/Windows/Fonts/segoeui.ttf"
FONT_B = "C:/Windows/Fonts/segoeuib.ttf"
FONT_M = "C:/Windows/Fonts/consola.ttf"

ZEMIN = (245, 247, 249)
MUREKKEP = (28, 38, 50)
SOLUK = (120, 132, 145)
CIZGI = (205, 212, 220)
KUTU = (255, 255, 255)
CEVRIMDISI = (176, 96, 20)  # amber
CEVRIMICI = (13, 118, 110)  # teal
GIT = (88, 80, 200)


def f(boyut, kalin=False, mono=False):
    yol = FONT_M if mono else (FONT_B if kalin else FONT)
    return ImageFont.truetype(yol, boyut * OLCEK)


# Kutular: ad -> (x, y, w, h, başlık, alt satır, renk)
KUTULAR = {
    "raw": (40, 120, 165, 92, "data/raw", "Nablusi · Miller · …", CEVRIMDISI),
    "ingest": (250, 120, 165, 92, "ingest/", "kurallarla ayrıştırma", CEVRIMDISI),
    "enrich": (460, 120, 185, 92, "enrich/", "sembol · çeviri · koşul", CEVRIMDISI),
    "entries": (690, 120, 185, 92, "entries.jsonl", "zenginleştirilmiş madde", CEVRIMDISI),
    "index": (920, 120, 240, 92, "index/", "sözlük tabloları · Chroma", CEVRIMDISI),
    "sozluk": (920, 248, 240, 64, "sozluk/symbols.json", "elle onay · git", GIT),
    "ruya": (40, 400, 150, 92, "Rüya metni", "Gradio · Colab", CEVRIMICI),
    "cikarim": (225, 400, 175, 92, "1 · Çıkarım", "Claude · JSON şema", CEVRIMICI),
    "esleme": (435, 400, 175, 92, "2 · Eşleme", "sözlük · zeyrek · vektör", CEVRIMICI),
    "getirme": (645, 400, 175, 92, "3 · Getirme", "symbol_id · kaynak başı N", CEVRIMICI),
    "sentez": (855, 400, 175, 92, "4 · Sentez", "Claude · atıflar", CEVRIMICI),
    "yorum": (1060, 400, 110, 92, "Yorum", "+ uyarı", CEVRIMICI),
}

# Oklar: (kaynak, hedef, kesikli mi)
OKLAR = [
    ("raw", "ingest", False),
    ("ingest", "enrich", False),
    ("enrich", "entries", False),
    ("entries", "index", False),
    ("sozluk", "index", False),
    ("ruya", "cikarim", False),
    ("cikarim", "esleme", False),
    ("esleme", "getirme", False),
    ("getirme", "sentez", False),
    ("sentez", "yorum", False),
    ("index", "esleme", True),
    ("entries", "getirme", True),
]

# Adımlar: (yanan kutu, gelen ok, açıklama)
ADIMLAR = [
    ("raw", None, "Ham kaynaklar Colab'den doğrudan Drive'a iner; SHA256 kaydedilir."),
    (
        "ingest",
        ("raw", "ingest"),
        "Ayrıştırıcılar her paragrafı lisans ve konumuyla bir Madde kaydına çevirir.",
    ),
    (
        "enrich",
        ("ingest", "enrich"),
        "LLM, Batch API ile alt paragraflara sembol atar ve Türkçeye çevirir.",
    ),
    (
        "entries",
        ("enrich", "entries"),
        "Sonuç: data/processed/entries.jsonl. Aslı ve çevirisi yan yana.",
    ),
    ("sozluk", None, "Kanonik semboller elle onaylanır ve git'te sürümlenir."),
    (
        "index",
        ("entries", "index"),
        "Oturum başında sözlük tabloları bellekte kurulur; Chroma Aşama 2'de.",
    ),
    ("ruya", None, "Kullanıcı rüyasını yazar; isterse bağlam ve gelenek seçer."),
    (
        "cikarim",
        ("ruya", "cikarim"),
        "Claude sembolleri yalın hâlde, nitelik ve duygusuyla çıkarır.",
    ),
    (
        "esleme",
        ("cikarim", "esleme"),
        "Önce sözlük, sonra zeyrek kökü, en son vektör yedeği: symbol_id.",
    ),
    (
        "getirme",
        ("esleme", "getirme"),
        "Her kaynaktan en fazla N madde; nitelik ve bağlama göre sıralanır.",
    ),
    (
        "sentez",
        ("getirme", "sentez"),
        "Claude her cümleyi bir kaynağa bağlar; çelişkiler yan yana kalır.",
    ),
    (
        "yorum",
        ("sentez", "yorum"),
        "Kaynaklı yorum + uyarı. Her adımın süresi ve maliyeti SorguKaydi'nda.",
    ),
]


def merkez(ad):
    x, y, w, h, *_ = KUTULAR[ad]
    return x + w / 2, y + h / 2


def ok_uclari(a, b):
    ax, ay, aw, ah, *_ = KUTULAR[a]
    bx, by, bw, bh, *_ = KUTULAR[b]
    if abs(ay - by) < 5:  # aynı satır: yatay
        return (ax + aw, ay + ah / 2), (bx, by + bh / 2)
    if a == "sozluk":  # yukarı
        return (ax + aw / 2, ay), (bx + bw / 2, by + bh)
    if a == "index":  # sözlük kutusunun solundan iner
        return (ax + 30, ay + ah), (bx + bw / 2, by)
    # yukarıdan aşağı çapraz
    return (ax + aw / 2, ay + ah), (bx + bw / 2, by)


def s(*v):
    return [d * OLCEK for d in v]


def cizgi(d, p, q, renk, kalinlik, kesikli=False):
    (x1, y1), (x2, y2) = p, q
    if not kesikli:
        d.line(s(x1, y1, x2, y2), fill=renk, width=kalinlik * OLCEK)
        return
    n = 22
    for i in range(0, n, 2):
        t1, t2 = i / n, (i + 1) / n
        d.line(
            s(x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1, x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2),
            fill=renk,
            width=kalinlik * OLCEK,
        )


def ok_basi(d, p, q, renk):
    import math

    (x1, y1), (x2, y2) = p, q
    aci = math.atan2(y2 - y1, x2 - x1)
    boy = 10
    noktalar = [
        (x2, y2),
        (x2 - boy * math.cos(aci - 0.45), y2 - boy * math.sin(aci - 0.45)),
        (x2 - boy * math.cos(aci + 0.45), y2 - boy * math.sin(aci + 0.45)),
    ]
    d.polygon([c * OLCEK for n in noktalar for c in n], fill=renk)


def kare(yanan: set, aktif: str | None, ok: tuple | None, t: float, aciklama: str, adim_no: int):
    img = Image.new("RGB", (W * OLCEK, H * OLCEK), ZEMIN)
    d = ImageDraw.Draw(img)

    # Başlık
    d.text(s(40, 26), "Rüya Tabirnamesi · Mimari", font=f(26, kalin=True), fill=MUREKKEP)
    d.text(
        s(40, 62),
        "Önce sözlük, sonra vektör · her adım ayrı ve gözlemlenebilir",
        font=f(15),
        fill=SOLUK,
    )

    # Bölge etiketleri
    d.text(
        s(40, 96), "ÇEVRİMDIŞI · VERİ HAZIRLAMA (BİR KEZ)", font=f(12, kalin=True), fill=CEVRIMDISI
    )
    d.text(s(40, 376), "ÇEVRİMİÇİ · SORGU (HER RÜYA)", font=f(12, kalin=True), fill=CEVRIMICI)
    d.line(s(40, 345, 1160, 345), fill=CIZGI, width=OLCEK)

    # Oklar
    for a, b, kesikli in OKLAR:
        p, q = ok_uclari(a, b)
        canli = a in yanan and b in yanan
        renk = KUTULAR[b][6] if canli else CIZGI
        cizgi(d, p, q, renk, 2, kesikli)
        ok_basi(d, p, q, renk)

    # Kutular
    for ad, (x, y, w, h, baslik, alt, renk) in KUTULAR.items():
        yaniyor = ad in yanan
        kenar = renk if yaniyor else CIZGI
        dolgu = KUTU
        if ad == aktif:
            dolgu = tuple(int(255 - (255 - c) * 0.10) for c in renk)
        d.rounded_rectangle(
            s(x, y, x + w, y + h),
            radius=10 * OLCEK,
            fill=dolgu,
            outline=kenar,
            width=(3 if ad == aktif else 2) * OLCEK,
        )
        yazi = MUREKKEP if yaniyor else SOLUK
        d.text(
            s(x + 14, y + (16 if h > 70 else 10)),
            baslik,
            font=f(17, kalin=True, mono=False),
            fill=yazi,
        )
        d.text(s(x + 14, y + (48 if h > 70 else 36)), alt, font=f(13), fill=SOLUK)

    # Ok üzerinde hareket eden nokta
    if ok and t < 1:
        p, q = ok_uclari(*ok)
        px, py = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        renk = KUTULAR[ok[1]][6]
        d.ellipse(s(px - 7, py - 7, px + 7, py + 7), fill=renk)

    # Açıklama şeridi
    d.rounded_rectangle(
        s(40, 540, 1160, 600), radius=10 * OLCEK, fill=KUTU, outline=CIZGI, width=OLCEK
    )
    if adim_no:
        d.text(s(60, 557), f"{adim_no:>2}/{len(ADIMLAR)}", font=f(17, mono=True), fill=SOLUK)
    d.text(s(130 if adim_no else 60, 556), aciklama, font=f(18), fill=MUREKKEP)

    # Alt bilgi: üç yer
    alt = "Kod: bilgisayar (VS Code + git)   ·   Çalıştırma: Google Colab   ·   Veri: Google Drive"
    d.text(s(40, 625), alt, font=f(14), fill=SOLUK)

    return img.resize((W, H), Image.LANCZOS)


def main(cikti: Path):
    kareler, sureler = [], []
    yanan: set = set()
    kareler.append(
        kare(
            yanan,
            None,
            None,
            1,
            "Veri bir kez hazırlanır; her rüya hafif bir sorgu hattından geçer.",
            0,
        )
    )
    sureler.append(2200)
    for no, (ad, ok, aciklama) in enumerate(ADIMLAR, start=1):
        if ok:
            for i in range(6):
                kareler.append(kare(yanan, None, ok, i / 6, aciklama, no))
                sureler.append(70)
        yanan.add(ad)
        kareler.append(kare(yanan, ad, None, 1, aciklama, no))
        sureler.append(2000)
    kareler.append(
        kare(
            yanan, None, None, 1, "Kesikli oklar: sorgu hattı yalnızca hazırlanmış veriyi okur.", 0
        )
    )
    sureler.append(3500)

    paletli = [k.quantize(colors=64, method=Image.MEDIANCUT) for k in kareler]
    paletli[0].save(
        cikti, save_all=True, append_images=paletli[1:], duration=sureler, loop=0, optimize=True
    )
    kareler[-1].save(cikti.with_suffix(".png"))
    print(cikti, cikti.stat().st_size // 1024, "KB,", len(kareler), "kare")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
