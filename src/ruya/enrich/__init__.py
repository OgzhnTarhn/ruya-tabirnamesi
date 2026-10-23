"""Çevrimdışı zenginleştirme: interim → processed/entries.jsonl (LLM, Batch API).

Her zenginleştirici iki adımlıdır; arada Colab oturumu kapanabilir (docs/11, bölüm 4):

1. ``batch_istekleri(...)`` → {custom_id: istek}; ``LLMIstemcisi.batch_gonder`` ile gönderilir.
2. ``sonuclari_uygula(maddeler, yanitlar)`` → güncellenmiş ``Madde`` listesi.

custom_id her zaman ``entry_id``'dir (":" yerine "__"), böylece sonuçlar sırasız gelse de eşlenir.
"""
