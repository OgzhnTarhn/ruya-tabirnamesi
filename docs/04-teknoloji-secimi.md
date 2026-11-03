# 04 · Teknoloji Seçimi

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Biçim: Her karar için bağlam, seçenekler, karar, gerekçe ve ne zaman yeniden düşünüleceği. Kararlar **TK-xx** koduyla numaralı.
> Sürüm numaraları kurulum sırasında `pyproject.toml` dosyasında sabitlenecek. Bu belgede yazanlar 21 Ekim 2026 itibarıyla geçerli.
> Güncelleme (22 Ekim 2026): Çalıştırma ortamı Colab ve Drive oldu (TK-13). Arayüz Streamlit yerine Gradio (TK-09).
> Güncelleme (31 Ekim 2026): Colab ve Drive bırakıldı; kod, çalıştırma ve veri bilgisayarda (TK-13, revizyon).

## Özet tablo

| Alan | Karar | Durum |
|---|---|---|
| Çalışma ortamı | Her şey **bilgisayarda**; veri `data/` altında, git'e girmez | ✅ Kararlaştırıldı (31 Ekim revizyonu) |
| Dil ve sürüm | Python ≥3.11 (uv ile) | ✅ |
| Paket yönetimi | `pyproject.toml` + uv | ✅ |
| LLM sağlayıcı | EVREN LLM geçidi (OpenAI uyumlu API, `httpx`) | ✅ 31 Ekim revizyonu |
| LLM modeli | `deepseek-v4.1-flash` (bütün işler) | ✅ 31 Ekim kararı |
| Embedding | `intfloat/multilingual-e5-large` ya da EVREN'deki `qwen3-embedding-8b` | 🕓 Aşama 2'de ölçülecek |
| Vektör deposu | Chroma (yerel, gömülü) | ✅ |
| Reranker | EVREN `qwen3-reranker-8b` ([13](13-hibrit-getirme.md), 3 Kasım; önceki seçim `bge-reranker-v2-m3`) | ✅ |
| Türkçe morfoloji | zeyrek | ✅ |
| Veri doğrulama | Pydantic v2 | ✅ |
| Arayüz | Gradio (yerelde, `share` kapalı) | ✅ |
| Test ve kalite | pytest, ruff, nbstripout | ✅ |
| Sürüm kontrolü | Git ve GitHub (özel repo) | ⚠️ **Senin onayın gerekli** |
| Açık model LLM | Colab GPU'sunda Gemma 4 / Qwen | 🕓 Aşama 4 deneyi |

---

## TK-01 · Python ≥3.11

- **Seçenekler:** 3.11, 3.12, 3.13
- **Karar:** `requires-python = ">=3.11"`. Python'u uv kurar ve yönetir.
- **Gerekçe:** İlk kararda Colab'in sunduğu sürüme uyum gözetilmişti (22 Ekim). Colab bırakıldıktan sonra (31 Ekim) da alt sınırı değiştirmek için bir neden yok.
- **Yeniden düşün:** Bir bağımlılık 3.11'i bırakırsa.

## TK-02 · Paket yönetimi: pyproject + uv

- **Seçenekler:** `venv` ve `pip`, Poetry, uv
- **Karar:** Bağımlılıkların tek kaynağı `pyproject.toml`; kurulum ve çalıştırma uv ile (`uv sync`, `uv run`). Ağır paketler isteğe bağlı ekte: `uv sync --extra hepsi`. (22 Ekim'deki ilk kararda Colab'de `pip install -e .` kullanılıyordu.)
- **Gerekçe:**
  - Tek araç hem Python sürümünü hem sanal ortamı hem bağımlılıkları yönetiyor.
  - Çok hızlı.
  - `uv.lock` dosyası kurulumu tekrarlanabilir kılıyor.
  - Windows'ta venv betiklerinin Türkçe karakterli yollarda yaşattığı sorunları da azaltıyor.
- **Not:** Sürümler `pyproject.toml`'da alt sınırla yazılır; tam sürümleri `uv.lock` sabitler.

## TK-03 · LLM sağlayıcı: EVREN LLM geçidi (31 Ekim 2026 revizyonu)

