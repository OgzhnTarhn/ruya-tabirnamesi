# 06 · Değerlendirme ve Ölçme Planı

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> İlke: **Ölçmediğin şeyi iyileştiremezsin.** Her aşama aynı test setiyle ölçülür, ayrıntılı raporlar Drive'da `raporlar/` altına tarihli olarak, özet satırı repoda [olcumler.md](olcumler.md)'ye kaydedilir.
> Kod: ölçütler `src/ruya/degerlendirme/metrikler.py`, test seti şeması `ruya.schemas.TestOrnegi`.

## 1. Test seti

### Nereden gelecek?

| Kaynak | Adet | Not |
|---|---|---|
| Senin yazacağın rüyalar | 15–20 | Gerçek ya da hayalî. Kısa, orta ve uzun karışık olsun. |
| LLM'e ürettirilen çeşitli rüyalar | 10–20 | Belirli sembolleri, olumsuzlamaları ve çok kelimeli ifadeleri sınamak için. Hepsini elle gözden geçirip düzelteceksin. |
| DreamBank'ten çevrilmiş raporlar (isteğe bağlı) | 5–10 | CC BY-NC-SA lisanslı, atıf verilmeli. Gerçekçi ve "dağınık" anlatılar için iyi. |
| Özel testler | 5 | Aşağıdaki listeye bak. |

**Hedef boyutlar:** Aşama 1'de 20 rüya, Aşama 3 sonunda 40–50 rüya.

**Özel testler:**

1. **Bulunamaz testi:** Kaynaklarda olmayan bir sembol, örneğin "uzay gemisi". Beklenen: "bulunamadı".
2. **Olumsuzlama testi:** "Yılan görmedim ama çok korktum." Beklenen: yılan sembol değil, korku duygu.
3. **Çok kelimeli sembol testi:** "Ölmüş babamı gördüm." Beklenen: `olmus_baba` ya da `baba` sembolü ve `ölü` niteliği.
4. **Koşul testi:** Aynı rüya bir kez kadın, bir kez erkek bağlamıyla verilir. Beklenen: farklı koşullu yorum öne çıkar (Aşama 3).
5. **Ağır içerik testi:** Ölüm ya da kaza içeren bir kâbus. Beklenen: yumuşak dil ve uyarı.

### Kayıt şeması (`eval/dataset/ruyalar_v1.jsonl`)

```json
{
  "id": "r007",
  "metin": "Rüyamda denize girdim, sudan siyah bir yılan çıktı, çok korktum.",
  "baglam": {"cinsiyet": "kadin", "mevsim": "sonbahar"},
  "beklenen_semboller": ["deniz", "yilan"],
  "beklenen_nitelikler": {"yilan": ["siyah"]},
  "beklenen_duygular": ["korku"],
  "olmamasi_gerekenler": [],
  "beklenen_maddeler": {"yilan": ["nablusi:004310", "miller:018710"]},
  "notlar": "siyah yılan için ayrı Nablusi maddesi var mı kontrol et"
}
```

`beklenen_maddeler` alanı sen elle doldurursun. Bu iş yavaş ama RAG'ı en iyi öğreten kısım.

## 2. Ölçütler

| Katman | Ölçüt | Nasıl hesaplanır | MVP hedefi | Aşama 3 hedefi |
|---|---|---|---|---|
| Çıkarım | Sembol recall (kapsama) | Bulunan beklenen sembol / tüm beklenen semboller | ≥ %80 | ≥ %90 |
| Çıkarım | Sembol precision (isabet) | Doğru semboller / bulunan tüm semboller | ≥ %80 | ≥ %90 |
| Çıkarım | Olumsuzlama doğruluğu | Olumsuzlama testlerinde hatalı sembol sayısı | 0 | 0 |
| Eşleme | Eşleme doğruluğu | Doğru `symbol_id` / eşlenen semboller | ≥ %85 | ≥ %95 |
| Getirme | Recall@5 | Kaynak başına ilk 5 sonuçta bulunan beklenen maddeler | ölçülür | ≥ %80 |
| Getirme | Kaynak çeşitliliği | Maddesi olan semboller için ortalama farklı kaynak sayısı | ≥ 1,5 | ≥ 2 |
| Sentez | Atıf kapsamı | Atıf taşıyan iddia bölümleri / tüm iddia bölümleri (aşağıdaki nota bak) | %100 | %100 |
| Sentez | Sadakat (elle) | Kaynağın söylemediğini söyleyen cümle sayısı (10 yanıt) | 0 | 0 |
| Sentez | "Bulunamadı" doğruluğu | Bulunamaz testinde doğru davranış | %100 | %100 |
| Sentez | Etik kurallar | Yasak ifadeler ("kesinlikle", "Diyanet'e göre"…) için otomatik tarama | 0 ihlal | 0 ihlal |
| İşletim | Süre | Rüya başına medyan saniye | ≤ 30 | ≤ 20 |
| İşletim | Maliyet | Rüya başına ortalama $ | ≤ 0,15 | ≤ 0,10 |

**Atıf kapsamının birimi.** Citations API yanıtı cümlelere değil, atıf sınırlarından bölünmüş metin bloklarına ayırır. Her blok bir `YorumBolumu` olur. Bir bloğa birden çok cümle düşebilir ve "## Yılan" gibi başlıklar atıfsız bloklar olarak gelir. Bu yüzden:

- Ölçüm birimi **iddia bölümüdür**. Başlık bölümleri (`#` ile başlayan satırlardan oluşan) ve harf içermeyen bölümler (boşluk, noktalama, liste işareti) sayılmaz.
- "Kaynaklarda bulunmayanlar" bölümü ve uyarı metni iddia değildir, sayılmaz.
- Cümle düzeyindeki sadakat, otomatik ölçütle değil elle yapılan sadakat kontrolüyle ölçülür.

## 3. Nasıl çalıştırılacak?

Colab'de `notebooks/06_degerlendirme.ipynb` açılır, etiket girilir (ör. `asama1-opus`) ve çalıştırılır. Notebook arka planda şunu çağırır:

```
python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl --etiket "asama1-opus"
```

- **Çıktı:** Drive'da `raporlar/2026-11-28_asama1-opus.md`. Rapor ölçüt tablosunu, başarısız örnekleri ve toplam maliyeti içerir. Özet satırı repodaki `docs/olcumler.md` dosyasına eklenip commit edilir. Böylece ilerleme git geçmişinde de görünür.
- Sentez sadakati gibi elle yapılan kontroller için betik bir kontrol listesi üretir. Sen işaretlersin.
- **Maliyet uyarısı:** Her çalıştırma ücretlidir. 20 rüya × ~0,10 $ = ~2 $. Geliştirme sırasında disk önbelleği açık kalır.

## 4. Karşılaştırmalı deneyler (Aşama 2 ve 4)

| Deney | Neyi karşılaştırır | Hangi ölçüt |
|---|---|---|
| D1 | e5-large ile Qwen3-Embedding-0.6B | Vektör yedeğinde eşleme doğruluğu |
| D2 | Reranker var ile yok | Recall@5 |
| D3 | Kaynak başı N=1, 2, 3 | Kaynak çeşitliliği ve sadakat |
| D4 | Opus 5.5, Sonnet 5.5 ve Haiku 5.5 (sentez) | Sadakat, maliyet ve süre |
| D5 | Claude ile yerel Gemma/Qwen | Bütün ölçütler |

Her deneyin sonucu `docs/deneyler/` altına kısa bir not olarak yazılır: hipotez, sonuç ve karar.
