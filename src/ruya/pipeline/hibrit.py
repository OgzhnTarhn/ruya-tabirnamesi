"""Adım 3 · Hibrit getirme: sözlük + BM25 + vektör + HyDE, RRF ile birleştirme,
reranker ve eşik (docs/13-hibrit-getirme.md).

- ``rrf``: Reciprocal Rank Fusion; her liste için 1/(k + sıra) toplanır (sıra 1'den başlar).
- ``getirme_sorgusu``: bir sembolden arama sorgusu üretir; HyDE metni ayrıca aranır.
- ``hibrit_getir``: dört kaynağın adaylarını RRF ile birleştirir, reranker ile sıralar ve
  eşiğin altındaki adayları atar.
- ``siralama``: deneyler için eşiksiz ve kaynak sınırsız sıralama (docs/15 K4).
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Protocol

from ruya.config import GETIRME_ESIGI
from ruya.hatalar import LLMHatasi
from ruya.index.parcalar import Parca
from ruya.index.store import MaddeDeposu
from ruya.schemas import (
    Aday,
    Baglam,
    Eslesme,
    Gelenek,
    Getirilenler,
    Madde,
    Sembol,
    getirme_anahtari,
)
from ruya.text.turkce import arama_terimleri

_log = logging.getLogger(__name__)

RRF_K = 60
BM25_K = 40
VEKTOR_K = 40
EN_FAZLA_ADAY = 40
KOSUL_PUANI = 0.1

# Getirmenin dört kolu; deneylerde bunların bir alt kümesi seçilir (docs/15 K4).
TUM_KOLLAR = frozenset({"sozluk", "bm25", "vektor", "hyde"})

# Bağlam koşulunda karşılaştırılan alanlar (Baglam'daki isimleriyle).
_KOSUL_ALANLARI = ("cinsiyet", "medeni_hal", "mevsim")


class _Indeks(Protocol):
    """Hibrit indeksin getirmenin kullandığı üç yöntemi."""

    def parca_listesi(self, entry_id: str) -> list[Parca]: ...

    def bm25_ara(self, terimler: Iterable[str], k: int = 10) -> list[tuple[Parca, float]]: ...

    def vektor_ara(self, sorgu: object, k: int = 10) -> list[tuple[Parca, float]]: ...


class _Istemci(Protocol):
    """LLM istemcisinin gömme ve yeniden sıralama yöntemleri."""

    def gom(self, metinler: list[str], ruya_icerir: bool = False) -> list[list[float]]: ...

    def yeniden_sirala(
        self, sorgu: str, belgeler: list[str], ruya_icerir: bool = False
    ) -> list[tuple[int, float]]: ...


def rrf(listeler: list[list[str]], k: int = RRF_K) -> dict[str, float]:
    """Reciprocal Rank Fusion: her belge için 1/(k + sıra) katkılarını toplar."""
    skorlar: dict[str, float] = {}
    for liste in listeler:
        for sira, belge in enumerate(liste, start=1):
            skorlar[belge] = skorlar.get(belge, 0.0) + 1.0 / (k + sira)
    return skorlar


def getirme_sorgusu(sembol: Sembol) -> str:
    """Bir sembol için arama sorgusu: "Rüyada <nitelikler> <yalın> görmek (eylem)"."""
    parcalar = [*sembol.nitelikler, sembol.yalin]
    sorgu = "Rüyada " + " ".join(parcalar) + " görmek"
    if sembol.eylem:
        sorgu += f" ({sembol.eylem})"
    return sorgu


def _gommeler(
    eslesmeler: list[Eslesme], istemci: _Istemci, hyde: bool = True
) -> dict[str, list[float]]:
    """Bütün sorguları ve HyDE metinlerini tek çağrıda gömer; metin → vektör döndürür.

    ``hyde=False`` iken HyDE metinleri gömülmez. Gömme geçidi hata verirse vektör araması
    atlanır: boş sözlük döner. Uyarıya rüya metni yazılmaz (İOG-07).
    """
    metinler: list[str] = []
    for eslesme in eslesmeler:
        metinler.append(getirme_sorgusu(eslesme.sembol))
        if hyde and eslesme.sembol.hyde:
            metinler.append(eslesme.sembol.hyde)
    if not metinler:
        return {}

    try:
        vektorler = istemci.gom(metinler, ruya_icerir=True)
    except LLMHatasi as hata:
        _log.warning("Gömme alınamadı, vektör araması atlanıyor: %s", type(hata).__name__)
        return {}

    return {metin: list(vektor) for metin, vektor in zip(metinler, vektorler, strict=False)}


def _gelenek_uygun(entry_id: str, depo: MaddeDeposu, gelenekler: list[Gelenek] | None) -> bool:
    """Gelenek filtresi: None yalnızca psikanalitik maddeleri dışarıda bırakır."""
    try:
        gelenek = depo.madde(entry_id).gelenek
    except KeyError:
        return False
    if gelenekler is None:
        return gelenek != "psikanalitik"
    return gelenek in gelenekler


def _listeler(
    eslesme: Eslesme,
    depo: MaddeDeposu,
    indeks: _Indeks,
    gelenekler: list[Gelenek] | None,
    gommeler: dict[str, list[float]],
) -> tuple[dict[str, list[str]], dict[str, Parca]]:
    """Bir eşleşme için liste adı → sıralı entry_id'ler ve entry başına en iyi parça."""
    listeler: dict[str, list[str]] = {}
    parcalar: dict[str, Parca] = {}

    def _vurulari_ekle(ad: str, vurular: list[tuple[Parca, float]]) -> None:
        entry_idler: list[str] = []
        for parca, _skor in vurular:
            if parca.entry_id in entry_idler:
                continue  # parça vuruları madde düzeyinde birleşir; ilk (en iyi) parça kalır
            if not _gelenek_uygun(parca.entry_id, depo, gelenekler):
                continue
            entry_idler.append(parca.entry_id)
            parcalar.setdefault(parca.entry_id, parca)
        listeler[ad] = entry_idler

    if eslesme.symbol_id is not None:
        listeler["sozluk"] = [
            madde.entry_id
            for madde in depo.sembolun_maddeleri(eslesme.symbol_id)
            if _gelenek_uygun(madde.entry_id, depo, gelenekler)
        ]

    sorgu = getirme_sorgusu(eslesme.sembol)
    _vurulari_ekle("bm25", indeks.bm25_ara(arama_terimleri(sorgu), BM25_K))

    vektor = gommeler.get(sorgu)
    if vektor is not None:
        _vurulari_ekle("vektor", indeks.vektor_ara(vektor, VEKTOR_K))

    hyde = eslesme.sembol.hyde
    if hyde:
        hyde_vektoru = gommeler.get(hyde)
        if hyde_vektoru is not None:
            _vurulari_ekle("hyde", indeks.vektor_ara(hyde_vektoru, VEKTOR_K))

    return listeler, parcalar


