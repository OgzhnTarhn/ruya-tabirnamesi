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

Bütün veri **Google Drive**'da, `MyDrive/ruya-tabirnamesi/` altında durur. Bilgisayara inmez. İşleri Colab notebook'ları çalıştırır (bkz. [11-calisma-ortami-colab-drive.md](11-calisma-ortami-colab-drive.md)). Aşağıdaki yollar bu Drive klasörüne göredir.

```
data/raw/            Ham dosyalar (indirildiği gibi, değiştirilmez)
   │  ingest/<kaynak>.py      ← kurallarla ayrıştırma, temizlik
   ▼
data/interim/<kaynak>.jsonl  Paragraf başına bir kayıt (asıl dil)
   │  enrich/assign_symbols.py   ← alt paragraflara sembol atama (LLM)
   │  enrich/translate.py        ← Türkçe çeviri (LLM, Batch API)
   │  enrich/conditions.py       ← koşul ayrıştırma (LLM, Aşama 3)
   ▼
data/processed/entries.jsonl  Zenginleştirilmiş, son kayıtlar
   │  index/build_symbols.py  ← kanonik sembol indeksi
   │  index/build_vectors.py  ← Chroma (Aşama 2)
   ▼
data/index/  symbols.json + chroma.zip (Chroma, Colab'in yerel diskinde açılır)
```

Veri git'e **eklenmez**. Repoda bir `data/` klasörü bile bulunmaz; `.gitignore` yalnızca önlem olarak duruyor. Bunun üç nedeni var: lisans (SA ve NC koşulları), dosya boyutu ve kendi rüyaların. Ham veriyi `01_kaynaklari_indir.ipynb` (içinde `scripts/download_sources.py`) Colab'den doğrudan Drive'a indirir.

## 4. Veri şeması

### 4.1 `entries.jsonl`: madde kaydı (her satır bir JSON)

```json
{
  "entry_id": "nablusi:0412",
  "kaynak": "nablusi",
  "eser": "Ta'tîrü'l-enâm fî ta'bîri'l-menâm",
  "yazar": "Abdülganî en-Nablusî",
  "gelenek": "islami_klasik",
  "dil": "ar",
  "lisans": "CC-BY-NC-SA-4.0",
  "atif_notu": null,
  "konum": {"bab": "باب الحاء", "sayfa": "V01P142", "satir": 4310},
  "baslik_asli": "حية",
  "ust_madde_id": null,
  "symbol_ids": ["yilan"],
  "metin_asli": "…",
  "metin_tr": "…",
  "ceviri": {"yontem": "llm", "model": "claude-opus-5-5", "tarih": "2026-11-05", "gozden_gecirildi": false},
  "kosullar": [
    {"kosul": {"renk": "siyah"}, "yorum_tr": "…", "otorite": "Nablusi"}
  ],
  "yontem": null,
  "kapsam": "kisi"
}
```

Alan kuralları:

- `entry_id` sabittir ve yeniden ayrıştırmada değişmez. Kimlik paragrafın sırasından değil, kaynak satır numarasından türetilir.
- `atif_notu` alanı İbn Sirin kayıtlarında `"Nispeti sahih değil (OpenITI metadatası)"` değerini alır.
- `ust_madde_id` alt paragrafları başlıklı maddelerine bağlar.
- `kosullar`, `yontem` ve `kapsam` alanları Aşama 3'te doldurulur. O zamana kadar `null` kalır.
- `lisans` hiçbir zaman boş olamaz. Doğrulama betiği boş bırakılırsa hata verir.

### 4.2 `symbols.json`: kanonik sembol indeksi

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

### 4.3 Test seti şeması

Ayrıntılar için bkz. [06-degerlendirme.md](06-degerlendirme.md).

## 5. Çeviri stratejisi

- **Ne çevrilecek:** Önce yalnızca 50 sembole ait maddeler çevrilecek, bunlar yaklaşık birkaç yüz paragraf. Tüm korpus Aşama 2'de çevrilecek.
- **Nasıl:** Claude ile, Message Batches API üzerinden. Batch API toplu işlerde %50 indirimli ve sonuçlar 24 saat içinde geliyor.
- **Çeviri yönergeleri:**
  - Anlamı koru, süsleme ekleme.
  - Ayet ve hadis alıntılarını işaretle.
  - Osmanlı tabir terminolojisini tutarlı kullan. Bunun için bir terim sözlüğü dosyası tutulacak (`docs/terimler.md`): رؤيا = rüya, تعبير = tabir, أضغاث أحلام = adgâs-ı ahlâm…
- **Kalite kontrolü:** Her partiden rastgele 10 madde elle okunacak. Sorunlu maddeler `gozden_gecirildi: false` olarak kalacak.
- **Maliyet (kaba tahmin, ölçülecek):**
  - Bütün Nablusi korpusunu Batch API ile çevirmek yaklaşık 0,5 milyon girdi ve 0,7 milyon çıktı tokenı tutar. Bu, Opus 5.5 ile yaklaşık 8–15 $, Haiku 5.5 ile 1 $'ın altında demek.
  - 50 sembollük ilk parti birkaç sent tutar.
  - Gerçek sayılar `count_tokens` ile ölçülüp bu belgeye işlenecek.
