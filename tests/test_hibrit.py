"""Hibrit getirme birim testleri (docs/13-hibrit-getirme.md).

Sahte indeks, sahte LLM istemcisi ve BellekDeposu ile ağa çıkmadan çalışır.
"""

import pytest

from ruya.config import GETIRME_ESIGI
from ruya.hatalar import LLMHatasi
from ruya.index.parcalar import Parca
from ruya.index.store import BellekDeposu
from ruya.pipeline.hibrit import (
    TUM_KOLLAR,
    getirme_sorgusu,
    hibrit_getir,
    rrf,
    siralama,
)
from ruya.schemas import Baglam, Eslesme, Kosul, Madde, Sembol
from ruya.text.turkce import arama_terimleri

# --- Yardımcılar ------------------------------------------------------------


def _madde(
    entry_id: str,
    kaynak: str,
    symbol_ids: list[str],
    *,
    metin_tr: str = "Rüyada bir şey görmek.",
    gelenek: str = "islami_klasik",
    kosullar: list[Kosul] | None = None,
) -> Madde:
    """Testte kullanılacak en küçük geçerli Madde."""
    return Madde(
        entry_id=entry_id,
        kaynak=kaynak,
        eser="Test Eseri",
        yazar="Test Yazarı",
        gelenek=gelenek,
        dil="tr",
        lisans="PD",
        konum={"satir": 1},
        symbol_ids=symbol_ids,
        metin_asli="(asıl metin)",
        metin_tr=metin_tr,
        kosullar=kosullar,
    )


def _eslesme(
    symbol_id: str | None,
    *,
    yalin: str = "yılan",
    nitelikler: list[str] | None = None,
    eylem: str | None = None,
    hyde: str | None = None,
    yontem: str = "birebir",
) -> Eslesme:
    return Eslesme(
        sembol=Sembol(
            yalin=yalin,
            nitelikler=nitelikler or [],
            eylem=eylem,
            hyde=hyde,
            ham_ifade=yalin,
        ),
        symbol_id=symbol_id,
        yontem=yontem,
        guven=1.0,
    )


def _parca(entry_id: str, sira: int = 0, metin: str | None = None) -> Parca:
    metin = metin if metin is not None else f"{entry_id} parça {sira}"
    return Parca(
        parca_id=f"{entry_id}#{sira}",
        entry_id=entry_id,
        metin=metin,
        baglamli_metin=f"Test Eseri · Test Yazarı.\n{metin}",
    )


def _vektor(metin: str) -> list[float]:
    """Sahte gömücü: metinden deterministik bir vektör üretir."""
    return [float(len(metin)), float(sum(ord(karakter) for karakter in metin) % 1000)]


def _vektor_anahtari(vektor) -> tuple[float, ...]:
    return tuple(round(float(deger), 6) for deger in vektor)


class SahteIndeks:
    """HibritIndeks'in testte kullanılan üç yöntemi."""

    def __init__(
        self,
        parcalar: dict[str, list[Parca]] | None = None,
        *,
        bm25: dict[tuple[str, ...], list[tuple[Parca, float]]] | None = None,
        vektor: dict[tuple[float, ...], list[tuple[Parca, float]]] | None = None,
    ) -> None:
        self._parcalar = parcalar or {}
        self._bm25 = bm25 or {}
        self._vektor = vektor or {}
        self.bm25_cagrilari: list[list[str]] = []
        self.vektor_cagrilari: list[tuple[float, ...]] = []

    def parca_listesi(self, entry_id: str) -> list[Parca]:
        return list(self._parcalar.get(entry_id, []))

    def bm25_ara(self, terimler, k: int = 10) -> list[tuple[Parca, float]]:
        terimler = list(terimler)
        self.bm25_cagrilari.append(terimler)
        return list(self._bm25.get(tuple(terimler), []))

    def vektor_ara(self, sorgu, k: int = 10) -> list[tuple[Parca, float]]:
        anahtar = _vektor_anahtari(sorgu)
        self.vektor_cagrilari.append(anahtar)
        return list(self._vektor.get(anahtar, []))


