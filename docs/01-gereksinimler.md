# 01 · Gereksinimler

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Etiketler: **[M]** = MVP'de (Aşama 1) olmalı · **[S]** = sonraki aşamalarda · **[O]** = isteğe bağlı

## İşlevsel gereksinimler (İG)

### Girdi

| Kod | Gereksinim | Aşama |
|---|---|---|
| İG-01 | Kullanıcı rüyasını serbest Türkçe metin olarak girebilir (en fazla ~3.000 karakter). | [M] |
| İG-02 | Kullanıcı isterse bağlam bilgisi girebilir: cinsiyet, medeni hâl, rüyanın görüldüğü mevsim, gurbette mi. Hepsi isteğe bağlıdır. | [S] Aşama 3 |
| İG-03 | Kullanıcı hangi geleneklerin kullanılacağını seçebilir: İslami klasik, Batı, psikanalitik. | [S] Aşama 2 |

### Sembol çıkarımı

| Kod | Gereksinim | Aşama |
|---|---|---|
| İG-10 | Sistem rüyadaki sembolleri yalın hâlde çıkarır (`yılanlar` → `yılan`). | [M] |
| İG-11 | Her sembol için nitelikleri (renk, boyut, sayı), eylemi ve duyguyu yakalar. | [M] |
| İG-12 | Olumsuzlamayı tanır. "Yılan görmedim" bir sembol değildir. | [M] |
| İG-13 | Çok kelimeli sembolleri tanır: "ölmüş babam", "deniz suyu". | [M] |
| İG-14 | Rüyanın türü hakkında bir ön değerlendirme yapar: rahmânî, şeytânî ya da nefsânî. Bu bir etiket olarak gösterilir, hüküm olarak değil. | [S] Aşama 3 |

### Eşleme ve getirme

| Kod | Gereksinim | Aşama |
|---|---|---|
| İG-20 | Çıkarılan her sembolü kanonik sembol indeksindeki bir `symbol_id`'ye eşler. Eş anlamlılar ve ekli biçimler de bu kimliğe eşlenir. | [M] |
| İG-21 | İndekste bulunamayan semboller için anlamsal (vektör) aramayla en yakın sembolü önerir. | [S] Aşama 2 |
| İG-22 | Her sembol için her kaynaktan en fazla N madde getirir (varsayılan N=2). Böylece büyük bir kaynak sonuçları domine edemez. | [M] |
| İG-23 | Kullanıcının bağlamına uyan koşullu maddeleri öne çıkarır. | [S] Aşama 3 |

### Yorum üretimi

| Kod | Gereksinim | Aşama |
|---|---|---|
| İG-30 | Yorum yalnızca getirilen maddelere dayanır. Her yorum cümlesi bir kaynağa atıf taşır. | [M] |
| İG-31 | Bir sembol için madde yoksa "kaynaklarda bulunamadı" der ve tahmin yürütmez. | [M] |
| İG-32 | Çıktıyı sabit bir yapıda verir: sembol başına "Kaynakların söyledikleri", ardından "Uzlaşılan noktalar", "Ayrışan noktalar" ve "Kaynaklarda bulunmayanlar". | [M] (basit) → [S] (tam) |
| İG-33 | Her yorumun hangi gelenekten geldiğini belirtir (İslami klasik / Batı halk / psikanalitik). Çeviri metinler için "makine çevirisi" notu düşer. | [M] |
| İG-34 | İbn Sirin'e atfedilen metinden gelen yorumlarda "nispeti sahih değil" notunu gösterir. | [M] |
| İG-35 | Ölüm, hastalık ve felaket sembollerinde yumuşatılmış bir dil kullanır ve geleneğin "kötü rüya anlatılmaz" adabını hatırlatır. | [M] |
| İG-36 | Her yanıtın altında sabit bir uyarı metni gösterir (bkz. [07-etik-ve-hukuk.md](07-etik-ve-hukuk.md)). | [M] |

### Arayüz

| Kod | Gereksinim | Aşama |
|---|---|---|
| İG-40 | Tek sayfalık bir web arayüzü: rüya kutusu, isteğe bağlı bağlam alanları, "Yorumla" düğmesi. | [M] |
| İG-41 | Yanıttaki atıflar tıklanınca kaynak maddenin hem aslı hem çevirisi gösterilir. | [M] |
| İG-42 | "Hata ayıklama" sekmesi: çıkarılan semboller, eşlemeler, getirilen maddeler ve skorlar. Öğrenmek için kritik. | [M] |

### Veri hattı

| Kod | Gereksinim | Aşama |
|---|---|---|
| İG-50 | Her kaynak için tekrar çalıştırılabilir bir ayrıştırma betiği. Ham dosyadan `entries.jsonl` üretir. | [M] |
| İG-51 | Yabancı dildeki maddeler Türkçeye çevrilir. Çeviri ayrı bir alanda saklanır, aslı korunur. | [M] |
| İG-52 | Her kayıt şu alanları taşır: `kaynak`, `gelenek`, `dil`, `lisans`, `konum` (bab, sayfa ya da satır). | [M] |
| İG-53 | Maddelerdeki koşullar ("kadın görürse", "kışın") yapılandırılmış bir alana ayrıştırılır. | [S] Aşama 3 |

## İşlevsel olmayan gereksinimler (İOG)

| Kod | Gereksinim | Hedef değer |
|---|---|---|
| İOG-01 | **Yanıt süresi** | Tipik bir rüya için ≤ 30 saniye (MVP), ≤ 20 saniye (Aşama 3) |
| İOG-02 | **Sorgu maliyeti** | Rüya başına ≤ 0,15 $. Aylık harcama limiti API panelinden ayarlanır. |
| İOG-03 | **Gizlilik** | Rüyalar yalnızca senin Google Drive'ında saklanır, kayıt tutma varsayılan olarak kapalıdır. API'ye yalnızca senin kendi rüyan gider. |
| İOG-04 | **Tekrarlanabilirlik** | Veri hattı tek komutla baştan kurulabilir. LLM çağrıları geliştirme sırasında diske önbelleklenir. |
| İOG-05 | **Platform** | Çalıştırma Google Colab'de (Python ≥3.11), veri Google Drive'da. Bilgisayarda (Windows 11, `C:\ruya-tabirnamesi`) yalnızca kod yazılır ve verisiz testler çalışır. |
| İOG-06 | **Lisans izlenebilirliği** | Her kaydın `lisans` alanı dolu. NC lisanslı kayıtlar tek bir filtreyle çıkarılabilir. |
| İOG-07 | **Gözlemlenebilirlik** | Her sorguda adım süreleri, token sayıları ve maliyet loglanır (rüya metni loglanmaz). |
| İOG-08 | **Test edilebilirlik** | Ayrıştırıcılar ve eşleme mantığı birim testlerle, boru hattı test setiyle sınanır. |

## Kabul ölçütleri (MVP, Aşama 1 sonu)

- [ ] 20 rüyalık test setinde sembol yakalama oranı (recall) ölçülmüş ve ≥ %80.
- [ ] Her yanıtta en az bir atıf var. Atıfı olmayan yorum cümlesi yok (10 yanıt elle incelenecek).
- [ ] "Uzay gemisi" testi: kaynakta olmayan bir sembolde sistem "bulunamadı" diyor.
- [ ] Uyarı metni her yanıtta görünüyor.
- [ ] Hata ayıklama sekmesi çalışıyor.
