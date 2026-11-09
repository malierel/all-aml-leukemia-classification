"""Projede her yerde kullandığımız ayarlar burada duruyor.
Hepsini tek bir dosyada topladım ki bir şeyi değiştirince her betik aynı değeri görsün."""
from pathlib import Path

SEED = 42  # Rastgelelik içeren her işlemde bu sayıyı kullanıyoruz, böylece her çalıştırmada aynı sonucu alıyoruz

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

GOLUB_DIR = RAW / "golub"
MILE_DIR = RAW / "mile"

# ALL'a 0, AML'ye 1 diyoruz; derste verilen modülde de böyleydi
LABEL_MAP = {"ALL": 0, "AML": 1}

# Sınıf renklerini burada sabitledim ki her grafikte ALL hep mavi, AML hep turuncu olsun.
# Mavi-turuncu seçtim çünkü renk körü biri de bu ikisini rahatça ayırt edebiliyor.
CLASS_COLORS = {"ALL": "#1f77b4", "AML": "#ff7f0e"}
# Eğitim ve test setini gösterirken sınıf renkleriyle karışmasın diye başka renkler kullanıyoruz
SET_COLORS = {"train": "#4d4d4d", "test": "#2ca02c"}

# IEEE makalesinde bir sütun yaklaşık 3,5 inç; şekilleri bu genişlikte çiziyoruz
FIG_WIDTH = 3.5
