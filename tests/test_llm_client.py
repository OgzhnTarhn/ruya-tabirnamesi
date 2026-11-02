"""LLMIstemcisi testleri: istek biçimi, disk önbelleği, yeniden deneme ve hatalar.

Ağa çıkılmaz (httpx.MockTransport) ve uyunmaz (bekle listeye yazar).
"""

from __future__ import annotations

import json

import httpx
import pytest

from ruya import config
from ruya.config import Ayarlar
from ruya.hatalar import ApiAnahtariYok, LLMHatasi, ModelReddetti, YanitBozuk, YanitKesildi
from ruya.llm.client import LLMIstemcisi, LLMYaniti, onbellek_anahtari

ISTEK = {
    "model": "deepseek-v4.1-flash",
    "messages": [{"role": "user", "content": "merhaba"}],
    "max_tokens": 500,
}


def _istek(metin: str) -> dict:
    return {**ISTEK, "messages": [{"role": "user", "content": metin}]}


ISTEK_A, ISTEK_B, ISTEK_C = _istek("a"), _istek("b"), _istek("c")


@pytest.fixture
def ayar(tmp_path) -> Ayarlar:
    return Ayarlar(data_dir=tmp_path)


@pytest.fixture(autouse=True)
def _anahtar(monkeypatch) -> None:
    monkeypatch.setenv(config.LLM_ANAHTAR_DEGISKENI, "test-anahtar")


def ok_govdesi() -> dict:
    mesaj = {"role": "assistant", "content": '{"a": 1}', "refusal": None}
    kullanim = {
        "prompt_tokens": 100,
        "completion_tokens": 40,
        "prompt_tokens_details": {"cached_tokens": 64},
    }
    return {
        "model": "deepseek-v4.1-flash",
        "choices": [{"message": mesaj, "finish_reason": "stop"}],
        "usage": kullanim,
    }


def yanit(govde: dict | None = None, durum: int = 200, basliklar: dict | None = None):
    return httpx.Response(durum, json=ok_govdesi() if govde is None else govde, headers=basliklar)


def kaydeden(donen=None):
    """Çağrıları kaydeden handler. ``donen(sira, istek)`` verilirse yanıtı o üretir."""
    cagrilar = []

    def handler(istek):
        cagrilar.append(istek)
        return yanit() if donen is None else donen(len(cagrilar), istek)

    return cagrilar, handler


def istemci(handler, ayar: Ayarlar, beklemeler: list[float]) -> LLMIstemcisi:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return LLMIstemcisi(ayar=ayar, http=http, bekle=beklemeler.append)


def onbellek_dosyasi(ayar: Ayarlar, istek: dict):
    return ayar.llm_onbellek_klasoru / f"{onbellek_anahtari(istek)}.json"


def test_istek_bicimi_ve_kullanim(ayar):
    cagrilar, handler = kaydeden()
    sonuc = istemci(handler, ayar, []).mesaj(ISTEK)
    assert len(cagrilar) == 1
    istek = cagrilar[0]
    assert istek.url.path == "/v1/chat/completions"
    assert str(istek.url).startswith(config.LLM_ADRESI)
    assert istek.headers["Authorization"] == "Bearer test-anahtar"
    assert json.loads(istek.content) == ISTEK
    assert isinstance(sonuc, LLMYaniti)
    assert sonuc.icerik == '{"a": 1}'
    assert sonuc.json() == {"a": 1}
    assert sonuc.kullanim.model == "deepseek-v4.1-flash"
    assert sonuc.kullanim.girdi_token == 36
    assert sonuc.kullanim.cikti_token == 40
    assert sonuc.kullanim.onbellek_okuma_token == 64
    assert sonuc.kullanim.disk_onbelleginden is False


def test_anahtar_yoksa_istek_atilmaz(ayar, monkeypatch):
    monkeypatch.delenv(config.LLM_ANAHTAR_DEGISKENI)
    cagrilar, handler = kaydeden()
    with pytest.raises(ApiAnahtariYok):
        istemci(handler, ayar, []).mesaj(ISTEK)
    assert cagrilar == []