class SahteIstemci:
    """LLMIstemcisi'nin gom ve yeniden_sirala yöntemleri; ağ yok."""

    def __init__(
        self,
        *,
        puanlar: dict[str, float] | None = None,
        gom_hatasi: bool = False,
        rerank_hatasi: bool = False,
    ) -> None:
        self._puanlar = puanlar or {}
        self._gom_hatasi = gom_hatasi
        self._rerank_hatasi = rerank_hatasi
        self.gom_cagrilari: list[tuple[list[str], bool]] = []
        self.rerank_cagrilari: list[tuple[str, list[str], bool]] = []

    def gom(self, metinler: list[str], ruya_icerir: bool = False) -> list[list[float]]:
        self.gom_cagrilari.append((list(metinler), ruya_icerir))
        if self._gom_hatasi:
            raise LLMHatasi("gömme geçidi hatası", durum=500)
        return [_vektor(metin) for metin in metinler]

    def yeniden_sirala(
        self, sorgu: str, belgeler: list[str], ruya_icerir: bool = False
    ) -> list[tuple[int, float]]:
        self.rerank_cagrilari.append((sorgu, list(belgeler), ruya_icerir))
        if self._rerank_hatasi:
            raise LLMHatasi("reranker geçidi hatası", durum=500)
        sonuclar = [(sira, self._puanlar.get(belge, 0.0)) for sira, belge in enumerate(belgeler)]
        return sorted(sonuclar, key=lambda cift: cift[1], reverse=True)


def _sorgu_ve_terimler(eslesme: Eslesme) -> tuple[str, tuple[str, ...]]:
    sorgu = getirme_sorgusu(eslesme.sembol)
    return sorgu, tuple(arama_terimleri(sorgu))


# --- rrf --------------------------------------------------------------------


def test_rrf_rank_birden_baslar_ve_k_arti_rank_toplanir():
    assert rrf([["a", "b"], ["b"]]) == pytest.approx({"a": 1 / 61, "b": 1 / 62 + 1 / 61})


def test_rrf_k_degistirilebilir():
    assert rrf([["a"]], k=10) == pytest.approx({"a": 1 / 11})


def test_rrf_bos_girdi_bos_sozluk():
    assert rrf([]) == {}
    assert rrf([[], []]) == {}


def test_rrf_ayni_belge_birden_cok_listede_toplanir():
    assert rrf([["a"], ["a"], ["a"]]) == pytest.approx({"a": 3 / 61})


# --- getirme_sorgusu --------------------------------------------------------


def test_getirme_sorgusu_nitelikler_ve_yalin():
    sembol = Sembol(yalin="yılan", nitelikler=["siyah", "büyük"], ham_ifade="yılan")

    assert getirme_sorgusu(sembol) == "Rüyada siyah büyük yılan görmek"


def test_getirme_sorgusu_niteliksiz():
    sembol = Sembol(yalin="yılan", ham_ifade="yılan")

    assert getirme_sorgusu(sembol) == "Rüyada yılan görmek"


def test_getirme_sorgusu_eylemi_parantez_icinde_ekler():
    sembol = Sembol(yalin="yılan", nitelikler=["siyah"], eylem="ısırdı", ham_ifade="yılan")

    assert getirme_sorgusu(sembol) == "Rüyada siyah yılan görmek (ısırdı)"


# --- hibrit_getir: temel akış -----------------------------------------------


def test_sozluk_adayi_rerank_skoru_ve_pasaji_ile_doner():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001", metin="Yılan görmek hayırdır.")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    sonuc = hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)

    assert set(sonuc) == {"yilan"}
    aday = sonuc["yilan"][0]
    assert aday.madde is madde
    assert aday.skor == pytest.approx(0.45)
    assert aday.pasaj == parca.metin
    assert "sozluk" in aday.gerekceler
    assert "rerank:0.45" in aday.gerekceler


def test_gom_ve_rerank_ruya_icerir_true_ile_cagrilir():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)

    assert istemci.gom_cagrilari
    assert all(bayrak is True for _, bayrak in istemci.gom_cagrilari)
    assert istemci.rerank_cagrilari
    assert all(bayrak is True for _, _, bayrak in istemci.rerank_cagrilari)


