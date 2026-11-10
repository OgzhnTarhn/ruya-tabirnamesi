"""LLM hakemle gümüş etiket (docs/15, K12).

D1/D2 için havuzu bir LLM hakem işaretler; kullanıcının kendi etiketleri gelince kesin
karar onun olur, hakem yalnız ön karar verir. Hakem **kaynak adını ve ``entry_id``'yi
görmez**: adaylar numaralı ve yalnız metinleriyle verilir, böylece çeşitlerden birini
kayırmaz. Sonuç kesin değildir; gümüş etiket yalnız ölçüm içindir.

Rüya metni hiçbir zaman loglanmaz (İOG-07); yalnız istek gövdesinde modele gider ve
işaretli dosyaya, kullanıcının işaretlemesi için yazılır. Model adı yalnız
``ruya.config.MODEL_HAKEM`` içinde tanımlıdır.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ruya.config import MODEL_HAKEM, SOHBET_EK_ALANLARI
from ruya.hatalar import RuyaHatasi, YanitBozuk
from ruya.index.store import MaddeDeposu
from ruya.llm.client import LLMIstemcisi
from ruya.llm.talimatlar import talimat_oku
from ruya.schemas import Madde

TALIMAT = "getirme_hakemi_v1"

# Yanıt yalnız bir numara listesi; düşünme kapalı olduğu için küçük bir sınır yeter.
EN_UZUN_CIKTI_TOKEN = 1000

# Aday metninin istekteki en fazla karakter sayısı.
METIN_SINIRI = 600

# Aynı anda uçuştaki hakem istekleri (geçit 429 verirse düşürülür).
EN_FAZLA_ESZAMANLI = 4

Satir = dict[str, Any]


def _aday_metni(madde: Madde) -> str:
    """Tek satırlık, kırpılmış aday metni; çeviri yoksa asıl metin kullanılır."""
    metin = madde.metin_tr or madde.metin_asli
    return " ".join(metin.split())[:METIN_SINIRI]


def _kullanici_metni(ruya_metni: str, sembol: str, maddeler: list[Madde]) -> str:
    """Rüya, sembol ve numaralı adaylar; kaynak adı ve ``entry_id`` yazılmaz."""
    satirlar = [f"Rüya:\n{ruya_metni}", "", f"Sembol: {sembol}", "", "Aday maddeler:"]
    for sira, madde in enumerate(maddeler, start=1):
        satirlar.append(f"[{sira}] {_aday_metni(madde)}")
    return "\n".join(satirlar)


def hakem_istegi(ruya_metni: str, sembol: str, maddeler: list[Madde]) -> dict[str, Any]:
    """OpenAI uyumlu sohbet gövdesi: sabit talimat başta, rüya ve adaylar sonda."""
    return {
        **SOHBET_EK_ALANLARI,
        "model": MODEL_HAKEM,
        "max_tokens": EN_UZUN_CIKTI_TOKEN,
        "messages": [
            {"role": "system", "content": talimat_oku(TALIMAT)},
            {"role": "user", "content": _kullanici_metni(ruya_metni, sembol, maddeler)},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "hakem",
                "schema": {
                    "type": "object",
                    "properties": {
                        "ilgili": {"type": "array", "items": {"type": "integer"}},
                    },
                    "required": ["ilgili"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        },
    }


def _numaralar(govde: object) -> list[int]:
    """Yanıt gövdesindeki ``ilgili`` numaralarını denetleyip döndürür."""
    if not isinstance(govde, dict):
        raise YanitBozuk(f"Hakem yanıtı nesne değil: {type(govde).__name__}")
    ilgili = govde.get("ilgili")
    if not isinstance(ilgili, list) or not all(
        isinstance(sira, int) and not isinstance(sira, bool) for sira in ilgili
    ):
        raise YanitBozuk(f"Hakem yanıtında 'ilgili' tam sayı listesi değil: {ilgili!r}")
    return ilgili


def hakem_sec(
    ruya_metni: str,
    sembol: str,
    maddeler: list[Madde],
    istemci: LLMIstemcisi,
) -> set[str]:
    """Adaylardan ilgili olanların ``entry_id`` kümesini döndürür.

    Numaralar 1'den başlar; sınır dışı ve tekrar eden numaralar atlanır. Aday yoksa
    istek yapılmaz. Şemaya uymayan yanıt ``YanitBozuk`` verir.
    """
    if not maddeler:
        return set()
    yanit = istemci.mesaj(hakem_istegi(ruya_metni, sembol, maddeler), ruya_icerir=True)
    secilen: set[str] = set()
    for sira in _numaralar(yanit.json()):
        if 1 <= sira <= len(maddeler):
            secilen.add(maddeler[sira - 1].entry_id)
    return secilen


def _sembol_adlari(satirlar: list[Satir]) -> dict[tuple[str, str], str]:
    """(rüya, anahtar) → görünen sembol adı; satırlardaki ilk ad kullanılır."""
    adlar: dict[tuple[str, str], str] = {}
    for satir in satirlar:
        adlar.setdefault((satir["ornek_id"], satir["anahtar"]), satir["sembol"])
    return adlar


def _maddeler(depo: MaddeDeposu, kimlikler: list[str]) -> list[Madde]:
    """Depoda bulunan maddeler; olmayan kimlikler sessizce atlanır."""
    maddeler: list[Madde] = []
    for entry_id in kimlikler:
        try:
            maddeler.append(depo.madde(entry_id))
        except KeyError:
            continue
    return maddeler


def gumus_etiketle(
    havuz: dict[tuple[str, str], list[str]],
    satirlar: list[Satir],
    metinler: dict[str, str],
    depo: MaddeDeposu,
    istemci: LLMIstemcisi,
    en_fazla_eszamanli: int = EN_FAZLA_ESZAMANLI,
) -> dict[tuple[str, str], set[str]]:
    """Havuzdaki her (rüya, anahtar) için hakemi çağırır; gümüş etiketleri döndürür.

    Sembol adı satırlardan gelir, yoksa anahtar kullanılır. Bir anahtar hata verirse
    (``RuyaHatasi``) yalnız o anahtar sonuçta yer almaz, diğerleri sürer.
    """
    adlar = _sembol_adlari(satirlar)

    def calistir(anahtar: tuple[str, str]) -> set[str]:
        ornek_id, anahtar_adi = anahtar
        maddeler = _maddeler(depo, havuz[anahtar])
        return hakem_sec(
            metinler.get(ornek_id, ""),
            adlar.get(anahtar, anahtar_adi),
            maddeler,
            istemci,
        )

    sonuc: dict[tuple[str, str], set[str]] = {}
    with ThreadPoolExecutor(max_workers=max(1, en_fazla_eszamanli)) as havuz_isi:
        gelecekler = {anahtar: havuz_isi.submit(calistir, anahtar) for anahtar in havuz}
        for anahtar, gelecek in gelecekler.items():
            try:
                sonuc[anahtar] = gelecek.result()
            except RuyaHatasi:
                continue
    return sonuc


def etiketleri_isaretle(
    kaynak: Path,
    etiketler: dict[tuple[str, str], set[str]],
    cikti: Path,
) -> Path:
    """Etiket dosyasının bir kopyasında ilgili satırları ``[x]`` yapar.

    Kaynak dosya değişmez; başlıklar, rüya alıntısı ve madde metinleri aynen kalır.
    Etiketi olmayan anahtarların bütün satırları işaretsiz yazılır.
    """
    metin = kaynak.read_text(encoding="utf-8")
    ornek_id: str | None = None
    anahtar: str | None = None
    yeni: list[str] = []
    for satir in metin.splitlines():
        if satir.startswith("## "):
            ornek_id = satir[3:].strip()
            anahtar = None
        elif satir.startswith("### ") and ornek_id is not None:
            baslik = satir[4:].strip()
            anahtar = baslik[baslik.rfind("(") + 1 : baslik.rfind(")")].strip()
        elif satir.startswith(("- [ ] ", "- [x] ", "- [X] ")) and anahtar is not None:
            entry_id = satir[6:].split(" — ", 1)[0].strip()
            ilgili = etiketler.get((ornek_id, anahtar), set())
            isaret = "[x]" if entry_id in ilgili else "[ ]"
            satir = f"- {isaret} {satir[6:]}"
        yeni.append(satir)

    cikti.parent.mkdir(parents=True, exist_ok=True)
    son = "\n".join(yeni) + ("\n" if metin.endswith("\n") else "")
    cikti.write_text(son, encoding="utf-8")
    return cikti
