# Ölçümler

> Her kilometre taşında ve her deneyden sonra bir satır eklenir (docs/06, bölüm 3).
> Ayrıntılı rapor `data/raporlar/<tarih>_<etiket>.md` dosyasında durur. Buraya yalnızca özet girer.
> Hedefler: MVP sütunu Aşama 1, A3 sütunu Aşama 3 sonu için (docs/06, bölüm 2).

## Özet tablo

| Tarih | Etiket | Commit | Test seti | Talimatlar | Sembol recall | Sembol precision | Olumsuzlama hatası | Eşleme doğruluğu | Recall@5 | Kaynak çeşitliliği | Atıf kapsamı | Sadakat ihlali (elle) | "Bulunamadı" | Etik ihlal | Medyan süre (sn) | Ort. maliyet ($) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| *hedef MVP* | | | 20 rüya | | ≥ %80 | ≥ %80 | 0 | ≥ %85 | ölçülür | ≥ 1,5 | %100 | 0 | %100 | 0 | ≤ 30 | ≤ 0,15 |
| *hedef A3* | | | 40–50 rüya | | ≥ %90 | ≥ %90 | 0 | ≥ %95 | ≥ %80 | ≥ 2 | %100 | 0 | %100 | 0 | ≤ 20 | ≤ 0,10 |
| 2026-11-02 | asama1-deepseek | 57426f9 | 20 rüya (sentetik; 1'i zaman aşımı) | cikarim_v1, sentez_v1 | %63 | %100 | 0 | %100 | — | 2,9 | %40 | ölçülmedi | ölçülmedi | 0 | ort. 538 | 0,00 |
| 2026-11-02 | asama1-deepseek-sentez-v2 | a1de337 | 20 rüya (sentetik) | cikarim_v1, sentez_v2 | %77 | %100 | 0 | %100 | — | 2,9 | %100 | ölçülmedi | ölçülmedi | 0 | 196 (yalnız sentez) | 0,00 |
| 2026-11-03 | asama1-mimo-sentez | a1de337 | 20 rüya (sentetik) | cikarim_v1, sentez_v2 | %77 | %100 | 0 | %100 | — | 2,9 | %100 | ölçülmedi | ölçülmedi | 0 | 207 (yalnız sentez) | 0,00 |

## Notlar

Her satırın altına, sayıları değiştiren şeyi bir cümleyle yaz (ör. "cikarim_v2: çok kelimeli sembol örnekleri eklendi").

- **2026-11-02 · asama1-deepseek:** Test seti sentetik ve gözden geçirilmedi. Medyan yerine ortalama süre yazıldı. r006 `ReadTimeout` ile düştü. Atıf kapsamı düşük çünkü `sentez_v1` başlıkları ayrı bölüm istiyor, ölçüt ise yalnızca `#` ile başlayanları başlık sayıyor; ayrıca r005 ve r015 yorumlarında başlıktan başka içerik yok. Recall düşük çünkü `en_fazla_sembol` sınırı eşlemeden önce uygulanıyor ve "güvercin sürüsü", "deniz kenarı" gibi ifadeler eşlenmiyor. Sembolü olmayan rüyalar da gereksiz yere sentezleniyor (r011, r016, r018).
- **2026-11-02/03 · sentez_v2:** Süreler önbellekten gelmeyen sentez çağrılarının medyanıdır (DeepSeek 14, MiMo 13 rüya); raporun yazdığı 121 ve 153 sn önbellekli sıfırları da içerdiği için kullanılmadı. Çıkarım önbellekten geldi, yeni bir rüyada buna dakikalar eklenir. MiMo yalnızca sentezde denendi, üründe model değişmedi. En uzun süre DeepSeek'te 798 sn, MiMo'da 403 sn.
- **2026-11-03 · kök eşleme düzeltmesi:** Bu iki ölçümde kök eşleme çalışmıyordu (zeyrek NLTK verisi eksikti, hata yutuluyordu). Düzeltmeden sonra çıkarım önbelleğiyle yalnız eşleme yeniden hesaplandı: recall %82 (51/62), yanlış eşleme yok. Uçtan uca ölçüm yenilenmedi.
