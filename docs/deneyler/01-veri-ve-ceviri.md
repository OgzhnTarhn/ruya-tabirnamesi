# 01 · Veri ve Çeviri Denemesi

> Tarih: 26 Ekim – 1 Kasım 2026 · Hafta: 1 · Kilometre taşı: K0 (1 Kasım)
> Notebook: `notebooks/deneyler/01_veri_ve_ceviri.ipynb` · Kod atılabilir; kalıcı kod Hafta 2'de `src/ruya/` altına yazılır.
> Görev listesi: [08, Hafta 1](../08-yol-haritasi-takvim.md)

## Soru

Projenin iki büyük bilinmeyeni: (1) Nablusi'nin alt paragrafları güvenilir biçimde ayrıştırılıp sembollere atanabilir mi? (2) Modelin (`deepseek-v4.1-flash`) Arapçadan Türkçeye çevirisi tabir için yeterince iyi mi?

## Hipotezler

| # | Hipotez | Eşik | Tutmazsa |
|---|---|---|---|
| H1 | "ح" babındaki 50 paragrafta başlıklı madde ve alt paragraf sınırları kurallarla doğru bulunur | 50 paragrafın ≥ 48'i | Ayrıştırma kuralları gözden geçirilir |
| H2 | 10 alt paragrafın sembolünü LLM doğru atar | ≥ 8/10 (R2) | Atama talimatı iyileştirilir; başlıklı maddelerle sınırlı başlanır |
| H3 | 10 Nablusi ve 10 Miller çevirisinin ortalama puanı yeterli | ≥ 3/5 (R1) | Talimat iyileştirilir ya da İngilizce ara katman denenir (1 hafta kayma) |
| H4 | Bütün Nablusi'nin çevirisi ücretsiz dönemde (1 Aralık'a kadar) rahatça biter | ≤ 30 milyon token (iki günlük kota) ve 5 eşzamanlı istekle ≤ 24 saat | Eşzamanlılık artırılır, iş günlere bölünür; çeviri yalnızca 50 sembolün maddeleriyle sınırlanabilir |

## Yöntem

- **Veri:** `scripts/download_sources.py` ile Nablusi ve Miller `data/raw/` altına indirilir; SHA256 kaydedilir.
- **Ayrıştırma:** "ح" (ḥâ) babından ardışık 50 paragraf.
- **Sembol atama:** Bu 50 paragraftan 10 alt paragraf; doğru cevap elle belirlenir.
- **Çeviri:** 10 Nablusi + 10 Miller maddesi. Çeviriler aslıyla yan yana okunur. Puanlama: 1 = anlam bozuk, 3 = anlam doğru ama terimler tutarsız, 5 = anlam ve terimler doğru, akıcı. Terimler [terimler.md](../terimler.md)'ye işlenir.
- **Token ve süre:** H3'teki 10 Nablusi çağrısından karakter başına girdi/çıktı tokenı ve istek başına etkin süre ölçülür; bütün Nablusi için toplam token ve süre tahmin edilir. (İlk sürümde H4, Claude Batch API maliyetiydi; 31 Ekim'de sağlayıcı EVREN olunca token ve süreye çevrildi.)

## Sonuç

| Hipotez | Ölçülen | Tuttu mu? |
|---|---|---|
| H1 | 50 paragraflık deneme yapılmadı; ayrıştırıcı doğrudan bütün Nablusi için yazıldı (5.782 madde, birim testli) | Denenmedi, iş aştı |
| H2 | LLM ile sembol atama denenmedi | Denenmedi: deterministik atama seçildi |
| H3 | 1–5 puanlaması yapılmadı; dört kaynağın tamamı çevrildi (2 Kasım) | Ölçülmedi |
| H4 | Çeviri 2 Kasım'da, ücretsiz dönem içinde bitti; ama EVREN tek istekte yavaş kaldığı için Claude Code + orkestra ile | Tuttu, başka yolla |

Gözlemler (7 Kasım'da geriye dönük yazıldı):

- Bu deney planlandığı gibi yapılmadı; 31 Ekim'de sağlayıcı EVREN'e geçince sıra değişti ve doğrudan asıl işlere geçildi.
- Ayrıştırma: başlıklı madde ve alt paragraf ayrımı kurallarla yapıldı, alt paragraflar `ust_madde_id` ile başlıklarına bağlandı.
- Sembol atama: LLM yerine sözlük varyantlarıyla eşleme; eşleşmeyen alt paragraf üst maddesinin sembolünü devralır (`enrich/sembol_ata.py`).
- Çeviri: önce Claude Code ajanları, kullanım sınırından sonra orkestra ile EVREN ajanları. İlk turda yarıda kesilen uzun paragraflar uzunluk oranı denetimiyle bulunup yeniden çevrildi.
- Çeviri kalitesi henüz insan gözünden geçmedi. Örnek kusur: ibn_sirin:006237'de ذَكَر "zikir" diye çevrilmiş.

## Karar

- K0 kararı: Deney atlandı; ayrıştırma kurallarla, sembol atama deterministik, çeviri Claude Code + EVREN ile tamamlandı. Kalite kontrolü çevirilerin gözden geçirilmesine bırakıldı.
- Güncellenen belgeler: 02 bölüm 5 (çeviri stratejisi), 04 TK-03/TK-04, 08 Hafta 1.
