"""Hibrit vektör indeksi birim testleri (``ruya.index.build_vectors``, docs/13).

``VektorDeposu`` satırları normalize edilmiş numpy matrisi tutar; ``hibrit_indeks_kur``
parçaları, BM25 indeksini ve manifesti bir klasöre yazar ve kesintiden sonra kaldığı
yerden devam edebilir. Testler sahte gömücü (``gomucu``) ve ``tmp_path`` kullanır; ağa
çıkmaz.
"""

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pytest

from ruya.index.build_vectors import HibritIndeks, VektorDeposu, hibrit_indeks_kur
from ruya.index.parcalar import Parca
from ruya.schemas import Madde
from ruya.text.turkce import arama_terimleri

MODEL_ADI = "sahte/gomucu-1"


# --- Yardımcılar -------------------------------------------------------------


def _madde(entry_id: str, metin_tr: str) -> Madde:
    """Testte kullanılacak en küçük geçerli Madde."""
    return Madde(
        entry_id=entry_id,
        kaynak=entry_id.split(":")[0],
        eser="Test Eseri",
        yazar="Test Yazarı",
        gelenek="islami_klasik",
        dil="tr",
        lisans="PD",
        konum={"satir": 1},
        metin_asli="(asıl metin)",
        metin_tr=metin_tr,
    )


def _vektorler(metinler: list[str], boyut: int = 4) -> list[list[float]]:
    """Deterministik sahte gömücü: her metinden bir birim vektör üretir."""
    cikti: list[list[float]] = []
    for metin in metinler:
        tohum = int.from_bytes(hashlib.sha256(metin.encode("utf-8")).digest()[:4], "big")
        rng = np.random.default_rng(tohum)
        dizi = rng.normal(size=boyut)
        dizi = dizi / np.linalg.norm(dizi)
        cikti.append([float(x) for x in dizi])
    return cikti


class SahteGomucu:
    """Çağrılan metinleri kaydeden sahte gömücü; istenirse belirli çağrıda patlar."""

    def __init__(self, *, hata_cagrisi: int | None = None) -> None:
        self.cagrilar: list[list[str]] = []
        self.hata_cagrisi = hata_cagrisi

    def __call__(self, metinler: list[str]) -> list[list[float]]:
        self.cagrilar.append(list(metinler))
        if self.hata_cagrisi is not None and len(self.cagrilar) >= self.hata_cagrisi:
            raise RuntimeError("gömücü hatası (kasıtlı)")
        return _vektorler(metinler)


def _girdilen_metinler(gomucu: SahteGomucu) -> list[str]:
    return [metin for cagri in gomucu.cagrilar for metin in cagri]


def _manifest(klasor: Path) -> dict:
    return json.loads((klasor / "manifest.json").read_text(encoding="utf-8"))


def _id_ozeti(entry_idler: list[str]) -> str:
    """Manifestteki giriş kimliği özeti: kimliklerin '\\n' ile birleştirilmiş sha256'sı."""
    return hashlib.sha256("\n".join(entry_idler).encode("utf-8")).hexdigest()


# --- VektorDeposu ------------------------------------------------------------


def test_vektor_deposu_satirlari_normalize_eder():
    matris = np.array([[3.0, 4.0], [0.0, 2.0]], dtype=np.float32)

    depo = VektorDeposu(matris)

    np.testing.assert_allclose(np.linalg.norm(depo.matris, axis=1), [1.0, 1.0])
    np.testing.assert_allclose(depo.matris[0], [0.6, 0.8])


def test_vektor_deposu_ara_kosinus_skorlarini_azalan_sirada_verir():
    depo = VektorDeposu(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))

    sonuc = depo.ara(np.array([1.0, 0.0]), k=3)

    assert [i for i, _ in sonuc] == [0, 2, 1]
    assert sonuc[0][1] == pytest.approx(1.0)
    assert sonuc[1][1] == pytest.approx(math.cos(math.pi / 4))
    assert sonuc[2][1] == pytest.approx(0.0)


def test_vektor_deposu_ara_k_adet_sonuc_verir():
    depo = VektorDeposu(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]))

    sonuc = depo.ara(np.array([1.0, 0.0]), k=2)

    assert len(sonuc) == 2
    assert [i for i, _ in sonuc] == [0, 2]


# --- hibrit_indeks_kur: dosyalar --------------------------------------------


def test_hibrit_indeks_kur_butun_dosyalari_yazar(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
    ]

    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    for ad in (
        "parcalar.jsonl",
        "vektorler.npy",
        "bm25.json",
        "manifest.json",
    ):
        assert (tmp_path / ad).is_file(), f"{ad} yazılmadı"