def test_tum_gommeler_tek_cagrida_gonderilir():
    yilan = _madde("nablusi:000001", "nablusi", ["yilan"])
    at = _madde("miller:000001", "miller", ["at"], gelenek="bati_halk")
    depo = BellekDeposu([yilan, at])
    indeks = SahteIndeks({})
    istemci = SahteIstemci()
    hyde = "Rüyada at görmek yolculuğa işarettir."

    hibrit_getir(
        [_eslesme("yilan"), _eslesme("at", yalin="at", hyde=hyde)],
        depo,
        indeks,
        istemci,
    )

    assert len(istemci.gom_cagrilari) == 1
    metinler, bayrak = istemci.gom_cagrilari[0]
    assert bayrak is True
    assert "Rüyada yılan görmek" in metinler
    assert "Rüyada at görmek" in metinler
    assert hyde in metinler


def test_bm25_ve_vektor_gerekceleri_yazilir():
    madde = _madde("nablusi:000001", "nablusi", [])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    eslesme = _eslesme("yilan")
    sorgu, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        {"nablusi:000001": [parca]},
        bm25={terimler: [(parca, 5.0)]},
        vektor={_vektor_anahtari(_vektor(sorgu)): [(parca, 0.8)]},
    )
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci)

    gerekceler = sonuc["yilan"][0].gerekceler
    assert "bm25" in gerekceler
    assert "vektor" in gerekceler
    assert "sozluk" not in gerekceler


def test_hyde_vektoru_ile_ayri_arama_yapilir():
    madde = _madde("nablusi:000001", "nablusi", [])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    hyde = "Rüyada yılan ısırırsa düşmana işarettir."
    eslesme = _eslesme("yilan", hyde=hyde)
    indeks = SahteIndeks(
        {"nablusi:000001": [parca]},
        vektor={_vektor_anahtari(_vektor(hyde)): [(parca, 0.7)]},
    )
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci)

    gerekceler = sonuc["yilan"][0].gerekceler
    assert "hyde" in gerekceler
    assert "vektor" not in gerekceler


def test_parca_vurulari_madde_duzeyinde_birlesir_en_iyi_parca_kalir():
    madde = _madde("nablusi:000001", "nablusi", [])
    iyi = _parca("nablusi:000001", 0, metin="en iyi parça")
    digeri = _parca("nablusi:000001", 1, metin="ikinci parça")
    depo = BellekDeposu([madde])
    eslesme = _eslesme("yilan")
    sorgu, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        {"nablusi:000001": [iyi, digeri]},
        bm25={terimler: [(iyi, 9.0), (digeri, 4.0)]},
        vektor={_vektor_anahtari(_vektor(sorgu)): [(iyi, 0.9)]},
    )
    istemci = SahteIstemci(
        puanlar={iyi.baglamli_metin: 0.45, digeri.baglamli_metin: 0.2}
    )

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci)

    assert len(sonuc["yilan"]) == 1
    assert sonuc["yilan"][0].pasaj == "en iyi parça"
    assert istemci.rerank_cagrilari[0][1] == [iyi.baglamli_metin]


def test_sozluk_adayi_parcasi_yoksa_ilk_parcasiyla_rerankere_gider():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    ilk = _parca("nablusi:000001", 0, metin="ilk parça")
    ikinci = _parca("nablusi:000001", 1, metin="ikinci parça")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [ilk, ikinci]})
    istemci = SahteIstemci(puanlar={ilk.baglamli_metin: 0.45})

    sonuc = hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)

    assert istemci.rerank_cagrilari[0][1] == [ilk.baglamli_metin]
    assert sonuc["yilan"][0].pasaj == "ilk parça"


# --- hibrit_getir: eşik -----------------------------------------------------


def test_esik_alti_aday_atilir_ve_bos_liste_doner():
    madde = _madde("nablusi:000001", "nablusi", [])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"nablusi:000001": [parca]}, bm25={terimler: [(parca, 5.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.05})

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci)

    assert sonuc["yilan"] == []


def test_sozluk_adayi_da_esik_altinda_atilir():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.05})

    sonuc = hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)

    assert sonuc["yilan"] == []


