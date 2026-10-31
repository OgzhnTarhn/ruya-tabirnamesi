"""Notebook'ların ortak kurulumu (docs/11, bölüm 5).

Notebook'un ilk hücresi repo kökünü bulur ve bu dosyayı ``%run`` ile çalıştırır
(hücrenin metni: notebooks/README.md). Sırasıyla çalışma klasörünü repo köküne alır,
``autoreload``u açar, API anahtarının tanımlı olup olmadığını söyler (yazdırmaz) ve
repo commit'ini, Python sürümünü, veri klasörünü, ham kaynakları gösterir.

Kod, veri ve çalıştırma aynı bilgisayarda; paket ``uv sync`` ile düzenlenebilir
kipte kurulur, veri ``<repo>/data`` altında durur.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def otomatik_yeniden_yukle() -> None:
    """Paket değişince modüller çekirdeği yeniden başlatmadan yüklensin."""
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
    except NameError:
        return
    ipython.run_line_magic("load_ext", "autoreload")
    ipython.run_line_magic("autoreload", "2")


def son_commit() -> str:
    """Kısa commit özeti; git yoksa ya da hata verirse '-' döner."""
    try:
        sonuc = subprocess.run(
            ["git", "-C", str(REPO), "log", "-1", "--format=%h %s"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return "-"
    return sonuc.stdout.strip() if sonuc.returncode == 0 else "-"


def main() -> None:
    os.chdir(REPO)
    otomatik_yeniden_yukle()

    from ruya import config
    from ruya.ingest.kaynaklar import KAYNAKLAR

    # Anahtar yoksa uyarılır ama durulmaz: veri hücreleri anahtarsız da çalışır.
    anahtar_var = bool(os.environ.get(config.LLM_ANAHTAR_DEGISKENI, "").strip())
    if not anahtar_var:
        print(
            f"UYARI: {config.LLM_ANAHTAR_DEGISKENI} tanımlı değil. LLM çağrıları çalışmaz; "
            "anahtarı ortam değişkenine ekleyin (docs/10-kurulum-rehberi.md, adım 1)."
        )

    ayar = config.ayarlar()
    print(f"Repo     : {son_commit()}")
    print(f"Python   : {sys.version.split()[0]}")
    print(f"Veri     : {ayar.data_dir}")
    print(f"API anahtarı: {'tanımlı' if anahtar_var else 'YOK'}")
    for ad in KAYNAKLAR:
        var = (ayar.ham_klasoru / f"{ad}.txt").is_file()
        print(f"  {ad}.txt {'var' if var else 'yok'}")


if __name__ == "__main__":
    main()
