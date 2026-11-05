"""Orkestrasyon: dört adımı sırayla çalıştırır ve her adımın izini SorguKaydi'na yazar.

Adımlar modül üzerinden çağrılır (``extract.extract`` gibi); böylece testlerde tek tek
sahteleriyle değiştirilebilir. Dış dünyaya (API, depo, sözlük) erişim yalnızca
``Bagimliliklar`` üzerinden olur.
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import TypeVar

from ruya.config import Ayarlar, ayarlar
from ruya.dosya import jsonl_oku
from ruya.etik import SEMBOL_YOK_MESAJI
from ruya.index.build_symbols import sozlugu_yukle, varyant_tablosu
from ruya.index.build_vectors import HibritIndeks
from ruya.index.store import BellekDeposu, MaddeDeposu
from ruya.llm.client import LLMIstemcisi
from ruya.pipeline import extract, hibrit, retrieve, synthesize
from ruya.pipeline import map as esleme
from ruya.schemas import AdimOlcumu, Eslesme, Madde, RuyaGirdisi, SorguKaydi

T = TypeVar("T")

_log = logging.getLogger(__name__)


@dataclass
class Bagimliliklar:
    """Boru hattının dış dünyaya açılan bütün kapıları. Notebook ve arayüz bir kez kurar."""

    istemci: LLMIstemcisi
    varyantlar: dict[str, str]  # index.build_symbols.varyant_tablosu
    depo: MaddeDeposu
    hibrit: HibritIndeks | None = None  # Aşama 3: varsa getirme hibrit yapılır
    ayar: Ayarlar = field(default_factory=ayarlar)


def varsayilan_bagimliliklar(ayar: Ayarlar | None = None) -> Bagimliliklar:
    """Gerçek bağımlılıkları kurar: sözlük (git), maddeler (data/), LLM istemcisi.

    Arayüz notebook'u ve değerlendirme betiği bunu çağırır; testler kendi sahtelerini kurar.
    """
    ayar = ayar or ayarlar()
    sozluk = sozlugu_yukle()
    maddeler = list(jsonl_oku(ayar.maddeler_dosyasi, Madde))
    hibrit_indeks = _hibrit_indeks_yukle(ayar, maddeler)
    return Bagimliliklar(
        istemci=LLMIstemcisi(ayar),
        varyantlar=varyant_tablosu(sozluk),
        depo=BellekDeposu(maddeler),
        hibrit=hibrit_indeks,
        ayar=ayar,
    )


def _hibrit_indeks_yukle(ayar: Ayarlar, maddeler: list[Madde]) -> HibritIndeks | None:
    """Hibrit indeksi okur; indeks yoksa ya da başka bir madde kümesine aitse None döner."""
    try:
        return HibritIndeks.yukle(ayar.veri("index", "hibrit"), maddeler)
    except (FileNotFoundError, ValueError) as hata:
        _log.warning("Hibrit indeks yüklenemedi, getirme sözlük/vektör ile yapılacak: %s", hata)
        return None


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

    # 2 · Eşleme
    eslesmeler, sure = _zamanla(esleme.map_symbols, semboller, bag.varyantlar)
    kayit.olcumler.append(AdimOlcumu(adim="esleme", sure_sn=sure))
    eslesmeler = esleme.genel_fiilleri_ele(eslesmeler)
    if not eslesmeler:
        kayit.mesaj = SEMBOL_YOK_MESAJI
        return kayit

    # Sınır eşlemeden sonra uygulanır: eşlenemeyen semboller sınırı kullanmaz.
    sinir = bag.ayar.en_fazla_sembol
    secilenler: list[Eslesme] = []
    atlananlar: list[Eslesme] = []
    eslenen = 0
    for es in eslesmeler:
        if es.symbol_id is not None:
            eslenen += 1
            if eslenen > sinir:
                atlananlar.append(es)
                continue
        secilenler.append(es)
    eslesmeler = secilenler
    kayit.eslesmeler = eslesmeler
    kayit.atlanan_semboller = [e.sembol.yalin for e in atlananlar]

    # 3 · Getirme
    if bag.hibrit is not None:
        getirilenler, sure = _zamanla(
            partial(
                hibrit.hibrit_getir,
                eslesmeler,
                bag.depo,
                bag.hibrit,
                bag.istemci,
                baglam=girdi.baglam,
                gelenekler=girdi.gelenekler,
                n=bag.ayar.kaynak_basina_n,
            )
        )
    else:
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