def test_esik_parametresi_degistirilebilir():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.4})

    assert hibrit_getir([_eslesme("yilan")], depo, indeks, istemci, esik=0.5)["yilan"] == []
    assert len(hibrit_getir([_eslesme("yilan")], depo, indeks, istemci, esik=0.3)["yilan"]) == 1


def test_varsayilan_esik_config_degeridir():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: GETIRME_ESIGI - 0.01})

    assert hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)["yilan"] == []


# --- hibrit_getir: kaynak sınırı ve anahtarlar ------------------------------


def test_kaynak_basina_en_fazla_n_aday_kalir():
    maddeler = [
        _madde("nablusi:000001", "nablusi", []),
        _madde("nablusi:000002", "nablusi", []),
        _madde("nablusi:000003", "nablusi", []),
        _madde("miller:000001", "miller", [], gelenek="bati_halk"),
    ]
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in maddeler}
    depo = BellekDeposu(maddeler)
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    puanlar = {
        "nablusi:000001": 0.9,
        "nablusi:000002": 0.8,
        "nablusi:000003": 0.7,
        "miller:000001": 0.6,
    }
    bm25 = [(parcalar[entry_id][0], 10.0 - sira) for sira, entry_id in enumerate(puanlar)]
    indeks = SahteIndeks(parcalar, bm25={terimler: bm25})
    istemci = SahteIstemci(
        puanlar={parcalar[entry_id][0].baglamli_metin: skor for entry_id, skor in puanlar.items()}
    )

    tek = hibrit_getir([eslesme], depo, indeks, istemci, n=1)
    assert [aday.madde.entry_id for aday in tek["yilan"]] == [
        "nablusi:000001",
        "miller:000001",
    ]

    iki = hibrit_getir([eslesme], depo, indeks, istemci, n=2)
    assert [aday.madde.entry_id for aday in iki["yilan"]] == [
        "nablusi:000001",
        "nablusi:000002",
        "miller:000001",
    ]


def test_eslenmemis_sembol_serbest_anahtariyla_aranir():
    madde = _madde("miller:000001", "miller", [], gelenek="bati_halk")
    parca = _parca("miller:000001")
    depo = BellekDeposu([madde])
    eslesme = _eslesme(None, yalin="baba", yontem="yok")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"miller:000001": [parca]}, bm25={terimler: [(parca, 3.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci)

    assert set(sonuc) == {"serbest:baba"}
    assert sonuc["serbest:baba"][0].madde is madde


def test_hicbir_sey_bulunamazsa_bos_liste():
    depo = BellekDeposu([_madde("nablusi:000001", "nablusi", ["yilan"])])
    indeks = SahteIndeks({})
    istemci = SahteIstemci()

    sonuc = hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)

    assert sonuc == {"yilan": []}


# --- hibrit_getir: gelenek filtresi -----------------------------------------


def test_gelenekler_none_psikanalitik_maddeleri_haric_tutar():
    freud = _madde("freud:000001", "freud", [], gelenek="psikanalitik")
    parca = _parca("freud:000001")
    depo = BellekDeposu([freud])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"freud:000001": [parca]}, bm25={terimler: [(parca, 5.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    assert hibrit_getir([eslesme], depo, indeks, istemci)["yilan"] == []

    secili = hibrit_getir([eslesme], depo, indeks, istemci, gelenekler=["psikanalitik"])
    assert [aday.madde.entry_id for aday in secili["yilan"]] == ["freud:000001"]


def test_gelenekler_verilince_yalniz_onlarin_maddeleri_kalir():
    islami = _madde("nablusi:000001", "nablusi", [])
    bati = _madde("miller:000001", "miller", [], gelenek="bati_halk")
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (islami, bati)}
    depo = BellekDeposu([islami, bati])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={
            terimler: [
                (parcalar["nablusi:000001"][0], 9.0),
                (parcalar["miller:000001"][0], 8.0),
            ]
        },
    )
    istemci = SahteIstemci(
        puanlar={
            parcalar["nablusi:000001"][0].baglamli_metin: 0.45,
            parcalar["miller:000001"][0].baglamli_metin: 0.44,
        }
    )

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci, gelenekler=["bati_halk"], n=5)

    assert [aday.madde.entry_id for aday in sonuc["yilan"]] == ["miller:000001"]


