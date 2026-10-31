# İlerleme Özeti: Ne yaptık, nasıl yaptık, sırada ne var?

> Tarih: 31 Ekim 2026 · Takvimde: Hafta 1'in sonu (deneme haftası)
> Bu belge projeye bir süre ara verip döndüğünde "neredeydik?" sorusunu cevaplamak için yazıldı. Ayrıntılar her bölümde bağlantısı verilen belgelerde.

---

## 1. Proje bir paragrafta

Sen bir rüya anlatıyorsun. Sistem rüyadaki sembolleri buluyor (ör. "siyah, büyük yılan"). Her sembolü bir sembol kimliğine eşliyor (`yilan`). Sonra Nablusi, İbn Sirin'e atfedilen *Muntahab*, Miller ve Freud'da o sembol için ne yazıldığını getiriyor. En son bunları **kaynak göstererek ve çelişkileri gizlemeden** Türkçe bir yorumda birleştiriyor.

Asıl amaç RAG'ı (getirmeyle güçlendirilmiş üretim) hazır bir framework kullanmadan, katman katman kendi elinle öğrenmek. Proje kişisel kalacak; internete açılmayacak. Bkz. [00-proje-vizyonu.md](00-proje-vizyonu.md).

Bir sorgunun izlediği yol dört adımdan oluşuyor ([03-mimari.md](03-mimari.md)):

```
Rüya metni
  → 1. Çıkarım   (Claude: rüyadaki semboller ve nitelikleri, JSON olarak)
  → 2. Eşleme    (sembol sözlüğü + zeyrek ile kök bulma; Aşama 2'de vektör yedeği)
  → 3. Getirme   (symbol_id ile her kaynaktan en fazla N madde)
  → 4. Sentez    (Claude: kaynak gösteren Türkçe yorum + uyarı metni)
```

---

## 2. Nasıl çalışıyoruz?

### Çalışma ortamı ([11](11-calisma-ortami-colab-drive.md))

| Ne | Nerede | Neden |
|---|---|---|
| Kod | Bilgisayarda (`C:\ruya-tabirnamesi`), GitHub'da özel repo | Kod VS Code'da yazılıyor, git ile izleniyor |
| Çalıştırma | Google Colab | GPU, bol disk; bilgisayara model ya da veri indirilmiyor |
| Veri | Google Drive (`MyDrive/ruya-tabirnamesi/`) | Lisans (NC/SA), boyut ve rüyaların gizliliği yüzünden veri git'e girmiyor |
| Gizli bilgiler | Yalnızca Colab Secrets | API anahtarı hiçbir dosyaya yazılmıyor |

Bilgisayarda yalnızca **verisiz testler** çalışıyor (`uv run pytest`). Gerçek veriyle çalışan her şey Colab'de oluyor.

### İş bölümü

