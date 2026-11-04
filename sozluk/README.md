# Sembol sözlüğü

`symbols.json`, elle onaylanan kanonik sembol indeksidir. Veri değil sözlüktür: içinde
yalnızca kelimeler ve eşlemeler var, lisanslı metin yok. Bu yüzden git'te durur ve her
değişikliği commit geçmişinde görünür.

- Şema: [docs/02, bölüm 4.2](../docs/02-veri-kaynaklari-ve-semasi.md) · kod: `ruya.schemas.SymbolKaydi`
- Yaşam döngüsü (öneri → gözden geçirme → onay): [docs/12, bölüm 5](../docs/12-kod-yapisi-ve-sozlesmeler.md)
- `gozden_gecirildi: true` olmayan sembol MVP'de kullanılmaz.
- Her değişiklikten sonra `uv run pytest tests/test_sozluk.py` çalıştır.

> **Not (4 Kasım 2026):** Sözlük 143 sembole çıkarıldı. Yeni 85 sembolü EVREN önerdi, Claude listeyi gözden geçirdi; kullanıcı henüz onaylamadı.

> **Not (2 Kasım 2026):** İlk 58 sembolü EVREN önerdi, Claude denetledi ve `gozden_gecirildi: true` yaptı; proje sahibi işi devrettiği için kendi gözden geçirmesi henüz yapılmadı. Bu listeyi okuyup düzeltmek hâlâ açık bir iştir.
