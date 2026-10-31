# 07 · Etik ve Hukuk Kuralları

> Durum: Taslak v0.1 · Tarih: 21 Ekim 2026
> Bu belge hukuki görüş değildir. Ayrıntılar ve kaynaklar araştırma raporunda: `docs/arastirma/`.

## 1. Veri ve telif kuralları

| # | Kural | Neden |
|---|---|---|
| V1 | Korpusa yalnızca kamu malı ya da açık lisanslı metin girer. Her kaydın `lisans` alanı dolu olmak zorunda. | FSEK md. 6 ve 27: çeviriler ayrı eser sayılır, koruma süresi çevirmenin ölümünden sonra 70 yıl |
| V2 | Türkçe Nablusi ve İbn Sirin çevirileri, Jung'un eserleri, Freud'un modern Türkçe çevirileri ve rüya siteleri korpusa **girmez**. | Telif ve veri tabanı hakkı (FSEK Ek md. 8) |
| V3 | Rüya siteleri kazınmaz. Yalnızca elle okunur, öğrenilenler kendi cümlelerinle ve klasik kaynağa atıfla yazılır. | Veri tabanı hakkı, robots.txt ve kullanım şartları. Milliyet ve Hürriyet yapay zekâ botlarını açıkça engelliyor. |
| V4 | Akademik makaleler (TDV, Balaban, Elbir & Uludüz) yalnızca **kural tasarımı** için okunur. Metinleri korpusa kopyalanmaz. | Telif |
| V5 | Gutenberg metinlerinin başlık ve dipnot bölümleri silinir. Metadataya `kaynak: Project Gutenberg #926` yazılır. | Gutenberg lisansı |
| V6 | OpenITI'den türetilen çeviriler paylaşılırsa aynı lisansla (CC BY-NC-SA 4.0) ve atıfla paylaşılır. | ShareAlike koşulu |
| V7 | Veri yalnızca senin bilgisayarında, repodaki `data/` klasöründe durur ve git'e eklenmez. Repo herkese açık olsa bile veri dağıtılmamış olur. | NC ve SA koşulları, rüya gizliliği |
| V8 | Proje ticarileşirse önce NC lisanslı bütün kayıtlar çıkarılır: `lisans` alanına göre tek bir filtre. | NC koşulu |
| V9 | `docs/KAYNAKLAR.md` dosyasında her kaynağın tam künyesi ve lisansı tutulur. | Atıf yükümlülüğü (CC BY) |

## 2. Yorum dili kuralları

Bu kurallar sentez talimatına yazılır ve değerlendirmede otomatik olarak taranır (bkz. [06-degerlendirme.md](06-degerlendirme.md)).

| # | Kural | Yasak ya da sakıncalı örnek | Doğru örnek |
|---|---|---|---|
| D1 | Kehanet dili yok | "Yakında zengin olacaksın." | "Gelenekte bu sembol bolluk olarak yorumlanır." |
| D2 | Dinî otorite iddiası yok | "Diyanet'e göre anlamı…", "Allah sana şunu söylüyor" | "Nablusi'nin tabirnamesine göre…" |
| D3 | Teşhis yok | "Bu rüya depresyonda olduğunu gösteriyor." | "Psikanalitik bir bakışla Freud bu tür rüyaları … olarak ele alır." |
| D4 | Korkutucu sembollerde yumuşak dil | "Bu rüya ölüm habercisi." | "Gelenek, kötü rüyaların anlatılmamasını ve üzerinde durulmamasını öğütler. Bazı tabirciler ölümü zıddıyla, uzun ömür olarak yorumlamıştır [kaynak]." |
| D5 | Kaynaksız yorum yok | Atıfsız cümle | Her yorum cümlesinde atıf |
| D6 | İbn Sirin atfında dürüstlük | "İbn Sirin'e göre…" | "İbn Sirin'e atfedilen *Muntahab*'a göre (nispeti tartışmalı)…" |

**Dayanak:** Diyanet Din İşleri Yüksek Kurulu'nun 2018 tarihli fetvası, peygamberler dışındakilerin rüyalarının bağlayıcı olmadığını söylüyor: "rüyalar delil değildir ve rüyalar ile amel edilmez".

## 3. Güvenlik ağı

- **Tekrarlayan kâbus ya da travma:** Rüyada şiddet, kendine zarar verme ya da intihar teması varsa veya kullanıcı tekrarlayan kâbuslardan söz ediyorsa yanıtın başına şu not eklenir: "Sizi rahatsız eden ve tekrarlayan rüyalar için bir ruh sağlığı uzmanıyla konuşmak iyi gelebilir. Acil bir durumda 112'yi arayın."
- **Algılama:** Bu durum sembol çıkarımı adımında `hassas_icerik: true` bayrağıyla algılanır.

## 4. Uyarı metni (her yanıtın altında)

> *Bu uygulama kişisel bir öğrenme projesidir. Yorumlar klasik tabirname geleneğinden ve tarihsel kaynaklardan derlenir. Geleceği öngörmez, dinî hüküm değildir ve tıbbi ya da psikolojik tavsiye yerine geçmez. Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu'na göre rüyalar bağlayıcı değildir. Sizi rahatsız eden, tekrarlayan rüyalar için bir uzmana başvurun.*

## 5. Kişisel veri (KVKK)

- **Neden önemli:** Rüyalar sağlık, din ve cinsel hayat gibi **özel nitelikli** bilgiler içerebilir (KVKK md. 6).
- **Bugünkü durum:** Yalnızca kendi rüyalarını yerelde işliyorsun. Bu kişisel kullanım istisnasına giriyor (KVKK md. 28/1-a; madde metni doğrulanacak). Ancak rüya metni çıkarım ve sentez için EVREN LLM geçidine (`evren-llmapi.ssyz.org.tr`), yani üçüncü bir tarafın sunucularına gidiyor; verinin orada nasıl saklandığı doğrulanmadı. Kendi rüyan için bu senin tercihin.
- **Yerel veri notu:** Rüya geçmişi ve loglar yalnızca senin bilgisayarında, `data/` altında durur. `data/` klasörünü bir bulut senkronizasyon klasörüne (OneDrive vb.) taşırsan bu verinin de oraya gideceğini unutma.
- **Kurallar:**
  - Varsayılan olarak rüya metni loglanmaz.
  - Rüya içeren LLM istekleri ve yanıtları varsayılan olarak disk önbelleğine yazılmaz (`RUYA_SORGU_ONBELLEGI`, bkz. [03](03-mimari.md), bölüm 5.2). Değerlendirme yalnızca repodaki test seti için bu önbelleği açar.
  - Notebook çıktıları commit'ten önce `nbstripout` ile temizlenir. Böylece rüya metni GitHub'a gitmez.
  - Rüya geçmişi isteğe bağlıdır.
  - Test setine başkalarının rüyaları **izinsiz** konmaz.
- **Uygulamayı başkalarına açarsan:** Açık rıza, aydınlatma metni ve yurt dışı aktarım (md. 9) yükümlülükleri doğar. Bu kapsam dışı. Gündeme gelirse bu belge yeniden yazılır.
