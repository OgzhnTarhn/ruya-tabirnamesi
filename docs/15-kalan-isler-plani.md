# 15 · Kalan İşler Planı (10 Kasım 2026)

MVP ölçütleri 7 Kasım'da sağlandı; arayüz yorumu geldikçe gösteriyor (10 Kasım). Bu belge
[08](08-yol-haritasi-takvim.md)'deki açık kutuları, [09](09-riskler-ve-acik-sorular.md)'daki
açık soruları ve ölçüm notlarını tek sıraya koyar. Takvim 08'in yerine geçmez; 08'deki
kutular iş bittikçe işaretlenir.

## 1. Durum

| Alan | Durum |
|---|---|
| Boru hattı | çıkarım `cikarim_v4` → eşleme → hibrit getirme (sözlük + BM25 + vektör + HyDE → RRF → reranker, eşik 0,15) → paralel sentez (`sentez_sembol_v2` + `genel_yorum_v1`) |
| Son tam ölçüm | 6 Kasım, 45 rüya, `cikarim_v3` + `sentez_v3`: sembol recall %96, precision %87, atıf kapsamı %100 |
| Ölçülmemiş | Şimdiki boru hattı (v4 + paralel sentez) tam setle hiç ölçülmedi; yalnız 5 rüyalık süre ölçümleri var |
| Recall@5 | Ölçülemiyor: test setinde `beklenen_maddeler` boş |
| Süre | Rüya başına 2,5–8 dk; çoğu geçidin dalgalanması (aynı istek 18 sn ile 151 sn arasında) |
| Bütçe | EVREN 1 Aralık 2026'ya kadar ücretsiz (R13) |

## 2. Kritik kararlar

