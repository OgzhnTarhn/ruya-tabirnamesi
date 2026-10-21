# Türk rüya tabiri siteleri, kazıma (scraping) hukuku ve rüya yorumlayan yapay zekâ için etik çerçeve

> Kapsam: Türkiye hukuku, Ekim 2026 itibarıyla. Bu not hukuki tavsiye değildir; aşağıdaki hukuki değerlendirmeler kaynaklı bulgular ile araştırmacının çıkarımlarını ayırır. Bu oturumda doğrudan metni okunan birincil kaynaklar: FSEK (mevzuat.gov.tr PDF), Diyanet Din İşleri Yüksek Kurulu fetvası, TDV İslâm Ansiklopedisi "RÜYA" ve "TÂBİRNÂME" maddeleri, ruyatabirleri.com / milliyet.com.tr / hurriyet.com.tr robots.txt dosyaları.

## (A) Türk rüya tabiri siteleri: ne yayımlıyorlar, kaynakları ne, robots.txt ve kullanım şartları ne diyor?

### Takeaway
Türkiye'de rüya tabiri içeriği iki tür yerde yayımlanıyor: bağımsız sözlük siteleri (ör. ruyatabirleri.com, ~7.900 madde, "Tüm hakları saklıdır") ve büyük gazetelerin "rüya tabirleri" bölümleri (Milliyet, Hürriyet, Vatan, Takvim vb.). İncelenen siteler belirli bir klasik kaynağa (Nablusî, İbn Sîrîn) açıkça atıf yapmıyor. Büyük gazeteler (Milliyet, Hürriyet) robots.txt dosyalarında yapay zekâ botlarını (GPTBot, ClaudeBot, anthropic-ai, PerplexityBot vb.) tüm siteden açıkça engelliyor. Bu, toplu kazımaya karşı açık bir "istemiyoruz" sinyali.

