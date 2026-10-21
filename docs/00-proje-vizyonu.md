# 00 · Proje Vizyonu

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026

## Tek cümlede

Kullanıcının anlattığı rüyadaki sembolleri bulan, her sembol için **birden çok klasik kaynağın** ne dediğini getiren ve bunları **kaynak göstererek, çelişkileri gizlemeden** Türkçe bir yorumda birleştiren, kişisel bir RAG (getirmeyle güçlendirilmiş üretim) projesi.

## Neden bu proje?

- **Öğrenmek için.** Asıl amaç RAG'ı uçtan uca öğrenmek: veri hazırlama, parçalama (chunking), embedding, arama, yeniden sıralama, kaynaklı üretim ve ölçme.
- **Sıradan olmaması için.** "PDF'e soru sor" kalıbından farklı. Kullanıcı soru sormuyor, bir anlatı yazıyor. Sistem bu anlatıdan sembolleri çıkarıp her biri için ayrı ayrı arama yapıyor. Kaynaklar dört dilde (Arapça, İngilizce, Almanca, Türkçe). Klasik tabir geleneğinin "koşullu yorum" mantığının da modellenmesi gerekiyor.
- **Alanda boşluk olduğu için.** Araştırmada Türkçe rüya metni ya da LLM ile rüya tabiri üzerine bir akademik çalışma bulunamadı (bkz. araştırma raporu).

## Ne yapacak? (kapsam)

1. Kullanıcı rüyasını serbest Türkçe metinle yazar. İsterse bağlam bilgisi de verir: cinsiyet, medeni hâl, mevsim, gurbette olup olmadığı.
2. Sistem rüyadaki sembolleri nitelikleriyle birlikte çıkarır. Örneğin "siyah, büyük yılan".
3. Her sembolü kanonik bir sembol kimliğine eşler. Örneğin `yilan`.
4. Her kaynaktan o sembolle ilgili maddeleri getirir: Nablusi, İbn Sirin'e atfedilen *Muntahab*, Miller, Freud vb.
5. Bir yorum yazar. Yorumda her cümlenin kaynağı gösterilir. Kaynakların uzlaştığı ve ayrıştığı noktalar ayrı ayrı belirtilir. Kullanıcının bağlamına uyan koşullu yorum öne çıkar. Kaynakta bulunmayan semboller için "kaynaklarda bulunamadı" denir.
6. Her yanıtın altında bir uyarı metni yer alır.

## Hedefler

| # | Hedef | Ölçüt |
|---|---|---|
| H1 | RAG'ın her katmanını kendi elimle kurmak | Framework'süz, düz Python ile çalışan bir boru hattı |
| H2 | Gerçeğe yakın, çok kaynaklı yorum | Test setindeki rüyalarda her sembol için ≥2 kaynaktan madde gelmesi (kaynakta varsa) |
| H3 | Uydurmama | Elle incelenen yanıtlarda kaynağa dayanmayan yorum cümlesi: 0 |
| H4 | Ölçerek ilerlemek | Her aşamada aynı test setiyle ölçülmüş sayılar (bkz. [06-degerlendirme.md](06-degerlendirme.md)) |
| H5 | Yasal veriyle çalışmak | Korpustaki her kaydın `lisans` alanı dolu; telifli içerik yok |

## Hedef olmayanlar

- Başkalarının kullanacağı, internete açık bir ürün. Proje kişisel ve yerel kalacak.
- Mobil uygulama ya da şık bir arayüz. Notebook içinde açılan bir Gradio arayüzü yeterli.
- Rüyadan psikolojik analiz ya da teşhis.
- Para kazanmak. Bu yüzden NC (ticari olmayan) lisanslı kaynaklar kullanılabiliyor.
- Bütün tabirname geleneğini kapsamak. Önce 50 sembolle başlanacak.

## Anti-hedefler (çalışsa bile başarısızlık sayılacaklar)

- Kehanet dili: "kesinlikle olacak", "Allah'ın mesajı".
- Otorite iddiası: "Diyanet'e göre anlamı".
- Kaynağı olmayan ya da yanlış kaynağa atfedilen yorum.
- Çelişen yorumları tek bir "doğru" yorumda eritmek.
- Ölüm, hastalık gibi korkutucu sembolleri sert ve doğrudan dille vermek.
- Telifli bir çeviriyi ya da kazınmış site içeriğini korpusa koymak.

## Başarı nasıl görünür?

Ocak 2027 ortasında şu senaryo çalışıyor olacak. Rüyamı yazarım ("Rüyamda denize girdim, sudan siyah bir yılan çıktı, korktum"). Yaklaşık 20 saniyede şöyle bir yanıt gelir:

- **Deniz:** Nablusi ne diyor, Miller ne diyor. Her cümlenin yanında kaynağı var.
- **Yılan:** Nablusi'ye göre düşman. Ancak "siyah yılan" için ayrı bir yorum var, o da öne çıkıyor. Miller'a göre ihanet. Uzlaşılan nokta: tehdit. Ayrışan noktalar ayrıca listeleniyor.
- **Korku:** Kaynakların korku duygusu hakkında ne dediği.
- **Altta:** Uyarı metni.

Bunun yanında elimde, her aşamada nasıl ilerlediğimi gösteren bir ölçüm tablosu olacak.

## Bağlantılı belgeler

- [01-gereksinimler.md](01-gereksinimler.md): ne yapması gerektiği
- [03-mimari.md](03-mimari.md): nasıl yapılacağı
- [08-yol-haritasi-takvim.md](08-yol-haritasi-takvim.md): ne zaman yapılacağı
