# 17 · Kapanış Planı (21 Kasım 2026)

[15](15-kalan-isler-plani.md)'in yerine geçen son plan. Teknik iş bitti; kalanlar arayüz
([16](16-arayuz-plani.md)), son belgeler ve tek bir sürüm etiketi.

## 1. Kararlar

| # | Karar | Gerekçe |
|---|---|---|
| S1 | **Tek sürüm etiketi: `v1.0`.** K9'daki `v0.1-mvp` … `v0.3` ara etiketleri atılmaz. | 21 Kasım: kullanıcı tek sürümün yettiğini söyledi. |
| S2 | `v1.0` arayüz yenilemesi ve son belgeler commit edildikten sonra atılır; etiketi ve push'u kullanıcı yapar. | CLAUDE.md: push kullanıcıda. |
| S3 | Gözden geçirme işlerini (15, Faz 4: test seti, sembol kategorileri, `kapsam`, çeviri puanları, terimler/kurallar, S1/S4/S5, OpenITI lisansı) kullanıcı kendisi yapar; bu plan onları beklemez. | 21 Kasım: kullanıcı üstlendi. |
| S4 | D1/D2 **gümüş etiketle** kapanır. İnsan etiketi gelirse aynı komutla yeniden hesaplanır, ama `v1.0` onu beklemez. HyDE şimdilik kalır. | Etiketleme 3–4 saat; ön sonuç kararı değiştirmiyor (G0 en iyi). |
| S5 | 1 Aralık'tan sonra yeni ölçüm yapılmaz. Arayüz yenilemesi boru hattına dokunmadığı için yeni ölçüm gerektirmez. | EVREN ücretsiz dönemi 1 Aralık'ta bitiyor (R13). |

## 2. Son sonuçlar (README ve sunum için)

Test seti: 45 sentetik rüya (43 farklı; gözden geçirilmedi). En iyi ve son boru hattı:
`cikarim_v4` → eşleme → hibrit getirme (sözlük + BM25 + vektör + HyDE → RRF → reranker, eşik
0,15) → paralel sentez (`sentez_sembol_v2` + `genel_yorum_v1`), N=1, sentez ve çıkarım
`deepseek-v4.1-flash`.

| Ölçüt | Sonuç | Hedef (A3) | Kaynak |
|---|---|---|---|
| Sembol recall | **%96** | ≥ %90 ✔ | 10 Kasım temel ölçüm |
| Sembol precision | **%87** | ≥ %90 ✘ (fazla sayılanların çoğu rüyada gerçekten geçiyor; test seti eksik) | 10 Kasım |
| Eşleme doğruluğu | %87 | ≥ %95 ✘ | 10 Kasım |
| Getirme Recall@5 | **%88,6** (MRR 0,951), gümüş etiket | ≥ %80 ✔ | D1/D2, 11 Kasım |
| Kaynak çeşitliliği | 2,8 | ≥ 2 ✔ | 10 Kasım |
| Atıf kapsamı | **%100** | %100 ✔ | 10 Kasım |
| Olumsuzlama hatası / etik ihlal | 0 / 0 | 0 ✔ | bütün ölçümler |
| Sadakat ihlali (8 rüya elle) | 0 | 0 ✔ | 6 Kasım |
| Medyan süre | 165 sn | ≤ 20 sn ✘ (geçidin hızı; arayüz sonucu geldikçe gösteriyor) | 10 Kasım |
| Maliyet | 0 $ (ücretsiz dönem) | ≤ 0,10 $ | — |

İlerleme özeti: recall %63 (2 Kasım) → %78 (hibrit getirme) → %96 (`cikarim_v3`); atıf
kapsamı %40 → %100 (`sentez_v2`).

Deney kararları: D1 vektör kolu kalır (+4 puan Recall@5), D2 reranker kalır (en büyük katkı,
+6,5 puan), HyDE kaldırma adayı (katkısı gürültü düzeyinde), D3 N=1, D4 sentez deepseek'te
kalır, D5 yapılmadı.

Açık kalan zayıflıklar (dürüstçe yazılacak): test seti sentetik ve gözden geçirilmedi;
Recall@5 LLM hakemin etiketiyle; süre hedefin çok üstünde; bir çeviri hatası yoruma taşındı
(ibn_sirin:006237).

## 3. İş sırası

**Durum (21 Kasım):** K1–K5 bitti; kalan yalnız K6 (`v1.0` etiketi ve push, kullanıcı).

| # | İş | Yapan | Çıktı |
|---|---|---|---|
| K1 | Arayüz yenilemesi ([16](16-arayuz-plani.md), U1–U6) | orkestra + Claude | kod, testler, ekran görüntüleri |
| K2 | README: ölçüm tablosunun altındaki "D1/D2 etiket bekliyor" cümlesini düzelt (artık gümüş etiketli sonuç var); "Son sonuçlar" özet tablosu (bölüm 2); yeni ekran görüntüsü; bilinen sınırlar | Claude | README |
| K3 | [08](08-yol-haritasi-takvim.md) kutuları: D1/D2 ve deney notları işaretlenir, ara etiket kutuları "S1: tek `v1.0`" notuyla kapanır | Claude | 08 |
| K4 | [15](15-kalan-isler-plani.md) durumuna 17'ye yönlendiren bir satır; [ilerleme özeti](ilerleme-ozeti.md), [14 ders notu](14-ders-notu.md) arayüz bölümü, ilerleme panosu | Claude | belgeler, pano |
| K5 | Son kontrol: `uv run pytest`, `uv run ruff check .`, çalışma ağacı temiz | Claude | — |
| K6 | `v1.0` etiketi ve push | **kullanıcı** | `git tag -a v1.0 -m "Rüya Tabirnamesi v1.0"`, `git push --follow-tags` |

## 4. Kullanıcının işleri (bu planı beklemez)

15'teki Faz 4 listesi geçerli: 45 rüyayı gözden geçirmek, 143 sembolün kategorileri,
`kapsam` alan 20 madde, 20 çeviriye puan, terimler/kurallar notları, 09 S1/S4/S5, OpenITI
lisansı. İsteğe bağlı: getirme etiketleri (`data/deneyler/getirme/etiketler.md`); gelirse
D1/D2 kesin sonucu yazılır.

## 5. Kapsam dışı

D5 (yerel model), yeni kaynaklar (Zhougong, Talmud), çıkarım şemasını kısaltmak, yeni
embedding modeli.