# --- hibrit_getir: bağlam koşulu --------------------------------------------


def test_baglam_kosulu_eslesince_skor_artar_ve_gerekce_yazilir():
    kosullu = _madde(
        "nablusi:000001",
        "nablusi",
        [],
        kosullar=[Kosul(kosul={"cinsiyet": "kadin"}, yorum_tr="Kadın görürse …")],
    )
    genel = _madde("nablusi:000002", "nablusi", [])
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (kosullu, genel)}
    depo = BellekDeposu([kosullu, genel])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={
            terimler: [
                (parcalar["nablusi:000001"][0], 9.0),
                (parcalar["nablusi:000002"][0], 8.0),
            ]
        },
    )
    istemci = SahteIstemci(
        puanlar={
            parcalar["nablusi:000001"][0].baglamli_metin: 0.44,
            parcalar["nablusi:000002"][0].baglamli_metin: 0.45,
        }
    )

    sonuc = hibrit_getir(
        [eslesme], depo, indeks, istemci, baglam=Baglam(cinsiyet="kadin"), n=5
    )

    assert [aday.madde.entry_id for aday in sonuc["yilan"]] == [
        "nablusi:000001",
        "nablusi:000002",
    ]
    assert "kosul:cinsiyet" in sonuc["yilan"][0].gerekceler


def test_baglam_kosulu_farkli_deger_skoru_dusurur():
    erkek = _madde(
        "nablusi:000001",
        "nablusi",
        [],
        kosullar=[Kosul(kosul={"cinsiyet": "erkek"}, yorum_tr="Erkek görürse …")],
    )
    genel = _madde("nablusi:000002", "nablusi", [])
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (erkek, genel)}
    depo = BellekDeposu([erkek, genel])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={
            terimler: [
                (parcalar["nablusi:000001"][0], 9.0),
                (parcalar["nablusi:000002"][0], 8.0),
            ]
        },
    )
    istemci = SahteIstemci(
        puanlar={
            parcalar["nablusi:000001"][0].baglamli_metin: 0.45,
            parcalar["nablusi:000002"][0].baglamli_metin: 0.44,
        }
    )

    sonuc = hibrit_getir(
        [eslesme], depo, indeks, istemci, baglam=Baglam(cinsiyet="kadin"), n=5
    )

    assert [aday.madde.entry_id for aday in sonuc["yilan"]] == [
        "nablusi:000002",
        "nablusi:000001",
    ]


def _tek_kosullu_aday(kosullar: list[Kosul], baglam: Baglam, puan: float = 0.45):
    """Tek maddeli, tek parçalı senaryo: dönen tek adayı verir."""
    madde = _madde("nablusi:000001", "nablusi", ["yilan"], kosullar=kosullar)
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: puan})

    sonuc = hibrit_getir([_eslesme("yilan")], depo, indeks, istemci, baglam=baglam)

    assert len(sonuc["yilan"]) == 1
    return sonuc["yilan"][0]


def test_ayni_cinsiyet_kosulu_iki_kez_sayilmaz():
    aday = _tek_kosullu_aday(
        [
            Kosul(kosul={"cinsiyet": "kadin"}, yorum_tr="Kadın görürse …"),
            Kosul(kosul={"cinsiyet": "kadin"}, yorum_tr="Kadına gelince …"),
        ],
        Baglam(cinsiyet="kadin"),
    )

    assert aday.skor == pytest.approx(0.55)
    assert aday.gerekceler.count("kosul:cinsiyet") == 1


def test_kadin_ve_erkek_kosulu_her_iki_cinsiyete_de_artirir():
    kosullar = [
        Kosul(kosul={"cinsiyet": "kadin"}, yorum_tr="Kadın görürse …"),
        Kosul(kosul={"cinsiyet": "erkek"}, yorum_tr="Erkek görürse …"),
    ]

    kadin = _tek_kosullu_aday(kosullar, Baglam(cinsiyet="kadin"))
    erkek = _tek_kosullu_aday(kosullar, Baglam(cinsiyet="erkek"))

    assert kadin.skor == pytest.approx(0.55)
    assert erkek.skor == pytest.approx(0.55)
    assert "kosul:cinsiyet" in kadin.gerekceler
    assert "kosul:cinsiyet" in erkek.gerekceler


