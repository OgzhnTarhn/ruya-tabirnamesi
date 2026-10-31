# 09 · Riskler ve Açık Sorular

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026

## 1. Senin cevaplaman gereken sorular

Bu sorular planı değiştirebilir. Cevaplar geldikçe ilgili belgeler güncellenecek.

| # | Soru | Neden önemli | Benim varsayımım |
|---|---|---|---|
| S1 | Haftada kaç saat ayırabilirsin? | Takvim buna göre ölçekleniyor | 8–10 saat. Takvim 12 hafta. |
| S2 | ~~Ekran kartın ne?~~ **Cevaplandı (22 Ekim):** GPU işleri Colab'de, veri Drive'da yapılacak. **Güncellendi (31 Ekim):** LLM ve embedding API'den alındığı için GPU gerekmiyor; her şey bilgisayarda. | — | Bkz. [11](11-calisma-ortami.md) |
| S3 | ~~Model önerisini (Opus 5.5) onaylıyor musun? Aylık bütçe tavanın ne?~~ **Cevaplandı (31 Ekim):** Claude API kullanılmıyor; EVREN üzerinden yalnızca `deepseek-v4.1-flash` (TK-03, TK-04). 1 Aralık sonrası bütçe, fiyat açıklanınca yeniden sorulacak. | Maliyet | — |
| S4 | Repo GitHub'da özel mi olsun, herkese açık mı? | Rüyaların ve prompt dosyalarının görünürlüğü | Özel |
| S5 | İleride uygulamayı başkalarına açmayı düşünüyor musun? | Açarsan KVKK ve NC lisanslar baştan ele alınmalı | Hayır, kişisel kalacak |
| S6 | Arapça biliyor musun, ya da çeviri kontrolüne yardım edebilecek biri var mı? | Çeviri kalitesinin kontrolü | Hayır. Kontrol, İngilizce ara çeviriyle ve tutarlılık kontrolüyle yapılacak. |

## 2. Risk kaydı

Olasılık ve etki: D = düşük, O = orta, Y = yüksek.

| # | Risk | Olasılık | Etki | Önlem | Erken uyarı işareti |
|---|---|---|---|---|---|
| R1 | **Arapçadan Türkçeye çeviri kalitesi düşük.** Klasik dil, harekesiz metin, terimler. | O | Y | Hafta 1 denemesi; terim sözlüğü; çeviri talimatında örnekler; gerekirse İngilizce ara katman; Arapça aslın her zaman gösterilmesi | Denemede ortalama puan < 3/5 |
| R2 | **Nablusi'deki alt paragrafların sembol ataması hatalı.** ~3.300 paragraf var. | O | O | LLM ile atama; üst madde bağlantısının korunması; 50 sembolle sınırlı başlangıç; örneklemle kontrol | Denemede doğruluk < %80 |
| R3 | **Model kaynakta olmayan yorum uyduruyor.** | D | Y | Numaralı kaynaklar ve kodda atıf doğrulama (uydurma atıflar atılır ve sayılır); "bulunamadı" kuralı; sadakatin elle kontrolü; bulunamaz testi | Sadakat kontrolünde ihlal görülmesi |
| R4 | **Token kullanımı beklenenden yüksek.** Düşünme tokenları, Türkçe tokenizasyon. Ücretsiz dönemde günlük kota (15 milyon token), sonrasında maliyet. | O | O | Disk önbelleği; her sorguda token logu; toplu işlerde kota takibi | Bir günlük toplu iş kotanın yarısını aşar |
| R5 | **Kapsam büyür ve takvim kayar.** | Y | O | Aşamalar sabit; yeni fikirler "isteğe bağlı devam" listesine yazılır; Hafta 10 tampon | İki hafta üst üste görevlerin %50'sinden azının bitmesi |
| R6 | ~~Colab oturumu kopar ya da GPU verilmez.~~ **Kapandı (31 Ekim):** Colab kullanılmıyor. Uzun işlerin yarıda kalması için: sonuçlar madde madde diske ve önbelleğe yazılır, yeniden başlatınca kaldığı yerden devam eder. | D | D | — | — |
| R7 | **Lisans hatası.** Yanlışlıkla telifli bir metnin korpusa girmesi. | D | Y | `lisans` alanı zorunlu; kontrat testi; `KAYNAKLAR.md`; site kazıma yasağı | Lisansı belirsiz bir kaynak eklenmek istenmesi |
| R8 | **Etik açıdan sakıncalı çıktı.** Korkutucu ya da otoriter dil. | O | O | Yorum dili kuralları ([07](07-etik-ve-hukuk.md)); otomatik yasak ifade taraması; ağır içerik testi | Taramada ihlal görülmesi |
| R9 | **Motivasyon düşer.** | O | Y | Her hafta görünür bir çıktı; 5. haftada çalışan bir MVP; ölçüm tablosuyla ilerlemenin görünmesi | Bir hafta hiç commit olmaması |
| R10 | **zeyrek alfa aşamasında ve hata verebiliyor.** | O | D | Yalnızca ikinci kontrol katmanı; LLM zaten yalın biçim döndürüyor | Birim testlerinde hata |
| R11 | ~~Drive bağlantısı yavaş ya da SQLite ile sorunlu.~~ **Kapandı (31 Ekim):** Drive kullanılmıyor; Chroma doğrudan `data/index/chroma` altında. | — | — | — | — |
| R12 | ~~Geliştirme döngüsü yavaşlar (bilgisayarda yaz, Colab'de çalıştır).~~ **Kapandı (31 Ekim):** kod yazıldığı yerde gerçek veriyle çalışıyor. | — | — | — | — |
| R13 | **EVREN'in ücretsiz dönemi 1 Aralık 2026'da bitiyor**; sonraki fiyat belli değil. Takvimde bütün korpusun çevirisi Hafta 6'da (30 Kasım–6 Aralık). | Y | O | Bütün korpusun sembol ataması ve çevirisi Hafta 3 sonuna çekilir; yanıtlar disk önbelleğinde kalır, ücretsiz dönemden sonra yeniden ödenmez | 25 Kasım'da çevrilmemiş madde kalması |
| R14 | **EVREN servisi yavaş ya da kesintili.** 31 Ekim'de iki model "dolu"/zaman aşımı verdi; orkestra'da DeepSeek turları 2–5 dakika sürdü. | O | O | Yeniden deneme ve uzun zaman aşımı; `toplu` işler önbellek sayesinde kaldığı yerden devam eder; arayüzde bekleme mesajı | Rüya başına medyan süre > 60 sn |

## 3. Doğrulanması gereken bilgiler

Araştırmada **[DOĞRULANMADI]** olarak işaretlenen ve bu projeyi etkileyen bilgiler:

- [ ] OpenITI lisansı (Zenodo kaydında CC BY-NC-SA 4.0): Hafta 0'da elle kontrol et.
- [ ] Gerçek token sayıları ve rüya başına maliyet: Hafta 1'de ölç.
- [ ] Chroma'nın yerel sürümünde hibrit arama olup olmadığı: yalnızca Aşama 3'te gerekirse bakılacak.
- [ ] KVKK md. 28/1-a'nın metni: proje kişisel kaldığı sürece düşük öncelikli.
