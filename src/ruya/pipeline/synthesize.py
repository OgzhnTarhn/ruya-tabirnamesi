"""Adım 4 · Sentez: kaynaklı Türkçe yorum (LLM, numaralı kaynaklar, kodda atıf doğrulama).
Takvim: Hafta 5.

- Adaylar numaralı kaynaklar olarak verilir ([K1] entry_id · başlık, metin_tr, metin_asli);
  model JSON şemasıyla bolumler[{metin, kaynaklar[{entry_id, alinti}]}] ve bulunamayanlar
  döndürür. ``atiflari_dogrula`` verilmemiş entry_id içeren atıfları atar, metinde geçmeyen
  alıntıları boşaltır (docs/03, adım 4).
- Sistem talimatı ``prompts/sentez_v<n>.md``; kurallar docs/05 bölüm 3 ve docs/07.
  Sabit talimat mesajların başında durur (geçidin önek önbelleği için).
- Eşleşmeyen ya da maddesi olmayan semboller ``Yorum.bulunamayanlar``'a (İG-31).
- ``cikarim.hassas_icerik`` ise ``Yorum.guvenlik_notu = etik.GUVENLIK_NOTU``.
- ``Yorum.uyari`` her zaman ``etik.UYARI_METNI`` (İG-36).
- İstek ``istemci.mesaj(istek, ruya_icerir=True)`` ile gönderilir (rüya metni
  içerir; docs/03 bölüm 5.2).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ruya.config import MODEL_SENTEZ
from ruya.etik import GUVENLIK_NOTU, UYARI_METNI
from ruya.hatalar import YanitBozuk
from ruya.llm.client import LLMIstemcisi
from ruya.llm.talimatlar import talimat_oku
from ruya.schemas import (
    Atif,
    Baglam,
    CikarimSonucu,
    Eslesme,
    Getirilenler,
    Kullanim,
    Madde,
    Yorum,
    YorumBolumu,
)

TALIMAT = "sentez_v2"

# Modelin düşünme tokenları da bu sınıra dahildir.
EN_UZUN_CIKTI_TOKEN = 16000
# Uzun maddeler isteği şişirip yavaşlatır; atıf doğrulama yine tam metne bakar.
EN_UZUN_METIN_TR = 600
EN_UZUN_METIN_ASLI = 200


# --- Model yanıtının ham biçimi ---------------------------------------------


class _HamKaynak(BaseModel):
    """Modelin döndürdüğü tek atıf; doğrulama ``atiflari_dogrula``'da yapılır."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str
    alinti: str


