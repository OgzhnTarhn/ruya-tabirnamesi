"""``synthesize`` paralel modu (sembol başına istek + genel yorum) birim testleri.

Ağa çıkılmaz: iş parçacığı güvenli sahte istemci isteği kaydeder, hazır bir yanıt nesnesi
döndürür. Sahte istemci isteği sistem mesajına göre yönlendirir.
"""

from __future__ import annotations

import threading
import time

import pytest

from ruya.config import MODEL_SENTEZ
from ruya.hatalar import YanitBozuk
from ruya.llm.talimatlar import talimat_oku
from ruya.pipeline import synthesize as sentez
from ruya.schemas import (
    Aday,
    Baglam,
    CikarimSonucu,
    Eslesme,
    Kosul,
    Kullanim,
    Madde,
    Sembol,
    YorumBolumu,
)


@pytest.fixture(autouse=True)
def _paralel_mod(monkeypatch):
    """Bu dosyadaki testler paralel sentez modunu sınar."""
    # raising=False: sabit henüz eklenmemişken de testler eksik davranışla yüzleşsin.
    monkeypatch.setattr(sentez, "PARALEL_SENTEZ", True, raising=False)


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
    kosullar: list[Kosul] | None = None,
    yontem: list[str] | None = None,
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
        kosullar=kosullar,
        yontem=yontem,
    )


YILAN_NABLUSI = _madde(
    "nablusi:004310",
    "nablusi",
    yazar="Abdülganî en-Nablusî",
    baslik_asli="حية",
    sembol_tr="yılan",
    metin_tr="Yılan rüyada düşmanla yorumlanır; siyah yılan daha güçlü bir düşmandır.",
    metin_asli="حية يدل على عدو",
)

YILAN_MILLER = _madde(
    "miller:000001",
    "miller",
    yazar="Gustavus Hindman Miller",
    baslik_asli="Snakes",
    sembol_tr="yılan",
    metin_tr="Yılan görmek düşmanın habercisidir.",
    metin_asli="To dream of snakes is a warning of enemies.",
)

DENIZ_NABLUSI = _madde(
    "nablusi:000777",
    "nablusi",
    yazar="Abdülganî en-Nablusî",
    baslik_asli="بحر",
    sembol_tr="deniz",
    metin_tr="Deniz rüyada ilim ve geniş bir rızka yorumlanır.",
    metin_asli="بحر يدل على العلم",
)

YILAN_ALINTI = "siyah yılan daha güçlü bir düşmandır"
DENIZ_ALINTI = "ilim ve geniş bir rızka"

YILAN_METIN = "Yılan: düşmanla yorumlanır."
DENIZ_METIN = "Deniz: ilim ve rızka yorumlanır."


# --- sahte istemci ----------------------------------------------------------


class SahteYanit:
    """LLMYaniti'nin synthesize'ın kullandığı yüzü: ``json()`` ve ``kullanim``."""

    def __init__(self, govde: object, kullanim: Kullanim) -> None:
        self._govde = govde
        self.kullanim = kullanim

    def json(self) -> object:
        return self._govde


def _mesajlar(istek: dict) -> dict[str, str]:
    return {m["role"]: m["content"] for m in istek["messages"]}


