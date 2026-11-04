"""Kural tabanlı koşul çıkarma (LLM'siz, deterministik). Kurallar: docs/13-hibrit-getirme.md.

Kurallar **bilinçli olarak dardır**: yalnızca aşağıda açıkça listelenen Türkçe biçimler
tanınır. Bir eşleşme şüpheliyse koşul üretilmez; kaçırmak, yanlış koşul üretmekten iyidir
(docs/13: kural kaçırırsa zarar yok, madde yine sıralamada kalır).

Koşullar **rüya sahibine** aittir: "kadın görürse" rüyayı görenin kadın olduğunu söyler.
Rüyada görülen bir figür ("bir kadın gördüyse") koşul değildir; bu yüzden yalın ad yalnızca
cümlenin başında ve bir koşul ekiyle birlikte tanınır, nesne konumundaki adlar atlanır.

Türkçe duyarlı küçük harfe çevirme ``ruya.text.turkce.kucuk_harf`` ile yapılır
(``"İlkbaharda"`` → ``"ilkbaharda"``); bütün eşleşmeler kelime sınırlı desenlerle aranır,
böylece "evlilik" sözcüğü "evli" koşulunu tetiklemez.

Çıktı ``ruya.schemas.Kosul`` nesneleridir; ``otorite`` alanı kural tabanlı çıkarmada boş kalır.
"""

from __future__ import annotations

import re

from ruya.schemas import Kosul, Madde
from ruya.text.turkce import kucuk_harf

# Cümle sonları: nokta, ünlem, soru işareti. İşaret cümlenin sonunda kalır.
_CUMLE_DESENI = re.compile(r"[^.!?]*[.!?]?")

# Cinsiyet adları: yalın hâl (rüya sahibi) ve tamlayan/tamlanan çekimleri ayrı kurallarda.
_KADIN = r"(?:kadın|kadınlar)"
_ERKEK = r"(?:erkek|erkekler|adam|adamlar)"

# Cümlenin başında kabul edilen sıfatlar ("genç bir kadın görürse").
_SIFATLAR = r"(?:genç|yaşlı|evli|bekar|bekâr|hamile|hasta)"

# Medeni hâl koşulundan sonra gelebilecek sözcükler ("evli ise", "bekâr biri").
_MEDENI_IZLEYEN = r"(?:ise|görürse|olan|için|biri|kişi)"

# Mevsim adından sonra gelen ve koşulu nesneye çeviren sözcük başları ("kışın şiddeti").
_MEVSIM_DISLAMA = r"(?:şiddet|geliş|gidiş|soğu|sıca)"

# --- Cinsiyet ----------------------------------------------------------------

# (a) Cümle sıfat(lar) ve isteğe bağlı "bir" ile başlar, ardından cinsiyet adı gelir ve
#     cümlede "-se/-sa" ekiyle biten bir sözcük vardır: "Genç bir kadın görürse".
# (b) Tamlayan hâli en fazla 6 sözcük sonra "görmesi" ile gelir: "kadının yılan görmesi".
# (c) Yönelme hâli "gelince" ile ya da yalın hâl "için" ile gelir: "kadına gelince".
_CINSIYET = (
    (
        "cinsiyet",
        "kadin",
        re.compile(
            rf"^(?:{_SIFATLAR}\s+)*(?:bir\s+)?{_KADIN}\b(?=.*\w*(?:sa|se)\b)"
        ),
    ),
    (
        "cinsiyet",
        "kadin",
        re.compile(r"\b(?:kadının|kadınların)\b(?:\s+\S+){0,6}\s+görmesi\b"),
    ),
    (
        "cinsiyet",
        "kadin",
        re.compile(rf"\b(?:kadına|kadınlara)\s+gelince\b|\b{_KADIN}\s+için\b"),
    ),
    (
        "cinsiyet",
        "erkek",
        re.compile(
            rf"^(?:{_SIFATLAR}\s+)*(?:bir\s+)?{_ERKEK}\b(?=.*\w*(?:sa|se)\b)"
        ),
    ),
    (
        "cinsiyet",
        "erkek",
        re.compile(r"\b(?:erkeğin|erkeklerin|adamın|adamların)\b(?:\s+\S+){0,6}\s+görmesi\b"),
    ),
    (
        "cinsiyet",
        "erkek",
        re.compile(rf"\b(?:erkeğe|erkeklere)\s+gelince\b|\b{_ERKEK}\s+için\b"),
    ),
)

