"""Her Colab notebook'unun ortak kurulumu (docs/11, bölüm 5).

Notebook'un ilk hücresi repoyu klonlar ve bu dosyayı ``%run`` ile çalıştırır
(hücrenin metni: notebooks/README.md). Bu dosya sırasıyla:

1. Drive'ı bağlar.
2. Colab Secrets'tan ANTHROPIC_API_KEY'i ortam değişkenine aktarır (yazdırmaz, dosyaya yazmaz).
3. Repoyu günceller (git pull). Token remote URL'sinde tutulmaz.
4. Paketi düzenlenebilir kipte kurar: ``pip install -e .[RUYA_EKLER]``.
5. RUYA_DATA_DIR, RUYA_WORK_DIR, HF_HOME değişkenlerini ayarlar, klasörleri açar.

Ağır paketler (Chroma, sentence-transformers, Gradio) gerekiyorsa ilk hücrede
``os.environ["RUYA_EKLER"] = "colab"`` yazılır; varsayılan yalnızca temel paketlerdir.
"""

import base64
import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/content/ruya-tabirnamesi")
REPO_URL = "https://github.com/OgzhnTarhn/ruya-tabirnamesi.git"
VERI = Path("/content/drive/MyDrive/ruya-tabirnamesi")
CALISMA = Path("/content/calisma")
DRIVE_KLASORLERI = (
    "data/raw",
    "data/interim",
    "data/processed",
    "data/index",
    "cache/llm",
    "cache/batch",
    "raporlar",
    "gecmis",
    "logs",
)


def _gizli(ad: str, zorunlu: bool) -> str | None:
    from google.colab import userdata

    try:
        return userdata.get(ad)
    except Exception:
        if zorunlu:
            raise RuntimeError(
                f"Colab Secrets'ta {ad} yok ya da notebook'un erişimi kapalı "
                "(docs/10-kurulum-rehberi.md, adım 4)."
            ) from None
        return None


def _git(*argumanlar: str, token: str | None = None) -> str:
    komut = ["git"]
    if token:
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        komut += ["-c", f"http.extraHeader=Authorization: Basic {basic}"]
    sonuc = subprocess.run([*komut, "-C", str(REPO), *argumanlar], capture_output=True, text=True)
    if sonuc.returncode:
        hata = sonuc.stderr.replace(token, "***") if token else sonuc.stderr
        raise RuntimeError(f"git {argumanlar[0]} başarısız:\n{hata}")
    return sonuc.stdout.strip()


def drive_bagla() -> None:
    if not Path("/content/drive/MyDrive").is_dir():
        from google.colab import drive

        drive.mount("/content/drive")


def gizli_bilgileri_yukle() -> str | None:
    os.environ["ANTHROPIC_API_KEY"] = _gizli("ANTHROPIC_API_KEY", zorunlu=True)
    return _gizli("GITHUB_TOKEN", zorunlu=False)


def repoyu_guncelle(github_token: str | None) -> str:
    _git("remote", "set-url", "origin", REPO_URL)  # klonlamada kullanılan token silinir
    _git("pull", "-q", "--ff-only", token=github_token)
    return _git("log", "-1", "--format=%h %s")


def paketi_kur() -> None:
    ekler = os.environ.get("RUYA_EKLER", "").strip()
    hedef = f"{REPO}[{ekler}]" if ekler else str(REPO)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", hedef], check=True)
    # Çalışan çekirdek yeni .pth dosyasını okumaz; yolu elle ekle.
    for yol in (str(REPO / "src"), str(REPO)):
        if yol not in sys.path:
            sys.path.insert(0, yol)


def ortami_ayarla() -> None:
    os.environ["RUYA_DATA_DIR"] = str(VERI)
    os.environ["RUYA_WORK_DIR"] = str(CALISMA)
    os.environ["HF_HOME"] = str(CALISMA / "hf")
    for klasor in DRIVE_KLASORLERI:
        (VERI / klasor).mkdir(parents=True, exist_ok=True)
    (CALISMA / "hf").mkdir(parents=True, exist_ok=True)
    os.chdir(REPO)


def otomatik_yeniden_yukle() -> None:
    """git pull sonrası değişen modüller çekirdeği yeniden başlatmadan yüklensin."""
    try:
        ipython = get_ipython()  # type: ignore[name-defined]
    except NameError:
        return
    ipython.run_line_magic("load_ext", "autoreload")
    ipython.run_line_magic("autoreload", "2")


def main() -> None:
    drive_bagla()
    github_token = gizli_bilgileri_yukle()
    son_commit = repoyu_guncelle(github_token)
    paketi_kur()
    ortami_ayarla()
    otomatik_yeniden_yukle()
    gpu = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.strip()
    print(f"Repo     : {son_commit}")
    print(f"Python   : {sys.version.split()[0]}")
    print(f"GPU      : {gpu or 'yok (CPU çalışma zamanı)'}")
    print(f"Veri     : {VERI}")
    print(f"Çalışma  : {CALISMA}")
    print(f"Ekler    : {os.environ.get('RUYA_EKLER') or '-'}")


if __name__ == "__main__":
    main()
