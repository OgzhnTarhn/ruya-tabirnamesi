"""Gradio arayüzü (İG-40, İG-41, İG-42). Takvim: Hafta 5.

notebooks/05_arayuz.ipynb içinden açılır::

    from app.gradio_app import baslat
    baslat(varsayilan_bagimliliklar())

Güvenlik: ``launch(share=True)`` **kullanılmaz** (TK-09). Herkese açık bir link üretir ve
linki bulan herkes senin API anahtarınla sorgu çalıştırabilir.
"""

from __future__ import annotations

from typing import Any

from ruya.etik import REDDEDILDI_MESAJI, SEMBOL_YOK_MESAJI, UYARI_METNI
from ruya.hatalar import (
    ApiAnahtariYok,
    LLMHatasi,
    ModelReddetti,
    RuyaHatasi,
    SozlukHatasi,
    YanitBozuk,
    YanitKesildi,
)
from ruya.pipeline.run import Bagimliliklar, yorumla
from ruya.schemas import Baglam, RuyaGirdisi, SorguKaydi

# docs/03, bölüm 5.4: hata sınıfı → kullanıcıya gösterilen Türkçe mesaj.
HATA_MESAJLARI: dict[type[RuyaHatasi], str] = {
    ApiAnahtariYok: (
        "LLM API anahtarı tanımlı değil. EVREN_LLM_API_KEY ortam değişkenini ayarlayıp "
        "uygulamayı yeniden başlatın."
    ),
    ModelReddetti: REDDEDILDI_MESAJI,
    YanitKesildi: ("Yanıt uzunluk sınırında kesildi. Rüyayı biraz kısaltıp yeniden deneyin."),
    LLMHatasi: ("Yorum servisine ulaşılamadı. Birkaç dakika sonra yeniden deneyin."),
    YanitBozuk: ("Modelin yanıtı beklenen biçimde gelmedi. Yeniden deneyin."),
    SozlukHatasi: ("Sembol sözlüğü okunamadı. Kurulumu denetleyip yeniden deneyin."),
}

GELENEKLER: list[tuple[str, str]] = [
    ("İslami klasik", "islami_klasik"),
    ("Batı halk", "bati_halk"),
    ("Psikanalitik", "psikanalitik"),
]


# --- Saf yardımcılar (sunucu açmadan test edilir) ---------------------------


def yorum_metni(kayit: SorguKaydi) -> str:
    """Yorum sekmesinin metni: güvenlik notu başta, numaralı atıflar, uyarı sonda."""
    yorum = kayit.yorum
    if yorum is None:
        return kayit.mesaj or SEMBOL_YOK_MESAJI

    parcalar: list[str] = []
    if yorum.guvenlik_notu:
        parcalar.append(yorum.guvenlik_notu)

    numara = 0
    for bolum in yorum.bolumler:
        parcalar.append(bolum.metin)
        for atif in bolum.atiflar:
            numara += 1
            satir = f"[{numara}] {atif.baslik}"
            if atif.alinti:
                satir += f" — “{atif.alinti}”"
            parcalar.append(satir)

    if yorum.bulunamayanlar:
        parcalar.append("Kaynaklarda bulunamayanlar: " + ", ".join(yorum.bulunamayanlar))

    parcalar.append(yorum.uyari or UYARI_METNI)
    return "\n\n".join(parcalar)


def atif_ayrintilari(kayit: SorguKaydi, entry_id: str, depo: Any) -> str:
    """Bir atıf tıklanınca gösterilen ayrıntı: çeviri ve asıl metin (İG-41)."""
    if not entry_id:
        return "Ayrıntısı gösterilecek bir atıf seçilmedi."
    try:
        madde = depo.madde(entry_id)
    except (KeyError, TypeError):
        return f"{entry_id} maddesi depoda bulunamadı."

    satirlar = [f"**{madde.yazar} · {madde.eser}** ({madde.entry_id})"]
    if madde.metin_tr:
        satirlar.append(f"Çeviri: {madde.metin_tr}")
    else:
        satirlar.append("Çeviri: henüz yok.")
    satirlar.append(f"Asıl metin ({madde.dil}): {madde.metin_asli}")
    if madde.atif_notu:
        satirlar.append(f"Atıf notu: {madde.atif_notu}")
    return "\n\n".join(satirlar)


