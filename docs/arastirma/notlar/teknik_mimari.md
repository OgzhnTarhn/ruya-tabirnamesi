# Türkçe, çok kaynaklı rüya tabiri RAG sistemi: teknik mimari ve araç seçimi (Ekim 2026)

> Kapsam notu: Bu notlar Ekim 2026 itibarıyla yapılan web araştırmasına dayanır. Kaynağı olan her iddia satır içinde linklidir. "[DOĞRULANMADI]" etiketi, arama sırasında birincil kaynakla teyit edemediğim (çoğunlukla eğitim bilgisine dayanan) iddiaları gösterir. "Inferences" bölümleri benim çıkarımım/önerimdir, kaynaklı bulgu değildir.

## 1. Türkçe ve çok dilli embedding modelleri (Türkçe performans, boyut, lisans, diller arası arama)

### Takeaway
Türkçe için yayımlanmış en kapsamlı karşılaştırma (TR-MTEB, EMNLP 2025 Findings), genel ortalamada ve retrieval'da çok dilli modellerin (multilingual-e5-large, gte-multilingual-base) Türkçeye özel modellerden önde olduğunu gösteriyor. Ancak bu karşılaştırmada bge-m3 ve Qwen3-Embedding yok. Genel çok dilli MTEB'de (MMTEB) Qwen3-Embedding-0.6B, e5-large-instruct ve bge-m3'ün üstünde, Apache-2.0 lisanslı ve CPU'da da çalışabilecek boyutta. Başlangıç için önerim `intfloat/multilingual-e5-large` (ya da `-instruct`) veya `Qwen/Qwen3-Embedding-0.6B`. Hangisinin bu veride daha iyi olduğuna kendi küçük test setinizle (bkz. Bölüm 9) karar verin.

