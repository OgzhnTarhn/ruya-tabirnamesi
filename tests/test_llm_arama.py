"""LLMIstemcisi'nin hibrit getirme yöntemleri: gom, yeniden_sirala, ocr.

Ağa çıkılmaz (httpx.MockTransport) ve uyunmaz (bekle listeye yazar).
Üç yöntem de disk önbelleğine yazmaz (docs/12, bölüm 5b; docs/13).
"""

from __future__ import annotations

import base64
import json

import httpx
import pytest

from ruya import config
from ruya.config import Ayarlar
from ruya.hatalar import LLMHatasi
from ruya.llm.client import LLMIstemcisi


@pytest.fixture
def ayar(tmp_path) -> Ayarlar:
    return Ayarlar(data_dir=tmp_path)


@pytest.fixture(autouse=True)
def _anahtar(monkeypatch) -> None:
    monkeypatch.setenv(config.LLM_ANAHTAR_DEGISKENI, "test-anahtar")


def kaydeden(donen):
    """Çağrıları kaydeden handler. ``donen(sira, istek)`` yanıtı üretir."""
    cagrilar = []

    def handler(istek):
        cagrilar.append(istek)
        return donen(len(cagrilar), istek)

    return cagrilar, handler


def istemci(handler, ayar: Ayarlar, beklemeler: list[float]) -> LLMIstemcisi:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return LLMIstemcisi(ayar=ayar, http=http, bekle=beklemeler.append)


def gom_govdesi(vektorler: list[list[float]]) -> dict:
    return {"data": [{"index": i, "embedding": v} for i, v in enumerate(vektorler)]}


def rerank_govdesi(sonuclar: list[tuple[int, float]]) -> dict:
    return {"results": [{"index": i, "relevance_score": s} for i, s in sonuclar]}


def test_gom_istek_bicimi(ayar):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(200, json=gom_govdesi([[0.1, 0.2], [0.3, 0.4]]))
    )
    sonuc = istemci(handler, ayar, []).gom(["bir", "iki"])
    assert sonuc == [[0.1, 0.2], [0.3, 0.4]]
    assert len(cagrilar) == 1
    istek = cagrilar[0]
    assert istek.url.path == "/v1/embeddings"
    assert str(istek.url).startswith(config.LLM_ADRESI)
    assert istek.headers["Authorization"] == "Bearer test-anahtar"
    assert json.loads(istek.content) == {
        "model": config.MODEL_EMBEDDING,
        "input": ["bir", "iki"],
        "dimensions": config.EMBEDDING_BOYUTU,
    }


def test_gom_yanit_sirasiz_gelse_de_girdi_sirasini_korur(ayar):
    def donen(_sira, _istek):
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 2, "embedding": [2.0]},
                    {"index": 0, "embedding": [0.0]},
                    {"index": 1, "embedding": [1.0]},
                ]
            },
        )

    cagrilar, handler = kaydeden(donen)
    sonuc = istemci(handler, ayar, []).gom(["a", "b", "c"])
    assert sonuc == [[0.0], [1.0], [2.0]]
    assert len(cagrilar) == 1


def test_gom_bos_listede_istek_atmaz(ayar):
    cagrilar, handler = kaydeden(lambda _sira, _istek: httpx.Response(200, json=gom_govdesi([])))
    assert istemci(handler, ayar, []).gom([]) == []
    assert cagrilar == []


def test_gom_istek_basina_en_fazla_64_metin(ayar):
    metinler = [f"m{i}" for i in range(130)]

    def donen(_sira, istek):
        girdi = json.loads(istek.content)["input"]
        return httpx.Response(200, json=gom_govdesi([[float(m[1:])] for m in girdi]))

    cagrilar, handler = kaydeden(donen)
    sonuc = istemci(handler, ayar, []).gom(metinler)
    assert [len(json.loads(c.content)["input"]) for c in cagrilar] == [64, 64, 2]
    assert sonuc == [[float(i)] for i in range(130)]


