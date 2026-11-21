# 16 · Arayüz Yenileme Planı (21 Kasım 2026)

**Durum (21 Kasım):** U1–U6 bitti. Sunum `app/sunum.py`'de (saf, testli), yerleşim `app/gradio_app.py`'de, stil `app/stil.css`'te. Açık ve koyu temada, 375 px genişlikte ve gerçek bir rüyayla denendi. Ek olarak: model metnindeki `*eser adı*` italik gösterilir.

Amaç: sade, modern ve anlaşılır bir arayüz. Boru hattına dokunulmaz; değişiklik
`app/gradio_app.py`, onun testleri ve gerekirse küçük bir CSS dosyasıyla sınırlıdır.
Gradio sürümü 6.30; `share=True` yok, yalnız `127.0.0.1` (CLAUDE.md).

## 1. Şimdiki durumda gördüklerim

| # | Sorun | Yer |
|---|---|---|
| A1 | Varsayılan Gradio teması; başlık, form ve sonuç alt alta, görsel hiyerarşi yok | `arayuz_kur` |
| A2 | Seçeneklerde Türkçe karakter yok: `kadin`, `bekar`, `kis` kullanıcıya böyle görünüyor | Bağlam açılır listeleri |
| A3 | Uyarı metni iki kez görünüyor: yorumun sonunda ve sekmenin altında | `yorum_metni` + `gr.Markdown(UYARI_METNI)` |
| A4 | Yorum düz metin: sembol başlıkları, "Genel yorum:" öneki ve `[1] …` atıf satırları aynı yazı ağırlığında | `yorum_metni`, `_bolum_satirlari` |
| A5 | Atıf ayrıntısı ayrı bir açılır listeden seçiliyor; metindeki `[1]` ile bağlantısı yok | `atif_secimi` |
| A6 | "Hata ayıklama" sekmesi son kullanıcıya açık, ham JSON | `gr.Tab("Hata ayıklama")` |
| A7 | İlerleme yalnız metin ("Kaynaklar aranıyor…"); kaç adım kaldığı, ne kadar süreceği belli değil | `ara_metin` |
| A8 | Anlatım eksik: uygulamanın ne yaptığı, geleneklerin ne demek olduğu, bağlamın neyi değiştirdiği, "bulunamadı"nın anlamı, atıfın ne olduğu açıklanmıyor | başlık ve etiketler |
| A9 | Boş durum yok: ilk açılışta örnek rüya ya da kısa yönlendirme yok | — |
| A10 | Mobil ve koyu tema denenmedi | — |
| A11 | **Yanlış anlatım:** gelenek etiketi "boş: hepsi" diyor, ama boş seçimde psikanalitik (Freud) maddeleri dışarıda kalıyor | `gr.CheckboxGroup(label=…)`, [hibrit.py:112](../src/ruya/pipeline/hibrit.py) |

## 2. Hedef tasarım

**İlke:** tek sütun, ortalanmış (en çok ~760 px), bol boşluk, tek vurgu rengi (gece mavisi /
lacivert), sakin bir serif başlık + okunaklı sans gövde. Süs yok; yorum metni öne çıkar.

Sayfa akışı yukarıdan aşağı:

1. **Başlık şeridi:** "Rüya Tabirnamesi" + tek cümlelik alt başlık: *Rüyanızdaki sembolleri
   klasik tabirnamelerde arar, kaynak göstererek yorumlar.* Altında küçük bir "Nasıl çalışır?"
   akordeonu (3 adım: sembolleri bul → kaynaklarda ara → kaynağa dayanarak yorumla).
2. **Girdi kartı:** rüya kutusu (karakter sayacı, 3.000 sınırı), altında iki-üç "örnek rüya"
   düğmesi, "Fotoğraftan oku" ve "Bağlam" akordeonları kapalı, gelenek seçimi, büyük
   "Yorumla" düğmesi.
3. **İlerleme şeridi:** üç adımlı gösterge — *Semboller · Kaynaklar · Yorum* — tamamlanan
   adım işaretlenir; altında "Genellikle 2–4 dakika sürer, bölümler hazır oldukça görünür."
4. **Sonuç kartı:**
   - Bulunan semboller **rozet** olarak (olumsuzlanan sembol üstü çizili ya da soluk, "yorumlanmadı" notuyla).
   - **Genel yorum** ayrı, hafif zeminli bir kutuda.
   - Her sembol için bir bölüm: başlık (sembol adı), yorum paragrafı, altında kaynak
     listesi. Her kaynak bir akordeon: başlık = "Nablusi · Taʿṭīr al-Anām"; açılınca alıntı,
     Türkçe çeviri ve asıl metin. Açılır liste (A5) kalkar.
   - "Kaynaklarda bulunamayanlar" kısa bir not kutusu: *Bu semboller için kaynaklarda yeterince
     yakın bir madde bulunamadı; uydurmamak için yorumlanmadı.*
