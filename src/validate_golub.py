"""EDA 1. adım: Golub verisini yükleyip etiketlerin doğru eşlendiğini kontrol ediyoruz.

load_golub.py sınıf sayılarını zaten kontrol ediyor. Burada iki şey daha yapıyoruz:
yönergenin bahsettiği sütun sırası sorununun gerçekten var olduğunu gösteriyoruz, sonra da
etiketlerin hasta numarasına göre doğru verildiğini ikinci bir yoldan kontrol ediyoruz.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR
from src.load_golub import FILES, load_split


def raw_patient_order(split: str) -> list[int]:
    """CSV dosyasında hasta sütunları hangi sırayla dizilmiş, onu veriyor."""
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

        # Önce sütunların gerçekten karışık olup olmadığına bakıyoruz.
        # Sıralı olsalardı etiketleri sırayla vermek de doğru sonuç verirdi.
        out[f"{split}_raw_order"] = order
        out[f"{split}_is_sorted"] = order == sorted(order)

        # Etiketleri sütun sırasına göre verseydik kaç hasta yanlış etiket alırdı?
        # Bu sayı sorunun ne kadar büyük olduğunu gösteriyor.
        start = min(order)
        naive = labels.loc[list(range(start, start + len(order)))].values  # "sütunlar 1, 2, 3 diye gidiyor" diye varsaysaydık
        true_for_raw = labels.loc[order].values
        out[f"{split}_naive_mislabeled"] = int((naive != true_for_raw).sum())

        # İkinci kontrol: her hastanın etiketini actual.csv'deki etiketiyle tek tek karşılaştırıyoruz
        assert (y.index == X.index).all()
        assert (y.map({0: "ALL", 1: "AML"}).values == labels.loc[X.index].values).all()

        out[f"{split}_shape"] = X.shape
        out[f"{split}_counts"] = y.map({0: "ALL", 1: "AML"}).value_counts().to_dict()
        out[f"{split}_ids"] = (X.index.min(), X.index.max())
        out[f"{split}_call_values"] = sorted(pd.unique(calls.values.ravel()))
        out[f"{split}_n_affx"] = int(X.columns.str.startswith("AFFX").sum())

    # Aynı hasta hem eğitimde hem testte olmamalı. İki set birlikte de 1'den 72'ye kadar bütün hastaları içermeli.
    tr, te = set(data["train"].index), set(data["test"].index)
    out["overlap"] = len(tr & te)
    out["union_is_1_72"] = (tr | te) == set(range(1, 73))
    # İki sette genler aynı sırada mı? İleride iki seti yan yana koyacağımız için bunun tutması lazım.
    out["same_genes"] = bool((data["train"].columns == data["test"].columns).all())
    return out


if __name__ == "__main__":
    for k, v in validate().items():
        print(f"{k}: {v}")