- **Sen:** Kararları veriyorsun (bütçe, repo görünürlüğü, sembol listesini onaylama), Colab'de notebook'ları çalıştırıyorsun, deneylerde çeviri ve atama kalitesini elle puanlıyorsun.
- **Claude (ben):** Belgeleri yazıyorum, mimariyi kuruyorum, kod işini küçük görevlere bölüp plan yazıyorum, sonucu okuyup doğruluyorum, commit ediyorum. Push etmiyorum; push'u sen yapıyorsun.
- **Orkestra (EVREN agent'ları):** Kodu ve testleri yazıyor. Ben görevi tanımlıyorum ("şu dosyada şu işlev, şu davranış, şu kontrol komutu geçmeli"). Agent'lar (`kodcu`, `testci`, `hizli` …) dosyayı düzenliyor ve kontrol komutu geçene kadar deniyor. Sonra ben `git diff`'i okuyup bütün testleri çalıştırıyorum. Böylece Claude token'ı kod yazmaya değil, plan ve doğrulamaya harcanıyor.

### Kurallar ([CLAUDE.md](../CLAUDE.md), [12](12-kod-yapisi-ve-sozlesmeler.md))

- **Önce belge, sonra kod.** Şema ya da davranış değişikliği önce `docs/`'ta yazılıyor.
- **TDD.** Davranış değişikliğinde önce kırmızı test, sonra onu geçiren kod.
- **Katman kuralı.** Her modül yalnızca izin verilen modülleri içe aktarabiliyor. Ağır paketler (chromadb, torch, gradio, zeyrek) yalnızca işlev içinde yükleniyor. `tests/test_mimari.py` bunu otomatik denetliyor.
- **Model adları** yalnızca `src/ruya/config.py` içinde duruyor.
- **Atomik commit'ler.** Her commit tek bir mantıksal değişiklik; mesajlar Türkçe ve emir kipinde.
- **Commit öncesi** `uv run pytest` ve `uv run ruff check .` temiz olmalı.

---

## 3. Şimdiye kadar ne yaptık? (zaman sırasıyla)

### 21 Ekim · Araştırma ve planlama (22 commit)

- Kaynak araştırması yapıldı ([arastirma/rapor.md](arastirma/rapor.md)). Hangi tabirnamelerin yasal olarak kullanılabileceği belirlendi.
- Nablusi ve Miller'ın ham dosyaları bir kez **incelendi** (kod yazılmadan). Nablusi'de ~5.746 paragraf, ~2.400 başlıklı madde ve ~3.300 alt paragraf görüldü. Miller'da 2.256 madde başlığı tek bir regex'le yakalanabiliyor ([02, bölüm 2](02-veri-kaynaklari-ve-semasi.md)).
- 00–11 arası proje belgeleri yazıldı: vizyon, gereksinimler, veri, mimari, teknoloji seçimleri, klasik tabir yöntemi, değerlendirme, etik ve hukuk, 12 haftalık takvim, riskler, kurulum.
- Çalışma ortamı "her şey bilgisayarda" yerine **Colab + Drive** olarak değiştirildi; bütün belgeler buna göre güncellendi.

### 23 Ekim · Mimari iskelet (27 commit)

- Python paketi kuruldu: `pyproject.toml`, uv, ruff, pytest, nbstripout.
- `config.py`: Colab algılama, Drive yolları, model adları ve fiyatlar.
- `schemas.py`: bütün veri sözleşmeleri Pydantic ile tanımlandı (`Madde`, sembol kaydı, boru hattı ara sonuçları, test örneği).
- Bütün modüllerin **imzaları** yazıldı: hangi fonksiyon ne alır, ne döndürür, hangi hafta yazılacak. Gövdeler bilerek boş bırakıldı.
- `pipeline/run.py`: dört adımı bağımlılık enjeksiyonuyla birleştiren çatı.
- Mimari testleri, kontrat testleri, Colab kurulum betiği, ortam kontrol notebook'u, kaynak indirme betiği.
- Ek belgeler: [12 · kod yapısı](12-kod-yapisi-ve-sozlesmeler.md), [KAYNAKLAR](KAYNAKLAR.md), [terimler](terimler.md), şablonlar.
- İlerleme panosu ve mimari GIF'i ([rapor/](rapor/), [gorseller/mimari.gif](gorseller/mimari.gif)).

### 30 Ekim · Proje incelemesi ve düzeltmeler (10 commit)

Projenin baştan sona bir incelemesi yapıldı (mimari, veri, hukuk, gizlilik, ölçüm). Bulunan sorunlar düzeltildi:

| Sorun | Düzeltme |
|---|---|
| Rüya içeren LLM yanıtları Drive'daki önbellekte birikebilirdi | Rüya içeren istekler artık varsayılan olarak önbelleğe **yazılmıyor**. Açmak için `RUYA_SORGU_ONBELLEGI=on` gerekiyor. Değerlendirme betiği bunu kendisi açıyor, çünkü test setindeki rüyalar zaten repoda. |
| OpenITI adresleri `master` dalını gösteriyordu; kaynak değişirse `entry_id`'ler (satır numarasına bağlı) kayardı | Nablusi ve İbn Sirin adresleri belirli commit'lere sabitlendi. İndirilen dosyanın SHA256 özeti beklenenle uyuşmazsa indirme hata veriyor. |
| İndirme yarıda kalırsa özetler kaybolabiliyordu | Özet dosyası her indirmeden sonra yazılıyor. |
| Lisans alanı yalnızca "boş değil" diye denetleniyordu | Geçerli lisans kodları listesi eklendi ve testle denetleniyor. |
| Mimari testi göreli içe aktarmaları (`from ..x import`) göremiyordu | Göreli içe aktarma yasaklandı; zeyrek de tembel yüklenen paketlere eklendi. |
| "Atıf kapsamı" ölçütünün birimi belirsizdi | Birim "iddia bölümü" olarak tanımlandı ([06](06-degerlendirme.md)). |

Sonra Hafta 1 deneme notebook'u yazıldı: [`notebooks/deneyler/01_veri_ve_ceviri.ipynb`](../notebooks/deneyler/01_veri_ve_ceviri.ipynb).

---

## 4. Şu anki durum

**Toplam:** 59 commit · 167 test geçiyor · veri henüz indirilmedi · Colab'de henüz hiçbir şey çalıştırılmadı.

### Çalışan kod

| Dosya | Ne yapıyor |
|---|---|
| `src/ruya/config.py` | Ortam algılama, yollar, model adları, fiyatlar, ayarlar |
| `src/ruya/schemas.py` | Bütün veri yapıları |
| `src/ruya/ingest/kaynaklar.py` | 4 kaynağın künyesi, lisansı, sabit adresi |
| `src/ruya/pipeline/run.py` | Boru hattı çatısı (adımlar boş) |
| `dosya.py`, `kayit.py`, `etik.py`, `hatalar.py`, `llm/talimatlar.py` | Yardımcılar |
| `scripts/download_sources.py` | Kaynakları Drive'a indirip SHA256 ile denetler |
| `notebooks/_kurulum.py`, `00_ortam_kontrolu.ipynb` | Colab kurulumu ve kontrolü |
| `notebooks/deneyler/01_veri_ve_ceviri.ipynb` | Hafta 1 denemesi |

### İmzası hazır, gövdesi boş olanlar

Bu dosyalardaki her fonksiyon `NotImplementedError("Hafta N …")` ile bitiyor, yani hangi hafta yazılacağı kodda yazılı.

| Hafta | Dosyalar |
|---|---|
| 2 | `ingest/miller.py`, `ingest/nablusi.py`, `text/turkce.py` |
| 3 | `enrich/assign_symbols.py`, `enrich/translate.py`, `index/build_symbols.py` |
| 4 | `llm/client.py`, `pipeline/extract.py`, `pipeline/map.py`, `pipeline/retrieve.py` |
| 5 | `pipeline/synthesize.py`, `app/gradio_app.py`, `degerlendirme/*` |
| 6–8 | `index/build_vectors.py`, `index/store.py`, `index/yedek.py`, `ingest/freud.py`, `ingest/ibn_sirin.py`, `enrich/conditions.py` |

### Henüz olmayanlar

- **Talimatlar:** `prompts/` altında hiç talimat dosyası yok (ilki Hafta 3'te).
- **Sembol sözlüğü:** `sozluk/symbols.json` boş (50 sembol Hafta 3'te).
- **Test seti:** Hiç yok (20 rüya Hafta 3'te).

---

## 5. Sırada ne var?

### Hemen: kurulum (~30 dk, senin işin) · [10-kurulum-rehberi.md](10-kurulum-rehberi.md)

1. Claude Console'da API anahtarı oluştur ve aylık harcama limiti koy.
2. Drive'da `MyDrive/ruya-tabirnamesi/` klasörünü aç.
3. Colab Secrets'a `ANTHROPIC_API_KEY` ve `GITHUB_TOKEN` ekle. Repo özel olduğu için token gerekli; yalnızca bu repoyu okuyabilen fine-grained bir token yeterli.
4. Colab'de `00_ortam_kontrolu.ipynb`'yi çalıştır. Testler bilgisayardaki gibi geçmeli.

### Sonra: Hafta 1 denemesi → K0 kararı · [deneyler/01](deneyler/01-veri-ve-ceviri.md)

`01_veri_ve_ceviri.ipynb`'yi Colab'de sırayla çalıştır. Notebook dört hipotezi ölçüyor:

| | Soru | Eşik | Sen ne yapacaksın |
|---|---|---|---|
| H1 | Nablusi paragrafları kurallarla doğru ayrışıyor mu? | 50'de ≥ 48 | Tabloya bakıp yanlışları `HATALI_H1`'e yazmak |
| H2 | Claude alt paragrafların sembolünü doğru buluyor mu? | 10'da ≥ 8 | Türkçe özete bakıp `DOGRU_H2`'yi doldurmak |
| H3 | Çeviri kalitesi yeterli mi? | Ortalama ≥ 3/5 | 20 çeviriyi aslıyla okuyup puanlamak |
| H4 | Bütün Nablusi'nin çevirisi bütçeye sığıyor mu? | Opus ile ≤ 15 $ | Hiçbir şey; notebook kendisi hesaplıyor |

Son hücrenin yazdırdığı tabloyu deney belgesine yapıştıracağız. **Kritik karar:** Çeviri 3/5'in altında kalırsa çeviri talimatı iyileştirilecek ya da İngilizce ara katman denenecek; bu takvime 1 hafta ekler.

İlk indirmeden sonra Gutenberg kaynaklarının SHA256 değerleri `KAYNAK_OZETLERI.json`'dan `kaynaklar.py`'ye işlenecek. Bunu bana yapıştırman yeterli.

### Takvimin geri kalanı · [08](08-yol-haritasi-takvim.md)

| Tarih | Ne | Kilometre taşı |
|---|---|---|
| 2–8 Kasım | Miller ve Nablusi ayrıştırıcıları, Türkçe metin normalleştirme | |
| 9–15 Kasım | 50 sembollük sözlük, sembol atama, Batch API ile çeviri, 20 rüyalık test seti | **K1 · Veri hazır** |
| 16–22 Kasım | LLM istemcisi, çıkarım, eşleme, getirme | |
| 23–29 Kasım | Sentez, Gradio arayüzü, ilk ölçüm | **K2 · v0.1-mvp** (uçtan uca çalışan ilk sürüm) |
| 30 Kasım–13 Aralık | Bütün korpus, vektör arama (Chroma), reranker, Freud, D1–D3 deneyleri | **K3 · v0.2** |
| 14 Aralık–10 Ocak | İbn Sirin, koşullu yorum, bağlam formu, uzlaşı/ayrışma çıktısı (yılbaşı tamponu dahil) | **K4 · v0.3** |
| 11–17 Ocak | Opus, Sonnet ve Haiku karşılaştırması, son README | **K5 · v1.0** |

Her hafta aynı döngüyle ilerleyeceğiz: ilgili belgeyi oku → orkestra planı → agent'lar yazar → ben doğrularım → commit → sen push edip Colab'de çalıştırırsın → sonucu belgeye işleriz.

---

## 6. Açık kararlar ve bekleyen küçük işler

| Konu | Durum | Nerede |
|---|---|---|
| **S3** · Model ve aylık bütçe tavanı | Cevap bekliyor; öneri: Opus 5.5 ile başla, tavan 10 $/ay | [09](09-riskler-ve-acik-sorular.md) |
| **S4** · Repo özel mi, açık mı? | Repo şu an özel görünüyor; belgede de "özel" diye işaretlenmeli | [09](09-riskler-ve-acik-sorular.md) |
| Haiku'nun önbellek okuma fiyatı | `config.py`'de boş, Haiku maliyeti olduğundan yüksek hesaplanıyor; doğrulanmış fiyat bulununca eklenecek | `src/ruya/config.py` |
| Gutenberg SHA256 değerleri | İlk indirmeden sonra işlenecek | `src/ruya/ingest/kaynaklar.py` |

---

## 7. Kısa sözlük

| Terim | Anlamı |
|---|---|
| **RAG** | Getirmeyle güçlendirilmiş üretim: LLM cevabı kendi hafızasından değil, getirilen kaynak metinlerden yazar |
| **Madde** | Bir tabirnamedeki tek bir kayıt (ör. Nablusi'deki "yılan" paragrafı); `entries.jsonl`'daki bir satır |
| **symbol_id** | Bir sembolün dilden bağımsız kimliği (`yilan`); bütün kaynakları birbirine bağlayan anahtar |
| **entry_id** | Bir maddenin kimliği: `kaynak:satır_no` (ör. `nablusi:004123`) |
| **Alt paragraf** | Nablusi'de "ومن رأى" ("kim … görürse") ile başlayan paragraf; çoğunlukla önceki başlığa ait, bazen yeni bir sembol |
| **Koşullu yorum** | Aynı sembolün görene göre farklı yorumu ("bekâr görürse …, evli görürse …") |
| **Batch API** | Claude'a toplu istek gönderme; %50 indirimli, sonuç 24 saat içinde |
| **Orkestra** | Kod yazdırma aracı: Claude plan yazar, EVREN agent'ları yazar, Claude doğrular |
| **K0–K5** | Takvimdeki kilometre taşları |
