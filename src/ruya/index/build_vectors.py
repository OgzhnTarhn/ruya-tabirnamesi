"""Chroma vektör indeksi (Aşama 2, TK-05, TK-06). Takvim: Hafta 6.

- Chroma Drive üzerinde çalıştırılmaz: ``Ayarlar.chroma_klasoru`` (/content/calisma/chroma)
  altında kurulur, ``yedek.py`` ile Drive'a zip olarak yedeklenir.
- e5 modelleri ``query: `` ve ``passage: `` önekleri ister; unutulursa kalite sessizce düşer.
- chromadb ve sentence-transformers ağır paketlerdir ve bilgisayarda kurulu değildir:
  içe aktarma yalnızca işlevlerin içinde yapılır.
"""

from __future__ import annotations

from ruya.config import Ayarlar
from ruya.schemas import Madde, SymbolKaydi

EMBEDDING_MODELI = "intfloat/multilingual-e5-large"  # D1 adayı: Qwen/Qwen3-Embedding-0.6B


def vektor_indeksi_kur(
    maddeler: list[Madde], sozluk: dict[str, SymbolKaydi], ayar: Ayarlar
) -> None:
    """İki koleksiyon kurar: ``semboller`` (ad + varyantlar, eşleme yedeği için) ve
    ``maddeler`` (metin_tr + metin_asli, symbol_id metadatasıyla)."""
    raise NotImplementedError("Hafta 6: index/build_vectors.py (docs/08)")


class ChromaVektorArayici:
    """store.VektorArayici arayüzünün Chroma ile gerçeklemesi."""

    def __init__(self, ayar: Ayarlar) -> None:
        raise NotImplementedError("Hafta 6: index/build_vectors.py (docs/08)")

    def en_yakin_semboller(self, ifade: str, k: int = 3) -> list[tuple[str, float]]:
        raise NotImplementedError
