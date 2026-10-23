"""Projeye özgü hata sınıfları.

Arayüz bu sınıfları yakalayıp kullanıcıya anlaşılır bir mesaj gösterir
(bkz. docs/03-mimari.md, bölüm 5.4).
"""


class RuyaHatasi(Exception):
    """Projedeki bütün özel hataların atası."""


class VeriYoluYok(RuyaHatasi):
    """Veri isteyen bir işlev, veri klasörü tanımlı değilken çağrıldı.

    Bilgisayarda veri yoktur; bu hata orada beklenen davranıştır.
    """


class ApiAnahtariYok(RuyaHatasi):
    """ANTHROPIC_API_KEY ortam değişkeni tanımlı değil."""


class ModelReddetti(RuyaHatasi):
    """Model isteği reddetti (stop_reason == "refusal")."""


class YanitKesildi(RuyaHatasi):
    """Yanıt max_tokens sınırında kesildi (stop_reason == "max_tokens")."""


class SozlukHatasi(RuyaHatasi):
    """sozluk/symbols.json okunamadı ya da şemaya uymuyor."""
