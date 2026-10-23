"""Hazır gelen küçük yardımcıların testleri: önbellek anahtarı, maliyet, talimat, JSONL, log."""

import datetime as dt
import json

import pytest

from ruya.config import Ayarlar
from ruya.dosya import jsonl_oku, jsonl_yaz
from ruya.kayit import gecmise_yaz, sorgu_logla
from ruya.llm.client import maliyet_hesapla, onbellek_anahtari
from ruya.llm.talimatlar import talimat_oku
from ruya.schemas import Madde, RuyaGirdisi, SorguKaydi


def test_onbellek_anahtari_sira_bagimsiz():
    a = onbellek_anahtari({"model": "m", "messages": [{"role": "user", "content": "rüya"}]})
    b = onbellek_anahtari({"messages": [{"content": "rüya", "role": "user"}], "model": "m"})
    c = onbellek_anahtari({"model": "m", "messages": [{"role": "user", "content": "rüyа"}]})
    assert a == b
    assert a != c
    assert len(a) == 64


def test_maliyet_hesabi():
    # Opus 5.5: 4 $ / 20 $ milyon token başına
    assert maliyet_hesapla("claude-opus-5-5", 1_000_000, 0) == pytest.approx(4.0)
    assert maliyet_hesapla("claude-opus-5-5", 10_000, 1_500) == pytest.approx(0.07)
    assert maliyet_hesapla("claude-opus-5-5", 10_000, 1_500, batch=True) == pytest.approx(0.035)
    assert maliyet_hesapla("claude-opus-5-5", 0, 0, onbellek_okuma_token=1_000_000) == (
        pytest.approx(0.20)
    )
    with pytest.raises(KeyError):
        maliyet_hesapla("bilinmeyen-model", 1, 1)


def test_talimat_oku(tmp_path):
    (tmp_path / "sentez_v1.md").write_text("  Yalnızca kaynaklara dayan.\n", encoding="utf-8")
    assert talimat_oku("sentez_v1", klasor=tmp_path) == "Yalnızca kaynaklara dayan."
    with pytest.raises(ValueError):
        talimat_oku("sentez", klasor=tmp_path)
    with pytest.raises(FileNotFoundError):
        talimat_oku("sentez_v2", klasor=tmp_path)


def test_jsonl_gidis_donus(tmp_path, ornek_maddeler):
    maddeler = [Madde.model_validate(m) for m in ornek_maddeler]
    yol = tmp_path / "alt" / "entries.jsonl"
    assert jsonl_yaz(maddeler, yol) == 3
    assert list(jsonl_oku(yol, Madde)) == maddeler


def test_jsonl_hatali_satir_numarasi(tmp_path, ornek_maddeler):
    yol = tmp_path / "bozuk.jsonl"
    bozuk = {**ornek_maddeler[0], "lisans": ""}
    yol.write_text(
        json.dumps(ornek_maddeler[1]) + "\n" + json.dumps(bozuk) + "\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match=r"bozuk\.jsonl:2"):
        list(jsonl_oku(yol, Madde))


def _kayit():
    return SorguKaydi(
        zaman=dt.datetime(2026, 11, 20, tzinfo=dt.UTC), girdi=RuyaGirdisi(metin="gizli rüya")
    )


def test_sorgu_logu_ruya_metni_icermez(tmp_path):
    yol = sorgu_logla(_kayit(), Ayarlar(data_dir=tmp_path))
    assert yol == tmp_path / "logs" / "sorgular.jsonl"
    assert "gizli rüya" not in yol.read_text(encoding="utf-8")


def test_gecmis_varsayilan_olarak_kapali(tmp_path):
    assert gecmise_yaz(_kayit(), Ayarlar(data_dir=tmp_path)) is None
    assert not (tmp_path / "gecmis").exists()
    yol = gecmise_yaz(_kayit(), Ayarlar(data_dir=tmp_path, gecmis=True))
    assert yol.name == "2026-11.jsonl"
    assert "gizli rüya" in yol.read_text(encoding="utf-8")
