"""Yollar ve model adları.

- Kod, veri ve çalıştırma aynı bilgisayarda: veri ``<repo>/data`` altında durur ve
  hiçbir zaman git'e eklenmez (lisans ve gizlilik).
- LLM model adları, API adresi ve fiyatları **yalnızca bu dosyada** tanımlanır (CLAUDE.md).
- Ayarlar ``RUYA_`` önekli ortam değişkenlerinden okunur. ``.env`` dosyası
  kullanılmaz; gizli bilgiler (API anahtarı) yalnızca ortam değişkeni
  olarak durur, hiçbir dosyaya yazılmaz.
"""

from __future__ import annotations

import datetime as dt
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

# --- LLM: EVREN geçidi (TK-03, TK-04) ---------------------------------------
MODEL_CIKARIM = "deepseek-v4.1-flash"
MODEL_SENTEZ = "deepseek-v4.1-flash"
MODEL_CEVIRI = "deepseek-v4.1-flash"
MODEL_SEMBOL_ATAMA = "deepseek-v4.1-flash"
MODEL_KOSUL = "deepseek-v4.1-flash"

# --- Hibrit getirme: EVREN modelleri ve eşikler (docs/13, bölümler 3-4) ------
MODEL_EMBEDDING = "qwen3-embedding-8b"
MODEL_RERANKER = "qwen3-reranker-8b"
MODEL_OCR = "deepseek-ocr-2"
EMBEDDING_BOYUTU = 1024  # docs/13, bölüm 4: 1.024 boyut
GETIRME_ESIGI = 0.15  # reranker eşiği; altı "bulunamadı" (docs/13, bölüm 3)

# Çeviri parçalarını birleştiren adımın etiketi ve tarihi (CeviriBilgisi.model/tarih).
CEVIRI_MODEL_ETIKETI = "claude-code+evren"
CEVIRI_TARIHI = dt.date(2026, 11, 2)

LLM_ADRESI = "https://evren-llmapi.ssyz.org.tr"
LLM_ANAHTAR_DEGISKENI = "EVREN_LLM_API_KEY"


@dataclass(frozen=True)
class Fiyat:
    """Milyon token başına fiyat (sağlayıcının kredi birimi)."""

    girdi: float
    cikti: float
    onbellek_okuma: float | None = None  # None: girdi fiyatıyla hesaplanır (temkinli)


# EVREN modelleri 1 Aralık 2026'ya kadar ücretsiz; fiyat açıklanınca yalnızca burası güncellenir.
FIYATLAR: dict[str, Fiyat] = {
    "deepseek-v4.1-flash": Fiyat(girdi=0.0, cikti=0.0),
}


class Ayarlar(BaseSettings):
    """Çalışma zamanı ayarları. Ortam değişkenleri: RUYA_DATA_DIR, …"""

    model_config = SettingsConfigDict(env_prefix="RUYA_", extra="ignore")

    data_dir: Path = VERI_KLASORU
    llm_cache: bool = True  # RUYA_LLM_CACHE=off ile kapatılır
    sorgu_onbellegi: bool = False  # RUYA_SORGU_ONBELLEGI=on: rüyalar da önbelleğe (docs/03, 5.2)
    gecmis: bool = False  # RUYA_GECMIS=on ise rüyalar gecmis/ altında saklanır
    kaynak_basina_n: int = 1  # İG-22; N=2 ile sentez 12 dakika sürüyordu
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