### Cited Findings
**ruyatabirleri.com**
- Site kendini Türkçe bir rüya tabiri sözlüğü olarak sunuyor ve 7.926 ayrıntılı yorum listelediğini söylüyor. Okur yorumları, "rüya ve bilinçaltı", "İslami rüya tabiri", "istihare" yazıları ve burç bölümü de var. — [ruyatabirleri.com ana sayfa](https://www.ruyatabirleri.com/)
- Kaynak gösterilmiyor. Nablusî, İbn Sîrîn ya da Diyanet adı geçmiyor. İslami yorumların "İslam alimleri" tarafından yapıldığı söyleniyor ama isim verilmiyor. — [ruyatabirleri.com](https://www.ruyatabirleri.com/)
- Altbilgide "© RuyaTabirleri.com · Tüm hakları saklıdır." yazıyor. Görünür bir "kullanım koşulları" bağlantısı yok. Gizlilik Politikası, çerez aydınlatma metni ve açık rıza metni bağlantıları var. Yorumların niteliğine ya da sınırlarına dair bir uyarı (disclaimer) görülmüyor; site "en doğru cevapları" sunduğunu iddia ediyor. — [ruyatabirleri.com](https://www.ruyatabirleri.com/)
- robots.txt dosyası `User-agent: * / Allow: /` diyor ve sitemap gösteriyor (sitemap_index.xml). Hiçbir bot kısıtlanmamış. — [ruyatabirleri.com/robots.txt](https://www.ruyatabirleri.com/robots.txt)

**Milliyet**
- Sembollere göre alfabetik bir rüya tabirleri bölümü var. — [Milliyet rüya haberleri](https://www.milliyet.com.tr/haberleri/ruya)
- robots.txt şu botları tüm siteden (`Disallow: /`) engelliyor: anthropic-ai, ChatGPT-User, ClaudeBot, Claude-Web, cohere-ai, GPTBot, OAI-SearchBot, quillbot.com, PerplexityBot, TurnitinBot. Genel botlar için yalnızca /root/*, /arama/ ve /Milliyet.aspx kapalı. CCBot ve Google-Extended için ayrı kural yok. — [milliyet.com.tr/robots.txt](https://www.milliyet.com.tr/robots.txt)

**Hürriyet**
- Rüya içerikli haber ve derlemeler yayımlıyor (ör. "rüyada uçmak ne anlama gelir"). — [Hürriyet](https://www.hurriyet.com.tr/haberleri/ruyada-ucmak-ne-anlama-gelir)
- robots.txt aynı 10 yapay zekâ / intihal botunu tüm siteden engelliyor. Genel botlar için /api/, /arama/, /widgets/ vb. dizinler kapalı. — [hurriyet.com.tr/robots.txt](https://www.hurriyet.com.tr/robots.txt)

**Diğer medya**
- Gazete Vatan rüya tabirleri sözlüğünü "İslami kaynaklardan oluşturulan" açıklamalara dayanan bir dijital sözlük olarak tanıtıyor. Hangi kaynaklar olduğunu belirtmiyor. — [Gazete Vatan](https://www.gazetevatan.com/astroloji/ruya-tabirleri-sozlugu-ile-en-guncel-ruya-yorumlari-991420)
- Takvim ve Haber Gazetesi gibi siteler "Diyanet'e göre rüyada X görmek" başlıklı içerikler üretiyor. Takvim, Diyanet'in rüyanın mahiyetine dair bir yazısını özetliyor. — [Takvim](https://www.takvim.com.tr/galeri/ruya-tabirleri/ruya-tabirlerinin-dinimizdeki-yeri-nedir-islamiyete-gore-ruyanin-ortaya-cikis-sebebi-nedir-ruya-cesitleri-neler); [Haber Gazetesi](https://www.habergazetesi.com.tr/ruyada-abi-ve-yenge-gormek-diyanete-gore-ne-anlama-gelir-ruyadaki-detaylar-yorumu-degistiriyor)
- Bir arama özetine göre Diyanet'in resmî kaynaklarında belirli bir rüyanın anlamını sabitleyen bir yorum bulunmuyor. Dolayısıyla "Diyanet'e göre rüyada X görmek" kalıbı, Diyanet'in yayımladığı bir tabirnameye dayanmıyor. — [Haber Gazetesi](https://www.habergazetesi.com.tr/ruyada-abi-ve-yenge-gormek-diyanete-gore-ne-anlama-gelir-ruyadaki-detaylar-yorumu-degistiriyor) (ikincil kaynak; Diyanet'in bir tabir sözlüğü yayımlamadığını [kurul.diyanet.gov.tr fetvası](https://kurul.diyanet.gov.tr/tr/fetva/uveysilik/0193c42d-b785-77ce-3e0a-e9ce6d2fa473) dolaylı olarak destekliyor, bkz. bölüm C)

**Klasik kaynaklar (içeriğin muhtemel kökeni)**
- TDV İslâm Ansiklopedisi'ne göre "tâbirnâme" rüya tabiri eserlerinin genel adı. İbn Sîrîn'e nispet edilen *Kitâbü'l-Cevâmi'* en bilinenlerden. Abdülganî en-Nablusî'nin *Ta'tîrü'l-enâm fî ta'bîri'l-menâm* adlı eseri 1684'te alfabetik düzenle yazılmış. Türkçe tâbirnâmelerin çoğu Arapçadan (bir kısmı Farsça üzerinden) çeviri ve çoğunun tasavvufî karakteri var. Maddenin yazarları Orhan Şaik Gökyay ve Vildan S. Coşkun. — [TDV İA "TÂBİRNÂME"](https://islamansiklopedisi.org.tr/tabirname)
- Tâbirnâmelerin çoğu iki bölümlü: önce İslam'da rüyaya dair bir giriş, sonra sembollerin anlamları. — [TDV İA "TÂBİRNÂME"](https://islamansiklopedisi.org.tr/tabirname)
- TDV İA "RÜYA" maddesi tabir alanında İbn Sîrîn, Kirmânî, Nablusî ve Seyyid Süleyman el-Hüseynî'yi önemli isimler olarak anıyor. — [TDV İA "RÜYA"](https://islamansiklopedisi.org.tr/ruya)
- Türk kütüphanelerinde çok sayıda yazma ve basma tâbirnâme bulunuyor. Akademik edisyonlar da var (ör. Uludağ Üniv. "Tüş tabirnamesi", Artuklu Üniv. "Terceme-i Tuhfetü'l-Mülûk"). — [Uludağ Açık Erişim](https://acikerisim.uludag.edu.tr/entities/publication/f773e044-b5be-4a05-b997-3771b5818378); [Artuklu GCRIS](https://gcris.artuklu.edu.tr/entities/publication/3fbaf778-0595-4b6d-941f-d0b2dd3a4644)

### Inferences
- Bağımsız sitelerde ve gazete bölümlerinde benzer kalıp ifadeler sık görülüyor. Bu metinlerin ortak bir kökene (Nablusî / İbn Sîrîn'e nispet edilen Türkçe çevirilerin modern sadeleştirmeleri) ya da birbirinden kopyaya dayandığı kuvvetle muhtemel. Ancak bu oturumda metin karşılaştırması yapılmadı; bu bir hipotez, kanıtlanmış değil.
- Altta yatan klasik eser kamu malı olsa bile (bkz. B), modern Türkçe çeviri / sadeleştirme ve sitenin kendi yazdığı metinler ayrı koruma konusu olabilir. "Bu zaten Nablusî'den" savunması, sitedeki metni kopyalamayı otomatik olarak meşrulaştırmaz.
- Milliyet ve Hürriyet'in yapay zekâ botlarını açıkça engellemesi, bu yayıncıların içeriğinin yapay zekâ için toplanmasına rıza göstermediğini açıkça ortaya koyuyor. Kişisel bir betik (script) bu bot adlarını kullanmasa bile, niyete saygı açısından bu içeriklerin toplu kazınmaması gerekir.

### Gaps
- Sitelerin popülerlik sıralaması (Similarweb vb.) bulunamadı. "En popüler" iddiası doğrulanmadı.
- ruyanizitabiredin, Onedio, Mynet, Sabah ve islamveihsan.com'un robots.txt ve kullanım şartları bu oturumda kontrol edilmedi.
- Hürriyet ve Milliyet'in "kullanım koşulları" metinleri okunmadı. Kazıma veya otomatik erişim yasağı içerip içermedikleri doğrulanmadı.
- Siteler arası metin benzerliğine ya da rüya tabiri içeriği üzerine bir telif uyuşmazlığına (dava, DMCA vb.) dair kaynak bulunamadı.
- Hangi modern Türkçe Nablusî/İbn Sîrîn çevirisinin (yayınevi, mütercim) kaynak alındığı tespit edilemedi.

## (B) Türk hukuku: FSEK, veri tabanı hakkı, alıntı ve şahsi kullanım istisnaları, TCK 243-244, KVKK, mahkeme kararları

### Takeaway
Türkiye'de web kazımaya özgü bir düzenleme yok. Risk, mevcut kurallardan doğuyor: FSEK'teki eser niteliğindeki veri tabanı koruması (md. 6/1-11), yatırımı koruyan sui generis veri tabanı yapımcısı hakkı (Ek md. 8, 15 yıl), çeviri/işlenme koruması (md. 6), sözleşme ve kullanım şartları ve izinsiz sisteme girme (TCK 243). Kâr amacı gütmeyen ve paylaşılmayan kişisel kullanım için FSEK md. 38 dar bir kapı açıyor. Bir sitenin içeriğini toplu kopyalayıp yayımlamak ise en riskli senaryo.

### Cited Findings
**FSEK (5846 sayılı Fikir ve Sanat Eserleri Kanunu)** — metin: [mevzuat.gov.tr FSEK PDF](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Md. 6, işlenmeler:** "Tercümeler" işlenme eser sayılıyor. İşleyenin hususiyetini taşıyan işlenmeler, kullanılan eserin sahibinin haklarına zarar vermemek şartıyla eser olarak korunuyor. Klasik bir tâbirnâmenin modern Türkçe çevirisi bu yüzden ayrıca korunabilir. — [FSEK md. 6](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Md. 6/1-11, eser niteliğindeki veri tabanı:** "Belli bir maksada göre ve hususi bir plan dahilinde verilerin ve materyallerin seçilip derlenmesi sonucu ortaya çıkan" veri tabanları işlenme/derleme eser olarak korunuyor. Ancak bu koruma, veri tabanındaki veri ve materyalin kendisine genişletilemiyor. — [FSEK md. 6](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Ek md. 8, veri tabanı yapımcısının sui generis hakkı (Ek: 3/3/2004-5101/26):** İçeriğin oluşturulması, doğrulanması veya sunumu için "nitelik ve nicelik açısından esaslı bir nispet dahilinde yatırım yapan" yapımcının hakları şunlar: içeriğin önemli bir kısmının veya tamamının (a) herhangi bir araçla sürekli ya da geçici olarak başka bir ortama aktarılmasına ve (b) dağıtılmasına, satılmasına, kiralanmasına veya topluma iletilmesine izin verme ya da bunu yasaklama. Koruma aleniyet tarihinden itibaren 15 yıl sürüyor. Esaslı değişiklik ve yeni yatırım yeni bir koruma süresi doğuruyor. İhlalde md. 72/3 cezaları uygulanıyor. — [FSEK Ek md. 8](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Md. 35, iktibas (alıntı) serbestisi:** Alenileşmiş bir eserin "bazı cümle ve fıkralarının" bağımsız bir ilim veya edebiyat eserine alınması ve haklı gösterilecek bir oranda bir ilim eserine konulması serbest. Alıntının belli olacak şekilde yapılması ve kaynağın (eser, eser sahibi, alındığı yer) belirtilmesi gerekiyor. — [FSEK md. 35](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Md. 38, şahsi kullanım:** Bütün fikir ve sanat eserleri, "kâr amacı güdülmeksizin şahsen kullanmaya mahsus" olarak çoğaltılabilir. Ancak bu çoğaltma hak sahibinin meşru menfaatlerine haklı bir sebep olmadan zarar veremez ve eserden normal yararlanmaya aykırı olamaz (üç basamak testi). — [FSEK md. 38](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Md. 27, koruma süresi:** Eser sahibinin yaşadığı süre ve ölümünden itibaren 70 yıl. — [FSEK md. 27](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- **Md. 71, ceza hükümleri:** Kaynak göstermeden iktibas 6 aydan 2 yıla kadar hapis veya adli para cezası gerektiriyor. Başkasının eserine kendi adını koymak da 6 aydan 2 yıla kadar hapis veya adli para cezası gerektiriyor; dağıtma veya yayımlama halinde hapsin üst sınırı 5 yıl. — [FSEK md. 71](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)

**Web kazımaya özel Türk hukuku analizi**
- Av. Nihat Özbek (Güleryüz Partners, Mondaq, 14 Nisan 2023): Türkiye'de web kazımayı doğrudan düzenleyen bir kural yok. Web siteleri, şartları taşıyorlarsa md. 6/b-11 (eser veri tabanı) veya Ek md. 8 (sui generis) kapsamında kazımaya karşı korunabilir. Sözleşme/üyelik şartları da kazımayı sınırlayabilir. Yazar, "çeşitli Yargıtay kararlarının" web sitelerini FSEK kapsamında korunan veri tabanı sayma eğiliminde olduğunu söylüyor ama somut karar numarası vermiyor. — [Mondaq / Güleryüz](https://mondaq.com/turkey/copyright/1304746/web-scraping-and-protection-of-websites); Türkçe sürüm: [guleryuz.av.tr](https://guleryuz.av.tr/news-publications/detail/https-wwwguleryuzavtr-tr-news-publications-detail-web-kazima-web-scraping-ve-internet-sitelerine-yonelik-koruma)
- Aynı yazı karşılaştırmalı olarak şunları aktarıyor: ABD'deki hiQ v. LinkedIn davasında kamuya açık veriyi kazımanın CFAA'yı ihlal etmediği, ancak sahte profiller nedeniyle kullanıcı sözleşmesinin ihlal edildiği değerlendirildi. AB'deki Ryanair v. PR Aviation (ABAD) davasında telif ve sui generis koruma dışında kalan bir veri tabanı için bile sözleşmeyle kısıtlama yapılabileceği kabul edildi. — [Mondaq](https://mondaq.com/turkey/copyright/1304746/web-scraping-and-protection-of-websites)
- Lexpera'da Ek md. 8 kapsamındaki ihlal fiillerine ayrılmış bir kitap bölümü var (tam metin üyelere açık). — [Lexpera](https://www.lexpera.com.tr/literatur/kitaplar/xii-veri-tabani-yapimcisinin-haklarina-yonelik-fiiller-ek-md-8-iv-978-625-432-310-2)
- Başkasına ait haberlerin izinsiz kullanılmasına dair uyuşmazlıklarda görevli mahkeme, FSEK md. 76 uyarınca Fikri ve Sınai Haklar Hukuk Mahkemesi (Yargıtay kararı özeti). — [Karamercan Hukuk](https://karamercanhukuk.com/yargitay-karari/baskasina-ait-haberlerin-izinsiz-kullanilmasina-dair-uyusmazliklara-bakma-gorevi-fsek-76-hukmu-uyarinca-fikri-ve-sinai-haklar-hukuk-mahkemlelerine-aittir)

**TCK 243-244 (bilişim suçları)**
- TCK md. 243: bir bilişim sisteminin bütününe veya bir kısmına hukuka aykırı olarak girme ya da orada kalmaya devam etme suçu. Md. 244: sistemi engelleme, bozma, verileri yok etme veya değiştirme. — [TCK 5237, mevzuat.gov.tr](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5237.pdf) (Not: madde metni bu oturumda yeniden açılıp okunmadı; özet araştırmacının mevzuat bilgisine dayanıyor, doğrulanmalı.)

**KVKK (6698)**
- 7499 sayılı Kanun KVKK md. 6'yı değiştirdi (Resmî Gazete 12.03.2024, yürürlük 01.06.2024). Özel nitelikli veriler arasında din, mezhep veya diğer inançlar, felsefi inanç, sağlık ve cinsel hayat var ve liste sınırlı sayıda (numerus clausus). Değişiklikle sağlık ve cinsel hayat verilerine yönelik ayrı rejim kaldırıldı ve GDPR'a paralel yeni işleme şartları eklendi. Açık rıza hâlâ bir işleme şartı. — [Erdem & Erdem](https://www.erdem-erdem.av.tr/bilgi-bankasi/kisisel-verilerin-korunmasi-kanununda-neler-degisti); [Hukuki Haber](https://www.hukukihaber.net/kvk-kanununda-ozel-nitelikli-kisisel-verilerin-islenmesi-ve-yurt-disina-veri-aktarimi-kapsaminda-yapilan-degisikliklere-iliskin-degerlendirmeler)
- KVK Kurumu "Özel Nitelikli Kişisel Verilerin İşlenmesine İlişkin Rehber"i yayımladı. Kaynaklarda tarih çelişkili: bir kaynak Şubat 2025, diğeri Haziran 2025 diyor. — [Alomaliye](https://www.alomaliye.com/2025/03/03/ozel-nitelikli-kisisel-verilerin-islenmesine-iliskin-rehber/); [Hukuki Haber bilgi notu](https://www.hukukihaber.net/ozel-nitelikli-kisisel-verilerin-islenmesine-iliskin-rehber-hakkinda-bilgi-notu)
- KVKK md. 28/1-a: kişisel verilerin üçüncü kişilere verilmemek ve veri güvenliği yükümlülüklerine uyulmak kaydıyla, gerçek kişilerce yalnızca kendisi ya da aynı konutta yaşayan aile fertleriyle ilgili faaliyetler kapsamında işlenmesi Kanun kapsamı dışında. — [KVKK 6698, mevzuat.gov.tr](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.6698.pdf) (Not: madde metni bu oturumda yeniden açılmadı; doğrulanmalı.)

### Inferences
- **Klasik eserler:** Nablusî (ö. 1731) ve İbn Sîrîn'e nispet edilen Arapça asıl metinlerin FSEK md. 27'deki 70 yıllık süre dolduğundan kamu malı olması gerekir. Osmanlıca tercümeler de büyük ihtimalle öyle. Ancak 20. yüzyıl ve sonrasına ait modern Türkçe tercümeler ve sadeleştirmeler, mütercim ölümünden itibaren 70 yıl korunabilir (md. 6 + md. 27). RAG için en güvenli kaynak: kamu malı asıl metinler, telifsiz/açık lisanslı akademik edisyonlar ya da kullanıcının kendi yazdığı özetler.
- **Rüya tabiri siteleri ve Ek md. 8:** ~8.000 maddelik, alfabetik düzenlenmiş ve sürekli güncellenen bir sözlük sitesi, "esaslı yatırım" şartını muhtemelen karşılar. "Önemli bir kısmın" otomatik olarak başka bir ortama aktarılması (toplu kazıma) Ek md. 8/a kapsamına girebilir. Bu, kişisel kopya olsa bile böyle. Md. 38'deki şahsi kullanım istisnası kâr amacı yokluğu ve yayımlamama şartıyla bir savunma olabilir. Ancak Ek md. 8'in "bu Kanunda sayılan istisnalar" atfının md. 38'i ne ölçüde kapsadığı ve üç basamak testinin toplu kazımaya nasıl uygulanacağı belirsiz.
- **Kişisel öğrenme projesi ile yayımlama arasındaki fark:** Tamamen yerel, kâr amacı gütmeyen ve kimseyle paylaşılmayan bir öğrenme projesinde pratik risk düşük. Ancak kazınan veriyle uygulama yayımlamak, GitHub'a veri seti koymak ya da ticari kullanım riski belirgin biçimde artırır (Ek md. 8/b "topluma iletme", md. 71 kaynak göstermeden iktibas).
- **TCK 243:** Herkese açık sayfaları normal hızla okumak, yaygın görüşe göre "hukuka aykırı giriş" sayılmaz. Giriş/üyelik gerektiren alanlara girmek, CAPTCHA veya engelleri aşmak ya da sunucuyu zorlayacak hızda istek göndermek (TCK 244 / hizmet engelleme) ise riski artırır. Bu konuda Türkiye'de kazımaya özgü bir içtihat bulunamadı.
- **KVKK:** Rüyanın kendisi bir veri kategorisi değil. Ancak rüya anlatımları sıklıkla sağlık (hastalık, ölüm korkusu, depresyon), cinsel hayat ve din/inanç bilgisi açığa çıkarır. Uygulama başkalarının rüyalarını saklarsa bunlar özel nitelikli kişisel veri olarak ele alınmalı. Sadece geliştiricinin kendi rüyalarını yerel olarak işlediği kişisel bir proje md. 28/1-a istisnasına girer. Rüyaları yurt dışındaki bir LLM API'sine göndermek ise (başkalarının verisi söz konusuysa) yurt dışı aktarım (md. 9) sorunu da doğurur.

### Gaps
- Web kazıma, scraping ya da Ek md. 8'in bir web sitesine uygulanmasına ilişkin somut bir Yargıtay veya BAM karar numarası bulunamadı. Mondaq yazısı "çeşitli Yargıtay kararları" diyor ama künye vermiyor.
- TTK md. 54-55 (haksız rekabet; özellikle 55/1-c "başkasının iş ürünlerinden yetkisiz yararlanma") bu oturumda kaynakla doğrulanmadı. Ticari bir rakip ürün için ilgili olabilir.
- Ek md. 8'in md. 38 şahsi kullanım istisnasıyla ilişkisi konusunda doktrin görüşü bulunamadı.
- Yapay zekâ eğitimi veya RAG için metin ve veri madenciliği (TDM) istisnası: Türkiye'de AB DSM Direktifi md. 3-4 benzeri bir TDM istisnası bulunduğuna dair kaynak bulunamadı. 2026 itibarıyla FSEK'te böyle bir değişiklik yapıldığı doğrulanamadı.
- KVK Kurulu'nun yapay zekâ / sohbet botlarıyla ilgili rehberleri bu oturumda incelenmedi.

## (C) Etik ve sorumlu yapay zekâ çerçevesi: Diyanet'in tutumu, psikolojik bakış, riskler, uyarılar, diğer uygulamalar

### Takeaway
Diyanet Din İşleri Yüksek Kurulu'na göre peygamber dışındaki kişilerin rüyaları "delil değildir", bağlayıcı değildir ve "rüyalar ile amel edilmez". TDV İslâm Ansiklopedisi rüyayı kesin bilgi vasıtası saymıyor. Dolayısıyla bir uygulamanın dinî tabirleri "kesin hüküm" gibi sunması hem dinî hem etik açıdan sorunlu. Piyasadaki yapay zekâ rüya uygulamaları kendilerini genellikle "kişisel düşünme / eğlence amaçlı, profesyonel psikolojik veya tıbbi tavsiye yerine geçmez" diye çerçeveliyor. Ancak bazıları kaygı ve depresyonla başa çıkma gibi ruh sağlığı iddiaları da taşıyor.

### Cited Findings
**Diyanet ve İslami kaynaklar**
- Din İşleri Yüksek Kurulu fetvası (03.05.2018, "Üveysilik"): Peygamberler dışındaki insanların gördüğü rüyalar kesin bir hüküm ifade etmez ve bağlayıcılıkları yoktur. "Rüyalar delil değildir ve rüyalar ile amel edilmez." Rüyaya dinî veya dünyevi bir hüküm bağlanamaz. — [kurul.diyanet.gov.tr – Üveysilik](https://kurul.diyanet.gov.tr/tr/fetva/uveysilik/0193c42d-b785-77ce-3e0a-e9ce6d2fa473)
- Diyanet'in "Hadislerle İslam" eserine göre tabir ancak akıllı, ilim sahibi, ehil ve dininde müstakim kişilerce yapılabilir. Eser, uydurma tabirlerle insanların aldatıldığı konusunda uyarıyor ve görülmemiş bir rüyayı görmüş gibi anlatmanın büyük iftira olduğunu bildiren hadisi aktarıyor. — [Hadislerle İslam c.1 s.471](https://hadislerleislam.diyanet.gov.tr/sayfa.php?CILT=1&SAYFA=471); [s.465](https://hadislerleislam.diyanet.gov.tr/sayfa.php?CILT=1&SAYFA=465)
- Diyanet'in bir vaaz metnine göre rüyanın hem hatırlanmasında hem yorumlanmasında hata ihtimali yüksek olduğu için rüya, aklî ve naklî deliller gibi kesin ve bağlayıcı değildir. Rüyaların önemli bir kısmı iç zihinsel süreçlerin ürettiği öznel imgelerdir. (Eski tarihli bir taşra müftülüğü dokümanı.) — [Diyanet İzmir/Seferihisar vaaz PDF](https://webdosyasp.diyanet.gov.tr/muftuluk/UserFiles/izmir/Ilceler/seferihisar/UserFiles/Files/din%20istismar%C4%B1%20konusunda%20vaazlar_8cdce08f-65df-4ee9-8aed-1cc92abae0a6.pdf)
- Diyanet'in Yûsuf Suresi 4-6. ayet tefsiri sadık rüya ile nefisten kaynaklanan rüyayı ayırıyor. — [kuran.diyanet.gov.tr](https://kuran.diyanet.gov.tr/tefsir/Y%C3%BBsuf-suresi/1600/4-6-ayet-tefsiri)
- TDV İA "RÜYA" (İlyas Çelebi, Süleyman Uludağ, 2008): Dinî literatürde rüya rahmânî (sadık, sâlih), şeytanî (hulm) ve nefsânî olarak üçe ayrılıyor. Rüya kesin bilgi vasıtası değil; rüyada Peygamber'den talimat alındığı iddiası itibar görmüyor. Peygamber dışındakilerin rüyasıyla amel, şer'î hükümlere aykırı olmamasına bağlı. Rüya kişiye özgüdür ve genel hüküm ifade etmez. Hz. Peygamber güzel rüyaların anlatılıp tabir edilmesini hoş karşılar, kötü rüyaların anlatılmasını istemezdi. Tabircinin rüyanın kim tarafından, nerede, nasıl görüldüğünü bilmesi gerekir. — [TDV İA "RÜYA"](https://islamansiklopedisi.org.tr/ruya)
- Aynı madde modern bakışı da özetliyor: rüyalar çoğunlukla REM evresinde görülür. Freud rüyayı bilinçdışı arzuların sembolik görünümü, Jung simgelerin kişisel anlamı, Fromm "unutulmuş bir sembol dili" olarak ele alıyor. Freud'a itiraz eden psikologlar da var. — [TDV İA "RÜYA"](https://islamansiklopedisi.org.tr/ruya)
- Türkgün'deki bir haber, Diyanet ve alimlerin her rüyanın tabire uygun olmadığı, tabirin ciddi bilgi gerektirdiği ve rüyalarda kesin hüküm bulunmadığı konusunda birleştiğini aktarıyor (ikincil kaynak). — [Türkgün](https://www.turkgun.com/ruya-tabirleri/ruya-ile-amel-edilir-mi-uzmanlar-son-noktayi-koydu/340425)

**Diğer yapay zekâ rüya uygulamalarının çerçevelemesi**
- Revea'nın kullanım şartları (Mayıs 2026): yorumlar "kişisel düşünme ve eğlence amaçlıdır" ve profesyonel psikolojik, psikiyatrik veya tıbbi tavsiyenin yerine geçmez. — [Revea ToS](https://foil-throat-7ce.notion.site/Revea-Terms-of-Service-354fe80f681780ecb96ff09501ee9160)
- DreamCodex AI (App Store): uyku, kaygı veya ruh sağlığı sorunu yaşayanlara nitelikli bir profesyonelle konuşmalarını öneriyor. — [App Store DreamCodex AI](https://apps.apple.com/app/id6756968105)
- DreamApp (App Store) kaygı ve depresyonun üstesinden gelme gibi ruh sağlığı vaatleriyle tanıtılıyor ve terapist bağlantısı sunuyor. Dream Story AI da ruh sağlığını iyileştirme vaat ediyor. Bu tür vaatler, "eğlence amaçlı" uyarılarla çelişebilir. — [App Store DreamApp](https://apps.apple.com/app/id1524421486); [App Store Dream Story](https://apps.apple.com/us/app/-/id6448614629)
- Astro Dream sonuçların sorumluluğunu kullanıcıya yüklüyor (arama özeti; birincil sayfa açılmadı). — [Mergeek](https://www.mergeek.com/latest/yDOarnx8818nBj6Q)
- Üretken yapay zekâ ile rüya analizinin etik sorunlarını tartışan akademik bir makale var: "Dreaming with AI", *Poligrafi*. — [Poligrafi](https://ojs.zrs-kp.si/poligrafi/article/view/418)

### Inferences
- **Dinî temsil:** Diyanet'in "rüya delil değildir / amel edilmez" tutumu, uygulamanın dinî tabirleri "geleneksel bir yorum" olarak sunmasını gerektiriyor; "Allah'ın mesajı", "kesin işaret" ya da "Diyanet'e göre anlamı" gibi bir dil kullanılmamalı. Uygulama Diyanet'in tabir sözlüğü olmadığını bilmeli. "Diyanet'e göre rüyada X" ifadesi yanıltıcı olur.
- **Çoklu gelenek:** Yanıtlar etiketlenmeli. Örneğin "Klasik İslami tâbirnâme geleneği (Nablusî'ye nispet edilen)", "Psikolojik / Jungçu bakış" ve "Senin bağlamın". Her biri için kaynak gösterilmeli ve hiçbiri tek doğru gibi sunulmamalı.
- **Zarar riski:** Tâbirnâmelerde ölüm, hastalık, felaket ve ihanet gibi kehanet içerikli yorumlar bol. Kaygılı, yas tutan, travma sonrası kâbus gören veya obsesif eğilimli kullanıcılarda bu yorumlar zarar verebilir. Önerilen önlemler: kehanet dili kullanmamak; ölüm/hastalık sembollerinde yumuşatılmış ve geleneğin de "kötü rüya anlatılmaz, üzerinde durulmaz" adabını (TDV İA) hatırlatan yanıt vermek; tekrarlayan kâbus, intihar düşüncesi veya travma işaretlerinde profesyonel desteğe yönlendirmek (Türkiye'de 112 Acil); tıbbi veya psikolojik teşhis koymamak.
- **Önerilen uyarı metni (taslak):** "Bu uygulama bir öğrenme projesidir. Yorumlar klasik tâbirnâme geleneğinden ve genel psikolojik yaklaşımlardan derlenir; geleceği öngörmez, dinî hüküm (fetva) değildir ve tıbbi ya da psikolojik tavsiye yerine geçmez. Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu'na göre rüyalar bağlayıcı değildir ve rüyalarla amel edilmez. Sizi rahatsız eden, tekrarlayan rüyalar için bir uzmana başvurun."
- **Ruh sağlığı vaadi:** "Kaygıyı yener" gibi iddialar, uygulamayı tıbbi cihaz / sağlık iddiası alanına iter. Bir öğrenme projesi bu tür iddialardan kaçınmalı.

### Gaps
- Diyanet'in özellikle "rüya tabiri / tabirname kullanmak caiz mi" sorusuna yanıt veren ayrı bir fetvası bulunamadı. "Rüya-yı sadıka" hakkında doğrudan bir Kurul fetvası da bulunamadı. Mevcut çerçeve "Üveysilik" fetvasındaki genel hükme ve TDV İA'ya dayanıyor.
- Rüyaların öngörü gücü olmadığına dair hakemli psikoloji/uyku bilimi kaynakları bu oturumda toplanmadı (ör. Hall/Domhoff, aktivasyon-sentez, tehdit simülasyonu kuramı).
- Türk Psikologlar Derneği veya Türk sağlık otoritelerinin yapay zekâ / rüya uygulamaları hakkında bir açıklaması bulunamadı.
- Kâbus / travma (TSSB) kullanıcılarına yönelik klinik rehberler (ör. imagery rehearsal therapy) kaynakla doğrulanmadı.

## (D) Yeni başlayan biri için somut öneri: ne güvenli, ne riskli?

### Takeaway
En güvenli yol şu: RAG korpusunu kamu malı klasik metinlerden (Nablusî / İbn Sîrîn'e nispet edilen Arapça asıllar ya da eski Osmanlıca tercümeler), açık lisanslı akademik edisyonlardan ve kendi yazdığın özetlerden kurmak. Ticari sitelerin ve gazetelerin içeriğini toplu kazımamak; onları sadece elle, referans amaçlı ve kaynak göstererek kullanmak. Kullanıcı rüyalarını yerelde tutmak ve özel nitelikli veri gibi korumak.

### Cited Findings
- Kâr amacı gütmeyen şahsi kullanım için çoğaltma FSEK md. 38 ile serbest, ancak hak sahibinin meşru menfaatlerine zarar verilmemesi ve normal yararlanmaya aykırı olmaması şartıyla. — [FSEK md. 38](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- Bir veri tabanının "önemli bir kısmının" başka bir ortama aktarılması veya topluma iletilmesi, yapımcının iznine tabi (15 yıl). — [FSEK Ek md. 8](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- Alıntı ancak bazı cümlelerle sınırlı, belli olacak şekilde ve kaynak göstererek yapılabilir. Kaynaksız iktibas cezai yaptırıma tabi (md. 71/3). — [FSEK md. 35, 71](https://www.mevzuat.gov.tr/mevzuatmetin/1.3.5846.pdf)
- Milliyet ve Hürriyet yapay zekâ botlarını robots.txt'de tüm siteden engelliyor. ruyatabirleri.com tüm botlara izin veriyor ama "Tüm hakları saklıdır" diyor. — [Milliyet robots](https://www.milliyet.com.tr/robots.txt); [Hürriyet robots](https://www.hurriyet.com.tr/robots.txt); [ruyatabirleri robots](https://www.ruyatabirleri.com/robots.txt); [ruyatabirleri.com](https://www.ruyatabirleri.com/)
- Sözleşme ve kullanım şartları, telif veya sui generis koruması olmayan veriler için bile kazımayı sınırlayabilir (Ryanair v. PR Aviation). — [Mondaq](https://mondaq.com/turkey/copyright/1304746/web-scraping-and-protection-of-websites)
- Rüya içerikleri sağlık, cinsel hayat ve din bilgisi taşıyabilir. Bunlar KVKK md. 6'da özel nitelikli veri. — [Erdem & Erdem](https://www.erdem-erdem.av.tr/bilgi-bankasi/kisisel-verilerin-korunmasi-kanununda-neler-degisti)

### Inferences (araştırmacının önerisi; hukuki tavsiye değildir)
**Yeşil (güvenli sayılabilir)**
1. Korpus: kamu malı asıl metinler (ör. Nablusî'nin *Ta'tîrü'l-enâm*'ının Arapça metni, Osmanlıca tercümelerin transkripsiyonları), yazarından izinli veya açık lisanslı akademik edisyonlar ve kendi cümlelerinle yazdığın sembol özetleri. Her parçaya `kaynak`, `gelenek`, `lisans` meta verisi ekle.
2. Siteleri yalnızca "okuyup kendi cümlenle özetleme" amacıyla, elle ve az sayıda sayfa için kullan. Fikirler korunmaz, ifade korunur: "rüyada yılan görmek düşmana işaret eder" bilgisini kendi cümlenle ve klasik kaynağa atıfla yazmak, sitenin paragrafını kopyalamaktan çok farklıdır.
3. Kullanıcı rüyaları: yerelde (SQLite / dosya), şifreli; yalnızca kendi rüyalarınla test et; buluta veya yurt dışı API'ye göndereceksen bunun yalnızca senin verin olduğundan emin ol.
4. Her yanıtta gelenek etiketi, kaynak ve uyarı metni (bkz. C) göster. Kehanet ve teşhis dili kullanma.

**Sarı (dikkatli)**
5. Kişisel, yerel ve yayımlanmayan bir deneme için bir sitenin birkaç düzine sayfasını indirmek: robots.txt'ye uy, düşük hızla çek (ör. 1 istek / birkaç saniye), kimliğini belirten bir User-Agent kullan, giriş gerektiren alanlara girme. Bu veriyi asla paylaşma ya da yayımlama; deneme bitince sil. (Md. 38 savunması mümkün ama Ek md. 8 ile ilişkisi belirsiz.)
6. Modern Türkçe çeviri kitaplardan (yayınevi baskısı Nablusî/İbn Sîrîn) metin almak: bunlar md. 6 kapsamında çeviri eser olarak korunuyor olabilir. Yalnızca kısa alıntı ve kaynak göstererek kullan.

**Kırmızı (kaçın)**
7. Bir sözlük sitesinin tamamını veya "önemli bir kısmını" otomatik kazımak, özellikle de bunu bir uygulamada yayımlamak, GitHub/Hugging Face'e veri seti olarak koymak ya da ticari kullanmak (Ek md. 8, md. 71).
8. robots.txt'de yapay zekâ botlarını engelleyen gazete sitelerini (Milliyet, Hürriyet) kazımak. Bot adını değiştirerek ya da CAPTCHA, oran sınırı ve engelleri aşarak erişmek (kullanım şartları ve TCK 243/244 riski).
9. Başkalarının rüyalarını açık rıza ve aydınlatma olmadan toplamak ya da saklamak (KVKK md. 6), bunları reklam veya profilleme amacıyla kullanmak.
10. "Diyanet'e göre" ya da "kesin anlamı" gibi otorite iddiası taşıyan yanıtlar; ölüm ve hastalık kehaneti; psikolojik teşhis.

### Gaps
- Kamu malı Nablusî/İbn Sîrîn metinlerinin dijital, makinece okunabilir ve açık lisanslı Türkçe (veya Arapça) sürümlerinin nerede bulunduğu bu oturumda araştırılmadı (ör. Wikisource, Shamela, Archive.org, YÖK Açık Bilim tezleri). Bu, başka bir araştırmacının kapsamında olabilir.
- Belirli bir sitenin kullanım şartları kazımayı açıkça yasaklıyorsa, şartların "tıkla-kabul" (clickwrap) değil yalnızca "göz at" (browsewrap) olduğu durumlarda Türk hukukunda bağlayıcılığı konusunda kaynak bulunamadı.
