"""İbn Sîrîn (OpenITI mARkdown) ayrıştırıcısının birim testleri.

Küçük mARkdown dosyaları ``tmp_path`` içinde yazılır; veri gerektirmez.
Kurallar ``data/interim/ceviri/_betikler/parcala2.py`` içindeki ``ibn_sirin()``
işlevinden gelir: ``#META#Header#End#`` sonrası başlar, ``###`` babı belirler,
``~~`` önceki paragrafı sürdürür, ``# Page…`` sonrasındaki ilk ``# `` satırı
özel bir kalıpla başlamıyorsa önceki paragrafa eklenir.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ruya.ingest.ibn_sirin import ayristir
from ruya.ingest.kaynaklar import KAYNAKLAR, OPENITI_ATIF_NOTU
from ruya.schemas import Madde

# Başlıktan sonraki satırlar; yorumlardaki numaralar 1 tabanlı satır numarasıdır.
ORNEK_SATIRLAR = [
    "# Bu satır başlıktan önce, atlanmalı",  # 1
    "#META#Header#End#",  # 2
    "# (başlangıç) ilk madde",  # 3
    "# PageV01P001",  # 4
    "### | باب الحاء ms123",  # 5
    "# - (حية) يرى في المنام ms042",  # 6
    "~~ وتزيد الحية",  # 7
    "# PageV01P002",  # 8
    "# نص   تابع للحية",  # 9
    "# (ومن رأى) أنه",  # 10
    "# PageV01P003",  # 11
    "# - (فراش) شيء",  # 12
    "# ms999",  # 13
    "### | باب الألف",  # 14
    "# (فصل) نص",  # 15
    "# PageV01P004",  # 16
    "# - (ماء) نص الماء",  # 17
]


def _yaz(tmp_path: Path, satirlar: list[str]) -> Path:
    """Satırları UTF-8 bir ham dosyaya yazar."""
    yol = tmp_path / "ibn_sirin.txt"
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return yol


@pytest.fixture
def maddeler(tmp_path: Path) -> list[Madde]:
    return list(ayristir(_yaz(tmp_path, ORNEK_SATIRLAR)))


def test_maddeler_semaya_uyar(maddeler):
    assert maddeler
    assert all(isinstance(m, Madde) for m in maddeler)


def test_basliktan_onceki_satirlar_atlanir(maddeler):
    # 1. satır "# " ile başlasa da #META#Header#End# öncesi okunmaz.
    assert [m.entry_id for m in maddeler] == [
        "ibn_sirin:000003",
        "ibn_sirin:000006",
        "ibn_sirin:000010",
        "ibn_sirin:000012",
        "ibn_sirin:000015",
        "ibn_sirin:000017",
    ]


def test_kunye_alanlari_kaynaklardan_gelir(maddeler):
    bilgi = KAYNAKLAR["ibn_sirin"]
    for madde in maddeler:
        assert madde.kaynak == "ibn_sirin"
        assert madde.eser == bilgi.eser
        assert madde.yazar == bilgi.yazar
        assert madde.gelenek == bilgi.gelenek
        assert madde.dil == bilgi.dil
        assert madde.lisans == bilgi.lisans


def test_atif_notu_ve_bos_alanlar(maddeler):
    for madde in maddeler:
        assert madde.atif_notu == OPENITI_ATIF_NOTU
        assert madde.baslik_asli is None
        assert madde.ust_madde_id is None


def test_bab_ve_satir_numarasi(maddeler):
    assert [m.konum.bab for m in maddeler] == [
        None,  # ilk ### satırından önce
        "باب الحاء",
        "باب الحاء",
        "باب الحاء",
        "باب الألف",
        "باب الألف",
    ]
    assert [m.konum.satir for m in maddeler] == [3, 6, 10, 12, 15, 17]


def test_sayfa_paragraf_satirindan_sonraki_ilk_isaret(maddeler):
    assert [m.konum.sayfa for m in maddeler] == [
        "V01P001",
        "V01P002",
        "V01P003",
        "V01P004",
        "V01P004",
        None,  # sonrasında sayfa işareti yok
    ]


def test_metin_temizligi(maddeler):
    assert [m.metin_asli for m in maddeler] == [
        "(başlangıç) ilk madde",
        # ms042 silinir, ~~ satırı boşlukla eklenir, sayfa sonrası düz satır eklenir,
        # çoklu boşluk tek boşluğa iner.
        "(حية) يرى في المنام وتزيد الحية نص تابع للحية",
        "(ومن رأى) أنه",
        "(فراش) شيء",
        "(فصل) نص",
        "(ماء) نص الماء",
    ]


def test_bos_metinli_madde_atilir(maddeler):
    # 13. satır yalnızca "ms999" taşır; temizlikten sonra boş kalır ve kayda girmez.
    assert "ibn_sirin:000013" not in {m.entry_id for m in maddeler}


@pytest.mark.parametrize(
    ("satir", "beklenen_metin"),
    [
        ("- yeni madde", "yeni madde"),
        ("(yeni madde", "(yeni madde"),
        ("[yeni madde", "[yeni madde"),
        ("ومن رأى yeni madde", "ومن رأى yeni madde"),
        ("من رأى yeni madde", "من رأى yeni madde"),
        ("فصل yeni madde", "فصل yeni madde"),
    ],
)
def test_sayfa_sonrasi_ozel_kalipli_satir_yeni_madde(tmp_path, satir, beklenen_metin):
    yol = _yaz(
        tmp_path,
        ["#META#Header#End#", "# (önceki) metin", "# PageV01P001", f"# {satir}"],
    )
    maddeler = list(ayristir(yol))
    assert [m.entry_id for m in maddeler] == ["ibn_sirin:000002", "ibn_sirin:000004"]
    assert maddeler[0].metin_asli == "(önceki) metin"
    assert maddeler[1].metin_asli == beklenen_metin


def test_sayfa_sonrasi_duz_satir_onceki_paragrafa_eklenir(tmp_path):
    yol = _yaz(
        tmp_path,
        ["#META#Header#End#", "# (önceki) metin", "# PageV01P001", "# düz devam"],
    )
    maddeler = list(ayristir(yol))
    assert len(maddeler) == 1
    assert maddeler[0].entry_id == "ibn_sirin:000002"
    assert maddeler[0].metin_asli == "(önceki) metin düz devam"


def test_bab_satiri_sayfa_basini_sifirlar(tmp_path):
    yol = _yaz(
        tmp_path,
        [
            "#META#Header#End#",
            "# (önceki) metin",
            "# PageV01P001",
            "### | باب الباء",
            "# düz yeni metin",
        ],
    )
    maddeler = list(ayristir(yol))
    assert [m.entry_id for m in maddeler] == ["ibn_sirin:000002", "ibn_sirin:000005"]
    assert maddeler[1].konum.bab == "باب الباء"
    assert maddeler[1].metin_asli == "düz yeni metin"
    # Sayfa işareti paragraf satırından önce: "en az paragraf satırı" kuralı gereği yok.
    assert maddeler[1].konum.sayfa is None
