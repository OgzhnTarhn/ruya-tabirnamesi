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
| H1 | | |
| H2 | | |
| H3 | | |
| H4 | | |

Gözlemler:

## Karar

- K0 kararı:
- Güncellenen belgeler (02 bölüm 5'teki süre ve kota, 09 R1/R2/R13/R14, terimler.md):
