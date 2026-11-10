# D4 · Sentezde deepseek-v4.1-flash ile mimo-v2.6-pro

> Tarih: 10 Kasım 2026 · Hafta: 12 · Betik: `eval/run_eval.py --sentez-modeli d4` · Commit: `f76e744`

## Soru

EVREN'deki başka bir sohbet modeli sentezde daha iyi ya da daha hızlı mı?

## Hipotez

Daha büyük model (`mimo-v2.6-pro`) atıf kurallarına en az aynı ölçüde uyar ama daha yavaştır.

## Yöntem

- Veri: [alt küme](../../eval/dataset/alt_kume_15.txt), 15 sentetik rüya; çıkarım ve getirme
  önbellekten, iki koşulda da aynı.
- Değişen: yalnız sentez modeli (`config.MODEL_SENTEZ_D4`) · Sabit: `cikarim_v4`, hibrit
  getirme, N=1, `sentez_sembol_v2` + `genel_yorum_v1`.
- 429 ile düşen 4 rüya tek başına yeniden koşuldu; 15/15.
- Maliyet: 0 $ (EVREN ücretsiz dönem).

## Sonuç

| Sentez modeli | Atıf kapsamı | Yasak ifade | Medyan süre | Ort. süre | Rüya başına token |
|---|---|---|---|---|---|
| deepseek-v4.1-flash | %99,5 | 0 | 160 sn | 158 sn | ~11.900 (45 rüya ortalaması) |
| mimo-v2.6-pro | %100 | 0 | 214 sn | 213 sn | 15.412 |

Gözlemler:

- İki model de kodun atıf denetiminden geçiyor; ölçülen kalite ölçütlerinde fark yok.
- mimo rüya başına ~55 sn daha yavaş ve ~%30 daha çok token harcıyor.
- Yorumların dili ve sadakati elle karşılaştırılmadı (3 Kasım'daki eski boru hattı
  denemesinde de fark görülmemişti).

## Karar

- **Sentez `deepseek-v4.1-flash`'ta kalır.** Ölçülen kalite aynı; deepseek daha hızlı ve daha az token harcıyor.
- `MODEL_SENTEZ_D4` deney için `config.py`'de kalır; boru hattı kullanmaz.
- Hangi belge güncellendi: [olcumler](../olcumler.md), [15](../15-kalan-isler-plani.md).
