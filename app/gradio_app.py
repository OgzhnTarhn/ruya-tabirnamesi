"""Gradio arayüzü (İG-40, İG-41, İG-42). Takvim: Hafta 5.

notebooks/05_arayuz.ipynb içinden açılır::

    from app.gradio_app import baslat
    baslat(varsayilan_bagimliliklar())

Güvenlik: ``launch(share=True)`` **kullanılmaz** (TK-09). Herkese açık bir link üretir ve
linki bulan herkes senin API anahtarınla sorgu çalıştırabilir.
"""

from __future__ import annotations

from typing import Any

from ruya.pipeline.run import Bagimliliklar


def arayuz_kur(bag: Bagimliliklar) -> Any:
    """``gr.Blocks`` döndürür.

    - Rüya kutusu (en fazla 3.000 karakter), isteğe bağlı bağlam alanları, gelenek seçimi
      ve "Yorumla" düğmesi.
    - "Yorum" sekmesi: yanıt, tıklanınca aslı ve çevirisi açılan atıflar, altta uyarı metni.
    - "Hata ayıklama" sekmesi: çıkarılan semboller, eşlemeler (yöntem, güven), getirilen
      maddeler ve skorları, adım süreleri, token ve maliyet. Hepsi SorguKaydi'ndan okunur.
    - HataSinifi → kullanıcı mesajı eşlemesi docs/03 bölüm 5.4'e göre.
    """
    raise NotImplementedError("Hafta 5: app/gradio_app.py (docs/08)")


def baslat(bag: Bagimliliklar) -> Any:
    demo = arayuz_kur(bag)
    demo.launch(share=False)
    return demo
