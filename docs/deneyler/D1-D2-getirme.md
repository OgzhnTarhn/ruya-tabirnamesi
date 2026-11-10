# D1 · D2 · Vektör kolu, HyDE ve reranker (ön sonuç: gümüş etiket)

> Tarih: 11 Kasım 2026 · Hafta: 12 · Betik: `eval/getirme_deneyi.py` · Commit: `4618b4a`

**Durum:** Ön sonuç. Etiketleri bir LLM hakem verdi ([15](../15-kalan-isler-plani.md) K12).
Kesin sonuç, `data/deneyler/getirme/etiketler.md` elle işaretlenince aynı komutla
hesaplanacak ve bu not güncellenecek.

## Soru

Hibrit getirmenin kolları doğru maddeyi üst sıralara taşımaya katkı veriyor mu?
- **D1:** vektör kolu (sorgu vektörü + HyDE vektörü) olmadan, yalnız sözlük + BM25 yeter mi?
- **D2:** reranker olmadan, yalnız RRF sırası yeter mi?
- Ek: HyDE (çıkarımda yazılan varsayımsal madde) işe yarıyor mu?

## Hipotez

Reranker en büyük katkıyı verir (BM25 ve vektör listeleri gürültülü). Vektör kolu sözlükte
olmayan ve farklı ifade edilen maddeleri yakalar; HyDE'nin katkısı küçüktür.

## Yöntem

- Veri: [alt küme](../../eval/dataset/alt_kume_15.txt), 15 sentetik rüya, 96 sembol
  (çıkarım bir kez, bütün çeşitler aynı eşleşmelerle).
- Çeşitler (`hibrit.siralama`: eşiksiz, kaynak sınırsız, bağlam koşulsuz ilk 10):

  | Çeşit | Kollar | Sıralama |
  |---|---|---|
  | G0 | sözlük + BM25 + vektör + HyDE | reranker (şimdiki hâl) |
  | G1 | sözlük + BM25 + vektör + HyDE | yalnız RRF |
  | G2 | sözlük + BM25 | reranker |
  | G3 | sözlük + BM25 + vektör | reranker |

- Etiket: bütün çeşitlerin ilk 5'i birleştirildi (havuz, 780 aday, kimlik sırasıyla).
  Hakem (`deepseek-v4.1-flash`, `getirme_hakemi_v1`) her sembol için rüya metnini ve
  numaralı aday metinlerini gördü; kaynak adını ve kimliği görmedi. 492 aday (%63) ilgili
  sayıldı; 2 sembolde hiçbiri ilgili bulunmadı, ölçüm 94 sembolle.
- Ölçüt: Recall@5 (ilk 5'te bulunan ilgili / min(5, ilgili sayısı)) ve MRR.
- Maliyet: 0 $ (EVREN ücretsiz dönem).

## Sonuç

| Çeşit | Recall@5 | MRR | G0'ın daha iyi olduğu sembol | G0'ın daha kötü olduğu sembol |
|---|---|---|---|---|
| G0 · hepsi + reranker | **%88,6** | **0,951** | — | — |
| G1 · reranker yok | %82,1 | 0,906 | 27 | 16 |
| G2 · vektör kolu yok | %84,6 | 0,912 | 15 | 13 |
| G3 · HyDE yok | %86,3 | 0,939 | 8 | 6 |

Gözlemler:

- Şimdiki hâl (G0) her iki ölçütte de en iyi. İlk Recall@5 sayısı: %88,6 (A3 hedefi ≥ %80),
  ama gümüş etiketle.
- Reranker'ın katkısı en belirgin olanı: 43 farklı sembolün 27'sinde G0 daha iyi.
- Vektör kolu ve HyDE ortalamada katkı veriyor, ama sembol bazında kazanan ve kaybeden
  sayıları birbirine yakın (15'e 13, 8'e 6): 94 sembolle gürültüden ayırmak zor.
- Hakem cömert (%63 ilgili); insan etiketinde oranlar değişebilir.
- Recall@5 yalnız sıralamayı ölçer; gerçek boru hattı bundan sonra eşik (0,15) ve kaynak
  başına 1 madde uygular.

## Karar (ön)

- **D2: Reranker kalır.**
- **D1: Vektör kolu kalır.** Ortalamada +4 puan, maliyeti küçük (embedding çağrısı < 1 sn).
- **HyDE: şimdilik kalır, kaldırma adayı.** Katkısı ölçülebilir değil, ama çıkarımın çıktı
  tokenlarının büyük kısmını o yazıyor ve çıkarım en dalgalı adım. İnsan etiketleri de HyDE'nin
  katkısını göstermezse çıkarımdan çıkarılır (yeni talimat sürümü + tam ölçüm).
- Hangi belge güncellendi: [deneyler](README.md), [15](../15-kalan-isler-plani.md).