### Cited Findings
- TR-MTEB (Baysan & Güngör, EMNLP 2025 Findings): Altı görev türü (classification, clustering, pair classification, retrieval, bitext mining, STS), yerli ve çeviri toplam 26 veri seti. Yazarlar ayrıca 34,2 milyon zayıf denetimli Türkçe cümle çifti derleyip iki Türkçe embedding modeli eğitmiş. Kaynaklar HF'de `trmteb` organizasyonunda. — [ACL Anthology](https://preview.aclanthology.org/new-sigs/2025.findings-emnlp.471/); [HF trmteb](https://huggingface.co/trmteb)
- TR-MTEB Tablo 2'de (PDF'den çıkarıldı; PDF düzeninde sütunlar bir satır kaymış görünüyordu, makale metnindeki 59.84→63.42 ifadesiyle eşleştirerek düzelttim) Mean(Task) / Retrieval skorları: multilingual-e5-large 66.82 / 60.62; text-embedding-3-small (OpenAI) 66.61 / **64.99** (en yüksek retrieval); multilingual-e5-large-instruct 65.92 / 57.21; gte-multilingual-base 64.49 / 57.51; multilingual-e5-base 64.26 / 58.29; turkish-embedding-model-fine-tuned (yazarların modeli, 110M) 63.42 / 52.75; multilingual-e5-small 61.71 (Mean); LaBSE retrieval 46.47; bert-base-turkish-uncased retrieval 34.82. — [TR-MTEB PDF](https://aclanthology.org/2025.findings-emnlp.471.pdf)
- Makalenin kendi yorumu: En iyi çok dilli modeller (e5-large, gte) genel performansta hâlâ önde. 110M parametreli Türkçe model farkı daraltıyor ama bitext mining'de (Türkçe-İngilizce hizalama) çok geride: 37.7 ve 86.88, buna karşılık e5-large 99.43 ve LaBSE 99.53. Sebep, modellerin tek dilli eğitilmiş olması. — [TR-MTEB PDF](https://aclanthology.org/2025.findings-emnlp.471.pdf)
- TR-MTEB'deki model boyutları: multilingual-e5-large ve e5-large-instruct 560M parametre, 1024 boyut; gte-multilingual-base 305M; multilingual-e5-base 278M, 768 boyut; multilingual-e5-small 118M, 384 boyut. — [TR-MTEB PDF, Ek tablo](https://aclanthology.org/2025.findings-emnlp.471.pdf)
- Ayrı bir benchmark olan TR-TEB (LREC 2026; Arslan ve ark.), 45 açık kaynak embedding modelini beş görev kategorisinde karşılaştırıyor (14 derlenmiş, 26 çeviri, 7 yeni Türkçe veri seti). Özet sayfasında model sıralaması yer almıyor. — [ACL Anthology 2026.lrec-1.862](https://aclanthology.org/2026.lrec-1.862/)
- Qwen3-Embedding serisi: 0.6B (1024 boyut), 4B (2560), 8B (4096). Hepsinde 32K bağlam, MRL (32–1024 arası özel boyut), instruction-aware kullanım (sorguya tek cümlelik görev talimatı eklemek sonucu %1–5 iyileştiriyor), 100+ dil ve Apache-2.0 lisans. MTEB Multilingual mean(task): 0.6B 64.33, 4B 69.45, 8B 70.58. Aynı tabloda multilingual-e5-large-instruct 63.22, bge-m3 59.56. Gereken sürümler: transformers ≥4.51.0, sentence-transformers ≥2.7.0. — [HF Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
- TurkEmbed makalesinde Qwen3-Embedding-8B, Türkçe STS'de en yüksek Pearson/Spearman değerlerini almış (0.701 / 0.721). Bu bir benzerlik (STS) görevi, retrieval değil. — [arXiv 2511.08376](https://arxiv.org/pdf/2511.08376) (arama özetinden, tam metin okunmadı)
- Mecellem (Türk hukuk alanı, arXiv 2601.16018): Embedding değerlendirmesinde embeddinggemma-300m, newmindai bge-m3-stsb ve BAAI/bge-m3 öne çıkıyor. BAAI/bge-m3'ün skoru Legal'de 51.16, MTEB tarzı Türkçe değerlendirmede 62.87. — [arXiv 2601.16018](https://arxiv.org/pdf/2601.16018) (arama özetinden)
- TurkEmbed4Retrieval: MS-MARCO-TR ile retrieval'a ince ayar yapılmış Türkçe model. SciFact-TR'de Turkish-ColBERT'e göre %19–26 kazanç bildiriyor. — [arXiv 2511.07595](https://arxiv.org/html/2511.07595v1)
- Topluluk ince ayarı `nezahatkorkmaz/turkce-embedding-bge-m3`: Türkçe STS'de Pearson 0.8535'ten 0.9096'ya çıkmış. — [HF model kartı](https://huggingface.co/nezahatkorkmaz/turkce-embedding-bge-m3)
- newmindai `Mursit-Large-TR-Retrieval` adlı bir Türkçe retrieval modeli var. Model kartı 17 görevli bir "MTEB-Turkish" kullanıyor; bu, TR-MTEB'in 26 veri setli paketiyle aynı şey değil. — [HF Mursit](https://huggingface.co/newmindai/Mursit-Large-TR-Retrieval)
- bge-m3: 568M parametre, 8192 token bağlam; dense, sparse (lexical) ve multi-vector (ColBERT) çıktılarını tek modelde veriyor, MIT lisanslı. [DOĞRULANMADI; eğitim bilgisi, bu oturumda model kartı açılmadı]
- jina-embeddings-v3 (570M) CC BY-NC 4.0 lisanslı, yani ticari kullanım kısıtlı. [DOĞRULANMADI]

### Inferences
- **Önerilen varsayılan:** `intfloat/multilingual-e5-large` veya `Qwen/Qwen3-Embedding-0.6B`. İkisi de ~0.6B parametre ve fp32'de yaklaşık 2,2–2,4 GB. Birkaç bin sözlük maddesini CPU'da bir kerelik indekslemek dakikalar ile onlarca dakika sürer; NVIDIA GPU varsa saniyeler-dakikalar. Rüya veri seti küçük olduğu için boyut sorun olmaz.
- **Diller arası arama (Türkçe sorgu → İngilizce Miller / Arapça Nablusi):** Tek dilli Türkçe modellerin bitext skoru düşük olduğundan, kaynaklar karışık dilliyse çok dilli bir model şart. Daha sağlam bir yol daha var: Her maddeye indeksleme sırasında Türkçe bir "kanonik sembol" etiketi ve (opsiyonel) Türkçe çeviri/özet eklemek. Böylece retrieval büyük ölçüde sembol ID'si üzerinden yapılır, embedding'e daha az yük biner (bkz. Bölüm 5).
- e5 ailesi `query: ` / `passage: ` öneklerini ister, Qwen3-Embedding ise sorgu tarafında talimat ister. Yeni başlayanların en sık yaptığı hata bu önekleri unutmak.
- Lisans açısından e5 (MIT), Qwen3-Embedding (Apache-2.0), bge-m3 ve gte-multilingual kişisel/ticari kullanımda rahat. jina-v3'ün NC lisansı ileride ticarileşme düşünülüyorsa dikkat gerektirir.

### Gaps
- bge-m3, Qwen3-Embedding ve embeddinggemma'yı aynı Türkçe retrieval benchmark'ında yan yana gösteren bir tablo bulamadım (TR-MTEB bunları içermiyor; TR-TEB'in sıralama tablosunu okuyamadım).
- MTEB leaderboard'un canlı "Turkish" filtresi bu oturumda açılmadı.
- Rüya sözlüğü gibi kısa madde + uzun anlatı sorgusu senaryosunda bu modellerin göreli başarısı hakkında yayımlanmış veri yok; kendi test setinizle ölçülmeli.

## 2. Reranker'lar

### Takeaway
Çok dilli bir cross-encoder reranker, Türkçe sorgu ile Arapça/İngilizce madde eşleşmesini belirgin biçimde iyileştirebilir. Başlangıç için `BAAI/bge-reranker-v2-m3` (0.6B, Apache-2.0) en basit seçenek. Alternatif olarak Qwen3-Reranker (0.6B/4B/8B) var. MVP'de reranker şart değil; 2. fazda eklenmeli.

### Cited Findings
- bge-reranker-v2-m3: 0.6B parametre, bge-m3 tabanlı, Apache-2.0, "güçlü çok dilli yetenek, hafif, hızlı" olarak tanımlanıyor. Kullanımı `FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True).compute_score([q, p], normalize=True)` ya da `sentence_transformers.CrossEncoder(...).predict([(q,p),...])` şeklinde. Model kartındaki karşılaştırmalar yalnızca grafik olarak verilmiş. — [HF bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
- Qwen3-Reranker-0.6B / 4B / 8B: 32K bağlam, instruction-aware, embedding üretmiyor (yalnızca skor). — [HF Qwen3-Embedding-0.6B kartı, ilgili modeller](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
- jina-reranker-v2-base-multilingual ve jina-reranker-m0 çok dilli seçenekler, fakat jina modellerinin çoğu CC BY-NC lisanslı. [DOĞRULANMADI]

### Inferences
- Önerilen akış: Her sembol için vektör/hibrit aramadan top-20 aday al, reranker ile top-5'e indir. Kaynak çeşitliliğini korumak için her kaynaktan en fazla N madde gelsin ("per-source top-k", bkz. Bölüm 5).
- CPU'da 20 çift × 0.6B cross-encoder birkaç saniye sürer; kabul edilebilir.

### Gaps
- Türkçe-Arapça veya Türkçe-Osmanlıca transkripsiyon çiftlerinde reranker başarısına dair ölçüm bulamadım.

## 3. Yeni başlayan için vektör veritabanı

### Takeaway
Bu ölçekte (en fazla on binlerce madde) her seçenek yeterli. Windows'ta sunucu kurmadan, pip ile çalışan ve metadata filtresi kolay olan **Chroma (PersistentClient)** en düşük sürtünmeli başlangıç. Hibrit arama (BM25+vektör) yerel olarak gerektiğinde ya BM25'i ayrı bir Python kütüphanesiyle yapıp sonuçları RRF ile birleştirin, ya da Qdrant'a (Docker veya yerel mod) veya LanceDB'ye geçin.

### Cited Findings
- Chroma: `where` ile metadata filtresi (`$eq` örtük; `$in`, `$nin`, `$and`, `$or`, `$gte/$lte`; dizi metadata için `$contains`). `where_document={"$contains": ...}` ile tam metin filtresi var ve metadata filtresiyle aynı sorguda birleştirilebiliyor. — [Chroma docs: metadata filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering)
- Chroma ve LanceDB Apache 2.0 lisanslı. Chroma "embedded-first" (uygulama içine gömülü) bir mimariye sahip ve tek düğümün ötesine ölçeklenmiyor; bu yorum rakip firma Zilliz'den. — [Zilliz: Chroma vs LanceDB](https://zilliz.com/comparison/chroma-vs-lancedb)
- Qdrant: payload (metadata) filtresi `Filter/FieldCondition/MatchValue` ile yapılıyor, hızlı filtre için payload index öneriliyor. Dokümantasyonda Hybrid Queries, BM25 ve FastEmbed (SPLADE, miniCOIL) sayfaları var. "Qdrant Edge" ile Python içinde sunucusuz gömülü çalışma mümkün. Windows'ta Docker kullanırken klasör yerine adlandırılmış Docker volume gerekebiliyor. — [Qdrant quickstart](https://qdrant.tech/documentation/quickstart/)
- qdrant-client'ta `QdrantClient(path="./qdrant_db")` veya `":memory:"` ile sunucusuz "local mode" var; prototip içindir. [DOĞRULANMADI: quickstart sayfasında geçmiyor, eğitim bilgisi]
- FAISS yalnızca bir vektör indeksi kütüphanesi: metadata ve kalıcılığı kendiniz yönetirsiniz. pgvector için PostgreSQL kurulumu gerekir; Windows'ta yeni başlayan için ek yük. [DOĞRULANMADI; genel bilgi]

### Inferences
- Metadata şeması önerisi (her chunk = bir sözlük maddesi): `{symbol_id, symbol_surface, source_id, source_title, author, tradition (islami/osmanli/antik_yunan/bati_modern), orig_lang (tr/ar/ota/en), page, url, edition, ocr_confidence}`. Böylece `where={"tradition": {"$in": [...]}}` ve `where={"symbol_id": "yilan"}` ile filtreleme mümkün olur.
- Sembol eşleşmesi kesinse (sembol indeksinden ID bulunduysa), vektör aramaya hiç gerek kalmadan `collection.get(where={"symbol_id": "yilan"})` ile tüm kaynaklardaki maddeler doğrudan çekilebilir. Bu, Bölüm 4–5'teki "önce sözlük, sonra vektör" yaklaşımının çekirdeği.
- Öğrenme amacıyla, Chroma yerine 50 satırlık bir "numpy + JSON" vektör deposu yazmak da makul. Bu ölçekte brute-force cosine yeterince hızlı.

### Gaps
- Chroma'nın yerel (açık kaynak) sürümünde yerleşik BM25/sparse hibrit arama olup olmadığını bu oturumda doğrulayamadım. Chroma Cloud'da sparse/hibrit özellikleri bulunduğu biliniyor [DOĞRULANMADI].
- Güncel sürüm numaraları (chromadb, qdrant-client, lancedb) bu oturumda teyit edilmedi.

## 4. Hibrit arama ve Türkçe morfoloji (BM25 + vektör, lemmatization)

### Takeaway
Türkçenin eklemeli yapısı ("yılanlar", "yılanı", "yılandan", "yılanın") ham BM25'te eşleşmeyi bozar. Çözüm: Hem indekslenen sembol başlıklarında hem sorguda kök/lemma normalizasyonu yapmak. Python'da kurulumu en kolay araç **zeyrek** (Zemberek'in kısmi Python portu, MIT, pip ile kuruluyor, alfa aşamasında). Daha basit bir yedek olarak "en uzun önek eşleşmesi" ve elle yazılmış bir varyant listesi de iş görür.

### Cited Findings
- zeyrek: Türkçe için Python morfolojik çözümleyici ve lemmatizer; Zemberek'in kısmi portu, MIT lisanslı, `pip install zeyrek`. Kararlı sürüm 0.1.3 (2022-12-29), ön sürüm 0.1.4a0 (2024-07-14). API: `MorphAnalyzer().analyze(word)` ve `.lemmatize(word)` → örn. `('benim', ['ben'])`. Paket kendini "alfa" olarak tanımlıyor; API değişebilir. — [PyPI zeyrek](https://pypi.org/project/zeyrek); [zeyrek docs](https://zeyrek.readthedocs.io/); [libraries.io](https://libraries.io/pypi/zeyrek)
- Zemberek-NLP'nin asıl hâli Java'da; Python'dan JPype veya gRPC ile çağrılabilir, bu yüzden Windows'ta JDK gerekir. Stanza'nın Türkçe (IMST/BOUN treebank) lemmatizer'ı ve spaCy için topluluk Türkçe modelleri (örn. `tr_core_news_*`, Turkish NLP Suite) de alternatif. [DOĞRULANMADI; bu oturumda kaynak açılmadı]
- bge-m3'ün tek modelden "sparse/lexical" ağırlık çıkarabilmesi, ayrı bir BM25 indeksi kurmadan hibrit arama imkânı verir. [DOĞRULANMADI; Bölüm 1 notuna bakın]

### Inferences
- **Sorgu tarafı:** Rüya anlatısı LLM'den geçiyor (Bölüm 5). LLM'den sembolleri zaten **yalın hâlde** ("yılan", "deniz") ve küçük harfle döndürmesini istemek, lemmatizer ihtiyacını büyük ölçüde ortadan kaldırır. zeyrek'i ikinci kontrol olarak kullanın.
- **İndeks tarafı:** Sözlük madde başlıkları zaten çoğunlukla yalın hâlde. Lemmatize edilmesi gereken asıl şey madde **gövdesi** (BM25 için). İki alan tutun: `text_raw` (gösterim ve LLM için) ve `text_lemmas` (BM25 için).
- **Türkçe küçük harf tuzağı:** Python'da `"I".lower()` → "i" olur (Türkçede "ı" olmalı), `"İ".lower()` ise "i̇" (birleşik nokta) üretir. Önce `str.replace("I","ı").replace("İ","i")` ile özel normalize yapılmalı. Osmanlıca transkripsiyonlardaki şapka ve diakritikler (â, î, û, ḥ, ʿ) için ayrıca "katlanmış" (ASCII-fold) bir alan tutmak, aramayı daha toleranslı yapar.
- BM25 için `rank_bm25` veya `bm25s` kütüphanesi kullanılıp sonuçları vektör sonuçlarıyla **Reciprocal Rank Fusion (RRF)** ile birleştirmek, yeni başlayan için anlaşılır ve öğretici bir hibrit yaklaşım [kütüphane adları DOĞRULANMADI].
- Sembolleri lemmatize etmek: **Evet**, ama kanonik sembol indeksiyle birlikte (yılan ← yılanlar, yılanı, ejderha? ...). Eş anlamlılar ("deniz/derya/bahr", "yılan/hayye/serpent") morfolojiyle çözülmez; elle veya LLM yardımıyla kurulmuş bir eş anlamlı tablosu gerekir.

### Gaps
- zeyrek'in Osmanlıca transkripsiyon metinlerindeki (eski imla, Arapça-Farsça kelimeler) başarısına dair veri bulamadım; büyük olasılıkla düşük.
- Stanza ve spaCy Türkçe modellerinin 2026 sürümleri ve Windows kurulum durumu doğrulanmadı.

## 5. Sembol çıkarımı, normalize sembol indeksi, chunking ve kaynak ayrıştırma

### Takeaway
En sağlam ve öğretici tasarım iki katmanlı: (a) LLM ile yapılandırılmış (JSON) sembol çıkarımı, (b) bu sembollerin kaynaklardan otomatik + elle türetilmiş **kanonik sembol indeksine** eşlenmesi; eşlenemeyenler için vektör arama yedeği. Sözlük tipi kaynaklarda **her madde = bir chunk** olmalı ve zengin metadata taşımalı. Claude kullanılıyorsa her madde bir `search_result` bloğu olarak verilebilir (bkz. Bölüm 6).

### Cited Findings
- Claude API'nin yapılandırılmış çıktı özelliği (`output_config.format`, JSON schema) çıkarım adımında kullanılabilir. Ancak citations ile **aynı istekte** kullanılamaz (Bölüm 6). — [Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Claude citations'ta "custom content" dokümanları ek chunking yapmaz; verdiğiniz blokları olduğu gibi kullanır ve atıfı blok indeksiyle döndürür. "Her RAG chunk'ını ayrı plain-text dokümana koyarsanız Claude cümle düzeyinde alıntılayabilir" deniyor. Taranmış (metin katmanı olmayan) PDF'ler alıntılanamıyor. — [Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)

### Inferences
- **Sembol çıkarım şeması (öneri):**
  `{"semboller":[{"yalin":"yılan","metindeki_ifade":"bir yılan gördüm","baglam":"denizden çıkan siyah yılan","nitelikler":["siyah","büyük"],"eylem":"görmek","duygu":"korku"}], "genel_duygu":"..."}`
  Nitelikler önemli, çünkü klasik tabirnameler sıklıkla "beyaz yılan", "yılan sokması" gibi alt maddeler içerir.
- **Kanonik sembol indeksi (symbols.json / SQLite):** `symbol_id` → `{tr_canonical, tr_variants[], ar[], ota[], en[], related[]}`. Kurulum: (1) Her kaynağın madde başlıklarını ayrıştır. (2) Başlıkları zeyrek ile lemmatize edip `symbol_id` öner. (3) Diller arası eşlemeyi LLM'e toplu yaptır ("Arapça 'الحية' → yılan") ve **elle gözden geçir**. (4) Belirsizleri `review_needed` olarak işaretle.
- **Eşleme sırası:** (1) Tam/lemma eşleşmesi → `symbol_id`. (2) Eş anlamlı tablosu. (3) Yalnızca sembol adını gömüp sembol başlıkları koleksiyonunda vektör araması (anlatının tamamını değil). Eşik altında kalıyorsa "bu sembol kaynaklarda bulunamadı" denir ve uydurulmaz.
- **Neden hem LLM hem sözlük:** Yalnız sözlük eşleşmesi ("deniz" kelimesi geçiyor mu) bağlamı kaçırır, olumsuzlamaları ("yılan görmedim") yakalayamaz ve çok kelimeli sembolleri ("ölmüş babamı gördüm") kaçırır. Yalnız LLM ise kaynakta olmayan sembol adları üretebilir. İkisini birleştirmek bu zayıflıkları dengeler.
- **Chunk = madde:** Metin `"[Nablusi – Yılan] Rüyada yılan görmek düşmana işarettir..."` biçiminde, başlık önekli tutulmalı. Çok uzun maddeler (>~800 token) alt başlıklara (beyaz yılan, yılan sokması...) bölünmeli ve hepsi aynı `symbol_id`'yi, farklı `sub_symbol` değerlerini taşımalı.
- **Ayrıştırma (parsing):** Sözlükler genelde düzenli kalıplar içerir. Madde başlığını kalın, büyük harf ya da `^[A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s*[:–-]` gibi bir regex ile yakalamak ilk geçiş için yeterli. Düzensiz kaynaklarda LLM'e "bu sayfayı {başlık, metin} listesine çevir" demek ve sonuçta orijinal metnin **birebir korunduğunu** kontrol etmek gerekir (çıktı metni orijinal sayfada substring olarak bulunmalı).
- **OCR gürültüsü:** `ocr_confidence` alanı tutun. Tire ile bölünmüş satırları birleştirin, sayfa başlık/numaralarını silin. Osmanlıca transkripsiyonlarda diakritiği hem koruyan hem katlayan iki alan tutun. OCR'si kötü maddeleri LLM'e "temizle" dedirtmek uydurma riski taşır; temizlenmiş sürümü ayrı alanda tutun ve atıfı orijinale yapın.
- **Retrieval stratejisi:** Her sembol için **kaynak başına** top-k (örn. her kaynaktan en fazla 2 madde). Böylece tek bir büyük sözlük (örn. Miller) sonuçları domine etmez ve "kaynaklar arası karşılaştırma" mümkün olur.

### Gaps
- Rüya tabiri sözlükleri için hazır bir parser veya açık, yapılandırılmış veri seti bulmadım (bu not kapsamında aranmadı; kaynak verileri başka araştırmacının konusu olabilir).

## 6. Üretim (generation): grounded çok kaynaklı sentez, atıflar, çelişkiler; LLM seçenekleri ve maliyet

### Takeaway
Claude API'de **`search_result` içerik blokları + `citations: {enabled: true}`** RAG için yerel (native) atıf sağlıyor ve beta başlığı gerektirmiyor. Atıflar kaynak/başlık/alıntı metnini otomatik döndürüyor ve alıntılanan metin çıktı tokenı sayılmıyor. **Kısıt:** Citations ile structured outputs (JSON schema) aynı istekte kullanılamıyor (400 hatası). Güncel fiyatlarla tek bir yorum isteği, sorgu başına Haiku 5.5'te ~0,2 sent, Sonnet 5.5'te ~3–4 sent, Opus 5.5'te ~7 sent mertebesinde. Yerel seçenekte Ollama ile Gemma 4 (12b/26b) veya güncel Qwen modelleri kullanılabilir, ancak Türkçe kalitesi ve atıf disiplini Claude'dan zayıf olacaktır [çıkarım].

### Cited Findings — Claude API
- `search_result` bloğu şeması: `{"type":"search_result","source":<URL/ID, zorunlu>,"title":<zorunlu>,"content":[{"type":"text","text":...}],"citations":{"enabled":true}}`. Citations varsayılan olarak kapalı ve bir istekteki tüm search_result'lar aynı ayarı kullanmalı. Bloklar ya doğrudan kullanıcı mesajında ya da bir tool_result içinde verilebiliyor. Haiku 3 dışındaki tüm aktif modeller destekliyor, **beta başlığı gerekmiyor**. — [Claude docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)
- Yanıttaki atıf alanları: `type: "search_result_location"`, `source`, `title`, `cited_text`, `search_result_index`, `start_block_index`, `end_block_index`. Claude bütün blokları alıntılar, alt-string düzeyinde değil. Daha ince atıf için içeriği daha küçük text bloklarına bölmek gerekiyor. — [Claude docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)
- `cited_text` çıktı tokenı sayılmıyor, sonraki turlarda geri gönderildiğinde girdi tokenı da sayılmıyor. Citations etkinleştirilince girdi tokenı biraz artıyor. Atıfların "verilen dokümanlara geçerli işaretçiler içermesi garanti". Prompt caching ve batch ile birlikte çalışıyor. — [Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- **"Citations and structured outputs are incompatible"**: `document` veya `search_result` bloklarında citations açıkken `output_config.format` (ya da eski `output_format`) verilirse API 400 döndürüyor. — [Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Fiyatlar (USD / milyon token, girdi / çıktı / cache hit): **Claude Opus 5.5** 4 / 20 / 0,20; **Claude Sonnet 5.5** 2 / 10 / 0,10; **Claude Haiku 5.5** 0,10 / 0,50 / 0,01 (100K tokena kadar prompt; 100K üstü 0,50 / 2,50). Batch API iki yönde de %50 indirimli. Claude 4.7 ve sonrası modeller, aynı metin için ~%30 daha fazla token üreten yeni bir tokenizer kullanıyor. Haiku 5.5 hariç 4.6+ modellerde 1M bağlam standart fiyatla sunuluyor. — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Dokümantasyon örneklerinde model ID'si `claude-opus-5-5`. — [Claude docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)

### Cited Findings — Yerel LLM (Ollama)
- Ollama `gemma4` etiketleri: e2b (4,6–7,5 GB), e4b (6,6–9,5 GB), 12b (7,7–8,0 GB, 256K bağlam), 26b (16–19 GB), 31b (19–20 GB). Metin+görüntü girişi var. Çok dilli MMMLU'da 31B %88,4, E2B %67,4. Sayfa lisans ve dil sayısı vermiyor. — [ollama.com/library/gemma4](https://ollama.com/library/gemma4)
- Ollama kütüphanesinde 2026'da Qwen 3.5 (0.8b–122b) ve daha yeni Qwen 3.6/3.8 27b etiketlerinin bulunduğu bildiriliyor. Kaynaklar sürüm ayrıntılarında çelişiyor, bu yüzden ollama.com/library'den teyit edilmeli. — [morphllm (Ağustos 2026)](https://www.morphllm.com/best-ollama-models); [computingforgeeks](https://computingforgeeks.com/ollama-models-cheat-sheet/) (ikincil kaynaklar)
- Türkçe LLM benchmark'ları: Cetvel (arXiv 2508.16431; ilk 10'u Llama ve Qwen2.5 domine ediyor, en iyi Llama-3.3-70B-Instruct), TurkishMMLU (EMNLP 2024 Findings), TR-MMLU (arXiv 2501.00593) ve TurkBench HF leaderboard (Qwen3-235B ve `ykt-arge/gemma-3-12b-Turkish-V1` gibi Türkçe ince ayarlı modeller listede). Qwen3 ile Gemma 3/4'ü Türkçede Ollama üzerinden doğrudan karşılaştıran bir kaynak bulamadım. — [Cetvel](https://arxiv.org/pdf/2508.16431); [TurkishMMLU](https://preview.aclanthology.org/new-sigs/2024.findings-emnlp.413/); [TR-MMLU](https://arxiv.org/html/2501.00593v2); [TurkBench](https://turkbench-turkbench.hf.space)

### Inferences
- **Maliyet tahmini (kendi hesabım, varsayımlara dayalı):** 6 sembol × ~5 madde × ~200 token ≈ 6K token bağlam, üstüne ~1,5K token sistem promptu ve rüya metni ≈ **~8–10K girdi**, ~1,5K çıktı (Türkçe ve yeni tokenizer nedeniyle tahmin yukarı yönlü belirsiz).
  - Sonnet 5.5: 10K × $2/M + 1,5K × $10/M ≈ **$0,035/sorgu**
  - Haiku 5.5: 10K × $0,10/M + 1,5K × $0,50/M ≈ **$0,002/sorgu**
  - Opus 5.5: 10K × $4/M + 1,5K × $20/M ≈ **$0,07/sorgu**
  - Sembol çıkarım adımı (Haiku, ~1K girdi / 300 çıktı) ihmal edilebilir (<$0,001). Sabit sistem promptu prompt caching ile ucuzlatılabilir.
- **Önerilen iki-çağrı tasarımı (citations/JSON kısıtı yüzünden):**
  1. *Çağrı A (çıkarım, Haiku 5.5, structured outputs):* rüya → JSON sembol listesi.
  2. *Çağrı B (sentez, Sonnet 5.5, citations açık, JSON yok):* Her madde bir `search_result` bloğu olur (`source` = `kaynak_id#sayfa`, `title` = `"Nablusi – Yılan"`). Çıktı, sabit Markdown başlıklarıyla istenir ("## Yılan → ### Kaynakların söyledikleri / ### Uzlaşılan noktalar / ### Ayrışan noktalar / ### Kaynaklarda bulunmayanlar"). Atıflar API'den yapılandırılmış olarak geldiği için UI'da dipnot gibi gösterilebilir.
  3. Yapılandırılmış veri gerekiyorsa üçüncü ucuz bir çağrıyla Markdown'dan JSON'a dönüştürme yapılabilir, ya da yerel LLM yolunda olduğu gibi `[S3]` ID'li JSON şeması kullanılabilir.
- **Uydurmayı önleyen prompt kuralları:** (1) "YALNIZCA verilen kaynak maddelerindeki yorumları kullan; kendi bilgini ekleme." (2) "Bir sembol için madde yoksa 'Kaynaklarda bu sembole dair yorum bulunamadı' yaz." (3) "Her yorum cümlesi bir kaynağa dayanmalı." (4) "Kaynaklar çelişiyorsa uzlaştırmaya çalışma; 'X şöyle derken Y şöyle der' diye yan yana koy." (5) "Kaynağın geleneğini (İslami, Osmanlı, antik Yunan, modern Batı) belirt." (6) "Orijinal Arapça/İngilizce ifadeyi çevirirken çeviri olduğunu belirt." Sentez sonrası kod tarafında bir kontrol: Her sembol bölümünde en az bir atıf yoksa uyarı ver.
- **Yerel LLM yolu:** Citations API yok. Her maddeye `[S1]..[Sn]` ID verin, LLM'den JSON (`{"sembol":..., "yorumlar":[{"kaynak_id":"S3","ozet":...}], "uzlasma":..., "celiski":...}`) isteyin (Ollama `format` parametresiyle JSON schema verilebilir [DOĞRULANMADI]) ve kodda (a) var olmayan kaynak ID'lerini, (b) özet ile kaynak metin arasındaki benzerliği kontrol edin.
- **Donanım (kaba, Q4 quantization):** 8 GB VRAM → gemma4:e4b/12b sınırda; 12–16 GB VRAM → 12b rahat; 24 GB → 26b–31b. Yalnız CPU'da 12b yavaş olur (saniyede birkaç token) [çıkarım; ollama sayfasındaki disk boyutlarından yaklaşık].
- Ollama dışında Windows'ta LM Studio da GUI ile aynı GGUF modellerini çalıştırır ve OpenAI uyumlu bir sunucu sağlar [DOĞRULANMADI].
- Trendyol LLM ve ytu-ce-cosmos Türkçe Llama gibi Türkçe ince ayarlı modeller var. Ancak 2026 sürümlerinin güncel genel modelleri (Gemma 4, Qwen 3.x) geçip geçmediğini doğrulayamadım.

### Gaps
- Gemma 4 / Qwen 3.5+ için Türkçe benchmark sonuçları ve Ollama Qwen sayfası bu oturumda birincil kaynaktan doğrulanmadı.
- Claude Haiku 5.5'in Türkçe sentez kalitesinin Sonnet 5.5'e göre yeterli olup olmadığına dair veri yok; A/B test edilmeli.

## 7. Framework seçimi (düz Python vs LlamaIndex vs LangChain vs Haystack)

### Takeaway
Temelleri öğrenmek isteyen bir yeni başlayan için **düz Python + birkaç küçük kütüphane** (sentence-transformers, chromadb, anthropic/ollama, zeyrek) öneriliyor. Pipeline zaten deterministik ve az adımlı (çıkar → eşle → getir → sentezle). Framework soyutlamaları burada öğrenmeyi gizler ve Claude'un `search_result`/citations gibi yerel özelliklerini sarmalayıcılar arkasında zorlaştırabilir.

### Cited Findings
- Claude'un search_result citations özelliği standart Messages API'nin parçası; doğrudan `anthropic` Python SDK ile kullanılıyor ve ek framework gerektirmiyor. — [Claude docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)

### Inferences
- LlamaIndex, sonraki aşamada "veri yükleyici + node/metadata + retriever" kalıplarını öğrenmek için iyi bir referans. LangChain ekosistemi geniş fakat sık API değişikliği yeni başlayanı yorabilir. Haystack daha "pipeline" odaklı ve üretim tarzında. Bu iddialar genel topluluk algısına dayanıyor ve bu oturumda birincil kaynakla doğrulanmadı.
- Önerilen proje yapısı: `ingest/parse_<kaynak>.py` → `data/entries.jsonl` → `build_symbol_index.py` → `index.py` (Chroma) → `pipeline.py` (`extract_symbols`, `map_symbols`, `retrieve`, `synthesize`) → `app.py` (UI) → `eval/`.

### Gaps
- LlamaIndex, LangChain ve Haystack'in Ekim 2026 sürüm numaraları ve Claude citations desteği doğrulanmadı.

## 8. Değerlendirme (gold set, metrikler, araçlar)

### Takeaway
30–50 rüyadan oluşan elle hazırlanmış küçük bir gold set (rüya → beklenen semboller → beklenen madde ID'leri) ve basit Python metrikleri (sembol precision/recall, retrieval recall@k, atıf geçerliliği) ilk aşamada Ragas/DeepEval'den daha öğretici ve güvenilir. Faithfulness için LLM-as-judge sonradan eklenebilir.

### Cited Findings
- Claude citations, atıfların verilen dokümanlara geçerli işaretçi olmasını garanti ediyor. Bu yüzden "var olmayan kaynağa atıf" hatası API düzeyinde ortadan kalkıyor; geriye "atıfsız cümle" ve "atıfın içeriği desteklememesi" riskleri kalıyor. — [Claude docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)

### Inferences
- **Gold set formatı (JSONL):** `{"id":"r01","ruya":"...","beklenen_semboller":["deniz","yılan"],"beklenen_maddeler":{"yilan":["nablusi_312","ibnsirin_88","miller_yilan"]},"olmamasi_gereken":["..."]}`
- **Metrikler:** (1) Sembol çıkarımı: precision/recall/F1 (lemma düzeyinde). (2) Sembol→ID eşleme doğruluğu. (3) Retrieval: sembol başına recall@5 ve MRR. (4) Sentez: atıf kapsamı (atıflı cümle oranı), "kaynakta olmayan yorum" oranı (LLM-judge veya elle), çelişki yakalama (gold'da işaretli çelişkilerin çıktıda belirtilmesi). (5) Negatif test: kaynaklarda olmayan bir sembol ("uzay gemisi") sorulduğunda sistemin "bulunamadı" demesi.
- Ragas (faithfulness, context precision/recall) ve DeepEval (pytest tarzı) Türkçe metinlerde de LLM-judge kullanır. Judge modelin Türkçe yeterliliği sonucu etkiler. Bu araçlara 3. fazda geçilmesi öneriliyor. Ragas/DeepEval'in güncel sürümleri ve Claude desteği bu oturumda doğrulanmadı.

### Gaps
- Türkçe RAG faithfulness ölçümü için doğrulanmış bir judge kurulumu veya Türkçe RAG değerlendirme makalesi bu oturumda incelenmedi.

## 9. Basit arayüz seçenekleri ve aşamalı yol haritası

### Takeaway
Arayüz için **Streamlit** (en az kod; metin alanı, butonlar, genişletilebilir kaynak kartları) veya **Gradio** (hızlı demo, HF Spaces paylaşımı) önerilir. Chainlit sohbet arayüzü için uygundur, ancak bu tek atımlık "rüya → rapor" akışı için gereksiz. Yol haritası: Önce tek kaynak + sözlük eşleme + Claude citations ile çalışan uçtan uca bir MVP; sonra kaynak ekleme, hibrit arama, reranker ve değerlendirme.

### Cited Findings
- Claude atıfları `search_result_location` nesneleri olarak (`source`, `title`, `cited_text`) yapılandırılmış biçimde döndüğü için UI'da dipnot veya kart olarak doğrudan render edilebilir. — [Claude docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)

### Inferences
- **Faz 0 (1–2 hafta) – Veri:** 2 kaynak (örn. bir Türkçe Nablusi/İbn Sirin çevirisi + Miller İngilizce) → `entries.jsonl` (madde başına bir kayıt, metadata ile). Elle 50 kanonik sembol.
- **Faz 1 – MVP:** (1) Claude Haiku 5.5 + structured outputs ile sembol çıkarımı. (2) Sözlük/lemma eşlemesi (zeyrek). (3) `symbol_id` ile doğrudan madde çekme (vektör DB'siz bile olur). (4) Claude Sonnet 5.5 + `search_result` citations ile sentez. (5) Streamlit arayüzü. (6) 20 rüyalık gold set ve sembol recall ölçümü.
- **Faz 2 – Retrieval:** Chroma + multilingual-e5-large veya Qwen3-Embedding-0.6B. Eşlenemeyen semboller için vektör yedeği, kaynak başına top-k, bge-reranker-v2-m3. Arapça ve Osmanlıca kaynaklar eklenir, diller arası eşanlamlı tablosu kurulur.
- **Faz 3 – Kalite:** BM25 (lemma alanı) + vektör RRF hibriti, OCR temizliği, Ragas/DeepEval veya LLM-judge ile faithfulness, çelişki tespit kalitesi, prompt caching ile maliyet optimizasyonu.
- **Faz 4 – Opsiyonel:** Ollama ile yerel mod (gemma4:12b vb.) ve aynı gold set üzerinden Claude ile A/B karşılaştırması. Embedding modellerinin kendi gold set üzerinde karşılaştırılması (e5 vs Qwen3 vs bge-m3 vs Türkçe modeller).
- **Ürün/etik notu:** Rüya tabirinin bilimsel dayanağı olmadığı ve klasik kaynakların tarihsel/kültürel metinler olduğu UI'da açıkça belirtilmeli. Sağlık, ölüm ve korku temalı rüyalarda kesin yargı içeren dil yumuşatılmalı (bu bir öneri; kaynaklı değil).

### Gaps
- Streamlit, Gradio ve Chainlit'in Ekim 2026 sürümleri ve Windows'a özgü sorunları bu oturumda doğrulanmadı.
