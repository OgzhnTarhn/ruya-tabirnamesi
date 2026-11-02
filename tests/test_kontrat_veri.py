"""Kontrat testleri: data/ altındaki gerçek veri şemaya uyuyor mu? (docs/03, bölüm 5.5)

Yalnızca veri varken çalışır; veri yoksa testler kendiliğinden atlanır.
``uv run pytest -m veri``
"""

import pytest

from ruya.config import Ayarlar
from ruya.dosya import jsonl_oku
from ruya.index.build_symbols import sozlugu_yukle, sozluk_maddeler_tutarliligi
from ruya.ingest.kaynaklar import LISANS_KODLARI
from ruya.schemas import Madde

pytestmark = pytest.mark.veri


@pytest.fixture(scope="module")
def maddeler() -> list[Madde]:
    yol = Ayarlar().maddeler_dosyasi
    if not yol.is_file():
        pytest.skip(f"{yol} henüz yok")
    return list(jsonl_oku(yol, Madde))  # her satır şemaya göre doğrulanır


def test_entry_id_benzersiz(maddeler):
    kimlikler = [m.entry_id for m in maddeler]
    assert len(kimlikler) == len(set(kimlikler))


def test_ust_maddeler_var(maddeler):
    kimlikler = {m.entry_id for m in maddeler}
    eksikler = {m.ust_madde_id for m in maddeler if m.ust_madde_id} - kimlikler
    assert not eksikler


def test_nc_kayitlar_tek_filtreyle_ayrilir(maddeler):
    # İOG-06, V8: lisans alanına göre tek filtre yeterli olmalı
    assert all(m.lisans in LISANS_KODLARI for m in maddeler)


def test_metin_tr_dolu(maddeler):
    eksikler = [m.entry_id for m in maddeler if not (m.metin_tr or "").strip()]
    assert not eksikler, f"metin_tr boş: {', '.join(eksikler[:10])}"


def test_kaynak_sayilari(maddeler):
    beklenen = {"nablusi": 5782, "miller": 2256, "ibn_sirin": 1544, "freud": 1219}
    sayilar: dict[str, int] = {}
    for m in maddeler:
        kaynak = m.entry_id.split(":", 1)[0]
        sayilar[kaynak] = sayilar.get(kaynak, 0) + 1
    assert sayilar == beklenen


def test_sembol_atamasi(maddeler):
    sembollu = [m for m in maddeler if m.symbol_ids]
    assert len(sembollu) >= 1000, f"sembol atanan madde sayısı: {len(sembollu)}"


def test_sozluk_maddeler_tutarli(maddeler):
    sorunlar = sozluk_maddeler_tutarliligi(sozlugu_yukle(), maddeler)
    assert sorunlar == [], "\n".join(sorunlar)


def test_zeyrek_gercek_kok_bulur():
    """Birim testleri kokler'i sahteler; gerçek analizör burada sınanır (eksik NLTK verisi)."""
    if not (Ayarlar().data_dir / "nltk_data").is_dir():
        pytest.skip("NLTK verisi yok: scripts/nltk_kur.py")
    from ruya.text.turkce import kokler

    assert "namaz" in kokler("namazı")
