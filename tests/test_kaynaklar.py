"""Kaynak künyelerinin tutarlılık testleri (docs/KAYNAKLAR.md, docs/07).

Veri gerektirmez; bilgisayarda da çalışır.
"""

import re

import pytest

from ruya.ingest.kaynaklar import KAYNAKLAR, LISANS_KODLARI

OPENITI_ONEK = "raw.githubusercontent.com/OpenITI/"
COMMIT_DILIMI = re.compile(r"/[0-9a-f]{40}/")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


@pytest.mark.parametrize("kaynak", sorted(KAYNAKLAR), ids=sorted(KAYNAKLAR))
def test_lisans_kodu_gecerli(kaynak):
    assert KAYNAKLAR[kaynak].lisans in LISANS_KODLARI


@pytest.mark.parametrize("kaynak", sorted(KAYNAKLAR), ids=sorted(KAYNAKLAR))
def test_anahtar_kaynakla_ayni(kaynak):
    assert KAYNAKLAR[kaynak].kaynak == kaynak


@pytest.mark.parametrize("kaynak", sorted(KAYNAKLAR), ids=sorted(KAYNAKLAR))
def test_openiti_url_sabit_commitli(kaynak):
    url = KAYNAKLAR[kaynak].url
    if OPENITI_ONEK not in url:
        pytest.skip("OpenITI URL'si değil")
    assert "/master/" not in url
    assert COMMIT_DILIMI.search(url), f"40 karakterlik commit dilimi yok: {url}"


@pytest.mark.parametrize("kaynak", sorted(KAYNAKLAR), ids=sorted(KAYNAKLAR))
def test_sha256_bicimi(kaynak):
    sha256 = KAYNAKLAR[kaynak].sha256
    if sha256 is None:
        pytest.skip("sha256 henüz yazılmamış")
    assert SHA256.match(sha256), f"geçersiz sha256: {sha256}"
