# Teknik Rehber: Sistemi nasıl kuracağız?

> Tarih: 31 Ekim 2026 · Takvimde: Hafta 1'in sonu
> Bu belge projeye teknik olarak hâkim olman için yazıldı: sistemin parçaları nasıl çalışacak, hangi teknik neden seçildi, her hafta kodda tam olarak ne yazılacak. Ayrıntıların asıl kaynakları: [03 · mimari](03-mimari.md), [04 · teknoloji](04-teknoloji-secimi.md), [12 · kod yapısı](12-kod-yapisi-ve-sozlesmeler.md), [02 · veri](02-veri-kaynaklari-ve-semasi.md), [06 · ölçme](06-degerlendirme.md).

---

## 1. Büyük resim: iki ayrı dünya

Sistem birbirinden bağımsız iki parçadan oluşuyor.

| | Çevrimdışı: veri hattı | Çevrimiçi: sorgu boru hattı |
|---|---|---|
| Ne zaman çalışır | Bir kez (kaynak eklenince yeniden) | Her rüyada |
| Ne yapar | Ham kitapları ayrıştırır, sembol atar, çevirir, indeksler | Rüyadan sembol çıkarır, maddeleri getirir, yorum yazar |
| Süre ve kota | Saatler, birkaç milyon token (eşzamanlı istekler) | İki LLM çağrısı; servisin yoğunluğuna göre saniyeler ile bir iki dakika arası |
| Kod | `ingest/`, `enrich/`, `index/` | `pipeline/` |
| Çıktı | `entries.jsonl` (madde deposu) | `SorguKaydi` (yorum + ölçümler) |

```
ÇEVRİMDIŞI (bir kez)                                  ÇEVRİMİÇİ (her rüya)
                                                       
data/raw/nablusi.txt ─┐                               "Rüyamda siyah bir yılan gördüm"
data/raw/miller.txt  ─┤                                        │
                      ▼                                        ▼
               ingest/ (regex)                        1. extract   (DeepSeek, JSON)
                      ▼                                        ▼
         data/interim/*.jsonl                         2. map       (sözlük + zeyrek)
                      ▼                                        ▼
     enrich/ (DeepSeek: sembol, çeviri)     ───────► 3. retrieve  (symbol_id ile)
                      ▼                                        ▼
       data/processed/entries.jsonl ─────────────────► 4. synthesize (DeepSeek, atıflı)
                                                               ▼
       sozluk/symbols.json (git, elle onaylı) ───────►      Yorum + uyarı
```

**Kural:** Sorgu kodu (`pipeline/`) veri hattı kodunu (`ingest/`, `enrich/`) asla içe aktarmaz; yalnızca onun ürettiği dosyaları okur. Bu kuralı `tests/test_mimari.py` denetliyor.

---

## 2. Neden "önce sözlük, sonra vektör"?

Klasik RAG şöyle çalışır: soruyu vektöre çevir, en benzer metin parçalarını bul, LLM'e ver. Bizim problemimiz farklı. Rüya tabiri bir **sözlükte sembol arama** problemi. Kullanıcı "yılan" dediğinde bize "yılana benzeyen metinler" değil, **yılan maddesi** lazım.

Bu yüzden ana yol **kesin eşleme**:

```
"yılan" ──► symbols.json ──► symbol_id = "yilan" ──► yilan etiketli bütün maddeler
```

Vektör arama yalnızca sözlükte bulunamayan semboller için **yedek** (Aşama 2). Örneğin kullanıcı "piton" yazdı ama sözlükte yalnızca "yılan" varsa, vektör benzerliği bunu yakalayabilir.

**Sonuç:** Asıl iş kodda değil, verinin hazırlanmasında: her maddeye doğru `symbol_id`'yi atamak ve sözlüğü iyi kurmak.

---

## 3. Teknoloji yığını

