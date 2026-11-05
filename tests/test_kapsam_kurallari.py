"""Kural tabanlı kapsam çıkarımı testleri (docs/05, Katman 3)."""

import pytest

from ruya.enrich.kapsam_kurallari import kapsami_cikar, maddelere_uygula
from ruya.schemas import Madde


@pytest.mark.parametrize(
    "metin",
    [
        "Hükümdar ise bu onun düşmanıdır.",
        "Gören hükümdar ise beldeleri fetheder.",
        "Eğer sultan ise düşmanlarından mal elde eder.",
        "Sultan için yüzük mülküne işaret eder.",
        "Satranç sevince delalet eder; hükümdar için büyük bir beldedir.",
        "Bunu bir hükümdar görürse bir hükümdarı yener.",
        "Onu sultan görürse saltanatı artar.",
    ],
)
def test_padisah(metin: str):
    assert kapsami_cikar(metin) == "padisah"


@pytest.mark.parametrize(
    "metin",
    [
        "O yerin halkı zalim ise onlardan intikam alınır.",
        "Bu, o yerin halkına isabet eden musibetlerdir.",
        "O şehrin halkı arasında düşmanlık ortaya çıkar.",
        "Riyaset elde eder ve o belde halkına hâkim olur.",
        "Bir beldenin ahalisinden hicrete işaret eder.",
        "Köy halkı için bereket demektir.",
    ],
)
def test_vilayet(metin: str):
    assert kapsami_cikar(metin) == "vilayet"


@pytest.mark.parametrize(
    "metin",
    [
        # Rüyada görülen kişi rüya sahibinin kapsamı değildir.
        "Bir hükümdarın kendisini dövdüğünü görürse elbise giydirilir.",
        "Sultanın deve kuşu olduğunu görmesi hizmetkâra işarettir.",
        "Kim bir hükümdar görürse izzet bulur.",
        "Bir sultan görürse sevinir.",
        "Rüyada padişah görmek şereftir.",
        "Hasta değilse ve sultan için öşür borcu varsa öder.",
        "Amiri bir sultan ise zâlimdir.",
        # Ev halkı, halk sözcüğünün yalın kullanımı toplum kapsamı değildir.
        "Ev halkına efendi olacak bir oğul doğar.",
        "Küçük çekirgeler, halkın avamıdır.",
        "Yılan düşmana işaret eder.",
        "",
        "   ",
        None,
    ],
)
def test_kapsam_yok(metin: str | None):
    assert kapsami_cikar(metin) is None


def test_ikisi_birden_varsa_padisah_oncelikli():
    metin = "O yerin halkı sevinir. Hükümdar ise beldeleri fetheder."

    assert kapsami_cikar(metin) == "padisah"


def _madde(metin_tr: str | None) -> Madde:
    return Madde(
        entry_id="nablusi:000001",
        kaynak="nablusi",
        eser="Test Eseri",
        yazar="Test Yazarı",
        gelenek="islami_klasik",
        dil="tr",
        lisans="PD",
        konum={"satir": 1},
        metin_asli="x",
        metin_tr=metin_tr,
    )


def test_maddelere_uygula_yalniz_kapsam_yazar():
    maddeler = [_madde("Hükümdar ise fetheder."), _madde("Yılan düşmandır."), _madde(None)]

    sonuc = maddelere_uygula(maddeler)

    assert [m.kapsam for m in sonuc] == ["padisah", None, None]
    assert sonuc[0].model_copy(update={"kapsam": None}) == maddeler[0]
    assert maddeler[0].kapsam is None
