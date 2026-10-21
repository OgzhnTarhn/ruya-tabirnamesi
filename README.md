# Rüya Tabirnamesi · Çok Kaynaklı Türkçe RAG

Anlattığın rüyadaki sembolleri bulan, her sembol için klasik tabirnamelerin (Nablusi, İbn Sirin'e atfedilen *Muntahab*) ve Batı kaynaklarının (Miller, Freud) ne dediğini getiren, sonra bunları **kaynak göstererek ve çelişkileri gizlemeden** Türkçe bir yorumda birleştiren kişisel bir öğrenme projesi.

> **Durum:** Planlama tamamlandı, kodlama başlamadı (21 Ekim 2026).
> **Sonraki adım:** Hafta 1'deki veri ve çeviri denemesi (bkz. [takvim](docs/08-yol-haritasi-takvim.md)).

## Belgeler

| # | Belge | İçerik |
|---|---|---|
| 00 | [Proje vizyonu](docs/00-proje-vizyonu.md) | Ne, neden; hedefler, hedef olmayanlar, anti-hedefler |
| 01 | [Gereksinimler](docs/01-gereksinimler.md) | İşlevsel ve işlevsel olmayan gereksinimler, MVP kabul ölçütleri |
| 02 | [Veri kaynakları ve şema](docs/02-veri-kaynaklari-ve-semasi.md) | Seçilen kaynaklar, gerçek veride görülenler, veri hattı, şemalar, çeviri stratejisi |
| 03 | [Mimari](docs/03-mimari.md) | Boru hattı, bileşenler, klasör yapısı, hata yönetimi, test stratejisi |
| 04 | [Teknoloji seçimi](docs/04-teknoloji-secimi.md) | Her teknoloji kararı ve gerekçesi (TK-01 … TK-12) |
| 05 | [Yorum yöntemi](docs/05-yorum-yontemi.md) | Klasik tabirin beş katmanı ve sentez kuralları |
| 06 | [Değerlendirme](docs/06-degerlendirme.md) | Test seti, ölçütler, hedefler, deneyler |
| 07 | [Etik ve hukuk](docs/07-etik-ve-hukuk.md) | Veri ve telif kuralları, yorum dili, uyarı metni, KVKK |
| 08 | [Yol haritası ve takvim](docs/08-yol-haritasi-takvim.md) | 12 haftalık plan, kilometre taşları ([.ics](docs/takvim.ics)) |
| 09 | [Riskler ve açık sorular](docs/09-riskler-ve-acik-sorular.md) | Senin cevaplaman gereken sorular, risk kaydı |
| 10 | [Kurulum rehberi](docs/10-kurulum-rehberi.md) | Hesaplar, uv, `.env` |
| — | [Araştırma](docs/arastirma/) | Kaynak araştırması: rapor ve 5 ayrıntılı not |

## Kısaca mimari

```
Rüya metni
  → 1. Sembol çıkarımı   (Claude · JSON)
  → 2. Eşleme            (sembol indeksi + zeyrek · yoksa vektör yedeği)
  → 3. Getirme           (symbol_id · kaynak başına N madde · bağlam koşulları)
  → 4. Sentez            (Claude · search_result atıfları)
  → Kaynaklı, gelenek etiketli Türkçe yorum + uyarı
```

**Teknolojiler:** Python 3.12 · uv · Anthropic SDK · Chroma · multilingual-e5-large · zeyrek · Streamlit · pytest · ruff

## Lisans notu

Kod sana aittir. `data/` klasörü git'e eklenmez. OpenITI metinleri CC BY-NC-SA 4.0 lisanslıdır; Gutenberg metinleri kamu malıdır. Ayrıntılar: [07-etik-ve-hukuk.md](docs/07-etik-ve-hukuk.md).
