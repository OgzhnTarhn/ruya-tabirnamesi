"""Sunum katmanının saf yardımcıları (docs/16).

Arayüz metinleri ve HTML parçaları burada tek yerde durur; Gradio içe aktarılmaz, böylece
sunucu açmadan test edilebilir. Bütün dinamik metinler ``html.escape`` ile kaçırılır.
"""

from __future__ import annotations

import html
import re
from typing import Any

from ruya.etik import SEMBOL_YOK_MESAJI
from ruya.schemas import SorguKaydi

# --- Metin sabitleri (docs/16, bölüm 3) -------------------------------------

BASLIK = "Rüya Tabirnamesi"

ALT_BASLIK = "Rüyanızdaki sembolleri klasik tabirnamelerde arar, kaynak göstererek yorumlar."

NASIL_CALISIR = (
    "1. Rüyanızdaki semboller bulunur; olumsuz geçenler ayıklanır.\n"
    "2. Semboller İbn Sîrîn'e atfedilen eser, Nablusi, Miller ve Freud maddeleri arasında "
    "aranır.\n"
    "3. Yorum yalnız bulunan maddelere dayanarak yazılır ve her cümlenin kaynağı gösterilir; "
    "bir sembol için uygun madde yoksa uydurulmaz."
)

RUYA_IPUCU = (
    "Rüyanızı kendi cümlelerinizle, gördüğünüz sırayla anlatın. "
    '"Görmedim", "yoktu" gibi olumsuzlar da anlaşılır.'
)

GELENEK_ACIKLAMASI = (
    "Boş bırakırsanız İslami klasik ve Batı halk kaynaklarında aranır; "
    "Freud yalnız seçilirse girer."
)

BAGLAM_ACIKLAMASI = (
    "Klasik tabirnameler bazı sembolleri kişiye göre farklı yorumlar (ör. evli ya da bekâr). "
    "Doldurmak zorunlu değil; bilgiler saklanmaz."
)

FOTO_ACIKLAMASI = (
    "Defterinizdeki rüyanın fotoğrafını yükleyin; metin okunup kutuya yazılır. "
    "Fotoğraf yalnız okuma servisine gönderilir, saklanmaz."
)

BEKLEME_NOTU = "Genellikle 2–4 dakika sürer; bölümler hazır oldukça görünür."

BULUNAMAYAN_ACIKLAMASI = (
    "Bu semboller için kaynaklarda yeterince yakın bir madde bulunamadı; "
    "uydurmamak için yorumlanmadı."
)

ORNEK_RUYALAR: list[str] = [
    "Rüyamda siyah bir yılan gördüm, beni kovaladı ama ısıramadı.",
    "Rüyamda berrak bir denizde yüzüyordum, kıyıda annem bekliyordu.",
    "Rüyamda bahçede elma topluyordum, ağaçtan bir kuş uçtu.",
]

# --- Seçenek listeleri: (etiket, değer) -------------------------------------

CINSIYET_SECENEKLERI: list[tuple[str, str]] = [
    ("Kadın", "kadin"),
    ("Erkek", "erkek"),
]

MEDENI_HAL_SECENEKLERI: list[tuple[str, str]] = [
    ("Evli", "evli"),
    ("Bekâr", "bekar"),
]

MEVSIM_SECENEKLERI: list[tuple[str, str]] = [
    ("İlkbahar", "ilkbahar"),
    ("Yaz", "yaz"),
    ("Sonbahar", "sonbahar"),
    ("Kış", "kis"),
]

GURBET_SECENEKLERI: list[tuple[str, str]] = [
    ("Evet", "evet"),
    ("Hayır", "hayır"),
]

GELENEKLER: list[tuple[str, str]] = [
    ("İslami klasik (İbn Sîrîn, Nablusi)", "islami_klasik"),
    ("Batı halk (Miller)", "bati_halk"),
    ("Psikanalitik (Freud)", "psikanalitik"),
]

# Bölüm başlığı sayılan önekin en fazla uzunluğu; daha uzunu gövde sayılır.
BASLIK_EN_FAZLA = 60


# --- Saf yardımcılar --------------------------------------------------------