class ParalelSahteIstemci:
    """İsteği sistem mesajına göre yönlendiren, çağrıları kilit altında kaydeden istemci."""

    def __init__(
        self,
        *,
        disk_onbelleginden: bool = False,
        yanlis_atif: set[str] | None = None,
        bos_bolumler: bool = False,
        genel_hatali: bool = False,
        hatali_semboller: set[str] | None = None,
    ) -> None:
        self._kilit = threading.Lock()
        self.cagrilar: list[tuple[dict, bool]] = []
        self._disk = disk_onbelleginden
        self._yanlis_atif = yanlis_atif or set()
        self._bos_bolumler = bos_bolumler
        self._genel_hatali = genel_hatali
        self._hatali_semboller = hatali_semboller or set()

    def _kullanim(self) -> Kullanim:
        return Kullanim(
            model=MODEL_SENTEZ,
            girdi_token=100,
            cikti_token=50,
            maliyet_usd=0.01,
            disk_onbelleginden=self._disk,
        )

    def _sembol_govdesi(self, ad: str) -> dict:
        if self._bos_bolumler:
            return {"bolumler": [], "bulunamayanlar": []}
        if ad == "yılan":
            madde, alinti, metin = YILAN_NABLUSI, YILAN_ALINTI, YILAN_METIN
        else:
            madde, alinti, metin = DENIZ_NABLUSI, DENIZ_ALINTI, DENIZ_METIN
        if ad in self._yanlis_atif:
            # Başka sembolün maddesine atıf: doğrulama bunu atmalı.
            madde = DENIZ_NABLUSI if ad == "yılan" else YILAN_NABLUSI
            alinti = DENIZ_ALINTI if ad == "yılan" else YILAN_ALINTI
        return {
            "bolumler": [
                {"metin": metin, "kaynaklar": [{"entry_id": madde.entry_id, "alinti": alinti}]}
            ],
            "bulunamayanlar": [],
        }

    def mesaj(self, istek: dict, ruya_icerir: bool = False) -> SahteYanit:
        with self._kilit:
            self.cagrilar.append((istek, ruya_icerir))
        mesajlar = _mesajlar(istek)
        if mesajlar["system"] == talimat_oku(sentez.GENEL_TALIMATI):
            if self._genel_hatali:
                raise YanitBozuk("genel yorum bozuk")
            return SahteYanit({"genel_yorum": "  Genel.  "}, self._kullanim())
        kullanici = mesajlar["user"]
        if "- yılan" in kullanici:
            ad = "yılan"
        elif "- deniz" in kullanici:
            ad = "deniz"
        else:
            raise AssertionError(f"sahte istemci isteği tanıyamadı: {kullanici!r}")
        if ad == "yılan":
            time.sleep(0.05)  # yılan yavaş bitsin: sıra yine de korunmalı
        if ad in self._hatali_semboller:
            raise YanitBozuk(f"{ad} yanıtı bozuk")
        return SahteYanit(self._sembol_govdesi(ad), self._kullanim())


# --- yardımcılar ------------------------------------------------------------


def _sembol(yalin: str) -> Sembol:
    return Sembol(yalin=yalin, ham_ifade=yalin)


def _eslesme(yalin: str, symbol_id: str | None = "yilan", yontem: str = "birebir") -> Eslesme:
    return Eslesme(sembol=_sembol(yalin), symbol_id=symbol_id, yontem=yontem, guven=1.0)


def _cikarim(*, hassas_icerik: bool = False) -> CikarimSonucu:
    return CikarimSonucu(
        semboller=[_sembol("yılan"), _sembol("deniz")], hassas_icerik=hassas_icerik
    )


def _getirilenler() -> dict[str, list[Aday]]:
    return {
        "yilan": [
            Aday(madde=YILAN_NABLUSI, skor=2.0, gerekceler=["nitelik:siyah"]),
            Aday(madde=YILAN_MILLER, skor=1.0),
        ],
        "deniz": [Aday(madde=DENIZ_NABLUSI, skor=2.0)],
    }


def _calistir(
    *,
    cikarim: CikarimSonucu | None = None,
    eslesmeler: list[Eslesme] | None = None,
    getirilenler: dict[str, list[Aday]] | None = None,
    baglam: Baglam | None = None,
    istemci: ParalelSahteIstemci | None = None,
    ilerleme=None,
):
    istemci = ParalelSahteIstemci() if istemci is None else istemci
    ek = {} if ilerleme is None else {"ilerleme": ilerleme}
    yorum, kullanim = sentez.synthesize(
        _cikarim() if cikarim is None else cikarim,
        [_eslesme("yılan", "yilan"), _eslesme("deniz", "deniz")]
        if eslesmeler is None
        else eslesmeler,
        _getirilenler() if getirilenler is None else getirilenler,
        baglam,
        istemci,
        **ek,
    )
    return istemci, yorum, kullanim


