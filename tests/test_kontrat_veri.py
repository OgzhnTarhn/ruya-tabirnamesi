"""Kontrat testleri: Drive'daki gerçek veri şemaya uyuyor mu? (docs/03, bölüm 5.5)

Yalnızca veri varken çalışır (Colab). Bilgisayarda kendiliğinden atlanır.
Colab'de: ``!cd /content/ruya-tabirnamesi && python -m pytest -m veri``
"""

import pytest

from ruya.config import Ayarlar
from ruya.dosya import jsonl_oku
from ruya.hatalar import VeriYoluYok
from ruya.ingest.kaynaklar import LISANS_KODLARI
from ruya.schemas import Madde

pytestmark = pytest.mark.veri


@pytest.fixture(scope="module")
def maddeler() -> list[Madde]:
    try:
        yol = Ayarlar().maddeler_dosyasi
    except VeriYoluYok:
        pytest.skip("veri yolu yok (bilgisayarda beklenen durum)")
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
