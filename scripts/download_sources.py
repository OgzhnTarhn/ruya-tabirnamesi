"""Ham kaynakları Drive'daki data/raw/ klasörüne indirir ve SHA256 özetlerini kaydeder.

Colab'de çalışır (notebooks/01_kaynaklari_indir.ipynb ya da Hafta 1 denemesi)::

    python scripts/download_sources.py            # Aşama 0 kaynakları: nablusi, miller
    python scripts/download_sources.py --asama 3  # Aşama 3'e kadar bütün kaynaklar

- Dosyalar tek tek ve aralıklı indirilir; Gutenberg'den toplu indirme yapılmaz (docs/07).
- Var olan dosya yeniden indirilmez (``--yeniden`` ile zorlanır).
- Özetler ``data/raw/KAYNAK_OZETLERI.json`` dosyasına yazılır; ham dosya değişirse fark edilir.
- Bilgisayarda çalışmaz: veri bilgisayara inmez (CLAUDE.md).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import time
import urllib.request
from pathlib import Path

from ruya.config import ayarlar
from ruya.ingest.kaynaklar import KAYNAKLAR, KaynakBilgisi

OZET_DOSYASI = "KAYNAK_OZETLERI.json"
BEKLEME_SN = 3
KULLANICI_AJANI = "ruya-tabirnamesi/0.0 (kisisel ogrenme projesi)"


def indir(bilgi: KaynakBilgisi, klasor: Path) -> dict[str, object]:
    istek = urllib.request.Request(bilgi.url, headers={"User-Agent": KULLANICI_AJANI})
    with urllib.request.urlopen(istek, timeout=120) as yanit:
        icerik = yanit.read()
    (klasor / bilgi.ham_dosya_adi).write_bytes(icerik)
    return {
        "dosya": bilgi.ham_dosya_adi,
        "url": bilgi.url,
        "lisans": bilgi.lisans,
        "bayt": len(icerik),
        "sha256": hashlib.sha256(icerik).hexdigest(),
        "indirme_zamani": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }


def main(argv: list[str] | None = None) -> None:
    ayristirici = argparse.ArgumentParser(description="Ham kaynakları Drive'a indirir.")
    ayristirici.add_argument("--asama", type=int, default=0, help="bu aşamaya kadarki kaynaklar")
    ayristirici.add_argument("--kaynak", nargs="*", choices=sorted(KAYNAKLAR))
    ayristirici.add_argument("--yeniden", action="store_true", help="var olanı da indir")
    args = ayristirici.parse_args(argv)

    secilenler = [
        b
        for b in KAYNAKLAR.values()
        if (b.kaynak in args.kaynak if args.kaynak else b.asama <= args.asama)
    ]
    klasor = ayarlar().ham_klasoru
    klasor.mkdir(parents=True, exist_ok=True)
    ozet_yolu = klasor / OZET_DOSYASI
    ozetler = json.loads(ozet_yolu.read_text(encoding="utf-8")) if ozet_yolu.exists() else {}

    for sira, bilgi in enumerate(secilenler):
        if (klasor / bilgi.ham_dosya_adi).exists() and not args.yeniden:
            print(f"{bilgi.kaynak}: zaten var, atlandı")
            continue
        if sira:
            time.sleep(BEKLEME_SN)
        ozetler[bilgi.kaynak] = indir(bilgi, klasor)
        print(f"{bilgi.kaynak}: {ozetler[bilgi.kaynak]['bayt']:,} bayt indirildi")

    ozet_yolu.write_text(json.dumps(ozetler, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Özetler: {ozet_yolu}")


if __name__ == "__main__":
    main()
