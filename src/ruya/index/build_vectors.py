"""Hibrit vektör indeksi (docs/13-hibrit-getirme.md, bölüm 4).

Vektör deposu Chroma değil, normalize edilmiş bir numpy matrisidir: ~13 bin parça için
tam tarama yeterlidir ve ağır bir bağımlılık gerekmez. Gömücü (embedding) bu modüle
dışarıdan verilir; indeks katmanı ``ruya.llm`` birimini içe aktarmaz (docs/12, bölüm 1).

``hibrit_indeks_kur`` bir klasöre şunları yazar:

- ``parcalar.jsonl``: bağlamlı parçalar (``Parca`` satırları)
- ``vektorler.npy``: parça vektörleri, float32, satırlar birim uzunlukta
- ``bm25.json``: bağlamlı metinden kurulan Okapi BM25 indeksi
- ``manifest.json``: parça sayısı, boyut, model adı ve giriş kimliği özeti

Gömme uzun sürer; ilerleme her 20 yığında ``vektorler.tmp.npy`` dosyasına yazılır ve
kesintiden sonra kaldığı yerden devam edilir.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ruya.index.bm25 import Bm25Indeksi
from ruya.index.parcalar import Parca, parcala
from ruya.schemas import Madde
from ruya.text.turkce import arama_terimleri

Gomucu = Callable[[list[str]], list[list[float]]]

VARSAYILAN_YIGIN = 32
# İlerlemenin diske yazıldığı yığın aralığı: uzun gömme işi kesilirse en fazla bu kadar
# yığın yeniden gömülür.
KAYIT_ARALIGI = 20

PARCALAR_DOSYASI = "parcalar.jsonl"
VEKTORLER_DOSYASI = "vektorler.npy"
GECICI_VEKTORLER_DOSYASI = "vektorler.tmp.npy"
BM25_DOSYASI = "bm25.json"
MANIFEST_DOSYASI = "manifest.json"


class VektorDeposu:
    """Satırları birim uzunluğa normalize edilmiş numpy matrisi üzerinde tam tarama."""

    def __init__(self, matris: np.ndarray) -> None:
        matris = np.asarray(matris, dtype=np.float32)
        if matris.ndim == 1:
            matris = matris.reshape(1, -1) if matris.size else matris.reshape(0, 0)
        normlar = np.linalg.norm(matris, axis=1, keepdims=True)
        normlar[normlar == 0] = 1.0  # sıfır satır sıfır kalır, bölme hatası olmaz
        self.matris = matris / normlar

    def ara(self, sorgu: np.ndarray, k: int = 10) -> list[tuple[int, float]]:
        """Kosinüs benzerliğine göre en yüksek ``(satır, skor)`` çiftleri, azalan sırada."""
        if k <= 0 or self.matris.shape[0] == 0:
            return []
        sorgu = np.asarray(sorgu, dtype=np.float32).reshape(-1)
        norm = float(np.linalg.norm(sorgu))
        if norm == 0.0:
            return []
        skorlar = self.matris @ (sorgu / norm)
        siralanmis = sorted(range(len(skorlar)), key=lambda i: (-float(skorlar[i]), i))
        return [(i, float(skorlar[i])) for i in siralanmis[:k]]


def hibrit_indeks_kur(
    maddeler: list[Madde],
    gomucu: Gomucu,
    klasor: str | Path,
    *,
    model: str,
    yigin: int = VARSAYILAN_YIGIN,
    terimler: Callable[[str], list[str]] = arama_terimleri,
) -> None:
    """Parçaları, BM25 indeksini ve manifesti ``klasor`` altına yazar.

    ``gomucu`` metin listesi alıp vektör listesi döndürür; ``yigin`` her çağrıdaki metin
    sayısıdır. ``terimler`` BM25 için metni terimlere böler (testlerde değiştirilebilir).
    """
    klasor = Path(klasor)
    klasor.mkdir(parents=True, exist_ok=True)

    parcalar = parcala(maddeler)
    vektorler = _parca_vektorleri([p.baglamli_metin for p in parcalar], gomucu, klasor, yigin)

    _jsonl_yaz(parcalar, klasor / PARCALAR_DOSYASI)
    np.save(klasor / VEKTORLER_DOSYASI, vektorler)

    bm25 = Bm25Indeksi()
    bm25.kur(terimler(p.baglamli_metin) for p in parcalar)
    bm25.kaydet(klasor / BM25_DOSYASI)

    manifest = {
        "parca_sayisi": len(parcalar),
        "boyut": int(vektorler.shape[1]) if vektorler.ndim == 2 else 0,
        "model": model,
        "kimlik_ozeti": _kimlik_ozeti([m.entry_id for m in maddeler]),
    }
    (klasor / MANIFEST_DOSYASI).write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )


class HibritIndeks:
    """Diskteki hibrit indeks: parçalar, BM25 ve parça vektörleri."""

    def __init__(
        self,
        parcalar: list[Parca],
        vektorler: np.ndarray,
        bm25: Bm25Indeksi,
        manifest: dict,
    ) -> None:
        self.parcalar = parcalar
        self.manifest = manifest
        self._vektor_deposu = VektorDeposu(vektorler)
        self._bm25 = bm25
        self._giris_parcalari: dict[str, list[Parca]] = {}
        for parca in parcalar:
            self._giris_parcalari.setdefault(parca.entry_id, []).append(parca)

    @classmethod
    def yukle(cls, klasor: str | Path, maddeler: list[Madde]) -> HibritIndeks:
        """``hibrit_indeks_kur`` çıktısını okur; kimlik özeti tutmazsa ``ValueError``."""
        klasor = Path(klasor)
        manifest_yolu = klasor / MANIFEST_DOSYASI
        if not manifest_yolu.is_file():
            raise FileNotFoundError(f"indeks klasörü bulunamadı: {klasor}")

        manifest = json.loads(manifest_yolu.read_text(encoding="utf-8"))
        beklenen = _kimlik_ozeti([m.entry_id for m in maddeler])
        if manifest.get("kimlik_ozeti") != beklenen:
            raise ValueError(
                f"indeks başka bir madde kümesiyle kurulmuş; yeniden kurulmalı ({klasor})"
            )

        parcalar = [
            Parca(**json.loads(satir))
            for satir in (klasor / PARCALAR_DOSYASI).read_text(encoding="utf-8").splitlines()
            if satir
        ]
        return cls(
            parcalar=parcalar,
            vektorler=np.load(klasor / VEKTORLER_DOSYASI),
            bm25=Bm25Indeksi.yukle(klasor / BM25_DOSYASI),
            manifest=manifest,
        )

    def parca_listesi(self, entry_id: str) -> list[Parca]:
        """Bir girişin parçaları; giriş indekste yoksa boş liste."""
        return list(self._giris_parcalari.get(entry_id, []))

    def bm25_ara(self, terimler: Iterable[str], k: int = 10) -> list[tuple[Parca, float]]:
        """BM25 skoruna göre en iyi parçalar, azalan sırada."""
        return [(self.parcalar[i], skor) for i, skor in self._bm25.ara(terimler, k)]

    def vektor_ara(self, sorgu: np.ndarray, k: int = 10) -> list[tuple[Parca, float]]:
        """Kosinüs benzerliğine göre en yakın parçalar, azalan sırada."""
        return [(self.parcalar[i], skor) for i, skor in self._vektor_deposu.ara(sorgu, k)]


def _parca_vektorleri(metinler: list[str], gomucu: Gomucu, klasor: Path, yigin: int) -> np.ndarray:
    """Parça metinlerini yığınlar hâlinde gömer; kesintiden sonra kaldığı yerden devam eder."""
    gecici = klasor / GECICI_VEKTORLER_DOSYASI
    vektorler: list[list[float]] = []
    if gecici.is_file():
        vektorler = [list(satir) for satir in np.load(gecici)]
    bas = min(len(vektorler), len(metinler))
    vektorler = vektorler[:bas]

    for yigin_sayaci, i in enumerate(range(bas, len(metinler), yigin), start=1):
        vektorler.extend(gomucu(metinler[i : i + yigin]))
        if yigin_sayaci % KAYIT_ARALIGI == 0:
            np.save(gecici, np.asarray(vektorler, dtype=np.float32))

    if gecici.is_file():
        gecici.unlink()
    return np.asarray(vektorler, dtype=np.float32)


def _kimlik_ozeti(entry_idler: list[str]) -> str:
    """Giriş kimliklerinin '\\n' ile birleştirilmiş sha256 özeti (manifest denetimi)."""
    return hashlib.sha256("\n".join(entry_idler).encode("utf-8")).hexdigest()


def _jsonl_yaz(parcalar: list[Parca], yol: Path) -> None:
    """Parçaları her satırda bir JSON nesnesi olacak biçimde yazar."""
    satirlar = [json.dumps(asdict(parca), ensure_ascii=False) for parca in parcalar]
    yol.write_text("\n".join(satirlar) + ("\n" if satirlar else ""), encoding="utf-8")
