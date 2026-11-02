"""synthesize (Adım 4 · sentez) ve ``atiflari_dogrula`` birim testleri (docs/03, adım 4).

Ağa çıkılmaz: sahte istemci isteği kaydeder, hazır bir yanıt nesnesi döndürür.
"""

from __future__ import annotations

import pytest

from ruya.etik import GUVENLIK_NOTU, UYARI_METNI
from ruya.hatalar import YanitBozuk
from ruya.llm.talimatlar import talimat_oku
from ruya.pipeline import synthesize as sentez
from ruya.schemas import (
    Aday,
    Atif,
    CikarimSonucu,
    Eslesme,
    Kullanim,
    Madde,
    Sembol,
    YorumBolumu,
)

# --- örnek maddeler ---------------------------------------------------------


def _madde(
    entry_id: str,
    kaynak: str,
    *,
    yazar: str = "Test Yazarı",
    baslik_asli: str | None = None,
    sembol_tr: str | None = None,
    metin_tr: str | None = None,
    metin_asli: str = "(asıl metin)",
) -> Madde:
    """Testte kullanılacak en küçük geçerli Madde."""
    return Madde(
        entry_id=entry_id,
        kaynak=kaynak,
        eser="Test Eseri",
        yazar=yazar,
        gelenek="islami_klasik",
        dil="tr",
        lisans="PD",
        konum={"satir": 1},
        baslik_asli=baslik_asli,
        sembol_tr=sembol_tr,
        symbol_ids=["yilan"],
        metin_asli=metin_asli,
        metin_tr=metin_tr,
    )


NABLUSI = _madde(
    "nablusi:004310",
    "nablusi",
    yazar="Abdülganî en-Nablusî",
    baslik_asli="حية",
    sembol_tr="yılan",
    metin_tr="Yılan rüyada düşmanla yorumlanır; siyah yılan daha güçlü bir düşmandır.",
    metin_asli="حية يدل على عدو",
)

SATIRLI = _madde(
    "nablusi:004311",
    "nablusi",
    yazar="Abdülganî en-Nablusî",
    baslik_asli="حية",
    metin_tr="Yılan rüyada düşmanla yorumlanır;\nsiyah yılan   daha güçlü bir düşmandır.",
    metin_asli="حية يدل على عدو",
)

MILLER = _madde(
    "miller:018710",
    "miller",
    yazar="Gustavus Hindman Miller",
    baslik_asli="Snakes",
    metin_asli="To dream of snakes is a warning of enemies.",
)

BASLIKSIZ = _madde(
    "miller:018711",
    "miller",
    yazar="Gustavus Hindman Miller",
    baslik_asli=None,
    sembol_tr="yılan",
    metin_asli="Snakes foretell enemies.",
)

ALINTI = "siyah yılan daha güçlü bir düşmandır"


# --- atiflari_dogrula -------------------------------------------------------


def _kaynak(entry_id: str, alinti: str) -> dict:
    return {"entry_id": entry_id, "alinti": alinti}


def _bolum(metin: str, *kaynaklar: dict) -> dict:
    return {"metin": metin, "kaynaklar": list(kaynaklar)}


def _veri(*bolumler: dict, bulunamayanlar: list[str] | None = None) -> dict:
    return {"bolumler": list(bolumler), "bulunamayanlar": bulunamayanlar or []}


def test_gecerli_atif_korunur():
    bolumler = sentez.atiflari_dogrula(
        _veri(
            _bolum(
                "Nablusi'ye göre siyah yılan güçlü bir düşmandır.",
                _kaynak("nablusi:004310", ALINTI),
            )
        ),
        {"nablusi:004310": NABLUSI},
    )

    assert len(bolumler) == 1
    assert isinstance(bolumler[0], YorumBolumu)
    assert bolumler[0].metin == "Nablusi'ye göre siyah yılan güçlü bir düşmandır."
    assert bolumler[0].atiflar == [
        Atif(entry_id="nablusi:004310", baslik="Abdülganî en-Nablusî · حية", alinti=ALINTI)
    ]


def test_bilinmeyen_entry_id_atilir():
    bolumler = sentez.atiflari_dogrula(
        _veri(_bolum("Uydurma bir kaynağa dayanan cümle.", _kaynak("uydurma:000001", ALINTI))),
        {"nablusi:004310": NABLUSI},
    )

    assert bolumler[0].metin == "Uydurma bir kaynağa dayanan cümle."
    assert bolumler[0].atiflar == []


def test_metinde_gecmeyen_alinti_bosaltilir_atif_kalir():
    bolumler = sentez.atiflari_dogrula(
        _veri(
            _bolum("Modelin kendi cümlesi.", _kaynak("nablusi:004310", "modelin uydurduğu cümle"))
        ),
        {"nablusi:004310": NABLUSI},
    )

    assert len(bolumler[0].atiflar) == 1
    assert bolumler[0].atiflar[0].entry_id == "nablusi:004310"
    assert bolumler[0].atiflar[0].alinti == ""


