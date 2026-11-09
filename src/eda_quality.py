"""EDA 2. adım: veri kalitesi.

Burada şu sorulara cevap arıyoruz:
- Veride eksik (NaN) ya da sonsuz (INF) değer var mı?
- Negatif değer ne kadar var? (Bir genin ifadesi negatif olamaz; bu, ölçüm cihazının arka plan
  sinyalini çıkarırken ortaya çıkan bir şey.)
- Çok küçük ve çok büyük uç değerler ne kadar?
- P/A/M çağrıları setlere ve sınıflara göre nasıl dağılıyor?
- Hiçbir hastada "Present" çıkmayan, yani hiç ifade edilmeyen kaç prob var?
- AFFX ile başlayan kontrol probları ayrıca nasıl davranıyor?
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH
from src.load_golub import load_split
from src.plotting import save_fig

# Dudoit ve ark. (2002) bu iki sınırı kullanıyor: 20'nin altı gürültü, 16.000'in üstü cihazın doyduğu bölge
LOW, HIGH = 20, 16000
INV = {0: "ALL", 1: "AML"}


def load_both():
    """İki seti de yükleyip tek tabloda birleştiriyoruz; hangi satırın hangi setten geldiğini de not ediyoruz."""
    parts = {s: load_split(s) for s in ("train", "test")}
    X = pd.concat([parts[s][0] for s in parts])
    y = pd.concat([parts[s][1] for s in parts]).map(INV)
    calls = pd.concat([parts[s][2] for s in parts])
    split = pd.Series([s for s in parts for _ in range(len(parts[s][0]))], index=X.index)
    return X, y, calls, split


def value_stats(X: pd.DataFrame) -> dict:
    """Bir tablo için eksik, negatif ve uç değer sayılarını çıkarıyoruz."""
    v = X.to_numpy(dtype=float)
    n = v.size
    return {
        "n_values": n,
        "n_nan": int(np.isnan(v).sum()),
        "n_inf": int(np.isinf(v).sum()),
        "neg_pct": 100 * (v < 0).sum() / n,
        "below_low_pct": 100 * (v < LOW).sum() / n,
        "above_high_pct": 100 * (v > HIGH).sum() / n,
        "min": int(v.min()),
        "max": int(v.max()),
        "median": float(np.median(v)),
    }


def call_table(calls: pd.DataFrame, y: pd.Series, split: pd.Series) -> pd.DataFrame:
    """Her set ve sınıf grubu için P, A ve M yüzdelerini hesaplıyoruz."""
    rows = {}
    for (s, c), idx in calls.groupby([split, y]).groups.items():
        counts = calls.loc[idx].stack().value_counts()
        rows[(s, c)] = 100 * counts / counts.sum()
    return pd.DataFrame(rows).T.reindex(columns=["P", "M", "A"]).fillna(0)


def plot_calls(tab: pd.DataFrame):
    """P/A/M oranlarını yığılmış çubuk grafikle gösteriyoruz; her çubuk bir set ve sınıf grubu."""
    order = [("train", "ALL"), ("train", "AML"), ("test", "ALL"), ("test", "AML")]
    tab = tab.loc[order]
    names = {"train": "Eğitim", "test": "Test"}
    labels = [f"{names[s]}\n{c}" for s, c in order]
    # P/M/A için sınıf renklerinden bağımsız gri tonlar kullanıyoruz, karışıklık olmasın
    shades = {"P": "#333333", "M": "#999999", "A": "#dddddd"}
    names_call = {"P": "Present (P)", "M": "Marginal (M)", "A": "Absent (A)"}

    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 2.2))
    bottom = np.zeros(len(tab))
    for k in ["P", "M", "A"]:
        ax.bar(labels, tab[k], bottom=bottom, color=shades[k], edgecolor="black", linewidth=0.4,
               label=names_call[k])
        bottom += tab[k].to_numpy()
    # Sınıf adlarını sınıf renkleriyle boyuyoruz ki diğer şekillerle uyumlu dursun
    for tick, (_, c) in zip(ax.get_xticklabels(), order):
        tick.set_color(CLASS_COLORS[c])
    ax.set_ylabel("Çağrı oranı (%)")
    ax.set_title("Set ve sınıfa göre P/M/A çağrı dağılımı")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=3, frameon=False)
    return save_fig(fig, "fig02_pma_dagilimi")


def quality() -> dict:
    X, y, calls, split = load_both()
    affx = X.columns.str.startswith("AFFX")
    out = {"fig": plot_calls(call_table(calls, y, split)),
           "call_table": call_table(calls, y, split)}

    # Değer istatistiklerini her set için ayrı, bir de kontrol probları için ayrı çıkarıyoruz
    for s in ("train", "test"):
        out[f"vals_{s}"] = value_stats(X.loc[split == s])
    out["vals_all"] = value_stats(X)
    out["vals_affx"] = value_stats(X.loc[:, affx])
    out["vals_genes"] = value_stats(X.loc[:, ~affx])

    # Hiçbir hastada Present çıkmamış problar. Bunları sadece betimlemek için sayıyoruz;
    # silme kararını modelleme aşamasında, eğitim katlarının içinde vereceğiz ki sızıntı olmasın.
    is_p = calls.eq("P")
    out["never_P_all"] = int((~is_p.any()).sum())
    out["never_P_train"] = int((~is_p.loc[split == "train"].any()).sum())
    out["never_P_affx"] = int((~is_p.loc[:, affx].any()).sum())

    # Negatif değerlerin hepsi Absent mı? Öyleyse negatiflik gerçekten "ölçülemeyecek kadar düşük" demek.
    neg = X < 0
    out["neg_call_dist"] = (100 * calls[neg].stack().value_counts(normalize=True)).round(2).to_dict()

    out["n_probes"] = X.shape[1]
    out["n_affx"] = int(affx.sum())
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in quality().items():
        print(f"{k}: {v}")
