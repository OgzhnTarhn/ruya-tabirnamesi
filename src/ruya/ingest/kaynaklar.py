"""Korpustaki kaynakların künye ve lisans bilgileri: tek doğru kaynak.

Ayrıştırıcılar ``Madde`` alanlarını (eser, yazar, gelenek, dil, lisans, atif_notu) buradan
doldurur; indirme betiği URL'leri buradan okur. Tam künyeler ve atıf metinleri:
docs/KAYNAKLAR.md. Yeni kaynak eklemeden önce docs/07 (V1–V9) okunur.

Lisans kodları: ``PD`` (kamu malı), ``CC-BY-NC-SA-4.0``, ``CC-BY-NC-4.0``, ``CC-BY-SA-4.0``.
"""

from __future__ import annotations

from dataclasses import dataclass

from ruya.schemas import Dil, Gelenek

OPENITI_ATIF_NOTU = "Nispeti sahih değil (OpenITI metadatası)"


@dataclass(frozen=True)
class KaynakBilgisi:
    kaynak: str  # entry_id öneki ve dosya adı: nablusi → data/raw/nablusi.txt
    eser: str
    yazar: str
    gelenek: Gelenek
    dil: Dil
    lisans: str
    url: str
    asama: int  # docs/02: hangi aşamada korpusa giriyor
    atif_notu: str | None = None

    @property
    def ham_dosya_adi(self) -> str:
        return f"{self.kaynak}.txt"


KAYNAKLAR: dict[str, KaynakBilgisi] = {
    k.kaynak: k
    for k in (
        KaynakBilgisi(
            kaynak="nablusi",
            eser="Ta'tîrü'l-enâm fî ta'bîri'l-menâm",
            yazar="Abdülganî en-Nablusî",
            gelenek="islami_klasik",
            dil="ar",
            lisans="CC-BY-NC-SA-4.0",
            url=(
                "https://raw.githubusercontent.com/OpenITI/1150AH/"
                "0412012ee6a24497a10c0ad9711ae450929f5f35/data/"
                "1143CabdGhaniNabulusi/1143CabdGhaniNabulusi.TactirAnam/"
                "1143CabdGhaniNabulusi.TactirAnam.Shamela0001217-ara1"
            ),
            asama=0,
        ),
        KaynakBilgisi(
            kaynak="miller",
            eser="Ten Thousand Dreams Interpreted",
            yazar="Gustavus Hindman Miller",
            gelenek="bati_halk",
            dil="en",
            lisans="PD",
            url="https://www.gutenberg.org/cache/epub/926/pg926.txt",
            asama=0,
        ),
        KaynakBilgisi(
            kaynak="freud",
            eser="The Interpretation of Dreams (çev. A. A. Brill, 1913)",
            yazar="Sigmund Freud",
            gelenek="psikanalitik",
            dil="en",
            lisans="PD",
            url="https://www.gutenberg.org/ebooks/66048.txt.utf-8",
            asama=2,
        ),
        KaynakBilgisi(
            kaynak="ibn_sirin",
            eser="Muntahabü'l-kelâm fî tefsîri'l-ahlâm",
            yazar="İbn Sîrîn'e atfedilen",
            gelenek="islami_klasik",
            dil="ar",
            lisans="CC-BY-NC-SA-4.0",
            url=(
                "https://raw.githubusercontent.com/OpenITI/0125AH/"
                "f53daf7815e24aa7870e11f30c0ab64f17bae6c0/data/"
                "0110IbnSirin/0110IbnSirin.MuntakhabKalamFiTafsirAhlam/"
                "0110IbnSirin.MuntakhabKalamFiTafsirAhlam.Shamela0021615-ara1"
            ),
            asama=3,
            atif_notu=OPENITI_ATIF_NOTU,
        ),
    )
}
