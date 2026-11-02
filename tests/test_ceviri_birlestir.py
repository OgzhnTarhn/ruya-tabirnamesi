"""Çeviri parçalarını maddelere işleme testleri (enrich/ceviri_birlestir.py).

Parça dosyaları ``data/interim/ceviri/<kaynak>/parca_NNNN.jsonl`` biçimindedir; her satır
``entry_id``, ``sembol_ar``, ``sembol_tr`` ve ``metin_tr`` alanlarını taşır.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest

from ruya.enrich.ceviri_birlestir import ceviri_oku, ceviriyi_uygula
from ruya.schemas import Madde

TARIH = dt.date(2026, 11, 2)
MODEL = "claude-code+evren"


def _madde(entry_id: str, metin_asli: str = "(asıl metin)") -> Madde:
    kaynak = entry_id.split(":", 1)[0]
    return Madde.model_validate(
        {
            "entry_id": entry_id,
            "kaynak": kaynak,
            "eser": "Örnek eser",
            "yazar": "Örnek yazar",
            "gelenek": "islami_klasik",
            "dil": "ar",
            "lisans": "CC-BY-NC-SA-4.0",
            "konum": {"satir": 1},
            "metin_asli": metin_asli,
        }
    )


def _parca_yaz(klasor, ad: str, kayitlar: list[dict], bos_satir: bool = False) -> None:
    satirlar = []
    for kayit in kayitlar:
        satirlar.append(json.dumps(kayit, ensure_ascii=False))
        if bos_satir:
            satirlar.append("")
    (klasor / ad).write_text("\n".join(satirlar) + "\n", encoding="utf-8")


# --- ceviri_oku -------------------------------------------------------------


def test_ceviri_oku_butun_parcalari_entry_id_ile_birler(tmp_path):
    _parca_yaz(
        tmp_path,
        "parca_0001.jsonl",
        [
            {
                "entry_id": "nablusi:004310",
                "sembol_ar": "حية",
                "sembol_tr": "yılan",
                "metin_tr": "Yılan görmek…",
            },
            {
                "entry_id": "nablusi:004314",
                "sembol_ar": None,
                "sembol_tr": None,
                "metin_tr": "Alt paragraf çevirisi.",
            },
        ],
    )
    _parca_yaz(
        tmp_path,
        "parca_0002.jsonl",
        [
            {
                "entry_id": "miller:018710",
                "sembol_ar": "Snakes",
                "sembol_tr": "yılanlar",
                "metin_tr": "Yılanlar…",
            },
        ],
    )

    ceviriler = ceviri_oku(tmp_path)

    assert set(ceviriler) == {"nablusi:004310", "nablusi:004314", "miller:018710"}
    assert ceviriler["nablusi:004310"]["metin_tr"] == "Yılan görmek…"
    assert ceviriler["nablusi:004310"]["sembol_ar"] == "حية"
    assert ceviriler["miller:018710"]["sembol_tr"] == "yılanlar"


def test_ceviri_oku_bos_satirlari_atlar(tmp_path):
    _parca_yaz(
        tmp_path,
        "parca_0001.jsonl",
        [{"entry_id": "nablusi:004310", "metin_tr": "çeviri"}],
        bos_satir=True,
    )
    # Baştaki ve sondaki boş satırlar da sorun çıkarmamalı.
    yol = tmp_path / "parca_0001.jsonl"
    yol.write_text("\n\n" + yol.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")

    ceviriler = ceviri_oku(tmp_path)

    assert list(ceviriler) == ["nablusi:004310"]


def test_ceviri_oku_parca_olmayan_dosyalari_yok_sayar(tmp_path):
    _parca_yaz(tmp_path, "parca_0001.jsonl", [{"entry_id": "nablusi:004310", "metin_tr": "a"}])
    (tmp_path / "notlar.jsonl").write_text(
        json.dumps({"entry_id": "nablusi:999999", "metin_tr": "olmamalı"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "parca_0001.json").write_text("{}", encoding="utf-8")

    ceviriler = ceviri_oku(tmp_path)

    assert list(ceviriler) == ["nablusi:004310"]


def test_ceviri_oku_bos_klasorde_bos_sozluk(tmp_path):
    assert ceviri_oku(tmp_path) == {}


# --- ceviriyi_uygula --------------------------------------------------------


def test_ceviriyi_uygula_alanlari_doldurur():
    maddeler = [_madde("nablusi:004310", "(asıl metin)")]
    ceviriler = {
        "nablusi:004310": {
            "entry_id": "nablusi:004310",
            "sembol_ar": "حية",
            "sembol_tr": "yılan",
            "metin_tr": "Yılan görmek…",
        }
    }

    sonuc = ceviriyi_uygula(maddeler, ceviriler, model=MODEL, tarih=TARIH)

    assert len(sonuc) == 1
    madde = sonuc[0]
    assert madde.metin_tr == "Yılan görmek…"
    assert madde.sembol_ar == "حية"
    assert madde.sembol_tr == "yılan"
    assert madde.metin_asli == "(asıl metin)"
    assert madde.ceviri is not None
    assert madde.ceviri.yontem == "llm"
    assert madde.ceviri.model == MODEL
    assert madde.ceviri.tarih == TARIH
    assert madde.ceviri.gozden_gecirildi is False


def test_ceviriyi_uygula_eksik_anahtarlar_none_olur():
    maddeler = [_madde("nablusi:004310")]
    ceviriler = {"nablusi:004310": {"entry_id": "nablusi:004310", "metin_tr": "sadece metin"}}

    madde = ceviriyi_uygula(maddeler, ceviriler, model=MODEL, tarih=TARIH)[0]

    assert madde.metin_tr == "sadece metin"
    assert madde.sembol_ar is None
    assert madde.sembol_tr is None


def test_ceviriyi_uygula_girdiyi_degistirmez():
    maddeler = [_madde("nablusi:004310")]
    ceviriler = {
        "nablusi:004310": {"entry_id": "nablusi:004310", "metin_tr": "çeviri", "sembol_tr": "yılan"}
    }

    sonuc = ceviriyi_uygula(maddeler, ceviriler, model=MODEL, tarih=TARIH)

    assert sonuc[0] is not maddeler[0]
    assert maddeler[0].metin_tr is None
    assert maddeler[0].ceviri is None
    assert sonuc[0].metin_tr == "çeviri"


def test_ceviriyi_uygula_sirayi_korur():
    maddeler = [
        _madde("miller:018710", "(sample text)"),
        _madde("nablusi:004310", "(asıl metin)"),
        _madde("nablusi:004314", "(alt paragraf)"),
    ]
    ceviriler = {
        "nablusi:004314": {"entry_id": "nablusi:004314", "metin_tr": "üçüncü"},
        "miller:018710": {"entry_id": "miller:018710", "metin_tr": "birinci"},
        "nablusi:004310": {"entry_id": "nablusi:004310", "metin_tr": "ikinci"},
    }

    sonuc = ceviriyi_uygula(maddeler, ceviriler, model=MODEL, tarih=TARIH)

    assert [m.entry_id for m in sonuc] == [
        "miller:018710",
        "nablusi:004310",
        "nablusi:004314",
    ]
    assert [m.metin_tr for m in sonuc] == ["birinci", "ikinci", "üçüncü"]
    assert [m.metin_asli for m in sonuc] == ["(sample text)", "(asıl metin)", "(alt paragraf)"]


def test_ceviriyi_uygula_cevirisi_olmayan_maddeyi_adiyla_bildirir():
    maddeler = [_madde("nablusi:004310"), _madde("miller:018710")]
    ceviriler = {"nablusi:004310": {"entry_id": "nablusi:004310", "metin_tr": "çeviri"}}

    with pytest.raises(ValueError, match="miller:018710"):
        ceviriyi_uygula(maddeler, ceviriler, model=MODEL, tarih=TARIH)


def test_ceviriyi_uygula_maddesi_olmayan_ceviriyi_adiyla_bildirir():
    maddeler = [_madde("nablusi:004310")]
    ceviriler = {
        "nablusi:004310": {"entry_id": "nablusi:004310", "metin_tr": "çeviri"},
        "nablusi:999999": {"entry_id": "nablusi:999999", "metin_tr": "fazlalık"},
    }

    with pytest.raises(ValueError, match="nablusi:999999"):
        ceviriyi_uygula(maddeler, ceviriler, model=MODEL, tarih=TARIH)


def test_ceviriyi_uygula_bos_listeler():
    assert ceviriyi_uygula([], {}, model=MODEL, tarih=TARIH) == []
