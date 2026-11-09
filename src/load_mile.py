"""MILE (GEO GSE13159) verisini yükleyen dosya.

Dosyada 2.096 hasta ve 18 tanı sınıfı var. Biz sadece ALL ve AML alt sınıflarını kullanıyoruz.
Matris çok büyük olduğu için (2.096 × 54.675) önce sadece hasta bilgilerini okuyup ALL/AML hastalarını
seçiyoruz, sonra matristen yalnızca o sütunları okuyoruz. İlk okumadan sonra sonucu
data/processed altına kaydediyoruz ki her seferinde 850 MB'lık dosyayı baştan açmayalım.
"""
import gzip
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import LABEL_MAP, MILE_DIR, PROCESSED

MATRIX = MILE_DIR / "GSE13159_series_matrix.txt.gz"
CACHE = PROCESSED / "mile_all_aml.pkl"

# Hangi alt sınıf ALL, hangisi AML? Dosyadaki adları birebir yazıyoruz.
# Burada olmayan sınıfları (CLL, CML, MDS, sağlıklı kemik iliği) kullanmıyoruz; problemimiz sadece ALL ve AML.
ALL_CLASSES = [
    "mature B-ALL with t(8;14)",
    "Pro-B-ALL with t(11q23)/MLL",
    "c-ALL/Pre-B-ALL with t(9;22)",
    "T-ALL",
    "ALL with t(12;21)",
    "ALL with t(1;19)",
    "ALL with hyperdiploid karyotype",
    "c-ALL/Pre-B-ALL without t(9;22)",
]
AML_CLASSES = [
    "AML with t(15;17)",
    "AML with t(8;21)",
    "AML with inv(16)/t(16;16)",
    "AML with t(11q23)/MLL",
    "AML complex aberrant karyotype",
    "AML with normal karyotype + other abnormalities",
]
EXPECTED_ALL = 750  # Haferlach ve ark. (2010): ALL alt sınıfları C1–C8 toplamı


def read_metadata() -> pd.DataFrame:
    """Dosyanın başındaki '!Sample_...' satırlarından her hastanın kimliğini, dokusunu ve tanısını alıyoruz."""
    fields = {}
    with gzip.open(MATRIX, "rt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("!series_matrix_table_begin"):
                break
            if not line.startswith("!Sample_"):
                continue
            key, *vals = line.rstrip("\n").split("\t")
            vals = [v.strip('"') for v in vals]
            # "characteristics" satırları "anahtar: değer" biçiminde; anahtarı sütun adı yapıyoruz
            if key == "!Sample_characteristics_ch1":
                key = vals[0].split(":")[0]
                vals = [v.split(": ", 1)[1] for v in vals]
            fields.setdefault(key, vals)
    meta = pd.DataFrame(fields)
    return meta.rename(columns={"!Sample_geo_accession": "gsm", "leukemia class": "subclass",
                                "sample type": "tissue"}).set_index("gsm")


def select_all_aml(meta: pd.DataFrame) -> pd.DataFrame:
    meta = meta[meta["subclass"].isin(ALL_CLASSES + AML_CLASSES)].copy()
    meta["cancer"] = meta["subclass"].map(lambda s: "ALL" if s in ALL_CLASSES else "AML")
    n_all = int((meta["cancer"] == "ALL").sum())
    # Beklediğimiz 750 ALL hastasını bulamazsak sınıf adlarında bir yanlışlık var demektir; burada durduruyoruz
    assert n_all == EXPECTED_ALL, f"ALL sayısı {n_all}, beklenen {EXPECTED_ALL}"
    return meta


def load_mile():
    """MILE'ın ALL/AML hastalarını yüklüyoruz. Dönüş: X (hasta × prob), y (ALL=0, AML=1), meta."""
    meta = select_all_aml(read_metadata())
    if CACHE.exists():
        X = pd.read_pickle(CACHE)
    else:
        # Sadece gereken sütunları okuyoruz; float32 kullanıyoruz ki bellek yarıya insin (~280 MB)
        cols = ["ID_REF"] + list(meta.index)
        X = pd.read_csv(MATRIX, sep="\t", comment="!", usecols=cols, index_col="ID_REF",
                        dtype={c: "float32" for c in meta.index}).T
        PROCESSED.mkdir(parents=True, exist_ok=True)
        X.to_pickle(CACHE)
    X = X.loc[meta.index]  # Etiketleri hasta kimliğine (GSM) göre eşliyoruz, sıraya göre değil
    y = meta["cancer"].map(LABEL_MAP)
    return X, y, meta


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    X, y, meta = load_mile()
    print(X.shape, y.value_counts().to_dict())
    print(meta["subclass"].value_counts())
