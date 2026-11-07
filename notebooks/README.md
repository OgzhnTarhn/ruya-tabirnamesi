# Notebook'lar

Notebook'lar **ince** tutulur: mantık `src/ruya/` paketinde, notebook yalnızca sırayla
fonksiyon çağırır ve sonucu gösterir (docs/11, bölüm 5). Notebook'lar bilgisayarda,
VS Code'da projenin `.venv` çekirdeğiyle açılır ve çalıştırılır (`uv sync` paketi ve
`ipykernel`'i kurar).

## Her notebook'un ilk hücresi

Hücre repo kökünü bulur ve `_kurulum.py`'yi çalıştırır. `_kurulum.py` çalışma klasörünü
repo köküne alır, `autoreload`'u açar, API anahtarının tanımlı olup olmadığını ve
`data/raw` altındaki kaynakları gösterir.

```python
# Kurulum hücresi: bütün notebook'larda aynı (bkz. notebooks/README.md)
from pathlib import Path

REPO = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").is_file())
%run {REPO}/notebooks/_kurulum.py
```

## Plan

| Notebook | İş | Hafta |
|---|---|---|
| `00_ortam_kontrolu.ipynb` | Python, API anahtarı, `data/` yolları, EVREN bağlantısı, birim testleri | 0 |
| `deneyler/01_veri_ve_ceviri.ipynb` | Nablusi ayrıştırma, sembol atama ve çeviri denemesi (atılabilir kod) | 1 |

Planlanan 02–06 notebook'larının yerini betikler aldı; mantık zaten `src/ruya/` altında olduğu için ayrı notebook gerekmedi:

| Planlanan notebook | Yerine |
|---|---|
| `02_ayristir.ipynb`, `03_zenginlestir.ipynb` | `scripts/maddeleri_kur.py` |
| `04_indeks.ipynb` | `scripts/hibrit_indeks_kur.py` (Chroma yerine numpy) |
| `05_arayuz.ipynb` | `scripts/arayuz_ac.py` |
| `06_degerlendirme.ipynb` | `eval/run_eval.py` |

Kaynakları indirmek için notebook gerekmez: `uv run python scripts/download_sources.py`.

## Kurallar

- Çıktılar commit'ten önce temizlenir: `nbstripout` git filtresi (`uv run nbstripout --install`,
  her klonda bir kez). `tests/test_notebooklar.py` çıktısı kalmış notebook'u yakalar.
  Çıktılarda kaynak metinler, API yanıtları ya da rüya metni bulunabilir.
- Bir hücrede 10 satırdan uzun mantık birikirse `src/ruya/` altına taşınır.
- Model adları notebook'a yazılmaz; `ruya.config`'den okunur.
- LLM çağrıları yalnızca `ruya.llm.client.LLMIstemcisi` üzerinden yapılır.
