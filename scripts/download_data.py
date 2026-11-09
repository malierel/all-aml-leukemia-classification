"""Ham veriyi indiren betik. Ham veriyi depoya koymuyoruz; bunun yerine herkes bu betikle aynı veriyi indirebiliyor.

Kullanım:
    python scripts/download_data.py golub   # Kaggle API anahtarı gerekiyor (~/.kaggle/kaggle.json)
    python scripts/download_data.py mile    # GEO'dan GSE13159'u indiriyor (yaklaşık 1 GB)
    python scripts/download_data.py all
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR, MILE_DIR


def download_golub():
    # Golub verisi Kaggle'daki crawford/gene-expression sayfasından geliyor, lisansı CC0
    from kaggle.api.kaggle_api_extended import KaggleApi

    GOLUB_DIR.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files("crawford/gene-expression", path=GOLUB_DIR, unzip=True)
    print("Golub indirildi:", sorted(p.name for p in GOLUB_DIR.iterdir()))


def download_mile():
    # MILE verisinin yanında iki yonganın anotasyon dosyalarını da indiriyoruz.
    # Bunlara ihtiyacımız var çünkü iki veri setindeki prob adlarını gen adlarına çevirip öyle karşılaştıracağız.
    import GEOparse

    MILE_DIR.mkdir(parents=True, exist_ok=True)
    GEOparse.get_GEO(geo="GSE13159", destdir=str(MILE_DIR), silent=False)
    GEOparse.get_GEO(geo="GPL570", destdir=str(MILE_DIR))  # MILE'ın kullandığı yonga: HG-U133 Plus 2.0
    GEOparse.get_GEO(geo="GPL80", destdir=str(MILE_DIR))   # Golub'un kullandığı yonga: Hu6800
    print("MILE ve platform anotasyonları indirildi.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("golub", "all"):
        download_golub()
    if target in ("mile", "all"):
        download_mile()
