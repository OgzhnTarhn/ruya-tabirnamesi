"""Kural tabanlı yöntem etiketi çıkarma (LLM'siz, deterministik). Kurallar: docs/05.

Klasik tabirci anlamı birkaç yoldan türetir: ayet, hadis, mesel (atasözü), zıddıyla tabir,
kelime kökü ve ebced (docs/05, Katman 4). Bu modül bir maddenin Türkçe metninde bu yolların
anıldığını sezer ve ``Madde.yontem`` alanına etiket olarak yazar.

Kurallar **bilinçli olarak dardır**: yalnızca aşağıda açıkça listelenen Türkçe biçimler
tanınır. Bir eşleşme şüpheliyse etiket üretilmez; kaçırmak, yanlış etiket üretmekten iyidir.

Türkçe duyarlı küçük harfe çevirme ``ruya.text.turkce.kucuk_harf`` ile yapılır
(``"Âyette"`` → ``"âyette"``); bütün eşleşmeler kelime sınırlı desenlerle aranır, böylece
yalın "hadis" sözcüğü "hadiste" biçimini tetiklemez.
"""

from __future__ import annotations

import re

from ruya.schemas import Madde
from ruya.text.turkce import kucuk_harf

# Cümle sonları: nokta, ünlem, soru işareti. İşaret cümlenin sonunda kalır.
_CUMLE_DESENI = re.compile(r"[^.!?]*[.!?]?")

# "buyur-" ile başlayan sözcük ("buyurmuştur", "buyurdu", "buyurur").
_BUYUR = r"\bbuyur\w*"

# --- Etiket kuralları -------------------------------------------------------

# Ayet: "Allah Teâlâ … buyur…" (aynı cümlede) ya da âyet sözcüğünün çekimli biçimleri.
_AYET = re.compile(
    r"\ballah\s+te[âa]l[âa]\b(?=.*" + _BUYUR + r")"
    r"|\b(?:âyet|ayet|âyeti|ayeti|âyette|ayette|âyetinde|ayetinde)\b"
)

# Hadis: hadis sözcüğünün çekimli biçimleri, "hadis-i" ya da peygamber/resûlullah + "buyur…".
_HADIS = re.compile(
    r"\b(?:hadiste|hadisinde|hadis-i)\b"
    r"|\bhadisi\s+şerif"
    r"|\b(?:peygamber|resûlullah|resulullah)\b(?=.*" + _BUYUR + r")"
)

# Mesel: atasözü ve mesel sözcüğünün çekimli biçimleri.
_MESEL = re.compile(r"\b(?:mesel|meselde|meselinde|atasözü|atasözünde)\b")

# Zıt: zıddıyla tabir kalıpları.
_ZIT = re.compile(r"\b(?:zıddıyla|zıddıdır|zıddına)\b|\btersine\s+yorumlanır\b")

# Kök: sözcüğün lafzından/kelimesinden/isminden türetme.
_KOK = re.compile(r"\b(?:lafzından|kelimesinden|isminden)\b")

# Ebced: sözcük başında "ebced" ("ebced hesabı", "ebcedle").
_EBCED = re.compile(r"\bebced\w*")

# Sabit sıra: etiketler bu sırayla ve her biri en fazla bir kez döner.
_KURALLAR: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ayet", _AYET),
    ("hadis", _HADIS),
    ("mesel", _MESEL),
    ("zit", _ZIT),
    ("kok", _KOK),
    ("ebced", _EBCED),
)


def _cumleler(metin: str) -> list[str]:
    """Metni ``. ! ?`` işaretlerinden böler; işaret cümlenin sonunda kalır, boşlar atılır."""
    return [parca.strip() for parca in _CUMLE_DESENI.findall(metin) if parca.strip()]


def yontemleri_cikar(metin_tr: str | None) -> list[str]:
    """Metinde tanınan anlam türetme yollarını sabit sırayla döndürür.

    Sıra ``ayet, hadis, mesel, zit, kok, ebced``; her etiket en fazla bir kez döner.
    ``metin_tr`` boş ya da ``None`` ise boş liste döner.
    """
    if not metin_tr or not metin_tr.strip():
        return []

    cumleler = [kucuk_harf(cumle) for cumle in _cumleler(metin_tr)]
    return [
        etiket
        for etiket, desen in _KURALLAR
        if any(desen.search(cumle) for cumle in cumleler)
    ]


def maddelere_uygula(maddeler: list[Madde]) -> list[Madde]:
    """Maddelerin kopyalarına ``yontem`` alanını yazar; başka hiçbir alanı değiştirmez.

    ``metin_tr`` boşsa ya da etiket bulunamazsa alan ``None`` kalır. Girdi nesneleri
    değiştirilmez, sıra korunur.
    """
    return [
        madde.model_copy(update={"yontem": yontemleri_cikar(madde.metin_tr) or None})
        for madde in maddeler
    ]
