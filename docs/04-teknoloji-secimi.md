# 04 · Teknoloji Seçimi

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Biçim: Her karar için bağlam, seçenekler, karar, gerekçe ve ne zaman yeniden düşünüleceği. Kararlar **TK-xx** koduyla numaralı.
> Sürüm numaraları kurulum sırasında `pyproject.toml` dosyasında sabitlenecek. Bu belgede yazanlar 21 Ekim 2026 itibarıyla geçerli.

## Özet tablo

| Alan | Karar | Durum |
|---|---|---|
| Dil ve sürüm | Python 3.12 | ✅ Kararlaştırıldı |
| Paket yöneticisi | uv | ✅ |
| LLM sağlayıcı | Claude API (Anthropic Python SDK) | ✅ |
| LLM modeli | `claude-opus-5-5` (varsayılan); Sonnet 5.5 ve Haiku 5.5 Aşama 4'te karşılaştırılacak | ⚠️ **Senin onayın gerekli** |
| Embedding | `intfloat/multilingual-e5-large`; aday: `Qwen/Qwen3-Embedding-0.6B` | ✅ (Aşama 2'de ölçülecek) |
| Vektör deposu | Chroma (yerel, gömülü) | ✅ |
| Reranker | `BAAI/bge-reranker-v2-m3` | 🕓 Aşama 2 |
| Türkçe morfoloji | zeyrek | ✅ |
| Veri doğrulama | Pydantic v2 | ✅ |
| Arayüz | Streamlit | ✅ |
| Test ve kalite | pytest, ruff | ✅ |
| Sürüm kontrolü | Git ve GitHub (özel repo) | ⚠️ **Senin onayın gerekli** |
| Yerel LLM | Ollama ile Gemma 4 / Qwen | 🕓 Aşama 4 deneyi |

---

## TK-01 · Python 3.12

- **Seçenekler:** 3.11, 3.12, 3.13
- **Karar:** 3.12
- **Gerekçe:** PyTorch, sentence-transformers ve chromadb Windows için 3.12'de hazır kurulum paketi (wheel) sunuyor ve en az sürprizi bu sürüm çıkarır. 3.13'te bazı bilimsel paketler geç destek verebiliyor (doğrulanmadı). uv istenen Python sürümünü kendisi indirebildiği için sistemdeki Python'a dokunmak gerekmiyor.
- **Yeniden düşün:** Bütün bağımlılıklar 3.13'ü sorunsuz desteklediğinde.

## TK-02 · Paket yöneticisi: uv

- **Seçenekler:** `venv` ve `pip`, Poetry, uv
- **Karar:** uv
- **Gerekçe:**
  - Tek araç hem Python sürümünü hem sanal ortamı hem bağımlılıkları yönetiyor.
  - Çok hızlı.
  - `uv.lock` dosyası kurulumu tekrarlanabilir kılıyor.
  - Windows'ta venv betiklerinin Türkçe karakterli yollarda yaşattığı sorunları da azaltıyor.
- **Not:** `pip` yolu da [10-kurulum-rehberi.md](10-kurulum-rehberi.md) belgesinde yedek olarak anlatılacak.

## TK-03 · LLM sağlayıcı: Claude API

- **Seçenekler:** Claude API, yerel model (Ollama), diğer bulut sağlayıcılar
- **Karar:** Claude API (resmî `anthropic` Python SDK)
- **Gerekçe:**
  - **Yerleşik kaynak gösterme.** `search_result` içerik blokları ve `citations` ile her iddia yapılandırılmış biçimde kaynağına bağlanıyor. Verilen belgelerde olmayan bir kaynağa atıf yapılması API düzeyinde engelleniyor. Projenin "uydurmama" hedefi (H3) için en kritik özellik bu.
  - **Yapılandırılmış çıktı.** Sembol çıkarımı için JSON şeması kullanılabiliyor (`output_config.format`).
  - **Batch API.** Çeviri gibi toplu işler %50 indirimli.
  - **Prompt önbelleği.** Sabit sistem talimatının maliyetini düşürüyor.
- **Bilinen kısıt:** Atıf ve yapılandırılmış çıktı aynı istekte kullanılamıyor (400 hatası). Bu yüzden boru hattında iki ayrı çağrı var.
- **Yeniden düşün:** Aşama 4'teki yerel model deneyi kaliteyi yakalarsa ya da maliyet bütçeyi aşarsa.

## TK-04 · Model seçimi ⚠️ senin kararın

21 Ekim 2026 itibarıyla güncel fiyatlar (milyon token başına, girdi / çıktı):

| Model | Kimlik | Girdi | Çıktı | Not |
|---|---|---|---|---|
| Claude Opus 5.5 | `claude-opus-5-5` | 4 $ | 20 $ | Varsayılan ve en yetenekli genel model |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2 $ | 10 $ | Hızlı ve dengeli |
| Claude Haiku 5.5 | `claude-haiku-5-5` | 0,10 $ | 0,50 $ | 100 bin token altındaki istemler için. Çok ucuz. |

- **Önerim:** Üç işin hepsinde (çıkarım, sentez, çeviri) **Opus 5.5** ile başla. Çıkarımda `effort: low`, sentezde `effort: medium` kullan. Sonra Aşama 4'te aynı test setiyle Sonnet 5.5 ve Haiku 5.5'i dene ve kaliteyi ölçerek ucuzla.
- **Neden önce en güçlü model:** "Çalışmıyor" dediğinde sorunun modelden mi, senin boru hattından mı kaynaklandığını ayırmak kolaylaşır. Önce kalite tavanını görürsün, sonra maliyeti düşürürsün.
- **Rüya başına tahmini maliyet:** Yaklaşık 10 bin girdi ve 1.500 çıktı tokenı varsayımıyla Opus 5.5'te yaklaşık 7–10 sent, Sonnet 5.5'te yaklaşık 3,5 sent, Haiku 5.5'te 1 sentin altında. Düşünme (thinking) tokenları bu tahmine dahil değil, ölçülecek.
- **Uygulama notları:**
  - Opus 5.5'te düşünme kapatılamaz. Maliyet ve derinlik `output_config.effort` ile ayarlanır.
  - Opus 5.5'in güvenlik sınıflandırıcıları bir isteği reddedebilir (`stop_reason: "refusal"`). Bu durum için sunucu tarafı yedek model (`fallbacks: "default"`) etkinleştirilecek.
  - Model adları `config.py` içinde tek bir yerde duracak.
- **Senden beklenen:** Aylık bütçe tavanı (önerim 10 $) ve bu önerinin onayı.

## TK-05 · Embedding modeli

- **Bağlam:** Arama Türkçe sorgularla, Arapça, İngilizce ve Türkçe metinler üzerinde yapılacak. Bu yüzden diller arası (cross-lingual) arama gerekiyor.
- **Seçenekler:**

| Model | TR-MTEB ortalama / retrieval | Not |
|---|---|---|
| `intfloat/multilingual-e5-large` (560M) | 66,82 / 60,62 | TR-MTEB'in en iyi açık modeli. Türkçe–İngilizce eşleştirmede 99,43 |
| `Qwen/Qwen3-Embedding-0.6B` | TR-MTEB'de yok | Çok dilli MTEB'de 64,33. Apache-2.0, 32K bağlam |
| `BAAI/bge-m3` | TR-MTEB'de yok | Çok dilli MTEB'de 59,56 |
| Türkçeye özel modeller (~110M) | 63,42 / 52,75 | Türkçe–İngilizce eşleştirmede yalnızca 37,7. **Diller arası iş için uygun değil.** |
| OpenAI `text-embedding-3-small` | 66,61 / 64,99 | En iyi retrieval puanı, ama ücretli ve ikinci bir sağlayıcı |

- **Karar:** Varsayılan olarak `multilingual-e5-large`. Aşama 2'de `Qwen3-Embedding-0.6B` ile kendi test setinde karşılaştırılacak.
- **Dikkat:** e5 modeli `query: ` ve `passage: ` önekleri ister. Unutulursa kalite sessizce düşer.
- **Not:** Vektör arama yalnızca yedek yol olduğundan bu karar projenin kalbi değil. Yine de öğrenme açısından değerli bir deney.

## TK-06 · Vektör deposu: Chroma

- **Seçenekler:** Chroma, Qdrant (yerel mod), LanceDB, FAISS, pgvector
- **Karar:** Chroma, kalıcı istemci modunda (`PersistentClient`)
- **Gerekçe:** Windows'ta sunucusuz çalışıyor ve pip ya da uv ile kuruluyor. Metadata filtresi (`where={"symbol_id": ...}`) projenin ana getirme yolu için birebir uygun. Tam metin filtresi de (`where_document`) var.
- **Yeniden düşün:** Gerçek hibrit (BM25 ve vektör) arama gerekirse. Bu durumda Qdrant'a geçilir.

## TK-07 · Reranker (Aşama 2)

- **Karar:** `BAAI/bge-reranker-v2-m3` (0,6B parametre, Apache-2.0, çok dilli)
- **Ne zaman kullanılır:** Yalnızca bir sembol için kaynak başına N'den fazla madde varsa. Böylece CPU'da gereksiz yük oluşmaz.

## TK-08 · Türkçe morfoloji: zeyrek

- **Seçenekler:** zeyrek, Zemberek (Java), Stanza, spaCy Türkçe modelleri
- **Karar:** zeyrek (MIT lisanslı, 0.1.3)
- **Gerekçe:** pip ile kuruluyor ve Java gerektirmiyor. Sembolleri zaten LLM'den yalın hâlde aldığımız için zeyrek yalnızca ikinci bir kontrol katmanı. Hâlâ alfa aşamasında olması bu yüzden kabul edilebilir.
- **Kendin yazacağın parça:** Türkçe küçük harf dönüşümü. Python'da `"I".lower()` "i" verir, oysa Türkçede "ı" olmalı.

## TK-09 · Arayüz: Streamlit

- **Seçenekler:** Streamlit, Gradio, Chainlit, FastAPI ile ayrı bir ön yüz
- **Karar:** Streamlit
- **Gerekçe:** En az kodla çalışan bir web sayfası çıkarıyor. Sekmeler, genişleyen kutular ve tablolar hata ayıklama ekranı için birebir uygun.

## TK-10 · Kalite araçları

- **pytest:** Birim testleri.
- **ruff:** Hem kod denetimi (lint) hem biçimlendirme. Ayrı bir black kurulumuna gerek bırakmıyor.
- **Pydantic v2:** Şemalar ve `.env` okuma (pydantic-settings).
- **Ragas veya DeepEval yok, en azından şimdilik.** Önce elle yazılmış basit ölçüm betikleri. Ölçütleri kendin yazmak, neyin neden ölçüldüğünü öğretir.

## TK-11 · Sürüm kontrolü ⚠️ senin kararın

- **Karar:** Git kullanılacak. Uzak depo için önerim **GitHub'da özel (private) bir repo**.
- **Neden özel:** `data/` zaten git'e eklenmiyor. Ama prompt dosyalarında ve testlerde kendi rüyaların bulunabilir. Herkese açık yapmak istersen önce bu dosyalar temizlenmeli.
- **Commit düzeni:**
  - Commitler **atomik** olacak: her commit tek bir mantıksal değişiklik içerir.
  - Mesajlar Türkçe ve emir kipinde yazılacak.
  - Commitlerde **Claude imzası olmayacak**: `Co-Authored-By` satırı ya da "Generated with" notu eklenmez.
  - Push'u sen yapacaksın.
  - Aşama sonlarında etiket atılacak (`v0.1-mvp` gibi).
  - Bu kurallar repo kökündeki `CLAUDE.md` dosyasında da yazılı.

## TK-12 · Yerel LLM (Aşama 4, isteğe bağlı)

- **Seçenekler:** Ollama ya da LM Studio ile Gemma 4 (12b sürümü yaklaşık 8 GB) veya güncel Qwen modelleri
- **Karar:** Ertelendi. Aşama 4'te deney olarak yapılacak.
- **Kısıt:** Yerel modellerde Claude'un atıf API'si yok. Atıflar `[S1]` biçimli kimliklerle ve kod tarafında doğrulamayla yapılacak.
- **Gerekli bilgi:** Ekran kartın ve VRAM miktarın (bkz. [09-riskler-ve-acik-sorular.md](09-riskler-ve-acik-sorular.md)).