def test_yalniz_erkek_kosulu_kadinda_skoru_dusurur():
    aday = _tek_kosullu_aday(
        [Kosul(kosul={"cinsiyet": "erkek"}, yorum_tr="Erkek görürse …")],
        Baglam(cinsiyet="kadin"),
    )

    assert aday.skor == pytest.approx(0.35)
    assert "kosul:cinsiyet" not in aday.gerekceler


# --- hibrit_getir: hata yolları ---------------------------------------------


def test_gom_hatasi_vektor_aramalarini_atlar_ama_hata_vermez():
    madde = _madde("nablusi:000001", "nablusi", [])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    eslesme = _eslesme("yilan", hyde="Rüyada yılan görmek korkuya işarettir.")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"nablusi:000001": [parca]}, bm25={terimler: [(parca, 5.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45}, gom_hatasi=True)

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci)

    assert [aday.madde.entry_id for aday in sonuc["yilan"]] == ["nablusi:000001"]
    assert indeks.vektor_cagrilari == []
    assert "bm25" in sonuc["yilan"][0].gerekceler


def test_rerank_hatasinda_rrf_sirasi_ve_rerank_yok_gerekcesi_kullanilir():
    sozluk_madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    bm25_madde = _madde("miller:000001", "miller", [], gelenek="bati_halk")
    vektor_madde = _madde("miller:000002", "miller", [], gelenek="bati_halk")
    parcalar = {
        madde.entry_id: [_parca(madde.entry_id)]
        for madde in (sozluk_madde, bm25_madde, vektor_madde)
    }
    depo = BellekDeposu([sozluk_madde, bm25_madde, vektor_madde])
    eslesme = _eslesme("yilan")
    sorgu, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={terimler: [(parcalar["miller:000001"][0], 5.0)]},
        vektor={_vektor_anahtari(_vektor(sorgu)): [(parcalar["miller:000002"][0], 0.9)]},
    )
    istemci = SahteIstemci(rerank_hatasi=True)

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci, n=5)

    adaylar = sonuc["yilan"]
    assert {aday.madde.entry_id for aday in adaylar} == {"nablusi:000001", "miller:000001"}
    assert all("rerank-yok" in aday.gerekceler for aday in adaylar)


def test_rerank_hatasinda_esik_uygulanmaz():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(rerank_hatasi=True)

    sonuc = hibrit_getir([_eslesme("yilan")], depo, indeks, istemci)

    assert [aday.madde.entry_id for aday in sonuc["yilan"]] == ["nablusi:000001"]


def test_rerankere_en_fazla_kirk_aday_gider():
    maddeler = [_madde(f"nablusi:{sira:06d}", "nablusi", []) for sira in range(1, 46)]
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in maddeler}
    depo = BellekDeposu(maddeler)
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    bm25 = [(parcalar[madde.entry_id][0], 50.0 - sira) for sira, madde in enumerate(maddeler)]
    indeks = SahteIndeks(parcalar, bm25={terimler: bm25})
    istemci = SahteIstemci(
        puanlar={parcalar[madde.entry_id][0].baglamli_metin: 0.45 for madde in maddeler}
    )

    hibrit_getir([eslesme], depo, indeks, istemci, n=100)

    assert len(istemci.rerank_cagrilari[0][1]) == 40


# --- siralama: deney için eşiksiz, sınırsız sıralama ------------------------


def test_tum_kollar_sabiti_dort_kolu_tasir():
    assert frozenset({"sozluk", "bm25", "vektor", "hyde"}) == TUM_KOLLAR


def test_siralama_esik_uygulamaz_dusuk_rerank_skoru_da_doner():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    indeks = SahteIndeks({"nablusi:000001": [parca]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.01})

    sonuc = siralama([_eslesme("yilan")], depo, indeks, istemci)

    assert set(sonuc) == {"yilan"}
    assert sonuc["yilan"] == [("nablusi:000001", pytest.approx(0.01))]


