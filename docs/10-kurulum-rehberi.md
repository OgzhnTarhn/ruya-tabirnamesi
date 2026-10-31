# 10 · Kurulum Rehberi (Hafta 0)

> Durum: v0.3 · Tarih: 31 Ekim 2026 (Colab ve Drive yerine bilgisayarda çalışma)
> Ortamın genel resmi: [11-calisma-ortami.md](11-calisma-ortami.md)

## 1. LLM API anahtarı [ZORUNLU]

Model olarak EVREN LLM geçidi üzerinden `deepseek-v4.1-flash` kullanılır (31 Ekim 2026 kararı; kodun bu sağlayıcıya geçişi ayrı bir adımda yapılır).

1. Anahtar `EVREN_LLM_API_KEY` adlı **kullanıcı ortam değişkeninde** durur. Orkestra da aynı anahtarı kullandığı için bu bilgisayarda tanımlı. Yeni bir bilgisayarda bir kez:

```powershell
[Environment]::SetEnvironmentVariable("EVREN_LLM_API_KEY", "<anahtar>", "User")
```

   Sonra VS Code'u ve terminali yeniden aç.
2. **Anahtarı hiçbir yere yapıştırma:** sohbete, koda, `.env` dosyasına, GitHub'a, notebook hücresine.
3. Kalan kota: günde 15 milyon token. Modeller 1 Aralık 2026'ya kadar ücretsiz.

## 2. GitHub repo [ÖNERİLEN]

1. Repo GitHub'da **Private** olarak duruyor. Push'u sen yaparsın.
2. GitHub yalnızca kod ve belgelerin yedeğidir. Veri (`data/`) oraya gitmez.

## 3. Bilgisayar [ZORUNLU]

- **VS Code** ve **Git** (ikisi de kurulu).
- **uv** (kurulu değilse):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Repo klasöründe bir kez:

```powershell
uv sync                      # .venv ve temel bağımlılıklar
uv run nbstripout --install  # notebook çıktılarını commit'ten önce temizleyen git filtresi
uv run pytest                # hepsi geçmeli; veri yoksa kontrat testleri "skipped" görünür
```

Arayüz (Gradio) ve vektör indeksi gerektiğinde ağır paketler: `uv sync --extra hepsi`.

Her değişiklikten sonra: `uv run pytest` ve `uv run ruff check . && uv run ruff format .`

## 4. Kaynakları indir

```powershell
uv run python scripts/download_sources.py            # Aşama 0: nablusi, miller
uv run python scripts/download_sources.py --asama 3  # bütün kaynaklar
```

Dosyalar `data/raw/` altına iner. Her dosyanın SHA256 özeti `data/raw/KAYNAK_OZETLERI.json` dosyasına yazılır. Bu özetler `src/ruya/ingest/kaynaklar.py`'deki `sha256` alanlarına işlenir; böylece kaynak sonradan değişirse indirme hata verir.

## 5. Elle doğrulanacaklar (10 dakika)

- [ ] [Zenodo'daki OpenITI kaydını](https://zenodo.org/records/17767721) aç ve lisansın CC BY-NC-SA 4.0 olduğunu gör. Atıf künyesi sonra `docs/KAYNAKLAR.md` dosyasına eklenecek.
- [ ] VS Code'da `notebooks/00_ortam_kontrolu.ipynb`'yi `.venv` çekirdeğiyle aç ve çalıştır.