def hata_ayiklama(kayit: SorguKaydi) -> dict[str, Any]:
    """Hata ayıklama sekmesinin içeriği; hepsi SorguKaydi'ndan okunur."""
    semboller = [
        {
            "yalin": s.yalin,
            "nitelikler": s.nitelikler,
            "eylem": s.eylem,
            "duygu": s.duygu,
            "olumsuz": s.olumsuz,
        }
        for s in (kayit.cikarim.semboller if kayit.cikarim else [])
    ]
    eslesmeler = [
        {
            "sembol": e.sembol.yalin,
            "symbol_id": e.symbol_id,
            "yontem": e.yontem,
            "guven": e.guven,
        }
        for e in kayit.eslesmeler
    ]
    getirilenler = [
        {
            "symbol_id": symbol_id,
            "entry_id": aday.madde.entry_id,
            "skor": aday.skor,
            "gerekceler": aday.gerekceler,
        }
        for symbol_id, adaylar in kayit.getirilenler.items()
        for aday in adaylar
    ]
    olcumler = [
        {
            "adim": o.adim,
            "sure_sn": o.sure_sn,
            "talimat": o.talimat,
            "girdi_token": o.kullanim.girdi_token if o.kullanim else None,
            "cikti_token": o.kullanim.cikti_token if o.kullanim else None,
            "maliyet_usd": o.kullanim.maliyet_usd if o.kullanim else None,
        }
        for o in kayit.olcumler
    ]
    return {
        "semboller": semboller,
        "eslesmeler": eslesmeler,
        "getirilenler": getirilenler,
        "olcumler": olcumler,
        "atlanan_semboller": kayit.atlanan_semboller,
        "toplam_sure_sn": round(kayit.toplam_sure_sn, 3),
        "toplam_maliyet_usd": round(kayit.toplam_maliyet_usd, 6),
    }


def hata_mesaji(hata: BaseException) -> str:
    """Bir hata sınıfını kullanıcıya gösterilecek Türkçe mesaja çevirir (docs/03, 5.4)."""
    for sinif, mesaj in HATA_MESAJLARI.items():
        if isinstance(hata, sinif):
            return mesaj
    return "Beklenmeyen bir hata oluştu. Lütfen yeniden deneyin."


# --- Arayüz -----------------------------------------------------------------


def _baglam_kur(
    cinsiyet: str | None,
    medeni_hal: str | None,
    mevsim: str | None,
    gurbette: str | None,
) -> Baglam | None:
    """Boş bırakılan alanlar bağlama girmez; hiçbiri dolu değilse bağlam None."""
    alanlar: dict[str, Any] = {
        "cinsiyet": cinsiyet or None,
        "medeni_hal": medeni_hal or None,
        "mevsim": mevsim or None,
        "gurbette": {"evet": True, "hayır": False}.get(gurbette or ""),
    }
    if all(deger is None for deger in alanlar.values()):
        return None
    return Baglam(**alanlar)


def _atif_secenekleri(kayit: SorguKaydi | None) -> list[tuple[str, str]]:
    """Atıf açılır listesinin seçenekleri: (etiket, entry_id), tekrarsız."""
    if kayit is None or kayit.yorum is None:
        return []
    secenekler: list[tuple[str, str]] = []
    gorulen: set[str] = set()
    for bolum in kayit.yorum.bolumler:
        for atif in bolum.atiflar:
            if atif.entry_id in gorulen:
                continue
            gorulen.add(atif.entry_id)
            secenekler.append((atif.baslik, atif.entry_id))
    return secenekler


