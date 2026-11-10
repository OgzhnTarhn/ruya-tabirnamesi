"""Gümüş etiket hakemi (``ruya.degerlendirme.hakem``) birim testleri (docs/15, K12).

Ağa çıkılmaz: sahte istemci isteği kaydeder, hazır bir yanıt nesnesi döndürür; depo ve
dosyalar sahtedir / ``tmp_path`` altındadır.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from ruya import config
from ruya.degerlendirme.getirme_deneyi import (
    etiket_dosyasi_yaz,
    etiketleri_oku,
    havuz,
)
from ruya.hatalar import RuyaHatasi, YanitBozuk
from ruya.llm.talimatlar import talimat_oku
from ruya.schemas import Kullanim, Madde

# --- modül (henüz yoksa testler eksik davranışla yüzleşsin) -----------------


@pytest.fixture
def hakem():
    """Test edilen modül; modül yoksa testi başarısız kılar (atlamaz)."""
    try:
        import ruya.degerlendirme.hakem as modul
    except ModuleNotFoundError as hata:  # pragma: no cover - uygulanınca geçer
        pytest.fail(f"ruya.degerlendirme.hakem yok: {hata}")
    return modul


# --- yardımcılar ------------------------------------------------------------


def _madde(
    entry_id: str,
    *,
    metin_tr: str | None = "Rüyada bir şey görmek.",
    metin_asli: str = "(asıl metin)",
) -> Madde:
    kaynak = entry_id.split(":")[0]
    return Madde(
        entry_id=entry_id,
        kaynak=kaynak,
        eser="Test Eseri",
        yazar="Test Yazarı",
        gelenek="islami_klasik",
        dil="tr",
        lisans="PD",
        konum={"satir": 1},
        metin_asli=metin_asli,
        metin_tr=metin_tr,
    )


class _SahteDepo:
    """``.madde(entry_id)`` veren en küçük depo; olmayan kimlikte KeyError atar."""

    def __init__(self, maddeler: dict[str, Madde]) -> None:
        self._maddeler = maddeler

    def madde(self, entry_id: str) -> Madde:
        return self._maddeler[entry_id]


class SahteYanit:
    """LLMYaniti'nin hakemin kullandığı yüzü: ``json()`` ve ``kullanim``."""

    def __init__(self, govde: object, kullanim: Kullanim) -> None:
        self._govde = govde
        self.kullanim = kullanim

    def json(self) -> object:
        return self._govde


class SahteIstemci:
    """``mesaj`` çağrısını kaydeder ve hazır (ya da isteğe göre üretilen) yanıtı döndürür."""

    def __init__(self, govde: object = None) -> None:
        self.kullanim = Kullanim(model=config.MODEL_HAKEM, girdi_token=100, cikti_token=10)
        self._govde = {"ilgili": [1]} if govde is None else govde
        self._kilit = threading.Lock()
        self.cagrilar: list[tuple[dict, bool]] = []

    def mesaj(self, istek: dict, ruya_icerir: bool = False) -> SahteYanit:
        with self._kilit:
            self.cagrilar.append((istek, ruya_icerir))
        govde = self._govde(istek) if callable(self._govde) else self._govde
        return SahteYanit(govde, self.kullanim)


def _mesajlar(istek: dict) -> dict[str, str]:
    return {m["role"]: m["content"] for m in istek["messages"]}


def _satir(ornek_id: str, anahtar: str, sembol: str, sirali: list[list[object]]) -> dict:
    return {
        "ornek_id": ornek_id,
        "cesit": "G0",
        "anahtar": anahtar,
        "sembol": sembol,
        "sirali": sirali,
    }


# --- TALIMAT -----------------------------------------------------------------


def test_talimat_adi(hakem):
    assert hakem.TALIMAT == "getirme_hakemi_v1"


# --- hakem_istegi ------------------------------------------------------------


def _maddeler() -> list[Madde]:
    return [
        _madde("nablusi:0001", metin_tr="Yılan düşmandır."),
        _madde("miller:0002", metin_tr=None, metin_asli="To dream of snakes."),
    ]


def test_hakem_istegi_model_ve_ek_alanlar(hakem):
    istek = hakem.hakem_istegi("Rüyamda yılan gördüm.", "yılan", _maddeler())

    assert istek["model"] == config.MODEL_HAKEM
    assert isinstance(istek["max_tokens"], int)
    assert istek["max_tokens"] > 0
    assert istek["chat_template_kwargs"] == {"enable_thinking": False}


