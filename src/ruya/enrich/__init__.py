"""Çevrimdışı zenginleştirme: interim → processed/entries.jsonl (LLM).

Her zenginleştirici iki adımlıdır; arada süreç kesilebilir:

1. ``istekler(...)`` → {custom_id: istek}; ``LLMIstemcisi.toplu`` ile gönderilir (yanıtlar
   disk önbelleğine yazıldığı için kesilen iş kaldığı yerden devam eder).
2. ``sonuclari_uygula(maddeler, yanitlar)`` → güncellenmiş ``Madde`` listesi.

custom_id her zaman ``entry_id``'dir (":" yerine "__"), böylece sonuçlar sırasız gelse de eşlenir.
"""