def _kosul_skoru(madde: Madde, baglam: Baglam | None) -> tuple[float, list[str]]:
    """Bağlam koşullarına göre skor düzeltmesi ve gerekçeleri."""
    if baglam is None:
        return 0.0, []

    skor = 0.0
    gerekceler: list[str] = []
    for alan in _KOSUL_ALANLARI:
        deger = getattr(baglam, alan)
        if deger is None:
            continue
        # Alan başına tek katkı: eşleşen bir koşul varsa artı, yoksa farklı bir koşul eksi.
        degerler = [
            kosul.kosul[alan]
            for kosul in madde.kosullar or []
            if alan in kosul.kosul
        ]
        if deger in degerler:
            skor += KOSUL_PUANI
            gerekceler.append(f"kosul:{alan}")
        elif degerler:
            skor -= KOSUL_PUANI
    return skor, gerekceler


def _parca_bul(entry_id: str, parcalar: dict[str, Parca], indeks: _Indeks) -> Parca | None:
    """Entry'nin en iyi parçası; vuruş yoksa indeksteki ilk parçası."""
    parca = parcalar.get(entry_id)
    if parca is not None:
        return parca
    parca_listesi = indeks.parca_listesi(entry_id)
    return parca_listesi[0] if parca_listesi else None


def _gerekceler(entry_id: str, listeler: dict[str, list[str]]) -> list[str]:
    """Entry'yi bulan liste adları (sozluk, bm25, vektor, hyde)."""
    return [ad for ad, entry_idler in listeler.items() if entry_id in entry_idler]