| # | Karar | Gerekçe |
|---|---|---|
| K1 | **Hız işi kapandı.** Çıkarım `cikarim_v4`'te kalır, şema kısaltılmaz. | `cikarim_v5` denemesi recall'ı düşürdü; kalan süre geçidin dalgalanmasından geliyor ve arayüz sonucu geldikçe gösteriyor ([olcumler](olcumler.md), 10 Kasım). |
| K2 | **API'ye yüklenen bütün ölçümler 1 Aralık'tan önce yapılır:** temel ölçüm, D3, D4 ve getirme deneyleri. | Ücretsiz dönemden sonra her ölçüm ücretli. |
| K3 | **D1 yeniden tanımlandı:** "e5-large / Qwen3-0.6B" yerine **vektör kolunun katkısı**: sözlük + BM25 ile, sözlük + BM25 + vektör + HyDE karşılaştırılır. | Vektör yedeği eşlemede kapatıldı (4 Kasım); embedding artık getirmede çalışıyor. Başka bir embedding için korpusu yeniden gömmek gerekir; önce kolun kendisinin işe yarayıp yaramadığı ölçülür. |
| K4 | **D1 ve D2 yalnız getirme düzeyinde ölçülür; sentez çalışmaz.** Her rüyanın çıkarımı bir kez yapılır ve saklanır; getirme çeşitleri bunun üzerinde koşar, sıralamalar dosyaya yazılır. Recall@5 etiketler gelince çevrimdışı hesaplanır. | Sentez en pahalı ve en yavaş adım; getirme deneyine katkısı yok. Etiketler geç gelse de ölçüm 1 Aralık'tan önce bitmiş olur. |
| K5 | **Altın etiket havuzlamayla hazırlanır (TREC usulü).** Her rüya ve sembol için bütün getirme çeşitlerinin ilk 5'i birleştirilir; sen yalnız bu havuzu "ilgili / değil" diye işaretlersin. İlk dilim **15 rüya**. | Bütün korpusu taramadan, hiçbir çeşidi kayırmadan etiket çıkar. docs/06'nın "elle doldurursun" kuralı korunur: karar sende, araç yalnız adayları önüne koyar. |
| K6 | **D3 ve D4 15 rüyalık alt kümeyle yapılır** (K5'teki 15 rüya). Temel ölçüm 45 rüyanın tamamıyla yapılır. | 45 rüya × birkaç çeşit, geçidin hızıyla günler sürer; karar için 15 rüya yeter. |
| K7 | **D4'te rakip model `mimo-v2.6-pro`**, yalnız sentezde. Çıkarım `deepseek-v4.1-flash`'ta kalır. | 3 Kasım'daki mimo denemesi eski boru hattıyla yapılmıştı; çıkarım recall'ı zaten %96. |
| K8 | **D5 (yerel model) yapılmayacak.** | GPU yok, API'siz yerel model bu proje için öğrenme getirisi düşük; 08'de isteğe bağlıydı. |
| K9 | **Etiketler senin kararın; ben öneririm, ben atmam.** Öneri: `v0.1-mvp` = MVP denetiminin commit'i (7 Kasım), `v0.2` = D1–D3 notları, `v0.3` = temel ölçüm, `v1.0` = D4 + son README. | CLAUDE.md: push ve sürüm kararı kullanıcıda. |
| K11 | **Ölçümler orkestra işleriyle ve birbirleriyle aynı anda koşmaz** (aynı modeli kullanıyorlarsa). 429'da istemci 15–60 sn bekler. | 10 Kasım temel ölçümünde 9 rüya, D3/D4'te 8 rüya eşzamanlı istek sınırıyla düştü; orkestra agent'ları da aynı hesabı kullanıyor. |
| K12 | **D1/D2 için önce gümüş etiket:** havuzu bir LLM hakem (`deepseek-v4.1-flash`, `getirme_hakemi_v1`) işaretler ve ön karar bununla verilir. Senin etiketlerin gelince aynı hesap tekrarlanır, hakemle uyuşma oranı da yazılır; kesin karar senin etiketlerinle. | 11 Kasım: etiketleme şimdilik yapılamıyor; hakem ücretsiz dönemde çalışmalı. Hakem reranker'dan (qwen) farklı bir model, çeşitlerden birini kayırmaz. |
| K10 | **Deney kodu `src/ruya/degerlendirme/` altına girer** (sınanır), çalıştırma betikleri `eval/` altında durur. Model ve ayar değişikliği kodu değiştirmeden `Ayarlar` ve parametrelerle yapılır. | Model adları yalnız `config.py`'de (CLAUDE.md); deney kodu tekrar kullanılabilir kalır. |

## 3. Fazlar

**Durum (10 Kasım akşamı):** Faz 1 bitti (temel ölçüm, getirme deney aracı, sıralamalar,
etiket dosyası `data/deneyler/getirme/etiketler.md`). Faz 2'de D3 ve D4 bitti; D1/D2
senin etiketlerini bekliyor.

### Faz 1 · 10–14 Kasım: temel ölçüm ve getirme deney aracı

| # | İş | Yapan | Çıktı |
|---|---|---|---|
| 1.1 | Temel ölçüm: 45 rüya, şimdiki boru hattı, etiket `asama3-paralel-sentez` | Claude (arka planda, ~3–4 saat) | `data/raporlar/…`, olcumler satırı |
| 1.2 | 15 rüyalık alt kümeyi seç (kısa/uzun, olumsuzlama, bağlam, çok sembollü) ve `eval/dataset/` altına kimlik listesi olarak yaz | Claude | `eval/dataset/alt_kume_15.txt` |
| 1.3 | Getirme çeşitleri: `hibrit_getir` kollarını ayardan kapatılabilir yap (vektör, HyDE, reranker) ve eşik/N öncesi sıralı aday listesini döndüren bir işlev ekle | orkestra | kod + testler |
| 1.4 | Getirme deneyi: alt kümede çıkarımı bir kez yap, 4 çeşidi koş, sıralamaları `data/deneyler/getirme/` altına yaz | orkestra (kod), Claude (çalıştırma) | `getirme_deneyi.py`, ham sıralamalar |
| 1.5 | Havuz ve etiket dosyası: her rüya/sembol için havuz maddeleri, Türkçe metinleriyle; işaretlemesi kolay bir dosya | orkestra | `data/deneyler/getirme/etiket_*.md` |

Getirme çeşitleri (K3, K4):

| Çeşit | Kollar | Sıralama | Soru |
|---|---|---|---|
| G0 | sözlük + BM25 + vektör + HyDE | reranker | şimdiki hâl |
| G1 | sözlük + BM25 + vektör + HyDE | yalnız RRF | **D2**: reranker işe yarıyor mu? |
| G2 | sözlük + BM25 | reranker | **D1**: vektör kolu işe yarıyor mu? |
| G3 | sözlük + BM25 + vektör (HyDE yok) | reranker | HyDE işe yarıyor mu? |

### Faz 2 · 15–24 Kasım: deneyler

| # | İş | Yapan | Çıktı |
|---|---|---|---|
| 2.1 | Havuzu etiketle: 15 rüyada ~100 sembol, sembol başına havuzda 5–12 madde; toplam 3–4 saat, birkaç oturumda | **sen** | işaretli etiket dosyası |
| 2.2 | Etiketleri `beklenen_maddeler`'e aktaran ve G0–G3 için Recall@5 / MRR hesaplayan çevrimdışı hesap | orkestra | `docs/deneyler/D1-D2-getirme.md` |
| 2.3 | D3: N = 1, 2, 3 ile 15 rüya; kaynak çeşitliliği, atıf kapsamı, süre, sentez tokenı; 3 rüyada elle sadakat | Claude (koşu), orkestra (gerekirse betik) | `docs/deneyler/D3-n-degeri.md` |
| 2.4 | D4: sentez `mimo-v2.6-pro` ile 15 rüya; aynı ölçütler + süre | Claude | `docs/deneyler/D4-model.md` |
| 2.5 | Her deneyin kararını ilgili belgeye işle (docs/13, config) | Claude | belge commit'leri |

D3 ve D4 aynı modeli kullanmadığı sürece aynı anda koşabilir; aynı modelde 4 eşzamanlı istek
sınırı var, temel ölçümle D3 aynı anda koşmaz.

### Faz 3 · 25–30 Kasım: kararları uygula, son ölçüm

| # | İş | Yapan |
|---|---|---|
| 3.1 | Deney kararları ayar değiştiriyorsa (reranker, N, model) uygula | orkestra / Claude |
| 3.2 | Değişiklik olduysa 45 rüyayla son ölçüm | Claude |
| 3.3 | README ölçüm tablosu, [14](14-ders-notu.md) ders notu (paralel sentez, akış, deneyler), [ilerleme özeti](ilerleme-ozeti.md), ilerleme panosu | Claude |

### Faz 4 · Aralık: senin işlerin ve kapanış

Bunlar API gerektirmez; sıra önerisi:

| # | İş | Tahmini süre | Neden |
|---|---|---|---|
| 4.1 | 45 sentetik rüyayı gözden geçir (eval/dataset) | 1 saat | Ölçümlerin hepsi bu sete dayanıyor |
| 4.2 | 143 sembolün kategorilerini gözden geçir | 1 saat | Eşleme bunlara dayanıyor |
| 4.3 | `kapsam` alan 20 maddeyi elle kontrol et | 30 dk | Kurallar dar, elle bakılmadı |
| 4.4 | Çevirilerden 10 Nablusi + 10 Miller maddesine 1–5 puan ver | 1 saat | Çeviri kalitesi hiç puanlanmadı |
| 4.5 | `docs/terimler.md`, `docs/kurallar.md` | okumalarına bağlı | Kendi notların |
| 4.6 | [09](09-riskler-ve-acik-sorular.md) S1, S4, S5 | 10 dk | Repo görünürlüğü ve paylaşım kararı |
| 4.7 | OpenITI lisansını Zenodo'da gör; künyeyi KAYNAKLAR.md'ye ekleriz | 10 dk | NC lisans |
| 4.8 | Sürüm etiketleri (K9) ve push | 10 dk | Karar sende |

KVKK (09) proje kişisel kaldığı sürece ertelenir; S5'e "açacağım" dersen öne alınır.

## 4. Kapsam dışı

- Çıkarım şemasını kısaltmak, HyDE'yi ayrı çağrıya almak (K1).
- Yeni embedding modeliyle korpusu yeniden gömmek (D1 sonucu vektör kolunun çok işe yaradığını
  gösterirse yeniden düşünülür).
- D5, Zhougong Jiemeng ve Talmud kaynakları (Ocak sonrası, 08).