# Model eser adlarını *Muntahab* diye yazıyor; kaçırmadan sonra italiğe çevrilir.
_ITALIK = re.compile(r"\*([^*\n<>]+)\*")


def _metin(deger: str) -> str:
    """Model metnini kaçırır; yalnız ``*…*`` kalıbını ``<em>`` yapar."""
    return _ITALIK.sub(r"<em>\1</em>", html.escape(deger, quote=False))


def bolum_basligi(metin: str) -> tuple[str | None, str]:
    """Bölüm metnini ilk iki noktadan başlık ve gövdeye böler.

    Önek çok uzunsa ya da içinde nokta varsa (cümle sonu) bölünmez; başlık ``None`` döner.
    """
    ayrac = metin.find(":")
    if ayrac < 0:
        return None, metin
    baslik = metin[:ayrac].strip()
    govde = metin[ayrac + 1 :].strip()
    if not baslik or len(baslik) > BASLIK_EN_FAZLA or "." in baslik:
        return None, metin
    return baslik, govde


def _kaynak_html(atif: Any, numara: int, depo: Any) -> str:
    """Tek bir atfın ``<details>`` kaynağı: alıntı, çeviri, asıl metin ve künye."""
    parcalar = [
        '<details class="ruya-kaynak">',
        f"<summary>[{numara}] {html.escape(atif.baslik, quote=False)}</summary>",
    ]
    if atif.alinti:
        alinti = html.escape(atif.alinti, quote=False)
        parcalar.append(f'<blockquote class="ruya-alinti">{alinti}</blockquote>')

    madde = None
    if depo is not None:
        try:
            madde = depo.madde(atif.entry_id)
        except (KeyError, TypeError):
            madde = None

    if madde is not None:
        if madde.metin_tr:
            ceviri = html.escape(madde.metin_tr, quote=False)
            parcalar.append(f'<p class="ruya-ceviri">Çeviri: {ceviri}</p>')
        else:
            parcalar.append('<p class="ruya-ceviri">Çeviri henüz yok.</p>')
        parcalar.append(
            f'<p class="ruya-asli" lang="{html.escape(madde.dil)}" dir="auto">'
            f"Asıl metin: {html.escape(madde.metin_asli, quote=False)}</p>"
        )
        if madde.atif_notu:
            atif_notu = html.escape(madde.atif_notu, quote=False)
            parcalar.append(f'<p class="ruya-not">Atıf notu: {atif_notu}</p>')
        kunye = f"{madde.yazar} · {madde.eser} · {madde.entry_id}"
        parcalar.append(f'<p class="ruya-not">{html.escape(kunye, quote=False)}</p>')

    parcalar.append("</details>")
    return "".join(parcalar)


def yorum_html(kayit: SorguKaydi, depo: Any = None) -> str:
    """Yorumun HTML'i: güvenlik notu, genel yorum, bölümler, kaynaklar, bulunamayanlar.

    Uyarı metni burada yazılmaz; sayfada bir kez alt bilgide gösterilir (docs/16, A3).
    """
    yorum = kayit.yorum
    if yorum is None:
        mesaj = kayit.mesaj or SEMBOL_YOK_MESAJI
        return f'<div class="ruya-bos">{html.escape(mesaj, quote=False)}</div>'

    parcalar = ['<div class="ruya-sonuc">']

    if yorum.guvenlik_notu:
        guvenlik = html.escape(yorum.guvenlik_notu, quote=False)
        parcalar.append(f'<div class="ruya-guvenlik">{guvenlik}</div>')

    if yorum.genel_yorum:
        parcalar.append(
            '<div class="ruya-genel">'
            '<span class="ruya-etiket">Genel yorum</span>'
            f"<p>{_metin(yorum.genel_yorum)}</p>"
            "</div>"
        )

    numara = 0
    for bolum in yorum.bolumler:
        baslik, govde = bolum_basligi(bolum.metin)
        parcalar.append('<section class="ruya-bolum">')
        if baslik is not None:
            parcalar.append(f"<h3>{html.escape(baslik, quote=False)}</h3>")
        parcalar.append(f"<p>{_metin(govde)}</p>")
        if bolum.atiflar:
            parcalar.append('<div class="ruya-kaynaklar">')
            for atif in bolum.atiflar:
                numara += 1
                parcalar.append(_kaynak_html(atif, numara, depo))
            parcalar.append("</div>")
        parcalar.append("</section>")

    if yorum.bulunamayanlar:
        bulunamayanlar = ", ".join(yorum.bulunamayanlar)
        parcalar.append(
            '<div class="ruya-bulunamayan">'
            f"<p>{html.escape(BULUNAMAYAN_ACIKLAMASI, quote=False)}</p>"
            f"<p>{html.escape(bulunamayanlar, quote=False)}</p>"
            "</div>"
        )

    parcalar.append("</div>")
    return "".join(parcalar)


