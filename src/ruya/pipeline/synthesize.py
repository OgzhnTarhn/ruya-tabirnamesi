"""Adım 4 · Sentez: kaynaklı Türkçe yorum (LLM, numaralı kaynaklar, kodda atıf doğrulama).
Takvim: Hafta 5.

- Adaylar numaralı kaynaklar olarak verilir ([K1] entry_id · başlık, metin_tr, metin_asli);
  model JSON şemasıyla bolumler[{metin, kaynaklar[{entry_id, alinti}]}] ve bulunamayanlar
  döndürür. ``atiflari_dogrula`` verilmemiş entry_id içeren atıfları atar, metinde geçmeyen
  alıntıları boşaltır (docs/03, adım 4).
- Sistem talimatı ``prompts/sentez_v<n>.md``; kurallar docs/05 bölüm 3 ve docs/07.
  Sabit talimat mesajların başında durur (geçidin önek önbelleği için).
- Eşleşmeyen ya da maddesi olmayan semboller ``Yorum.bulunamayanlar``'a (İG-31).
- ``cikarim.hassas_icerik`` ise ``Yorum.guvenlik_notu = etik.GUVENLIK_NOTU``.
- ``Yorum.uyari`` her zaman ``etik.UYARI_METNI`` (İG-36).
- İstek ``istemci.mesaj(istek, ruya_icerir=True)`` ile gönderilir (rüya metni
  içerir; docs/03 bölüm 5.2).
"""

from __future__ import annotations

from ruya.llm.client import LLMIstemcisi
from ruya.schemas import Baglam, CikarimSonucu, Eslesme, Getirilenler, Kullanim, Yorum

TALIMAT = "sentez_v1"


def synthesize(
    cikarim: CikarimSonucu,
    eslesmeler: list[Eslesme],
    getirilenler: Getirilenler,
    baglam: Baglam | None,
    istemci: LLMIstemcisi,
) -> tuple[Yorum, Kullanim]:
    raise NotImplementedError("Hafta 5: pipeline/synthesize.py (docs/08)")
