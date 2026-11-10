# 14 · Ders Notu: Projeyi Baştan Sona Anlamak

> Tarih: 7 Kasım 2026. Bu not, projeden uzak kalmış birinin her parçayı yeniden kavraması için yazıldı.
> Sırayla okunacak biçimde kuruldu: önce kavramlar, sonra veri hazırlığı, sonra bir rüyanın sistemdeki yolculuğu, en sonda ölçme, mühendislik ve dersler.
> Sayılar bu tarihteki koda ve veriye göredir. Ayrıntılı kaynaklar her bölümün sonunda gösterilir.

---

## İçindekiler

1. [Proje tek paragrafta](#1-proje-tek-paragrafta)
2. [Önce kavramlar: RAG nedir, neden gerekir?](#2-önce-kavramlar-rag-nedir-neden-gerekir)
3. [Büyük resim: iki ayrı dünya](#3-büyük-resim-iki-ayrı-dünya)
4. [Çevrimdışı hat: kütüphaneyi kurmak](#4-çevrimdışı-hat-kütüphaneyi-kurmak)
5. [Çevrimiçi hat: bir rüyanın yolculuğu](#5-çevrimiçi-hat-bir-rüyanın-yolculuğu)
6. [LLM istemcisi: modelle konuşan katman](#6-llm-istemcisi-modelle-konuşan-katman)
7. [Arayüz](#7-arayüz)
8. [Etik ve hukuk](#8-etik-ve-hukuk)
9. [Ölçme: iyi olduğunu nereden biliyoruz?](#9-ölçme-iyi-olduğunu-nereden-biliyoruz)
10. [Yazılım mühendisliği tarafı](#10-yazılım-mühendisliği-tarafı)
11. [Denenip vazgeçilenler: en öğretici kısım](#11-denenip-vazgeçilenler-en-öğretici-kısım)
12. [Bilinen sorunlar ve sıradaki işler](#12-bilinen-sorunlar-ve-sıradaki-işler)
13. [Kendini sına](#13-kendini-sına)
14. [Dosya haritası: neye nereden bakılır](#14-dosya-haritası-neye-nereden-bakılır)

---

## 1. Proje tek paragrafta

Kullanıcı Türkçe bir rüya yazar ("Rüyamda siyah bir yılan gördüm"). Sistem rüyadaki sembolleri bulur (yılan, siyah), dört klasik kaynakta bu sembollerle ilgili maddeleri arar, bulduklarını bir dil modeline verir ve modelden **yalnızca bu maddelere dayanan, her cümlesi kaynak gösteren** bir yorum yazmasını ister. Kaynaklarda olmayan bir şey için "bulunamadı" der, uydurmaz.

Dört kaynak:

| Kaynak | Gelenek | Dil | Madde sayısı |
|---|---|---|---|
| Abdülganî en-Nablusî, *Ta'tîrü'l-enâm* | İslami klasik | Arapça | 5.782 |
| Gustavus H. Miller, *Ten Thousand Dreams Interpreted* | Batı halk geleneği | İngilizce | 2.256 |
| İbn Sîrîn'e atfedilen *Muntahab* (nispeti tartışmalı) | İslami klasik | Arapça | 1.544 |
| Sigmund Freud, *Rüyaların Yorumu* (Brill 1913) | Psikanaliz | İngilizce | 1.219 |
| **Toplam** | | | **10.801** |

Hepsi Türkçeye çevrildi. Ürünün içindeki dil modeli EVREN geçidindeki `deepseek-v4.1-flash`.

---

## 2. Önce kavramlar: RAG nedir, neden gerekir?

### 2.1 Dil modeli (LLM) ve sorunu

Bir LLM (büyük dil modeli), çok büyük miktarda metinle eğitilmiş ve "bir sonraki kelimeyi tahmin etmeyi" öğrenmiş bir programdır. Sorulara akıcı cevaplar verir, ama iki temel zaafı vardır:

1. **Halüsinasyon:** Bilmediği bir şeyi bildiği şeyle aynı özgüvenle uydurur. "Nablusi yılan için ne der?" diye sorarsan ezberindeki kırıntılardan ikna edici ama yanlış bir cevap üretebilir.
2. **Kaynak gösteremez:** Cevabın hangi kitabın hangi sayfasından geldiğini bilmez, çünkü bilgi modelin içinde dağınık sayılar olarak durur.

Rüya tabiri gibi geleneğe ve kaynağa dayanan bir alanda bu kabul edilemez. "Gelenek böyle diyor" dediğimiz her şeyin gerçekten o kitapta yazması gerekir.

### 2.2 RAG: açık kitap sınavı

**RAG (Retrieval-Augmented Generation, getirmeyle güçlendirilmiş üretim)** bu sorunun standart çözümüdür. Benzetme: modeli kapalı kitap sınavından açık kitap sınavına geçiriyoruz.

```
Kapalı kitap:  soru ─────────────────────────► model ─► cevap (ezberden, uydurabilir)

RAG:           soru ─► ARAMA (kütüphanede ilgili sayfaları bul)
                          │
                          ▼
               soru + bulunan sayfalar ─► model ─► cevap (sayfalara dayanarak, atıflı)
```

RAG'ın üç parçası vardır:

1. **Kütüphane (korpus):** Modelin dayanacağı metinler. Bizde 10.801 madde.
2. **Getirme (retrieval):** Soruya en ilgili metinleri bulan arama sistemi. Projenin en çok emek isteyen kısmı burası.
3. **Üretim (generation):** Bulunan metinleri modele verip "yalnızca bunlara dayanarak cevap ver" demek.

RAG'ın altın kuralı: **getirme kötüyse üretim de kötüdür.** Model yanlış sayfaları görürse en iyi ihtimalle "bulamadım" der, en kötü ihtimalle ilgisiz sayfayı zorlayarak yorumlar. Bu yüzden projede emeğin çoğu getirmeye gitti.

### 2.3 Bu projede kullanılan temel kavramlar

Aşağıdaki kavramları bilirsen kodun tamamını okuyabilirsin.

**Token:** Modelin metni böldüğü parçalar (kabaca kelime parçaları). Hız "token/saniye", maliyet "token başına" ölçülür. Bizim sentez adımı rüya başına yaklaşık 1.300 token yazıyor.

**Prompt / sistem talimatı:** Modele verilen yönergeler. Bizde `prompts/` klasöründe sürümlü dosyalar olarak durur (`cikarim_v4.md`, `sentez_v3.md`).

**Yapılandırılmış çıktı (JSON şeması):** Modelden serbest metin değil, belirli alanları olan bir JSON istemek. Böylece kod cevabı güvenle okuyabilir. Örnek: `{"semboller": [{"yalin": "yılan", "olumsuz": false}]}`.

**Normalleştirme:** Metni karşılaştırılabilir hâle getirmek: küçük harf (Türkçeye uygun: `I → ı`, `İ → i`), boşluk ve noktalama temizliği. "Yılanlar!" → "yılanlar".

**Kök bulma (stemming/lemmatization):** Türkçe eklemeli bir dil: "yılanlarımızdan" kelimesinin kökü "yılan". Kök bulmadan "yılan" araması "yılanlar"ı kaçırır. Bunun için **zeyrek** kütüphanesini kullanıyoruz.

**BM25 (anahtar kelime araması):** Klasik arama motoru formülü. Mantığı:
- Sorgudaki kelime bir metinde **çok geçiyorsa** o metin ilgilidir.
- Kelime **nadir** bir kelimeyse ("ve" değil, "yılan") daha değerlidir (IDF: ters belge sıklığı).
- Uzun metinler sırf uzun oldukları için öne geçmesin diye uzunluğa göre düzeltme yapılır.
- Bizim ayarlar: k1 = 1,5 (tekrarın etkisi ne kadar doyar), b = 0,75 (uzunluk düzeltmesinin gücü).
- Güçlü yanı: kesin kelimeyi kaçırmaz. Zayıf yanı: eş anlamlıyı bilmez ("ihanet" arayınca "aldatma"yı bulmaz).

**Embedding (vektör, gömme):** Bir metni anlamını temsil eden sayı listesine çevirmek. Bizim modelimiz (`qwen3-embedding-8b`) her metni 1.024 sayılık bir vektöre çevirir. Anlamca yakın metinlerin vektörleri de yakındır: "kötü niyetli düşman" ile "hasım" kelime paylaşmasa bile yakın düşer.

**Kosinüs benzerliği:** İki vektörün ne kadar aynı yöne baktığı; 1'e yaklaştıkça anlam yakın. Vektör araması, sorgunun vektörüne en yakın vektörleri bulmaktır.

**Hibrit arama:** BM25 (kelime) ile vektörü (anlam) birlikte kullanmak. Biri kesin kelimeyi, diğeri anlamı yakalar; birbirlerinin açığını kapatırlar.

**HyDE (Hypothetical Document Embeddings, varsayımsal belge):** Kısa bir sorgu ("yılan") ile uzun, resmî üsluplu bir madde ("Kim rüyasında yılan görürse düşmanına...") arasında biçim farkı vardır. HyDE'de modele önce "bu sembol için bir tabirnamede ne yazabilirdi?" diye **sahte bir madde** yazdırılır, sonra bu sahte madde ile arama yapılır. Sahte madde gerçek maddelere üslupça benzediği için onları daha iyi bulur. **Önemli:** Sahte madde yalnızca aramada kullanılır, kullanıcıya gösterilmez, kaynak sayılmaz.

**RRF (Reciprocal Rank Fusion, sıra füzyonu):** Birden çok arama listesini tek listede birleştirme yöntemi. Her listede bir maddenin skoru `1 / (k + sıra)`, k = 60. Toplam skor bu değerlerin toplamıdır. Örnek:
- Madde A: BM25'te 1., vektörde 3. → 1/61 + 1/63 ≈ 0,0164 + 0,0159 = **0,0323**
- Madde B: dört listenin dördünde de 2. → 4 × 1/62 ≈ **0,0645**

B hiçbir listede birinci değil ama her yerde iyi olduğu için kazanır. RRF'nin güzelliği, farklı ölçekteki skorları (BM25 skoru 12,4, kosinüs 0,81) denkleştirmeye gerek bırakmamasıdır; yalnızca sıraya bakar.

**Reranker (yeniden sıralayıcı):** Aramanın ilk aşaması hızlı ama kabadır. Reranker, sorgu ile adayı **birlikte** okuyup "bu metin bu soruya ne kadar cevap?" diye 0–1 arası bir skor veren daha yavaş ama daha isabetli bir modeldir. Bizde `qwen3-reranker-8b`. Hızlı arama 40 aday bulur, reranker bunları dikkatle sıralar.

**Eşik:** Reranker skoru 0,15'in altındaysa madde atılır. Hiçbir madde kalmazsa sistem "bulunamadı" der. Bu, uydurmaya karşı ana kalkandır.

**Atıf doğrulama:** Model "şu maddeye dayanıyorum" dediğinde bunu kodda kontrol etmek. Modele verilmemiş bir madde kimliği yazarsa atıf atılır.

**Önbellek (cache):** Aynı isteği ikinci kez göndermemek için cevabı diske yazmak. Geliştirmeyi hızlandırır ve ücreti düşürür.

---

## 3. Büyük resim: iki ayrı dünya

Sistem iki ayrı bölümden oluşur. Bunu kavramak her şeyi kavramaktır.

```
┌───────────────────── ÇEVRİMDIŞI (bir kez, toplu) ─────────────────────┐
│                                                                       │
│  ham kitaplar ─► ayrıştır ─► çevir ─► sembol ata ─► zenginleştir      │
│  data/raw        ingest/     (bitti)   enrich/       enrich/          │
│                                                                       │
│                ─► entries.jsonl (10.801 madde) ─► indeks kur          │
│                   data/processed/                  data/index/hibrit/ │
└───────────────────────────────────────────────────────────────────────┘
                                   │ (hazır kütüphane)
                                   ▼
┌───────────────────── ÇEVRİMİÇİ (her rüyada) ──────────────────────────┐
│                                                                       │
│  rüya ─► 1 çıkarım ─► 2 eşleme ─► 3 getirme ─► 4 sentez ─► yorum      │
│          (LLM)        (kod)       (arama)      (LLM + kod denetimi)    │
└───────────────────────────────────────────────────────────────────────┘
```

**Neden ayrı?** Çeviri, etiketleme ve indeksleme pahalı ve yavaş işlerdir. Bunları her rüyada yapamayız. Bir kez yapıp diske yazarız; sorgu anında yalnızca hafif işler kalır.

**Tasarım ilkeleri (docs/03):**
1. **Önce sözlük, sonra arama.** Rüya tabiri aslında "sözlükte sembol bulma" işidir. Kesin eşleşme birinci yol.
2. **Her adım ayrı ve gözlemlenebilir.** Her adımın girdisi ve çıktısı bir veri sınıfıdır; arayüzdeki "Hata ayıklama" sekmesi hepsini gösterir.
3. **LLM yalnızca gerektiği yerde.** Eşleme ve getirme saf koddur. LLM yalnızca çıkarım ve sentezde (ve çevrimdışı çeviride) kullanılır.
4. **Kaynak bilgisi her yerde taşınır.** Her madde kaynağını, lisansını ve konumunu sonuna kadar götürür.
5. **Framework yok.** LangChain gibi hazır çerçeveler kullanılmadı. Düz Python, az kütüphane. Amaç her katmanı görerek öğrenmekti.

---

## 4. Çevrimdışı hat: kütüphaneyi kurmak

### 4.1 Kaynak seçimi ve lisans

Kaynak seçerken üç soru soruldu: telif açısından kullanılabilir mi, geleneği iyi temsil ediyor mu, makine ile ayrıştırılabilir mi?

- **Nablusi** (OpenITI, CC BY-NC-SA 4.0): İslami tabirin alfabetik çekirdek sözlüğü.
- **Miller** (Project Gutenberg #926, kamu malı): En büyük Batı sembol sözlüğü, temiz yapılı.
- **İbn Sîrîn'e atfedilen *Muntahab*** (OpenITI): İkinci İslami ses. Eserin İbn Sîrîn'e ait olduğu tartışmalı, bu yüzden her yerde "atfedilen" ve "nispeti tartışmalı" denir.
- **Freud** (Gutenberg #66048, kamu malı): Sembol sözlüğü değil, bir **yöntem**. Bu yüzden yalnızca kullanıcı "psikanalitik" geleneğini seçerse aramaya girer.

**Bilinçli olarak alınmayanlar:** Türkçe Nablusi ve İbn Sîrîn çevirileri (çeviriler ayrı eser sayılır, telifli), Jung, Freud'un modern Türkçe çevirileri, rüya siteleri. Akademik makaleler yalnızca kural tasarlamak için okundu, metinleri korpusa girmedi.

### 4.2 İndirme ve kimliklerin sabitlenmesi

`scripts/download_sources.py` ham dosyaları `data/raw/` altına indirir.

Burada ince ama çok önemli bir fikir var: **her maddenin kimliği, ham dosyadaki satır numarasından türetilir.** `nablusi:004310` = Nablusi dosyasının 4310. satırı. Bu kimlik test setinde, çeviride, sembol atamasında her yerde kullanılır.

Sorun: Kaynak dosyada tek satır değişirse bütün kimlikler kayar ve her şey yanlış maddeyi gösterir. Çözüm:
- OpenITI adresleri `master` dalına değil, **belirli bir commit'e** sabitlenir.
- Gutenberg dosyalarının **SHA256 özeti** saklanır. Özet tutmazsa indirme betiği dosyayı yazmaz ve hata verir.

Öğrenilecek ders: **Kimlik veren bir sistemde girdiyi dondurmak zorundasın.**

### 4.3 Ayrıştırma (`src/ruya/ingest/`)

Her kaynak için ayrı bir ayrıştırıcı ham metni madde kayıtlarına böler:

- **Miller (`miller.py`):** En kolayı. Her madde başlığı `_Abbey_.` biçiminde; tek bir düzenli ifade (regex) yakalar: `^_[^_]+_\.(\[\d+\])?$`. Baştaki uzun önsöz atlanır.
- **Nablusi (`nablusi.py`):** En zoru. Harekesiz Arapça, 29 bölüm. Her paragraf `# - (` ile başlar, ama iki tür paragraf var:
  - **Başlıklı madde** (yaklaşık 2.400): `# - (حية)`; parantez içi sembolün kendisi.
  - **Alt paragraf** (yaklaşık 3.300): `# - (ومن رأى)` ("ve kim görürse") ile başlar ve bir önceki başlığın alt durumudur. Bunlar `ust_madde_id` alanıyla başlıklarına bağlanır.
  - Gürültü temizlenir: satır devam işaretleri (`~~`), sayfa işaretleri (`# PageV01P009`). Sayfa bilgisi `konum` alanında saklanır.
- **İbn Sîrîn (`ibn_sirin.py`):** Konu (bab) düzeninde, yine OpenITI biçiminde.
- **Freud (`freud.py`):** Bölümler ve paragraflar; içindekiler, kaynakça ve dizin alınmadı.

Çıktı `data/interim/<kaynak>.jsonl`: paragraf başına bir kayıt, asıl dilde.

### 4.4 Çeviri

On binlerce paragrafın Türkçeye çevrilmesi projenin en büyük tek işiydi (2 Kasım 2026'da bitti).

- **Nasıl:** EVREN tek istekte çok yavaş olduğu için çeviri çevrimdışı ve parça parça yapıldı. Önce Claude Code ajanları (Miller'in tamamı, Nablusi'nin çoğu), kullanım sınırına gelince orkestra ile EVREN ajanları. Parçalar `data/interim/ceviri/<kaynak>/parca_NNNN.jsonl` altında; `enrich/ceviri_birlestir.py` bunları maddelere işler.
- **Kalite önlemi:** İlk EVREN turunda ajanlar uzun paragrafları yarıda bırakıp "[metin burada kesiliyor]" yazmıştı. Bunlar **uzunluk oranı denetimiyle** (çeviri asıl metne göre çok kısaysa şüphelen) bulunup yeniden çevrildi.
- **Şeffaflık:** Her maddede `ceviri.model = "claude-code+evren"` ve `gozden_gecirildi: false` yazar. Çeviri henüz insan gözünden geçmedi.
- **Bilinen hata örneği:** İbn Sîrîn'in bir maddesinde Arapça ذَكَر (erkeklik organı) kelimesi "zikir" diye çevrilmiş. Yorum bu hatayı aynen taşıdı. RAG'ın bir sınırını gösteriyor: **model kaynağa sadıksa, kaynağın hatası da cevaba geçer.**
- **Terim tutarlılığı:** `docs/terimler.md` sık kavramlar için tek karşılık belirler; "siyah" ile "kara" karışırsa arama kaçırır.

### 4.5 Sözlük (`sozluk/symbols.json`)

Projenin kalbi, elle denetlenen bir sembol sözlüğüdür. 143 sembol var. Bir kayıt:

```json
"yilan": {
  "ad_tr": "yılan",
  "varyantlar_tr": ["engerek", "kobra"],
  "ar": ["حية", "ثعبان", "أفعى"],
  "en": ["snake", "snakes", "serpent"],
  "bab_kategorisi": "hayvanlar",
  "hvdc_kategorisi": "karakterler",
  "gozden_gecirildi": true
}
```

- **`symbol_id`** (`yilan`) her zaman ASCII ve küçük harflidir; dosya adlarında ve sorgularda Türkçe karakter sorunu çıkmaz.
- **Varyantlar:** "gülümsemek" → `gulmek`, "cami" → `mescit`, "avuç" → `el`. Kullanıcının kelimesini sözlükteki sembole bağlayan köprüler.
- **Üç dil:** Arapça ve İngilizce karşılıklar, farklı kaynaklardaki aynı sembolü tek kimlikte toplar (Miller'ın "Snakes" ve "Serpents" maddeleri ile Nablusi'nin حية maddesi aynı `yilan`).
- **İki kategori ekseni:**
  - `bab_kategorisi`: klasik tabirnamelerin konu düzeninden sadeleştirilmiş 15 üst kategori (hayvanlar, su, ibadet...).
  - `hvdc_kategorisi`: Hall & Van de Castle'ın modern rüya içerik analizinden 10 kategori (karakterler, duygular, mekânlar ve nesneler...).
  - Bu kategoriler şu an kodda kullanılmıyor; ileride "rüyanda en çok hayvan sembolü var" gibi özetler ve kategori bazında ölçüm için.
- Sözlük **git'te** durur, `data/` içinde değil. Çünkü telifli metin içermez, yalnızca kelimeler içerir ve her değişikliği commit geçmişinde görmek isteriz.

### 4.6 Sembol atama (`enrich/sembol_ata.py`)

Her maddeye hangi sembollere ait olduğu yazılır (`symbol_ids`). Kural basit ve deterministiktir (LLM yok):

1. Maddenin çeviride önerilen sembol adı (`sembol_tr`) normalleştirilir ve sözlükte aranır.
2. Bulunamazsa ve madde bir alt paragrafsa, **üst maddesinin sembolünü devralır.** ("Kim onu öldürürse..." paragrafı, başlığı "yılan" olan maddenin altındaysa yılana aittir.)
3. Freud maddelerinin sembolü yoktur; yalnızca serbest aramayla bulunurlar.

### 4.7 Zenginleştirme: koşul, yöntem, kapsam

Klasik tabirci rüyayı **kimin, ne zaman, hangi hâlde** gördüğüne bakar. "Kadın görürse şöyle, erkek görürse böyle" gibi. Bunu yakalamak için maddelere üç etiket eklendi. Üçü de **kurallarla** (düzenli ifadelerle) çıkarıldı, LLM ile değil.

**Neden LLM değil?** 10.801 maddeyi saniyede 18 token hızla LLM'den geçirmek günler sürerdi. Kural hızlı, ucuz, tekrarlanabilir. Bedeli: bazı durumları kaçırır. Kaçırması zararsızdır: madde yine sıralamada kalır, yalnızca bonus almaz.

| Etiket | Ne yakalar | Madde sayısı | Dosya |
|---|---|---|---|
| `kosullar` | Rüya sahibinin cinsiyeti, medeni hâli, mevsim ("kadın görürse", "evli ise", "kışın") | 1.025 | `enrich/kosul_kurallari.py` |
| `yontem` | Yorumun dayanağı: ayet, hadis, atasözü, zıddıyla tabir | 392 | `enrich/yontem_kurallari.py` |
| `kapsam` | Kişiye değil hükümdara (`padisah`) ya da bir yerin halkına (`vilayet`) yönelik maddeler | 116 | `enrich/kapsam_kurallari.py` |

**Önemli ders: kuralı daraltmak.** Koşul kurallarının ilk sürümü maddelerin %23'ünü işaretliyordu, çünkü "bir kadına iftira eder" gibi cümleleri de "kadın" koşulu sayıyordu. Oysa orada kadın rüyayı gören değil, rüyada geçen biri. Kural yalnızca **rüya sahibini** anlatan kalıplara daraltılınca oran %9,5'e indi. Kapsam kurallarında da aynı ilke: etiket, maddenin en az bir cümlesini gerçekten anlatmalı.

Kullanım: Kullanıcı arayüzde "kadın" seçerse, "kadın görürse" koşulu taşıyan madde +0,1 bonus alır, yalnız farklı koşul taşıyan madde −0,1 ceza alır. Kapsam etiketi olan maddeler sentez isteğine `Kapsam: padisah` satırıyla gider ve model "bu yorum hükümdara yöneliktir" diye belirtir.

### 4.8 Bir madde kaydının anatomisi

`data/processed/entries.jsonl` dosyasının her satırı bir maddedir:

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
  "sembol_tr": "yılan",
  "ust_madde_id": null,
  "symbol_ids": ["yilan"],
  "metin_asli": "…Arapça asıl…",
  "metin_tr": "…Türkçe çeviri…",
  "ceviri": {"yontem": "llm", "model": "claude-code+evren", "gozden_gecirildi": false},
  "kosullar": [...],
  "yontem": ["ayet"],
  "kapsam": null
}
```

Kurallar: `lisans` asla boş olamaz (şema hata verir). Bilinmeyen alan kabul edilmez. İbn Sîrîn maddelerinde `atif_notu` "nispeti sahih değil" der. Kodda bu şema `src/ruya/schemas.py` içindeki `Madde` sınıfıdır.

`scripts/maddeleri_kur.py` bütün bu adımları sırayla çalıştırıp dosyayı üretir.

### 4.9 İndeksi kurmak (`index/`, `scripts/hibrit_indeks_kur.py`)

Arama yapabilmek için maddeleri aranabilir bir yapıya çeviririz.

**Adım 1 · Parçalara bölme (`index/parcalar.py`).** Bazı maddeler çok uzun ("Allah'ı görmek" maddesi 40 satırı aşar). Uzun bir metnin tek vektörü anlamı bulanıklaştırır. Bu yüzden maddeler en çok 1.000 karakterlik, 150 karakter örtüşen **parçalara** bölünür. Toplam **12.364 parça**.

Her parçanın başına bir **bağlam öneki** eklenir:

```
Ta'tîrü'l-enâm · Nablusi. Sembol: yılan. Bölüm: …
<parça metni>
```

Neden? "Onu sokarsa ayıp bulur" gibi bir alt paragraf "yılan" kelimesini hiç içermez; önek olmadan "yılan" aramasında kaybolur. Bu fikir Anthropic'in "contextual retrieval" çalışmasından; biz öneki LLM ile değil, künye ve üst maddeden kodla kurduk (12 bin LLM çağrısı günler sürerdi). Önek yalnızca arama içindir; alıntı doğrulaması yine asıl `metin_tr` üzerinde yapılır.

**Adım 2 · BM25 indeksi (`index/bm25.py`).** Kendi yazdığımız küçük Okapi BM25. Terimler zeyrek ile köke indirilir; kök bulunamazsa kelimenin ilk 5 harfi kullanılır (Türkçe için ucuz ve yakın bir yöntem). Çıktı `bm25.json`.

**Adım 3 · Vektörler (`index/build_vectors.py`).** Her parça EVREN'deki embedding modeline gönderilir, 1.024 boyutlu vektörler `vektorler.npy` dosyasına (numpy dizisi) yazılır. Arama, bütün vektörlerle tam karşılaştırmadır; 12 bin parça için milisaniyeler sürer, ayrı bir vektör veritabanına gerek yok.

**Adım 4 · Manifest.** `manifest.json` parça sayısını, modeli ve madde kümesinin özetini saklar. `entries.jsonl` değişip indeks eski kalırsa sistem bunu anlar, hibrit indeksi yüklemez ve uyarı verir.

---

## 5. Çevrimiçi hat: bir rüyanın yolculuğu

Bir örnekle izleyelim: **"Rüyamda gümüş bir anahtarla kapıyı açtım, ölmüş dedemi gördüm."**

Orkestrasyon `src/ruya/pipeline/run.py` içindeki `yorumla` fonksiyonudur. Dört adımı sırayla çağırır, her adımın süresini ve token sayısını `SorguKaydi` nesnesine yazar.

### 5.1 Adım 1 · Çıkarım (`pipeline/extract.py`, LLM)

Model, `prompts/cikarim_v4.md` talimatıyla rüyayı okur ve JSON döner:

```json
{
  "semboller": [
    {"yalin": "anahtar", "nitelikler": ["gümüş"], "eylem": "açtı", "olumsuz": false,
     "ham_ifade": "gümüş bir anahtarla", "hyde": "Rüyada anahtar görmek, kapalı bir işin açılmasına..."},
    {"yalin": "gümüş", ...},
    {"yalin": "kapı", ...},
    {"yalin": "dede", ...},
    {"yalin": "ölü", ...}
  ],
  "ruya_turu_ipucu": null,
  "hassas_icerik": false
}
```

Alanlar:
- `yalin`: sembolün yalın, tekil, küçük harfli hâli ("kapının" → `kapı`).
- `nitelikler`, `eylem`, `duygu`: tabirde anlamı değiştiren ayrıntılar.
- `olumsuz`: "yılan görmedim" → `true`; olumsuz semboller yorumlanmaz.
- `hyde`: arama için sahte madde (bkz. 2.3). Ek LLM çağrısı açmamak için aynı yanıtın içinde gelir.
- `ruya_turu_ipucu`: klasik üçlü (rahmani, şeytani, nefsani) için yalnızca ipucu.
- `hassas_icerik`: kendine zarar, travma varsa güvenlik notu eklenir.

**Talimat sürümleri neden önemli?** Ölçümler talimatın her sürümünün etkisini gösterdi:
- `cikarim_v2`: tamlamaları ayır ("evimin kapısı" → ev + kapı), HyDE ekle.
- `cikarim_v3`: ekli beden parçaları ("elimde bir fener" → el + fener), olayın geçtiği yer ("ormanın içinde" → orman), ölmüş kişi için `ölü`, madde sıfatı ayrı sembol ("altın bir tarak" → tarak + altın). **Sembol yakalama %78'den %96'ya çıktı.**
- `cikarim_v4`: "kelimeyi anlamıyla yaz" kuralı ("bir tas su" kâsedir, taş değildir).

**Talimat örneklerinde test setinden cümle kullanılmaz.** Kullanılırsa model test sorularının cevabını ezberler ve ölçüm şişer (veri sızıntısı). v3'ü yazarken ilk taslaktaki örneklerin test setiyle çakıştığı görüldü ve hepsi değiştirildi.

**Hız ayarı:** DeepSeek varsayılan olarak cevap vermeden önce uzun uzun "düşünür" (akıl yürütme tokenleri). Bu iş için gerekli değil. `chat_template_kwargs: {"enable_thinking": false}` ile kapatıldı: kısa bir çıkarım 77 saniyeden 7 saniyeye indi.

### 5.2 Adım 2 · Eşleme (`pipeline/map.py`, saf kod)

Her sembol sözlükteki bir `symbol_id`'ye bağlanmaya çalışılır. Sıra:

1. **Normalleştir:** "Anahtar" → "anahtar".
2. **Birebir:** Sözlüğün ad ve varyant tablosunda doğrudan ara. `anahtar` → `anahtar` ✓ (güven 1,0)
3. **Kök:** Bulunamazsa zeyrek ile kök bulup yeniden ara. "yılanlar" → kök "yılan" → `yilan` (güven 0,9)
4. **Parça:** Çok kelimeli ifadeyi kelimelere bölüp tek tek dene (güven 0,8). Kelime sırası Türkçe dilbilgisine göre seçilir:
   - Son kelime iyelik ekiyle bitiyorsa (ı/i/u/ü) **soldan sağa**: "deniz kenarı" → `deniz`, "kız çocuğu" → `kiz`.
   - Bitmiyorsa sıfat + isim sayılır, **sağdan sola** (önce baş isim): "gümüş anahtar" → `anahtar`.
5. **Yok:** Hiçbiri tutmazsa `symbol_id = None`. Bu sembol çöpe gitmez; "serbest arama" ile hibrit aramaya girer (anahtarı `serbest:dede`).

Sonra iki temizlik:
- **Genel fiilleri ele:** Sözlükte karşılığı olmayan "kullanmak", "yapmak", "gitmek" gibi fiiller atılır; serbest aramada rastgele maddeler getiriyorlardı ("allık kullanmak"). Sözlükte karşılığı olan fiiller ("uçmak", "düşmek") kalır.
- **Tekrarları ele:** "ölüm haberi" ve "ölüm" ikisi de `olum` olursa yalnızca ilki kalır.

En fazla 8 eşlenmiş sembol işlenir; fazlası `atlanan_semboller` listesine yazılır. Hiç sembol kalmazsa "sembol bulamadım" mesajı döner.

**Neden LLM değil de kod?** Eşleme deterministik olmalı: aynı girdi her seferinde aynı sonucu vermeli, test edilebilmeli, hızlı olmalı. `tests/test_map.py` bu kuralların her birini sınar.

### 5.3 Adım 3 · Getirme (`pipeline/hibrit.py`, arama)

Her sembol için dört ayrı arama listesi çıkarılır:

```
Sembol: anahtar (nitelik: gümüş, eylem: açtı, hyde: "Rüyada anahtar görmek...")
  ├─ Sözlük:  symbol_id = "anahtar" olan maddeler
  ├─ BM25:    "gümüş anahtar açmak" sorgusunun kökleriyle parça araması
  ├─ Vektör:  sorgunun embedding'ine en yakın parçalar
  └─ HyDE:    sahte maddenin embedding'ine en yakın parçalar
        │
        ▼  RRF (k = 60), madde düzeyinde birleştir → en iyi 40 aday
        │
        ▼  Reranker: sorgu ↔ her adayın en iyi parçası, 0–1 skor
        │
        ▼  Eşik: 0,15 altı atılır (hiçbiri kalmazsa → "bulunamadı")
        │
        ▼  Bağlam bonusu (±0,1, koşullar eşleşirse)
        │
        ▼  Kaynak başına en fazla N = 1 madde → Nablusi 1, İbn Sîrîn 1, Miller 1
```

Ayrıntılar:
- **Pasaj:** Sentez modeli maddenin kırpılmış başını değil, aramayı kazanan **parçayı** görür. Uzun bir maddede ilgili kısım ortada olabilir.
- **Eşik nasıl belirlendi:** Denemelerde ilgili madde 0,45, ilgisiz madde 0,003, "uzay gemisi" ↔ "gemi" 0,10 aldı. 0,15 seçildi. Pay dar; eşik test setiyle ayarlanmadı.
- **Kaynak başına N = 1:** N = 2 ile sentez modeli iki kat metin okuyup 12 dakika sürüyordu.
- **Freud:** Yalnızca kullanıcı "psikanalitik" geleneğini seçerse aramaya girer.
- **Yedek yol:** Hibrit indeks yoksa ya da embedding/reranker çağrısı hata verirse sistem yalnızca sözlüğe dayalı eski getirmeye (`pipeline/retrieve.py`) döner ve bunu kayda yazar.

**Hibrite neden geçtik?** Yalnız sözlükle getirme, 10.801 maddenin yalnızca sembole bağlı olanlarına ulaşabiliyordu (3 Kasım'da 1.436 madde). Sözlükte olmayan bir sembol ("baba", "şehir") hiç bulunamıyordu. Hibrit arama ile sözlük dışı semboller de kaynaklarda aranıyor.

### 5.4 Adım 4 · Sentez (`pipeline/synthesize.py`, LLM + kod denetimi)

Getirilen maddeler modele **numaralı kaynaklar** olarak verilir:

```
[K1] nablusi:011650 · Abdülganî en-Nablusî · anahtar
Kapsam: (yoksa satır yok)
<pasaj metni>
```

Model JSON yazar: her sembol için bir bölüm, her bölümde atıflar (`entry_id` + kısa alıntı), bulunamayan semboller ve en sonda birkaç cümlelik düz bir **genel yorum**.

**Paralel sentez (9 Kasım).** İlk sürümde bütün semboller tek istekte yazılıyordu (`sentez_v4`); model uzun bir metni tek başına yazarken rüya başına 2–6 dakika geçiyordu. Şimdi her sembol için ayrı, kısa bir istek gider (`sentez_sembol_v2`: en çok 3 cümle, 3 kaynak, 20 kelimelik alıntı) ve bu istekler aynı anda çalışır. Bölümler bitince ayrı bir kısa istek (`genel_yorum_v1`) onları düz bir paragrafta birleştirir; bu istek hata verirse yorum genel yorumsuz döner. Her sembol isteği yalnız o sembolün maddelerini görür, atıflar da yalnız onlarla denetlenir. Geçit hesap başına bir modelde **en fazla 4 eşzamanlı** istek kabul ettiği için `EN_FAZLA_ESZAMANLI = 4`. Sentez süresi yaklaşık %40 kısaldı.

Talimattaki başlıca kurallar (docs/05, docs/07):
1. Yalnızca verilen maddelere dayan; her yorum cümlesi atıf taşısın.
2. Madde yoksa "kaynaklarda bulunamadı" de, tahmin yürütme.
3. Kaynaklar çelişiyorsa uzlaştırma, yan yana koy. Çelişki hata değil, geleneğin doğası (bir madde aynı sembolü "yedi vecih üzre" açıklayabilir).
4. İbn Sîrîn için hep "İbn Sîrîn'e atfedilen *Muntahab*'a göre (nispeti tartışmalı)".
5. Kehanet dili yok ("zengin olacaksın" değil, "gelenekte bolluk olarak yorumlanır").
6. Dinî otorite iddiası yok, teşhis yok, korkutucu sembollerde yumuşak dil.
7. Kapsam satırı olan maddeyi kişiye yönelik gibi sunma.

**Modele güvenme, denetle (`atiflari_dogrula`).** Model çıktısı kodda kontrol edilir:
- Atıftaki `entry_id` modele verilen maddelerden biri değilse → **atıf atılır** (uydurma atıf).
- Alıntı, maddenin metninde (normalleştirilmiş hâliyle) geçmiyorsa → atıf kalır ama **alıntı boşaltılır**.
- Atıf başlığı modelden değil, maddenin kendisinden alınır.
- Bir sembol hem atıflı bölümde hem "bulunamayanlar" listesinde görünmez (`_uzlastir`).

Son olarak her yanıtın altına sabit uyarı metni eklenir (`etik.py`): bu bir kültürel/edebî aktarımdır, kehanet ya da dinî hüküm değildir.

### 5.5 Kayıt (`SorguKaydi`)

Her rüya için tek bir kayıt nesnesi oluşur: girdi, çıkarım sonucu, eşleşmeler, getirilen adaylar (skorları ve gerekçeleriyle), yorum, her adımın süresi, token sayısı ve hangi talimat sürümünün kullanıldığı. Arayüz de değerlendirme betiği de aynı nesneyi kullanır. Bir yorum neden kötü çıktıysa bu kayda bakıp hangi adımda bozulduğunu bulursun.

---

## 6. LLM istemcisi: modelle konuşan katman

`src/ruya/llm/client.py` bütün model çağrılarının tek kapısıdır.

- **EVREN geçidi:** `https://evren-llmapi.ssyz.org.tr`. OpenAI uyumlu bir API; sohbet, embedding, rerank ve OCR uçları var. Anahtar yalnızca `EVREN_LLM_API_KEY` ortam değişkeninde durur, hiçbir dosyaya yazılmaz.
- **Model adları tek yerde:** Bütün model adları ve adres yalnızca `src/ruya/config.py` içinde. Model değiştirmek tek satır.
- **Yeniden deneme:**
  - 429/502/503/504 gibi geçici hatalarda 4 kez denenir.
  - "Model dolu" (503) ve "çok istek" (429: 4 eşzamanlı istek ya da dakikalık token sınırı) yanıtlarında 15, 30, 60 saniye beklenir; kısa beklemeler yetmiyordu, test setinde rüyalar düşüyordu.
  - 409 "istek hâlâ işleniyor" yanıtında aynı **Idempotency-Key** ile beklenip yeniden sorulur, böylece aynı istek iki kez çalıştırılmaz.
  - Sunucu "çok uzun bekle" diyorsa (günlük kota) beklemek anlamsız; hata verilir.
- **Disk önbelleği:** İsteğin tamamının özeti (hash) dosya adı olur, cevap `data/cache/llm/` altına yazılır. Aynı istek ikinci kez gelirse cevap diskten okunur. Talimat değişirse özet değişir, önbellek kendiliğinden geçersiz olur.
- **Gizlilik:** Rüya içeren istekler varsayılan olarak önbelleğe **yazılmaz** (`sorgu_onbellegi = False`). Yalnızca değerlendirme betiği, repodaki test seti için açar.
- **Ölçüm:** Her çağrının token sayısı ve süresi `Kullanim` nesnesine yazılır.

---

## 7. Arayüz

`app/gradio_app.py`, Gradio ile yazılmış bir web arayüzü. Açmak için:

```
uv run python scripts/arayuz_ac.py
```

- Yalnızca yerelde (`localhost`) açılır; `share=True` kullanılmaz, rüyalar internete açılmaz.
- **Rüya metni** kutusu ve **Yorumla** düğmesi.
- **Rüya defterinden oku:** Fotoğraf yüklenir, EVREN'deki `deepseek-ocr-2` modeli el yazısını metne çevirir (OCR).
- **Bağlam (isteğe bağlı):** cinsiyet, medeni hâl, mevsim, gurbette mi. Koşul bonusunu besler. Sistem bunları asla tahmin etmez, yalnızca kullanıcının verdiğini kullanır.
- **Gelenek seçimi:** boş bırakılırsa hepsi; "psikanalitik" seçilirse Freud da girer.
- **Yorum sekmesi:** atıflı yorum; bir atıf seçilince maddenin tam metni görünür.
- **Akış (10 Kasım):** Yorum geldikçe görünür. Boru hattı ayrı bir iş parçacığında çalışır ve her aşamada (`esleme`, `getirme`, her biten sembol için `sentez`) kaydın bir kopyasıyla haber verir; arayüz bu haberleri bir kuyruktan okuyup ekrana yazar. Kullanıcı birkaç saniyede sembolleri, sonra sembol yorumlarını tek tek görür; uyarı ve genel yorum en sonda gelir.
- **Hata ayıklama sekmesi:** `SorguKaydi`'nin tamamı JSON olarak; her adımın çıktısı ve süresi.

---

## 8. Etik ve hukuk

Bu proje iki hassas alanda: telifli metinler ve inanç.

**Veri kuralları (docs/07):**
- Korpusa yalnızca kamu malı ya da açık lisanslı metin girer; her maddenin `lisans` alanı dolu olmak zorunda.
- Türkiye'de çeviriler ayrı eser sayılır (FSEK); bu yüzden mevcut Türkçe tabirname çevirileri kullanılmadı, kendi çevirimiz yapıldı.
- OpenITI kaynakları CC BY-NC-SA: ticari kullanım yok, türetilen paylaşılırsa aynı lisansla. Proje ticarileşirse NC lisanslı kayıtlar `lisans` alanına göre tek filtreyle çıkarılabilir.
- `data/` git'e girmez: lisans, boyut ve rüya gizliliği.

**Yorum dili kuralları:**

| Kural | Yanlış | Doğru |
|---|---|---|
| Kehanet yok | "Yakında zengin olacaksın." | "Gelenekte bu sembol bolluk olarak yorumlanır." |
| Dinî otorite yok | "Diyanet'e göre…", "Allah sana şunu söylüyor" | "Nablusi'nin tabirnamesine göre…" |
| Teşhis yok | "Depresyondasın." | "Psikanalitik bir bakışla Freud…" |
| Yumuşak dil | "Bu rüya ölüm habercisi." | "Bazı tabirciler ölümü zıddıyla, uzun ömür olarak yorumlamıştır." |
| Atıf dürüstlüğü | "İbn Sîrîn'e göre…" | "İbn Sîrîn'e atfedilen *Muntahab*'a göre (nispeti tartışmalı)…" |

Bu kurallar talimata yazılır ve değerlendirmede yasak ifadeler kodla taranır.

**Güvenlik ağı:** Rüyada kendine zarar, şiddet ya da travma teması varsa (`hassas_icerik: true`) yanıtın başına bir ruh sağlığı uzmanına ve 112'ye yönlendiren not eklenir.

---

## 9. Ölçme: iyi olduğunu nereden biliyoruz?

İlke: **Ölçmediğin şeyi iyileştiremezsin.** Bir değişikliğin işe yarayıp yaramadığını hissiyatla değil, aynı test setiyle ölçerek anlarız.

### 9.1 Test seti

`eval/dataset/ruyalar_v1.jsonl`, 45 rüya. Her kayıtta rüya metni ve beklenen semboller var:

```json
{"id": "r031", "metin": "Rüyamda eski bir sandıktan gümüş bir anahtar çıkardım.",
 "beklenen_semboller": ["anahtar", "gumus"], ...}
```

Özel testler: bulunamaz testi ("uzay gemisi"), olumsuzlama testi ("örümcek görmedim"), çok kelimeli ifade ("ölmüş babam"), ağır içerik.

**Sınır:** Test seti EVREN'e ürettirildi ve henüz elle gözden geçirilmedi. İki rüya iki kez yazılmış, bazı beklenen listeleri eksik ya da yanlış (r009'daki "tas" kâsedir, taş değil).

### 9.2 Ölçütler (`degerlendirme/metrikler.py`)

| Ölçüt | Soru | Hesap |
|---|---|---|
| Sembol recall (kapsama) | Beklenen sembollerin kaçını bulduk? | bulunan beklenen / tüm beklenen |
| Sembol precision (isabet) | Bulduklarımızın kaçı doğru? | doğru bulunan / tüm bulunan |
| Eşleme doğruluğu | Doğru `symbol_id`'ye mi bağladık? | doğru eşleme / eşlenen |
| Kaynak çeşitliliği | Sembol başına kaç farklı kaynak? | ortalama farklı kaynak sayısı |
| Atıf kapsamı | Yorum bölümlerinin kaçı atıflı? | atıflı bölüm / tüm bölüm |
| Olumsuzlama hatası | "Görmedim" denen sembol yorumlandı mı? | sayı (hedef 0) |
| Yasak ifade | Kehanet, otorite, teşhis dili var mı? | sayı (hedef 0) |
| Sadakat (elle) | Yorum kaynağın söylemediğini söylüyor mu? | elle okunur |

**Recall ile precision arasındaki gerilim:** Her şeyi sembol sayarsan recall yükselir ama precision düşer; çok seçici olursan tersi. İkisine birlikte bakılır.

### 9.3 Sonuçlar

| Tarih | Ne değişti | Rüya | Recall | Precision | Atıf | Medyan süre |
|---|---|---|---|---|---|---|
| 2 Kasım | İlk ölçüm (düşünme açık) | 20 | %63 | %100 | %40 | ~538 sn (ort.) |
| 2 Kasım | sentez_v2 | 20 | %77 | %100 | %100 | ~196 sn (yalnız sentez) |
| 5 Kasım | Düşünme kapalı, hibrit getirme, sentez_v3 | 45 | %78 | %86 | %100 | 177 sn |
| 6 Kasım | cikarim_v3, eşleme düzeltmeleri | 45 | **%96** | %87 | %100 | ölçülemedi (önbellek) |
| 10 Kasım | cikarim_v4, paralel sentez, genel yorum | 45 | %96 | %87 | %100 | 165 sn |

Bütün koşularda olumsuzlama hatası 0, yasak ifade 0.

**Sayıları doğru okumak:**
- **Precision neden %87?** "Fazla" sayılanların çoğu gerçekten rüyada geçen semboller (bahçe, anne, baba, toprak, cami → mescit); test setinin beklenen listeleri eksik. Gerçekten yanlış olanlar az: "uzay gemisi" → gemi, "anahtarı düşürdüm" → düşmek. Ders: **ölçütün değeri, test setinin kalitesi kadardır.**
- **Süre:** Rüya başına medyan 177 saniye, hedef 30 saniye. v3 ile rüya başına sembol 3'ten 5,5'e çıktı, sentez uzadı. Modelin hızı düşmedi (12'den 16 token/sn'ye çıktı); yavaşlık daha çok metin yazmaktan. Daha iyi kapsama bedava gelmedi.
- **Önbellek tuzağı:** Bir koşuda çıkarım önceki denemenin önbelleğinden geldiği için süre gerçek değildi; o satıra süre yazılmadı. Ölçüm yaparken önbelleğin neyi değiştirdiğini bilmek gerekir.

**Sadakat (8 rüya elle okundu):** Uydurma atıf ya da kaynakta olmayan bir iddia görülmedi; olumsuzlanan örümcek yorumlanmadı; her yanıtta uyarı vardı. Görülen kusurlar: çeviri hatasının ("zikir") yoruma geçmesi ve bazı atıfların konuya gevşek bağlı olması (deniz kenarı bölümünde balık maddesi).

**Deneyler (10 Kasım, 15 rüyalık alt küme):**
- **D3 · Kaynak başına N:** N=2 tokenı %55 artırdı ama süreyi değiştirmedi (paralel istekler); N=3 süreyi %56 uzattı. Talimat sembol başına en çok 3 kaynak kullandığı için fazladan maddeler yoruma pek girmiyor. **N=1 kalıyor.**
- **D4 · Sentez modeli:** `mimo-v2.6-pro` ölçülen kalitede aynı, ama rüya başına ~55 sn daha yavaş ve %30 daha çok token. **deepseek kalıyor.**
- **D1/D2 · Vektör kolu ve reranker:** Getirme dört çeşitle koşuldu (hepsi, reranker'sız, vektörsüz, HyDE'siz), sıralamalar kaydedildi. Hangisinin doğru maddeyi bulduğunu bilmek için "doğru cevap" etiketi gerekiyor; etiketler **havuzlamayla** hazırlanır: her çeşidin ilk 5'i birleştirilir, yalnız bu havuz işaretlenir (TREC usulü). Ön karar için havuzu bir LLM hakem işaretliyor (gümüş etiket); kesin karar insan etiketleriyle verilecek. İlk bulgu: HyDE'yi kapatınca ilk 5 sonucun %93'ü aynı kalıyor, reranker'ı kapatınca %64'ü.

Çalıştırma: `uv run python eval/run_eval.py --dataset eval/dataset/ruyalar_v1.jsonl --etiket <ad>`. Rapor `data/raporlar/<tarih>_<etiket>.md`, özet satırı `docs/olcumler.md`.

---

## 10. Yazılım mühendisliği tarafı

### 10.1 Araçlar

| Araç | Ne işe yarar |
|---|---|
| **uv** | Python sürümünü ve paketleri kurar (`uv sync`), komut çalıştırır (`uv run ...`). Bağımlılıkların tek kaynağı `pyproject.toml`. |
| **pydantic** | Veri şemaları (`schemas.py`): `Madde`, `Sembol`, `Eslesme`, `Aday`, `Yorum`, `SorguKaydi`. Yanlış tipte ya da bilinmeyen alanlı veri hata verir. |
| **httpx** | HTTP istemcisi (EVREN çağrıları). Testlerde `MockTransport` ile ağa çıkmadan sahte cevap verilir. |
| **zeyrek** | Türkçe morfoloji, kök bulma. |
| **numpy** | Vektörlerin saklanması ve kosinüs hesabı. |
| **Gradio** | Web arayüzü. |
| **pytest** | Testler: 818 test geçiyor. |
| **ruff** | Kod denetimi (lint). Commit'ten önce temiz olmalı. |

### 10.2 Klasör yapısı ve katmanlar

```
src/ruya/
  config.py, schemas.py, hatalar.py, etik.py, dosya.py   ← temel
  text/turkce.py            ← normalleştirme, kök, arama terimleri
  llm/client.py, talimatlar.py   ← model çağrıları, talimat okuma
  ingest/                   ← kaynak ayrıştırıcıları
  enrich/                   ← çeviri birleştirme, sembol atama, koşul/yöntem/kapsam
  index/                    ← sözlük tabloları, parçalar, BM25, vektörler, depo
  pipeline/                 ← extract, map, hibrit, retrieve, synthesize, run
  degerlendirme/            ← metrikler, calistir, getirme_deneyi, hakem
app/gradio_app.py           ← arayüz
scripts/                    ← ince komut satırı betikleri
prompts/                    ← sürümlü talimatlar
sozluk/symbols.json         ← sözlük (git'te)
eval/dataset/               ← test seti (git'te)
data/                       ← bütün veri (git'e girmez)
tests/                      ← testler ve küçük örnek veriler (fixtures)
```

**Katman kuralı:** Her modül yalnızca izin verilen modülleri içe aktarabilir. Örneğin `pipeline`, `text`, `llm` ve `index`'i kullanabilir ama `enrich`'i kullanamaz (çevrimdışı iş çevrimiçi koda sızmasın). Ağır paketler (gradio, numpy gibi) yalnızca fonksiyon içinde içe aktarılır. `tests/test_mimari.py` bu kuralları otomatik denetler; kural bozulursa test kırmızı olur.

**Bağımlılık enjeksiyonu (`Bagimliliklar`):** Boru hattının dış dünyaya (API, depo, sözlük) açılan tek kapısı bir veri sınıfıdır. Gerçek çalışmada gerçek istemci verilir, testte sahtesi. Bu sayede boru hattı ağa çıkmadan, saniyeler içinde test edilir.

### 10.3 Test stratejisi

- **Birim testleri verisizdir:** `tests/fixtures/` içindeki birkaç satırlık örneklerle çalışır, gerçek veriye ihtiyaç duymaz.
- **Kontrat testleri (`-m veri`):** Gerçek `entries.jsonl` dosyasını denetler (her madde şemaya uyuyor mu, kimlikler benzersiz mi); veri yoksa kendiliğinden atlanır.
- **TDD (testle başlamak):** Davranış değişikliklerinde önce kırmızı test yazılır, sonra kod yeşile çekilir. Eşleme kuralları böyle eklendi.

### 10.4 Çalışma kuralları

- **Belge önce:** Şema değişikliği önce `docs/02` ve `docs/12`'de, sonra `schemas.py`'de yapılır.
- **Talimat sürümleme:** Bir ölçüm raporunda kullanılmış talimat dosyası bir daha değiştirilmez; yeni sürüm açılır (v3 raporda kullanıldığı için düzeltme v4 olarak yazıldı). Böylece her ölçüm tekrarlanabilir kalır.
- **Atomik commit:** Her commit tek mantıksal değişiklik, Türkçe, emir kipinde ("Eşlemedeki harf katlama yedeğini kaldır").
- **Gizli bilgi dosyaya yazılmaz.** API anahtarı yalnızca ortam değişkeninde.
- **Kod yalnızca `data/` altına veri yazar.**

### 10.5 Kodu kim yazdı?

Planlama ve doğrulama Claude Code'da, kodun bir kısmı **orkestra** ile EVREN ajanlarına yazdırıldı: Claude işi küçük görevlere böler (önce kırmızı test, sonra kod), ajanlar yazar ve kendi kontrol komutlarıyla sınar, Claude farkı okuyup doğrular. Amaç Claude kullanımını azaltmaktı.

---

## 11. Denenip vazgeçilenler: en öğretici kısım

İyi mühendislik, neyin işe yaramadığını bilmektir.

| Denenen | Neden vazgeçildi | Ders |
|---|---|---|
| Chroma vektör veritabanı | 12 bin parça için numpy dizisinde tam tarama yeterli; bağımlılık azaldı | Ölçeğe uygun en basit araç |
| Yerel embedding (`multilingual-e5-large`) ve yerel reranker (`bge-reranker`) | EVREN'deki Qwen3 modelleri hızlı (0,3–0,4 sn), torch kurmak gerekmiyor | Altyapı yükü de bir maliyet |
| **Sembol adlarını vektörle eşlemek** | "yılan" 0,82 ile `akrep`e, 0,60 ile doğru `yilan`a yakın çıktı. Aynı skorda doğru ve yanlış eşleme olduğu için hiçbir eşik işe yaramadı | Embedding "aynı türden" ile "aynı şey"i ayıramaz; kesin eşleme gereken yerde kural kullan |
| **Türkçe harf katlama** ("tas" → taş) | "tas" (kâse) ile "taş", "kus" ile "kuş" ayrı kelimeler; gerçek kelimeleri yanlış sembole bağlıyordu | Dil kurallarını basitleştirmek anlamı bozabilir |
| Kaynak başına N = 2 madde | Tek çağrılı sentezde 12 dakika sürdü; paralel sentezde süre aynı ama token %55 fazla ve kazanç görünmüyor (D3) | Bağlam penceresine konan her şey hız ya da para demektir |
| Tek istekte bütün yorum (`sentez_v4`) | Uzun metni tek istekte yazmak 2–6 dakika; sembol başına paralel istekler %40 kısalttı | Bağımsız parçaları paralel iste |
| Kısa çıkarım talimatı (`cikarim_v5`) | En çok 10 sembol ve kısa HyDE; uzun rüyada süre kısaldı ama beklenen sembolleri kesti, kısa rüyada hiçbir şey değişmedi | Önce neyin yavaş olduğunu ölç; geçidin dalgalanması talimat farkından büyüktü |
| Sentezde `mimo-v2.6-pro` | Kalite aynı, daha yavaş ve daha pahalı (D4) | Büyük model her işte daha iyi değil |
| DeepSeek'in düşünme adımı açık | 7–14 dakikalık yanıtlar; bu iş akıl yürütme gerektirmiyor | Model ayarları göründüğünden önemli |
| Geniş koşul kuralları (%23) | Rüyada görülen kişiyi rüya sahibi sandı; daraltılınca %9,5 | Kural kesinliği kapsamadan önemli |
| LLM ile koşul çıkarma | 10.801 madde günler sürerdi | Ucuz kural + zararsız kaçırma |
| Colab + Drive | Bilgisayarda çalışmak daha basit | Ortamı sadeleştir |
| Streamlit | Gradio daha az kodla aynı işi yapıyor | — |

---

## 12. Bilinen sorunlar ve sıradaki işler

**Bilinen sorunlar:**
1. **Hız:** Medyan 165 saniye, hedef 30 saniye. Süre büyük ölçüde geçidin yüküne bağlı (aynı istek 18 ile 151 sn arasında sürdü). Arayüz sonucu geldikçe gösterdiği için bekleme daha az hissediliyor.
2. **Gözden geçirilmemiş içerik:** Sözlük, test seti ve çeviriler insan gözünden geçmedi.
3. **Getirme gevşekliği:** Bazı atıflar konuya gevşek bağlı; eşik (0,15) test setiyle ayarlanmadı.
4. **Kategoriler kullanılmıyor:** Bab ve HVDC kategorileri sözlükte var, kodda yok.
5. **Eşzamanlılık sınırı:** Geçit hesap başına 4 eşzamanlı istek kabul ediyor; iki rüya aynı anda yorumlanırsa ya da ölçümle kod yazan agent'lar aynı anda çalışırsa istekler 429 alır.

**Senin yapacakların:** sözlüğü, test setini ve çevirileri gözden geçirmek; 10 yanıtın atıflarını, 20 koşulu, 20 kapsam etiketini elle kontrol etmek; Brill ve OpenITI lisanslarını doğrulamak; `v0.1-mvp` etiketine karar vermek.

**Sıradaki işler:** Sıra ve kararlar [15 · Kalan işler planı](15-kalan-isler-plani.md)'nda. D1/D2 etiket bekliyor; D3 ve D4 bitti, D5 yapılmayacak.

---

## 13. Kendini sına

Cevaplar altta. Önce kendin düşün.

1. RAG olmadan bir LLM'e "Nablusi yılan için ne der?" diye sorsak sorun ne olur?
2. Madde kimliği neden satır numarasından türetiliyor ve bunun bedeli ne?
3. BM25 ile vektör aramasının birbirine göre güçlü ve zayıf yanları nedir?
4. HyDE metni neden kullanıcıya gösterilmiyor?
5. RRF'de bir madde hiçbir listede birinci değilken nasıl kazanır?
6. Reranker neden ilk aramadan sonra, tek başına değil?
7. Sembol eşlemesi neden LLM ile değil kodla yapılıyor?
8. "Gümüş anahtar" neden `anahtar`a, "kız çocuğu" neden `kiz`e eşleniyor?
9. Model, verilmemiş bir madde kimliğine atıf yaparsa ne olur?
10. Koşul etiketleri neden LLM ile değil kurallarla çıkarıldı?
11. Precision %87 iken sistem gerçekten %13 yanlış mı?
12. Talimat örneklerine test setinden cümle koymak neden yanlış?
13. Bir talimat dosyası ölçümde kullanıldıktan sonra neden değiştirilmez?
14. Rüyalar neden varsayılan olarak önbelleğe yazılmıyor?

**Cevaplar:**

1. Ezberden, kaynak gösteremeden, uydurabilecek bir cevap verir. RAG cevabı gerçek maddelere bağlar ve atıfı denetlenebilir kılar.
2. Böylece yeniden ayrıştırmada kimlik değişmez ve test seti, çeviri, atama hep aynı maddeyi gösterir. Bedeli: ham dosya dondurulmak zorunda (commit sabitleme, SHA256).
3. BM25 kesin kelimeyi kaçırmaz ama eş anlamlıyı bilmez; vektör anlamı yakalar ama kesin kelimeyi ve nadir terimleri kaçırabilir. Birlikte kullanınca açıklarını kapatırlar.
4. Çünkü uydurmadır; yalnızca gerçek maddelere üslupça benzediği için aramaya yardım eder. Kaynak sayılırsa sistem kendi uydurmasına atıf yapmış olur.
5. RRF sıraları toplar; her listede iyi sıradaki bir madde, tek listede birinci olandan fazla puan toplayabilir.
6. Reranker sorgu ile her adayı birlikte okuduğu için yavaştır; 12 bin parçaya uygulanamaz. Hızlı arama 40 adaya indirir, reranker bunları dikkatle sıralar.
7. Deterministik, hızlı ve test edilebilir olmalı. Vektörle eşleme denendi; "yılan"ı `akrep`e bağladı.
8. Türkçede sıfat + isimde baş isim sondadır ("gümüş anahtar"); iyelikli tamlamada ("kız çocuğu") anlamı taşıyan ilk kelime çoğu zaman sözlükte vardır. Kural son kelimenin iyelik ekine bakar.
9. Atıf kodda atılır ve sayılır (uydurma atıf). Alıntı metinde geçmezse alıntı boşaltılır.
10. LLM ile 10.801 madde günler sürerdi. Kural ucuz ve tekrarlanabilir; kaçırdığı madde yine sıralamada kalır.
11. Hayır. "Fazla" sayılanların çoğu rüyada gerçekten geçen ama test setinin beklenen listesinde olmayan semboller. Test seti gözden geçirilince sayı değişir.
12. Model sınav sorularının cevabını görmüş olur, ölçüm gerçek başarıyı değil ezberi gösterir (veri sızıntısı).
13. Ölçümün tekrarlanabilir kalması için: rapordaki sayı hangi talimatla alındıysa o talimat aynen durmalı.
14. Rüya kişisel veridir; disk önbelleği düz dosyadır. Yalnızca repodaki test seti için açılır.

---

## 14. Dosya haritası: neye nereden bakılır

| Merak ettiğin | Bak |
|---|---|
| Bir rüyanın dört adımı | `src/ruya/pipeline/run.py` → `extract.py`, `map.py`, `hibrit.py`, `synthesize.py` |
| Model adları, eşik, N, adres | `src/ruya/config.py` |
| Veri şemaları | `src/ruya/schemas.py`, `docs/02` |
| Talimatlar | `prompts/cikarim_v4.md`, `prompts/sentez_v3.md` |
| Sözlük | `sozluk/symbols.json` |
| Türkçe normalleştirme ve kök | `src/ruya/text/turkce.py` |
| Hibrit arama tasarımı ve gerekçeleri | `docs/13-hibrit-getirme.md` |
| Klasik tabirin katmanları | `docs/05-yorum-yontemi.md` |
| Etik kurallar ve uyarı metni | `docs/07-etik-ve-hukuk.md`, `src/ruya/etik.py` |
| Ölçüm sonuçları | `docs/olcumler.md`, `data/raporlar/` |
| Teknoloji kararları | `docs/04-teknoloji-secimi.md` |
| Katman kuralları ve modül imzaları | `docs/12-kod-yapisi-ve-sozlesmeler.md` |
| Takvim ve kalan işler | `docs/08-yol-haritasi-takvim.md` |
| Arayüz | `app/gradio_app.py`, `scripts/arayuz_ac.py` |
| Bir rüyayı komut satırından denemek | `scripts/ruya_dene.py` |
| Veriyi baştan kurmak | `scripts/download_sources.py` → `scripts/maddeleri_kur.py` → `scripts/hibrit_indeks_kur.py` |
