import sys
import types
from pathlib import Path

import pytest

from ruya import config
from ruya.config import Ayarlar
from ruya.hatalar import VeriYoluYok


@pytest.fixture
def temiz_ortam(monkeypatch):
    for ad in ("RUYA_DATA_DIR", "RUYA_WORK_DIR", "RUYA_LLM_CACHE", "RUYA_GECMIS"):
        monkeypatch.delenv(ad, raising=False)
    monkeypatch.delitem(sys.modules, "google.colab", raising=False)


def test_bilgisayarda_veri_yolu_yok(temiz_ortam):
    ayar = Ayarlar()
    assert ayar.data_dir is None
    with pytest.raises(VeriYoluYok):
        _ = ayar.maddeler_dosyasi


def test_colabda_drive_yollari_varsayilan(temiz_ortam, monkeypatch):
    monkeypatch.setitem(sys.modules, "google.colab", types.ModuleType("google.colab"))
    ayar = Ayarlar()
    assert ayar.data_dir == config.COLAB_VERI_KLASORU
    assert ayar.chroma_klasoru == config.COLAB_CALISMA_KLASORU / "chroma"
    assert ayar.maddeler_dosyasi == (
        config.COLAB_VERI_KLASORU / "data" / "processed" / "entries.jsonl"
    )


def test_ortam_degiskenleri_okunur(temiz_ortam, monkeypatch, tmp_path):
    monkeypatch.setenv("RUYA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("RUYA_LLM_CACHE", "off")
    monkeypatch.setenv("RUYA_GECMIS", "on")
    ayar = Ayarlar()
    assert ayar.llm_onbellek_klasoru == tmp_path / "cache" / "llm"
    assert ayar.llm_cache is False
    assert ayar.gecmis is True


def test_varsayilanlar_gizlilikten_yana(temiz_ortam):
    ayar = Ayarlar()
    assert ayar.gecmis is False
    assert ayar.kaynak_basina_n == 2


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