def test_hakem_istegi_sistem_mesaji_talimat(hakem):
    istek = hakem.hakem_istegi("Rüyamda yılan gördüm.", "yılan", _maddeler())

    assert _mesajlar(istek)["system"] == talimat_oku(hakem.TALIMAT)


def test_hakem_istegi_kullanici_metni_ruya_sembol_ve_numarali_adaylar(hakem):
    istek = hakem.hakem_istegi("Rüyamda yılan gördüm.", "yılan", _maddeler())
    kullanici = _mesajlar(istek)["user"]

    assert "Rüyamda yılan gördüm." in kullanici
    assert "Sembol: yılan" in kullanici
    assert "[1] Yılan düşmandır." in kullanici
    assert "[2] To dream of snakes." in kullanici
    assert kullanici.index("[1]") < kullanici.index("[2]")


def test_hakem_istegi_metin_tr_yoksa_metin_asli_ve_bosluklar_toplanir(hakem):
    maddeler = [
        _madde("nablusi:0001", metin_tr="  Yılan\n\tdüşmandır.  "),
        _madde("miller:0002", metin_tr=None, metin_asli="To dream\n of snakes."),
    ]
    kullanici = _mesajlar(hakem.hakem_istegi("Rüya.", "yılan", maddeler))["user"]

    assert "[1] Yılan düşmandır." in kullanici
    assert "[2] To dream of snakes." in kullanici


def test_hakem_istegi_uzun_metni_600_karaktere_kirpar(hakem):
    uzun = "a" * 700
    kullanici = _mesajlar(
        hakem.hakem_istegi("Rüya.", "yılan", [_madde("nablusi:0001", metin_tr=uzun)])
    )["user"]

    assert "[1] " + "a" * 600 in kullanici
    assert "a" * 601 not in kullanici


def test_hakem_istegi_kaynak_ve_entry_id_gostermez(hakem):
    kullanici = _mesajlar(hakem.hakem_istegi("Rüya.", "yılan", _maddeler()))["user"]

    assert "nablusi:0001" not in kullanici
    assert "miller:0002" not in kullanici
    assert "nablusi" not in kullanici
    assert "miller" not in kullanici


def test_hakem_istegi_json_semasi_ilgili_listesi(hakem):
    bicim = hakem.hakem_istegi("Rüya.", "yılan", _maddeler())["response_format"]

    assert bicim["type"] == "json_schema"
    assert bicim["json_schema"]["strict"] is True
    sema = bicim["json_schema"]["schema"]
    assert set(sema["properties"]) == {"ilgili"}
    assert sema["properties"]["ilgili"]["type"] == "array"
    assert sema["properties"]["ilgili"]["items"]["type"] == "integer"


# --- hakem_sec ---------------------------------------------------------------


def test_hakem_sec_ruya_icerir_ile_gonderir_ve_numaralari_kimlige_cevirir(hakem):
    istemci = SahteIstemci({"ilgili": [2]})
    maddeler = _maddeler()

    sonuc = hakem.hakem_sec("Rüyamda yılan gördüm.", "yılan", maddeler, istemci)

    assert sonuc == {"miller:0002"}
    assert len(istemci.cagrilar) == 1
    istek, ruya_icerir = istemci.cagrilar[0]
    assert ruya_icerir is True
    assert _mesajlar(istek)["system"] == talimat_oku(hakem.TALIMAT)


def test_hakem_sec_sinir_disi_ve_tekrar_numaralari_atlar(hakem):
    istemci = SahteIstemci({"ilgili": [0, 1, 1, 3, 9]})

    sonuc = hakem.hakem_sec("Rüya.", "yılan", _maddeler(), istemci)

    assert sonuc == {"nablusi:0001"}


def test_hakem_sec_bos_maddede_istek_yapmaz(hakem):
    istemci = SahteIstemci({"ilgili": [1]})

    assert hakem.hakem_sec("Rüya.", "yılan", [], istemci) == set()
    assert istemci.cagrilar == []