| Parça | Seçim | Neden |
|---|---|---|
| Dil | Python ≥3.11 | uv ile kurulur |
| Paketler | `pyproject.toml` + **uv** | Tek bağımlılık kaynağı; `uv.lock` kurulumu tekrarlanabilir kılar |
| LLM | **EVREN LLM geçidi**, `deepseek-v4.1-flash` (`httpx` ile) | OpenAI uyumlu API, JSON şeması; 1 Aralık 2026'ya kadar ücretsiz, günde 15 milyon token. Claude API kullanılamadığı için seçildi (TK-03) |
| Veri doğrulama | **Pydantic v2**, `extra="forbid"` | Yanlış yazılmış alan adı sessizce kaybolmaz, hata verir |
| Ayarlar | **pydantic-settings**, `RUYA_` önekli ortam değişkenleri | `.env` dosyası yok, gizli bilgi diske yazılmaz |
| Türkçe kök bulma | **zeyrek** | Java gerektirmez; "yılanlar" → "yılan" |
| Embedding (Aşama 2) | `intfloat/multilingual-e5-large` | Türkçe sorgu ↔ Arapça/İngilizce metin, diller arası arama |
| Vektör deposu (Aşama 2) | **Chroma** (`PersistentClient`) | Sunucusuz; `where={"symbol_id": ...}` filtresi var |
| Reranker (Aşama 2) | `BAAI/bge-reranker-v2-m3` | Bir sembolün çok maddesi varsa rüya cümlesine göre yeniden sıralar |
| Arayüz | **Gradio** (`gr.Blocks`) | Yerelde (`localhost`) açılır; `share=True` yasak |
| Kalite | pytest, ruff, nbstripout | Test, lint, notebook çıktısı temizliği |

**Bilerek kullanılmayanlar:** LangChain/LlamaIndex (öğrenmeyi gizler; atıf doğrulamasını kendimiz yazıyoruz), ajan yapısı (adımlar baştan belli), ayrı veritabanı sunucusu (~10 bin kayıt için gereksiz).

---

## 4. Veri hattı: kitaptan madde deposuna

### 4.1 İndirme (hazır)

`scripts/download_sources.py` kaynakları `data/raw/` klasörüne indirir ve her dosyanın SHA256 özetini `KAYNAK_OZETLERI.json`'a yazar.

**Neden özet ve commit sabitleme önemli?** Madde kimliği satır numarasından türüyor (`nablusi:004310` = 4310. satır). Kaynak dosyada tek bir satır eklenirse bütün kimlikler kayar, test setindeki "beklenen maddeler" yanlış maddeleri gösterir. Bu yüzden OpenITI adresleri belirli bir commit'e sabitli, Gutenberg dosyaları da özetle denetleniyor.

### 4.2 Ayrıştırma · `ingest/` (Hafta 2)

Her kaynak için bir ayrıştırıcı. Girdisi ham metin, çıktısı `Madde` listesi. Burada LLM yok, yalnızca regex ve kurallar var.

**Nablusi (OpenITI mARkdown biçimi):**

```
### | باب الحاء                       ← bab (bölüm) başlığı
# - (حية) يدل على عدو ...             ← yeni paragraf, parantez içi = başlık (yılan)
~~ وإن رآه مظلوم انتصر PageV01P142    ← devam satırı + sayfa işareti
# - (ومن رأى) حية سوداء ...           ← alt paragraf ("kim görürse ...")
```

Ayrıştırıcının işleri:
- `# - (` ile başlayan satır yeni paragraf, `~~` ile başlayan satır devam satırı.
- `PageV01P142` sayfa işaretini ve `ms008` el yazması işaretini metinden temizleyip sayfayı `konum` alanına yazmak. Dikkat: OpenITI'de işaret sayfayı **kapatır**, yani işaretten önceki metin o sayfaya aittir.
- Başlıklı maddeyi (`(حية)` → sembolün kendisi) alt paragraftan (`(ومن رأى)`) ayırmak.
- Alt paragrafı `ust_madde_id` ile başlıklı maddesine bağlamak.

Bunun ilk sürümü deneme notebook'unda yazıldı (`nablusi_paragraflari`). Hafta 2'de testleriyle birlikte `src/ruya/ingest/nablusi.py`'ye taşınacak.

**Miller (Gutenberg):** Çok daha kolay. `*** START/END ***` arasını al, `^_([^_]+)_\.(\[\d+\])?$` regex'iyle başlıkları yakala (`_Snakes_.`), aradaki paragrafları gövde yap.

**Türkçe normalleştirme · `text/turkce.py` (Hafta 2):** Python'da `"I".lower()` → `"i"` verir, Türkçede `"ı"` olmalı. `"İ".lower()` ise `"i̇"` (noktalı, iki karakter) verir. Kendi `kucuk_harf()` fonksiyonumuzu yazacağız: önce I→ı, İ→i, sonra `lower()`, ardından boşluk ve noktalama temizliği. Eşlemenin tamamı buna dayanıyor.

### 4.3 Zenginleştirme · `enrich/` (Hafta 3, 6, 8)

