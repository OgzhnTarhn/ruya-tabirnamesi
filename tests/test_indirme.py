"""scripts/download_sources.py indirme akışının ağsız testleri.

Betik paket değildir; modül olarak yüklenir. Ağ yerine sahte bir ``urlopen`` kullanılır,
bekleme süresi sıfırlanır. Veri gerektirmez; bilgisayarda da çalışır.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from ruya.ingest.kaynaklar import KaynakBilgisi

BETIK = Path(__file__).resolve().parents[1] / "scripts" / "download_sources.py"


@pytest.fixture(scope="module")
def indirme():
    """Betiği paket olmadan modül olarak yükler."""
    spec = importlib.util.spec_from_file_location("download_sources", BETIK)
    assert spec is not None and spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


class SahteYanit:
    """``with urlopen(...) as yanit`` bağlamında kullanılan sahte yanıt."""

    def __init__(self, icerik: bytes) -> None:
        self._icerik = icerik

    def __enter__(self) -> SahteYanit:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._icerik


def sahte_urlopen(indirme, monkeypatch, icerikler: dict[str, bytes | OSError]) -> list[str]:
    """URL'ye göre bayt döndüren (ya da OSError yükselten) sahte urlopen kurar.

    Çağrılan URL'leri sırayla döndürür; testler ağa çıkmadığını bununla doğrular.
    """
    cagrilar: list[str] = []

    def urlopen(istek, timeout=None):
        url = istek.full_url if hasattr(istek, "full_url") else str(istek)
        cagrilar.append(url)
        sonuc = icerikler[url]
        if isinstance(sonuc, OSError):
            raise sonuc
        return SahteYanit(sonuc)

    monkeypatch.setattr(indirme.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(indirme.time, "sleep", lambda _sn: None)
    return cagrilar


def kaynak(kaynak_adi: str, url: str, sha256: str | None = None) -> KaynakBilgisi:
    """Testler için doğrudan kurulan kaynak künyesi."""
    return KaynakBilgisi(
        kaynak=kaynak_adi,
        eser="Deneme eseri",
        yazar="Deneme yazarı",
        gelenek="bati_halk",
        dil="en",
        lisans="PD",
        url=url,
        asama=0,
        sha256=sha256,
    )


def test_sha256_uyusmazsa_hata_verir_ve_dosya_yazmaz(indirme, monkeypatch, tmp_path):
    icerik = b"gercek icerik"
    bilgi = kaynak("deneme", "https://ornek.test/deneme.txt", sha256="0" * 64)
    sahte_urlopen(indirme, monkeypatch, {bilgi.url: icerik})

    with pytest.raises(ValueError, match="SHA256"):
        indirme.indir(bilgi, tmp_path)

    assert not (tmp_path / bilgi.ham_dosya_adi).exists()


def test_sha256_uyusursa_dosya_yazilir(indirme, monkeypatch, tmp_path):
    icerik = b"gercek icerik"
    ozet = hashlib.sha256(icerik).hexdigest()
    bilgi = kaynak("deneme", "https://ornek.test/deneme.txt", sha256=ozet)
    sahte_urlopen(indirme, monkeypatch, {bilgi.url: icerik})

    sonuc = indirme.indir(bilgi, tmp_path)

    assert (tmp_path / bilgi.ham_dosya_adi).read_bytes() == icerik
    assert sonuc["sha256"] == ozet


def test_sha256_yoksa_dosya_yazilir(indirme, monkeypatch, tmp_path):
    icerik = b"ozetsiz icerik"
    bilgi = kaynak("deneme", "https://ornek.test/deneme.txt")
    sahte_urlopen(indirme, monkeypatch, {bilgi.url: icerik})

    sonuc = indirme.indir(bilgi, tmp_path)

    assert (tmp_path / bilgi.ham_dosya_adi).read_bytes() == icerik
    assert sonuc["sha256"] == hashlib.sha256(icerik).hexdigest()


def test_kaynaklari_indir_ozet_yolunu_dondurur(indirme, monkeypatch, tmp_path):
    icerik = b"birinci icerik"
    bilgi = kaynak("birinci", "https://ornek.test/birinci.txt")
    sahte_urlopen(indirme, monkeypatch, {bilgi.url: icerik})

    yol = indirme.kaynaklari_indir([bilgi], tmp_path)

    assert yol == tmp_path / "KAYNAK_OZETLERI.json"
    ozetler = json.loads(yol.read_text(encoding="utf-8"))
    assert ozetler["birinci"]["sha256"] == hashlib.sha256(icerik).hexdigest()


def test_kaynaklari_indir_hatada_ozeti_korur(indirme, monkeypatch, tmp_path):
    birinci = kaynak("birinci", "https://ornek.test/birinci.txt")
    ikinci = kaynak("ikinci", "https://ornek.test/ikinci.txt")
    icerik = b"birinci icerik"
    sahte_urlopen(
        indirme,
        monkeypatch,
        {birinci.url: icerik, ikinci.url: OSError("bağlantı koptu")},
    )

    with pytest.raises(OSError):
        indirme.kaynaklari_indir([birinci, ikinci], tmp_path)

    ozet_yolu = tmp_path / "KAYNAK_OZETLERI.json"
    assert ozet_yolu.exists()
    ozetler = json.loads(ozet_yolu.read_text(encoding="utf-8"))
    assert ozetler["birinci"]["sha256"] == hashlib.sha256(icerik).hexdigest()
    assert "ikinci" not in ozetler


def test_var_olan_dosya_atlanir(indirme, monkeypatch, tmp_path):
    bilgi = kaynak("deneme", "https://ornek.test/deneme.txt")
    (tmp_path / bilgi.ham_dosya_adi).write_bytes(b"eski icerik")
    cagrilar = sahte_urlopen(indirme, monkeypatch, {bilgi.url: b"yeni icerik"})

    indirme.kaynaklari_indir([bilgi], tmp_path)

    assert cagrilar == []
    assert (tmp_path / bilgi.ham_dosya_adi).read_bytes() == b"eski icerik"


def test_yeniden_istendiginde_dosya_indirilir(indirme, monkeypatch, tmp_path):
    bilgi = kaynak("deneme", "https://ornek.test/deneme.txt")
    (tmp_path / bilgi.ham_dosya_adi).write_bytes(b"eski icerik")
    cagrilar = sahte_urlopen(indirme, monkeypatch, {bilgi.url: b"yeni icerik"})

    indirme.kaynaklari_indir([bilgi], tmp_path, yeniden=True)

    assert cagrilar == [bilgi.url]
    assert (tmp_path / bilgi.ham_dosya_adi).read_bytes() == b"yeni icerik"
