"""EDA 3. adım: değerlerin dağılımı ve log dönüşümünün etkisi.

İki soruya bakıyoruz:
1. Ham değerler nasıl dağılıyor, kırpma ve log2'den sonra ne değişiyor?
2. Hastalar arasında genel bir ölçek farkı var mı? Mesela bir hastanın bütün genleri
   ötekilerden sistematik olarak daha yüksek mi? Varsa bu biyolojik değil teknik bir farktır.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from scipy.stats import skew

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH
from src.eda_quality import load_both
from src.plotting import save_fig
from src.preprocess import HIGH, LOW, clip_log2


def plot_hist(X, L, y):
    """Solda ham değerler, sağda kırpılmış ve log2 alınmış değerler."""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH, 1.8))

    # Ham değerler çok geniş bir aralığa yayıldığı için y eksenini log ölçekte çiziyoruz;
    # yoksa sıfır civarındaki dev tepe dışında hiçbir şey görünmüyor.
    raw = X.to_numpy().ravel()
    axes[0].hist(raw, bins=200, color="#777777")
    axes[0].set_yscale("log")
    axes[0].axvline(LOW, color="red", lw=0.6, ls="--")
    axes[0].axvline(HIGH, color="red", lw=0.6, ls="--")
    axes[0].set_xlabel("Ham ifade değeri")
    axes[0].set_ylabel("Değer sayısı (log)")
    axes[0].set_title("(a) Ham")

    # Log2 sonrası her sınıfı kendi renginde çiziyoruz. Yoğunluk kullanıyoruz ki
    # ALL'ın hasta sayısı fazla diye eğrisi daha büyük görünmesin.
    bins = np.linspace(np.log2(LOW), np.log2(HIGH), 50)
    for c in ("ALL", "AML"):
        axes[1].hist(L[y == c].to_numpy().ravel(), bins=bins, density=True, histtype="step",
                     color=CLASS_COLORS[c], lw=1, label=c)
    axes[1].set_xlabel("log$_2$(kırpılmış değer)")
    axes[1].set_ylabel("Yoğunluk")
    axes[1].set_title("(b) Kırpma + log$_2$")
    axes[1].legend(frameon=False)
    fig.tight_layout()
    return save_fig(fig, "fig03a_dagilim_ham_log")


def plot_box(L, y, split):
    """Her hasta için bir kutu: kutuların yükseklikleri hizalıysa hastalar arasında ölçek farkı yok demektir."""
    # Hastaları önce sete, sonra numaraya göre diziyoruz ki eğitim ve test yan yana görülsün
    order = list(L.index[split == "train"]) + list(L.index[split == "test"])
    data = [L.loc[i].to_numpy() for i in order]

    fig, ax = plt.subplots(figsize=(FIG_WIDTH * 2, 2.2))  # 72 kutu tek sütuna sığmıyor, iki sütun genişliğinde çiziyoruz
    bp = ax.boxplot(data, patch_artist=True, showfliers=False, widths=0.7,
                    medianprops={"color": "black", "lw": 0.6}, whiskerprops={"lw": 0.4},
                    capprops={"lw": 0.4}, boxprops={"lw": 0.4})
    for patch, i in zip(bp["boxes"], order):
        patch.set_facecolor(CLASS_COLORS[y[i]])

    n_train = int((split == "train").sum())
    ax.axvline(n_train + 0.5, color="black", lw=0.8, ls="--")  # Eğitim ile testi ayıran çizgi
    ax.text(n_train / 2, ax.get_ylim()[1], "Eğitim", ha="center", va="bottom")
    ax.text(n_train + (len(order) - n_train) / 2, ax.get_ylim()[1], "Test", ha="center", va="bottom")
    ax.set_xticks(range(1, len(order) + 1))
    ax.set_xticklabels(order, fontsize=5, rotation=90)
    ax.set_xlabel("Hasta numarası")
    ax.set_ylabel("log$_2$(kırpılmış değer)")
    ax.legend(handles=[Patch(color=CLASS_COLORS[c], label=c) for c in ("ALL", "AML")],
              loc="lower right", bbox_to_anchor=(1, 1.06), ncol=2, frameon=False)  # Kutuların üstüne binmesin diye çerçevenin dışına
    fig.tight_layout()
    return save_fig(fig, "fig03b_ornek_kutu")


def distribution() -> dict:
    X, y, calls, split = load_both()
    L = clip_log2(X)

    out = {"fig_hist": plot_hist(X, L, y), "fig_box": plot_box(L, y, split)}

    # Çarpıklık: 0'a ne kadar yakınsa dağılım o kadar simetrik. Log dönüşümünün etkisini bununla ölçüyoruz.
    out["skew_raw"] = float(skew(X.to_numpy().ravel()))
    out["skew_log"] = float(skew(L.to_numpy().ravel()))
    out["clipped_low_pct"] = 100 * float((X < LOW).to_numpy().mean())
    out["clipped_high_pct"] = 100 * float((X > HIGH).to_numpy().mean())

    # Hasta bazında ölçek farkı: her hastanın ortalamasına ve medyanına bakıyoruz.
    # Ham ölçekteki fark, "en yüksek hasta ortalaması en düşüğün kaç katı" diye ifade ediliyor.
    raw_mean = X.mean(axis=1)
    out["raw_mean_min"], out["raw_mean_max"] = float(raw_mean.min()), float(raw_mean.max())
    out["raw_mean_ratio"] = float(raw_mean.max() / raw_mean.min())
    out["raw_mean_min_id"], out["raw_mean_max_id"] = int(raw_mean.idxmin()), int(raw_mean.idxmax())

    med = L.median(axis=1)
    mean = L.mean(axis=1)
    out["log_median_min"], out["log_median_max"] = float(med.min()), float(med.max())
    out["log_mean_min"], out["log_mean_max"] = float(mean.min()), float(mean.max())
    # log2'de 1 birim fark = 2 kat fark. Ortalamalar arasındaki en büyük farkı kat olarak da veriyoruz.
    out["log_mean_fold"] = float(2 ** (mean.max() - mean.min()))
    for s in ("train", "test"):
        out[f"log_mean_{s}"] = float(mean[split == s].mean())
    for c in ("ALL", "AML"):
        out[f"log_mean_{c}"] = float(mean[y == c].mean())
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in distribution().items():
        print(f"{k}: {v}")
