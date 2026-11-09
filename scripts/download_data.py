"""Ham veriyi indirir. Ham veri depoya konmadığı için herkes bu betikle aynı veriyi elde eder.

Kullanım:
    python scripts/download_data.py golub   # Kaggle API anahtarı gerekir (~/.kaggle/kaggle.json)
    python scripts/download_data.py mile    # GEO'dan GSE13159 (~1 GB indirme)
    python scripts/download_data.py all
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR, MILE_DIR


def download_golub():
    # Kaggle: crawford/gene-expression (CC0)
    from kaggle.api.kaggle_api_extended import KaggleApi

    GOLUB_DIR.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files("crawford/gene-expression", path=GOLUB_DIR, unzip=True)
    print("Golub indirildi:", sorted(p.name for p in GOLUB_DIR.iterdir()))


def download_mile():
    # GEO GSE13159 seri matrisi + iki platformun anotasyonu (prob -> gen sembolü eşlemesi için)
    import GEOparse

    MILE_DIR.mkdir(parents=True, exist_ok=True)
    GEOparse.get_GEO(geo="GSE13159", destdir=str(MILE_DIR), silent=False)
    GEOparse.get_GEO(geo="GPL570", destdir=str(MILE_DIR))  # HG-U133 Plus 2.0 (MILE)
    GEOparse.get_GEO(geo="GPL80", destdir=str(MILE_DIR))   # Hu6800 (Golub)
    print("MILE ve platform anotasyonları indirildi.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("golub", "all"):
        download_golub()
    if target in ("mile", "all"):
        download_mile()
