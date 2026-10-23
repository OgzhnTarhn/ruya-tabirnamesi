# İlerleme raporu

Projenin canlı raporu bir claude.ai panosu olarak durur:
**https://claude.ai/artifact/U78T1cv6x2npEbriMxGZdU** (özel; yalnızca sen açabilirsin).

Pano; yapılanları ve yapılacakları, kilometre taşlarını, benchmark ölçütlerini hedefleriyle ve
kod sağlığını (testler, hazır ve iskelet işlevler) gösterir. Mimarinin animasyonu:
[`../gorseller/mimari.gif`](../gorseller/mimari.gif).

## Veri nereden gelir?

Panodaki her sayı repodaki bir belgeden türetilir. Repo tek doğru kaynaktır; pano onun aynasıdır.

| Pano bölümü | Kaynak | Nasıl güncellenir |
|---|---|---|
| Görevler | [08-yol-haritasi-takvim.md](../08-yol-haritasi-takvim.md) | Biten görevi `- [x]` yap |
| Kilometre taşları | 08'deki tablo | Tamamlanan taşın adına ✅ ekle |
| Benchmark | [olcumler.md](../olcumler.md) | Her ölçümden sonra bir satır ekle (`%84`, `0,12` gibi) |
| Kod sağlığı | `pytest`, `src/ruya/`, git | Kendiliğinden; gün başına bir satır birikir |

## Güncelleme

```powershell
uv run python scripts/rapor_verisi.py   # docs/rapor/veri/*.json yeniden üretilir
```

Ardından JSON dosyaları commit edilir ve panoya yüklenir. Yükleme claude.ai üzerinden
yapıldığı için Claude'a "raporu güncelle" demen yeterli: betiği çalıştırır, değişen dosyaları
panoya yükler ve commit eder.

Mimari değişirse animasyon da yeniden üretilir:

```powershell
uvx --with pillow python scripts/mimari_gif.py docs/gorseller/mimari.gif
```
