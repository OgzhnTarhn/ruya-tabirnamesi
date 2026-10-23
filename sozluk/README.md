# Sembol sözlüğü

`symbols.json`, elle onaylanan kanonik sembol indeksidir. Veri değil sözlüktür: içinde
yalnızca kelimeler ve eşlemeler var, lisanslı metin yok. Bu yüzden git'te durur ve her
değişikliği commit geçmişinde görünür.

- Şema: [docs/02, bölüm 4.2](../docs/02-veri-kaynaklari-ve-semasi.md) · kod: `ruya.schemas.SymbolKaydi`
- Yaşam döngüsü (öneri → gözden geçirme → onay): [docs/12, bölüm 5](../docs/12-kod-yapisi-ve-sozlesmeler.md)
- `gozden_gecirildi: true` olmayan sembol MVP'de kullanılmaz.
- Her değişiklikten sonra `uv run pytest tests/test_sozluk.py` çalıştır.
