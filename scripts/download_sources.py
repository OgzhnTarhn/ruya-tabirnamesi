"""Ham kaynakları data/raw/ klasörüne indirir ve SHA256 özetlerini kaydeder.

Hedef klasör ``ayarlar().ham_klasoru``dır. Bilgisayarda çalıştırılır::

    uv run python scripts/download_sources.py            # Aşama 0 kaynakları: nablusi, miller
    uv run python scripts/download_sources.py --asama 3  # Aşama 3'e kadar bütün kaynaklar

- Dosyalar tek tek ve aralıklı indirilir; Gutenberg'den toplu indirme yapılmaz (docs/07).
- Var olan dosya yeniden indirilmez (``--yeniden`` ile zorlanır).
- Özetler ``data/raw/KAYNAK_OZETLERI.json`` dosyasına her başarılı indirmeden sonra yazılır;
  ham dosya değişirse fark edilir.
- ``KaynakBilgisi.sha256`` doluysa indirilen içeriğin özeti doğrulanır; uyuşmazsa hata verilir
  ve dosya yazılmaz (docs/02, 4.1).
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
    ozet = hashlib.sha256(icerik).hexdigest()
    if bilgi.sha256 is not None and bilgi.sha256 != ozet:
        raise ValueError(
            f"{bilgi.kaynak}: SHA256 uyuşmuyor — beklenen {bilgi.sha256}, indirilen {ozet}. "
            "Kaynağın sürümü değişmiş olabilir (docs/02, 4.1); dosya yazılmadı."
        )
    (klasor / bilgi.ham_dosya_adi).write_bytes(icerik)
    return {
        "dosya": bilgi.ham_dosya_adi,
        "url": bilgi.url,
        "lisans": bilgi.lisans,
        "bayt": len(icerik),
        "sha256": ozet,
        "indirme_zamani": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
    }


def kaynaklari_indir(secilenler: list[KaynakBilgisi], klasor: Path, yeniden: bool = False) -> Path:
    ozet_yolu = klasor / OZET_DOSYASI
    ozetler = json.loads(ozet_yolu.read_text(encoding="utf-8")) if ozet_yolu.exists() else {}

    indirilen = 0
    for bilgi in secilenler:
        if (klasor / bilgi.ham_dosya_adi).exists() and not yeniden:
            print(f"{bilgi.kaynak}: zaten var, atlandı")
            continue
        if indirilen:
            time.sleep(BEKLEME_SN)
        ozetler[bilgi.kaynak] = indir(bilgi, klasor)
        indirilen += 1
        ozet_yolu.write_text(json.dumps(ozetler, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{bilgi.kaynak}: {ozetler[bilgi.kaynak]['bayt']:,} bayt indirildi")

    return ozet_yolu


def main(argv: list[str] | None = None) -> None:
    ayristirici = argparse.ArgumentParser(description="Ham kaynakları data/raw/ klasörüne indirir.")
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
    ozet_yolu = kaynaklari_indir(secilenler, klasor, yeniden=args.yeniden)
    print(f"Özetler: {ozet_yolu}")


if __name__ == "__main__":
    main()