Burada LLM devreye giriyor, **toplu** olarak.

| İş | Ne yapar | Neden LLM |
|---|---|---|
| `assign_symbols.py` | Her paragrafa `symbol_ids` atar | Nablusi'nin ~3.300 alt paragrafından bazıları yeni sembol getiriyor; kuralla bulunamıyor |
| `translate.py` | `metin_asli` → `metin_tr` | Arapça/İngilizce → Türkçe; terim sözlüğü (`terimler.md`) talimata gömülü |
| `conditions.py` (Aşama 3) | "Kadın görürse …" kalıplarını `kosullar` alanına ayrıştırır | Serbest metinden yapı çıkarma |

**Toplu istekler (`LLMIstemcisi.toplu`):** Geçitte Batch API olmadığı için istekler eşzamanlı gönderilir (varsayılan 4 iş parçacığı). Akış şöyle:
1. İstekler hazırlanır; her birinin anahtarı `entry_id` olur.
2. `toplu(istekler)` her isteği `mesaj` üzerinden gönderir; her yanıt diske (`data/cache/llm/`) yazılır.
3. İş yarıda kesilirse (bilgisayar kapandı, kota doldu) yeniden başlatılır; önbellekteki istekler tekrar gönderilmez, iş kaldığı yerden sürer.
4. Tek bir isteğin hatası bütün işi durdurmaz; o anahtarın sonucu hata olarak döner, sonra yeniden denenir.

### 4.4 Madde kaydı: `entries.jsonl`

Veri hattının son ürünü. Her satır bir `Madde`:

```json
{
  "entry_id": "nablusi:004310",
  "kaynak": "nablusi", "gelenek": "islami_klasik", "dil": "ar",
  "lisans": "CC-BY-NC-SA-4.0",
  "konum": {"bab": "باب الحاء", "sayfa": "V01P142", "satir": 4310},
  "baslik_asli": "حية",
  "ust_madde_id": null,
  "symbol_ids": ["yilan"],
  "metin_asli": "…", "metin_tr": "…",
  "ceviri": {"yontem": "llm", "model": "…", "gozden_gecirildi": false},
  "kosullar": null, "yontem": null, "kapsam": null
}
```

`lisans` boş olamaz (hukuki zorunluluk). `kosullar` Aşama 3'e kadar `null` kalır.

### 4.5 Sembol sözlüğü: `sozluk/symbols.json`

Projenin kalbi. Git'te duruyor, çünkü senin **elle onayladığın** bir veri:

```json
"yilan": {
  "ad_tr": "yılan",
  "varyantlar_tr": ["yılan", "engerek", "kobra", "piton"],
  "ar": ["حية", "ثعبان", "أفعى"],
  "en": ["snake", "snakes", "serpent", "serpents"],
  "gozden_gecirildi": true
}
```

Yaşam döngüsü: LLM önerir → öneri `data/interim/` altına yazılır → sen okuyup `symbols.json`'a eklersin → `pytest` şemayı ve çakışmaları denetler → commit. Bir varyant iki sembolde birden geçerse test bunu hata olarak yakalar.

Oturum başında bu dosyadan bellekte iki tablo kurulur: **varyant tablosu** (`"engerek"` → `"yilan"`) ve **sembol → maddeler tablosu**. Diske yazılmaz; 150 sembol ve 10 bin madde için kurulumu bir saniyeden kısa sürer.

### 4.6 Vektör indeksi · `index/` (Aşama 2, Hafta 6)

