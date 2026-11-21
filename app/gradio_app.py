"""Gradio arayüzü (İG-40, İG-41, İG-42). Takvim: Hafta 5.

notebooks/05_arayuz.ipynb içinden açılır::

    from app.gradio_app import baslat
    baslat(varsayilan_bagimliliklar())

Güvenlik: ``launch(share=True)`` **kullanılmaz** (TK-09). Herkese açık bir link üretir ve
linki bulan herkes senin API anahtarınla sorgu çalıştırabilir.
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from app import sunum

from ruya.etik import REDDEDILDI_MESAJI, UYARI_METNI
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


# --- Saf yardımcılar (sunucu açmadan test edilir) ---------------------------


def yorum_akisi(girdi: RuyaGirdisi, bag: Bagimliliklar) -> Iterator[tuple[str, SorguKaydi | None]]:
    """Boru hattını ayrı bir iş parçacığında çalıştırır, ilerlemeyi parça parça yayar.

    Her parça ``(html, kayıt)`` çiftidir: ilerleme parçalarında kayıt ``None``, sonda
    yorum HTML'iyle birlikte tam kayıt döner. ``RuyaHatasi`` kullanıcı mesajına çevrilir;
    diğer hatalar iş parçacığından ana iş parçacığına taşınıp yeniden fırlatılır.
    """
    depo = getattr(bag, "depo", None)
    kuyruk: queue.Queue[tuple[str, Any]] = queue.Queue()

    def _bildir(asama: str, kayit: SorguKaydi) -> None:
        kuyruk.put(("ara", (asama, kayit)))

    def _calistir() -> None:
        try:
            kayit = yorumla(girdi, bag, ilerleme=_bildir)
        except BaseException as hata:  # ana iş parçacığına taşınır
            kuyruk.put(("hata", hata))
        else:
            kuyruk.put(("son", kayit))

    yield sunum.ilerleme_html("baslangic"), None

    is_parcacigi = threading.Thread(target=_calistir, daemon=True)
    is_parcacigi.start()

    while True:
        tur, veri = kuyruk.get()
        if tur == "ara":
            asama, kayit = veri
            yield sunum.akis_html(asama, kayit, depo), None
        elif tur == "son":
            yield sunum.akis_html("bitti", veri, depo), veri
            return
        else:
            if isinstance(veri, RuyaHatasi):
                yield sunum.hata_html(hata_mesaji(veri)), None
                return
            raise veri


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
            "pasaj": aday.pasaj,
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


# Uzantı → MIME; OCR servisi görselin türünü buradan öğrenir.
GORSEL_MIME: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

DESTEKLENMEYEN_GORSEL_MESAJI = (
    "Bu dosya türü okunamıyor. Lütfen PNG, JPG ya da WEBP bir fotoğraf yükleyin."
)


def gorselden_ruya(yol: str | None, istemci: Any) -> str:
    """Bir fotoğraftaki rüya metnini OCR ile okur (İG-40).

    Görsel ve okunan metin **loglanmaz**; görsel yalnızca EVREN servisine gönderilir.
    Hata durumunda kullanıcıya gösterilecek Türkçe mesaj döner.
    """
    if not yol:
        return ""
    mime = GORSEL_MIME.get(Path(yol).suffix.lower())
    if mime is None:
        return DESTEKLENMEYEN_GORSEL_MESAJI
    try:
        veri = Path(yol).read_bytes()
        metin = istemci.ocr(veri, mime)
    except RuyaHatasi as hata:
        return hata_mesaji(hata)
    except OSError:
        return "Fotoğraf okunamadı. Lütfen dosyayı yeniden yükleyin."
    return (metin or "").strip()[:3000]


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


def arayuz_kur(bag: Bagimliliklar) -> Any:
    """``gr.Blocks`` döndürür; tek sütunlu, ortalanmış bir sayfa kurar (docs/16).

    - Başlık şeridi (``sunum.BASLIK`` + ``sunum.ALT_BASLIK``) ve "Nasıl çalışır?" akordeonu.
    - Girdi kartı: rüya kutusu (3.000 karakter, ipucu metni), örnek rüyalar, kapalı
      "Fotoğraftan oku" akordeonu (İG-40; görsel saklanmaz, loglanmaz), kapalı "Bağlam"
      akordeonu (Türkçe etiketli açılır listeler), gelenek seçimi ve "Yorumla" düğmesi.
    - Sonuç alanı: tek bir ``gr.HTML``; akış sırasında ilerleme şeridi, sembol rozetleri ve
      yorum bölümleri, kaynaklar ``<details>`` olarak görünür.
    - Uyarı metni sayfada bir kez, alt bilgide.
    - Sayfanın en altında kapalı "Geliştirici ayrıntıları" akordeonu: ham ``SorguKaydi`` izleri.
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
    ) -> Iterator[tuple[str, SorguKaydi | None, dict[str, Any]]]:
        """Yorumla düğmesi: boru hattını akışlı çalıştırır, sonuç ve izleri döndürür."""
        metin = (metin or "").strip()
        if not metin:
            yield sunum.hata_html("Lütfen rüyanızı yazın."), None, {}
            return
        girdi = RuyaGirdisi(
            metin=metin[:3000],
            baglam=_baglam_kur(cinsiyet, medeni_hal, mevsim, gurbette),
            gelenekler=list(gelenekler) if gelenekler else None,
        )
        for parca, kayit in yorum_akisi(girdi, bag):
            if kayit is None:
                yield parca, None, {}
                continue
            yield parca, kayit, hata_ayiklama(kayit)

    def _gorselden_oku(dosya: str | None) -> str:
        """Fotoğraftan okunan metni rüya kutusuna yazar; görsel ve metin loglanmaz."""
        return gorselden_ruya(dosya, bag.istemci)

    with gr.Blocks(title="Rüya Tabirnamesi") as demo:
        kayit_durumu = gr.State(None)

        with gr.Column(elem_classes="ruya-sayfa"):
            gr.HTML(
                '<header class="ruya-baslik">'
                f"<h1>{sunum.BASLIK}</h1>"
                f"<p>{sunum.ALT_BASLIK}</p>"
                "</header>"
            )
            with gr.Accordion("Nasıl çalışır?", open=False):
                gr.Markdown(sunum.NASIL_CALISIR)

            with gr.Group(elem_classes="ruya-kart"):
                metin = gr.Textbox(
                    label="Rüyanız",
                    info=sunum.RUYA_IPUCU,
                    lines=6,
                    max_length=3000,
                    placeholder="Rüyamda …",
                )
                gr.Examples(
                    examples=[[ruya] for ruya in sunum.ORNEK_RUYALAR],
                    inputs=[metin],
                    label="Örnek rüyalar",
                )
                with gr.Accordion("Fotoğraftan oku", open=False):
                    gr.Markdown(sunum.FOTO_ACIKLAMASI)
                    foto = gr.Image(type="filepath", label="Rüya defteri fotoğrafı")
                    oku = gr.Button("Metni oku")
                with gr.Accordion("Bağlam (isteğe bağlı)", open=False):
                    gr.Markdown(sunum.BAGLAM_ACIKLAMASI)
                    with gr.Row():
                        cinsiyet = gr.Dropdown(
                            choices=sunum.CINSIYET_SECENEKLERI,
                            label="Cinsiyet",
                            value=None,
                        )
                        medeni_hal = gr.Dropdown(
                            choices=sunum.MEDENI_HAL_SECENEKLERI,
                            label="Medeni hâl",
                            value=None,
                        )
                        mevsim = gr.Dropdown(
                            choices=sunum.MEVSIM_SECENEKLERI,
                            label="Mevsim",
                            value=None,
                        )
                        gurbette = gr.Dropdown(
                            choices=sunum.GURBET_SECENEKLERI,
                            label="Gurbette mi?",
                            value=None,
                        )
                gelenekler = gr.CheckboxGroup(
                    choices=sunum.GELENEKLER,
                    label="Gelenek",
                    info=sunum.GELENEK_ACIKLAMASI,
                    value=None,
                )
                dugme = gr.Button("Yorumla", variant="primary", size="lg")

            sonuc_html = gr.HTML(
                '<div class="ruya-bos">Yorum burada görünecek.</div>',
                elem_classes="ruya-sonuc-alani",
            )

            gr.Markdown(UYARI_METNI, elem_classes="ruya-uyari")

            with gr.Accordion("Geliştirici ayrıntıları", open=False):
                ayiklama = gr.JSON(label="SorguKaydi izleri")

        dugme.click(
            _calistir,
            inputs=[metin, cinsiyet, medeni_hal, mevsim, gurbette, gelenekler],
            outputs=[sonuc_html, kayit_durumu, ayiklama],
        )
        oku.click(_gorselden_oku, inputs=[foto], outputs=[metin])

    return demo


def baslat(bag: Bagimliliklar) -> Any:
    import gradio as gr  # ağır paket: yalnızca işlevin içinde (docs/12, bölüm 1)

    demo = arayuz_kur(bag)
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            neutral_hue="slate",
            font=["system-ui", "Segoe UI", "sans-serif"],
        ),
        css_paths=[Path(__file__).with_name("stil.css")],
    )
    return demo
