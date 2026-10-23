"""Orkestrasyon: dört adımı sırayla çalıştırır ve her adımın izini SorguKaydi'na yazar.

Adımlar modül üzerinden çağrılır (``extract.extract`` gibi); böylece testlerde tek tek
sahteleriyle değiştirilebilir. Dış dünyaya (API, depo, sözlük) erişim yalnızca
``Bagimliliklar`` üzerinden olur.
"""

from __future__ import annotations

import datetime as dt
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

from ruya.config import Ayarlar, ayarlar
from ruya.dosya import jsonl_oku
from ruya.etik import SEMBOL_YOK_MESAJI
from ruya.index.build_symbols import sozlugu_yukle, varyant_tablosu
from ruya.index.store import BellekDeposu, MaddeDeposu, VektorArayici
from ruya.llm.client import LLMIstemcisi
from ruya.pipeline import extract, retrieve, synthesize
from ruya.pipeline import map as esleme
from ruya.schemas import AdimOlcumu, Madde, RuyaGirdisi, SorguKaydi

T = TypeVar("T")


@dataclass
class Bagimliliklar:
    """Boru hattının dış dünyaya açılan bütün kapıları. Notebook ve arayüz bir kez kurar."""

    istemci: LLMIstemcisi
    varyantlar: dict[str, str]  # index.build_symbols.varyant_tablosu
    depo: MaddeDeposu
    vektor: VektorArayici | None = None  # Aşama 2
    ayar: Ayarlar = field(default_factory=ayarlar)


def varsayilan_bagimliliklar(ayar: Ayarlar | None = None) -> Bagimliliklar:
    """Colab'deki gerçek bağımlılıkları kurar: sözlük (git), maddeler (Drive), Claude istemcisi.

    Arayüz notebook'u ve değerlendirme betiği bunu çağırır; testler kendi sahtelerini kurar.
    """
    ayar = ayar or ayarlar()
    sozluk = sozlugu_yukle()
    maddeler = list(jsonl_oku(ayar.maddeler_dosyasi, Madde))
    return Bagimliliklar(
        istemci=LLMIstemcisi(ayar),
        varyantlar=varyant_tablosu(sozluk),
        depo=BellekDeposu(maddeler),
        ayar=ayar,
    )


def _zamanla(islev: Callable[..., T], *argumanlar: object) -> tuple[T, float]:
    baslangic = time.perf_counter()
    sonuc = islev(*argumanlar)
    return sonuc, time.perf_counter() - baslangic


def yorumla(girdi: RuyaGirdisi, bag: Bagimliliklar) -> SorguKaydi:
    """Bir rüyayı uçtan uca yorumlar. API hataları (ModelReddetti vb.) çağırana iletilir."""
    kayit = SorguKaydi(zaman=dt.datetime.now(dt.UTC), girdi=girdi)

    # 1 · Çıkarım
    (cikarim, kullanim), sure = _zamanla(extract.extract, girdi, bag.istemci)
    kayit.cikarim = cikarim
    kayit.olcumler.append(
        AdimOlcumu(adim="cikarim", sure_sn=sure, kullanim=kullanim, talimat=extract.TALIMAT)
    )
    semboller = cikarim.gecerli_semboller
    if not semboller:
        kayit.mesaj = SEMBOL_YOK_MESAJI
        return kayit
    sinir = bag.ayar.en_fazla_sembol
    semboller, atlananlar = semboller[:sinir], semboller[sinir:]
    kayit.atlanan_semboller = [s.yalin for s in atlananlar]

    # 2 · Eşleme
    eslesmeler, sure = _zamanla(esleme.map_symbols, semboller, bag.varyantlar, bag.vektor)
    kayit.eslesmeler = eslesmeler
    kayit.olcumler.append(AdimOlcumu(adim="esleme", sure_sn=sure))

    # 3 · Getirme
    getirilenler, sure = _zamanla(
        retrieve.retrieve,
        eslesmeler,
        bag.depo,
        girdi.baglam,
        girdi.gelenekler,
        bag.ayar.kaynak_basina_n,
    )
    kayit.getirilenler = getirilenler
    kayit.olcumler.append(AdimOlcumu(adim="getirme", sure_sn=sure))

    # 4 · Sentez
    (yorum, kullanim), sure = _zamanla(
        synthesize.synthesize, cikarim, eslesmeler, getirilenler, girdi.baglam, bag.istemci
    )
    kayit.yorum = yorum
    kayit.olcumler.append(
        AdimOlcumu(adim="sentez", sure_sn=sure, kullanim=kullanim, talimat=synthesize.TALIMAT)
    )
    return kayit
