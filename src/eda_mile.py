"""EDA 7. adım: MILE verisini tanıyoruz ve Golub ile ortak genleri buluyoruz.

Sorular:
- MILE'da kaç ALL, kaç AML hastası var, alt sınıflara nasıl dağılıyorlar?
- Değerler hangi ölçekte? Ham mı, log mu? (Golub'a uyguladığımız kırpma + log2'yi burada da uygulayabilir miyiz?)
- İki yonganın probları gen sembollerine çevrilince kaç ortak gen kalıyor?
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import skew

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH, PROCESSED, SEED
from src.eda_quality import load_both
from src.gene_mapping import collapse, probe_to_symbol
from src.load_mile import load_mile
from src.plotting import save_fig
from src.preprocess import clip_log2

INV = {0: "ALL", 1: "AML"}
N_BOX = 60  # Kutu grafiğinde 1.292 hastanın hepsi okunmaz; rastgele 60 hasta gösteriyoruz


def plot_subclasses(meta):
    """Alt sınıfların hasta sayıları; ALL alt sınıfları mavi, AML alt sınıfları turuncu."""
    counts = meta.groupby(["cancer", "subclass"]).size().sort_values()
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 2.8))
    colors = [CLASS_COLORS[c] for c, _ in counts.index]
    ax.barh([s for _, s in counts.index], counts.values, color=colors)
    for i, v in enumerate(counts.values):
        ax.text(v + 5, i, str(v), va="center", fontsize=5)
    ax.tick_params(axis="y", labelsize=5)
    ax.set_xlabel("Hasta sayısı")
    ax.set_title("MILE ALL ve AML alt sınıfları")
    ax.set_xlim(0, counts.max() * 1.15)
    fig.tight_layout()
    return save_fig(fig, "fig07a_mile_alt_siniflar")


def plot_scale(X, y):
    """(a) MILE değerlerinin dağılımı, (b) rastgele 60 hastanın kutu grafiği.
    Kutular birebir aynı hizadaysa veri quantile normalize edilmiş demektir."""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH, 1.9), gridspec_kw={"width_ratios": [1, 1.3]})
    bins = np.linspace(0, 1, 50)
    for c in ("ALL", "AML"):
        axes[0].hist(X[y == c].to_numpy().ravel(), bins=bins, density=True, histtype="step",
                     color=CLASS_COLORS[c], lw=1, label=c,
                     ls="-" if c == "ALL" else "--")  # İki eğri tamamen üst üste biniyor; AML kesikli olsun ki ikisi de görünsün
    axes[0].set_xlabel("MILE ifade değeri")
    axes[0].set_ylabel("Yoğunluk")
    axes[0].set_title("(a) Değer dağılımı")
    axes[0].legend(frameon=False)

    rng = np.random.default_rng(SEED)
    idx = rng.choice(len(X), N_BOX, replace=False)
    bp = axes[1].boxplot(X.iloc[idx].to_numpy().T, patch_artist=True, showfliers=False, widths=0.7,
                         medianprops={"color": "black", "lw": 0.5}, whiskerprops={"lw": 0.3},
                         capprops={"lw": 0.3}, boxprops={"lw": 0.3})
    for patch, i in zip(bp["boxes"], idx):
        patch.set_facecolor(CLASS_COLORS[y.iloc[i]])
    axes[1].set_xticks([])
    axes[1].set_xlabel(f"Rastgele {N_BOX} hasta")
    axes[1].set_ylabel("İfade değeri")
    axes[1].set_title("(b) Hasta bazında")
    fig.tight_layout()
    return save_fig(fig, "fig07b_mile_olcek")


def mile_eda() -> dict:
    X, y, meta = load_mile()
    y = y.map(INV)
    out = {"n_total": 2096, "n_all": int((y == "ALL").sum()), "n_aml": int((y == "AML").sum()),
           "n_probes_raw": X.shape[1]}
    out["subclass_counts"] = meta.groupby(["cancer", "subclass"]).size()
    out["tissue_counts"] = meta.groupby(["cancer", "tissue"]).size()

    # Bütün hastalarda boş olan problar var mı? Varsa hangileri?
    all_nan = X.columns[X.isna().all()]
    out["n_all_nan"] = len(all_nan)
    out["all_nan_affx"] = int(all_nan.str.startswith("AFFX").sum())
    X = X.drop(columns=all_nan)
    out["n_nan_left"] = int(X.isna().to_numpy().sum())

    # Ölçek kontrolü
    v = X.to_numpy()
    out["min"], out["max"] = float(v.min()), float(v.max())
    out["n_neg"] = int((v < 0).sum())
    med = np.median(v, axis=1)
    out["sample_median_min"], out["sample_median_max"] = float(med.min()), float(med.max())
    # Her hastanın değerlerini sıralayıp karşılaştırıyoruz: quantile normalizasyonda bu sıralı listeler aynı olur
    s = np.sort(v, axis=1)
    out["sorted_max_diff"] = float(np.abs(s - s.mean(axis=0)).max())
    # Çarpıklık: ham sinyal çok çarpık olur (Golub'da 7,08), log ölçeği simetriğe yakın olur (Golub log2'de 0,55)
    sub = v[np.random.default_rng(SEED).choice(len(v), 200, replace=False)].ravel()
    out["skew"] = float(skew(sub))
    out["skew_after_log"] = float(skew(np.log2(sub + 0.01)))  # Bir kez daha log alsak ne olurdu?
    out["fig_sub"] = plot_subclasses(meta)
    out["fig_scale"] = plot_scale(X, y)

    # Prob → gen eşlemesi
    sym80, st80 = probe_to_symbol("GPL80")
    sym570, st570 = probe_to_symbol("GPL570")
    out["annot80"], out["annot570"] = st80, st570

    Xg, yg, calls, split = load_both()
    Xg = Xg.loc[:, ~Xg.columns.str.startswith("AFFX")]
    Lg = clip_log2(Xg)
    g_genes, gst = collapse(Lg, sym80, ref=Lg[split == "train"])  # Golub'da ortalama sadece eğitimden
    m_genes, mst = collapse(X.loc[:, ~X.columns.str.startswith("AFFX")], sym570, ref=X)
    out["golub_collapse"], out["mile_collapse"] = gst, mst

    common = sorted(set(g_genes.columns) & set(m_genes.columns))
    out["n_common"] = len(common)
    # 8. adımda tekrar okumak için ortak genlerdeki matrisleri kaydediyoruz
    # load_both() etiketleri zaten "ALL"/"AML" yazısı olarak veriyor; tekrar çevirmiyoruz
    g_genes[common].assign(_set=split, _cancer=yg).to_pickle(PROCESSED / "golub_common_genes.pkl")
    assert g_genes.index.equals(yg.index)
    m_genes[common].assign(_cancer=y).to_pickle(PROCESSED / "mile_common_genes.pkl")
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in mile_eda().items():
        print(f"{k}: {v}")