- Her maddenin metni ve her sembolün adı/tanımı **multilingual-e5-large** ile 1024 boyutlu vektöre çevrilir (embedding modeli Aşama 2'de kesinleşir).
- **Önemli tuzak:** e5 modeli `query: ` ve `passage: ` önekleri ister. Unutulursa kalite sessizce düşer, hata da vermez.
- Vektörler Chroma'ya `symbol_id` metadata'sıyla yazılır.
- İndeks `data/index/chroma` altında kurulur ve diskte kalır; her çalıştırmada yeniden kurulmaz.

---

## 5. Sorgu boru hattı: bir rüyanın yolculuğu

Örnek girdi: *"Rüyamda denize girdim, sudan siyah bir yılan çıktı, çok korktum. Yılan beni ısırmadı."*

### Adım 1 · Çıkarım · `pipeline/extract.py` (Hafta 4)

Modele rüya verilir, **JSON şemasıyla** (`response_format` + `json_schema`, `strict: true`) yapılandırılmış çıktı istenir. Yanıt ayrıca Pydantic şemasıyla doğrulanır:

```json
{
  "semboller": [
    {"yalin": "deniz", "nitelikler": [], "eylem": "girdi", "olumsuz": false},
    {"yalin": "yılan", "nitelikler": ["siyah"], "eylem": "gördü", "duygu": "korku", "olumsuz": false},
    {"yalin": "ısırık", "olumsuz": true}
  ],
  "ruya_turu_ipucu": null
}
```

- `olumsuz: true` olan semboller ("ısırmadı") sonraki adımlara geçmez. Olumsuzlama testi tam olarak bunu ölçüyor.
- En fazla 8 sembol işlenir, fazlası listelenir.

### Adım 2 · Eşleme · `pipeline/map.py` (Hafta 4)

Her sembol için sırayla:
1. `kucuk_harf("Yılan")` → `"yılan"` → varyant tablosunda var mı? → **birebir**
2. Yoksa zeyrek ile kök bul ("yılanlar" → "yılan") ve tekrar ara → **kök**
3. Yoksa (Aşama 2) vektör yedeği: en yakın sembol, benzerlik eşiğin üstündeyse → **vektör**
4. Hiçbiri tutmazsa `symbol_id = None` → **yok** (yanıtta "kaynaklarda bulunamadı")

Çıktı: `Eslesme(sembol, symbol_id="yilan", yontem="birebir", guven=1.0)`. `yontem` hata ayıklama sekmesinde görünür; neyin neden eşleştiğini her zaman görebilirsin.

### Adım 3 · Getirme · `pipeline/retrieve.py` (Hafta 4)

`symbol_id="yilan"` için bütün maddeler alınır, sonra **kaynak başına en fazla N tane** (varsayılan N=2) seçilir. Böylece tek bir kaynak yanıtı domine etmez.

Sıralama ölçütleri:
1. **Nitelik eşleşmesi:** "siyah" niteliği `metin_tr` içinde geçen madde öne çıkar.
2. **Bağlam koşulu** (Aşama 3): kullanıcı "kadın" dediyse kadın koşullu yorum öne çıkar.
3. **Başlıklı madde** alt paragraftan önce gelir.

Çıktı `Aday` nesneleri: madde, skor ve gerekçe ("nitelik eşleşti: siyah"). Gerekçeler hata ayıklama sekmesinde görünür.

### Adım 4 · Sentez · `pipeline/synthesize.py` (Hafta 5)

Projenin en önemli teknik parçası **atıf doğrulama**. Maddeler modele numaralı kaynaklar olarak verilir:

```
[K1] nablusi:004310 · Nablusi · حية (yılan)
Yılan rüyada düşmanla yorumlanır; siyah yılan daha güçlü bir düşmandır...
حية يدل على عدو ...
```

Model yanıtı JSON olarak döner; her bölüm hangi kaynağa dayandığını ve kaynaktan kısa bir alıntıyı taşır:

```json
{"bolumler": [
   {"metin": "Nablusi'ye göre siyah yılan güçlü bir düşmana işaret eder.",
    "kaynaklar": [{"entry_id": "nablusi:004310", "alinti": "siyah yılan daha güçlü bir düşmandır"}]}],
 "bulunamayanlar": []}
```

Sonra kod (`atiflari_dogrula`) her atıfı denetler:
- `entry_id` modele verilen maddelerden biri değilse atıf **atılır** ve "uydurma atıf" olarak sayılır.
- Alıntı maddenin metninde geçmiyorsa alıntı boşaltılır ve sayılır.

Claude'un Citations API'si uydurma atıfı baştan engelliyordu; burada engellenmiyor ama **her seferinde yakalanıyor ve ölçülüyor**. Değerlendirmedeki "uydurma atıf = 0" hedefi bunu izliyor.

Çıktı yapısı: her sembol için "Kaynakların söyledikleri", ardından "Uzlaşılan" ve "Ayrışan" noktalar, en sonda "Kaynaklarda bulunmayanlar" ve zorunlu uyarı metni. Kurallar [05](05-yorum-yontemi.md) ve [07](07-etik-ve-hukuk.md)'den geliyor: kesin konuşmamak, "Diyanet'e göre" dememek, çelişkileri uzlaştırmayıp yan yana koymak.

### Orkestrasyon · `pipeline/run.py` (hazır)

```python
def yorumla(girdi: RuyaGirdisi, bag: Bagimliliklar) -> SorguKaydi:
    cikarim, k1  = extract(girdi, bag.istemci)
    eslesmeler   = map_symbols(cikarim.gecerli_semboller[:8], bag.varyantlar, bag.vektor)
    getirilenler = retrieve(eslesmeler, bag.depo, girdi.baglam, girdi.gelenekler, n)
    yorum, k2    = synthesize(cikarim, eslesmeler, getirilenler, girdi.baglam, bag.istemci)
    return SorguKaydi(...)   # her adımın çıktısı + süre, token, maliyet
```

`SorguKaydi` hem arayüzün hem değerlendirmenin kullandığı tek nesne. Gradio'daki hata ayıklama sekmesi bu nesnenin her alanını gösterecek.

---

## 6. LLM'i nasıl kullanıyoruz?

Bütün çağrılar tek bir sarmalayıcıdan geçiyor: `llm/client.py` (hazır, 31 Ekim).

| Konu | Nasıl |
|---|---|
| **Geçit** | EVREN LLM geçidi, OpenAI uyumlu `POST /v1/chat/completions`. Anahtar `EVREN_LLM_API_KEY` ortam değişkeninde. |
| **Yapılandırılmış çıktı** | `response_format={"type": "json_schema", "json_schema": {"name": ..., "schema": ..., "strict": True}}` |
| **Düşünme tokenları** | Model yanıt vermeden önce düşünür; bu tokenlar `completion_tokens`'a dahildir. Kısa bir istekte bile yüzlerce token tutabilir, `max_tokens` geniş verilir. |
| **Prompt önbelleği** | Geçit aynı önekle başlayan istekleri kendisi önbellekler. Sabit talimat mesajların başında durur; `usage.prompt_tokens_details.cached_tokens` ile görülür. |
| **Disk önbelleği** | Her isteğin SHA-256 özeti → `data/cache/llm/<özet>.json`. Aynı istek ikinci kez gönderilmez; toplu işler bu sayede kaldığı yerden devam eder. |
| **Gizlilik** | Rüya içeren istekler (`ruya_icerir=True`) varsayılan olarak diske **yazılmaz**; yalnızca `RUYA_SORGU_ONBELLEGI=on` iken (değerlendirme bunu açar). Loglara rüya metni girmez. |
| **Hatalar** | 429, 502, 503, 504 ve bağlantı/zaman aşımı hataları aynı `Idempotency-Key` ile en fazla 4 kez denenir. `Retry-After` 30 saniyeyi aşarsa günlük kota dolmuş sayılır, beklenmez. `finish_reason == "length"` → `YanitKesildi`, `refusal` → `ModelReddetti`. |
| **Kota ve maliyet** | `usage`'dan token sayıları okunur, `SorguKaydi`'ya yazılır. 1 Aralık'a kadar ücretsiz; asıl sınır günlük 15 milyon token ve servisin hızı. |
| **Talimatlar** | `prompts/<is>_v<n>.md`. Ölçümde kullanılmış bir sürüm bir daha değiştirilmez; değişiklik yeni sürüm dosyasıyla yapılır. Böylece her ölçüm tekrarlanabilir. |

---

## 7. Kod mimarisi: neden böyle?

### Katmanlar

```
4 · Üst        kayit, degerlendirme
3 · Sorgu      pipeline/*
2 · Veri       ingest/*, enrich/*, index/*
1 · Araçlar    text/turkce, llm/*
0 · Temel      schemas, config, hatalar, etik, dosya
```

Bir modül yalnızca kendi katmanından ya da altındakilerden içe aktarabilir. `tests/test_mimari.py` her dosyanın `import` satırlarını AST ile okuyup bunu denetliyor. Göreli içe aktarma (`from ..x`) bu denetimden kaçabileceği için yasak.

### Bağımlılık enjeksiyonu

Boru hattı dış dünyaya (API, depo, sözlük) yalnızca tek bir nesne üzerinden erişir:

```python
@dataclass
class Bagimliliklar:
    istemci: LLMIstemcisi
    varyantlar: dict[str, str]     # "engerek" → "yilan"
    depo: MaddeDeposu              # Protocol
    vektor: VektorArayici | None   # Aşama 2
    ayar: Ayarlar
```

- **Testte:** Sahte istemci ve sahte depo verilir. API çağrılmaz, para harcanmaz, test milisaniyede biter.
- **Aşama 2'de:** Bellekteki depo yerine Chroma'lı depo takılır. `pipeline/` kodu değişmez, çünkü somut sınıfı değil `Protocol`'ü (arayüzü) tanır.

### Tembel içe aktarma

`chromadb`, `torch`, `gradio`, `zeyrek` modülün başında değil, kullanıldıkları fonksiyonun içinde içe aktarılır. Böylece bilgisayarda bu dev paketler kurulu olmadan bütün paket içe aktarılabiliyor ve testler çalışıyor.

### Test türleri

| Tür | Nerede | Ne sınar |
|---|---|---|
| Birim | Bilgisayar, verisiz | Ayrıştırıcı, normalleştirme, eşleme, getirme; `tests/fixtures/`'daki birkaç satırlık örneklerle |
| Mimari | Bilgisayar, verisiz | Katman kuralı, model adları, tembel içe aktarma, notebook temizliği |
| Kontrat (`-m veri`) | Veri indirildiyse | Gerçek `entries.jsonl`'daki her kayıt şemaya uyuyor mu, `entry_id` benzersiz mi |
| Değerlendirme | Elle, API kotası harcar | Test setiyle uçtan uca ölçüm (bölüm 8) |

---

## 8. Ölçerek ilerlemek

### Test seti (`eval/dataset/ruyalar_v1.jsonl`, Hafta 3)

```json
{"id": "r007",
 "metin": "Rüyamda denize girdim, sudan siyah bir yılan çıktı, çok korktum.",
 "beklenen_semboller": ["deniz", "yilan"],
 "beklenen_nitelikler": {"yilan": ["siyah"]},
 "olmamasi_gerekenler": [],
 "beklenen_maddeler": {"yilan": ["nablusi:004310", "miller:018710"]}}
```

20 rüyayla başlayacağız (Aşama 3'te 40–50). Aralarında özel testler de olacak: kaynakta olmayan sembol ("uzay gemisi"), olumsuzlama ("yılan görmedim"), çok kelimeli sembol ("ölmüş babam"), ağır içerik.

### Ölçütler (`degerlendirme/metrikler.py`, Hafta 5)

| Adım | Ölçüt | MVP hedefi |
|---|---|---|
| Çıkarım | Sembol recall / precision | ≥ %80 / ≥ %80 |
| Çıkarım | Olumsuzlama hatası | 0 |
| Eşleme | Doğru `symbol_id` oranı | ≥ %85 |
| Getirme | Kaynak çeşitliliği | ≥ 1,5 kaynak/sembol |
| Sentez | Atıf kapsamı (atıflı iddia bölümü oranı) | %100 |
| Sentez | Uydurma atıf (doğrulamada atılan) | 0 |
| Sentez | Sadakat (elle, 10 yanıt) | 0 uydurma cümle |
| İşletim | Rüya başına süre | ≤ 30 sn (servis hızına bağlı, ölçülecek) |

**Recall ve precision:** Recall "beklenen sembollerin kaçını buldum?", precision "bulduklarımın kaçı doğru?" sorusunu cevaplar. Biri yüksek diğeri düşükse sistem ya çok şey kaçırıyor ya da çok şey uyduruyor demektir.

Her ölçüm `data/raporlar/` altına tarihli bir rapor yazar, özet satırı [olcumler.md](olcumler.md)'ye girer. Böylece "talimatı değiştirdim, iyileşti mi?" sorusunun cevabı her zaman bir sayıdır.

### Deneyler

| | Neyi karşılaştırır | Ne zaman |
|---|---|---|
| D1 | e5-large ile Qwen3-Embedding | Aşama 2 |
| D2 | Reranker var / yok | Aşama 2 |
| D3 | Kaynak başı N = 1, 2, 3 | Aşama 2 |
| D4 | EVREN'deki başka bir sohbet modeliyle karşılaştırma | Aşama 4 |
| D5 | API modeli ile yerel açık model | Aşama 4 (isteğe bağlı) |

---

## 9. Aşama 3: klasik tabir yöntemini koda dökmek

Projeyi sıradan bir RAG'dan ayıran kısım bu. Ayrıntı: [05 · yorum yöntemi](05-yorum-yontemi.md).

- **Koşullu yorum:** Maddelerdeki "kadın görürse …, mazlum görürse …" kalıpları LLM ile yapılandırılmış alana ayrıştırılır: `{"kosul": {"cinsiyet": "kadin"}, "yorum_tr": "…"}`. Sorgu anında kullanıcının bağlam formuyla karşılaştırılır; eşleşen yorum öne çıkar, diğerleri "diğer vecihler" olur.
- **Rüya türü:** Çıkarım adımı rahmânî / şeytânî / nefsânî için yalnızca bir **ipucu** verir. Kesin hüküm vermez.
- **Türetme yolları:** "Zıddıyla tabir" (ölüm = uzun ömür) gibi yöntemler `yontem` etiketine yazılır ve kullanıcıya açıklanır.
- **Uzlaşı ve ayrışma:** `sentez_v2.md` kaynakların nerede birleştiğini ve nerede ayrıştığını ayrı başlıklar altında gösterir.

---

## 10. Bir hafta nasıl geçecek? (geliştirme döngüsü)

Hafta 2'yi (ayrıştırıcılar) örnek alalım:

1. **Belge:** İlgili belge okunur ([02](02-veri-kaynaklari-ve-semasi.md) bölüm 2, [12](12-kod-yapisi-ve-sozlesmeler.md) bölüm 2). Şema değişecekse önce belge güncellenir.
2. **Fixture:** `tests/fixtures/` altına gerçek biçimi taklit eden 10–20 satırlık örnek konur. Gerçek veri bilgisayara inmez.
3. **Plan:** Ben orkestra planı yazarım: "`nablusi.py`'de `ayristir(ham_dosya) -> Iterator[Madde]`, şu davranışlar, şu kenar durumları."
4. **Kırmızı:** `testci` agent'ı testleri yazar, testler başarısız olur (henüz kod yok).
5. **Yeşil:** `kodcu` agent'ı testleri geçirecek kodu yazar.
6. **Doğrulama:** Ben `git diff`'i okurum, `pytest` ve `ruff` çalıştırırım, gerekirse düzeltirim, commit ederim.
7. **Gerçek veriyle çalıştır:** Ayrıştırma bilgisayarda gerçek veri üzerinde çalışır; istatistikler ve kontrat testleri (`uv run pytest -m veri`) koşar. Push'u sen yaparsın.
8. **Geri bildirim:** Beklenmeyen bir şey çıkarsa (ör. paragraf sayısı 5.746 değil 4.900) çıktıyı bana yapıştırırsın; fixture'a o vaka eklenir ve döngü tekrarlanır.

---

## 11. Bilinen zor noktalar

| Zorluk | Neden zor | Planımız |
|---|---|---|
| Nablusi alt paragrafları | ~3.300 paragrafın bir kısmı yeni sembol getiriyor; kuralla bulunamıyor | LLM ataması; Hafta 1'de 10 örnekle ölçülüyor (H2) |
| Çeviri kalitesi | Arapça bilen biri yok (S6) | Terim sözlüğü, yan yana okuma, 1–5 puan; 3'ün altındaysa İngilizce ara katman |
| Nitelik eşleşmesi çeviriye bağlı | Çeviri "kara yılan" derse "siyah" eşleşmez | Terimler.md'de tek karşılık; asıl çözüm Aşama 3'teki yapılandırılmış `kosullar` |
| `entry_id` kararlılığı | Satır numarasına bağlı | Kaynak sabitleme + SHA256 denetimi |
| Türkçe harfler | `"I".lower()` yanlış | Kendi `kucuk_harf()` fonksiyonumuz + testleri |
| Diller arası vektör arama | Türkçe sorgu, Arapça metin | e5 çok dilli model, `query:`/`passage:` önekleri, D1 deneyi |
| Hız ve ücretsiz dönem | Servis yoğunken tek istek 100 saniyeyi aşabiliyor; ücretsizlik 1 Aralık'ta bitiyor | Eşzamanlı toplu istekler, disk önbelleği (kaldığı yerden devam); bütün korpusun çevirisi 2 Kasım'da bitti (R13, R14) |
| Atıf güvencesi | Atıf API'si yok; model verilmemiş kaynağa atıf yapabilir | Kodda doğrulama; uydurma atıflar atılır ve sayılır |

---

## 12. Şu an neredeyiz?

- **Hazır:**
  - Şemalar, ayarlar ve boru hattı çatısı (`run.py`).
  - İndirme betiği.
  - EVREN LLM istemcisi (`llm/client.py`): önbellek, yeniden deneme, toplu istekler.
  - Mimari ve birim testleri (180'den fazla test geçiyor).
  - Hafta 1 deneme notebook'u (bilgisayarda, DeepSeek ile).
  - Dört kaynak `data/raw/` altında (5,8 MB).
- **Yalnızca imza:** Diğer bütün modüller. Her fonksiyonun gövdesi `NotImplementedError("Hafta N …")`; hangi hafta yazılacağı kodda yazılı.
- **Sıradaki:**
  1. Kurulum: API anahtarı ortam değişkeninde, `uv sync` ([10](10-kurulum-rehberi.md)).
  2. `notebooks/deneyler/01_veri_ve_ceviri.ipynb`'yi bilgisayarda çalıştırıp H1–H4'ü puanlamak.
  3. Hafta 2: ayrıştırıcılar.

| Tarih | Teknik iş | Taş |
|---|---|---|
| 2–8 Kasım | `ingest/miller.py`, `ingest/nablusi.py`, `text/turkce.py` | |
| 9–15 Kasım | `enrich/assign_symbols.py`, `symbols.json` (50 sembol), test seti (korpus çevirisi 2 Kasım'da bitti) | K1 |
| 16–22 Kasım | `extract.py`, `map.py`, `retrieve.py` | |
| 23–29 Kasım | `synthesize.py` (atıf doğrulama), Gradio, `metrikler.py`, ilk ölçüm | K2 · v0.1 |
| 30 Kasım–13 Aralık | Chroma + e5, vektör yedeği, reranker, Freud, D1–D3 | K3 · v0.2 |
| 14 Aralık–10 Ocak | İbn Sirin, `conditions.py`, bağlam formu, `sentez_v2` | K4 · v0.3 |
| 11–17 Ocak | D4 model karşılaştırması, README | K5 · v1.0 |

**Açık kararlar:** S4 (repo şu an özel; belgeye işlenmeli). 1 Aralık sonrası EVREN fiyatı açıklanınca bütçe konuşulacak. Ayrıntı: [09](09-riskler-ve-acik-sorular.md).

---

## 13. Teknik sözlük

| Terim | Anlamı |
|---|---|
| **RAG** | Getirmeyle güçlendirilmiş üretim: LLM cevabı kendi hafızasından değil, ona verilen kaynak metinlerden yazar |
| **Embedding** | Metnin anlamını temsil eden sayı vektörü; benzer anlamlı metinlerin vektörleri birbirine yakındır |
| **Vektör deposu** | Embedding'leri saklayıp "buna en yakın k tane" sorgusunu hızlı cevaplayan veritabanı (Chroma) |
| **Reranker** | Getirilen adayları sorguyla birlikte tek tek okuyup daha isabetli yeniden sıralayan model |
| **Diller arası arama** | Türkçe sorguyla Arapça/İngilizce metin bulmak; çok dilli embedding modeli gerektirir |
| **Structured output** | LLM'in yanıtını verilen JSON şemasına uymaya zorlamak |
| **Atıf doğrulama** | Modelin gösterdiği kaynak kimliklerinin ve alıntıların, ona gerçekten verilen maddelerde bulunup bulunmadığını kodda denetlemek |
| **Düşünme tokenları** | Modelin yanıttan önce ürettiği iç akıl yürütme; çıktı tokenı sayılır |
| **Prompt caching** | Tekrar eden talimat önekini sunucuda önbelleğe alıp ucuz okumak |
| **Idempotency-Key** | Bir isteğe verilen tekil kimlik; yeniden denemede aynı kalır, geçit isteği iki kez çalıştırmaz |
| **Recall / precision** | Kapsama ("kaçını buldum?") / isabet ("bulduklarımın kaçı doğru?") |
| **Recall@5** | Doğru maddenin ilk 5 sonuç içinde olma oranı |
| **Fixture** | Testlerde kullanılan küçük, sabit örnek veri |
| **Protocol** | Python'da "şu metotlara sahip her nesne olur" diyen arayüz tanımı; sahte nesne takmayı sağlar |
| **Bağımlılık enjeksiyonu** | Kodun dış kaynaklarını kendisi kurmak yerine dışarıdan almak; test edilebilirliğin temeli |
| **Tembel içe aktarma** | Ağır paketi yalnızca gerektiği an içe aktarmak |
| **TDD** | Önce başarısız test (kırmızı), sonra onu geçiren kod (yeşil) |
| **entry_id / symbol_id** | Madde kimliği (`nablusi:004310`) / sembol kimliği (`yilan`) |
| **mARkdown** | OpenITI'nin Arapça metin işaretleme biçimi (`###`, `~~`, `PageV..P..`) |
| **nbstripout** | Notebook çıktılarını commit'ten önce silen git filtresi; rüyalar ve API yanıtları GitHub'a gitmez |
