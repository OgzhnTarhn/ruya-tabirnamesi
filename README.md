# Rüya Tabirnamesi · Çok Kaynaklı Türkçe RAG

Anlattığın rüyadaki sembolleri bulan, her sembol için klasik tabirnamelerin (Nablusi, İbn Sirin'e atfedilen *Muntahab*) ve Batı kaynaklarının (Miller, Freud) ne dediğini getiren, sonra bunları **kaynak göstererek ve çelişkileri gizlemeden** Türkçe bir yorumda birleştiren kişisel bir öğrenme projesi.

> **Durum:** Planlama ve mimari iskelet tamam (23 Ekim 2026). Veri sözleşmeleri, modül arayüzleri ve mimari testleri hazır; adımların gövdeleri takvimdeki haftalarda yazılacak.
> **Sonraki adım:** Hesaplar ve ilk push ([10](docs/10-kurulum-rehberi.md)), ardından Hafta 1'deki veri ve çeviri denemesi ([takvim](docs/08-yol-haritasi-takvim.md), [deney notu](docs/deneyler/01-veri-ve-ceviri.md)).

## Belgeler

| # | Belge | İçerik |
|---|---|---|
| 00 | [Proje vizyonu](docs/00-proje-vizyonu.md) | Ne, neden; hedefler, hedef olmayanlar, anti-hedefler |
| 01 | [Gereksinimler](docs/01-gereksinimler.md) | İşlevsel ve işlevsel olmayan gereksinimler, MVP kabul ölçütleri |
| 02 | [Veri kaynakları ve şema](docs/02-veri-kaynaklari-ve-semasi.md) | Seçilen kaynaklar, gerçek veride görülenler, veri hattı, şemalar, çeviri stratejisi |
| 03 | [Mimari](docs/03-mimari.md) | Boru hattı, bileşenler, klasör yapısı, hata yönetimi, test stratejisi |
| 04 | [Teknoloji seçimi](docs/04-teknoloji-secimi.md) | Her teknoloji kararı ve gerekçesi (TK-01 … TK-13) |
| 05 | [Yorum yöntemi](docs/05-yorum-yontemi.md) | Klasik tabirin beş katmanı ve sentez kuralları |
| 06 | [Değerlendirme](docs/06-degerlendirme.md) | Test seti, ölçütler, hedefler, deneyler |
| 07 | [Etik ve hukuk](docs/07-etik-ve-hukuk.md) | Veri ve telif kuralları, yorum dili, uyarı metni, KVKK |
| 08 | [Yol haritası ve takvim](docs/08-yol-haritasi-takvim.md) | 12 haftalık plan, kilometre taşları ([.ics](docs/takvim.ics)) |
| 09 | [Riskler ve açık sorular](docs/09-riskler-ve-acik-sorular.md) | Senin cevaplaman gereken sorular, risk kaydı |
| 10 | [Kurulum rehberi](docs/10-kurulum-rehberi.md) | API anahtarı, uv, kaynakları indirme |
| 11 | [Çalışma ortamı](docs/11-calisma-ortami.md) | Kod, çalıştırma ve veri bilgisayarda; veri `data/` altında, git'e girmez |
| 12 | [Kod yapısı ve sözleşmeler](docs/12-kod-yapisi-ve-sozlesmeler.md) | Katmanlar, modül imzaları, veri ürünleri, adlandırma, geliştirme döngüsü |
| — | [Kaynaklar](docs/KAYNAKLAR.md) | Künyeler, lisanslar, atıf metinleri |
| — | [Terimler](docs/terimler.md) | Çeviride kullanılan tabir terimleri |
| — | [Kurallar](docs/kurallar.md) | Okuma notların (şablon, Hafta 3) |
| — | [Ölçümler](docs/olcumler.md) · [Deneyler](docs/deneyler/) | Ölçüm özet tablosu, deney notları |
| — | [Araştırma](docs/arastirma/) | Kaynak araştırması: rapor ve 5 ayrıntılı not |

## Kısaca mimari

![Mimari: çevrimdışı veri hattı ve çevrimiçi sorgu boru hattı](docs/gorseller/mimari.gif)

```
Rüya metni
  → 1. Sembol çıkarımı   (DeepSeek · JSON şeması)
  → 2. Eşleme            (sembol indeksi + zeyrek · yoksa vektör yedeği)
  → 3. Getirme           (symbol_id · kaynak başına N madde · bağlam koşulları)
  → 4. Sentez            (DeepSeek · numaralı kaynaklar + kodda atıf doğrulama)
  → Kaynaklı, gelenek etiketli Türkçe yorum + uyarı
```

**Ortam:** Her şey bilgisayarda (VS Code + Git + uv) · veri `data/` altında, git'e girmez

**Teknolojiler:** Python ≥3.11 · EVREN LLM geçidi (`deepseek-v4.1-flash`, httpx) · Chroma · multilingual-e5-large · zeyrek · Gradio · pytest · ruff · nbstripout

## Repo düzeni

```
src/ruya/     paket: config, schemas, llm, ingest, enrich, index, pipeline, degerlendirme
notebooks/    ince notebook'lar: deneyler ve inceleme (VS Code, .venv çekirdeği)
prompts/      sürümlü sistem talimatları
sozluk/       elle onaylanan sembol sözlüğü (symbols.json)
app/ eval/ scripts/   giriş noktaları: Gradio arayüzü, değerlendirme, kaynak indirme
tests/        verisiz birim testleri, mimari testleri, kontrat testleri
```

## Bilgisayarda (verisiz) çalıştırma

```powershell
uv sync
uv run nbstripout --install
uv run pytest
uv run ruff check . ; uv run ruff format .
```

Kurulum ve çalıştırma: [10](docs/10-kurulum-rehberi.md), [11](docs/11-calisma-ortami.md).

## Lisans notu

Kod sana aittir. Veri `data/` klasöründe durur ve git'e eklenmez. OpenITI metinleri CC BY-NC-SA 4.0 lisanslıdır; Gutenberg metinleri kamu malıdır. Ayrıntılar: [07-etik-ve-hukuk.md](docs/07-etik-ve-hukuk.md), künyeler: [KAYNAKLAR.md](docs/KAYNAKLAR.md).