def arayuz_kur(bag: Bagimliliklar) -> Any:
    """``gr.Blocks`` döndürür.

    - Rüya kutusu (en fazla 3.000 karakter), isteğe bağlı bağlam alanları, gelenek seçimi
      ve "Yorumla" düğmesi.
    - "Yorum" sekmesi: yanıt, tıklanınca aslı ve çevirisi açılan atıflar, altta uyarı metni.
    - "Hata ayıklama" sekmesi: çıkarılan semboller, eşlemeler (yöntem, güven), getirilen
      maddeler ve skorları, adım süreleri, token ve maliyet. Hepsi SorguKaydi'ndan okunur.
    - HataSinifi → kullanıcı mesajı eşlemesi docs/03 bölüm 5.4'e göre.
    """
    import gradio as gr  # ağır paket: yalnızca işlevin içinde (docs/12, bölüm 1)

    def _calistir(
        metin: str,
        cinsiyet: str | None,
        medeni_hal: str | None,
        mevsim: str | None,
        gurbette: str | None,
        gelenekler: list[str] | None,
    ) -> tuple[str, SorguKaydi | None, Any, dict[str, Any]]:
        """Yorumla düğmesi: boru hattını çalıştırır, sekme çıktılarını döndürür."""
        metin = (metin or "").strip()
        if not metin:
            return (
                "Lütfen rüyanızı yazın.",
                None,
                gr.update(choices=[], value=None),
                {},
            )
        girdi = RuyaGirdisi(
            metin=metin[:3000],
            baglam=_baglam_kur(cinsiyet, medeni_hal, mevsim, gurbette),
            gelenekler=list(gelenekler) if gelenekler else None,
        )
        try:
            kayit = yorumla(girdi, bag)
        except RuyaHatasi as hata:
            return hata_mesaji(hata), None, gr.update(choices=[], value=None), {}

        secenekler = _atif_secenekleri(kayit)
        return (
            yorum_metni(kayit),
            kayit,
            gr.update(choices=secenekler, value=None),
            hata_ayiklama(kayit),
        )

    def _atif_goster(kayit: SorguKaydi | None, entry_id: str | None) -> str:
        if kayit is None or not entry_id:
            return "Bir atıf seçin."
        return atif_ayrintilari(kayit, entry_id, bag.depo)

    with gr.Blocks(title="Rüya Tabirnamesi") as demo:
        kayit_durumu = gr.State(None)

        gr.Markdown("# Rüya Tabirnamesi\nKlasik tabirname geleneğinden kaynaklı yorumlar.")
        with gr.Column():
            metin = gr.Textbox(
                label="Rüyanız",
                placeholder="Rüyanızı kendi cümlelerinizle anlatın…",
                lines=6,
                max_length=3000,
            )
            with gr.Accordion("Bağlam (isteğe bağlı)", open=False):
                cinsiyet = gr.Dropdown(["kadin", "erkek"], label="Cinsiyet", value=None)
                medeni_hal = gr.Dropdown(["evli", "bekar"], label="Medeni hâl", value=None)
                mevsim = gr.Dropdown(
                    ["ilkbahar", "yaz", "sonbahar", "kis"], label="Mevsim", value=None
                )
                gurbette = gr.Dropdown(["evet", "hayır"], label="Gurbette mi?", value=None)
            gelenekler = gr.CheckboxGroup(
                choices=GELENEKLER,
                label="Gelenek (boş: hepsi)",
                value=None,
            )
            dugme = gr.Button("Yorumla", variant="primary")

        with gr.Tabs():
            with gr.Tab("Yorum"):
                yanit = gr.Markdown("Yorum burada görünecek.")
                atif_secimi = gr.Dropdown(
                    choices=[], label="Atıflar (ayrıntı için seçin)", value=None
                )
                atif_ayrinti = gr.Markdown("")
                gr.Markdown(UYARI_METNI)
            with gr.Tab("Hata ayıklama"):
                ayiklama = gr.JSON(label="SorguKaydi izleri")

        dugme.click(
            _calistir,
            inputs=[metin, cinsiyet, medeni_hal, mevsim, gurbette, gelenekler],
            outputs=[yanit, kayit_durumu, atif_secimi, ayiklama],
        )
        atif_secimi.change(
            _atif_goster,
            inputs=[kayit_durumu, atif_secimi],
            outputs=[atif_ayrinti],
        )

    return demo


def baslat(bag: Bagimliliklar) -> Any:
    demo = arayuz_kur(bag)
    demo.launch(share=False, server_name="127.0.0.1")
    return demo
