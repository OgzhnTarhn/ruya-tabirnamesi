"""extract (Adım 1 · sembol çıkarımı) birim testleri (docs/03, bölüm 5.1).

Ağa çıkılmaz: sahte istemci isteği kaydeder, hazır bir yanıt nesnesi döndürür.
"""

from __future__ import annotations

import pytest

from ruya.hatalar import YanitBozuk
from ruya.llm.talimatlar import talimat_oku
from ruya.pipeline.extract import TALIMAT, extract
from ruya.schemas import CikarimSonucu, Kullanim, RuyaGirdisi

RUYA = "Rüyada bahçede siyah bir yılan gördüm, sonra uçtu."

GECERLI_CIKARIM = {
    "semboller": [
        {
            "yalin": "yılan",
            "nitelikler": ["siyah"],
            "eylem": "gördü",
            "duygu": "korku",
            "olumsuz": False,
            "ham_ifade": "siyah bir yılan",
        }
    ],
    "ruya_turu_ipucu": None,
    "hassas_icerik": False,
}


class SahteYanit:
    """LLMYaniti'nin extract'ın kullandığı yüzü: ``json()`` ve ``kullanim``."""

    def __init__(self, govde: object, kullanim: Kullanim) -> None:
        self._govde = govde
        self.kullanim = kullanim

    def json(self) -> object:
        return self._govde


class SahteIstemci:
    """``mesaj`` çağrısını kaydeder ve önceden verilen yanıtı döndürür."""

    def __init__(self, govde: object = GECERLI_CIKARIM) -> None:
        self.kullanim = Kullanim(model="deepseek-v4.1-flash", girdi_token=120, cikti_token=30)
        self._govde = govde
        self.cagrilar: list[tuple[dict, bool]] = []

    def mesaj(self, istek: dict, ruya_icerir: bool = False) -> SahteYanit:
        self.cagrilar.append((istek, ruya_icerir))
        return SahteYanit(self._govde, self.kullanim)


def _calistir(govde: object = GECERLI_CIKARIM) -> tuple[SahteIstemci, CikarimSonucu, Kullanim]:
    istemci = SahteIstemci(govde)
    cikarim, kullanim = extract(RuyaGirdisi(metin=RUYA), istemci)
    return istemci, cikarim, kullanim


def _istek(istemci: SahteIstemci) -> dict:
    assert len(istemci.cagrilar) == 1
    return istemci.cagrilar[0][0]


def _mesajlar(istek: dict) -> dict[str, str]:
    return {m["role"]: m["content"] for m in istek["messages"]}


# --- istek biçimi -----------------------------------------------------------


def test_ruya_icerir_true_ile_gonderilir():
    istemci, _, _ = _calistir()

    assert istemci.cagrilar[0][1] is True


def test_sistem_mesaji_cikarim_talimati():
    istemci, _, _ = _calistir()

    assert _mesajlar(_istek(istemci))["system"] == talimat_oku(TALIMAT)


def test_kullanici_mesaji_ruya_metnini_icerir():
    istemci, _, _ = _calistir()

    assert RUYA in _mesajlar(_istek(istemci))["user"]


def test_response_format_json_semasi_ister():
    istemci, _, _ = _calistir()

    bicim = _istek(istemci)["response_format"]
    assert bicim["type"] == "json_schema"
    assert bicim["json_schema"]["strict"] is True


# --- sonuç ------------------------------------------------------------------


def test_json_sonucu_cikarim_sonucuna_donusur():
    _, cikarim, _ = _calistir()

    assert isinstance(cikarim, CikarimSonucu)
    assert [s.yalin for s in cikarim.semboller] == ["yılan"]
    assert cikarim.semboller[0].nitelikler == ["siyah"]
    assert cikarim.semboller[0].ham_ifade == "siyah bir yılan"


def test_kullanim_yanittan_aynen_doner():
    istemci, _, kullanim = _calistir()

    assert kullanim == istemci.kullanim


def test_gecersiz_json_sekli_yanitbozuk_verir():
    with pytest.raises(YanitBozuk):
        _calistir({"semboller": "yılan"})
