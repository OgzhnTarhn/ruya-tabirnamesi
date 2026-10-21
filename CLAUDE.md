# Proje kuralları

## Commitler
- Commitler **atomik** olur: her commit tek bir mantıksal değişiklik içerir. Büyük işleri mantıksal parçalara bölerek ayrı ayrı commit et.
- Commit mesajlarında ve PR açıklamalarında **Claude imzası yoktur**: `Co-Authored-By: Claude …` satırı ve "Generated with Claude Code" notu eklenmez.
- Commit mesajları Türkçedir, ilk satır kısa ve emir kipindedir (ör. `Miller ayrıştırıcısını ekle`).
- Push'u kullanıcı yapar; sorulmadan push etme.

## Çalışma düzeni
- Kod yazmadan önce `docs/` altındaki ilgili belgeyi oku (mimari: `docs/03-mimari.md`, takvim: `docs/08-yol-haritasi-takvim.md`).
- `data/`, `.env`, `.cache/`, `logs/` git'e eklenmez.
- Yollar: proje `C:\ruya-tabirnamesi`; Hugging Face önbelleği `HF_HOME` ile proje içine yönlendirilir.
- Claude API model adları yalnızca `src/ruya/config.py` içinde tanımlanır.
