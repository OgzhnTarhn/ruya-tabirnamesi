"""eval/run_eval.py betiğinin ağsız testleri.

Betik paket değildir; modül olarak yüklenir. Değerlendirme ve bağımlılıklar sahtelerle
değiştirilir, böylece API çağrılmaz ve rapor yazılmaz. Yeni seçeneklerin (``--alt-kume``,
``--n``, ``--sentez-modeli``) değerlendirmeye ve ayarlara doğru geçtiği denetlenir.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ruya import config
from ruya.pipeline import synthesize

BETIK = Path(__file__).resolve().parents[1] / "eval" / "run_eval.py"


@pytest.fixture(scope="module")
def run_eval():
    """Betiği paket olmadan modül olarak yükler."""
    spec = importlib.util.spec_from_file_location("run_eval", BETIK)
    assert spec is not None and spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture
def sahte(run_eval, monkeypatch):
    """``degerlendir`` ve ``varsayilan_bagimliliklar`` yerine geçer; argümanları kaydeder."""
    kayit: dict[str, list] = {"cagrilar": [], "ayarlar": [], "sentez_modelleri": []}

    def degerlendir(*args, **kwargs):
        kayit["cagrilar"].append((args, kwargs))
        kayit["sentez_modelleri"].append(synthesize.MODEL_SENTEZ)
        return Path("rapor.md")

    def varsayilan_bagimliliklar(ayar):
        kayit["ayarlar"].append(ayar)
        return "BAG"

    monkeypatch.setattr(run_eval, "degerlendir", degerlendir)
    monkeypatch.setattr(run_eval, "varsayilan_bagimliliklar", varsayilan_bagimliliklar)
    return kayit


@pytest.fixture
def veri_seti(tmp_path: Path) -> Path:
    yol = tmp_path / "ruyalar_test.jsonl"
    yol.write_text('{"id": "r001", "metin": "Rüyamda deniz gördüm."}\n', encoding="utf-8")
    return yol


def _kimlikler(cagri: tuple[tuple, dict]) -> set[str] | None:
    """``degerlendir`` çağrısındaki ``kimlikler`` argümanı (konumsal ya da anahtar sözcüklü)."""
    args, kwargs = cagri
    if "kimlikler" in kwargs:
        return kwargs["kimlikler"]
    return args[3] if len(args) > 3 else None


def test_alt_kume_kimlikleri_okunur(run_eval, sahte, veri_seti, tmp_path):
    alt_kume = tmp_path / "alt_kume.txt"
    alt_kume.write_text("r001\n\n  \nr003\nr005\n", encoding="utf-8")

    run_eval.main(
        ["--dataset", str(veri_seti), "--etiket", "asama1-test", "--alt-kume", str(alt_kume)]
    )

    assert len(sahte["cagrilar"]) == 1
    assert _kimlikler(sahte["cagrilar"][0]) == {"r001", "r003", "r005"}


def test_n_kaynak_basina_n_ayarlanir(run_eval, sahte, veri_seti):
    run_eval.main(["--dataset", str(veri_seti), "--etiket", "asama1-test", "--n", "3"])

    assert len(sahte["ayarlar"]) == 1
    ayar = sahte["ayarlar"][0]
    assert ayar.kaynak_basina_n == 3
    assert ayar.sorgu_onbellegi is True


def test_sentez_modeli_d4_kosu_boyunca_kullanilir(run_eval, sahte, veri_seti, monkeypatch):
    # main modeli geri yüklemese bile test sonunda eski değere dönsün.
    monkeypatch.setattr(synthesize, "MODEL_SENTEZ", config.MODEL_SENTEZ)

    run_eval.main(
        ["--dataset", str(veri_seti), "--etiket", "asama1-test", "--sentez-modeli", "d4"]
    )

    assert sahte["sentez_modelleri"] == [config.MODEL_SENTEZ_D4]
    assert synthesize.MODEL_SENTEZ == config.MODEL_SENTEZ


def test_sentez_modeli_varsayilan_modeli_degistirmez(run_eval, sahte, veri_seti, monkeypatch):
    monkeypatch.setattr(synthesize, "MODEL_SENTEZ", config.MODEL_SENTEZ)

    run_eval.main(
        ["--dataset", str(veri_seti), "--etiket", "asama1-test", "--sentez-modeli", "varsayilan"]
    )

    assert sahte["sentez_modelleri"] == [config.MODEL_SENTEZ]
    assert synthesize.MODEL_SENTEZ == config.MODEL_SENTEZ


def test_yeni_secenekler_yokken_kimlikler_none(run_eval, sahte, veri_seti):
    run_eval.main(["--dataset", str(veri_seti), "--etiket", "asama1-test"])

    assert len(sahte["cagrilar"]) == 1
    assert _kimlikler(sahte["cagrilar"][0]) is None