def test_yeniden_sirala_istek_bicimi_ve_siralama(ayar):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(
            200, json=rerank_govdesi([(0, 0.1), (2, 0.9), (1, 0.4)])
        )
    )
    sonuc = istemci(handler, ayar, []).yeniden_sirala("sorgu", ["a", "b", "c"])
    assert sonuc == [(2, 0.9), (1, 0.4), (0, 0.1)]
    assert len(cagrilar) == 1
    istek = cagrilar[0]
    assert istek.url.path == "/v1/rerank"
    assert istek.headers["Authorization"] == "Bearer test-anahtar"
    assert json.loads(istek.content) == {
        "model": config.MODEL_RERANKER,
        "query": "sorgu",
        "documents": ["a", "b", "c"],
    }


def test_yeniden_sirala_bos_belgelerde_istek_atmaz(ayar):
    cagrilar, handler = kaydeden(lambda _sira, _istek: httpx.Response(200, json=rerank_govdesi([])))
    assert istemci(handler, ayar, []).yeniden_sirala("sorgu", []) == []
    assert cagrilar == []


def test_ocr_istek_bicimi(ayar):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(200, json={"text": "rüya metni"})
    )
    veri = b"\x89PNG\r\n\x1a\n"
    sonuc = istemci(handler, ayar, []).ocr(veri, "image/png")
    assert sonuc == "rüya metni"
    assert len(cagrilar) == 1
    istek = cagrilar[0]
    assert istek.url.path == "/v1/ocr"
    assert istek.headers["Authorization"] == "Bearer test-anahtar"
    b64 = base64.b64encode(veri).decode("ascii")
    assert json.loads(istek.content) == {
        "model": config.MODEL_OCR,
        "image": f"data:image/png;base64,{b64}",
    }


def test_uc_yontem_de_diske_onbellek_yazmaz(tmp_path):
    ayar = Ayarlar(data_dir=tmp_path, llm_cache=True, sorgu_onbellegi=True)

    def donen(_sira, istek):
        if istek.url.path == "/v1/embeddings":
            return httpx.Response(200, json=gom_govdesi([[0.5]]))
        if istek.url.path == "/v1/rerank":
            return httpx.Response(200, json=rerank_govdesi([(0, 0.5)]))
        return httpx.Response(200, json={"text": "metin"})

    cagrilar, handler = kaydeden(donen)
    c = istemci(handler, ayar, [])
    assert c.gom(["bir"], ruya_icerir=True) == [[0.5]]
    assert c.yeniden_sirala("sorgu", ["a"], ruya_icerir=True) == [(0, 0.5)]
    assert c.ocr(b"veri", "image/jpeg") == "metin"
    assert len(cagrilar) == 3
    onbellek = ayar.llm_onbellek_klasoru
    assert not onbellek.exists() or not any(onbellek.iterdir())


@pytest.mark.parametrize(
    ("cagri", "govde"),
    [
        (lambda c: c.gom(["bir"]), gom_govdesi([[0.5]])),
        (lambda c: c.yeniden_sirala("sorgu", ["a"]), rerank_govdesi([(0, 0.5)])),
        (lambda c: c.ocr(b"veri", "image/png"), {"text": "metin"}),
    ],
    ids=["gom", "yeniden_sirala", "ocr"],
)
def test_500_sonra_200_yeniden_denenir(ayar, cagri, govde):
    def donen(sira, _istek):
        if sira == 1:
            return httpx.Response(500, json={"error": {"message": "sunucu hatası"}})
        return httpx.Response(200, json=govde)

    cagrilar, handler = kaydeden(donen)
    beklemeler: list[float] = []
    cagri(istemci(handler, ayar, beklemeler))
    assert len(cagrilar) == 2
    assert len(beklemeler) == 1


@pytest.mark.parametrize(
    "cagri",
    [
        lambda c: c.gom(["bir"]),
        lambda c: c.yeniden_sirala("sorgu", ["a"]),
        lambda c: c.ocr(b"veri", "image/png"),
    ],
    ids=["gom", "yeniden_sirala", "ocr"],
)
def test_yeniden_denemeler_tukenince_llmhatasi(ayar, cagri):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(503, json={"error": {"message": "meşgul"}})
    )
    with pytest.raises(LLMHatasi) as hata:
        cagri(istemci(handler, ayar, []))
    assert hata.value.durum == 503
    assert len(cagrilar) == 4
