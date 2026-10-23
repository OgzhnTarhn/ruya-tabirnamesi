# Notebook'lar

Notebook'lar **ince** tutulur: mantık `src/ruya/` paketinde, notebook yalnızca sırayla
fonksiyon çağırır ve sonucu gösterir (docs/11, bölüm 5). Notebook'lar bilgisayarda
(VS Code) düzenlenir, Colab'de çalıştırılır.

## Her notebook'un ilk hücresi

Colab'de repo henüz yokken çalışabilmesi için bu hücre `_kurulum.py`'ye taşınamaz;
her notebook'a aynen kopyalanır. Hücre repoyu klonlar, sonra `_kurulum.py` Drive'ı bağlar,
Secrets'ı okur, `git pull` yapar, paketi kurar ve yolları ayarlar.

```python
# Kurulum hücresi: bütün notebook'larda aynı (bkz. notebooks/README.md)
import os, subprocess
REPO = "/content/ruya-tabirnamesi"
# os.environ["RUYA_EKLER"] = "colab"  # Chroma, sentence-transformers, Gradio gerekiyorsa
if not os.path.isdir(REPO):
    from google.colab import userdata
    try:
        kimlik = "x-access-token:" + userdata.get("GITHUB_TOKEN") + "@"
    except Exception:
        kimlik = ""  # repo herkese açıksa token gerekmez
    sonuc = subprocess.run(
        ["git", "clone", "-q", f"https://{kimlik}github.com/OgzhnTarhn/ruya-tabirnamesi.git", REPO],
        capture_output=True,
    )
    if sonuc.returncode:
        raise RuntimeError("git clone başarısız: GITHUB_TOKEN'ı ve repo adını kontrol et")
%run {REPO}/notebooks/_kurulum.py
```

## Plan

| Notebook | İş | Hafta |
|---|---|---|
| `00_ortam_kontrolu.ipynb` | Python, GPU, Drive, Secrets kontrolü; birim testleri | 0 |
| `deneyler/01_veri_ve_ceviri.ipynb` | Nablusi ayrıştırma ve çeviri denemesi (atılabilir kod) | 1 |
| `01_kaynaklari_indir.ipynb` | `scripts/download_sources.py` | 2 |
| `02_ayristir.ipynb` | `ingest/*` → `data/interim/*.jsonl`, istatistikler | 2 |
| `03_zenginlestir.ipynb` | Sembol atama, çeviri, koşul Batch işleri | 3, 6, 8 |
| `04_indeks.ipynb` | Chroma indeksi (GPU), Drive'a zip yedeği | 6 |
| `05_arayuz.ipynb` | Gradio arayüzü (`share=False`) | 5 |
| `06_degerlendirme.ipynb` | `eval/run_eval.py`, rapor Drive'a | 5 |

## Kurallar

- Çıktılar commit'ten önce temizlenir: `nbstripout` git filtresi (`uv run nbstripout --install`,
  her klonda bir kez). `tests/test_notebooklar.py` çıktısı kalmış notebook'u yakalar.
- Colab'deki "GitHub'a kopya kaydet" kullanılmaz: filtreyi atlar, çıktılar (rüya metni,
  API yanıtı) GitHub'a gider.
- Bir hücrede 10 satırdan uzun mantık birikirse `src/ruya/` altına taşınır.
- Model adları notebook'a yazılmaz; `ruya.config`'den okunur.