# --- Medeni hâl --------------------------------------------------------------

# "evli değilse / evli olmayan" bekar sayılır ve o aralıkta "evli" eşleşmesini kapatır.
_MEDENI_HAL = (
    (
        "medeni_hal",
        "bekar",
        re.compile(
            r"\bevli\s+(?:değilse|değil\s+ise|olmayan)\b"
            rf"|\b(?:bekar|bekâr)\b(?=(?:\s+\w+){{0,3}}\s+{_MEDENI_IZLEYEN}\b)"
            r"|\b(?:bekarsa|bekârsa)\b"
            r"|\b(?:bekarın|bekârın|bekarların|bekârların)\s+evlenmesine\b"
        ),
    ),
    (
        "medeni_hal",
        "evli",
        re.compile(
            r"\bevli\b(?!\s+(?:değilse|değil\s+ise|olmayan)\b)"
            rf"(?=(?:\s+\w+){{0,3}}\s+{_MEDENI_IZLEYEN}\b)"
            r"|\bevliyse\b"
        ),
    ),
)

# --- Mevsim ------------------------------------------------------------------

# Mevsim adları yalın hâlde koşul sayılmaz ("kışlık erzak"); yalnızca zaman bildiren
# biçimler tanınır ("kışın", "ilkbaharda"). "kışın şiddeti" gibi nesne kullanımları atlanır.
_MEVSIM = (
    (
        "mevsim",
        "kis",
        re.compile(rf"\bkışın\b(?!\s+{_MEVSIM_DISLAMA})|\bkış mevsiminde\b"),
    ),
    (
        "mevsim",
        "yaz",
        re.compile(rf"\byazın\b(?!\s+{_MEVSIM_DISLAMA})|\byaz mevsiminde\b"),
    ),
    ("mevsim", "ilkbahar", re.compile(r"\bilkbaharda\b")),
    ("mevsim", "sonbahar", re.compile(r"\bsonbaharda\b")),
)

# Düz tablo: (alan, deger, küçük harfli cümlede aranan desen).
_KURALLAR: tuple[tuple[str, str, re.Pattern[str]], ...] = _CINSIYET + _MEDENI_HAL + _MEVSIM


def _cumleler(metin: str) -> list[str]:
    """Metni ``. ! ?`` işaretlerinden böler; işaret cümlenin sonunda kalır, boşlar atılır."""
    return [parca.strip() for parca in _CUMLE_DESENI.findall(metin) if parca.strip()]


def kosullari_cikar(metin: str | None) -> list[Kosul]:
    """Metinden kural tabanlı koşulları çıkarır.

    Her cümle için tanınan her koşul ayrı bir ``Kosul`` döndürür; ``yorum_tr`` o cümlenin
    kırpılmış hâlidir, ``otorite`` boş kalır. Koşul bulunmayan cümleler atlanır; ``metin``
    boş ya da ``None`` ise boş liste döner. Sıra korunur: cümle sırası, içinde kuralların
    tanımlı sırası. Aynı cümlede aynı ``{alan: deger}`` ikinci kez eklenmez.
    """
    if not metin or not metin.strip():
        return []

    kosullar: list[Kosul] = []
    for cumle in _cumleler(metin):
        kucuk = kucuk_harf(cumle)
        bulunan: set[tuple[str, str]] = set()
        for alan, deger, desen in _KURALLAR:
            if (alan, deger) in bulunan or desen.search(kucuk) is None:
                continue
            bulunan.add((alan, deger))
            kosullar.append(Kosul(kosul={alan: deger}, yorum_tr=cumle))
    return kosullar


def maddelere_uygula(maddeler: list[Madde]) -> list[Madde]:
    """Maddelerin kopyalarına ``kosullar`` alanını yazar; başka hiçbir alanı değiştirmez.

    ``metin_tr`` boşsa ya da cümlelerde koşul bulunamazsa alan ``None`` kalır. Girdi
    nesneleri değiştirilmez, sıra korunur.
    """
    return [
        madde.model_copy(update={"kosullar": kosullari_cikar(madde.metin_tr) or None})
        for madde in maddeler
    ]
