"""Veri sözleşmeleri: modüller arasında dolaşan bütün nesneler burada tanımlanır.

- Veri hattı: Madde (entries.jsonl), SymbolKaydi (sozluk/symbols.json)
- Sorgu boru hattı: RuyaGirdisi → CikarimSonucu → Eslesme → Aday → Yorum → SorguKaydi
- Değerlendirme: TestOrnegi (eval/dataset/*.jsonl)

Şemaların anlatımı: docs/02-veri-kaynaklari-ve-semasi.md (bölüm 4) ve
docs/03-mimari.md (bölüm 3). Bir alan değişirse önce belge, sonra bu dosya güncellenir.
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator

# --- Ortak türler -----------------------------------------------------------

SYMBOL_ID_DESENI = r"^[a-z0-9]+(_[a-z0-9]+)*$"  # ASCII, küçük harf: yilan, olmus_baba
ENTRY_ID_DESENI = r"^[a-z0-9_]+:[a-z0-9_]+$"  # <kaynak>:<yerel kimlik>, ör. nablusi:0412

Gelenek = Literal["islami_klasik", "bati_halk", "psikanalitik"]
Dil = Literal["ar", "en", "de", "tr"]
Kapsam = Literal["kisi", "vilayet", "padisah"]
RuyaTuru = Literal["rahmani", "seytani", "nefsani"]
EslemeYontemi = Literal["birebir", "kok", "vektor", "yok"]
Adim = Literal["cikarim", "esleme", "getirme", "sentez"]

SymbolId = str  # SYMBOL_ID_DESENI'ne uyan bir dize


class _Sema(BaseModel):
    """Bütün şemaların ortak ayarı: bilinmeyen alan kabul edilmez."""

    model_config = ConfigDict(extra="forbid")


# --- Veri hattı: madde kaydı (entries.jsonl) --------------------------------


class Konum(_Sema):
    """Maddenin kaynaktaki yeri. entry_id satır numarasından türetilir."""

    bab: str | None = None
    sayfa: str | None = None
    satir: int = Field(ge=1)


class CeviriBilgisi(_Sema):
    yontem: Literal["llm", "elle"]
    model: str | None = None
    tarih: dt.date
    gozden_gecirildi: bool = False


class Kosul(_Sema):
    """Bir maddedeki koşullu yorum: "kadın görürse …" (Aşama 3)."""

    kosul: dict[str, str]  # ör. {"cinsiyet": "kadin"}, {"renk": "siyah"}
    yorum_tr: str
    otorite: str | None = None


class Madde(_Sema):
    """Korpustaki tek bir madde. interim/*.jsonl ve processed/entries.jsonl satırı."""

    entry_id: str = Field(pattern=ENTRY_ID_DESENI)
    kaynak: str = Field(pattern=r"^[a-z0-9_]+$")
    eser: str
    yazar: str
    gelenek: Gelenek
    dil: Dil
    lisans: str = Field(min_length=1)  # hiçbir zaman boş olamaz (V1, İOG-06)
    atif_notu: str | None = None  # İbn Sirin: "Nispeti sahih değil (OpenITI metadatası)"
    konum: Konum
    baslik_asli: str | None = None  # alt paragraflarda yok
    # Çevirinin önerdiği ham sembol adları; sözlük kimliği (symbol_id) değildir.
    sembol_ar: str | None = None
    sembol_tr: str | None = None
    ust_madde_id: str | None = Field(default=None, pattern=ENTRY_ID_DESENI)
    symbol_ids: list[SymbolId] = Field(default_factory=list)
    metin_asli: str = Field(min_length=1)
    metin_tr: str | None = None  # çeviri; Türkçe kaynaklarda ya da çevrilmeden önce None
    ceviri: CeviriBilgisi | None = None
    # Aşama 3'te doldurulur; o zamana kadar None kalır.
    kosullar: list[Kosul] | None = None
    yontem: list[str] | None = None  # ayet, hadis, mesel, kok, zit, ebced
    kapsam: Kapsam | None = None

    @field_validator("lisans")
    @classmethod
    def _lisans_bos_olamaz(cls, deger: str) -> str:
        if not deger.strip():
            raise ValueError("lisans alanı boş olamaz")
        return deger

    @field_validator("symbol_ids")
    @classmethod
    def _symbol_id_bicimi(cls, degerler: list[str]) -> list[str]:
        for deger in degerler:
            _symbol_id_dogrula(deger)
        return degerler

    @model_validator(mode="after")
    def _kimlikler_tutarli(self) -> Madde:
        on_ek = self.kaynak + ":"
        if not self.entry_id.startswith(on_ek):
            raise ValueError(f"entry_id '{self.kaynak}:' ile başlamalı: {self.entry_id}")
        if self.ust_madde_id is not None and not self.ust_madde_id.startswith(on_ek):
            raise ValueError("ust_madde_id aynı kaynaktan olmalı")
        if self.ust_madde_id == self.entry_id:
            raise ValueError("madde kendisinin üst maddesi olamaz")
        return self

    @property
    def baslikli_mi(self) -> bool:
        """Başlıklı madde mi, yoksa bir başlığın alt paragrafı mı?"""
        return self.ust_madde_id is None


def _symbol_id_dogrula(deger: str) -> None:
    if not re.fullmatch(SYMBOL_ID_DESENI, deger):
        raise ValueError(f"geçersiz symbol_id (ASCII, küçük harf, alt çizgi): {deger!r}")


# --- Veri hattı: kanonik sembol indeksi (sozluk/symbols.json) ---------------


class SymbolKaydi(_Sema):
    ad_tr: str
    varyantlar_tr: list[str] = Field(default_factory=list)
    ar: list[str] = Field(default_factory=list)
    en: list[str] = Field(default_factory=list)
    bab_kategorisi: str | None = None
    hvdc_kategorisi: str | None = None
    ilgili: list[SymbolId] = Field(default_factory=list)
    gozden_gecirildi: bool = False  # True olmayan sembol MVP'de kullanılmaz


class SozlukDosyasi(RootModel[dict[SymbolId, SymbolKaydi]]):
    """symbols.json dosyasının tamamı: {symbol_id: SymbolKaydi}."""

    @model_validator(mode="after")
    def _anahtarlar_gecerli(self) -> SozlukDosyasi:
        for symbol_id, kayit in self.root.items():
            _symbol_id_dogrula(symbol_id)
            for ilgili in kayit.ilgili:
                _symbol_id_dogrula(ilgili)  # sözlükte henüz olmayabilir
        return self


# --- Sorgu boru hattı -------------------------------------------------------


class Baglam(_Sema):
    """Kullanıcının isteğe bağlı verdiği bağlam (İG-02). Sistem bunları tahmin etmez."""

    cinsiyet: Literal["kadin", "erkek"] | None = None
    medeni_hal: Literal["evli", "bekar"] | None = None
    mevsim: Literal["ilkbahar", "yaz", "sonbahar", "kis"] | None = None
    gurbette: bool | None = None


class RuyaGirdisi(_Sema):
    metin: str = Field(min_length=1, max_length=3000)  # İG-01
    baglam: Baglam | None = None
    gelenekler: list[Gelenek] | None = None  # None: hepsi (İG-03)


class Sembol(_Sema):
    """Adım 1'in çıkardığı bir sembol."""

    yalin: str  # yalın ve küçük harf: "yılan"
    nitelikler: list[str] = Field(default_factory=list)  # siyah, büyük, ölü
    eylem: str | None = None  # gördü, öldürdü, ısırıldı
    duygu: str | None = None  # korku, sevinç
    olumsuz: bool = False  # "yılan görmedim" → True; sonraki adımlara geçmez
    ham_ifade: str  # metinde geçtiği biçim; rüya metninin parçası, loglanmaz


class CikarimSonucu(_Sema):
    semboller: list[Sembol]
    ruya_turu_ipucu: RuyaTuru | None = None  # İG-14: etiket, hüküm değil
    hassas_icerik: bool = False  # docs/07, bölüm 3: güvenlik ağı

    @property
    def gecerli_semboller(self) -> list[Sembol]:
        """Olumsuzlanmamış semboller: eşlemeye bunlar gider."""
        return [s for s in self.semboller if not s.olumsuz]


class Eslesme(_Sema):
    """Adım 2'nin çıktısı: bir sembolün kanonik kimliğe eşlenmesi."""

    sembol: Sembol
    symbol_id: SymbolId | None
    yontem: EslemeYontemi
    guven: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _yontem_ve_kimlik(self) -> Eslesme:
        if (self.yontem == "yok") != (self.symbol_id is None):
            raise ValueError("yontem 'yok' ise symbol_id None olmalı, değilse dolu olmalı")
        return self


class Aday(_Sema):
    """Adım 3'ün getirdiği bir madde, sıralama skoru ve gerekçesiyle (İG-42)."""

    madde: Madde
    skor: float
    gerekceler: list[str] = Field(default_factory=list)  # "nitelik:siyah", "baslikli"


Getirilenler = dict[SymbolId, list[Aday]]


class Atif(_Sema):
    """Sentezdeki bir cümlenin dayandığı kaynak parça (kodda doğrulanmış atıf; docs/03, adım 4)."""

    entry_id: str
    baslik: str  # "Nablusi · حية (yılan)"
    alinti: str  # cited_text


class YorumBolumu(_Sema):
    metin: str
    atiflar: list[Atif] = Field(default_factory=list)


class Yorum(_Sema):
    """Adım 4'ün çıktısı."""

    bolumler: list[YorumBolumu]
    bulunamayanlar: list[str] = Field(default_factory=list)  # İG-31
    guvenlik_notu: str | None = None  # hassas içerikte yanıtın başına
    uyari: str  # İG-36: her yanıtın altında

    @property
    def metin(self) -> str:
        return "".join(b.metin for b in self.bolumler)


class Kullanim(_Sema):
    """Bir LLM çağrısının token ve maliyet bilgisi."""

    model: str
    girdi_token: int = 0
    cikti_token: int = 0
    onbellek_okuma_token: int = 0
    onbellek_yazma_token: int = 0
    maliyet_usd: float = 0.0
    disk_onbelleginden: bool = False  # True ise API'ye gidilmedi, maliyet 0


class AdimOlcumu(_Sema):
    adim: Adim
    sure_sn: float = Field(ge=0.0)
    kullanim: Kullanim | None = None  # yalnızca LLM çağıran adımlarda
    talimat: str | None = None  # ör. "cikarim_v1"


class SorguKaydi(_Sema):
    """Bir rüyanın boru hattındaki bütün izi. Arayüz ve değerlendirme aynı nesneyi kullanır."""

    zaman: dt.datetime
    girdi: RuyaGirdisi
    cikarim: CikarimSonucu | None = None
    eslesmeler: list[Eslesme] = Field(default_factory=list)
    getirilenler: Getirilenler = Field(default_factory=dict)
    yorum: Yorum | None = None
    atlanan_semboller: list[str] = Field(default_factory=list)  # en_fazla_sembol aşılınca
    mesaj: str | None = None  # "Rüyanda tabir edilecek bir sembol bulamadım" gibi
    olcumler: list[AdimOlcumu] = Field(default_factory=list)

    @property
    def toplam_sure_sn(self) -> float:
        return sum(o.sure_sn for o in self.olcumler)

    @property
    def toplam_maliyet_usd(self) -> float:
        return sum(o.kullanim.maliyet_usd for o in self.olcumler if o.kullanim)

    def log_kaydi(self) -> dict[str, Any]:
        """logs/sorgular.jsonl satırı. **Rüya metni ve onun parçaları yazılmaz** (İOG-07)."""
        return {
            "zaman": self.zaman.isoformat(),
            "karakter_sayisi": len(self.girdi.metin),
            "baglam_verildi": self.girdi.baglam is not None,
            "gelenekler": self.girdi.gelenekler,
            "sembol_sayisi": len(self.cikarim.semboller) if self.cikarim else 0,
            "hassas_icerik": self.cikarim.hassas_icerik if self.cikarim else False,
            "eslesmeler": [
                {"symbol_id": e.symbol_id, "yontem": e.yontem, "guven": e.guven}
                for e in self.eslesmeler
            ],
            "madde_sayilari": {sid: len(adaylar) for sid, adaylar in self.getirilenler.items()},
            "atlanan_sembol_sayisi": len(self.atlanan_semboller),
            "olcumler": [o.model_dump(mode="json") for o in self.olcumler],
            "toplam_sure_sn": round(self.toplam_sure_sn, 3),
            "toplam_maliyet_usd": round(self.toplam_maliyet_usd, 6),
        }


# --- Değerlendirme: test seti kaydı (eval/dataset/ruyalar_v1.jsonl) ---------


class TestOrnegi(_Sema):
    """Test setindeki bir rüya (docs/06, bölüm 1)."""

    __test__ = False  # pytest bu sınıfı test sınıfı sanmasın

    id: str = Field(pattern=r"^r\d{3,}$")
    metin: str = Field(min_length=1)
    baglam: Baglam | None = None
    beklenen_semboller: list[SymbolId] = Field(default_factory=list)
    beklenen_nitelikler: dict[SymbolId, list[str]] = Field(default_factory=dict)
    beklenen_duygular: list[str] = Field(default_factory=list)
    olmamasi_gerekenler: list[SymbolId] = Field(default_factory=list)
    beklenen_maddeler: dict[SymbolId, list[str]] = Field(default_factory=dict)
    notlar: str | None = None