def test_disk_onbellegi_ikinci_cagriyi_karsilar(ayar):
    cagrilar, handler = kaydeden()
    c = istemci(handler, ayar, [])
    ilk = c.mesaj(ISTEK)
    ikinci = c.mesaj(ISTEK)
    assert len(cagrilar) == 1
    assert ilk.kullanim.disk_onbelleginden is False
    assert ikinci.kullanim.disk_onbelleginden is True
    assert ikinci.kullanim.maliyet_usd == 0
    assert ikinci.json() == {"a": 1}
    assert onbellek_dosyasi(ayar, ISTEK).exists()


def test_onbellek_kapaliyken_her_cagri_gider(tmp_path):
    ayar = Ayarlar(data_dir=tmp_path, llm_cache=False)
    cagrilar, handler = kaydeden()
    c = istemci(handler, ayar, [])
    c.mesaj(ISTEK)
    c.mesaj(ISTEK)
    assert len(cagrilar) == 2
    assert not onbellek_dosyasi(ayar, ISTEK).exists()


def test_ruya_icerir_sorgu_onbellegine_bagli(ayar, tmp_path):
    cagrilar, handler = kaydeden()
    c = istemci(handler, ayar, [])
    c.mesaj(ISTEK, ruya_icerir=True)
    c.mesaj(ISTEK, ruya_icerir=True)
    assert len(cagrilar) == 2
    assert not onbellek_dosyasi(ayar, ISTEK).exists()

    acik = Ayarlar(data_dir=tmp_path, sorgu_onbellegi=True)
    cagrilar2, handler2 = kaydeden()
    c2 = istemci(handler2, acik, [])
    c2.mesaj(ISTEK, ruya_icerir=True)
    ikinci = c2.mesaj(ISTEK, ruya_icerir=True)
    assert len(cagrilar2) == 1
    assert ikinci.kullanim.disk_onbelleginden is True


def test_gecici_hata_yeniden_denenir(ayar):
    cagrilar, handler = kaydeden(lambda sira, _: httpx.Response(503) if sira == 1 else yanit())
    beklemeler: list[float] = []
    sonuc = istemci(handler, ayar, beklemeler).mesaj(ISTEK)
    assert sonuc.json() == {"a": 1}
    assert len(cagrilar) == 2
    assert len(beklemeler) == 1
    assert cagrilar[0].headers["Idempotency-Key"] == cagrilar[1].headers["Idempotency-Key"]


def test_retry_after_suresi_kadar_beklenir(ayar):
    def donen(sira, _):
        if sira == 1:
            return httpx.Response(429, headers={"Retry-After": "2"})
        return yanit()

    cagrilar, handler = kaydeden(donen)
    beklemeler: list[float] = []
    sonuc = istemci(handler, ayar, beklemeler).mesaj(ISTEK)
    assert sonuc.json() == {"a": 1}
    assert len(cagrilar) == 2
    assert beklemeler == [2.0]


def test_yeniden_denemeler_tukenince_hata(ayar):
    cagrilar, handler = kaydeden(lambda _sira, _istek: httpx.Response(503))
    with pytest.raises(LLMHatasi) as hata:
        istemci(handler, ayar, []).mesaj(ISTEK)
    assert hata.value.durum == 503
    assert len(cagrilar) == 4


def test_zaman_asimi_yeniden_denenir_sonra_hata(ayar):
    def donen(sira, istek):
        if sira == 1:
            raise httpx.ReadTimeout("yavaş", request=istek)
        return yanit()

    cagrilar, handler = kaydeden(donen)
    assert istemci(handler, ayar, []).mesaj(ISTEK).json() == {"a": 1}
    assert len(cagrilar) == 2

    def hep_zaman_asimi(_sira, istek):
        raise httpx.ReadTimeout("yavaş", request=istek)

    cagrilar, handler = kaydeden(hep_zaman_asimi)
    with pytest.raises(LLMHatasi, match="ReadTimeout"):
        istemci(handler, ayar, []).mesaj(_istek("başka"))
    assert len(cagrilar) == 4


