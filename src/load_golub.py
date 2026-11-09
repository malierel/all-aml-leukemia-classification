"""Golub verisini okuyup temizleyen ve etiketlerin doğru eşlendiğini kontrol eden dosya.

Yönerge iki konuda özellikle uyarıyordu, ikisini de burada hallediyoruz:
1. 'call' sütunları (P/A/M) sayı değil, harf. Bunları ifade değerlerinden ayırıyoruz.
2. CSV'de hastalar numara sırasıyla dizilmemiş. O yüzden etiketi sütunun sırasına bakarak değil,
   hasta numarasına bakarak veriyoruz. Sonra da sınıf sayıları beklediğimiz gibi mi diye kontrol ediyoruz.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import GOLUB_DIR, LABEL_MAP

EXPECTED = {"train": {"ALL": 27, "AML": 11}, "test": {"ALL": 20, "AML": 14}}
FILES = {"train": "data_set_ALL_AML_train.csv", "test": "data_set_ALL_AML_independent.csv"}


def _split_expression_and_calls(raw: pd.DataFrame):
    """Ham tabloyu ikiye ayırıyor: bir yanda sayısal ifade değerleri, öbür yanda call harfleri."""
    gene_info = raw[["Gene Description", "Gene Accession Number"]]
    call_cols = [c for c in raw.columns if c.startswith("call")]
    sample_cols = [c for c in raw.columns if c not in call_cols and c not in gene_info.columns]

    # Her hastanın call sütunu hemen sağında duruyor. Bunu varsaymak yerine assert ile kontrol ediyoruz;
    # tutmazsa program burada durup hangi sütunda sorun olduğunu söylüyor.
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

    # Tabloyu çeviriyoruz: her satır bir hasta, her sütun bir gen olsun.
    # Etiketi hasta numarasına göre alıyoruz; sütun sırası karışık olduğu için sıraya güvenmiyoruz.
    X = expr.T.sort_index()
    calls = calls.T.loc[X.index]
    y_text = labels.loc[X.index]

    # Son kontrol: ALL ve AML sayıları beklediğimiz gibi mi?
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
