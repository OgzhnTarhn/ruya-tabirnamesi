# Kaynaklar ve Lisanslar

> Durum: v0.1 · Tarih: 23 Ekim 2026
> Atıf yükümlülüğü (CC BY) gereği her kaynağın künyesi ve lisansı burada tutulur (docs/07, V9).
> Koddaki karşılığı: `src/ruya/ingest/kaynaklar.py`. İkisi her zaman birlikte güncellenir.
> **[DOĞRULANACAK]** etiketli bilgiler araştırmada birincil kaynaktan teyit edilemedi; elle kontrol edilince etiket silinir.

## 1. Korpus kaynakları

Bu metinler ayrıştırılıp `entries.jsonl`'e girer. Veri yalnızca Google Drive'da durur, git'e eklenmez.

### 1.1 Nablusi · *Ta'tîrü'l-enâm fî ta'bîri'l-menâm* (Aşama 0)

| Alan | Değer |
|---|---|
| Yazar | Abdülganî en-Nablusî (ö. 1143/1731) |
| Eser | *Ta'tîrü'l-enâm fî ta'bîri'l-menâm*; 1684'te alfabetik düzenle yazılmış |
| Dijital metin | OpenITI, `1143CabdGhaniNabulusi.TactirAnam.Shamela0001217-ara1` (2.371.805 bayt) |
| Baskı (metadataya göre) | Dâru'l-Fikr, Beyrut |
| Adres | [OpenITI ham dosya](https://raw.githubusercontent.com/OpenITI/1150AH/master/data/1143CabdGhaniNabulusi/1143CabdGhaniNabulusi.TactirAnam/1143CabdGhaniNabulusi.TactirAnam.Shamela0001217-ara1) |
| Lisans | Eser kamu malı; OpenITI derlemesi **CC BY-NC-SA 4.0** · kod: `CC-BY-NC-SA-4.0` |
| Koşullar | Ticari olmayan kullanım, atıf, türetilen çeviriler paylaşılırsa aynı lisansla (V6) |

### 1.2 Miller · *Ten Thousand Dreams Interpreted* (Aşama 0)

| Alan | Değer |
|---|---|
| Yazar | Gustavus Hindman Miller (ö. 1929) |
| Eser | *Ten Thousand Dreams Interpreted* (1901) |
| Dijital metin | Project Gutenberg #926 |
| Adres | [gutenberg.org/ebooks/926](https://www.gutenberg.org/ebooks/926) · [düz metin](https://www.gutenberg.org/cache/epub/926/pg926.txt) |
| Lisans | Kamu malı · kod: `PD` |
| Koşullar | Gutenberg başlık ve dipnot bölümleri silinir; metadataya `Project Gutenberg #926` yazılır (V5). Toplu ve otomatik indirme yapılmaz. |

### 1.3 Freud · *The Interpretation of Dreams* (Aşama 2)

| Alan | Değer |
|---|---|
| Yazar | Sigmund Freud; çeviren A. A. Brill |
| Eser | *The Interpretation of Dreams* (Brill çevirisi, 1913) |
| Dijital metin | Project Gutenberg #66048 |
| Adres | [gutenberg.org/ebooks/66048](https://www.gutenberg.org/ebooks/66048) |
| Lisans | Kamu malı · kod: `PD` · **[DOĞRULANACAK]** Brill'in ölüm yılı (Türkiye'deki koruma süresi çevirmene göre işler) |
| İsteğe bağlı | Almanca asıl: *Die Traumdeutung* (1914, 4. baskı), [Gutenberg #40739](https://www.gutenberg.org/ebooks/40739) |

### 1.4 İbn Sîrîn'e atfedilen · *Muntahabü'l-kelâm fî tefsîri'l-ahlâm* (Aşama 3)

| Alan | Değer |
|---|---|
| Yazar | İbn Sîrîn'e (ö. 110/728) **atfedilen**; nispeti sahih değil |
| Dijital metin | OpenITI, `0110IbnSirin.MuntakhabKalamFiTafsirAhlam.Shamela0021615-ara1` (~794 bin karakter) |
| Adres | [OpenITI ham dosya](https://raw.githubusercontent.com/OpenITI/0125AH/master/data/0110IbnSirin/0110IbnSirin.MuntakhabKalamFiTafsirAhlam/0110IbnSirin.MuntakhabKalamFiTafsirAhlam.Shamela0021615-ara1) |
| Lisans | **CC BY-NC-SA 4.0** · kod: `CC-BY-NC-SA-4.0` |
| Atıf notu | Her kayıtta `atif_notu = "Nispeti sahih değil (OpenITI metadatası)"`; yanıtta "İbn Sirin'e atfedilen *Muntahab*'a göre (nispeti tartışmalı)" (İG-34, D6) |

### 1.5 OpenITI derlemesinin kendisi

| Alan | Değer |
|---|---|
| Kayıt | OpenITI, Zenodo, sürüm 2025.1.9 (30 Aralık 2025) |
| DOI | [10.5281/zenodo.17767721](https://zenodo.org/records/17767721) |
| Lisans | CC BY-NC-SA 4.0 · **[DOĞRULANACAK]** Hafta 0'da elle kontrol et (docs/10, bölüm 6) |
| Önerilen atıf | **[DOĞRULANACAK]** Zenodo kaydındaki "Cite as" metnini buraya aynen kopyala |

## 2. İsteğe bağlı kaynaklar (Aşama 4 sonrası)

| Kaynak | Dil | Lisans | Adres | Not |
|---|---|---|---|---|
| *Zhougong Jiemeng* (周公解夢) | Klasik Çince | Alt metin kamu malı; Wikisource transkripsiyonu CC BY-SA 4.0 | [zh.wikisource](https://zh.wikisource.org/zh-hant/%E5%91%A8%E5%85%AC%E8%A7%A3%E5%A4%A2) | ~900 kısa madde, 27 bölüm |
| Talmud, Berakhot 55a–57b | İngilizce | William Davidson Edition: CC BY-NC | [Sefaria API](https://www.sefaria.org/api/v3/texts/Berakhot.55a?version=english) | Lisans sürüm bazında API'de döner |
| DreamBank rüya raporları | İngilizce | CC BY-NC-SA 4.0 (HF aynasındaki "Apache-2.0" asıl lisansla çelişiyor; asıl lisansa uyulur) | [dreambank.net](https://dreambank.net/) | Yalnızca test seti için; korpusa girmez |

## 3. Okuma kaynakları (korpusa girmez)

Bu eserler telifli. Yalnızca yorum kurallarını tasarlamak için okunur; metinleri korpusa ya da talimatlara kopyalanmaz. Öğrenilenler `docs/kurallar.md`'ye kendi cümlelerinle yazılır (V3, V4).

- İlyas Çelebi ve Süleyman Uludağ, "Rüya", *TDV İslâm Ansiklopedisi*, c. 35 (2008), s. 306–309. [islamansiklopedisi.org.tr/ruya](https://islamansiklopedisi.org.tr/ruya) · **[DOĞRULANACAK]** cilt bilgisi (Balaban 2014'te c. 20 ve c. 35 birlikte geçiyor)
- Orhan Şaik Gökyay ve Vildan S. Coşkun, "Tâbirnâme", *TDV İslâm Ansiklopedisi*. [islamansiklopedisi.org.tr/tabirname](https://islamansiklopedisi.org.tr/tabirname) · **[DOĞRULANACAK]** cilt ve sayfa
- Adem Balaban, "Türkçe Yazma Tabirnameler", *Dil ve Edebiyat Eğitimi Dergisi* 9 (2014), s. 112–132. [PDF](https://turkoloji.cu.edu.tr/pdf/adem_balaban_turkce_yazma_tabirnameler.pdf)
- Elbir ve Uludüz (2019): bir İbn Sîrîn tercümesinin 53 babı ve iki nüsha karşılaştırması. [DergiPark](https://dergipark.org.tr/tr/download/article-file/3169759) · **[DOĞRULANACAK]** tam künye (başlık, dergi, sayı, sayfa)
- Hall ve Van de Castle'ın içerik çözümleme sistemi (HVDC): `hvdc_kategorisi` için 10 kategori. **[DOĞRULANACAK]** künye

## 4. Kesinlikle kullanılmayacaklar

Türkçe Nablusi ve İbn Sirin çevirileri, Jung'un eserleri, Freud'un modern Türkçe çevirileri, rüya siteleri ve gazete sayfaları, lisansı belirsiz tezler (docs/02, bölüm 1; docs/07, V2–V3).

## 5. Lisans kodları

| Kod | Anlamı | Ticari kullanım | Paylaşımda |
|---|---|---|---|
| `PD` | Kamu malı | Serbest | Atıf iyi pratik |
| `CC-BY-NC-SA-4.0` | Atıf, ticari olmayan, aynı lisansla paylaş | **Yasak** | Aynı lisans, atıf |
| `CC-BY-NC-4.0` | Atıf, ticari olmayan | **Yasak** | Atıf |
| `CC-BY-SA-4.0` | Atıf, aynı lisansla paylaş | Serbest | Aynı lisans, atıf |

Proje ticarileşirse `NC` içeren bütün kayıtlar `lisans` alanına göre tek filtreyle çıkarılır (V8, İOG-06).