def _kaynak_sinirla(adaylar: list[Aday], n: int) -> list[Aday]:
    """Her kaynaktan en fazla ``n`` aday bırakır (İG-22)."""
    secilen: list[Aday] = []
    kaynak_sayaci: dict[str, int] = {}
    for aday in adaylar:
        kaynak = aday.madde.kaynak
        if kaynak_sayaci.get(kaynak, 0) >= n:
            continue
        kaynak_sayaci[kaynak] = kaynak_sayaci.get(kaynak, 0) + 1
        secilen.append(aday)
    return secilen


def _yedek_sec(
    adaylar: list[tuple[str, float]],
    listeler: dict[str, list[str]],
    parcalar: dict[str, Parca],
    depo: MaddeDeposu,
    indeks: _Indeks,
    n: int,
) -> list[Aday]:
    """Reranker yokken: yalnızca sözlük/BM25 adayları, RRF sırasıyla, eşiksiz."""
    secilen: list[Aday] = []
    for entry_id, skor in adaylar:
        if not any(entry_id in listeler.get(ad, []) for ad in ("sozluk", "bm25")):
            continue
        parca = _parca_bul(entry_id, parcalar, indeks)
        gerekceler = _gerekceler(entry_id, listeler)
        gerekceler.append("rerank-yok")
        secilen.append(
            Aday(
                madde=depo.madde(entry_id),
                skor=skor,
                pasaj=parca.metin if parca is not None else None,
                gerekceler=gerekceler,
            )
        )
    return _kaynak_sinirla(secilen, n)


def _rerank_puanlari(
    eslesme: Eslesme,
    adaylar: list[tuple[str, float]],
    parcalar: dict[str, Parca],
    indeks: _Indeks,
    istemci: _Istemci,
) -> list[tuple[str, Parca, float]] | None:
    """Adayları reranker ile puanlar: (entry_id, parça, puan) listesi.

    Parçası olmayan adaylar atlanır. Reranker hata verirse ``None`` döner (çağıran RRF
    sırasına düşer).
    """
    belgeler: list[str] = []
    parca_ile: list[tuple[str, Parca]] = []
    for entry_id, _skor in adaylar:
        parca = _parca_bul(entry_id, parcalar, indeks)
        if parca is None:
            continue  # parçası olmayan aday rerankere gidemez
        belgeler.append(parca.baglamli_metin)
        parca_ile.append((entry_id, parca))

    if not belgeler:
        return []

    sorgu = getirme_sorgusu(eslesme.sembol)
    try:
        puanlar = istemci.yeniden_sirala(sorgu, belgeler, ruya_icerir=True)
    except LLMHatasi as hata:
        _log.warning(
            "Yeniden sıralama yapılamadı, RRF sırası kullanılıyor: %s", type(hata).__name__
        )
        return None

    puan_sozlugu = {sira: puan for sira, puan in puanlar}
    return [
        (entry_id, parca, puan_sozlugu[sira])
        for sira, (entry_id, parca) in enumerate(parca_ile)
        if sira in puan_sozlugu
    ]