5. **Alt bilgi:** uyarı metni bir kez, küçük puntoda (A3).
6. **Geliştirici ayrıntıları:** sayfanın en altında kapalı bir akordeon; içeride şimdiki JSON
   + adım süreleri ve token tablosu. Sekme yapısı kalkar (A6).

## 3. Anlatım (metinler)

Bütün metinler tek yerde, modül başında sabitler olarak durur; testler bunları kontrol eder.

| Yer | Metin (taslak) |
|---|---|
| Gelenek seçimi | İslami klasik: İbn Sîrîn'e atfedilen eser, Nablusi · Batı halk: Miller · Psikanalitik: Freud. Boş bırakırsanız İslami klasik ve Batı halk kaynaklarında aranır; Freud yalnız seçilirse girer. |
| Bağlam | Klasik tabirnameler bazı sembolleri kişiye göre farklı yorumlar (ör. evli/bekâr). Doldurmak zorunlu değil; bilgiler saklanmaz. |
| Bağlam seçenekleri | Kadın, Erkek · Evli, Bekâr · İlkbahar, Yaz, Sonbahar, Kış · Evet, Hayır (değerler şemadaki gibi kalır, yalnız etiket değişir) |
| Fotoğraf | Defterinizdeki rüyanın fotoğrafını yükleyin; metin okunup kutuya yazılır. Fotoğraf yalnız okuma servisine gönderilir, saklanmaz. |
| Rüya kutusu | Rüyanızı kendi cümlelerinizle, gördüğünüz sırayla anlatın. "Görmedim", "yoktu" gibi olumsuzlar da anlaşılır. |
| Atıf | Her yorum bir kaynak maddesine dayanır; kaynağa tıklayınca maddenin aslını ve çevirisini görürsünüz. |
| Hata mesajları | Şimdiki `HATA_MESAJLARI` kalır, uyarı kutusu biçiminde gösterilir. |

Kaynak/kişi adları `docs/02` ve `KAYNAKLAR.md` ile karşılaştırılarak yazılır (yanlış eser adı
yazılmaz).

## 4. Uygulama adımları

| # | İş | Yapan | Çıktı |
|---|---|---|---|
| U1 | Metin sabitleri, Türkçe seçenek etiketleri, gelenek açıklamasının düzeltilmesi (A2, A8, A11) | orkestra | `gradio_app.py`, testler |
| U2 | Yorumun HTML/Markdown işlenişi: sembol rozetleri, genel yorum kutusu, sembol bölümleri, kaynak akordeonları (`<details>`), uyarı bir kez (A3, A4, A5) | orkestra | `yorum_html(kayit)` saf işlevi + testleri |
| U3 | İlerleme şeridi: `ara_metin` yerine adım durumunu da döndüren saf işlev (A7) | orkestra | `ilerleme_html(asama, kayit)` + testler |
| U4 | Yerleşim, tema ve CSS: tek sütun, tema rengi, font, koyu tema, mobil (A1, A10) | orkestra | `app/stil.css` ya da `gr.themes` ayarı |
| U5 | Örnek rüya düğmeleri, "Nasıl çalışır?" akordeonu, geliştirici ayrıntıları akordeonu (A6, A9) | orkestra | `arayuz_kur` |
| U6 | Doğrulama: `uv run pytest`, `ruff`; arayüzü yerelde açıp masaüstü ve 375 px genişlikte, açık ve koyu temada ekran görüntüsü; bir gerçek rüyayla uçtan uca deneme | Claude | ekran görüntüleri `docs/gorseller/` |
| U7 | README'ye yeni ekran görüntüsü, [14](14-ders-notu.md)'e kısa not | Claude | belge commit'i |

Saf işlevler sunucu açmadan test edilir (şimdiki `test_gradio_app.py` düzeni). Ağır paket
`gradio` yine yalnız işlev içinde içe aktarılır (`tests/test_mimari.py`).

## 5. Kapsam dışı

- Gradio dışında bir ön yüz (React vb.); proje yerel ve kişisel kalıyor.
- Boru hattında, talimatlarda ya da şemada değişiklik.
- Sorgu geçmişi, hesap, paylaşım bağlantısı.

## 6. Bitti sayılma ölçütü

- A1–A10'un hepsi kapanmış, ekran görüntüleriyle gösterilmiş.
- Uyarı metni tam bir kez görünüyor; her yorum bölümünün kaynağı açılabiliyor.
- Testler ve ruff temiz; bir gerçek rüya hatasız yorumlanmış.
