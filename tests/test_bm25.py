"""Okapi BM25 indeksi testleri (``ruya.index.bm25.Bm25Indeksi``).

Belgeler zaten tokenize edilmiş listeler olarak verilir; skorlar elle hesaplanabilir
küçük derlemlerle denetlenir.
"""

import json
import math

import pytest

from ruya.index.bm25 import Bm25Indeksi


def _kur(belgeler: list[list[str]], **kwargs) -> Bm25Indeksi:
    indeks = Bm25Indeksi()
    indeks.kur(belgeler, **kwargs)
    return indeks


# --- sıralama: idf, tf ve belge uzunluğu ------------------------------------


def test_nadir_terim_yaygin_terimi_gecer():
    # "nadir" yalnızca 1 belgede, "yaygın" 3 belgede geçer; idf farkı sıralamayı belirler.
    indeks = _kur([["nadir"], ["yaygın"], ["yaygın"], ["yaygın"]])

    sonuc = indeks.ara(["nadir", "yaygın"], k=10)

    assert [belge for belge, _ in sonuc] == [0, 1, 2, 3]


def test_yuksek_terim_frekansi_daha_yuksek_skor_verir():
    # İki belge de aynı uzunlukta; yalnızca "yılan" frekansı farklı.
    indeks = _kur([["yılan", "yılan"], ["yılan", "at"]])

    sonuc = indeks.ara(["yılan"], k=10)

    assert [belge for belge, _ in sonuc] == [0, 1]
    assert sonuc[0][1] > sonuc[1][1]


def test_ayni_frekansla_kisa_belge_daha_yuksek_skor_verir():
    # Her iki belgede "yılan" bir kez geçer; kısa belge daha yüksek skor alır.
    indeks = _kur([["yılan"], ["yılan", "at", "at", "at"]])

    sonuc = indeks.ara(["yılan"], k=10)

    assert [belge for belge, _ in sonuc] == [0, 1]
    assert sonuc[0][1] > sonuc[1][1]


def test_skor_okapi_bm25_formulu_ile_hesaplanir():
    # N=2, df("yılan")=2, avgdl=1.5, k1=1.5, b=0.75.
    indeks = _kur([["yılan"], ["yılan", "at"]])

    sonuc = indeks.ara(["yılan"], k=10)

    idf = math.log(1 + (2 - 2 + 0.5) / (2 + 0.5))
    kisa = idf * (1 * 2.5) / (1 + 1.5 * (1 - 0.75 + 0.75 * 1 / 1.5))
    uzun = idf * (1 * 2.5) / (1 + 1.5 * (1 - 0.75 + 0.75 * 2 / 1.5))
    assert sonuc == [(0, pytest.approx(kisa)), (1, pytest.approx(uzun))]


def test_b_sifir_ise_belge_uzunlugu_skoru_etkilemez():
    # b=0 uzunluk normalizasyonunu kapatır; aynı frekanstaki belgeler eşit skor alır.
    indeks = _kur([["yılan"], ["yılan", "at", "at", "at"]], b=0.0)

    sonuc = indeks.ara(["yılan"], k=10)

    assert [belge for belge, _ in sonuc] == [0, 1]
    assert sonuc[0][1] == pytest.approx(sonuc[1][1])


def test_esit_skorda_belge_indeksi_artan_siralanir():
    indeks = _kur([["yılan"], ["yılan"]])

    sonuc = indeks.ara(["yılan"], k=10)

    assert [belge for belge, _ in sonuc] == [0, 1]
    assert sonuc[0][1] == pytest.approx(sonuc[1][1])


def test_sonuc_en_fazla_k_belge_dondurur():
    indeks = _kur([["yılan"], ["yılan"], ["yılan"]])

    sonuc = indeks.ara(["yılan"], k=2)

    assert [belge for belge, _ in sonuc] == [0, 1]


def test_skoru_sifir_olan_belgeler_dondurulmez():
    indeks = _kur([["yılan"], ["at"]])

    sonuc = indeks.ara(["yılan"], k=10)

    assert [belge for belge, _ in sonuc] == [0]


def test_sonuc_belge_indeksi_ve_skor_ciftleridir():
    indeks = _kur([["yılan"]])

    sonuc = indeks.ara(["yılan"], k=10)

    assert len(sonuc) == 1
    belge, skor = sonuc[0]
    assert isinstance(belge, int)
    assert isinstance(skor, float)
    assert skor > 0


# --- boş durumlar -----------------------------------------------------------


def test_bilinmeyen_terim_bos_liste():
    indeks = _kur([["yılan"], ["at"]])

    assert indeks.ara(["ejderha"], k=10) == []


def test_bos_sorgu_bos_liste():
    indeks = _kur([["yılan"], ["at"]])

    assert indeks.ara([], k=10) == []


def test_bos_derlem_bos_liste():
    indeks = _kur([])

    assert indeks.ara(["yılan"], k=10) == []


# --- kaydet / yükle ---------------------------------------------------------


def test_kaydet_yukle_ayni_aramayi_verir(tmp_path):
    belgeler = [["yılan", "siyah"], ["yılan", "at"], ["at", "at", "at"]]
    indeks = _kur(belgeler)
    yol = tmp_path / "bm25.json"

    indeks.kaydet(yol)
    yuklenen = Bm25Indeksi.yukle(yol)

    assert yuklenen.ara(["yılan", "at"], k=10) == indeks.ara(["yılan", "at"], k=10)


def test_kaydet_yukle_k1_ve_b_ayarlarini_korur(tmp_path):
    belgeler = [["yılan"], ["yılan", "at", "at", "at"]]
    indeks = _kur(belgeler, k1=1.2, b=0.5)
    yol = tmp_path / "bm25.json"

    indeks.kaydet(yol)
    yuklenen = Bm25Indeksi.yukle(yol)

    assert yuklenen.ara(["yılan"], k=10) == indeks.ara(["yılan"], k=10)


def test_kaydet_json_dosyasi_yazar(tmp_path):
    indeks = _kur([["yılan"]])
    yol = tmp_path / "bm25.json"

    indeks.kaydet(yol)

    with yol.open(encoding="utf-8") as dosya:
        assert json.load(dosya) is not None