class _HamBolum(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metin: str
    kaynaklar: list[_HamKaynak] = Field(default_factory=list)


class _HamYanit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bolumler: list[_HamBolum]
    bulunamayanlar: list[str] = Field(default_factory=list)


def _yanit_dogrula(veri: object) -> _HamYanit:
    """Ham JSON'u şemaya çevirir; biçim bozuksa ``YanitBozuk`` verir."""
    try:
        return _HamYanit.model_validate(veri)
    except ValidationError as hata:
        raise YanitBozuk(f"Sentez yanıtı şemaya uymuyor: {hata}") from hata


# --- Atıf doğrulama ---------------------------------------------------------


def _bosluklari_normalize(metin: str) -> str:
    """Satır sonlarını ve ardışık boşlukları tek boşluğa indirir."""
    return " ".join(metin.split())


def _baslik(madde: Madde) -> str:
    """Atıf başlığı maddeden gelir: ``<yazar> · <başlık ya da sembol>``."""
    ad = madde.baslik_asli or madde.sembol_tr or madde.entry_id
    return f"{madde.yazar} · {ad}"


def _alinti_dogrula(alinti: str, madde: Madde) -> str:
    """Alıntı madde metninde geçiyorsa normalize edilmiş hâlini, geçmiyorsa boş dize döndürür."""
    aranan = _bosluklari_normalize(alinti)
    if not aranan:
        return ""
    kaynaklar = [madde.metin_tr, madde.metin_asli]
    for kaynak in kaynaklar:
        if kaynak and aranan in _bosluklari_normalize(kaynak):
            return aranan
    return ""


def _bolumleri_cevir(ham: _HamYanit, maddeler: dict[str, Madde]) -> list[YorumBolumu]:
    """Ham bölümleri doğrulanmış ``YorumBolumu`` listesine çevirir; sıra korunur."""
    bolumler: list[YorumBolumu] = []
    for bolum in ham.bolumler:
        atiflar: list[Atif] = []
        for kaynak in bolum.kaynaklar:
            madde = maddeler.get(kaynak.entry_id)
            if madde is None:
                continue  # uydurma atıf: atılır
            atiflar.append(
                Atif(
                    entry_id=madde.entry_id,
                    baslik=_baslik(madde),
                    alinti=_alinti_dogrula(kaynak.alinti, madde),
                )
            )
        bolumler.append(YorumBolumu(metin=bolum.metin, atiflar=atiflar))
    return bolumler


def atiflari_dogrula(veri: object, maddeler: dict[str, Madde]) -> list[YorumBolumu]:
    """Model yanıtındaki atıfları maddelere karşı doğrular (docs/03, adım 4).

    - ``entry_id`` verilen maddelerden biri değilse atıf atılır.
    - ``alinti`` maddenin ``metin_tr`` ya da ``metin_asli`` metninde (boşluklar
      normalize edilerek) geçmiyorsa atıf korunur, alıntı boşaltılır.
    - ``baslik`` maddeden gelir, modelden alınmaz.
    """
    return _bolumleri_cevir(_yanit_dogrula(veri), maddeler)


# --- İstek ------------------------------------------------------------------


def _maddeler(getirilenler: Getirilenler) -> dict[str, Madde]:
    """Numaralanacak maddeler: sembol sırasına göre, entry_id'ye göre tekilleştirilmiş."""
    maddeler: dict[str, Madde] = {}
    for adaylar in getirilenler.values():
        for aday in adaylar:
            maddeler.setdefault(aday.madde.entry_id, aday.madde)
    return maddeler


def _baglam_metni(baglam: Baglam | None) -> str:
    if baglam is None:
        return "Bağlam verilmedi."
    parcalar = [f"{alan}: {deger}" for alan, deger in baglam.model_dump(exclude_none=True).items()]
    return "Bağlam: " + ", ".join(parcalar) if parcalar else "Bağlam verilmedi."


def _maddesi_olanlar(eslesmeler: list[Eslesme], getirilenler: Getirilenler) -> list[Eslesme]:
    """Maddesi olan semboller; maddesi olmayanlar istekte listelenmez (İG-31)."""
    return [
        eslesme
        for eslesme in eslesmeler
        if eslesme.symbol_id is not None and getirilenler.get(eslesme.symbol_id)
    ]


def _kullanici_mesaji(
    eslesmeler: list[Eslesme],
    maddeler: dict[str, Madde],
    baglam: Baglam | None,
) -> str:
    """Semboller, bağlam ve numaralı kaynaklar; rüya metni bu adıma gelmez."""
    satirlar = ["Rüyadaki semboller:"]
    for eslesme in eslesmeler:
        sembol = eslesme.sembol
        ekler = []
        if sembol.nitelikler:
            ekler.append("nitelikler: " + ", ".join(sembol.nitelikler))
        if sembol.eylem:
            ekler.append("eylem: " + sembol.eylem)
        if sembol.duygu:
            ekler.append("duygu: " + sembol.duygu)
        son = f" ({'; '.join(ekler)})" if ekler else ""
        satirlar.append(f"- {sembol.yalin}{son}")
    satirlar.append("")
    satirlar.append(_baglam_metni(baglam))
    satirlar.append("")
    satirlar.append("Kaynaklar:")
    for numara, madde in enumerate(maddeler.values(), start=1):
        satirlar.append(f"[K{numara}] {madde.entry_id} · {_baslik(madde)}")
        if madde.metin_tr:
            satirlar.append(madde.metin_tr[:EN_UZUN_METIN_TR])
        satirlar.append(madde.metin_asli[:EN_UZUN_METIN_ASLI])
        satirlar.append("")
    return "\n".join(satirlar).rstrip()


def _istek_kur(
    eslesmeler: list[Eslesme],
    maddeler: dict[str, Madde],
    baglam: Baglam | None,
) -> dict[str, Any]:
    """OpenAI uyumlu sohbet gövdesi: sabit sistem talimatı başta, kaynaklar sonda."""
    return {
        "model": MODEL_SENTEZ,
        "max_tokens": EN_UZUN_CIKTI_TOKEN,
        "messages": [
            {"role": "system", "content": talimat_oku(TALIMAT)},
            {
                "role": "user",
                "content": _kullanici_mesaji(eslesmeler, maddeler, baglam),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "sentez",
                "schema": _HamYanit.model_json_schema(),
                "strict": True,
            },
        },
    }


# --- Sentez -----------------------------------------------------------------


def _bulunamayanlar(
    model_verdigi: list[str],
    eslesmeler: list[Eslesme],
    getirilenler: Getirilenler,
) -> list[str]:
    """Modelin listesi + eşleşmeyen ya da maddesi olmayan semboller; tekrarsız, sıra korunur."""
    sonuc: list[str] = []
    for ad in model_verdigi:
        if ad not in sonuc:
            sonuc.append(ad)
    for eslesme in eslesmeler:
        ad = eslesme.sembol.yalin
        maddesi_yok = eslesme.symbol_id is None or not getirilenler.get(eslesme.symbol_id)
        if maddesi_yok and ad not in sonuc:
            sonuc.append(ad)
    return sonuc


def synthesize(
    cikarim: CikarimSonucu,
    eslesmeler: list[Eslesme],
    getirilenler: Getirilenler,
    baglam: Baglam | None,
    istemci: LLMIstemcisi,
) -> tuple[Yorum, Kullanim]:
    """Kaynaklı Türkçe yorumu üretir; atıfları kodda doğrular."""
    maddeler = _maddeler(getirilenler)
    if not maddeler:
        # Maddesi olmayan semboller için modele gitmeye değmez (İG-31).
        yorum = Yorum(
            bolumler=[],
            bulunamayanlar=_bulunamayanlar([], eslesmeler, getirilenler),
            guvenlik_notu=GUVENLIK_NOTU if cikarim.hassas_icerik else None,
            uyari=UYARI_METNI,
        )
        return yorum, Kullanim(model=MODEL_SENTEZ)
    yanit = istemci.mesaj(
        _istek_kur(_maddesi_olanlar(eslesmeler, getirilenler), maddeler, baglam),
        ruya_icerir=True,
    )
    ham = _yanit_dogrula(yanit.json())
    yorum = Yorum(
        bolumler=_bolumleri_cevir(ham, maddeler),
        bulunamayanlar=_bulunamayanlar(ham.bulunamayanlar, eslesmeler, getirilenler),
        guvenlik_notu=GUVENLIK_NOTU if cikarim.hassas_icerik else None,
        uyari=UYARI_METNI,
    )
    return yorum, yanit.kullanim
