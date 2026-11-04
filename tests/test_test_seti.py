"""Test seti (eval/dataset/ruyalar_v1.jsonl) sözleşmesi: şema, kimlikler ve kapsam.

Test seti şimdilik 45 rüyadan oluşur (docs/06, bölüm 1). Bu dosya veriyi değil,
verinin biçimini ve kapsamını denetler: her satır `ruya.schemas.TestOrnegi` olmalı,
kimlikler sıralı olmalı, semboller sözlükte bulunmalı ve set bazı davranışları
(bulunamayan sembol, olumsuzlama, bağlam koşulu) mutlaka örneklemeli.
"""

import json
from pathlib import Path

import pytest

from ruya.schemas import TestOrnegi

KOK = Path(__file__).resolve().parents[1]
TEST_SETI = KOK / "eval" / "dataset" / "ruyalar_v1.jsonl"
SOZLUK_DOSYASI = KOK / "sozluk" / "symbols.json"

BEKLENEN_SAYI = 45
EN_AZ_SEMBOL = 15


@pytest.fixture(scope="module")
def satirlar() -> list[dict]:
    """Test setinin ham satırları; dosya yoksa testi anlaşılır biçimde düşürür."""
    if not TEST_SETI.exists():
        pytest.fail(f"test seti bulunamadı: {TEST_SETI.relative_to(KOK)}")
    with TEST_SETI.open(encoding="utf-8") as dosya:
        return [json.loads(satir) for satir in dosya if satir.strip()]


@pytest.fixture(scope="module")
def ornekler(satirlar) -> list[TestOrnegi]:
    return [TestOrnegi.model_validate(satir) for satir in satirlar]


@pytest.fixture(scope="module")
def sozluk() -> dict:
    """sozluk/symbols.json: {symbol_id: SymbolKaydi}."""
    with SOZLUK_DOSYASI.open(encoding="utf-8") as dosya:
        return json.load(dosya)


def test_her_satir_semaya_uyar(satirlar):
    for satir in satirlar:
        TestOrnegi.model_validate(satir)


def test_yirmi_ornek_var(ornekler):
    assert len(ornekler) == BEKLENEN_SAYI


def test_kimlikler_sirali(ornekler):
    assert [o.id for o in ornekler] == [f"r{i:03d}" for i in range(1, BEKLENEN_SAYI + 1)]


def test_sembol_kimlikleri_sozlukte(ornekler, sozluk):
    for ornek in ornekler:
        istenen = (
            list(ornek.beklenen_semboller)
            + list(ornek.olmamasi_gerekenler)
            + list(ornek.beklenen_nitelikler)
        )
        eksik = [sid for sid in istenen if sid not in sozluk]
        assert not eksik, f"{ornek.id}: sözlükte olmayan sembol kimliği: {eksik}"


def test_beklenen_ve_yasak_cakismaz(ornekler):
    for ornek in ornekler:
        ortak = set(ornek.beklenen_semboller) & set(ornek.olmamasi_gerekenler)
        assert not ortak, f"{ornek.id}: hem beklenen hem yasak sembol: {sorted(ortak)}"


def test_beklenen_maddeler_bos(ornekler):
    for ornek in ornekler:
        assert ornek.beklenen_maddeler == {}, f"{ornek.id}: beklenen_maddeler dolu"


def test_notlar_sentetik(ornekler):
    for ornek in ornekler:
        assert ornek.notlar is not None, f"{ornek.id}: notlar boş"
        assert ornek.notlar.startswith("sentetik"), f"{ornek.id}: notlar 'sentetik' ile başlamalı"


def test_bulunamayan_sembol_ornegi_var(ornekler):
    """Sözlükte karşılığı olmayan bir rüya da test edilmeli (İG-31)."""
    assert any(not o.beklenen_semboller for o in ornekler)


def test_olumsuzlama_ornegi_var(ornekler):
    """'Yılan görmedim' gibi olumsuz bir rüya korku duygusuyla birlikte bulunmalı."""
    assert any(
        "yilan" in o.olmamasi_gerekenler and "korku" in o.beklenen_duygular for o in ornekler
    )


def test_yeterli_sembol_cesitliligi(ornekler):
    semboller = {sid for o in ornekler for sid in o.beklenen_semboller}
    assert len(semboller) >= EN_AZ_SEMBOL, f"yalnızca {len(semboller)} farklı sembol bekleniyor"


def test_kosul_ornegi_var(ornekler):
    """Aynı rüya metni kadın ve erkek bağlamıyla iki kez yer almalı (koşullu yorum)."""
    cinsiyetler: dict[str, set[str]] = {}
    for ornek in ornekler:
        if ornek.baglam is not None and ornek.baglam.cinsiyet is not None:
            cinsiyetler.setdefault(ornek.metin, set()).add(ornek.baglam.cinsiyet)
    assert any({"kadin", "erkek"} <= c for c in cinsiyetler.values())
