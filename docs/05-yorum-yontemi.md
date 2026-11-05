# 05 · Yorum Yöntemi: Klasik Tabiri Sisteme Dökmek

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Projenin en özgün kısmı bu belge. Teknik altyapı hazır ve ucuz. Asıl zor iş, tabircinin düşünme biçimini veri şemasına ve talimatlara dönüştürmek.
> Dayanaklar: TDV İA "Rüya" ve "Tâbirnâme" maddeleri, Balaban 2014, Elbir & Uludüz 2019 (bkz. `docs/arastirma/`).

## 1. Temel fikir

Klasik tabirci rüyaya sözlüğe bakar gibi bakmaz. TDV İslâm Ansiklopedisi'ne göre muabbir (rüya yorumcusu) şunları yapar:

- Rüyadaki suretlerin dış ve iç yönlerini ayırır.
- Bir ipucu (*karîne*) üzerinden anlama geçer.
- Rahmânî rüyayı şeytânî rüyadan ayırt eder.
- Kur'an'daki teşbihleri, kelime köklerini, atasözlerini ve deyimleri bilir.
- Rüyanın **nerede, nasıl, ne zaman ve kim tarafından** görüldüğünü dikkate alır.

Bu tanım sistemin beş katmanını veriyor.

## 2. Beş katman

### Katman 1 · Rüya türü (Aşama 3)

| Tür | Anlamı | Sistemin davranışı |
|---|---|---|
| Rahmânî (sâdık) | Müjde ya da uyarı | Normal yorum |
| Şeytânî (*adgâs-ı ahlâm*) | Korkutucu ve karışık; gelenekte tabir edilmez | Önce geleneğin "kötü rüya anlatılmaz, üzerinde durulmaz" adabı hatırlatılır. Sonra yumuşak bir dille ve isteğe bağlı olarak yorum verilir. |
| Nefsânî | Gün içinde zihni meşgul eden şeylerin yansıması (aç olan yemek görür) | "Bu tür rüyalar gelenekte genellikle günlük kaygıların yansıması sayılır" notu eklenir. |

- Tür, sembol çıkarımı adımında **bir ipucu** olarak tahmin edilir. Kesin hüküm gibi sunulmaz, "geleneksel sınıflandırmaya göre şuna benziyor" denir.
- **Sınır:** Sistem bir rüyanın "Allah'tan" olduğunu ya da olmadığını söylemez.

### Katman 2 · Sembol ve nitelik (Aşama 1)

- **Sembol:** yalın isim. Örnek: `yılan`.
- **Nitelikler:** renk, boyut, sayı, durum. Örnek: `siyah`, `büyük`, `ölü`.
- **Eylem:** rüya görenin sembolle ilişkisi. Örnek: `gördü`, `öldürdü`, `ısırıldı`, `yedi`.
- **Duygu:** Örnek: `korku`, `sevinç`.

Kaynaklarda nitelik ve eylem anlamı değiştiriyor. Bu yüzden getirme adımında nitelik eşleşmesi sıralamayı etkiliyor (bkz. [03-mimari.md](03-mimari.md), Adım 3).

### Katman 3 · Bağlam koşulları (Aşama 3)

Gerçek veride görülen koşul türleri:

| Koşul | Değerler | Örnek (kaynak) |
|---|---|---|
| `cinsiyet` | kadın / erkek | "For a young woman to…" (Miller, 513 paragraf); "Kadın görürse bahtlı bir ere varır" (İbn Sirin tercümesi) |
| `medeni_hal` | evli / bekâr | Miller'da sık geçiyor |
| `mevsim` | yaz / kış / … | Buz yazın nimet, kışın meşakkat (İbn Sirin tercümesi) |
| `durum` | hasta / gurbette / mazlum / sapkın / zengin / fakir | "وإن رآه مظلوم انتصر" (mazlum görürse zafer bulur, Nablusi) |
| `din` | Müslüman / Hristiyan / … | Kilise görmek (Ekinci, ikincil kaynak) |
| `kapsam` | kişi / vilayet / padişah | Bazı tabirler kişiye değil topluma yöneliktir. Dar kurallarla işaretlenir (`enrich/kapsam_kurallari.py`) ve sentezde `Kapsam:` satırı olarak verilir |

**Nasıl uygulanacak:**

1. **Çevrimdışı:** Her madde, "eğer … ise" kalıplarına göre `kosullar` listesine ayrıştırılır. Bu işi LLM yapar, 20 madde elle kontrol edilir.
2. **Sorgu anında:** Kullanıcının verdiği bağlam (isteğe bağlı form) koşullarla karşılaştırılır.
   - Eşleşen koşullu yorum **öne** çıkar.
   - Eşleşmeyenler "diğer vecihler" başlığı altında gösterilir.
   - Kullanıcı bağlam vermediyse koşullar listelenir: "kadın görürse…, erkek görürse…".
3. **Sınır:** Sistem kullanıcının cinsiyetini ya da dinini tahmin etmez, yalnızca kullanıcının verdiği bilgiyi kullanır.

