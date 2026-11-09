"""Ham verinin nereden, hangi adla indirileceğini gösteren ve dosyaların yerinde olup olmadığını kontrol eden betik.

Ham veriyi depoya koymuyoruz. Dosyaları elle indiriyoruz, çünkü GEO'nun "Download full table" ile verdiği
anotasyon dosyalarının adında sürüm numarası var ve bunlar otomatik indirilen .annot dosyalarından farklı.
Projede kullandığımız dosyaların birebir aynısını elde etmek için aşağıdaki adımları izlemek yeterli.

Kullanım:
    python scripts/download_data.py          # Eksik dosya varsa nereden indireceğini yazar
    python scripts/download_data.py golub    # (İsteğe bağlı) Golub'u Kaggle API ile indirir
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR, MILE_DIR

# Her dosya için: (klasör, dosya adı, nereden ve nasıl indirileceği)
FILES = [
    (GOLUB_DIR, "data_set_ALL_AML_train.csv",
     "Kaggle 'crawford/gene-expression' sayfasından (https://www.kaggle.com/datasets/crawford/gene-expression)"),
    (GOLUB_DIR, "data_set_ALL_AML_independent.csv", "Aynı Kaggle sayfasından"),
    (GOLUB_DIR, "actual.csv", "Aynı Kaggle sayfasından"),
    (MILE_DIR, "GSE13159_series_matrix.txt.gz",
     "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE13nnn/GSE13159/matrix/ (sıkıştırılmış haliyle bırakın)"),
    (MILE_DIR, "GPL570-55999.txt",
     "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL570 sayfasının altındaki 'Download full table'"),
    (MILE_DIR, "GPL80-30376.txt",
     "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL80 sayfasının altındaki 'Download full table'"),
]


def check() -> bool:
    """Her dosyanın yerinde olup olmadığına bakıyoruz; eksik olanlar için nereden indirileceğini yazıyoruz."""
    ok = True
    for folder, name, how in FILES:
        path = folder / name
        if path.exists():
            print(f"[var]   {path.relative_to(folder.parents[2])}")
        else:
            ok = False
            print(f"[EKSİK] {path.relative_to(folder.parents[2])}\n        İndirme: {how}")
    print("\nBütün dosyalar hazır." if ok else "\nEksik dosyaları indirip yukarıdaki klasörlere koyun.")
    return ok


def download_golub():
    # İsteğe bağlı kısayol: Kaggle API anahtarı (~/.kaggle/kaggle.json) varsa Golub'u otomatik indiriyoruz
    from kaggle.api.kaggle_api_extended import KaggleApi

    GOLUB_DIR.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files("crawford/gene-expression", path=GOLUB_DIR, unzip=True)
    print("Golub indirildi:", sorted(p.name for p in GOLUB_DIR.iterdir()))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1 and sys.argv[1] == "golub":
        download_golub()
    sys.exit(0 if check() else 1)