def test_409_sonra_200_ayni_anahtarla_doner(ayar):
    cagrilar, handler = kaydeden(
        lambda sira, _: httpx.Response(409, json={"error": {"message": "işleniyor"}})
        if sira == 1
        else yanit()
    )
    beklemeler: list[float] = []
    sonuc = istemci(handler, ayar, beklemeler).mesaj(ISTEK)
    assert sonuc.json() == {"a": 1}
    assert len(cagrilar) == 2
    assert beklemeler == [20.0]
    assert cagrilar[0].headers["Idempotency-Key"] == cagrilar[1].headers["Idempotency-Key"]


def test_409_sinir_asilinca_hata(ayar):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(409, json={"error": {"message": "işleniyor"}})
    )
    with pytest.raises(LLMHatasi) as hata:
        istemci(handler, ayar, []).mesaj(ISTEK)
    assert hata.value.durum == 409
    assert len(cagrilar) == 31


def test_409_sonrasi_zaman_asimi_isleniyor_sayilir(ayar):
    def donen(sira, istek):
        if sira == 1:
            return httpx.Response(409, json={"error": {"message": "işleniyor"}})
        if sira == 2:
            raise httpx.ReadTimeout("yavaş", request=istek)
        return yanit()

    cagrilar, handler = kaydeden(donen)
    beklemeler: list[float] = []
    sonuc = istemci(handler, ayar, beklemeler).mesaj(ISTEK)
    assert sonuc.json() == {"a": 1}
    assert len(cagrilar) == 3
    assert beklemeler == [20.0, 20.0]


def test_400_tekrar_denenmez(ayar):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(400, json={"error": {"message": "bozuk istek"}})
    )
    with pytest.raises(LLMHatasi) as hata:
        istemci(handler, ayar, []).mesaj(ISTEK)
    assert len(cagrilar) == 1
    assert "bozuk istek" in str(hata.value)


def test_gunluk_kota_hemen_hata(ayar):
    cagrilar, handler = kaydeden(
        lambda _sira, _istek: httpx.Response(429, headers={"Retry-After": "3600"})
    )
    with pytest.raises(LLMHatasi):
        istemci(handler, ayar, []).mesaj(ISTEK)
    assert len(cagrilar) == 1


def test_kesilen_ve_reddedilen_yanit_onbellege_yazilmaz(ayar):
    kesik = ok_govdesi()
    kesik["choices"][0]["finish_reason"] = "length"
    red = ok_govdesi()
    red["choices"][0]["message"]["refusal"] = "hayır"

    _, handler = kaydeden(lambda _sira, _istek: yanit(kesik))
    with pytest.raises(YanitKesildi):
        istemci(handler, ayar, []).mesaj(ISTEK)
    assert not onbellek_dosyasi(ayar, ISTEK).exists()

    _, handler2 = kaydeden(lambda _sira, _istek: yanit(red))
    with pytest.raises(ModelReddetti):
        istemci(handler2, ayar, []).mesaj(ISTEK)
    assert not onbellek_dosyasi(ayar, ISTEK).exists()


def test_bozuk_json_yanitbozuk_verir(ayar):
    govde = ok_govdesi()
    govde["choices"][0]["message"]["content"] = "bu json değil"
    _, handler = kaydeden(lambda _sira, _istek: yanit(govde))
    sonuc = istemci(handler, ayar, []).mesaj(ISTEK)
    with pytest.raises(YanitBozuk):
        sonuc.json()


def test_toplu_hata_sonuc_olarak_doner(ayar):
    def donen(_sira, istek):
        if json.loads(istek.content)["messages"][0]["content"] == "b":
            return httpx.Response(400, json={"error": {"message": "bozuk istek"}})
        return yanit()

    _, handler = kaydeden(donen)
    sonuclar = istemci(handler, ayar, []).toplu(
        {"a": ISTEK_A, "b": ISTEK_B, "c": ISTEK_C}, eszamanli=2
    )
    assert set(sonuclar) == {"a", "b", "c"}
    assert isinstance(sonuclar["a"], LLMYaniti)
    assert isinstance(sonuclar["c"], LLMYaniti)
    assert isinstance(sonuclar["b"], LLMHatasi)
