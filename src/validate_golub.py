"""EDA Adım 1: Golub yükleme ve etiket eşleştirmesinin doğrulanması.

load_golub.py zaten sınıf sayılarını assert ile kontrol ediyor. Burada ek olarak,
yönergenin uyardığı "sütun sırası" sorununun gerçekten var olduğunu gösteriyor ve
eşleştirmenin hasta numarasıyla yapıldığını bağımsız bir yoldan kontrol ediyoruz.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR
from src.load_golub import FILES, load_split


def raw_patient_order(split: str) -> list[int]:
    """CSV'deki hasta sütunlarının dosyadaki (ham) sırası."""
    cols = pd.read_csv(GOLUB_DIR / FILES[split], nrows=0).columns
    return [int(c) for c in cols if c.isdigit()]


def validate() -> dict:
    labels = pd.read_csv(GOLUB_DIR / "actual.csv").set_index("patient")["cancer"]
    out = {"n_label_rows": len(labels)}
    data = {}

    for split in ("train", "test"):
        X, y, calls, gene_info = load_split(split)
        order = raw_patient_order(split)
        data[split] = X

        # Sütun sırası sorunu gerçekten var mı? (sıralı olsaydı sıraya göre eşlemek de işe yarardı)
        out[f"{split}_raw_order"] = order
        out[f"{split}_is_sorted"] = order == sorted(order)

        # Sıraya göre eşleseydik kaç hasta yanlış etiket alırdı? Sorunun büyüklüğünü gösterir.
        start = min(order)
        naive = labels.loc[list(range(start, start + len(order)))].values  # 1,2,3... varsayımı
        true_for_raw = labels.loc[order].values
        out[f"{split}_naive_mislabeled"] = int((naive != true_for_raw).sum())

        # Bağımsız kontrol: y her hastada actual.csv'deki etiketle aynı mı?
        assert (y.index == X.index).all()
        assert (y.map({0: "ALL", 1: "AML"}).values == labels.loc[X.index].values).all()

        out[f"{split}_shape"] = X.shape
        out[f"{split}_counts"] = y.map({0: "ALL", 1: "AML"}).value_counts().to_dict()
        out[f"{split}_ids"] = (X.index.min(), X.index.max())
        out[f"{split}_call_values"] = sorted(pd.unique(calls.values.ravel()))
        out[f"{split}_n_affx"] = int(X.columns.str.startswith("AFFX").sum())

    # Eğitim ve test aynı hastayı içermemeli; birlikte 72 hastayı (1-72) kapsamalı
    tr, te = set(data["train"].index), set(data["test"].index)
    out["overlap"] = len(tr & te)
    out["union_is_1_72"] = (tr | te) == set(range(1, 73))
    # İki sette prob listesi ve sırası aynı mı? (sonradan birleştirmek için şart)
    out["same_genes"] = bool((data["train"].columns == data["test"].columns).all())
    return out


if __name__ == "__main__":
    for k, v in validate().items():
        print(f"{k}: {v}")
