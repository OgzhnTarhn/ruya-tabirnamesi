# Tabir Terimleri Sözlüğü

> Durum: v0.1 taslak · Tarih: 23 Ekim 2026
> Amaç: Çevirilerde ve yorumlarda aynı kavram için hep aynı Türkçe karşılığın kullanılması (docs/02, bölüm 5). Çeviri talimatı (`prompts/ceviri_v1.md`) bu tabloyu olduğu gibi içerir.
> **Gözden geçirme:** Arapça bilmediğin için (S6) karşılıklar TDV İA'daki kullanımla karşılaştırılarak kontrol edilir. Kontrol edilen satırın "Durum" sütununa ✅ konur. Hafta 1 denemesinde çeviriler okunurken tablo büyütülür.

## 1. Temel kavramlar

| Arapça | Okunuş | Çeviride kullanılacak karşılık | Açıklama | Durum |
|---|---|---|---|---|
| رؤيا | rü'yâ | rüya | Uykuda görülen; gelenekte çoğunlukla anlamlı (sâdık) rüya için | 🕓 |
| حُلْم ، أحلام | hulm, ahlâm | karışık rüya | "Rüya Allah'tan, hulm şeytandandır" hadisindeki ayrımla; bağlam genel "rüya" diyorsa "rüya" | 🕓 |
| منام | menâm | rüya (fi'l-menâm: "rüyada") | Kelime anlamı uyku, uyku yeri | 🕓 |
| تعبير | ta'bîr | tabir | Rüyayı yorumlama | 🕓 |
| تأويل | te'vîl | yorum | Tabir ile yakın; "te'vil" olarak bırakılmaz | 🕓 |
| تفسير | tefsîr | yorum, açıklama | *Muntahab*'ın adında geçer | 🕓 |
| معبِّر | muabbir | tabirci (rüya yorumcusu) | | 🕓 |
| أضغاث أحلام | adgâs-ı ahlâm | karışık, anlamsız rüyalar | Yusuf suresi 12:44'teki ifade; tabir edilmez | 🕓 |
| الرؤيا الصادقة ، الصالحة | rü'yâ-yı sâdıka, sâliha | sadık rüya, salih rüya | Rahmânî türe karşılık gelir | 🕓 |
| حديث النفس | hadîsü'n-nefs | nefsin konuşması (nefsânî rüya) | Gün içinde zihni meşgul edenin yansıması | 🕓 |
| بُشرى ، بشارة | büşrâ, beşâret | müjde | | 🕓 |
| إنذار ، نذارة | inzâr, nezâret | uyarı | | 🕓 |
| خير ، شرّ | hayr, şerr | hayır, şer | "hayra yorulur", "şerre yorulur" | 🕓 |

## 2. Metin yapısı ve kalıplar

| Arapça | Okunuş | Çeviride kullanılacak karşılık | Not | Durum |
|---|---|---|---|---|
| باب | bâb | bab (bölüm) | `konum.bab` alanında aslı kalır | 🕓 |
| ومن رأى ، من رأى | ve men raâ | "kim … görürse" | Nablusi'de alt paragrafların başı | 🕓 |
| فإن رآه … | fe-in raâhu | "… görürse" | Koşullu yorumun başı (bkz. docs/05, Katman 3) | 🕓 |
| يدلّ على | yedüllü alâ | "… ile yorumlanır" / "…ya işaret eder" | En sık kalıp; kehanet diline çevrilmez | 🕓 |
| وربما دلّ على | ve rubbemâ delle alâ | "bazen … ile de yorumlanır" | Vecih çokluğunun işareti | 🕓 |
| وجه ، وجوه | vech, vücûh | vecih, vecihler (yorum yolları) | "yedi vecih üzre" → "yedi şekilde yorumlanır" | 🕓 |
| قرينة | karîne | ipucu | Tabircinin anlama geçtiği işaret | 🕓 |

## 3. Rüya türleri (docs/05, Katman 1)

| Terim | Kod (`RuyaTuru`) | Kısa tanım |
|---|---|---|
| Rahmânî (sâdık) rüya | `rahmani` | Müjde ya da uyarı içeren rüya |
| Şeytânî rüya (adgâs-ı ahlâm) | `seytani` | Korkutucu ve karışık; gelenekte tabir edilmez, anlatılmaz |
| Nefsânî rüya | `nefsani` | Günlük kaygıların yansıması |

## 4. Anlam türetme yolları (docs/05, Katman 4 · `Madde.yontem` etiketleri)

| Etiket | Türkçe ad | Örnek |
|---|---|---|
| `ayet` | Ayetten tabir | Kur'an'daki bir teşbihe dayanan yorum |
| `hadis` | Hadisten tabir | |
| `mesel` | Meselden (atasözü, deyim) tabir | |
| `kok` | Kelime kökünden tabir | Sembolün adının kökündeki anlamdan |
| `zit` | Zıddıyla tabir | Ölüm = uzun ömür, ağlamak = sevinç |
| `ebced` | Ebced hesabıyla tabir | |

## 5. Çeviri kuralları

- Anlam korunur, süsleme eklenmez. Kehanet tonunu yumuşatmak çevirinin değil sentezin işidir (docs/07, D1): çeviri aslına sadık kalır.
- Ayet alıntıları `[Ayet: Sure adı sure:ayet]`, hadisler `[Hadis]` ile işaretlenir.
- "صلى الله عليه وسلم" → "(s.a.v.)", "رضي الله عنه" → "(r.a.)".
- Özel adlar Türkçedeki yerleşik yazımıyla: Nablusî, İbn Sîrîn, Yûsuf.
- Emin olunmayan kelime için tahmin yapılmaz: `[?: <aslı>]` biçiminde bırakılır, madde `gozden_gecirildi: false` kalır.

## 6. İngilizce kaynaklar (Miller, Freud)

| İngilizce | Karşılık | Not |
|---|---|---|
| denotes, signifies | "… anlamına gelir", "…ya işaret eder" | |
| foretells, portends | "… habercisi sayılır" | Aslına sadık; sentezde "olarak yorumlanır"a çevrilir |
| For a young woman to dream … | "Genç bir kadın rüyasında … görürse" | Koşul: `cinsiyet=kadin`, `medeni_hal=bekar` (Miller'da "young woman" çoğunlukla bekâr) 🕓 |
| dream-work, latent content, manifest content | rüya çalışması, gizil içerik, açık içerik | Freud terimleri |
