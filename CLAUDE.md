# Proje kuralları

## Commitler
- Commitler **atomik** olur: her commit tek bir mantıksal değişiklik içerir. Büyük işleri mantıksal parçalara bölerek ayrı ayrı commit et.
- Commit mesajlarında ve PR açıklamalarında **Claude imzası yoktur**: `Co-Authored-By: Claude …` satırı ve "Generated with Claude Code" notu eklenmez.
- Commit mesajları Türkçedir, ilk satır kısa ve emir kipindedir (ör. `Miller ayrıştırıcısını ekle`).
- Push'u kullanıcı yapar; sorulmadan push etme.

## Çalışma ortamı
- Kod bilgisayarda (`C:\ruya-tabirnamesi`) yazılır; **çalıştırma Google Colab'de** yapılır; **veri Google Drive'da** (`MyDrive/ruya-tabirnamesi/`) durur. Ayrıntı: `docs/11-calisma-ortami-colab-drive.md`.
- Veri setlerini, modelleri veya indeksleri bilgisayara indirme. Bilgisayarda yalnızca verisiz birim testleri çalışır (`tests/fixtures/` içindeki birkaç satırlık örneklerle).
- Notebook'lar ince kalır: mantık `src/ruya/` paketinde, notebook yalnızca fonksiyon çağırır. Notebook çıktıları commit'ten önce temizlenir (nbstripout).
- Chroma/SQLite Drive üzerinde çalıştırılmaz; `/content/calisma` altında kurulur, Drive'a zip olarak yedeklenir.
- Gradio arayüzünde `share=True` kullanılmaz.

## Çalışma düzeni
- Kod yazmadan önce `docs/` altındaki ilgili belgeyi oku (mimari: `docs/03-mimari.md`, kod yapısı ve modül sözleşmeleri: `docs/12-kod-yapisi-ve-sozlesmeler.md`, takvim: `docs/08-yol-haritasi-takvim.md`).
- Katman kuralına uy: bir modül yalnızca `docs/12` bölüm 1'de izin verilen `ruya` birimlerini içe aktarır; ağır paketler (chromadb, sentence-transformers, gradio, torch) yalnızca işlev içinde içe aktarılır. `tests/test_mimari.py` bunu denetler.
- Şema değişikliği önce belgede (`docs/02`, `docs/12`), sonra `src/ruya/schemas.py`'de yapılır.
- Commit'ten önce `uv run pytest` ve `uv run ruff check .` temiz olmalı.
- `data/`, `.env`, `.cache/`, `logs/` git'e eklenmez.
- Gizli bilgiler (API anahtarı, GitHub token) yalnızca Colab Secrets'ta durur; hiçbir dosyaya yazılmaz.
- Claude API model adları yalnızca `src/ruya/config.py` içinde tanımlanır.