def semboller_html(kayit: SorguKaydi) -> str:
    """Bulunan sembolleri rozet olarak yazar; olumsuzlar ayrı biçimde işaretlenir."""
    rozetler: list[str] = []
    for eslesme in kayit.eslesmeler:
        yalin = html.escape(eslesme.sembol.yalin, quote=False)
        rozetler.append(f'<span class="ruya-rozet">{yalin}</span>')

    if kayit.cikarim is not None:
        for sembol in kayit.cikarim.semboller:
            if not sembol.olumsuz:
                continue
            rozetler.append(
                '<span class="ruya-rozet ruya-rozet--olumsuz" '
                'title="Rüyada olumsuz geçtiği için yorumlanmadı">'
                f"{html.escape(sembol.yalin, quote=False)}</span>"
            )

    if not rozetler and not kayit.atlanan_semboller:
        return ""

    parcalar = ['<div class="ruya-rozetler">', "".join(rozetler), "</div>"]
    if kayit.atlanan_semboller:
        atlananlar = ", ".join(kayit.atlanan_semboller)
        parcalar.append(
            '<p class="ruya-not">'
            f"Çok sembol olduğu için yorumlanmayanlar: {html.escape(atlananlar, quote=False)}</p>"
        )
    return "".join(parcalar)


# Aşama → üç adımın durumu (Semboller, Kaynaklar, Yorum).
_ADIM_DURUMLARI: dict[str, tuple[str, str, str]] = {
    "baslangic": ("suruyor", "bekliyor", "bekliyor"),
    "esleme": ("tamam", "suruyor", "bekliyor"),
    "getirme": ("tamam", "tamam", "suruyor"),
    "sentez": ("tamam", "tamam", "suruyor"),
    "bitti": ("tamam", "tamam", "tamam"),
}

_ADIM_ETIKETLERI = ("Semboller", "Kaynaklar", "Yorum")


def ilerleme_html(asama: str) -> str:
    """Üç adımlı ilerleme şeridi; bilinmeyen aşama başlangıç sayılır."""
    durumlar = _ADIM_DURUMLARI.get(asama, _ADIM_DURUMLARI["baslangic"])
    adimlar = "".join(
        f'<li class="ruya-adim ruya-adim--{durum}">{html.escape(etiket, quote=False)}</li>'
        for etiket, durum in zip(_ADIM_ETIKETLERI, durumlar, strict=True)
    )
    parcalar = [f'<ol class="ruya-ilerleme">{adimlar}</ol>']
    if asama != "bitti":
        parcalar.append(f'<p class="ruya-not">{html.escape(BEKLEME_NOTU, quote=False)}</p>')
    return "".join(parcalar)


def akis_html(asama: str, kayit: SorguKaydi, depo: Any = None) -> str:
    """İlerleme, semboller ve (varsa) yorum; akışta da son sonuçta da kullanılır.

    Yorum henüz yokken yorum kısmı yazılmaz: aksi hâlde akış sırasında "sembol bulunamadı"
    mesajı görünürdü.
    """
    parca = ilerleme_html(asama) + semboller_html(kayit)
    if kayit.yorum is not None or asama == "bitti":
        parca += yorum_html(kayit, depo)
    return parca


def hata_html(mesaj: str) -> str:
    """Kullanıcıya gösterilecek hata mesajını kaçırılmış bir kutuda yazar."""
    return f'<div class="ruya-hata">{html.escape(mesaj, quote=False)}</div>'
