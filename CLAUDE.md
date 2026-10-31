# Proje kuralları

## Commitler
- Commitler **atomik** olur: her commit tek bir mantıksal değişiklik içerir. Büyük işleri mantıksal parçalara bölerek ayrı ayrı commit et.
- Commit mesajlarında ve PR açıklamalarında **Claude imzası yoktur**: `Co-Authored-By: Claude …` satırı ve "Generated with Claude Code" notu eklenmez.
- Commit mesajları Türkçedir, ilk satır kısa ve emir kipindedir (ör. `Miller ayrıştırıcısını ekle`).
- Push'u kullanıcı yapar; sorulmadan push etme.

## Çalışma ortamı
- Kod yazma, çalıştırma ve veri **bilgisayardadır** (`C:\ruya-tabirnamesi`). Ayrıntı: `docs/11-calisma-ortami.md`.
- Bütün veri (ham kaynaklar, işlenmiş maddeler, indeks, LLM önbelleği, raporlar, loglar) repodaki `data/` klasöründe durur; `data/` git'e girmez. Kod `data/` dışına veri yazmaz.
- Birim testleri verisizdir (`tests/fixtures/` içindeki birkaç satırlık örnekler); gerçek veriyi denetleyen kontrat testleri (`-m veri`) veri yoksa kendiliğinden atlanır.
- Notebook'lar ince kalır: mantık `src/ruya/` paketinde, notebook yalnızca fonksiyon çağırır. Notebook çıktıları commit'ten önce temizlenir (nbstripout).
- Gradio arayüzü yalnızca yerelde (`localhost`) açılır; `share=True` kullanılmaz.

## Çalışma düzeni
- Kod yazmadan önce `docs/` altındaki ilgili belgeyi oku (mimari: `docs/03-mimari.md`, kod yapısı ve modül sözleşmeleri: `docs/12-kod-yapisi-ve-sozlesmeler.md`, takvim: `docs/08-yol-haritasi-takvim.md`).
- Katman kuralına uy: bir modül yalnızca `docs/12` bölüm 1'de izin verilen `ruya` birimlerini içe aktarır; ağır paketler (chromadb, sentence-transformers, gradio, torch) yalnızca işlev içinde içe aktarılır. `tests/test_mimari.py` bunu denetler.
- Şema değişikliği önce belgede (`docs/02`, `docs/12`), sonra `src/ruya/schemas.py`'de yapılır.
- Commit'ten önce `uv run pytest` ve `uv run ruff check .` temiz olmalı.
- `data/`, `.env`, `.cache/`, `logs/` git'e eklenmez.
- Gizli bilgiler (API anahtarı) yalnızca ortam değişkeninde durur; hiçbir dosyaya (`.env` dahil) yazılmaz.
- Claude API model adları yalnızca `src/ruya/config.py` içinde tanımlanır.
