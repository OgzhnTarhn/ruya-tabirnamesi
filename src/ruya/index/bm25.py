"""Okapi BM25 sözlüksel arama indeksi.

Belgeler zaten tokenize edilmiş listeler olarak verilir. İndeks ters (inverted) yapıdadır:
her terim, o terimi içeren belgelerin ``[belge_indeksi, terim_frekansi]`` çiftlerini tutar.
Böylece bir arama yalnızca sorgu terimlerini içeren belgelere dokunur; bütün derlem taranmaz.

Skor, klasik Okapi BM25 formülüyle hesaplanır::

    idf(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
    skor(t, d) = idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))

Yalnızca standart kütüphane kullanılır; indeks JSON olarak kaydedilip yüklenebilir.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from pathlib import Path

VARSAYILAN_K1 = 1.5
VARSAYILAN_B = 0.75


class Bm25Indeksi:
    """Ters indeksli Okapi BM25 arayıcısı."""

    def __init__(self, k1: float = VARSAYILAN_K1, b: float = VARSAYILAN_B) -> None:
        self.k1 = k1
        self.b = b
        self._ters_indeks: dict[str, list[list[int]]] = {}
        self._uzunluklar: list[int] = []
        self._ortalama_uzunluk = 0.0

    @property
    def belge_sayisi(self) -> int:
        return len(self._uzunluklar)

    def kur(
        self,
        belgeler: Iterable[Iterable[str]],
        *,
        k1: float | None = None,
        b: float | None = None,
    ) -> None:
        """İndeksi verilen token listelerinden sıfırdan kurar."""
        if k1 is not None:
            self.k1 = k1
        if b is not None:
            self.b = b

        self._ters_indeks = {}
        self._uzunluklar = []
        for belge_indeksi, belge in enumerate(belgeler):
            terimler = list(belge)
            self._uzunluklar.append(len(terimler))
            frekanslar: dict[str, int] = {}
            for terim in terimler:
                frekanslar[terim] = frekanslar.get(terim, 0) + 1
            for terim, tf in frekanslar.items():
                self._ters_indeks.setdefault(terim, []).append([belge_indeksi, tf])

        toplam = sum(self._uzunluklar)
        self._ortalama_uzunluk = toplam / len(self._uzunluklar) if self._uzunluklar else 0.0

    def _idf(self, df: int) -> float:
        n = self.belge_sayisi
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def ara(self, sorgu: Iterable[str], k: int = 10) -> list[tuple[int, float]]:
        """Sorgu terimlerine göre en yüksek skorlu ``(belge_indeksi, skor)`` çiftleri.

        Skoru sıfır olan belgeler döndürülmez; eşit skorda belge indeksi küçük olan önce gelir.
        """
        if k <= 0 or not self._uzunluklar:
            return []

        skorlar: dict[int, float] = {}
        for terim in sorgu:
            kayitlar = self._ters_indeks.get(terim)
            if not kayitlar:
                continue
            idf = self._idf(len(kayitlar))
            for belge_indeksi, tf in kayitlar:
                dl = self._uzunluklar[belge_indeksi]
                payda = tf + self.k1 * (
                    1 - self.b + self.b * dl / self._ortalama_uzunluk
                )
                skorlar[belge_indeksi] = skorlar.get(belge_indeksi, 0.0) + (
                    idf * tf * (self.k1 + 1) / payda
                )

        siralanmis = sorted(
            ((belge, skor) for belge, skor in skorlar.items() if skor > 0),
            key=lambda cift: (-cift[1], cift[0]),
        )
        return siralanmis[:k]

    def kaydet(self, yol: str | Path) -> None:
        """İndeksi (ayarlar ve ters indeks dahil) JSON dosyasına yazar."""
        veri = {
            "k1": self.k1,
            "b": self.b,
            "uzunluklar": self._uzunluklar,
            "ortalama_uzunluk": self._ortalama_uzunluk,
            "ters_indeks": self._ters_indeks,
        }
        Path(yol).write_text(
            json.dumps(veri, ensure_ascii=False), encoding="utf-8"
        )

    @classmethod
    def yukle(cls, yol: str | Path) -> Bm25Indeksi:
        """``kaydet`` ile yazılmış bir indeksi okur."""
        veri = json.loads(Path(yol).read_text(encoding="utf-8"))
        indeks = cls(k1=veri["k1"], b=veri["b"])
        indeks._uzunluklar = list(veri["uzunluklar"])
        indeks._ortalama_uzunluk = veri["ortalama_uzunluk"]
        indeks._ters_indeks = {
            terim: [list(kayit) for kayit in kayitlar]
            for terim, kayitlar in veri["ters_indeks"].items()
        }
        return indeks
