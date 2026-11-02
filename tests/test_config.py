from pathlib import Path

import pytest

from ruya import config
from ruya.config import Ayarlar


@pytest.fixture
def temiz_ortam(monkeypatch):
    for ad in (
        "RUYA_DATA_DIR",
        "RUYA_LLM_CACHE",
        "RUYA_GECMIS",
        "RUYA_SORGU_ONBELLEGI",
    ):
        monkeypatch.delenv(ad, raising=False)


def test_varsayilan_veri_yolu_repodaki_data(temiz_ortam):
    ayar = Ayarlar()
    assert ayar.data_dir == config.REPO_KOKU / "data"
    assert ayar.maddeler_dosyasi == config.REPO_KOKU / "data" / "processed" / "entries.jsonl"
    assert ayar.ham_klasoru == config.REPO_KOKU / "data" / "raw"
    assert ayar.chroma_klasoru == config.REPO_KOKU / "data" / "index" / "chroma"


def test_butun_veri_yollari_data_altinda(tmp_path):
    # Gizlilik: git'e girmeyen klasörün dışına hiçbir şey yazılmaz.
    ayar = Ayarlar(data_dir=tmp_path)
    for yol in (
        ayar.ham_klasoru,
        ayar.ara_klasoru,
        ayar.islenmis_klasoru,
        ayar.maddeler_dosyasi,
        ayar.indeks_klasoru,
        ayar.chroma_klasoru,
        ayar.llm_onbellek_klasoru,
        ayar.rapor_klasoru,
        ayar.gecmis_klasoru,
        ayar.log_klasoru,
    ):
        assert yol.is_relative_to(tmp_path)


def test_ortam_degiskenleri_okunur(temiz_ortam, monkeypatch, tmp_path):
    monkeypatch.setenv("RUYA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("RUYA_LLM_CACHE", "off")
    monkeypatch.setenv("RUYA_GECMIS", "on")
    monkeypatch.setenv("RUYA_SORGU_ONBELLEGI", "on")
    ayar = Ayarlar()
    assert ayar.llm_onbellek_klasoru == tmp_path / "cache" / "llm"
    assert ayar.llm_cache is False
    assert ayar.gecmis is True
    assert ayar.sorgu_onbellegi is True


def test_varsayilanlar_gizlilikten_yana(temiz_ortam):
    ayar = Ayarlar()
    assert ayar.gecmis is False
    assert ayar.sorgu_onbellegi is False
    assert ayar.kaynak_basina_n == 1


def test_her_modelin_fiyati_var():
    modeller = {
        config.MODEL_CIKARIM,
        config.MODEL_SENTEZ,
        config.MODEL_CEVIRI,
        config.MODEL_SEMBOL_ATAMA,
        config.MODEL_KOSUL,
    }
    assert modeller <= set(config.FIYATLAR)


def test_repo_yollari_repoyu_gosterir():
    assert (config.REPO_KOKU / "pyproject.toml").is_file()
    assert config.SOZLUK_DOSYASI.parent.name == "sozluk"
    assert isinstance(config.TALIMAT_KLASORU, Path)
