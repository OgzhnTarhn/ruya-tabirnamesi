"""Freud ayrıştırıcısının birim testleri (docs/02, docs/12).

Veri gerektirmez: ham metin tmp_path içine yazılır, satır aralıkları elden verilir.
Kural kaynağı: data/interim/ceviri/_betikler/parcala2.py içindeki ``freud()``.
"""

import pytest

from ruya.ingest import freud
from ruya.ingest.kaynaklar import KAYNAKLAR

KUNYE = KAYNAKLAR["freud"]


def _yaz(tmp_path, satirlar):
    """Satırları 1 tabanlı numaralandırmayla aynen dosyaya yazar."""
    yol = tmp_path / "freud.txt"
    yol.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    return yol


def test_araliklar_sabiti():
    assert getattr(freud, "ARALIKLAR", None) == ((62, 275), (303, 17624))


def test_paragraflar_bolumler_ve_dipnot(tmp_path):
    satirlar = [
        "     DREAM PSYCHOLOGY",  # 1: bölüm başlığı, aynı zamanda madde
        "",  # 2
        "The first paragraph is",  # 3
        "wrapped over two lines.",  # 4
        "",  # 5
        "     SECOND SECTION",  # 6: yeni bölüm
        "",  # 7
        "Footnote A:",  # 8: sonraki paragrafla birleşir
        "",  # 9
        "This footnote text belongs",  # 10
        "to the footnote.",  # 11
        "",  # 12
        "IGNORED OUTSIDE RANGE",  # 13: aralık dışı
        "",  # 14
        "     THIRD SECTION",  # 15
        "",  # 16
        "Last paragraph.",  # 17
        "",  # 18
        "Footnote B:",  # 19: son paragraf, birleşecek paragraf yok
    ]
    ham = _yaz(tmp_path, satirlar)

    maddeler = list(freud.ayristir(ham, araliklar=((1, 11), (15, 19))))

    assert [m.entry_id for m in maddeler] == [
        "freud:000001",
        "freud:000003",
        "freud:000006",
        "freud:000008",
        "freud:000015",
        "freud:000017",
        "freud:000019",
    ]
    assert [m.konum.satir for m in maddeler] == [1, 3, 6, 8, 15, 17, 19]
    assert [m.konum.bab for m in maddeler] == [
        "DREAM PSYCHOLOGY",
        "DREAM PSYCHOLOGY",
        "SECOND SECTION",
        "SECOND SECTION",
        "THIRD SECTION",
        "THIRD SECTION",
        "THIRD SECTION",
    ]
    assert [m.metin_asli for m in maddeler] == [
        "DREAM PSYCHOLOGY",
        "The first paragraph is wrapped over two lines.",
        "SECOND SECTION",
        "Footnote A: This footnote text belongs to the footnote.",
        "THIRD SECTION",
        "Last paragraph.",
        "Footnote B:",
    ]


def test_kunye_alanlari_ve_bos_sozluk(tmp_path):
    ham = _yaz(tmp_path, ["     A SECTION", "", "Some text."])

    maddeler = list(freud.ayristir(ham, araliklar=((1, 3),)))

    assert maddeler
    for madde in maddeler:
        assert madde.kaynak == "freud"
        assert madde.eser == KUNYE.eser
        assert madde.yazar == KUNYE.yazar
        assert madde.gelenek == KUNYE.gelenek
        assert madde.dil == KUNYE.dil
        assert madde.lisans == KUNYE.lisans
        assert madde.atif_notu == KUNYE.atif_notu
        assert madde.symbol_ids == []


def test_bolum_olmayan_girintili_paragraflar(tmp_path):
    satirlar = [
        "     FIRST SECTION",  # 1
        "",  # 2
        "     ALL CAPS BUT",  # 3: üç satır → bölüm değil
        "     THREE LINES HERE",  # 4
        "     SO NOT A SECTION",  # 5
        "",  # 6
        "     lower case indented",  # 7: büyük harf değil → bölüm değil
        "",  # 8
        "     TWO LINE SECTION",  # 9: iki satır, büyük harf → bölüm
        "     CONTINUES HERE",  # 10
        "",  # 11
        "    FOUR SPACES ONLY",  # 12: beş boşluk yok → bölüm değil
    ]
    ham = _yaz(tmp_path, satirlar)

    maddeler = list(freud.ayristir(ham, araliklar=((1, 12),)))

    assert [m.entry_id for m in maddeler] == [
        "freud:000001",
        "freud:000003",
        "freud:000007",
        "freud:000009",
        "freud:000012",
    ]
    assert [m.konum.bab for m in maddeler] == [
        "FIRST SECTION",
        "FIRST SECTION",
        "FIRST SECTION",
        "TWO LINE SECTION CONTINUES HERE",
        "TWO LINE SECTION CONTINUES HERE",
    ]
    assert maddeler[1].metin_asli == "ALL CAPS BUT THREE LINES HERE SO NOT A SECTION"
    assert maddeler[3].metin_asli == "TWO LINE SECTION CONTINUES HERE"


def test_aralik_disi_satirlar_yok_sayilir(tmp_path):
    satirlar = [
        "Before the range.",  # 1
        "",  # 2
        "     IN RANGE",  # 3
        "",  # 4
        "Inside the range.",  # 5
        "",  # 6
        "After the range.",  # 7
    ]
    ham = _yaz(tmp_path, satirlar)

    maddeler = list(freud.ayristir(ham, araliklar=((3, 5),)))

    assert [m.entry_id for m in maddeler] == ["freud:000003", "freud:000005"]
    assert [m.metin_asli for m in maddeler] == ["IN RANGE", "Inside the range."]


def test_bos_aralik_madde_uretmez(tmp_path):
    ham = _yaz(tmp_path, ["     A SECTION", "", "Some text."])

    assert list(freud.ayristir(ham, araliklar=((2, 2),))) == []


def test_ilk_bolumden_once_bab_none(tmp_path):
    satirlar = [
        "Introductory paragraph.",  # 1
        "",  # 2
        "     LATER SECTION",  # 3
    ]
    ham = _yaz(tmp_path, satirlar)

    maddeler = list(freud.ayristir(ham, araliklar=((1, 3),)))

    assert maddeler[0].konum.bab is None
    assert maddeler[1].konum.bab == "LATER SECTION"


@pytest.mark.parametrize("satir_sayisi", [1, 2])
def test_bolum_maddesi_kendi_babidir(tmp_path, satir_sayisi):
    satirlar = ["     ONE LINE" if satir_sayisi == 1 else "     TWO LINES", ""]
    if satir_sayisi == 2:
        satirlar.insert(1, "     OF HEADING")
    ham = _yaz(tmp_path, satirlar)

    maddeler = list(freud.ayristir(ham, araliklar=((1, satir_sayisi),)))

    assert len(maddeler) == 1
    assert maddeler[0].konum.bab == maddeler[0].metin_asli