def _sec(
    eslesme: Eslesme,
    listeler: dict[str, list[str]],
    parcalar: dict[str, Parca],
    depo: MaddeDeposu,
    indeks: _Indeks,
    istemci: _Istemci,
    baglam: Baglam | None,
    n: int,
    esik: float,
) -> list[Aday]:
    """RRF ile adayları seçer, reranker ile sıralar, eşiği ve kaynak sınırını uygular."""
    skorlar = rrf(list(listeler.values()))
    if not skorlar:
        return []
    adaylar = sorted(skorlar.items(), key=lambda cift: (-cift[1], cift[0]))[:EN_FAZLA_ADAY]

    puanlar = _rerank_puanlari(eslesme, adaylar, parcalar, indeks, istemci)
    if puanlar is None:
        return _yedek_sec(adaylar, listeler, parcalar, depo, indeks, n)
    if not puanlar:
        return []

    secilen: list[Aday] = []
    for entry_id, parca, puan in puanlar:
        if puan < esik:
            continue
        madde = depo.madde(entry_id)
        kosul_skoru, kosul_gerekceleri = _kosul_skoru(madde, baglam)
        gerekceler = _gerekceler(entry_id, listeler)
        gerekceler.append(f"rerank:{puan:.2f}")
        gerekceler.extend(kosul_gerekceleri)
        secilen.append(
            Aday(
                madde=madde,
                skor=puan + kosul_skoru,
                pasaj=parca.metin,
                gerekceler=gerekceler,
            )
        )

    secilen.sort(key=lambda aday: (-aday.skor, aday.madde.entry_id))
    return _kaynak_sinirla(secilen, n)


def siralama(
    eslesmeler: list[Eslesme],
    depo: MaddeDeposu,
    indeks: _Indeks,
    istemci: _Istemci,
    gelenekler: list[Gelenek] | None = None,
    kollar: frozenset[str] | set[str] = TUM_KOLLAR,
    rerank: bool = True,
    k: int = 10,
) -> dict[str, list[tuple[str, float]]]:
    """Deneyler için eşiksiz, kaynak sınırsız sıralama (docs/15 K4).

    Yalnızca ``kollar`` içindeki kaynaklar kullanılır; ``rerank=False`` iken RRF skoru döner.
    Sonuç anahtarı ``getirme_anahtari(eslesme)``; değer ``(entry_id, skor)`` çiftleridir.
    """
    gerekli_gomme = bool(kollar & {"vektor", "hyde"})
    gommeler = _gommeler(eslesmeler, istemci, hyde="hyde" in kollar) if gerekli_gomme else {}

    sonuc: dict[str, list[tuple[str, float]]] = {}
    for eslesme in eslesmeler:
        listeler, parcalar = _listeler(eslesme, depo, indeks, gelenekler, gommeler)
        listeler = {ad: entry_idler for ad, entry_idler in listeler.items() if ad in kollar}
        skorlar = rrf(list(listeler.values()))
        adaylar = sorted(skorlar.items(), key=lambda cift: (-cift[1], cift[0]))[:EN_FAZLA_ADAY]

        if rerank:
            puanlar = _rerank_puanlari(eslesme, adaylar, parcalar, indeks, istemci)
            if puanlar is None:
                sirali = adaylar
            else:
                sirali = [(entry_id, puan) for entry_id, _parca, puan in puanlar]
        else:
            sirali = adaylar

        sirali.sort(key=lambda cift: (-cift[1], cift[0]))
        sonuc[getirme_anahtari(eslesme)] = sirali[:k]
    return sonuc


def hibrit_getir(
    eslesmeler: list[Eslesme],
    depo: MaddeDeposu,
    indeks: _Indeks,
    istemci: _Istemci,
    baglam: Baglam | None = None,
    gelenekler: list[Gelenek] | None = None,
    n: int = 1,
    esik: float = GETIRME_ESIGI,
) -> Getirilenler:
    """Her eşleşme için hibrit getirme: sözlük + BM25 + vektör + HyDE → RRF → reranker.

    Sonuç anahtarı ``getirme_anahtari(eslesme)``; hiçbir şey bulunamazsa boş liste döner.
    """
    gommeler = _gommeler(eslesmeler, istemci)
    sonuc: Getirilenler = {}
    for eslesme in eslesmeler:
        listeler, parcalar = _listeler(eslesme, depo, indeks, gelenekler, gommeler)
        sonuc[getirme_anahtari(eslesme)] = _sec(
            eslesme, listeler, parcalar, depo, indeks, istemci, baglam, n, esik
        )
    return sonuc