def test_vektorler_npy_float32_ve_parca_sayisi_kadar_satir(tmp_path: Path):
    maddeler = [_madde("nablusi:000001", "yılan görmek güzeldir")]

    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    matris = np.load(tmp_path / "vektorler.npy")
    assert matris.dtype == np.float32
    assert matris.shape[0] == 1  # tek madde, tek parça
    assert matris.shape[1] == 4  # sahte gömücünün boyutu


def test_parcalar_jsonl_parca_nesnelerini_tasir(tmp_path: Path):
    maddeler = [_madde("nablusi:000001", "yılan görmek güzeldir")]

    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    satirlar = [
        json.loads(s) for s in (tmp_path / "parcalar.jsonl").read_text("utf-8").splitlines() if s
    ]
    assert len(satirlar) == 1
    assert satirlar[0]["parca_id"] == "nablusi:000001#0"
    assert satirlar[0]["entry_id"] == "nablusi:000001"
    assert satirlar[0]["metin"] == "yılan görmek güzeldir"
    assert satirlar[0]["baglamli_metin"].endswith("yılan görmek güzeldir")


# --- hibrit_indeks_kur: gömücü ve BM25 girdisi -------------------------------


def test_gomucu_baglamli_metni_alir(tmp_path: Path):
    maddeler = [_madde("nablusi:000001", "yılan görmek güzeldir")]
    gomucu = SahteGomucu()

    hibrit_indeks_kur(maddeler, gomucu, tmp_path, model=MODEL_ADI)

    parcalar = HibritIndeks.yukle(tmp_path, maddeler).parca_listesi("nablusi:000001")
    assert len(parcalar) == 1
    assert parcalar[0].baglamli_metin in _girdilen_metinler(gomucu)
    assert parcalar[0].baglamli_metin.startswith("Test Eseri · Test Yazarı.")


def test_bm25_terimleri_baglamli_metinden_hesaplanir(tmp_path: Path):
    # Yalnızca önekte geçen "bölüm" terimi, bağlamlı metinden üretildiğini kanıtlar.
    maddeler = [
        Madde(
            entry_id="nablusi:000001",
            kaynak="nablusi",
            eser="Test Eseri",
            yazar="Test Yazarı",
            gelenek="islami_klasik",
            dil="tr",
            lisans="PD",
            konum={"satir": 1, "bab": "Rüyalar"},
            metin_asli="(asıl metin)",
            metin_tr="yılan görmek güzeldir",
        )
    ]

    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    indeks = HibritIndeks.yukle(tmp_path, maddeler)
    parcalar = indeks.parca_listesi("nablusi:000001")
    beklenen = arama_terimleri(parcalar[0].baglamli_metin)
    onek_terimi = arama_terimleri("Bölüm")[0]  # yalnızca önekte geçer
    assert onek_terimi in beklenen
    assert onek_terimi not in arama_terimleri(parcalar[0].metin)
    sonuc = indeks.bm25_ara([onek_terimi], k=5)
    assert [p.parca_id for p, _ in sonuc] == ["nablusi:000001#0"]


# --- hibrit_indeks_kur: manifest ---------------------------------------------


def test_manifest_bilgileri(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
    ]

    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    manifest = _manifest(tmp_path)
    assert manifest["parca_sayisi"] == 2
    assert manifest["boyut"] == 4
    assert manifest["model"] == MODEL_ADI
    assert manifest["kimlik_ozeti"] == _id_ozeti([m.entry_id for m in maddeler])


# --- hibrit_indeks_kur: kesintiden sonra devam -------------------------------