@pytest.mark.parametrize("govde", [{}, {"ilgili": "yok"}, {"ilgili": [1, "x"]}, []])
def test_hakem_sec_gecersiz_sekil_yanitbozuk(hakem, govde):
    istemci = SahteIstemci(govde)

    with pytest.raises(YanitBozuk):
        hakem.hakem_sec("Rüya.", "yılan", _maddeler(), istemci)


# --- gumus_etiketle ----------------------------------------------------------


def _havuz() -> dict[tuple[str, str], list[str]]:
    return {
        ("r001", "yilan"): ["nablusi:0001", "miller:0002"],
        ("r001", "su"): ["ibn:0003"],
    }


def _gumus_satirlar() -> list[dict]:
    return [
        _satir("r001", "yilan", "yılan", [["nablusi:0001", 0.9]]),
        _satir("r001", "su", "su", [["ibn:0003", 0.9]]),
    ]


def _gumus_depo() -> _SahteDepo:
    return _SahteDepo(
        {
            "nablusi:0001": _madde("nablusi:0001", metin_tr="Yılan düşmandır."),
            "miller:0002": _madde("miller:0002", metin_tr="Yılan görmek."),
            "ibn:0003": _madde("ibn:0003", metin_tr="Su berraklıktır."),
        }
    )


def test_gumus_etiketle_her_anahtar_icin_hakem_sec_cagirir(hakem, monkeypatch):
    cagrilar: list[tuple] = []

    def sahte_hakem_sec(ruya_metni, sembol, maddeler, istemci):
        cagrilar.append((ruya_metni, sembol, [m.entry_id for m in maddeler], istemci))
        return {maddeler[0].entry_id}

    monkeypatch.setattr(hakem, "hakem_sec", sahte_hakem_sec)
    istemci = object()

    sonuc = hakem.gumus_etiketle(
        _havuz(),
        _gumus_satirlar(),
        {"r001": "Rüyamda yılan ve su gördüm."},
        _gumus_depo(),
        istemci,
    )

    assert sonuc == {("r001", "yilan"): {"nablusi:0001"}, ("r001", "su"): {"ibn:0003"}}
    assert len(cagrilar) == 2
    assert all(c[0] == "Rüyamda yılan ve su gördüm." for c in cagrilar)
    assert all(c[3] is istemci for c in cagrilar)
    adlar = {c[1]: c[2] for c in cagrilar}
    assert adlar["yılan"] == ["nablusi:0001", "miller:0002"]
    assert adlar["su"] == ["ibn:0003"]


def test_gumus_etiketle_sembol_satirdan_gelir_yoksa_anahtar(hakem, monkeypatch):
    gorulen: dict[str, str] = {}

    def sahte_hakem_sec(ruya_metni, sembol, maddeler, istemci):
        gorulen[maddeler[0].entry_id] = sembol
        return set()

    monkeypatch.setattr(hakem, "hakem_sec", sahte_hakem_sec)
    havuz_ = {("r001", "yilan"): ["nablusi:0001"], ("r001", "su"): ["ibn:0003"]}
    satirlar = [_satir("r001", "yilan", "yılan", [["nablusi:0001", 0.9]])]

    hakem.gumus_etiketle(havuz_, satirlar, {"r001": "Rüya."}, _gumus_depo(), object())

    assert gorulen == {"nablusi:0001": "yılan", "ibn:0003": "su"}


def test_gumus_etiketle_depoda_olmayan_kimligi_atlar(hakem, monkeypatch):
    gorulen: list[list[str]] = []

    def sahte_hakem_sec(ruya_metni, sembol, maddeler, istemci):
        gorulen.append([m.entry_id for m in maddeler])
        return set()

    monkeypatch.setattr(hakem, "hakem_sec", sahte_hakem_sec)
    havuz_ = {("r001", "yilan"): ["nablusi:0001", "yok:9999"]}

    hakem.gumus_etiketle(havuz_, _gumus_satirlar(), {"r001": "Rüya."}, _gumus_depo(), object())

    assert gorulen == [["nablusi:0001"]]


def test_gumus_etiketle_hatali_anahtar_sonucta_yok_ve_digerleri_devam_eder(hakem, monkeypatch):
    def sahte_hakem_sec(ruya_metni, sembol, maddeler, istemci):
        if sembol == "yılan":
            raise RuyaHatasi("hakem düştü")
        return {maddeler[0].entry_id}

    monkeypatch.setattr(hakem, "hakem_sec", sahte_hakem_sec)

    sonuc = hakem.gumus_etiketle(
        _havuz(), _gumus_satirlar(), {"r001": "Rüya."}, _gumus_depo(), object()
    )

    assert ("r001", "yilan") not in sonuc
    assert sonuc == {("r001", "su"): {"ibn:0003"}}


