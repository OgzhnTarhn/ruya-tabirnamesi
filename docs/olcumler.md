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
| 2026-11-10 | asama3-paralel-sentez | 696aa88 | 45 rüya (sentetik; 429'la düşen 9'u tek başına yeniden koşuldu) | cikarim_v4, sentez_sembol_v2 + genel_yorum_v1 | %96 | %87 | 0 | %87 | — | 2,8 | %100 | ölçülmedi | ölçülmedi | 0 | 165 | 0,00 |

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

### 2026-11-09 · Süre: paralel sentez (5 rüya)

Önbellek kapalı, aynı 5 rüya (r003, r005, r008, r013, r030), aynı akşam. Geçit o gün yavaştı
(tek çağrı saniyede ~6 token); süreler 5 Kasım'la değil yalnız kendi aralarında karşılaştırılır.
Betik `data/deneyler/hiz5.jsonl` dosyasına yazar; tam test seti koşulmadı.

| Kip | Talimat | Sentez medyanı | Toplam medyanı | Sentez çıktı tokenı (5 rüya) | Atıf kapsamı | Yasak ifade |
|---|---|---|---|---|---|---|
| Tek çağrı | sentez_v4 | 341 sn | 389 sn | 14.811 | %100 | 0 |
| Paralel, 4 eşzamanlı | sentez_sembol_v1 + genel_yorum_v1 | 239 sn | 307 sn | 24.075 | 4'ünde %100, 1'inde %85 | 0 |
| Paralel, 4 eşzamanlı | sentez_sembol_v2 + genel_yorum_v1 | 193 sn | 270 sn | 16.695 | %100 | 0 |

- Paralel kip sentezi yaklaşık %40 kısalttı. v1'de her sembol çağrısı ~575 token yazıyordu;
  v2'de 3 cümle, 3 kaynak ve 20 kelimelik alıntı sınırı tokenı %30 azalttı.
- EVREN hesap başına model için en fazla 4 eşzamanlı istek kabul ediyor; 8 denenince bir rüya
  429 ile düştü. `EN_FAZLA_ESZAMANLI = 4`.
- Kalan sürenin büyük ve en dalgalı parçası çıkarım (26–158 sn, ~330 token, çoğu HyDE metni).
  30 saniye hedefi bu geçitte paralellikle tutmuyor; sıradaki aday çıkarımı kısaltmak ve
  arayüzde bölümleri geldikçe göstermek.

### 2026-11-10 · Süre: kısa çıkarım talimatı (5 rüya, 2 tur)

`cikarim_v5` = v4 + HyDE tek cümle ve en çok 12 kelime, `ham_ifade` en çok dört kelime, en çok
10 sembol. Aynı 5 rüya (r003, r005, r008, r013, r030), önbellek kapalı, sentez kapalı. Her
rüyada v4 ile v5 aynı anda gönderildi; geçidin o anki hızı ikisini eşit etkiledi. Betik
`data/deneyler/cikarim_v5.jsonl` dosyasına yazar.

| Talimat | Çıkarım medyanı | Çıktı tokenı medyanı | Çıktı tokenı (10 çağrı) | Sembol recall | Sembol precision |
|---|---|---|---|---|---|
| cikarim_v4 | 85 sn | 659 | 8.281 | %97,5 | %92,2 |
| cikarim_v5 | 50 sn | 650 | 6.966 | %93,8 | %94,7 |

- Kazancın tamamı uzun rüyalardan geldi (r005, r013: 13–14 sembol yerine 10). Kısa rüyalarda
  token ve süre değişmedi; HyDE'yi kısaltma talimatı çıktıyı fark edilir kısaltmadı.
- 10 sembol sınırı beklenen sembolleri de kesti (r005'te `yol`, bir turda `su`). v5 bir kez
  `cami` yerine `camii` yazdı.
- İki sürümün getirdiği maddeler sembol başına ortalama %84 örtüştü (Jaccard, 63 sembol).
- Aynı rüyanın süresi turdan tura 7 kata kadar değişti (r003: 18 ve 151 sn); geçidin
  dalgalanması talimat farkından büyük.
- **Karar:** v5 kullanılmıyor, `extract.py` v4'te kaldı. Çıkarım bir sembol başına ~90 token
  yazıyor; büyük kısmı JSON alan adları ve HyDE. Gerçek kısaltma şema değişikliği ister.

### 2026-11-10 · Temel ölçüm: şimdiki boru hattı (45 rüya)

`cikarim_v4` + hibrit getirme + paralel sentez (`sentez_sembol_v2` + `genel_yorum_v1`), N=1.
Raporlar `data/raporlar/2026-11-10_asama3-paralel-sentez*.md` (ana koşu ve iki tekrar);
ölçütler rüya sayısına göre birleştirildi.

- İlk koşuda 9 rüya 429 ile düştü: aynı anda çalışan orkestra işleri de aynı hesabın
  `deepseek-v4.1-flash` sınırlarını (4 eşzamanlı istek, dakikalık token) kullanıyordu.
  İstemci 429'da 7 sn bekleyip vazgeçiyordu; artık 503 gibi 15, 30, 60 sn bekliyor (696aa88).
  Tekrarlar başka hiçbir iş çalışmazken yapıldı ve hepsi geçti.
- Sembol recall %96, precision %87: 6 Kasım (`cikarim_v3`) ile aynı düzey; v4 recall'ı düşürmedi.
- Kaçırılan semboller: r005 `yol`, r009 `hastalik` ve `tas`, r011 `cennet`, r015 `el`.
- Medyan süre 165 sn, ortalama 170 sn; tek çağrılı sentezle yapılan 5 Kasım ölçümünde 177 sn
  medyandı, ama geçidin hızı günden güne değiştiği için fark kesin değil.
- Aynı gün D3 ve D4 ([deneyler](deneyler/README.md)): N=1 ve `deepseek-v4.1-flash` kalıyor.
