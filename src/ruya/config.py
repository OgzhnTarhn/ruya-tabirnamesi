"""Yollar ve model adları.

- Kod, veri ve çalıştırma aynı bilgisayarda: veri ``<repo>/data`` altında durur ve
  hiçbir zaman git'e eklenmez (lisans ve gizlilik).
- Claude model adları ve fiyatları **yalnızca bu dosyada** tanımlanır (CLAUDE.md).
- Ayarlar ``RUYA_`` önekli ortam değişkenlerinden okunur. ``.env`` dosyası
  kullanılmaz; gizli bilgiler (API anahtarı) yalnızca ortam değişkeni
  olarak durur, hiçbir dosyaya yazılmaz.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Repodaki yollar (git'te duran dosyalar) --------------------------------
# Paket her zaman düzenlenebilir kipte (pip install -e) kurulur, bu yüzden
# __file__ repodaki kaynak dosyayı gösterir.
REPO_KOKU = Path(__file__).resolve().parents[2]
SOZLUK_DOSYASI = REPO_KOKU / "sozluk" / "symbols.json"
TALIMAT_KLASORU = REPO_KOKU / "prompts"
TEST_SETI_KLASORU = REPO_KOKU / "eval" / "dataset"
# data/ git'e eklenmez; lisans ve gizlilik.
VERI_KLASORU = REPO_KOKU / "data"

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


class Ayarlar(BaseSettings):
    """Çalışma zamanı ayarları. Ortam değişkenleri: RUYA_DATA_DIR, …"""

    model_config = SettingsConfigDict(env_prefix="RUYA_", extra="ignore")

    data_dir: Path = VERI_KLASORU
    llm_cache: bool = True  # RUYA_LLM_CACHE=off ile kapatılır
    sorgu_onbellegi: bool = False  # RUYA_SORGU_ONBELLEGI=on: rüyalar da önbelleğe (docs/03, 5.2)
    gecmis: bool = False  # RUYA_GECMIS=on ise rüyalar gecmis/ altında saklanır
    kaynak_basina_n: int = 2  # İG-22
    en_fazla_sembol: int = 8  # docs/03, bölüm 5.4

    # --- Yerel veri: kalıcı (docs/11, bölüm 3) ------------------------------

    def veri(self, *parcalar: str) -> Path:
        """Veri klasörünün altındaki bir yol."""
        return self.data_dir.joinpath(*parcalar)

    @property
    def ham_klasoru(self) -> Path:
        return self.veri("raw")

    @property
    def ara_klasoru(self) -> Path:
        return self.veri("interim")

    @property
    def islenmis_klasoru(self) -> Path:
        return self.veri("processed")

    @property
    def maddeler_dosyasi(self) -> Path:
        return self.islenmis_klasoru / "entries.jsonl"

    @property
    def indeks_klasoru(self) -> Path:
        return self.veri("index")

    @property
    def chroma_klasoru(self) -> Path:
        return self.veri("index", "chroma")

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

    # --- Yerel önbellek: git'te durmayan hızlı dosyalar (modeller) ----------

    @property
    def hf_klasoru(self) -> Path:
        return REPO_KOKU / ".cache" / "hf"


@lru_cache(maxsize=1)
def ayarlar() -> Ayarlar:
    """Süreç boyunca tek bir Ayarlar nesnesi döndürür."""
    return Ayarlar()
