"""Nablusi (OpenITI mARkdown) ayrıştırıcısının birim testleri (docs/02, bölüm 2).

Küçük satır içi örnekler ``tmp_path`` altına yazılır; gerçek veri gerekmez.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ruya.ingest.kaynaklar import KAYNAKLAR
from ruya.ingest.nablusi import ayristir
from ruya.schemas import Madde

ENTRY_ID = re.compile(r"^nablusi:\d{6}$")


def _ayristir(tmp_path: Path, satirlar: list[str]) -> list[Madde]:
    """Satırları geçici bir ham dosyaya yazar ve ayrıştırıcıyı çalıştırır."""
    yol = tmp_path / "nablusi.txt"
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return list(ayristir(yol))


def test_meta_basligindan_onceki_satirlar_atilir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Title: Ta'tîrü'l-enâm",
            "# - (yok sayılmalı) bu satır künyeden önce",
            "#META#Header#End#",
            "# - (حية) يرى النائم حية.",
        ],
    )

    assert len(maddeler) == 1
    assert maddeler[0].baslik_asli == "حية"
    assert "yok sayılmalı" not in maddeler[0].metin_asli


def test_bab_basligi_konum_bab_alanini_doldurur(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "### | باب الألف",
            "# - (حية) نص",
        ],
    )

    assert len(maddeler) == 1
    assert maddeler[0].konum.bab == "باب الألف"


def test_bab_basligi_kendi_basina_madde_uretmez(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "### | باب الألف",
            "### | باب الباء",
        ],
    )

    assert maddeler == []


def test_paragraf_ve_tilde_devami_tek_madde_olur(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# - (حية) birinci",
            "~~ ikinci",
            "# PageV01P002",
            "~~ üçüncü",
        ],
    )

    assert len(maddeler) == 1
    metin = maddeler[0].metin_asli
    assert "birinci ikinci üçüncü" in metin
    assert "~~" not in metin
    assert "PageV01P002" not in metin


def test_yalnizca_sayfa_isareti_paragraf_baslatmaz(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# PageV01P001",
            "# - (حية) birinci",
            "# PageV01P002",
            "# PageV01P003",
            "# - (فراش) ikinci",
        ],
    )

    assert len(maddeler) == 2
    assert [m.baslik_asli for m in maddeler] == ["حية", "فراش"]


def test_ms_ve_sayfa_isaretleri_metinden_temizlenir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# - (فراش) نص ms123 PageV01P002 أكثر",
        ],
    )

    assert len(maddeler) == 1
    metin = maddeler[0].metin_asli
    assert "ms123" not in metin
    assert "PageV01P002" not in metin
    assert "نص" in metin
    assert "أكثر" in metin


def test_parantezli_baslik_baslikli_maddedir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# - (حية) يرى النائم حية.",
        ],
    )

    assert len(maddeler) == 1
    madde = maddeler[0]
    assert madde.baslik_asli == "حية"
    assert madde.ust_madde_id is None


@pytest.mark.parametrize("baslik", ["(ومن رأى)", "(ومن رآه)", "(رؤية)"])
def test_alt_isaretli_baslik_alt_paragraftir(tmp_path, baslik):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# - (حية) birinci",
            "# - (فراش) ikinci",
            f"# - {baslik} حية في المنام",
        ],
    )

    assert len(maddeler) == 3
    alt = maddeler[2]
    assert alt.baslik_asli is None
    assert alt.ust_madde_id == "nablusi:000003"


def test_basliksiz_paragraf_kendi_maddesidir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# - giriş paragrafı",
        ],
    )

    assert len(maddeler) == 1
    madde = maddeler[0]
    assert madde.baslik_asli is None
    assert madde.ust_madde_id is None
    assert "giriş paragrafı" in madde.metin_asli


def test_maddeden_sonraki_basliksiz_paragraf_onceki_maddeye_eklenir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "### | باب الألف",
            "# - (حية) birinci",
            "# - devam",
            "### | باب الباء",
            "# - (باب) ikinci",
            "# - devam iki",
        ],
    )

    assert len(maddeler) == 2
    assert maddeler[0].metin_asli.endswith("birinci devam")
    assert maddeler[1].metin_asli.endswith("ikinci devam iki")
    assert [m.entry_id for m in maddeler] == ["nablusi:000003", "nablusi:000006"]


def test_bab_basligi_gecse_de_devam_onceki_maddeye_eklenir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "### | باب الألف",
            "# - (حية) birinci",
            "### | باب الباء",
            "# - devam",
        ],
    )

    assert len(maddeler) == 1
    assert maddeler[0].konum.bab == "باب الألف"
    assert maddeler[0].metin_asli.endswith("birinci devam")


def test_entry_id_satir_numarasindan_alti_haneli_uretilir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "### | باب الألف",
            "# - (حية) birinci",
            "# - (فراش) ikinci",
        ],
    )

    assert [m.entry_id for m in maddeler] == ["nablusi:000003", "nablusi:000004"]
    assert all(ENTRY_ID.match(m.entry_id) for m in maddeler)
    assert [m.konum.satir for m in maddeler] == [3, 4]


def test_konum_sayfa_paragraf_satirindan_sonraki_ilk_isarettir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# PageV01P001",
            "# - (حية) birinci",
            "# PageV01P002",
            "# - (فراش) ikinci",
            "# PageV01P003",
        ],
    )

    assert [m.konum.sayfa for m in maddeler] == ["V01P002", "V01P003"]


def test_kunye_alanlari_kaynaklar_nablusiden_gelir(tmp_path):
    maddeler = _ayristir(
        tmp_path,
        [
            "#META#Header#End#",
            "# - (حية) نص",
        ],
    )

    assert len(maddeler) == 1
    madde = maddeler[0]
    bilgi = KAYNAKLAR["nablusi"]
    assert madde.kaynak == "nablusi"
    assert madde.eser == bilgi.eser
    assert madde.yazar == bilgi.yazar
    assert madde.gelenek == bilgi.gelenek
    assert madde.dil == bilgi.dil
    assert madde.lisans == bilgi.lisans
    assert madde.lisans == "CC-BY-NC-SA-4.0"
    assert madde.atif_notu == bilgi.atif_notu
