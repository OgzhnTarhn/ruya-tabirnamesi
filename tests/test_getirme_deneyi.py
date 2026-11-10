"""Getirme deneyi birim testleri (docs/15, K4–K5).

Ağa çıkmadan çalışır: LLM istemcisi, depo ve hibrit indeks sahtelerle değiştirilir;
dosyalar ``tmp_path`` altına yazılır.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from ruya.degerlendirme.getirme_deneyi import (
    CESITLER,
    deney_kos,
    etiket_dosyasi_yaz,
    etiketleri_oku,
    havuz,
    mrr,
    ozet,
    recall_at_k,
    satirlari_oku,
)

from ruya.hatalar import LLMHatasi
from ruya.schemas import (
    CikarimSonucu,
    Eslesme,
    Kullanim,
    Madde,
    RuyaGirdisi,
    Sembol,
    TestOrnegi,
    getirme_anahtari,
)

# --- Yardımcılar ------------------------------------------------------------


def _madde(entry_id: str, *, metin_tr: str | None = "Rüyada bir şey görmek.") -> Madde:
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
        metin_asli="(asıl metin)",
        metin_tr=metin_tr,
    )


class _SahteDepo:
    """``.madde(entry_id)`` veren en küçük depo; olmayan kimlikte KeyError atar."""

    def __init__(self, maddeler: dict[str, Madde]) -> None:
        self._maddeler = maddeler

    def madde(self, entry_id: str) -> Madde:
        return self._maddeler[entry_id]


def _satir(
    ornek_id: str,
    cesit: str,
    anahtar: str,
    sembol: str,
    sirali: list[list[object]],
) -> dict:
    return {
        "ornek_id": ornek_id,
        "cesit": cesit,
        "anahtar": anahtar,
        "sembol": sembol,
        "sirali": sirali,
    }


def _sembol(yalin: str) -> Sembol:
    return Sembol(yalin=yalin, ham_ifade=yalin)


def _eslesme(yalin: str, symbol_id: str | None = "yilan") -> Eslesme:
    if symbol_id is None:
        return Eslesme(sembol=_sembol(yalin), symbol_id=None, yontem="yok", guven=0.0)
    return Eslesme(sembol=_sembol(yalin), symbol_id=symbol_id, yontem="birebir", guven=1.0)


# --- CESITLER ---------------------------------------------------------------


def test_cesitler_tam_dort_cesit_ve_kollar():
    assert set(CESITLER) == {"G0", "G1", "G2", "G3"}
    assert CESITLER["G0"] == (frozenset({"sozluk", "bm25", "vektor", "hyde"}), True)
    assert CESITLER["G1"] == (frozenset({"sozluk", "bm25", "vektor", "hyde"}), False)
    assert CESITLER["G2"] == (frozenset({"sozluk", "bm25"}), True)
    assert CESITLER["G3"] == (frozenset({"sozluk", "bm25", "vektor"}), True)


# --- havuz ------------------------------------------------------------------


def test_havuz_cesitlerin_ilk_k_birlesimi_artan_sirada():
    satirlar = [
        _satir("r001", "G0", "yilan", "yılan", [["a:1", 0.9], ["a:2", 0.8], ["a:3", 0.7]]),
        _satir("r001", "G1", "yilan", "yılan", [["a:2", 0.9], ["a:4", 0.8], ["a:5", 0.7]]),
        _satir("r001", "G2", "yilan", "yılan", [["a:1", 0.9], ["a:5", 0.8]]),
    ]
    sonuc = havuz(satirlar, k=2)
    assert sonuc == {("r001", "yilan"): ["a:1", "a:2", "a:4", "a:5"]}


def test_havuz_anahtarlari_ayirir_ve_tekrarlari_birlestirir():
    satirlar = [
        _satir("r001", "G0", "yilan", "yılan", [["a:1", 0.9]]),
        _satir("r001", "G1", "yilan", "yılan", [["a:1", 0.8]]),
        _satir("r001", "G0", "su", "su", [["b:2", 0.9], ["b:1", 0.8]]),
        _satir("r002", "G0", "yilan", "yılan", [["c:1", 0.9]]),
    ]
    sonuc = havuz(satirlar, k=5)
    assert sonuc[("r001", "yilan")] == ["a:1"]
    assert sonuc[("r001", "su")] == ["b:1", "b:2"]
    assert sonuc[("r002", "yilan")] == ["c:1"]


# --- etiket dosyası ---------------------------------------------------------


def _etiket_satirlari() -> list[dict]:
    return [
        _satir("r001", "G0", "yilan", "yılan", [["nablusi:0412", 0.9], ["miller:0007", 0.8]]),
        _satir("r001", "G2", "yilan", "yılan", [["miller:0007", 0.9], ["ibn:0003", 0.8]]),
        _satir("r001", "G0", "su", "su", [["nablusi:0100", 0.9]]),
    ]


def test_etiket_dosyasi_yaz_bicim(tmp_path: Path):
    satirlar = _etiket_satirlari()
    depo = _SahteDepo(
        {
            "nablusi:0412": _madde("nablusi:0412", metin_tr="Yılan görmek\nhayra yorulur."),
            "miller:0007": _madde("miller:0007", metin_tr=None),
            "ibn:0003": _madde("ibn:0003"),
            "nablusi:0100": _madde("nablusi:0100", metin_tr="Su berraklıktır."),
        }
    )
    yol = tmp_path / "etiket.md"
    etiket_dosyasi_yaz(
        havuz(satirlar, k=5),
        satirlar,
        {"r001": "Rüyamda bir yılan gördüm."},
        depo,
        yol,
    )

    metin = yol.read_text(encoding="utf-8")
    assert "## r001" in metin
    assert "> Rüyamda bir yılan gördüm." in metin
    assert "### yılan (yilan)" in metin
    assert "### su (su)" in metin
    # Havuz artan entry_id sırasıyla yazılır; hangi çeşidin bulduğu görünmez.
    assert "- [ ] ibn:0003 — Rüyada bir şey görmek." in metin
    assert "- [ ] miller:0007 — (asıl metin)" in metin
    assert "- [ ] nablusi:0412 — Yılan görmek hayra yorulur." in metin
    assert "- [ ] nablusi:0100 — Su berraklıktır." in metin
    assert metin.index("ibn:0003") < metin.index("miller:0007") < metin.index("nablusi:0412")


def test_etiket_dosyasi_yaz_metin_kirpar_ve_eksik_maddeyi_yazar(tmp_path: Path):
    satirlar = [
        _satir("r001", "G0", "yilan", "yılan", [["nablusi:0412", 0.9], ["yok:0001", 0.8]]),
    ]
    uzun = "a" * 400
    depo = _SahteDepo({"nablusi:0412": _madde("nablusi:0412", metin_tr=uzun)})
    yol = tmp_path / "etiket.md"
    etiket_dosyasi_yaz(havuz(satirlar, k=5), satirlar, {"r001": "Rüya."}, depo, yol)

    metin = yol.read_text(encoding="utf-8")
    assert "- [ ] nablusi:0412 — " + "a" * 300 + "\n" in metin
    assert "a" * 301 not in metin
    assert "- [ ] yok:0001 — (madde bulunamadı)" in metin


def test_etiketleri_oku_gidis_donus(tmp_path: Path):
    satirlar = _etiket_satirlari()
    depo = _SahteDepo(
        {
            "nablusi:0412": _madde("nablusi:0412"),
            "miller:0007": _madde("miller:0007"),
            "ibn:0003": _madde("ibn:0003"),
            "nablusi:0100": _madde("nablusi:0100"),
        }
    )
    yol = tmp_path / "etiket.md"
    etiket_dosyasi_yaz(havuz(satirlar, k=5), satirlar, {"r001": "Rüya."}, depo, yol)

    metin = yol.read_text(encoding="utf-8")
    yol.write_text(metin.replace("- [ ]", "- [x]", 2), encoding="utf-8")

    etiketler = etiketleri_oku(yol)
    assert set(etiketler) == {("r001", "yilan"), ("r001", "su")}
    # Dosyadaki ilk iki işaretli satır: su bölümünün tek maddesi ve yılanın ilk maddesi.
    assert etiketler[("r001", "su")] == {"nablusi:0100"}
    assert etiketler[("r001", "yilan")] == {"ibn:0003"}


def test_etiketleri_oku_buyuk_x_ve_isaretsiz_satir(tmp_path: Path):
    yol = tmp_path / "etiket.md"
    yol.write_text(
        "## r001\n"
        "> Rüya.\n"
        "\n"
        "### yılan (yilan)\n"
        "- [X] nablusi:0412 — bir metin\n"
        "- [ ] miller:0007 — başka metin\n",
        encoding="utf-8",
    )
    assert etiketleri_oku(yol) == {("r001", "yilan"): {"nablusi:0412"}}


# --- recall_at_k / mrr ------------------------------------------------------


def test_recall_at_k_ilgili_yoksa_none():
    assert recall_at_k(["a:1"], set()) is None


def test_recall_at_k_ilk_k_ile_kesişim():
    assert recall_at_k(["a:1", "a:2", "a:3"], {"a:1", "a:3"}, k=2) == 0.5
    assert recall_at_k(["a:1", "a:2", "a:3"], {"a:1", "a:3"}, k=5) == 1.0


def test_recall_at_k_payda_min_k_ve_ilgili():
    # |ilgili| = 1 < k: payda 1 olur.
    assert recall_at_k(["x:1", "a:1"], {"a:1"}, k=5) == 1.0
    # |ilgili| = 3 > k = 2: payda 2 olur.
    assert recall_at_k(["a:1", "a:2"], {"a:1", "a:2", "a:3"}, k=2) == 1.0


def test_mrr_ilgili_yoksa_none():
    assert mrr(["a:1"], set()) is None


def test_mrr_ilk_ilgilinin_sirasi():
    assert mrr(["x:1", "a:1", "a:2"], {"a:1", "a:2"}) == 0.5
    assert mrr(["a:1", "a:2"], {"a:2"}) == 0.5
    assert mrr(["x:1", "x:2"], {"a:1"}) == 0.0


# --- ozet -------------------------------------------------------------------


def _ozet_satirlari() -> list[dict]:
    return [
        _satir("r001", "G0", "yilan", "yılan", [["a:1", 0.9], ["x:9", 0.8], ["a:2", 0.7]]),
        _satir("r001", "G0", "su", "su", [["x:1", 0.9], ["b:1", 0.8]]),
        _satir("r001", "G1", "yilan", "yılan", [["x:9", 0.9], ["a:1", 0.8]]),
        _satir("r001", "G1", "su", "su", [["x:1", 0.9], ["x:2", 0.8]]),
        # G2 yalnızca etiketi boş bir anahtara sahip: kullanılabilir anahtar yok.
        _satir("r002", "G2", "yilan", "yılan", [["a:1", 0.9]]),
    ]


def test_ozet_cesit_basina_ortalama_ve_n():
    etiketler = {
        ("r001", "yilan"): {"a:1", "a:2"},
        ("r001", "su"): {"b:1"},
        ("r002", "yilan"): set(),
    }
    sonuc = ozet(_ozet_satirlari(), etiketler, k=5)

    assert sonuc["G0"]["n"] == 2
    assert sonuc["G0"]["recall"] == pytest.approx(1.0)
    assert sonuc["G0"]["mrr"] == pytest.approx(0.75)

    assert sonuc["G1"]["n"] == 2
    assert sonuc["G1"]["recall"] == pytest.approx(0.25)
    assert sonuc["G1"]["mrr"] == pytest.approx(0.25)

    assert sonuc["G2"]["n"] == 0
    assert sonuc["G2"]["recall"] is None
    assert sonuc["G2"]["mrr"] is None


# --- deney_kos --------------------------------------------------------------


def _ornekler() -> list[TestOrnegi]:
    return [
        TestOrnegi(id="r001", metin="Rüyamda bir yılan gördüm."),
        TestOrnegi(id="r002", metin="Rüyamda su gördüm."),
    ]


def _bag(hibrit: object = object()) -> SimpleNamespace:
    return SimpleNamespace(istemci=object(), depo=object(), hibrit=hibrit, varyantlar={})


def test_deney_kos_her_cesit_icin_satir_yazar(tmp_path: Path, monkeypatch):
    import ruya.degerlendirme.getirme_deneyi as modul

    cagrilar: dict[str, list] = {"extract": [], "map": [], "siralama": []}

    def sahte_extract(girdi, istemci):
        cagrilar["extract"].append(girdi)
        return CikarimSonucu(semboller=[_sembol("yılan")]), Kullanim(model="test")

    def sahte_map(semboller, varyantlar):
        cagrilar["map"].append((semboller, varyantlar))
        return [_eslesme(sembol.yalin) for sembol in semboller]

    def sahte_siralama(eslesmeler, depo, indeks, istemci, **kwargs):
        cagrilar["siralama"].append((eslesmeler, kwargs))
        return {getirme_anahtari(e): [("a:1", 0.9), ("a:2", 0.8)] for e in eslesmeler}

    monkeypatch.setattr(modul.extract, "extract", sahte_extract)
    monkeypatch.setattr(modul.esleme, "map_symbols", sahte_map)
    monkeypatch.setattr(modul.hibrit, "siralama", sahte_siralama)

    cikti = tmp_path / "deney" / "siralamalar.jsonl"
    sonuc = deney_kos(_ornekler(), _bag(), cikti)

    assert sonuc == cikti
    assert cikti.exists()
    assert len(cagrilar["extract"]) == 2
    assert [g.metin for g in cagrilar["extract"]] == [
        "Rüyamda bir yılan gördüm.",
        "Rüyamda su gördüm.",
    ]

    satirlar = satirlari_oku(cikti)
    assert len(satirlar) == 8  # 2 rüya × 4 çeşit × 1 anahtar
    assert {s["cesit"] for s in satirlar} == {"G0", "G1", "G2", "G3"}
    assert {s["ornek_id"] for s in satirlar} == {"r001", "r002"}
    for satir in satirlar:
        assert satir["anahtar"] == "yilan"
        assert satir["sembol"] == "yılan"
        assert satir["sirali"] == [["a:1", 0.9], ["a:2", 0.8]]

    # Her çeşit kendi kolları ve rerank ayarıyla çağrılır.
    assert len(cagrilar["siralama"]) == 8
    for _eslesmeler, kwargs in cagrilar["siralama"]:
        assert kwargs["gelenekler"] is None
        assert kwargs["k"] == 10
        assert (frozenset(kwargs["kollar"]), kwargs["rerank"]) in set(CESITLER.values())


def test_deney_kos_ozel_cesit_ve_k(tmp_path: Path, monkeypatch):
    import ruya.degerlendirme.getirme_deneyi as modul

    kayitlar: list[dict] = []

    monkeypatch.setattr(
        modul.extract,
        "extract",
        lambda girdi, istemci: (
            CikarimSonucu(semboller=[_sembol("yılan")]),
            Kullanim(model="test"),
        ),
    )
    monkeypatch.setattr(
        modul.esleme,
        "map_symbols",
        lambda semboller, varyantlar: [_eslesme(s.yalin) for s in semboller],
    )

    def sahte_siralama(eslesmeler, depo, indeks, istemci, **kwargs):
        kayitlar.append(kwargs)
        return {getirme_anahtari(e): [("a:1", 0.9)] for e in eslesmeler}

    monkeypatch.setattr(modul.hibrit, "siralama", sahte_siralama)

    cikti = tmp_path / "s.jsonl"
    deney_kos(_ornekler()[:1], _bag(), cikti, cesitler={"G2": CESITLER["G2"]}, k=3)

    assert len(satirlari_oku(cikti)) == 1
    assert kayitlar == [
        {
            "kollar": frozenset({"sozluk", "bm25"}),
            "rerank": True,
            "gelenekler": None,
            "k": 3,
        }
    ]


def test_deney_kos_hatayi_satir_olarak_yazar_ve_devam_eder(tmp_path: Path, monkeypatch):
    import ruya.degerlendirme.getirme_deneyi as modul

    def sahte_extract(girdi, istemci):
        if "su" in girdi.metin:
            raise LLMHatasi("geçit hatası")
        return CikarimSonucu(semboller=[_sembol("yılan")]), Kullanim(model="test")

    monkeypatch.setattr(modul.extract, "extract", sahte_extract)
    monkeypatch.setattr(
        modul.esleme,
        "map_symbols",
        lambda semboller, varyantlar: [_eslesme(s.yalin) for s in semboller],
    )
    monkeypatch.setattr(
        modul.hibrit,
        "siralama",
        lambda eslesmeler, depo, indeks, istemci, **kwargs: {
            getirme_anahtari(e): [("a:1", 0.9)] for e in eslesmeler
        },
    )

    cikti = tmp_path / "s.jsonl"
    deney_kos(_ornekler(), _bag(), cikti)

    ham = [json.loads(satir) for satir in cikti.read_text(encoding="utf-8").splitlines()]
    hatalar = [s for s in ham if "hata" in s]
    assert hatalar == [{"ornek_id": "r002", "hata": "LLMHatasi: geçit hatası"}]
    assert len(satirlari_oku(cikti)) == 4  # yalnızca r001'in dört çeşidi


def test_deney_kos_hibrit_yoksa_value_error(tmp_path: Path, monkeypatch):
    import ruya.degerlendirme.getirme_deneyi as modul

    cagrildi = False

    def sahte_extract(girdi, istemci):
        nonlocal cagrildi
        cagrildi = True
        return CikarimSonucu(semboller=[]), Kullanim(model="test")

    monkeypatch.setattr(modul.extract, "extract", sahte_extract)

    with pytest.raises(ValueError):
        deney_kos(_ornekler(), _bag(hibrit=None), tmp_path / "s.jsonl")
    assert cagrildi is False


# --- satirlari_oku ----------------------------------------------------------


def test_satirlari_oku_hata_satirlarini_atlar(tmp_path: Path):
    yol = tmp_path / "s.jsonl"
    iyi = _satir("r001", "G0", "yilan", "yılan", [["a:1", 0.9]])
    yol.write_text(
        "\n".join(
            [
                json.dumps(iyi, ensure_ascii=False),
                json.dumps({"ornek_id": "r002", "hata": "LLMHatasi: x"}, ensure_ascii=False),
                json.dumps(_satir("r003", "G1", "su", "su", [["b:1", 0.5]]), ensure_ascii=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    satirlar = satirlari_oku(yol)
    assert [s["ornek_id"] for s in satirlar] == ["r001", "r003"]
    assert satirlar[0] == iyi


def test_satirlari_oku_bos_satirlari_atlar(tmp_path: Path):
    yol = tmp_path / "s.jsonl"
    yol.write_text(
        json.dumps(_satir("r001", "G0", "yilan", "yılan", []), ensure_ascii=False) + "\n\n",
        encoding="utf-8",
    )
    assert len(satirlari_oku(yol)) == 1


# --- Girdi ------------------------------------------------------------------


def test_deney_kos_ornek_metnini_girdiye_tasir(tmp_path: Path, monkeypatch):
    import ruya.degerlendirme.getirme_deneyi as modul

    gorulen: list[RuyaGirdisi] = []

    def sahte_extract(girdi, istemci):
        gorulen.append(girdi)
        return CikarimSonucu(semboller=[]), Kullanim(model="test")

    monkeypatch.setattr(modul.extract, "extract", sahte_extract)
    monkeypatch.setattr(modul.esleme, "map_symbols", lambda semboller, varyantlar: [])
    monkeypatch.setattr(
        modul.hibrit,
        "siralama",
        lambda eslesmeler, depo, indeks, istemci, **kwargs: {},
    )

    deney_kos(_ornekler()[:1], _bag(), tmp_path / "s.jsonl")

    assert [g.metin for g in gorulen] == ["Rüyamda bir yılan gördüm."]
