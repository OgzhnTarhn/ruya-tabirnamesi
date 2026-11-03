# 02 · Veri Kaynakları ve Veri Şeması

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Kaynakların telif ve lisans ayrıntıları için araştırma raporuna bak: `docs/arastirma/`.

## 1. Seçilen kaynaklar

| Öncelik | Kaynak | Dil | Lisans | Neden | Aşama |
|---|---|---|---|---|---|
| 1 | Nablusi, *Ta'tîrü'l-enâm* (OpenITI, Shamela0001217) | Arapça | CC BY-NC-SA 4.0 | İslami tabirin çekirdek ve alfabetik sözlüğü | 0 |
| 1 | Miller, *Ten Thousand Dreams Interpreted* (Gutenberg #926) | İngilizce | Kamu malı | En büyük Batı sembol sözlüğü, temiz yapı | 0 |
| 2 | İbn Sirin'e atfedilen *Muntahab* (OpenITI, Shamela0021615) | Arapça | CC BY-NC-SA 4.0 | İkinci İslami ses; bab (konu) düzeninde | 3 |
| 2 | Freud, *Interpretation of Dreams* (Brill 1913, Gutenberg #66048) | İngilizce | Kamu malı | Psikanalitik "yöntem" katmanı | 2 |
| 3 | *Zhougong Jiemeng* (zh.wikisource) | Klasik Çince | Kamu malı / CC BY-SA | Üçüncü bir kültür | 4 (isteğe bağlı) |
| 3 | Talmud Berakhot 55a–57b (Sefaria, Davidson) | İngilizce | CC BY-NC | Yahudi geleneği | 4 (isteğe bağlı) |
| Okuma | TDV İA "Rüya" ve "Tâbirnâme", Balaban 2014, Elbir & Uludüz 2019 | Türkçe | Telifli | Yorum kurallarını çıkarmak için. **Korpusa girmez.** | 0 |

**Kesinlikle girmeyecekler:** Türkçe Nablusi ve İbn Sirin çevirileri, Jung'un eserleri, Freud'un modern Türkçe çevirileri, rüya siteleri ve gazete sayfaları, lisansı belirsiz tezler.

## 2. Gerçek veride ne gördük? (21 Ekim 2026'daki ön inceleme)

Dosyalar indirildi ve yapıları incelendi. Kod yazılmadı. Bulgular veri tasarımını doğrudan etkiliyor.

### Nablusi (OpenITI)

- **Boyut:** 2,37 MB, 21.759 satır. Harekesiz Arapça.
- **Başlık:** `#META#` satırlarında künye bilgisi var. Yayınevi: Dâru'l-Fikr, Beyrut.
- **Bölümler:** `### | باب الألف` biçiminde 29 bölüm var: mukaddime, 28 harf babı ve hatime. Alfabetik sıra korunmuş.
- **Maddeler:** Her paragraf `# - (` ile başlıyor. Toplam **5.746 paragraf** var ve bunlar iki türe ayrılıyor:
  - **Yaklaşık 2.400 başlıklı madde.** Örnekler: `# - (الله تعالى)`, `# - (أخ الإنسان)`, `# - (فراش)`. Parantezin içindeki kelime sembolün kendisi.
  - **Yaklaşık 3.300 alt paragraf.** Bunlar `# - (ومن رأى)` ("ve kim görürse") gibi kalıplarla başlıyor. Çoğu bir önceki başlığın alt durumu, ama bazıları **yeni bir sembol** getiriyor. Örneğin peygamberler maddesinin altında `(ومن رأى) إبراهيم` geçiyor. Hangi sembole ait olduklarını kural tabanlı bir ayrıştırıcı bulamaz. **LLM ile sembol ataması gerekecek.**
- **Gürültü:** Satır devamları `~~` ile işaretli. Sayfa işaretleri (`# PageV01P009`) ve el yazması kilometre taşları (`ms008`) var. Bunların hepsi temizlenmeli. Sayfa numarası da `konum` alanı için saklanmalı.
- **Uzunluk:** Paragraf başına ortalama yaklaşık 3,8 satır. Ama bazı maddeler çok uzun. Örneğin "Allah'ı görmek" maddesi 40 satırdan fazla. Uzun maddelerin cümle sınırlarından bölünmesi gerekecek.
- **Koşullu yapı doğrulandı.** Metinde "وإن رآه ضال اهتدى" (sapkın görürse hidayete erer) ve "وإن رآه مظلوم انتصر" (mazlum görürse zafer bulur) gibi kalıplar sürekli geçiyor. [05-yorum-yontemi.md](05-yorum-yontemi.md)'deki koşul modeli gerçek veriyle uyumlu.

### Miller (Gutenberg #926)

- **Boyut:** 0,94 MB, 25.875 satır. Asıl metin `*** START/END OF THE PROJECT GUTENBERG EBOOK ***` işaretlerinin arasında.
- **Maddeler:** `_Abbey_.` ya da `_Sea_.[198]` biçiminde **2.256 madde başlığı** var. Tek bir düzenli ifadeyle (regex) yakalanabiliyor: `^_[^_]+_\.(\[\d+\])?$`. Köşeli parantezdeki sayı bir dipnot işareti.
- **Koşullu yapı:** 513 paragraf "For a young woman…" ya da "For a man…" gibi kalıplarla başlıyor. Yani Miller'da da cinsiyete ve duruma bağlı yorumlar var. Koşul modeli bu kaynakta da işe yarayacak.
- **Gürültü:** Kitabın başında uzun bir önsöz ve kuram bölümü var (yaklaşık 1.540. satıra kadar). Bu bölüm madde değil, ayıklanacak.
- **Dikkat:** Miller'ın Ocean, Sea, Serpents ve Snakes gibi birbirine yakın başlıkları ayrı maddeler. Eşleme tablosunda bunlar aynı `symbol_id`'ye bağlanacak.

### Bu bulguların sonucu

1. Nablusi'yi ayrıştırmak sanıldığından zor ama yapılabilir. Başlıklı maddeler kurallarla, alt paragraflar LLM ile ayrıştırılacak.
2. Miller kolay. Aşama 0'ın ilk günü bitebilir.
3. **Hâlâ cevapsız tek kritik soru çeviri kalitesi.** Hafta 1'deki deneme bunu ölçecek (bkz. [08-yol-haritasi-takvim.md](08-yol-haritasi-takvim.md)).

## 3. Veri işleme hattı

Bütün veri repodaki `data/` klasöründe durur (bkz. [11-calisma-ortami.md](11-calisma-ortami.md)). Aşağıdaki yollar repo köküne göredir.

```
data/raw/            Ham dosyalar (indirildiği gibi, değiştirilmez)
   │  ingest/<kaynak>.py      ← kurallarla ayrıştırma, temizlik
   ▼
data/interim/<kaynak>.jsonl  Paragraf başına bir kayıt (asıl dil)
   │  enrich/assign_symbols.py   ← alt paragraflara sembol atama (LLM)
   │  enrich/translate.py        ← Türkçe çeviri (LLM, eşzamanlı istekler)
   │  enrich/conditions.py       ← koşul ayrıştırma (LLM, Aşama 3)
   ▼
data/processed/entries.jsonl  Zenginleştirilmiş, son kayıtlar
   │  index/build_symbols.py  ← sözlük + maddelerden arama tabloları (bellekte, diske yazılmaz)
   │  index/build_vectors.py  ← Chroma (Aşama 2)
   ▼
data/index/  chroma/ (Aşama 2)

(git) sozluk/symbols.json   ← elle onaylanan sembol indeksi repoda durur
```

Her dosyayı kimin ürettiği ve kimin okuduğu: [12-kod-yapisi-ve-sozlesmeler.md](12-kod-yapisi-ve-sozlesmeler.md), bölüm 5.

Veri git'e **eklenmez**: `data/` `.gitignore`'da. Bunun üç nedeni var: lisans (SA ve NC koşulları), dosya boyutu ve kendi rüyaların. Ham veriyi `scripts/download_sources.py` `data/raw/` altına indirir.

## 4. Veri şeması

### 4.1 `entries.jsonl`: madde kaydı (her satır bir JSON)

```json
{
  "entry_id": "nablusi:004310",
  "kaynak": "nablusi",
  "eser": "Ta'tîrü'l-enâm fî ta'bîri'l-menâm",
  "yazar": "Abdülganî en-Nablusî",
  "gelenek": "islami_klasik",
  "dil": "ar",
  "lisans": "CC-BY-NC-SA-4.0",
  "atif_notu": null,
  "konum": {"bab": "باب الحاء", "sayfa": "V01P142", "satir": 4310},
  "baslik_asli": "حية",
  "sembol_ar": "حية",
  "sembol_tr": "yılan",
  "ust_madde_id": null,
  "symbol_ids": ["yilan"],
  "metin_asli": "…",
  "metin_tr": "…",
  "ceviri": {"yontem": "llm", "model": "claude-code+evren", "tarih": "2026-11-02", "gozden_gecirildi": false},
  "kosullar": [
    {"kosul": {"renk": "siyah"}, "yorum_tr": "…", "otorite": "Nablusi"}
  ],
  "yontem": null,
  "kapsam": "kisi"
}
```

Alan kuralları:

- `entry_id` sabittir ve yeniden ayrıştırmada değişmez. Kimlik paragrafın sırasından değil, kaynak satır numarasından türetilir: `<kaynak>:<6 haneli satır no>`, örneğin `nablusi:004310`.
- **Bu yüzden ham kaynak sabitlenir.** Ham dosyada tek bir satır değişirse bütün kimlikler kayar. Bu durumda test setindeki `beklenen_maddeler` ve LLM ile yapılmış sembol atamaları yanlış maddeleri gösterir.
  - OpenITI adresleri `master` dalını değil, belirli bir commit'i gösterir (`ingest/kaynaklar.py`, [KAYNAKLAR.md](KAYNAKLAR.md)).
  - Gutenberg adresleri sabitlenemez. Her kaynağın beklenen SHA256 özeti `KaynakBilgisi.sha256` alanına ilk indirmeden sonra yazılır. Özet uyuşmazsa `download_sources.py` dosyayı yazmaz ve hata verir.
  - Kaynağın yeni sürümüne geçmek bilinçli bir iştir: adres ve özet değişir, `entries.jsonl` yeniden üretilir, test setindeki `beklenen_maddeler` gözden geçirilir.
- Bilinmeyen alan kabul edilmez. Kodda şema `ruya.schemas.Madde`; alan eklenecekse önce bu belge, sonra şema güncellenir.
- `atif_notu` alanı İbn Sirin kayıtlarında `"Nispeti sahih değil (OpenITI metadatası)"` değerini alır.
- `ust_madde_id` alt paragrafları başlıklı maddelerine bağlar.
- `kosullar`, `yontem` ve `kapsam` alanları Aşama 3'te doldurulur. O zamana kadar `null` kalır.
- `lisans` hiçbir zaman boş olamaz. Şema boş bırakılırsa hata verir; kodlar [KAYNAKLAR.md](KAYNAKLAR.md), bölüm 5'te.
- `yontem` bir etiket listesidir (`["zit"]` gibi; bkz. [terimler.md](terimler.md), bölüm 4).

### 4.2 `symbols.json`: kanonik sembol indeksi

> **Konum: git'te, `sozluk/symbols.json`.** Bu dosya veri setinin kendisi değil. Senin elle onayladığın bir sözlük. Değişiklikleri sürümlenmeli ve commit geçmişinde görünmeli. İçinde yalnızca kelimeler ve eşlemeler var, lisanslı metin yok. Kod bu dosyayı doğrudan repodan okur.

```json
{
  "yilan": {
    "ad_tr": "yılan",
    "varyantlar_tr": ["yılan", "engerek", "kobra", "piton"],
    "ar": ["حية", "ثعبان", "أفعى"],
    "en": ["snake", "snakes", "serpent", "serpents"],
    "bab_kategorisi": "hayvanlar",
    "hvdc_kategorisi": "hayvan",
    "ilgili": ["ejderha", "solucan"],
    "gozden_gecirildi": true
  }
}
```

- `symbol_id` her zaman ASCII ve küçük harfli olur, örneğin `yilan` ve `olmus_baba`. Böylece dosya adlarında ve sorgularda Türkçe karakter sorunu yaşanmaz.
- **İlk sürüm 50 sembol olacak.** Liste, test setindeki rüyalarda en sık geçen sembollerden seçilecek. Bir LLM önerecek, sen gözden geçirip onaylayacaksın. `gozden_gecirildi: true` olmayan sembol MVP'de kullanılmaz.
- Bab kategorileri Elbir & Uludüz 2019'daki 53 babdan sadeleştirilecek. HVDC kategorileri Hall & Van de Castle'ın 10 kategorisinden alınacak.

### 4.2b Hibrit getirme alanları (3 Kasım)

`Madde` değişmez. `Sembol.hyde: str | None` (yalnızca arama için varsayımsal madde) ve `Aday.pasaj: str | None` (aramayı kazanan parça) eklenir. Ayrıntı: [13](13-hibrit-getirme.md).

### 4.3 Test seti şeması

Ayrıntılar için bkz. [06-degerlendirme.md](06-degerlendirme.md).

## 5. Çeviri stratejisi

- **Ne çevrildi:** Dört kaynağın tamamı, 2 Kasım 2026'da bitti: Nablusi 5.782, Miller 2.256, İbn Sîrîn 1.544, Freud 1.219 satır. Freud yalnızca önsözler ve yedi ana bölümdür; içindekiler, kaynakça ve dizin çevrilmedi.
- **Nasıl:** EVREN tek istekte çok yavaş olduğu için çeviri çevrimdışı ve parça parça yapıldı: önce Claude Code ajanları (Miller'in tamamı, Nablusi'nin çoğu, İbn Sîrîn'in ilk parçası), kullanım sınırı nedeniyle sonra orkestra ile EVREN agent'ları (`deepseek-v4.1-flash`, zaman zaman `mimo-v2.6-pro`). Çıktılar `data/interim/ceviri/<kaynak>/parca_NNNN.jsonl` altındadır; `enrich/ceviri_birlestir.py` bunları maddelere işler. Kalite parçadan parçaya değişebilir, bu yüzden `ceviri.model` karma etiket taşır (`claude-code+evren`) ve `gozden_gecirildi` varsayılan olarak `false` kalır.
- **Uyarı:** İlk EVREN turunda agent'lar uzun paragrafları yarıda bırakıp `[metin burada kesiliyor]` yazarak gevşek denetimden geçti. Yarım satırlar uzunluk oranı denetimiyle bulunup yeniden çevrildi. Yeni toplu işlerde bu denetim sıkı tutulmalı.
- **Çeviri yönergeleri:**
  - Anlamı koru, süsleme ekleme.
  - Ayet ve hadis alıntılarını işaretle.
  - Osmanlı tabir terminolojisini tutarlı kullan. Bunun için bir terim sözlüğü dosyası tutulacak (`docs/terimler.md`): رؤيا = rüya, تعبير = tabir, أضغاث أحلام = adgâs-ı ahlâm…
- **Kalite kontrolü:** Her partiden rastgele 10 madde elle okunacak. Sorunlu maddeler `gozden_gecirildi: false` olarak kalacak.
- **Gerçek kullanım:** EVREN tarafında yaklaşık 8 saat sürdü. Yeni bir kaynak eklenirse aynı yol izlenir; EVREN modelleri 1 Aralık 2026'ya kadar ücretsizdir.