def _sembol_istekleri(istemci: ParalelSahteIstemci) -> list[dict]:
    return [
        istek
        for istek, _ in istemci.cagrilar
        if _mesajlar(istek)["system"] == talimat_oku(sentez.SEMBOL_TALIMATI)
    ]


def _genel_istekleri(istemci: ParalelSahteIstemci) -> list[dict]:
    return [
        istek
        for istek, _ in istemci.cagrilar
        if _mesajlar(istek)["system"] == talimat_oku(sentez.GENEL_TALIMATI)
    ]


# --- istek biçimi -----------------------------------------------------------


def test_sembol_basina_bir_istek_ve_bir_genel_istek():
    istemci, _, _ = _calistir()

    assert len(istemci.cagrilar) == 3
    assert len(_sembol_istekleri(istemci)) == 2
    assert len(_genel_istekleri(istemci)) == 1
    assert all(ruya_icerir is True for _, ruya_icerir in istemci.cagrilar)


def test_sembol_istegi_kendi_talimati_ve_yalnizca_kendi_maddeleri():
    istemci, _, _ = _calistir()

    istekler = _sembol_istekleri(istemci)
    yilan = next(i for i in istekler if "- yılan" in _mesajlar(i)["user"])
    deniz = next(i for i in istekler if "- deniz" in _mesajlar(i)["user"])

    yilan_kullanici = _mesajlar(yilan)["user"]
    assert "- yılan" in yilan_kullanici
    assert "- deniz" not in yilan_kullanici
    assert "nablusi:004310" in yilan_kullanici
    assert "miller:000001" in yilan_kullanici
    assert "nablusi:000777" not in yilan_kullanici

    deniz_kullanici = _mesajlar(deniz)["user"]
    assert "- deniz" in deniz_kullanici
    assert "- yılan" not in deniz_kullanici
    assert "nablusi:000777" in deniz_kullanici
    assert "nablusi:004310" not in deniz_kullanici
    assert "miller:000001" not in deniz_kullanici


# --- sonuç ------------------------------------------------------------------


def test_bolumler_sembol_sirasinda_yavas_yanita_ragmen():
    _, yorum, _ = _calistir()

    assert [b.metin for b in yorum.bolumler] == [YILAN_METIN, DENIZ_METIN]


def test_baska_sembolun_atfi_atilir():
    istemci = ParalelSahteIstemci(yanlis_atif={"yılan"})
    _, yorum, _ = _calistir(istemci=istemci)

    assert yorum.bolumler[0].metin == YILAN_METIN
    assert yorum.bolumler[0].atiflar == []
    assert [a.entry_id for a in yorum.bolumler[1].atiflar] == ["nablusi:000777"]


def test_genel_istek_bolum_metinlerini_icerir_ve_genel_yorum_striplenir():
    istemci, yorum, _ = _calistir()

    genel = _genel_istekleri(istemci)[0]
    kullanici = _mesajlar(genel)["user"]
    assert YILAN_METIN in kullanici
    assert DENIZ_METIN in kullanici
    assert yorum.genel_yorum == "Genel."


def test_genel_cagri_bozuksa_genel_yorum_none_doner():
    istemci = ParalelSahteIstemci(genel_hatali=True)
    _, yorum, _ = _calistir(istemci=istemci)

    assert yorum.genel_yorum is None
    assert [b.metin for b in yorum.bolumler] == [YILAN_METIN, DENIZ_METIN]


def test_sembol_cagrisi_bozuksa_yanitbozuk_yukselir():
    istemci = ParalelSahteIstemci(hatali_semboller={"yılan"})

    with pytest.raises(YanitBozuk):
        _calistir(istemci=istemci)