def test_alinti_bosluklar_normalize_edilerek_aranir():
    bolumler = sentez.atiflari_dogrula(
        _veri(
            _bolum("Cümle.", _kaynak("nablusi:004310", "siyah yılan\n  daha güçlü   bir düşmandır"))
        ),
        {"nablusi:004310": NABLUSI},
    )

    assert len(bolumler[0].atiflar) == 1
    assert " ".join(bolumler[0].atiflar[0].alinti.split()) == ALINTI


def test_kaynak_metnindeki_bosluklar_da_normalize_edilir():
    bolumler = sentez.atiflari_dogrula(
        _veri(_bolum("Cümle.", _kaynak("nablusi:004311", ALINTI))),
        {"nablusi:004311": SATIRLI},
    )

    assert len(bolumler[0].atiflar) == 1
    assert " ".join(bolumler[0].atiflar[0].alinti.split()) == ALINTI


def test_alinti_metin_asli_icinde_de_aranir():
    bolumler = sentez.atiflari_dogrula(
        _veri(_bolum("Cümle.", _kaynak("nablusi:004310", "حية يدل على عدو"))),
        {"nablusi:004310": NABLUSI},
    )

    assert len(bolumler[0].atiflar) == 1
    assert bolumler[0].atiflar[0].alinti == "حية يدل على عدو"


def test_baslik_asli_yoksa_sembol_tr_kullanilir():
    bolumler = sentez.atiflari_dogrula(
        _veri(_bolum("Cümle.", _kaynak("miller:018711", "Snakes foretell enemies."))),
        {"miller:018711": BASLIKSIZ},
    )

    assert bolumler[0].atiflar[0].baslik == "Gustavus Hindman Miller · yılan"


def test_baslik_bolumunun_atiflari_bos_kalir_ve_sira_korunur():
    bolumler = sentez.atiflari_dogrula(
        _veri(
            _bolum("Yılan"),
            _bolum("Kaynakların söyledikleri", _kaynak("nablusi:004310", ALINTI)),
            _bolum("Ayrışan noktalar", _kaynak("miller:018710", "To dream of snakes is a warning")),
        ),
        {"nablusi:004310": NABLUSI, "miller:018710": MILLER},
    )

    assert [b.metin for b in bolumler] == [
        "Yılan",
        "Kaynakların söyledikleri",
        "Ayrışan noktalar",
    ]
    assert bolumler[0].atiflar == []
    assert [a.entry_id for a in bolumler[1].atiflar] == ["nablusi:004310"]
    assert [a.entry_id for a in bolumler[2].atiflar] == ["miller:018710"]


# --- synthesize: sahte istemci ----------------------------------------------


GECERLI_YORUM = {
    "bolumler": [
        {"metin": "Yılan", "kaynaklar": []},
        {
            "metin": "Nablusi'nin tabirnamesine göre siyah yılan güçlü bir düşmandır.",
            "kaynaklar": [{"entry_id": "nablusi:004310", "alinti": ALINTI}],
        },
    ],
    "bulunamayanlar": [],
}


class SahteYanit:
    """LLMYaniti'nin synthesize'ın kullandığı yüzü: ``json()`` ve ``kullanim``."""

    def __init__(self, govde: object, kullanim: Kullanim) -> None:
        self._govde = govde
        self.kullanim = kullanim

    def json(self) -> object:
        return self._govde


class SahteIstemci:
    """``mesaj`` çağrısını kaydeder ve önceden verilen yanıtı döndürür."""

    def __init__(self, govde: object = GECERLI_YORUM) -> None:
        self.kullanim = Kullanim(model="deepseek-v4.1-flash", girdi_token=900, cikti_token=200)
        self._govde = govde
        self.cagrilar: list[tuple[dict, bool]] = []

    def mesaj(self, istek: dict, ruya_icerir: bool = False) -> SahteYanit:
        self.cagrilar.append((istek, ruya_icerir))
        return SahteYanit(self._govde, self.kullanim)


def _sembol(yalin: str) -> Sembol:
    return Sembol(yalin=yalin, ham_ifade=yalin)


def _eslesme(yalin: str, symbol_id: str | None = "yilan", yontem: str = "birebir") -> Eslesme:
    return Eslesme(sembol=_sembol(yalin), symbol_id=symbol_id, yontem=yontem, guven=1.0)


def _cikarim(*, hassas_icerik: bool = False) -> CikarimSonucu:
    return CikarimSonucu(semboller=[_sembol("yılan")], hassas_icerik=hassas_icerik)


