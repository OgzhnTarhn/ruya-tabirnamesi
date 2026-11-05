"""Kural tabanlı kapsam çıkarma (LLM'siz, deterministik). Kurallar: docs/05, Katman 3.

Bazı tabirler kişiye değil hükümdara ya da bir yerin halkına yöneliktir. Bu modül böyle
bir cümle taşıyan maddeyi ``Madde.kapsam`` alanında ``padisah`` ya da ``vilayet`` diye
işaretler. Etiket maddenin tamamını değil, **en az bir cümlesini** anlatır; ikisi de varsa
``padisah`` yazılır. Etiket yoksa alan ``None`` kalır ve madde kişiye yönelik sayılır.

Kurallar **bilinçli olarak dardır**: "bir hükümdarın … görürse" gibi rüyada görülen bir kişi
kapsam değildir, "ev halkı" ya da yalın "halk" da toplum anlamına gelmez.
"""

from __future__ import annotations

import re

from ruya.schemas import Kapsam, Madde
from ruya.text.turkce import kucuk_harf

_HUKUMDAR = r"(?:padişah|sultan|hükümdar|melik|halife)"
# Cümle ya da yan cümle başı; "ve sultan için", "amiri bir sultan ise" burada eşleşmez.
_BAS = r"(?:^|[;:,(]\s*)"

_PADISAH = (
    re.compile(rf"{_BAS}(?:eğer\s+|gören\s+|bir\s+)*{_HUKUMDAR}\s+(?:ise|için)\b"),
    re.compile(rf"\b(?:bunu|onu)\s+(?:bir\s+)?{_HUKUMDAR}\s+görürse\b"),
)

_YER = (
    r"(?:yer|yerin|şehir|şehrin|belde|beldenin|memleket|memleketin"
    r"|köy|köyün|bölge|bölgenin|ülke|ülkenin)"
)
_VILAYET = (re.compile(rf"\b{_YER}\s+(?:halk|ahali)\w*"),)


def _cumleler(metin: str) -> list[str]:
    return [kucuk_harf(parca).strip() for parca in re.split(r"(?<=[.!?])\s+", metin)]


def kapsami_cikar(metin_tr: str | None) -> Kapsam | None:
    """Metinde hükümdara ya da bir yerin halkına yönelik cümle varsa etiketini döndürür."""
    if not metin_tr or not metin_tr.strip():
        return None
    cumleler = _cumleler(metin_tr)
    if any(desen.search(cumle) for desen in _PADISAH for cumle in cumleler):
        return "padisah"
    if any(desen.search(cumle) for desen in _VILAYET for cumle in cumleler):
        return "vilayet"
    return None


def maddelere_uygula(maddeler: list[Madde]) -> list[Madde]:
    """Maddelerin kopyalarına ``kapsam`` yazar; başka alana dokunmaz, sıra korunur."""
    return [
        madde.model_copy(update={"kapsam": kapsami_cikar(madde.metin_tr)}) for madde in maddeler
    ]
