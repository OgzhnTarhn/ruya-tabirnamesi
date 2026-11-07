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
| 2026-11-05 | asama3-hibrit-deepseek | 8cefe2e | 45 rüya (sentetik; 2'si 503 ile düştü) | cikarim_v2, sentez_v3 | %78 | %86 | 0 | %86 | — | 2,7 | %100 | ölçülmedi | ölçülmedi | 0 | 177 | 0,00 |
| 2026-11-06 | asama3-cikarim-v3 | c300307 | 45 rüya (sentetik; 503'ler yeniden koşuldu) | cikarim_v3, sentez_v3 | %96 | %87 | 0 | %87 | — | 2,7 | %100 | 0 (8 rüya elle) | ölçülmedi | 0 | önbellekli, ölçülemedi | 0,00 |

## Notlar

Her satırın altına, sayıları değiştiren şeyi bir cümleyle yaz (ör. "cikarim_v2: çok kelimeli sembol örnekleri eklendi").

- **2026-11-02 · asama1-deepseek:** Test seti sentetik ve gözden geçirilmedi. Medyan yerine ortalama süre yazıldı. r006 `ReadTimeout` ile düştü. Atıf kapsamı düşük çünkü `sentez_v1` başlıkları ayrı bölüm istiyor, ölçüt ise yalnızca `#` ile başlayanları başlık sayıyor; ayrıca r005 ve r015 yorumlarında başlıktan başka içerik yok. Recall düşük çünkü `en_fazla_sembol` sınırı eşlemeden önce uygulanıyor ve "güvercin sürüsü", "deniz kenarı" gibi ifadeler eşlenmiyor. Sembolü olmayan rüyalar da gereksiz yere sentezleniyor (r011, r016, r018).
- **2026-11-02/03 · sentez_v2:** Süreler önbellekten gelmeyen sentez çağrılarının medyanıdır (DeepSeek 14, MiMo 13 rüya); raporun yazdığı 121 ve 153 sn önbellekli sıfırları da içerdiği için kullanılmadı. Çıkarım önbellekten geldi, yeni bir rüyada buna dakikalar eklenir. MiMo yalnızca sentezde denendi, üründe model değişmedi. En uzun süre DeepSeek'te 798 sn, MiMo'da 403 sn.
- **2026-11-05 · düşünme kapalı:** Tablodaki sayılar düşünme açıkken ve hibrit getirmeden önce alındı. Düşünme kapalı, sentez_v3 ve hibrit getirmeyle yalnız 8 rüya elle denendi (40–236 sn); test seti yeniden çalıştırılmadı.
- **2026-11-05 · asama3-hibrit-deepseek:** Düşünme kapalı, hibrit getirme ve sentez_v3 ile ilk tam ölçüm. Süre önbelleksiz: medyan 177 sn (çıkarım 52, getirme 5, sentez 100). En çok kaçan sembol `el` (8 rüya): "elimde", "avucumda" gibi ekli beden parçaları çıkarılmıyordu. r013 ve r014 EVREN 503 "model dolu" ile düştü.
- **2026-11-06 · asama3-cikarim-v3:** Recall %78 → %96. Sayıları değiştirenler: cikarim_v3 (ekli beden parçaları, olayın geçtiği yer, ölmüş kişi için `ölü`, madde sıfatı ayrı sembol), sıfat + isim tamlamasında baş isim önce ("gümüş anahtar" → `anahtar`), aynı sembole düşen tekrarların atılması, sözlüğe gülümsemek/avuç/parmak/ölmek/tabut varyantları. Çıkarım önbellekten geldiği için süre ölçülemedi. 503'te bekleme 15/30/60 sn'ye çıkarıldı, yine de 3 rüya düştü ve ikinci koşuda tamamlandı.
- **Precision neden %87:** "Fazla" sayılanların çoğu gerçekten rüyada geçen semboller (`bahce`, `anne`, `baba`, `toprak`, `duvar`, cami → `mescit`); test setinin beklenen listeleri eksik. Gerçekten yanlış olanlar az: "uzay gemisi" → `gemi`, "anahtarı düşürdüm" → `dusmek`. Test seti gözden geçirilince sayı değişir.
- **Test seti sorunları (gözden geçirmen için):** iki rüya iki kez yazılmış ("parmağımda bir yüzük…", "kız çocuğu çiçek…"), yani 45 satırda 43 farklı rüya var. r009'da "bir tas su" kâse demek, beklenen listesindeki `tas` taş sembolü.
- **Sadakat (8 rüya elle):** r003, r009, r013, r020, r026, r031, r040, r045. Uydurma atıf ya da kaynakta olmayan iddia görülmedi; olumsuzlanan örümcek (r040) yorumlanmadı; her yanıtta uyarı var. Bir çeviri hatası yoruma taşınmış: ibn_sirin:006237'de Arapça ذَكَر (erkeklik organı) "zikir" diye çevrilmiş. Bazı atıflar konuya gevşek bağlı (deniz kenarı bölümünde balık maddesi).
- **2026-11-06 · cikarim_v4 (yarım):** v3'teki "`taş` (tas değil)" örneği kâse anlamındaki "tas"ı bozduğu için v4 yazıldı ve harf katlama yedeği kaldırıldı. Ölçüm 18 rüyada durduruldu: aynı 18 rüyada recall v3 %90, v4 %89; tam ölçüm yapılmadı. Bu 18 rüyada önbelleksiz medyan süre 204 sn: rüya başına sembol 3'ten 5,5'e çıktığı için sentez uzuyor (sentez hızı 12 → 16 token/sn, yavaşlık modelden değil).
- **2026-11-03 · kök eşleme düzeltmesi:** Bu iki ölçümde kök eşleme çalışmıyordu (zeyrek NLTK verisi eksikti, hata yutuluyordu). Düzeltmeden sonra çıkarım önbelleğiyle yalnız eşleme yeniden hesaplandı: recall %82 (51/62), yanlış eşleme yok. Uçtan uca ölçüm yenilenmedi.
