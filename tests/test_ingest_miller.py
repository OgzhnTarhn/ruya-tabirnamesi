"""ruya.ingest.miller.ayristir için verisiz birim testleri.

Gutenberg #926 metninin küçük bir taklidi ``tmp_path`` içine utf-8 olarak yazılır; gerçek
veri kullanılmaz. Satır numaraları dosyanın tamamına göredir (Gutenberg işaretlerinden
önceki satırlar dahil), çünkü ``entry_id`` bu numaradan türetilir.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ruya.ingest.kaynaklar import KAYNAKLAR
from ruya.ingest.miller import ayristir

# Satır numaraları yorumlarda verilmiştir; başlıklar 6, 13 ve 20. satırdadır.
METIN = """\
_BEFORE_START_.
This heading is outside the Gutenberg markers.
*** START OF THE PROJECT GUTENBERG EBOOK ***
Preface paragraph that is not an entry.

_ABBEY_.
To see an abbey in your dreams, denotes peace.
You will find
happiness.

Second paragraph with a footnote[12] mark.

_ABYSS_.[12]
To dream of an abyss foretells trouble.

S.

"The heavens declare the glory of God."

_ACORN_.
Acorns signify prosperity.

INDEX

_AFTER_INDEX_.
Should not appear.
*** END OF THE PROJECT GUTENBERG EBOOK ***
_AFTER_END_.
Should not appear either.
"""


@pytest.fixture
def maddeler(tmp_path: Path) -> list:
    """Örnek metni yazıp ayrıştırıcının bütün maddelerini döndürür."""
    ham_dosya = tmp_path / "miller.txt"
    ham_dosya.write_text(METIN, encoding="utf-8")
    return list(ayristir(ham_dosya))


def _basliklara_gore(maddeler: list) -> dict[str, object]:
    return {m.baslik_asli: m for m in maddeler}


def test_yalnizca_gutenberg_isaretleri_arasindaki_metin_kullanilir(maddeler):
    basliklar = [m.baslik_asli for m in maddeler]

    assert basliklar == ["ABBEY", "ABYSS", "ACORN"]
    assert "BEFORE_START" not in basliklar
    assert "AFTER_END" not in basliklar
    assert "AFTER_INDEX" not in basliklar


def test_baslik_ve_kimlik_baslik_satirindan_turetilir(maddeler):
    maddeler = _basliklara_gore(maddeler)

    assert maddeler["ABBEY"].entry_id == "miller:000006"
    assert maddeler["ABYSS"].entry_id == "miller:000013"
    assert maddeler["ACORN"].entry_id == "miller:000020"

    assert maddeler["ABBEY"].konum.satir == 6
    assert maddeler["ABYSS"].konum.satir == 13
    assert maddeler["ACORN"].konum.satir == 20

    for madde in maddeler.values():
        assert madde.ust_madde_id is None


def test_paragraflar_bos_satirla_satir_kaymalari_boslukla_birlesir(maddeler):
    abbey = _basliklara_gore(maddeler)["ABBEY"]

    assert abbey.metin_asli == (
        "To see an abbey in your dreams, denotes peace. You will find happiness."
        "\n\n"
        "Second paragraph with a footnote mark."
    )


def test_dipnot_isareti_metinden_silinir(maddeler):
    abbey = _basliklara_gore(maddeler)["ABBEY"]

    assert "[12]" not in abbey.metin_asli
    assert "footnote mark" in abbey.metin_asli


def test_buyuk_harf_paragrafi_ve_sonrasi_atilir(maddeler):
    abyss = _basliklara_gore(maddeler)["ABYSS"]

    assert abyss.metin_asli == "To dream of an abyss foretells trouble."
    assert "S." not in abyss.metin_asli
    assert "heavens" not in abyss.metin_asli


def test_index_satirinda_ayristirma_durur(maddeler):
    acorn = _basliklara_gore(maddeler)["ACORN"]

    assert acorn.metin_asli == "Acorns signify prosperity."
    assert "INDEX" not in acorn.metin_asli


def test_kunye_kaynaklardan_gelir(maddeler):
    bilgi = KAYNAKLAR["miller"]

    for madde in maddeler:
        assert madde.kaynak == "miller"
        assert madde.eser == bilgi.eser
        assert madde.yazar == bilgi.yazar
        assert madde.gelenek == bilgi.gelenek
        assert madde.dil == bilgi.dil
        assert madde.lisans == bilgi.lisans