def test_butun_bolumler_bossa_genel_istek_yapilmaz():
    istemci = ParalelSahteIstemci(bos_bolumler=True)
    _, yorum, _ = _calistir(istemci=istemci)

    assert _genel_istekleri(istemci) == []
    assert len(istemci.cagrilar) == 2
    assert yorum.genel_yorum is None


def test_maddesi_olmayan_sembol_istek_almaz_ve_bulunamayanlara_girer():
    istemci, yorum, _ = _calistir(
        eslesmeler=[_eslesme("yılan", "yilan"), _eslesme("deniz", "deniz"), _eslesme("at", "at")],
        getirilenler={**_getirilenler(), "at": []},
    )

    assert len(_sembol_istekleri(istemci)) == 2
    assert all("- at" not in _mesajlar(i)["user"] for i in _sembol_istekleri(istemci))
    assert "at" in yorum.bulunamayanlar


def test_hic_madde_yoksa_cagri_yapilmaz():
    istemci, yorum, kullanim = _calistir(getirilenler={})

    assert istemci.cagrilar == []
    assert yorum.bolumler == []
    assert yorum.genel_yorum is None
    assert kullanim.girdi_token == 0
    assert kullanim.cikti_token == 0


def test_kullanim_butun_cagrilarin_toplamidir():
    _, _, kullanim = _calistir()

    assert kullanim.girdi_token == 300
    assert kullanim.cikti_token == 150
    assert kullanim.maliyet_usd == pytest.approx(0.03)


def test_disk_onbelleginden_yalnizca_butun_cagrilar_ondan_geldiyse_true():
    _, _, hepsi_diskten = _calistir(istemci=ParalelSahteIstemci(disk_onbelleginden=True))
    _, _, hicbiri = _calistir(istemci=ParalelSahteIstemci(disk_onbelleginden=False))

    assert hepsi_diskten.disk_onbelleginden is True
    assert hicbiri.disk_onbelleginden is False


# --- ilerleme geri çağrısı --------------------------------------------------


def test_ilerleme_her_biten_sembol_icin_sembol_sirasinda_cagrilir():
    cagrilar: list[list[YorumBolumu]] = []

    _calistir(ilerleme=cagrilar.append)

    # yılan yavaş bitse de liste sembol sırasında: önce deniz, sonra yılan + deniz.
    assert [[b.metin for b in bolumler] for bolumler in cagrilar] == [
        [DENIZ_METIN],
        [YILAN_METIN, DENIZ_METIN],
    ]


def test_ilerleme_genel_yorum_icin_cagrilmaz():
    cagrilar: list[list[YorumBolumu]] = []

    istemci, _, _ = _calistir(ilerleme=cagrilar.append)

    assert len(_genel_istekleri(istemci)) == 1
    assert len(cagrilar) == 2


def test_ilerleme_synthesize_i_cagiran_is_parcacigindan_cagrilir():
    ana_is_parcacigi = threading.get_ident()
    kimlikler: list[int] = []

    _calistir(ilerleme=lambda bolumler: kimlikler.append(threading.get_ident()))

    assert kimlikler == [ana_is_parcacigi, ana_is_parcacigi]


def test_ilerleme_verilmezse_davranis_degismez():
    _, yorum, _ = _calistir()

    assert [b.metin for b in yorum.bolumler] == [YILAN_METIN, DENIZ_METIN]


def test_tek_cagri_modunda_ilerleme_kabul_edilir_ama_cagrilmaz(monkeypatch):
    monkeypatch.setattr(sentez, "PARALEL_SENTEZ", False)
    cagrilar: list[list[YorumBolumu]] = []

    istemci, yorum, _ = _calistir(ilerleme=cagrilar.append)

    assert cagrilar == []
    assert len(istemci.cagrilar) == 1
    assert [b.metin for b in yorum.bolumler] == [YILAN_METIN]
