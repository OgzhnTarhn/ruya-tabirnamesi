# Deneyler

Her deney kısa bir not olarak burada durur (docs/06, bölüm 4). Not, deney bittiğinde yazılır ve
**bir karar** içerir; karar başka bir belgeyi değiştiriyorsa o belge aynı gün güncellenir.

- Şablon: [`_sablon.md`](_sablon.md)
- Notebook'lar: `notebooks/deneyler/`
- Ham çıktılar ve tablolar `data/deneyler/` altında; buraya özet ve karar girer.

| # | Deney | Hafta | Not | Durum |
|---|---|---|---|---|
| 01 | Veri ve çeviri denemesi (K0) | 1 | [01-veri-ve-ceviri.md](01-veri-ve-ceviri.md) | 🕓 |
| D1 | Vektör kolu var / yok (sözlük + BM25 ile hibrit; 10 Kasım'da yeniden tanımlandı, [15](../15-kalan-isler-plani.md) K3) | 7 | [D1-D2-getirme.md](D1-D2-getirme.md) | 🟡 ön sonuç (gümüş etiket): vektör kolu kalır |
| D2 | Reranker var / yok | 7 | [D1-D2-getirme.md](D1-D2-getirme.md) | 🟡 ön sonuç (gümüş etiket): reranker kalır |
| D3 | Kaynak başına N = 1, 2, 3 | 7 | [D3-n-degeri.md](D3-n-degeri.md) | ✅ N=1 kalır |
| D4 | Sentezde `deepseek-v4.1-flash` / `mimo-v2.6-pro` ([15](../15-kalan-isler-plani.md) K7) | 12 | [D4-model.md](D4-model.md) | ✅ deepseek kalır |
| D5 | ~~Yerel Gemma/Qwen~~ yapılmayacak ([15](../15-kalan-isler-plani.md) K8) | 12 | — | ✖ |