def _getirilenler() -> dict[str, list[Aday]]:
    return {
        "yilan": [
            Aday(madde=NABLUSI, skor=2.0, gerekceler=["nitelik:siyah"]),
            Aday(madde=MILLER, skor=1.0),
        ]
    }


def _calistir(
    govde: object = GECERLI_YORUM,
    *,
    cikarim: CikarimSonucu | None = None,
    eslesmeler: list[Eslesme] | None = None,
    getirilenler: dict[str, list[Aday]] | None = None,
):
    istemci = SahteIstemci(govde)
    yorum, kullanim = sentez.synthesize(
        _cikarim() if cikarim is None else cikarim,
        [_eslesme("yılan")] if eslesmeler is None else eslesmeler,
        _getirilenler() if getirilenler is None else getirilenler,
        None,
        istemci,
    )
    return istemci, yorum, kullanim


def _istek(istemci: SahteIstemci) -> dict:
    assert len(istemci.cagrilar) == 1
    return istemci.cagrilar[0][0]


def _mesajlar(istek: dict) -> dict[str, str]:
    return {m["role"]: m["content"] for m in istek["messages"]}


# --- synthesize: istek biçimi -----------------------------------------------


def test_ruya_icerir_true_ile_gonderilir():
    istemci, _, _ = _calistir()

    assert istemci.cagrilar[0][1] is True


def test_sistem_mesaji_sentez_talimati():
    istemci, _, _ = _calistir()

    assert _mesajlar(_istek(istemci))["system"] == talimat_oku("sentez_v1")


def test_adaylar_numarali_kaynak_olarak_verilir():
    istemci, _, _ = _calistir()

    kullanici = _mesajlar(_istek(istemci))["user"]
    satirlar = kullanici.splitlines()
    for entry_id in ("nablusi:004310", "miller:018710"):
        assert any(s.startswith("[K") and entry_id in s for s in satirlar)
    assert "[K1]" in kullanici
    assert "[K2]" in kullanici
    assert NABLUSI.metin_tr in kullanici
    assert NABLUSI.metin_asli in kullanici
    assert MILLER.metin_asli in kullanici


# --- synthesize: sonuç ------------------------------------------------------


def test_bolumler_ve_dogrulanmis_atiflar_doner():
    _, yorum, _ = _calistir()

    assert [b.metin for b in yorum.bolumler] == [
        "Yılan",
        "Nablusi'nin tabirnamesine göre siyah yılan güçlü bir düşmandır.",
    ]
    assert yorum.bolumler[0].atiflar == []
    assert yorum.bolumler[1].atiflar == [
        Atif(entry_id="nablusi:004310", baslik="Abdülganî en-Nablusî · حية", alinti=ALINTI)
    ]
    assert yorum.metin == "".join(b.metin for b in yorum.bolumler)


def test_uyari_her_zaman_eklenir():
    _, yorum, _ = _calistir()

    assert yorum.uyari == UYARI_METNI


def test_hassas_icerikte_guvenlik_notu_eklenir():
    _, yorum, _ = _calistir(cikarim=_cikarim(hassas_icerik=True))

    assert yorum.guvenlik_notu == GUVENLIK_NOTU


def test_hassas_olmayan_icerikte_guvenlik_notu_yok():
    _, yorum, _ = _calistir()

    assert yorum.guvenlik_notu is None


def test_kullanim_yanittan_aynen_doner():
    istemci, _, kullanim = _calistir()

    assert kullanim == istemci.kullanim


def test_yontem_yok_sembol_bulunamayanlara_eklenir():
    _, yorum, _ = _calistir(
        eslesmeler=[_eslesme("yılan"), _eslesme("at", symbol_id=None, yontem="yok")]
    )

    assert "at" in yorum.bulunamayanlar


def test_maddesi_olmayan_sembol_bulunamayanlara_eklenir():
    _, yorum, _ = _calistir(
        eslesmeler=[_eslesme("yılan"), _eslesme("at", symbol_id="at")],
        getirilenler={"yilan": _getirilenler()["yilan"], "at": []},
    )

    assert "at" in yorum.bulunamayanlar


def test_bulunamayanlar_tekrarlanmaz():
    govde = {**GECERLI_YORUM, "bulunamayanlar": ["at", "deniz"]}
    _, yorum, _ = _calistir(
        govde,
        eslesmeler=[_eslesme("yılan"), _eslesme("at", symbol_id=None, yontem="yok")],
    )

    assert yorum.bulunamayanlar.count("at") == 1
    assert "deniz" in yorum.bulunamayanlar


@pytest.mark.parametrize(
    "govde",
    [
        {"bolumler": "yılan"},
        {"bolumler": [{"metin": 1}]},
        {"bulunamayanlar": []},
    ],
)
def test_gecersiz_json_sekli_yanitbozuk_verir(govde: object):
    with pytest.raises(YanitBozuk):
        _calistir(govde)
