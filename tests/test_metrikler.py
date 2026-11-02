import datetime as dt

from ruya.degerlendirme.metrikler import (
    atif_kapsami,
    esleme_dogrulugu,
    kaynak_cesitliligi,
    olumsuzlama_hatalari,
    recall_at_k,
    sembol_precision,
    sembol_recall,
    yasak_ifadeler,
)
from ruya.schemas import (
    Aday,
    Atif,
    CikarimSonucu,
    Eslesme,
    Madde,
    RuyaGirdisi,
    Sembol,
    SorguKaydi,
    TestOrnegi,
    Yorum,
    YorumBolumu,
)


def _sembol(yalin: str) -> Sembol:
    return Sembol(yalin=yalin, ham_ifade=yalin)


def _eslesme(yalin: str, symbol_id: str | None) -> Eslesme:
    if symbol_id is None:
        return Eslesme(sembol=_sembol(yalin), symbol_id=None, yontem="yok", guven=0.0)
    return Eslesme(sembol=_sembol(yalin), symbol_id=symbol_id, yontem="birebir", guven=1.0)


def _kayit(eslesmeler: list[Eslesme] | None = None, **alanlar) -> SorguKaydi:
    return SorguKaydi(
        zaman=dt.datetime(2026, 11, 20, tzinfo=dt.UTC),
        girdi=RuyaGirdisi(metin="Rüyamda bir yılan gördüm."),
        cikarim=CikarimSonucu(semboller=[e.sembol for e in eslesmeler or []]),
        eslesmeler=eslesmeler or [],
        **alanlar,
    )


def _ornek(**alanlar) -> TestOrnegi:
    return TestOrnegi(id="r001", metin="Rüyamda bir yılan gördüm.", **alanlar)


def _madde(entry_id: str) -> Madde:
    kaynak = entry_id.split(":")[0]
    return Madde(
        entry_id=entry_id,
        kaynak=kaynak,
        eser="Örnek eser",
        yazar="Örnek yazar",
        gelenek="islami_klasik",
        dil="tr",
        lisans="CC-BY-NC-SA-4.0",
        konum={"satir": 1},
        metin_asli="(örnek metin)",
    )


def _aday(entry_id: str) -> Aday:
    return Aday(madde=_madde(entry_id), skor=1.0)


# --- sembol_recall ----------------------------------------------------------


def test_sembol_recall_beklenenlerin_bulunan_orani():
    kayit = _kayit([_eslesme("yılan", "yilan"), _eslesme("deniz", "deniz")])
    ornek = _ornek(beklenen_semboller=["yilan", "deniz", "su"])
    assert sembol_recall(kayit, ornek) == 2 / 3


def test_sembol_recall_beklenen_yoksa_none():
    kayit = _kayit([_eslesme("yılan", "yilan")])
    assert sembol_recall(kayit, _ornek()) is None


# --- sembol_precision -------------------------------------------------------


def test_sembol_precision_dogru_sembollerin_bulunanlara_orani():
    kayit = _kayit(
        [
            _eslesme("yılan", "yilan"),
            _eslesme("deniz", "deniz"),
            _eslesme("uzay gemisi", None),
        ]
    )
    ornek = _ornek(beklenen_semboller=["yilan"])
    assert sembol_precision(kayit, ornek) == 1 / 2


# --- olumsuzlama_hatalari ---------------------------------------------------


def test_olumsuzlama_hatalari_eslenen_yasak_sembolleri_sayar():
    kayit = _kayit([_eslesme("yılan", "yilan"), _eslesme("deniz", "deniz")])
    ornek = _ornek(olmamasi_gerekenler=["yilan", "su"])
    assert olumsuzlama_hatalari(kayit, ornek) == 1


def test_olumsuzlama_hatalari_temiz_kayitta_sifir():
    kayit = _kayit([_eslesme("deniz", "deniz")])
    ornek = _ornek(olmamasi_gerekenler=["yilan"])
    assert olumsuzlama_hatalari(kayit, ornek) == 0


# --- esleme_dogrulugu -------------------------------------------------------


def test_esleme_dogrulugu_dogru_kimliklerin_eslenenlere_orani():
    kayit = _kayit(
        [
            _eslesme("yılan", "yilan"),
            _eslesme("deniz", "deniz"),
            _eslesme("uzay gemisi", None),
        ]
    )
    ornek = _ornek(beklenen_semboller=["yilan", "su"])
    assert esleme_dogrulugu(kayit, ornek) == 1 / 2


# --- recall_at_k ------------------------------------------------------------


def test_recall_at_k_ilk_k_adayda_bulunan_beklenen_maddeler():
    kayit = _kayit(
        getirilenler={
            "yilan": [
                _aday("nablusi:004314"),
                _aday("nablusi:004310"),
                _aday("miller:000001"),
                _aday("miller:000002"),
                _aday("miller:000003"),
                _aday("miller:018710"),
            ]
        }
    )
    ornek = _ornek(beklenen_maddeler={"yilan": ["nablusi:004310", "miller:018710"]})
    assert recall_at_k(kayit, ornek, k=5) == 0.5
    assert recall_at_k(kayit, ornek, k=6) == 1.0


def test_recall_at_k_beklenen_madde_yoksa_none():
    kayit = _kayit(getirilenler={"yilan": [_aday("nablusi:004310")]})
    assert recall_at_k(kayit, _ornek()) is None


# --- kaynak_cesitliligi -----------------------------------------------------


def test_kaynak_cesitliligi_maddesi_olan_sembollerin_ortalamasi():
    kayit = _kayit(
        getirilenler={
            "yilan": [_aday("nablusi:004310"), _aday("miller:018710")],
            "deniz": [_aday("nablusi:004314")],
        }
    )
    assert kaynak_cesitliligi(kayit) == 1.5


def test_kaynak_cesitliligi_getirilen_yoksa_none():
    assert kaynak_cesitliligi(_kayit()) is None


# --- atif_kapsami -----------------------------------------------------------


def _atif() -> Atif:
    return Atif(entry_id="nablusi:004310", baslik="Nablusi · حية (yılan)", alinti="(örnek)")


def test_atif_kapsami_baslik_ve_harfsiz_bolumler_sayilmaz():
    yorum = Yorum(
        bolumler=[
            YorumBolumu(metin="## Yılan"),
            YorumBolumu(metin="Yılan, düşmanlığa işaret eder.", atiflar=[_atif()]),
            YorumBolumu(metin="Deniz ise ferahlığa yorulur."),
            YorumBolumu(metin="---"),
        ],
        uyari="Uyarı metni.",
    )
    kayit = _kayit(yorum=yorum)
    assert atif_kapsami(kayit) == 0.5


def test_atif_kapsami_iddia_bolumu_yoksa_none():
    yorum = Yorum(bolumler=[YorumBolumu(metin="## Yılan")], uyari="Uyarı metni.")
    assert atif_kapsami(_kayit(yorum=yorum)) is None


# --- yasak_ifadeler ---------------------------------------------------------


def test_yasak_ifadeler_turkce_kucuk_harfle_bulur():
    assert yasak_ifadeler("Bu rüya KESİNLİKLE hayra yorulur.") == ["kesinlikle"]


def test_yasak_ifadeler_cok_kelimeli_ifade():
    assert yasak_ifadeler("İbn Sirin'e göre bu bir işarettir.") == ["ibn sirin'e göre"]


def test_yasak_ifadeler_temiz_metinde_bos():
    assert yasak_ifadeler("Rüyanız hayırlara vesile olsun.") == []
