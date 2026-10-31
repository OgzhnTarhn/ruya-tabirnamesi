"""Projeye özgü hata sınıfları.

Arayüz bu sınıfları yakalayıp kullanıcıya anlaşılır bir mesaj gösterir
(bkz. docs/03-mimari.md, bölüm 5.4).
"""


class RuyaHatasi(Exception):
    """Projedeki bütün özel hataların atası."""


class ApiAnahtariYok(RuyaHatasi):
    """EVREN_LLM_API_KEY ortam değişkeni tanımlı değil."""


class ModelReddetti(RuyaHatasi):
    """Model isteği reddetti (yanıtta ``message.refusal`` dolu)."""


class YanitKesildi(RuyaHatasi):
    """Yanıt max_tokens sınırında kesildi (``finish_reason == "length"``)."""


class LLMHatasi(RuyaHatasi):
    """Geçit hata döndürdü ve yeniden denemeler tükendi ya da hata tekrarlanamaz."""

    def __init__(self, mesaj: str, durum: int | None = None) -> None:
        super().__init__(mesaj)
        self.durum = durum


class YanitBozuk(RuyaHatasi):
    """JSON şeması istenen yanıt ayrıştırılamadı."""


class SozlukHatasi(RuyaHatasi):
    """sozluk/symbols.json okunamadı ya da şemaya uymuyor."""
