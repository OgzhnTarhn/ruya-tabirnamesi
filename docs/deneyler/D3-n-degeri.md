# D3 · Kaynak başına N = 1, 2, 3

> Tarih: 10 Kasım 2026 · Hafta: 12 · Betik: `eval/run_eval.py --alt-kume … --n` · Commit: `f76e744`

## Soru

Sentezde her kaynaktan birden fazla madde vermek yorumu zenginleştirmeye değer mi?

## Hipotez

N büyüdükçe sentez tokenı ve süresi artar. Atıf kapsamı ve kaynak çeşitliliği değişmez,
çünkü `sentez_sembol_v2` sembol başına en çok 3 kaynak kullanır ve N=1 bile 4 kaynağa
kadar madde getirir.

## Yöntem

- Veri: [alt küme](../../eval/dataset/alt_kume_15.txt), 15 sentetik rüya. Çıkarım sorgu
  önbelleğinden geldi; bütün koşullarda semboller ve eşlemeler aynı.
- Değişen: `kaynak_basina_n` (1, 2, 3) · Sabit: `cikarim_v4`, paralel sentez
  (`sentez_sembol_v2` + `genel_yorum_v1`), `deepseek-v4.1-flash`, hibrit getirme.
- N=1 değerleri 10 Kasım temel ölçümünün bu 15 rüyalık kısmı.
- 429 ile düşen rüyalar tek başına yeniden koşuldu; her koşulda 15/15.
- Maliyet: 0 $ (EVREN ücretsiz dönem).

## Sonuç

| N | Atıf kapsamı | Kaynak çeşitliliği | Medyan süre | Ort. süre | Rüya başına token |
|---|---|---|---|---|---|
| 1 | %99,5 | 2,8 | 160 sn | 158 sn | ~11.900 (45 rüya ortalaması) |
| 2 | %99,5 | 2,8 | 158 sn | 163 sn | 18.431 |
| 3 | %100 | 2,8 | 250 sn | 230 sn | 23.956 |

Gözlemler:

- N=2 süreyi değiştirmedi: paralel sentezde sembol çağrıları aynı anda gidiyor, girdi
  uzaması süreye az yansıyor. N=3'te çıktı da uzadı ve süre %56 arttı.
- Kaynak çeşitliliği ölçütü N'e duyarlı değil (kaynak sayısını sayıyor, madde sayısını değil);
  bu deney için kör bir ölçüt.
- Sadakat elle ölçülmedi; zenginlik farkı sayıyla görünmüyor.

## Karar

- **N=1 kalır.** N=2 tokenı %55 artırıyor, ama talimat sembol başına en çok 3 kaynağa izin
  verdiği için fazladan maddeler yoruma pek giremiyor. 1 Aralık'tan sonra token ücretli olacak.
- `config.py`'deki "N=2 ile sentez 12 dakika sürüyordu" notu tek çağrılı sentez içindi;
  güncellendi.
- Hangi belge güncellendi: `src/ruya/config.py` (yorum), [olcumler](../olcumler.md), [15](../15-kalan-isler-plani.md).
