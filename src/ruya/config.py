"""Ortam algılama, yollar ve model adları.

- Colab'de veri Drive'dan okunur; bilgisayarda veri yolu yoktur (docs/11).
- Claude model adları ve fiyatları **yalnızca bu dosyada** tanımlanır (CLAUDE.md).
- Ayarlar ``RUYA_`` önekli ortam değişkenlerinden okunur. ``.env`` dosyası
  kullanılmaz; gizli bilgiler yalnızca Colab Secrets'ta durur.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ruya.hatalar import VeriYoluYok

# --- Repodaki yollar (git'te duran dosyalar) --------------------------------
# Paket her zaman düzenlenebilir kipte (pip install -e) kurulur, bu yüzden
# __file__ repodaki kaynak dosyayı gösterir.
REPO_KOKU = Path(__file__).resolve().parents[2]
SOZLUK_DOSYASI = REPO_KOKU / "sozluk" / "symbols.json"
TALIMAT_KLASORU = REPO_KOKU / "prompts"
TEST_SETI_KLASORU = REPO_KOKU / "eval" / "dataset"

# --- Colab varsayılanları ---------------------------------------------------
COLAB_VERI_KLASORU = Path("/content/drive/MyDrive/ruya-tabirnamesi")
COLAB_CALISMA_KLASORU = Path("/content/calisma")

# --- Modeller (TK-04) -------------------------------------------------------
MODEL_CIKARIM = "claude-opus-5-5"
MODEL_SENTEZ = "claude-opus-5-5"
MODEL_CEVIRI = "claude-opus-5-5"
MODEL_SEMBOL_ATAMA = "claude-opus-5-5"
MODEL_KOSUL = "claude-opus-5-5"

# Opus 5.5'te düşünme kapatılamaz; derinlik ve maliyet effort ile ayarlanır.
# Opus 5.5'in varsayılanı "medium" olduğu için her iş için açıkça yazılır.
EFFORT_CIKARIM = "low"
EFFORT_SENTEZ = "medium"
EFFORT_CEVIRI = "medium"
EFFORT_SEMBOL_ATAMA = "low"
EFFORT_KOSUL = "low"


@dataclass(frozen=True)
class Fiyat:
    """Milyon token başına dolar."""

    girdi: float
    cikti: float
    onbellek_okuma: float | None = None  # None: girdi fiyatıyla hesaplanır (temkinli)


# 23 Ekim 2026 itibarıyla birinci taraf API fiyatları. Değişirse yalnızca burası güncellenir.
# Haiku 5.5 fiyatı 100 bin token altındaki istemler için geçerlidir.
FIYATLAR: dict[str, Fiyat] = {
    "claude-opus-5-5": Fiyat(girdi=4.00, cikti=20.00, onbellek_okuma=0.20),
    "claude-sonnet-5-5": Fiyat(girdi=2.00, cikti=10.00, onbellek_okuma=0.20),
    "claude-haiku-5-5": Fiyat(girdi=0.10, cikti=0.50),
}
BATCH_INDIRIMI = 0.5  # Message Batches API toplu işlerde %50 indirimli


def colabda_mi() -> bool:
    """Kod Google Colab'de mi çalışıyor?"""
    return "google.colab" in sys.modules


class Ayarlar(BaseSettings):
    """Çalışma zamanı ayarları. Ortam değişkenleri: RUYA_DATA_DIR, RUYA_WORK_DIR, …"""

    model_config = SettingsConfigDict(env_prefix="RUYA_", extra="ignore")

    data_dir: Path | None = None
    work_dir: Path | None = None
    llm_cache: bool = True  # RUYA_LLM_CACHE=off ile kapatılır
    sorgu_onbellegi: bool = False  # RUYA_SORGU_ONBELLEGI=on: rüyalar da önbelleğe (docs/03, 5.2)
    gecmis: bool = False  # RUYA_GECMIS=on ise rüyalar Drive'da gecmis/ altında saklanır
    kaynak_basina_n: int = 2  # İG-22
    en_fazla_sembol: int = 8  # docs/03, bölüm 5.4

    @model_validator(mode="after")
    def _colab_varsayilanlari(self) -> Ayarlar:
        if colabda_mi():
            if self.data_dir is None:
                self.data_dir = COLAB_VERI_KLASORU
            if self.work_dir is None:
                self.work_dir = COLAB_CALISMA_KLASORU
        return self

    # --- Drive: kalıcı veri (docs/11, bölüm 3) ------------------------------

    def veri(self, *parcalar: str) -> Path:
        """Drive'daki proje klasörünün altındaki bir yol."""
        if self.data_dir is None:
            raise VeriYoluYok(
                "Veri klasörü tanımlı değil. Veri yalnızca Colab'de, Drive üzerinden okunur "
                "(bkz. docs/11-calisma-ortami-colab-drive.md). Bilgisayarda yalnızca verisiz "
                "testler çalışır; gerekiyorsa RUYA_DATA_DIR ortam değişkenini ayarla."
            )
        return self.data_dir.joinpath(*parcalar)

    @property
    def ham_klasoru(self) -> Path:
        return self.veri("data", "raw")

    @property
    def ara_klasoru(self) -> Path:
        return self.veri("data", "interim")

    @property
    def islenmis_klasoru(self) -> Path:
        return self.veri("data", "processed")

    @property
    def maddeler_dosyasi(self) -> Path:
        return self.islenmis_klasoru / "entries.jsonl"

    @property
    def indeks_yedek_klasoru(self) -> Path:
        return self.veri("data", "index")

    @property
    def llm_onbellek_klasoru(self) -> Path:
        return self.veri("cache", "llm")

    @property
    def batch_klasoru(self) -> Path:
        return self.veri("cache", "batch")

    @property
    def rapor_klasoru(self) -> Path:
        return self.veri("raporlar")

    @property
    def gecmis_klasoru(self) -> Path:
        return self.veri("gecmis")

    @property
    def log_klasoru(self) -> Path:
        return self.veri("logs")

    # --- Colab yerel diski: geçici ve hızlı (Chroma, modeller) --------------

    def calisma(self, *parcalar: str) -> Path:
        """Colab'in yerel diskindeki çalışma klasörünün altındaki bir yol."""
        if self.work_dir is None:
            raise VeriYoluYok("Çalışma klasörü tanımlı değil (RUYA_WORK_DIR).")
        return self.work_dir.joinpath(*parcalar)

    @property
    def chroma_klasoru(self) -> Path:
        return self.calisma("chroma")

    @property
    def hf_klasoru(self) -> Path:
        return self.calisma("hf")


@lru_cache(maxsize=1)
def ayarlar() -> Ayarlar:
    """Süreç boyunca tek bir Ayarlar nesnesi döndürür."""
    return Ayarlar()