### Katman 4 · Anlam türetme yolları ve vecih çokluğu (Aşama 3)

- **Türetme yolları:** ayet, hadis, mesel (atasözü), kelime kökü, zıddıyla tabir (ölüm = uzun ömür, ağlamak = sevinç), ebced. Bunlar `yontem` alanına etiket olarak eklenir. Kullanıcıya "bu yorum zıddıyla tabir yoluyla yapılmış" diye açıklanabilir. Öğretici ve şeffaf.
- **Vecih çokluğu:** Tek bir metin bile aynı sembol için birden çok yorum veriyor. Örneğin bir madde "yedi vecih üzre" açıklanıyor. **Çelişki bir hata değil, geleneğin doğal yapısı.**
- **Kural:** Sistem çelişkileri uzlaştırmaya çalışmaz. Yorumları otorite ve kaynak etiketiyle yan yana koyar.

### Katman 5 · İki eksenli sembol taksonomisi (Aşama 0'da basit, Aşama 3'te tam)

- **Klasik eksen (`bab_kategorisi`):** Elbir & Uludüz 2019'daki 53 bab, yaklaşık 15 üst kategoriye sadeleştirilecek: kutsal varlıklar; gök cisimleri; su; ateş ve ışık; yeryüzü ve yapılar; ibadet; insan ve beden; aile; eşya; yiyecek; giyim; silah; ölüm; hayvanlar; meslekler.
- **Modern eksen (`hvdc_kategorisi`):** Hall & Van de Castle'ın 10 kategorisi: karakterler, etkileşimler, duygular, aktiviteler, çabalama, şans ve talihsizlik, mekânlar ve nesneler, betimleyici öğeler, yiyecek, geçmişten öğeler. Hayvanlar "karakterler", beden parçaları "mekânlar ve nesneler" sayılır; alan adları `schemas.py` içindeki `BabKategorisi` ve `HvdcKategorisi` türlerindedir.
- **Neden iki eksen:** Kullanıcıya "rüyanda en çok hayvan ve su sembolleri var" gibi bir özet gösterilebilir. Değerlendirmede de kategori bazında başarı ölçülebilir.

## 3. Sentez talimatının kuralları (`prompts/sentez_v1.md` için taslak)

Talimat dosyası Aşama 1'de yazılacak. Şimdilik kuralları:

1. Yalnızca verilen kaynak maddelerine dayan. Her yorum cümlesi bir atıf taşısın.
2. Bir sembol için madde yoksa "kaynaklarda bulunamadı" de ve tahmin yürütme.
3. Kaynaklar çelişiyorsa uzlaştırma, yan yana koy ve hangisinin hangi gelenekten geldiğini belirt.
4. Kullanıcı bağlam verdiyse ona uyan koşullu yorumu önce ver. Bağlam vermediyse koşulları listele.
5. Çevrilmiş bir ifadeyi aktarırken çeviri olduğunu belirt. İbn Sirin kaynaklı yorumlarda atıf notunu koru.
6. Gelecek hakkında kesin konuşma. "Gelenekte … olarak yorumlanır" kalıbını kullan.
7. Ölüm, hastalık ve felaket sembollerinde yumuşak bir dil kullan. Gerekirse geleneğin zıddıyla tabir yoluna değin (ölüm = uzun ömür), ama bunu teselli amacıyla çarpıtma.
8. Dinî otorite iddiasında bulunma. "Diyanet'e göre", "Allah'ın mesajı" ve benzeri ifadeler yasak.
9. Psikolojik ya da tıbbi teşhis koyma. Freud'dan gelen yorumları "psikanalitik bir bakış açısı" olarak sun.
10. Çıktı yapısı: her sembol için "Kaynakların söyledikleri", ardından "Uzlaşılan noktalar", "Ayrışan noktalar" ve en sonda "Kaynaklarda bulunmayanlar".

## 4. Örnek: beklenen yanıtın iskeleti

> **Girdi:** "Rüyamda denize girdim, sudan siyah bir yılan çıktı, çok korktum." Bağlam: kadın, bekâr, sonbahar.
>
> **Yılan (siyah)**
> - *İslami klasik:* Nablusi yılanı genel olarak düşmanla, siyah yılanı ise daha güçlü bir düşmanla yorumlar [Nablusi · حية]. *(Kadınlar için ayrı bir koşul bulunamadı.)*
> - *Batı halk geleneği:* Miller'a göre yılan görmek ihanete karşı bir uyarıdır. Genç bir kadın için ise … [Miller · Snakes].
> - **Uzlaşılan:** Her iki kaynak da tehdit ve dikkat temasında birleşiyor.
> - **Ayrışan:** Nablusi tehdidi bir kişiye (düşmana) bağlıyor, Miller ise bir duruma (ihanete).
>
> **Deniz** …
>
> **Kaynaklarda bulunamayanlar:** –
>
> *Uyarı metni…*

Bu örnek gösterim amaçlıdır. Yorumlar gerçek maddelerden alınmamıştır.