def test_gumus_etiketle_eszamanli_calistirir(hakem, monkeypatch):
    kilit = threading.Lock()
    durum = {"acik": 0, "en_fazla": 0}

    def sahte_hakem_sec(ruya_metni, sembol, maddeler, istemci):
        with kilit:
            durum["acik"] += 1
            durum["en_fazla"] = max(durum["en_fazla"], durum["acik"])
        time.sleep(0.05)
        with kilit:
            durum["acik"] -= 1
        return set()

    monkeypatch.setattr(hakem, "hakem_sec", sahte_hakem_sec)
    havuz_ = {("r001", f"s{i}"): ["nablusi:0001"] for i in range(4)}

    hakem.gumus_etiketle(
        havuz_, [], {"r001": "Rüya."}, _gumus_depo(), object(), en_fazla_eszamanli=2
    )

    assert durum["en_fazla"] == 2


def test_gumus_etiketle_gercek_hakem_sec_ile_istemciye_gider(hakem):
    def govde(istek: dict) -> dict:
        kullanici = _mesajlar(istek)["user"]
        return {"ilgili": [1] if "Sembol: yılan" in kullanici else []}

    istemci = SahteIstemci(govde)

    sonuc = hakem.gumus_etiketle(
        _havuz(), _gumus_satirlar(), {"r001": "Rüya."}, _gumus_depo(), istemci
    )

    assert sonuc == {("r001", "yilan"): {"nablusi:0001"}, ("r001", "su"): set()}
    assert len(istemci.cagrilar) == 2
    assert all(ruya_icerir is True for _, ruya_icerir in istemci.cagrilar)


# --- etiketleri_isaretle -----------------------------------------------------


def _etiket_dosyasi(tmp_path: Path) -> Path:
    satirlar = [
        _satir("r001", "yilan", "yılan", [["nablusi:0001", 0.9], ["miller:0002", 0.8]]),
        _satir("r001", "su", "su", [["ibn:0003", 0.9]]),
    ]
    depo = _gumus_depo()
    yol = tmp_path / "etiket.md"
    etiket_dosyasi_yaz(havuz(satirlar, k=5), satirlar, {"r001": "Rüya."}, depo, yol)
    return yol


def test_etiketleri_isaretle_yalniz_ilgili_satirlari_isaretler(hakem, tmp_path: Path):
    kaynak = _etiket_dosyasi(tmp_path)
    hedef = tmp_path / "isaretli.md"

    sonuc = hakem.etiketleri_isaretle(
        kaynak, {("r001", "yilan"): {"miller:0002"}}, hedef
    )

    assert sonuc == hedef
    metin = hedef.read_text(encoding="utf-8")
    assert "- [x] miller:0002 — " in metin
    assert "- [ ] nablusi:0001 — " in metin
    assert "- [ ] ibn:0003 — " in metin
    # Başlıklar ve rüya alıntısı değişmez.
    assert "## r001" in metin
    assert "> Rüya." in metin
    assert "### yılan (yilan)" in metin


def test_etiketleri_isaretle_gidis_donus(hakem, tmp_path: Path):
    kaynak = _etiket_dosyasi(tmp_path)
    hedef = tmp_path / "isaretli.md"
    etiketler = {("r001", "yilan"): {"nablusi:0001", "miller:0002"}}

    hakem.etiketleri_isaretle(kaynak, etiketler, hedef)

    okunan = etiketleri_oku(hedef)
    assert okunan == {("r001", "yilan"): {"nablusi:0001", "miller:0002"}, ("r001", "su"): set()}


def test_etiketleri_isaretle_bos_etiket_her_seyi_isaretsiz_birakir(hakem, tmp_path: Path):
    kaynak = _etiket_dosyasi(tmp_path)
    hedef = tmp_path / "isaretli.md"

    hakem.etiketleri_isaretle(kaynak, {}, hedef)

    assert hedef.read_text(encoding="utf-8") == kaynak.read_text(encoding="utf-8")
    assert etiketleri_oku(hedef) == {("r001", "yilan"): set(), ("r001", "su"): set()}
