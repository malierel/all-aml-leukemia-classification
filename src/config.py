"""Proje genelinde kullanılan sabitler. Tek bir yerde tutulur ki her betik aynı değeri kullansın."""
from pathlib import Path

SEED = 42  # Sabit random seed (yönerge 6.9)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"

GOLUB_DIR = RAW / "golub"
MILE_DIR = RAW / "mile"

# Etiket kodlaması (modüldeki gibi): ALL = 0, AML = 1
LABEL_MAP = {"ALL": 0, "AML": 1}

# Sınıf renkleri: tüm şekillerde aynı kalsın diye tek yerde tanımlı.
# Mavi/turuncu çifti renk körlüğünde de ayırt edilebilir.
CLASS_COLORS = {"ALL": "#1f77b4", "AML": "#ff7f0e"}
# Set (batch) renkleri: sınıf renkleriyle karışmasın diye farklı ton ailesi
SET_COLORS = {"train": "#4d4d4d", "test": "#2ca02c"}

# IEEE tek sütun genişliği (inç); şekiller bu genişlikte üretilir
FIG_WIDTH = 3.5