def test_siralama_kaynak_siniri_uygulamaz_ayni_kaynaktan_iki_aday_doner():
    birinci = _madde("nablusi:000001", "nablusi", [])
    ikinci = _madde("nablusi:000002", "nablusi", [])
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (birinci, ikinci)}
    depo = BellekDeposu([birinci, ikinci])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={
            terimler: [
                (parcalar["nablusi:000001"][0], 9.0),
                (parcalar["nablusi:000002"][0], 8.0),
            ]
        },
    )
    istemci = SahteIstemci(
        puanlar={
            parcalar["nablusi:000001"][0].baglamli_metin: 0.9,
            parcalar["nablusi:000002"][0].baglamli_metin: 0.8,
        }
    )

    sonuc = siralama([eslesme], depo, indeks, istemci, kollar={"bm25"})

    assert [entry_id for entry_id, _skor in sonuc["yilan"]] == [
        "nablusi:000001",
        "nablusi:000002",
    ]


def test_siralama_yalniz_istenen_kollar_kullanilir_gom_cagrilmaz():
    madde = _madde("nablusi:000001", "nablusi", ["yilan"])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    eslesme = _eslesme("yilan", hyde="Rüyada yılan görmek korkuya işarettir.")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"nablusi:000001": [parca]}, bm25={terimler: [(parca, 5.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    sonuc = siralama([eslesme], depo, indeks, istemci, kollar={"sozluk", "bm25"})

    assert [entry_id for entry_id, _skor in sonuc["yilan"]] == ["nablusi:000001"]
    assert istemci.gom_cagrilari == []
    assert indeks.vektor_cagrilari == []


def test_siralama_hyde_kolu_yoksa_hyde_metni_gomlenmez():
    madde = _madde("nablusi:000001", "nablusi", [])
    parca = _parca("nablusi:000001")
    depo = BellekDeposu([madde])
    hyde = "Rüyada yılan ısırırsa düşmana işarettir."
    eslesme = _eslesme("yilan", hyde=hyde)
    sorgu, _terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        {"nablusi:000001": [parca]},
        vektor={_vektor_anahtari(_vektor(sorgu)): [(parca, 0.8)]},
    )
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    siralama([eslesme], depo, indeks, istemci, kollar={"vektor"})

    assert len(istemci.gom_cagrilari) == 1
    metinler, _bayrak = istemci.gom_cagrilari[0]
    assert sorgu in metinler
    assert hyde not in metinler


def test_siralama_rerank_false_rrf_skoru_ve_sirasi_doner():
    birinci = _madde("nablusi:000001", "nablusi", [])
    ikinci = _madde("nablusi:000002", "nablusi", [])
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (birinci, ikinci)}
    depo = BellekDeposu([birinci, ikinci])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={
            terimler: [
                (parcalar["nablusi:000002"][0], 9.0),
                (parcalar["nablusi:000001"][0], 8.0),
            ]
        },
    )
    istemci = SahteIstemci()

    sonuc = siralama([eslesme], depo, indeks, istemci, kollar={"bm25"}, rerank=False)

    assert istemci.rerank_cagrilari == []
    assert sonuc["yilan"] == [
        ("nablusi:000002", pytest.approx(1 / 61)),
        ("nablusi:000001", pytest.approx(1 / 62)),
    ]


def test_siralama_rerank_hatasinda_rrf_sirasi_kullanilir():
    birinci = _madde("nablusi:000001", "nablusi", [])
    ikinci = _madde("nablusi:000002", "nablusi", [])
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (birinci, ikinci)}
    depo = BellekDeposu([birinci, ikinci])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={
            terimler: [
                (parcalar["nablusi:000002"][0], 9.0),
                (parcalar["nablusi:000001"][0], 8.0),
            ]
        },
    )
    istemci = SahteIstemci(rerank_hatasi=True)

    sonuc = siralama([eslesme], depo, indeks, istemci, kollar={"bm25"})

    assert sonuc["yilan"] == [
        ("nablusi:000002", pytest.approx(1 / 61)),
        ("nablusi:000001", pytest.approx(1 / 62)),
    ]


