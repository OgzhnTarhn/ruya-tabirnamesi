"""Notebook'lar çıktısız commit edilir ve ortak kurulum hücresiyle başlar (docs/11)."""

import json
from pathlib import Path

import pytest

NOTEBOOKLAR = sorted((Path(__file__).resolve().parents[1] / "notebooks").rglob("*.ipynb"))


def _kod_hucreleri(yol: Path) -> list[dict]:
    nb = json.loads(yol.read_text(encoding="utf-8"))
    return [h for h in nb["cells"] if h["cell_type"] == "code"]


@pytest.mark.parametrize("yol", NOTEBOOKLAR, ids=lambda p: p.name)
def test_ciktilar_temiz(yol):
    for hucre in _kod_hucreleri(yol):
        assert hucre["outputs"] == [], f"{yol.name}: çıktısı temizlenmemiş hücre var"
        assert hucre["execution_count"] is None


@pytest.mark.parametrize("yol", NOTEBOOKLAR, ids=lambda p: p.name)
def test_kurulum_hucresiyle_baslar(yol):
    ilk = "".join(_kod_hucreleri(yol)[0]["source"])
    assert "%run {REPO}/notebooks/_kurulum.py" in ilk