def test_kesintiden_sonra_yalniz_eksik_parcalar_gomulur(tmp_path: Path):
    # 25 parça, yığın 1 → 25 yığın. Gömücü 23. çağrıda patlar; ilerleme 20. yığından
    # sonra kaydedilmiş olmalı, ikinci koşu yalnızca kalan parçaları gömmeli.
    maddeler = [_madde(f"nablusi:{i:06d}", f"yılan görmek güzeldir {i}") for i in range(1, 26)]
    basarisiz = SahteGomucu(hata_cagrisi=23)

    with pytest.raises(RuntimeError):
        hibrit_indeks_kur(maddeler, basarisiz, tmp_path, model=MODEL_ADI, yigin=1)

    assert (tmp_path / "vektorler.tmp.npy").is_file()
    ilerleme = np.load(tmp_path / "vektorler.tmp.npy")
    assert ilerleme.shape == (20, 4)  # 20. yığına kadar gömülen parçalar

    # Patlayan çağrı da kaydedildiği için son çağrı hariç tutulur.
    ilk_kosum = _girdilen_metinler(basarisiz)[:-1]
    assert len([m for m in ilk_kosum if m.startswith("Test Eseri")]) == 22

    tamamlayici = SahteGomucu()
    hibrit_indeks_kur(maddeler, tamamlayici, tmp_path, model=MODEL_ADI, yigin=1)

    ikinci_parcalar = [m for m in _girdilen_metinler(tamamlayici) if m.startswith("Test Eseri")]
    # Kaydedilen ilerleme 20 parça; yalnızca 21–25 yeniden gömülür.
    assert ikinci_parcalar == [
        f"Test Eseri · Test Yazarı.\nyılan görmek güzeldir {i}" for i in range(21, 26)
    ]

    matris = np.load(tmp_path / "vektorler.npy")
    assert matris.shape == (25, 4)
    indeks = HibritIndeks.yukle(tmp_path, maddeler)
    assert len(indeks.parca_listesi("nablusi:000001")) == 1
    assert len(indeks.parca_listesi("nablusi:000025")) == 1


def test_yigin_gomucuye_yigin_buyuklugunde_cagri_yapar(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
        _madde("nablusi:000003", "at görmek iyidir"),
    ]
    gomucu = SahteGomucu()

    hibrit_indeks_kur(maddeler, gomucu, tmp_path, model=MODEL_ADI, yigin=2)

    parca_cagrilari = [c for c in gomucu.cagrilar if c and c[0].startswith("Test Eseri")]
    assert [len(c) for c in parca_cagrilari] == [2, 1]


def test_terimler_islevi_bm25_terimlerini_uretir(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
    ]

    def terimler(metin: str) -> list[str]:
        return ["ozel"] if "yılan" in metin else []

    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI, terimler=terimler)

    indeks = HibritIndeks.yukle(tmp_path, maddeler)
    sonuc = indeks.bm25_ara(["ozel"], k=5)
    assert [p.parca_id for p, _ in sonuc] == ["nablusi:000001#0"]


# --- HibritIndeks.yukle ------------------------------------------------------


def test_yukle_eksik_klasorde_file_not_found_verir(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        HibritIndeks.yukle(tmp_path / "yok", [])


def test_yukle_kimlik_ozeti_tutmazsa_value_error_verir(tmp_path: Path):
    maddeler = [_madde("nablusi:000001", "yılan görmek güzeldir")]
    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    farkli_maddeler = [_madde("nablusi:000002", "yılan görmek güzeldir")]
    with pytest.raises(ValueError):
        HibritIndeks.yukle(tmp_path, farkli_maddeler)


# --- HibritIndeks: arama -----------------------------------------------------


def test_bm25_ara_baglamli_metne_gore_getirir(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
    ]
    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    indeks = HibritIndeks.yukle(tmp_path, maddeler)
    sonuc = indeks.bm25_ara(arama_terimleri("yılan"), k=5)

    assert [p.parca_id for p, _ in sonuc] == ["nablusi:000001#0"]
    assert sonuc[0][1] > 0.0


def test_vektor_ara_parcalari_skorla_siralar(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
    ]
    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    indeks = HibritIndeks.yukle(tmp_path, maddeler)
    parcalar = indeks.parca_listesi("nablusi:000001")
    sorgu = np.asarray(_vektorler([parcalar[0].baglamli_metin])[0])

    sonuc = indeks.vektor_ara(sorgu, k=2)

    assert [p.parca_id for p, _ in sonuc] == ["nablusi:000001#0", "nablusi:000002#0"]
    assert sonuc[0][1] == pytest.approx(1.0)
    assert sonuc[0][1] > sonuc[1][1]


def test_parca_listesi_girisin_parcalarini_verir(tmp_path: Path):
    maddeler = [
        _madde("nablusi:000001", "yılan görmek güzeldir"),
        _madde("nablusi:000002", "denizde yıkanmak hayırdır"),
    ]
    hibrit_indeks_kur(maddeler, _vektorler, tmp_path, model=MODEL_ADI)

    indeks = HibritIndeks.yukle(tmp_path, maddeler)

    parcalar = indeks.parca_listesi("nablusi:000001")
    assert [p.parca_id for p in parcalar] == ["nablusi:000001#0"]
    assert isinstance(parcalar[0], Parca)
    assert indeks.parca_listesi("nablusi:000009") == []