def test_siralama_gelenekler_none_psikanalitik_maddeleri_haric_tutar():
    freud = _madde("freud:000001", "freud", [], gelenek="psikanalitik")
    parca = _parca("freud:000001")
    depo = BellekDeposu([freud])
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"freud:000001": [parca]}, bm25={terimler: [(parca, 5.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    assert siralama([eslesme], depo, indeks, istemci, kollar={"bm25"})["yilan"] == []

    secili = siralama(
        [eslesme], depo, indeks, istemci, kollar={"bm25"}, gelenekler=["psikanalitik"]
    )
    assert [entry_id for entry_id, _skor in secili["yilan"]] == ["freud:000001"]


def test_siralama_k_siniri_ve_esit_skorda_entry_id_artan_sira():
    birinci = _madde("nablusi:000001", "nablusi", [])
    ikinci = _madde("nablusi:000002", "nablusi", [])
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in (birinci, ikinci)}
    depo = BellekDeposu([birinci, ikinci])
    eslesme = _eslesme("yilan")
    sorgu, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks(
        parcalar,
        bm25={terimler: [(parcalar["nablusi:000002"][0], 9.0)]},
        vektor={_vektor_anahtari(_vektor(sorgu)): [(parcalar["nablusi:000001"][0], 0.9)]},
    )
    istemci = SahteIstemci()

    sonuc = siralama([eslesme], depo, indeks, istemci, kollar={"bm25", "vektor"}, rerank=False)

    assert sonuc["yilan"] == [
        ("nablusi:000001", pytest.approx(1 / 61)),
        ("nablusi:000002", pytest.approx(1 / 61)),
    ]

    tek = siralama([eslesme], depo, indeks, istemci, kollar={"bm25", "vektor"}, rerank=False, k=1)
    assert tek["yilan"] == [("nablusi:000001", pytest.approx(1 / 61))]


def test_siralama_eslenmemis_sembol_serbest_anahtariyla_doner():
    madde = _madde("miller:000001", "miller", [], gelenek="bati_halk")
    parca = _parca("miller:000001")
    depo = BellekDeposu([madde])
    eslesme = _eslesme(None, yalin="baba", yontem="yok")
    _, terimler = _sorgu_ve_terimler(eslesme)
    indeks = SahteIndeks({"miller:000001": [parca]}, bm25={terimler: [(parca, 3.0)]})
    istemci = SahteIstemci(puanlar={parca.baglamli_metin: 0.45})

    sonuc = siralama([eslesme], depo, indeks, istemci, kollar={"bm25"})

    assert set(sonuc) == {"serbest:baba"}
    assert [entry_id for entry_id, _skor in sonuc["serbest:baba"]] == ["miller:000001"]


# --- hibrit_getir: refaktör sonrası eşik ve kaynak sınırı korunur -----------


def test_hibrit_getir_esik_ve_kaynak_siniri_hala_uygulanir():
    maddeler = [
        _madde("nablusi:000001", "nablusi", []),
        _madde("nablusi:000002", "nablusi", []),
        _madde("miller:000001", "miller", [], gelenek="bati_halk"),
        _madde("miller:000002", "miller", [], gelenek="bati_halk"),
    ]
    parcalar = {madde.entry_id: [_parca(madde.entry_id)] for madde in maddeler}
    depo = BellekDeposu(maddeler)
    eslesme = _eslesme("yilan")
    _, terimler = _sorgu_ve_terimler(eslesme)
    puanlar = {
        "nablusi:000001": 0.9,
        "nablusi:000002": 0.8,
        "miller:000001": 0.6,
        "miller:000002": 0.05,
    }
    bm25 = [(parcalar[entry_id][0], 10.0 - sira) for sira, entry_id in enumerate(puanlar)]
    indeks = SahteIndeks(parcalar, bm25={terimler: bm25})
    istemci = SahteIstemci(
        puanlar={parcalar[entry_id][0].baglamli_metin: skor for entry_id, skor in puanlar.items()}
    )

    sonuc = hibrit_getir([eslesme], depo, indeks, istemci, n=1)

    assert [aday.madde.entry_id for aday in sonuc["yilan"]] == [
        "nablusi:000001",
        "miller:000001",
    ]
