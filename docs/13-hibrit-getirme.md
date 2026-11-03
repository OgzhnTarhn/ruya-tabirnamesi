# 13 · Hibrit getirme: araştırma ve tasarım

> Durum: Karar · Tarih: 3 Kasım 2026. Önceki "yalnız sözlük" getirmesinin yerine geçer ([03](03-mimari.md), Adım 3).

## 1. Çözülen sorun

Sözlüğe dayalı getirme yalnızca bir sembole bağlı 1.436 maddeye (10.801'de) ulaşır; sözlükte olmayan sembol ("baba") hiç bulunamaz. Alt paragrafların çoğu sembolün adını taşımaz ("onu sokarsa ayıp bulur"), bu yüzden düz metin aramada da kaybolur.

## 2. Araştırma özeti

| Bulgu | Kaynak | Bu projedeki sonucu |
|---|---|---|
| Hibrit arama ve HyDE birlikte iyi bir varsayılandır; tek varsayımsal belge genellikle yeter | [Wang vd., 2024](https://arxiv.org/pdf/2407.01219) | BM25 + vektör + HyDE, sembol başına tek HyDE metni |
| Füzyonda RRF, k=60 yaygın bir seçimdir | [UTokyo, TREC 34](https://trec.nist.gov/pubs/trec34/papers/UTokyo.rag.pdf) | RRF k=60; skor ölçeklerini denkleştirmek gerekmez |
| HyDE en çok kısa sorgu ve resmî üsluplu belgelerde işe yarar; üzerine LLM gecikmesi ekler | [Elastic (üretici, küçük örnek)](https://www.elastic.co/search-labs/de/blog/hyde-semantic-search-elasticsearch) | Sorgularımız tam bu tür; ek çağrı açmadan çıkarım yanıtında üretilir |
| Türkçe aramada köke indirgeme başarımı %20'ye kadar artırabilir; kök bulucu en iyi, kelime kesme ise ucuz ve yakın bir seçenektir | [Lemur deneyleri](https://arxiv.org/pdf/1405.1740), [Can vd., 2008](https://repository.bilkent.edu.tr/items/5be10741-6b40-44ba-b324-9e7951d54c03) | BM25 terimi zeyrek kökü; kök yoksa ilk 5 harf |
| Parçanın başına bağlam eklemek getirme hatasını azaltır; bağlamlı vektör + bağlamlı BM25 %49, yeniden sıralama ile %67 (ilk 20 parça, kendi veri setleri) | [Anthropic](https://www.anthropic.com/engineering/contextual-retrieval) | Bağlam önekini LLM ile değil, künye ve üst maddeden kodla kurarız |
| Bu oranlar yalnızca getirmeyi ölçer, yanıt kalitesini değil | [Almond AI yanıtı](https://medium.com/almond-ai/responding-to-anthropics-contextual-retrieval-for-rag-apps-why-context-is-not-all-you-need-af503985aa55) | Sayıları kendi korpusumuz için varsaymıyoruz |

**Sınır:** Türkçe kök bulmayı hibrit, çok dilli bir RAG içinde sınayan çalışma bulamadık. Türkçe bulgular eski (2008–2014). Bu tasarımın bu korpustaki kazancı **ölçülmedi**.

## 3. Akış

```
Sembol (yalın, nitelik, eylem, hyde)
  ├─ sözlük: symbol_id'nin maddeleri        (varsa)
  ├─ BM25: bağlamlı parçalar, Türkçe kök
  ├─ vektör: sembol sorgusunun embedding'i
  └─ HyDE: varsayımsal maddenin embedding'i  (varsa)
        ↓ RRF (k=60), madde düzeyinde; en iyi 40 aday
  EVREN reranker: sorgu ↔ maddenin en iyi parçası
        ↓ eşik altı atılır → hiç kalmazsa "bulunamadı"
  Bağlam koşulu bonusu → kaynak başına en fazla N madde
```

- **Bağlamlı parça:** `eser · yazar. Sembol: … Bölüm: …` öneki + en çok 1.000 karakterlik pencere (150 örtüşme). Alt paragraf, üst maddenin sembolünü miras alır. Önek arama içindir; atıf ve alıntı doğrulaması yine `metin_tr` üzerindedir.
- **Pasaj:** Sentez, kırpılmış madde başı yerine aramayı kazanan parçayı görür (`Aday.pasaj`).
- **HyDE:** `Sembol.hyde` tabirname üslubunda en çok iki cümledir ve `cikarim_v2` yanıtının içinde gelir, yani ek LLM çağrısı açmaz. **Yalnızca aramada kullanılır; kullanıcıya gösterilmez, modele kaynak diye verilmez.**
- **Sözlükte olmayan sembol:** Artık hibrit aramaya girer. `Getirilenler` anahtarı `symbol_id`, yoksa `serbest:<normalleştirilmiş ad>`.
- **"Bulunamadı":** Reranker eşiği (`GETIRME_ESIGI`, config) korur. Denemede ilgili madde 0,45, ilgisiz 0,003, "uzay gemisi" ↔ "gemi" 0,10 aldı; eşik 0,15. Üç örnekten alınmış başlangıç değeridir.
- **Freud:** `gelenekler` boşsa hibrit aramaya girmez; kullanıcı `psikanalitik` seçerse girer (Freud yöntem katmanıdır, sembol sözlüğü değildir).
- **Yedek:** İndeks yoksa ya da embedding/reranker çağrısı hata verirse sistem sözlük yoluna döner ve bunu `Aday.gerekceler` ile loga yazar.

## 4. Teknoloji kararları

| Karar | Seçim | Gerekçe | Bedeli |
|---|---|---|---|
| Embedding | EVREN `qwen3-embedding-8b`, 1.024 boyut | Denemede 0,4 sn; torch gerekmez | Rüyadan türetilen sorgu geçide gider (LLM adımlarıyla aynı) |
| Reranker | EVREN `qwen3-reranker-8b` | Denemede 0,3 sn | 1 Aralık sonrası fiyatı belirsiz (R13) |
| Vektör deposu | numpy dizisi, tam tarama | ~13 bin parça için yeterli, Chroma bağımlılığı kalkar | 100 bin parçayı geçerse yeniden düşünülür |
| BM25 | Kendi Okapi kodumuz (k1=1,5, b=0,75) | Küçük, testli; Türkçe kök kontrolü bizde | Kendi kodumuzun bakımı |
| HyDE modeli | DeepSeek (ana model, çıkarımın parçası) | Kullanıcı kararı; ek çağrı yok | Çıkarım yanıtı biraz uzar |
| OCR | EVREN `deepseek-ocr-2`, `POST /v1/ocr` | Rüya defteri fotoğrafı ve taranmış belge girişi | Görsel geçide gider; önbelleğe yazılmaz |

Koşullu yorum için `kosullar`, 18 token/sn hızda 10.801 maddelik LLM geçişi gün sürdüğünden önce kurallarla çıkarılır ("kadın görürse", "evli ise", "kışın"); bağlam eşleşirse aday öne geçer. Kural kaçırırsa zarar yok: madde yine sıralamada kalır.

## 5. Bilinçli olarak yapılmayan

- Deneyler D1–D3 ve yeni ölçüm: kullanıcı isteğiyle ertelendi. Kazanç iddia edilmez.
- LLM ile parça başına bağlam üretimi: 13 bin çağrı, bu hızda günler sürer.
