# Sistem talimatları

LLM'e verilen sabit talimatlar burada, sürümlü olarak durur. Kod bunları
`ruya.llm.talimatlar.talimat_oku("<ad>")` ile okur.

## Kurallar

- Ad biçimi: `<is>_v<n>.md` (ör. `sentez_v1.md`).
- Bir ölçüm raporunda kullanılmış sürüm **bir daha değiştirilmez**. Değişiklik yeni bir
  sürüm dosyasıyla yapılır ve kodda `TALIMAT` sabiti güncellenir. Böylece her ölçüm,
  hangi talimatla yapıldığıyla birlikte tekrarlanabilir kalır.
- Talimat değişince değerlendirme yeniden çalıştırılır (docs/06).
- Talimatlara kendi rüyalarını örnek olarak koyma; repo herkese açılırsa sızar.
- Talimatın içine tarih, saat gibi değişen bilgi yazılmaz: prompt önbelleğini bozar.

## Planlanan talimatlar

| Dosya | Kullanan modül | Hafta | Dayanak |
|---|---|---|---|
| `ceviri_v1.md` | `enrich/translate.py` | 3 | docs/02 bölüm 5, docs/terimler.md |
| `sembol_atama_v1.md` | `enrich/assign_symbols.py` | 3 | docs/02 bölüm 2 |
| `cikarim_v1.md` | `pipeline/extract.py` | 4 | docs/03 Adım 1, İG-10–14 |
| `sentez_v1.md` | `pipeline/synthesize.py` | 5 | docs/05 bölüm 3, docs/07 |
| `kosul_v1.md` | `enrich/conditions.py` | 8 | docs/05 Katman 3–4 |
| `sentez_v2.md` | `pipeline/synthesize.py` | 11 | uzlaşı/ayrışma çıktısı |