- **Seçenekler:** Claude API, EVREN LLM geçidi, yerel model (Ollama)
- **İlk karar (21 Ekim):** Claude API. En önemli gerekçesi yerleşik kaynak göstermeydi (`search_result` blokları ve Citations API: verilmemiş bir kaynağa atıf API düzeyinde engelleniyor). Ek olarak Batch API (%50 indirim) ve prompt önbelleği vardı.
- **Revizyon (31 Ekim):** Claude API kullanılamıyor. Yerel model, bilgisayarda GPU olmadığı ve küçük modeller klasik Arapçada zayıf kaldığı için elendi. Karar: **EVREN LLM geçidi** (`https://evren-llmapi.ssyz.org.tr`).
- **Gerekçe:**
  - OpenAI uyumlu API; JSON şemasıyla yapılandırılmış çıktıyı destekliyor (31 Ekim'de örnek bir Nablusi maddesiyle denendi).
  - Modeller 1 Aralık 2026'ya kadar ücretsiz; günde 15 milyon token kota. Bütün korpusun çevirisine yeter.
  - Aynı geçitte embedding (`qwen3-embedding-8b`) ve reranker (`qwen3-reranker-8b`) modelleri de var; Aşama 2'de yerel model kurmadan kullanılabilir.
- **Bedeli:**
  - **Atıf API'si yok.** Atıflar numaralı kaynaklar ve JSON çıktısıyla alınır, kodda doğrulanır ([03](03-mimari.md), adım 4). Uydurma atıf engellenmez ama her seferinde yakalanır ve sayılır.
  - **Batch API yok.** Toplu işler eşzamanlı isteklerle yapılır; disk önbelleği sayesinde kesilen iş kaldığı yerden devam eder.
  - **Servis kesintileri.** 31 Ekim denemesinde bazı modeller "dolu" yanıtı verdi ya da zaman aşımına uğradı. İstemci yeniden dener ([03](03-mimari.md), bölüm 5.2).
  - **Ücretsizlik süreli.** 1 Aralık'tan sonraki fiyat belli değil; ağır işler (bütün korpusun çevirisi) bu tarihten önce bitirilmeli.
  - **Gizlilik.** Rüya metni EVREN sunucularına gider ([07](07-etik-ve-hukuk.md)).
- **Yeniden düşün:** Hafta 1 denemesinde çeviri ya da sembol atama kalitesi yetersiz çıkarsa, servis sürekli kesilirse ya da 1 Aralık sonrası fiyat bütçeyi aşarsa. İstemci tek modülde olduğu için sağlayıcı değişikliği `llm/client.py` ve `config.py` ile sınırlı kalır.

## TK-04 · Model seçimi: `deepseek-v4.1-flash` (31 Ekim 2026)

- **İlk öneri (21 Ekim):** Claude Opus 5.5, Aşama 4'te Sonnet 5.5 ve Haiku 5.5 ile karşılaştırma. TK-03 revizyonuyla geçersiz oldu.
- **Karar:** Ürün içi LLM işlerinde (çıkarım, sentez, sembol atama, koşullar) **`deepseek-v4.1-flash`**. Korpus çevirisi çevrimdışı yapıldı ve bitti ([02](02-veri-kaynaklari-ve-semasi.md), bölüm 5). Yedek model kullanılmaz; "dolu" yanıtında aynı model yeniden denenir.
- **Gerekçe:** 31 Ekim denemesinde geçitteki üç sohbet modelinden yalnızca bu yanıt verdi; şemaya uygun JSON döndürdü, sembolü doğru buldu, çevirisi iyiydi. Tek modelle başlamak sistemi sade tutar.
- **Gözlenen sorun:** Örnek çevirinin sonuna anlamsız bir kelime ("ürün") eklemişti. Hafta 1'deki H3 puanlaması bunun ne sıklıkta olduğunu gösterecek.
- **Uygulama notları:**
  - Model düşünme (reasoning) tokenları üretir; bunlar `completion_tokens`'a dahildir. Kısa bir istekte bile yüzlerce token tutabilir; `max_tokens` buna göre geniş verilir.
  - Model adları `config.py` içinde tek bir yerde durur. Her iş için ayrı sabit (`MODEL_CIKARIM`, `MODEL_SENTEZ`…) korunur; ileride işlere farklı modeller atanabilir.

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
- **Gerekçe:** Sunucusuz çalışıyor ve pip ile kuruluyor. Metadata filtresi (`where={"symbol_id": ...}`) projenin ana getirme yolu için birebir uygun. Tam metin filtresi de (`where_document`) var.
- **Konum:** İndeks `data/index/chroma` altında kurulur (bkz. [11](11-calisma-ortami.md), bölüm 3).
- **Yeniden düşün:** Gerçek hibrit (BM25 ve vektör) arama gerekirse. Bu durumda Qdrant'a geçilir.

## TK-07 · Reranker (Aşama 2)

- **Karar:** `BAAI/bge-reranker-v2-m3` (0,6B parametre, Apache-2.0, çok dilli)
- **Ne zaman kullanılır:** Yalnızca bir sembol için kaynak başına N'den fazla madde varsa. API'deki reranker ya da yerelde CPU ile çalışır.

## TK-08 · Türkçe morfoloji: zeyrek

- **Seçenekler:** zeyrek, Zemberek (Java), Stanza, spaCy Türkçe modelleri
- **Karar:** zeyrek (MIT lisanslı, 0.1.3)
- **Gerekçe:** pip ile kuruluyor ve Java gerektirmiyor. Sembolleri zaten LLM'den yalın hâlde aldığımız için zeyrek yalnızca ikinci bir kontrol katmanı. Hâlâ alfa aşamasında olması bu yüzden kabul edilebilir.
- **Kendin yazacağın parça:** Türkçe küçük harf dönüşümü. Python'da `"I".lower()` "i" verir, oysa Türkçede "ı" olmalı.

## TK-09 · Arayüz: Gradio (22 Ekim'de Streamlit'ten değişti)

- **Seçenekler:** Streamlit, Gradio, Chainlit, FastAPI ile ayrı bir ön yüz
- **Karar:** Gradio, `gr.Blocks` ile
- **Gerekçe:** Karar Colab döneminde verildi: Gradio notebook hücresinin içinde doğrudan açılıyordu; Streamlit ise Colab'de ek bir tünel servisi gerektiriyordu. Bilgisayarda ikisi de çalışır; Gradio'da kalınması için yeniden yazmaya değecek bir neden yok. Gradio'da da sekme (`gr.Tab`), açılır kutu (`gr.Accordion`) ve tablo (`gr.Dataframe`) var, yani hata ayıklama ekranı aynen yapılabiliyor.
- **Güvenlik:** `launch(share=True)` **kullanılmaz**. Bu ayar herkese açık bir link üretir ve linki bulan herkes senin API anahtarınla sorgu çalıştırabilir.
- **Yeniden düşün:** Uygulama bir gün sunucuya taşınırsa.

## TK-10 · Kalite araçları

- **pytest:** Birim testleri.
- **ruff:** Hem kod denetimi (lint) hem biçimlendirme. Ayrı bir black kurulumuna gerek bırakmıyor.
- **Pydantic v2:** Şemalar ve `.env` okuma (pydantic-settings).
- **nbstripout:** Notebook çıktıları commit'ten önce otomatik temizlenir. Çıktılarda rüya metni ya da API yanıtı kalmaz.
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

## TK-12 · Açık model LLM (Aşama 4, isteğe bağlı)

- **Seçenekler:** Colab GPU'sunda Gemma 4 ya da güncel Qwen modelleri. Ollama ile çalıştırılabilir ya da `transformers` ile 4-bit sıkıştırmayla yüklenebilir.
- **Karar:** Ertelendi. Aşama 4'te deney olarak yapılacak. Senin bilgisayarının ekran kartı kullanılmaz.
- **Kısıt:** Atıflar zaten numaralı kaynaklar ve kodda doğrulamayla yapıldığı için (TK-03) açık modele geçmek boru hattını değiştirmez.
- **Bilinmeyen:** Ücretsiz Colab GPU'sunun (T4, 16 GB) hangi model boyutunu kaldıracağı. Aşama 4'te denenecek, sığmazsa daha küçük bir model seçilecek.

## TK-13 · Çalışma ortamı: Colab ve Drive (22 Ekim 2026)

- **Seçenekler:**
  - Her şey bilgisayarda
  - Kod bilgisayarda; çalıştırma Colab'de; veri Drive'da
  - Bulut sunucu (VM)
- **Karar:** Kod bilgisayarda yazılır ve GitHub'a gider. Bütün çalıştırma Colab'de yapılır. Veri, önbellekler ve raporlar Google Drive'da (`MyDrive/ruya-tabirnamesi/`) durur. Ayrıntılar: [11-calisma-ortami.md](11-calisma-ortami.md).
- **Gerekçe:** Senin tercihin: veri seti bilgisayara inmesin, GPU gerektiren işler Colab'de yapılsın. Ek faydaları:
  - Ücretsiz GPU.
  - Gizli bilgiler için Colab Secrets.
  - Drive sayesinde oturumlar arası kalıcılık.
- **Bedeli:**
  - Kod değişikliğini Colab'de görmek için önce commit ve push, sonra `git pull` gerekir. Bu, geliştirme döngüsünü biraz yavaşlatır.
  - Colab oturumları zaman aşımına uğrar.
  - Drive bağlantısı yavaştır.

  Bu bedeller "notebook'lar ince, mantık `src/` paketinde" kuralıyla ve [11](11-calisma-ortami.md)'deki Drive kurallarıyla hafifletilir.
- **Yeniden düşün:** Colab sınırları işi gerçekten engellerse. Bu durumda Colab Pro ya da küçük bir bulut sunucu düşünülür.
- **Revizyon (31 Ekim 2026): her şey bilgisayarda.** LLM ve embedding API'den alınınca GPU gerekçesi ortadan kalktı. Veri küçük (ham kaynaklar 10 MB'ın altında) ve `data/` git'e girmediği için lisans ve gizlilik koşulları bilgisayarda da korunuyor. Colab'in bedelleri (push/pull döngüsü, oturum kopmaları, Drive yavaşlığı, Chroma'nın zip yedeği, gizli repo için token) kalktı. Ayrıntılar: [11](11-calisma-ortami.md).
