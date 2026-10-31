"""Mimari kuralların testleri (docs/12-kod-yapisi-ve-sozlesmeler.md, bölüm 1)."""

import ast
import importlib
import pkgutil
import re
from pathlib import Path

import pytest

import ruya

KOK = Path(__file__).resolve().parents[1]
PAKET = KOK / "src" / "ruya"

# Her birimin içe aktarabileceği ruya birimleri. Kendi alt modülleri her zaman serbest.
IZINLER: dict[str, set[str]] = {
    "hatalar": set(),
    "schemas": set(),
    "etik": set(),
    "config": {"hatalar"},
    "dosya": set(),
    "text": {"config", "hatalar"},
    "llm": {"config", "hatalar", "schemas"},
    "ingest": {"config", "hatalar", "schemas", "dosya", "text"},
    "enrich": {"config", "hatalar", "schemas", "dosya", "text", "llm"},
    "index": {"config", "hatalar", "schemas", "dosya", "text"},
    "pipeline": {"config", "hatalar", "schemas", "etik", "dosya", "text", "llm", "index"},
    "kayit": {"config", "hatalar", "schemas", "dosya"},
    "degerlendirme": {
        "config",
        "hatalar",
        "schemas",
        "dosya",
        "etik",
        "text",
        "llm",
        "index",
        "pipeline",
        "kayit",
    },
}

# Ağır paketler: modül düzeyinde içe aktarılamaz (bilgisayarda kurulu değil ya da yüklenmesi yavaş).
AGIR_PAKETLER = {
    "chromadb",
    "sentence_transformers",
    "torch",
    "transformers",
    "gradio",
    "google",
    "zeyrek",
}

MODEL_ADI = re.compile(r"claude-(opus|sonnet|haiku|fable|mythos)-[0-9]|deepseek-v[0-9]")


def _moduller() -> list[Path]:
    return sorted(p for p in PAKET.rglob("*.py"))


def _birim(yol: Path) -> str:
    return yol.relative_to(PAKET).with_suffix("").parts[0]


def _ruya_iceaktarmalari(yol: Path) -> set[str]:
    agac = ast.parse(yol.read_text(encoding="utf-8"))
    birimler = set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom) and dugum.module:
            adlar = [dugum.module]
        elif isinstance(dugum, ast.Import):
            adlar = [a.name for a in dugum.names]
        else:
            continue
        for ad in adlar:
            parcalar = ad.split(".")
            if parcalar[0] == "ruya" and len(parcalar) > 1:
                birimler.add(parcalar[1])
    return birimler


@pytest.mark.parametrize("yol", _moduller(), ids=lambda p: str(p.relative_to(PAKET)))
def test_katman_kurali(yol):
    birim = _birim(yol)
    assert birim in IZINLER or birim == "__init__", f"{birim} için izin tanımlanmamış"
    yasakli = _ruya_iceaktarmalari(yol) - IZINLER.get(birim, set()) - {birim}
    assert not yasakli, f"{birim} şunları içe aktaramaz: {sorted(yasakli)}"


@pytest.mark.parametrize("yol", _moduller(), ids=lambda p: str(p.relative_to(PAKET)))
def test_goreli_iceaktarma_yok(yol):
    agac = ast.parse(yol.read_text(encoding="utf-8"))
    goreli = [
        dugum for dugum in ast.walk(agac) if isinstance(dugum, ast.ImportFrom) and dugum.level > 0
    ]
    assert not goreli, (
        f"{yol.relative_to(PAKET)} göreli içe aktarma kullanıyor; katman kuralı yalnızca "
        "mutlak 'ruya.' içe aktarmalarını denetleyebildiği için göreli içe aktarma yasaktır"
    )


@pytest.mark.parametrize("yol", _moduller(), ids=lambda p: str(p.relative_to(PAKET)))
def test_agir_paketler_modul_duzeyinde_yok(yol):
    agac = ast.parse(yol.read_text(encoding="utf-8"))
    for dugum in agac.body:
        if isinstance(dugum, ast.Import):
            adlar = [a.name for a in dugum.names]
        elif isinstance(dugum, ast.ImportFrom) and dugum.module:
            adlar = [dugum.module]
        else:
            continue
        for ad in adlar:
            assert ad.split(".")[0] not in AGIR_PAKETLER, (
                f"{ad} işlevin içinde içe aktarılmalı (bilgisayarda kurulu değil)"
            )


def test_butun_moduller_bilgisayarda_ice_aktarilabilir():
    for bilgi in pkgutil.walk_packages(ruya.__path__, prefix="ruya."):
        importlib.import_module(bilgi.name)


def test_model_adlari_yalnizca_configde():
    taranacaklar = [
        p
        for klasor in ("src", "app", "eval", "scripts", "notebooks")
        for p in (KOK / klasor).rglob("*")
        if p.suffix in {".py", ".ipynb"}
    ]
    ihlaller = [
        str(p.relative_to(KOK))
        for p in taranacaklar
        if p != PAKET / "config.py" and MODEL_ADI.search(p.read_text(encoding="utf-8"))
    ]
    assert not ihlaller, f"Model adları yalnızca src/ruya/config.py içinde olmalı: {ihlaller}"
