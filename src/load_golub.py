"""Golub verisini yükler, temizler ve etiket eşleştirmesini DOĞRULAR.

Yönergenin özellikle uyardığı iki nokta burada ele alınır:
1. 'call' (P/A/M) sütunları sayısal değildir, ifade matrisinden ayrılır.
2. CSV'deki hasta sütunları numara sırasında DEĞİLDİR. Etiketler sütun sırasına göre
   değil, hasta numarasına göre eşlenir ve sonuç beklenen sınıf sayılarıyla kontrol edilir.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR, LABEL_MAP

EXPECTED = {"train": {"ALL": 27, "AML": 11}, "test": {"ALL": 20, "AML": 14}}
FILES = {"train": "data_set_ALL_AML_train.csv", "test": "data_set_ALL_AML_independent.csv"}


def _split_expression_and_calls(raw: pd.DataFrame):
    """Ham tabloyu (gen x sütun) ifade matrisi ve call matrisi olarak ikiye ayırır."""
    gene_info = raw[["Gene Description", "Gene Accession Number"]]
    call_cols = [c for c in raw.columns if c.startswith("call")]
    sample_cols = [c for c in raw.columns if c not in call_cols and c not in gene_info.columns]

    # Her hasta sütununun hemen sağındaki sütun onun call sütunudur
    calls = {}
    for s in sample_cols:
        nxt = raw.columns[raw.columns.get_loc(s) + 1]
        assert nxt.startswith("call"), f"{s} sütununun yanında call sütunu yok: {nxt}"
        calls[int(s)] = raw[nxt].values

    expr = raw[sample_cols].copy()
    expr.columns = [int(c) for c in sample_cols]
    expr.index = raw["Gene Accession Number"]
    calls = pd.DataFrame(calls, index=expr.index)
    return expr, calls, gene_info


def load_split(split: str):
    raw = pd.read_csv(GOLUB_DIR / FILES[split])
    labels = pd.read_csv(GOLUB_DIR / "actual.csv").set_index("patient")["cancer"]

    expr, calls, gene_info = _split_expression_and_calls(raw)

    # Satır = hasta, sütun = gen. Etiket hasta NUMARASINDAN eşlenir, sıradan değil.
    X = expr.T.sort_index()
    calls = calls.T.loc[X.index]
    y_text = labels.loc[X.index]

    # Doğrulama: beklenen sınıf sayıları tutuyor mu?
    counts = y_text.value_counts().to_dict()
    assert counts == EXPECTED[split], f"{split}: beklenen {EXPECTED[split]}, bulunan {counts}"

    y = y_text.map(LABEL_MAP)
    return X, y, calls, gene_info


if __name__ == "__main__":
    for split in ("train", "test"):
        X, y, calls, _ = load_split(split)
        print(f"{split}: X={X.shape}, sınıflar={y.value_counts().to_dict()}, "
              f"hasta no aralığı={X.index.min()}-{X.index.max()}")
    print("Etiket eşleştirmesi doğrulandı.")
