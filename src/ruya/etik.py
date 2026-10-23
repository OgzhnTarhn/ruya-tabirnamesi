"""Sabit etik metinler ve yasak ifadeler (docs/07-etik-ve-hukuk.md).

Metinler burada tek yerde durur; sentez talimatı, arayüz ve değerlendirme buradan okur.
Belgedeki metin değişirse burası da aynı commit'te güncellenir.
"""

# docs/07, bölüm 4 · İG-36: her yanıtın altında
UYARI_METNI = (
    "Bu uygulama kişisel bir öğrenme projesidir. Yorumlar klasik tabirname geleneğinden ve "
    "tarihsel kaynaklardan derlenir. Geleceği öngörmez, dinî hüküm değildir ve tıbbi ya da "
    "psikolojik tavsiye yerine geçmez. Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu'na "
    "göre rüyalar bağlayıcı değildir. Sizi rahatsız eden, tekrarlayan rüyalar için bir uzmana "
    "başvurun."
)

# docs/07, bölüm 3: hassas_icerik=True ise yanıtın başına
GUVENLIK_NOTU = (
    "Sizi rahatsız eden ve tekrarlayan rüyalar için bir ruh sağlığı uzmanıyla konuşmak iyi "
    "gelebilir. Acil bir durumda 112'yi arayın."
)

# docs/03, bölüm 5.4
SEMBOL_YOK_MESAJI = "Rüyanda tabir edilecek bir sembol bulamadım."
REDDEDILDI_MESAJI = "Bu rüya yorumlanamadı."

# docs/07, bölüm 2 (D1–D3, D6): değerlendirmede otomatik taranır.
# Küçük harfle yazılır; tarama Türkçe küçük harfe çevrilmiş metinde yapılır.
YASAK_IFADELER: tuple[str, ...] = (
    "kesinlikle",
    "diyanet'e göre",
    "allah'ın mesajı",
    "allah sana",
    "ölüm habercisi",
    "depresyonda olduğunu",
    "ibn sirin'e göre",  # doğrusu: "İbn Sirin'e atfedilen Muntahab'a göre"
)
