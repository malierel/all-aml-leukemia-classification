"""EDA 4. adım: boyut indirgeme (PCA, t-SNE, UMAP).

7.129 boyutlu veriyi 2 boyuta indirip hastaları düzlemde görmeye çalışıyoruz. Sorduğumuz şey:
sınıf bilgisini hiç vermeden ALL ve AML kendiliğinden ayrı gruplara düşüyor mu?
Bir de eğitim ve test hastaları ayrı yerlerde toplanıyor mu (yani batch farkı var mı)?

Bu adımda 72 hastanın hepsini kullanıyoruz. Burada model kurmuyoruz, sadece veriye bakıyoruz.
Bu yöntemler etiketi hiç görmüyor; o yüzden test setini burada kullanmak sızıntı sayılmaz.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy.stats import mannwhitneyu
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH, SEED, SET_COLORS
from src.eda_quality import load_both
from src.plotting import save_fig
from src.preprocess import clip_log2

MARKERS = {"train": "o", "test": "^"}  # Eğitim hastaları daire, test hastaları üçgen
SET_TR = {"train": "Eğitim", "test": "Test"}
N_PCS = 20  # Varyans grafiğinde ilk 20 bileşeni gösteriyoruz; sonrası zaten çok küçük


def prepare():
    """Veriyi yükleyip kırpıyor, log alıyor ve AFFX kontrol problarını çıkarıyoruz.
    AFFX'ler gen değil, yonganın kendi kontrol probları; hastaları gruplamaya katkıları olmamalı."""
    X, y, calls, split = load_both()
    L = clip_log2(X)
    L = L.loc[:, ~L.columns.str.startswith("AFFX")]
    return L, y, split


def scatter(ax, Z, y, split, color_by: str):
    """İki boyutlu noktaları çiziyoruz. Renk ya sınıfı ya seti gösteriyor; şekil her zaman seti."""
    for s in ("train", "test"):
        for c in ("ALL", "AML"):
            m = ((split == s) & (y == c)).to_numpy()
            color = CLASS_COLORS[c] if color_by == "class" else SET_COLORS[s]
            ax.scatter(Z[m, 0], Z[m, 1], c=color, marker=MARKERS[s], s=12,
                       edgecolors="black", linewidths=0.3)


def legend(fig, set_colors: bool):
    """Bütün şekil için tek bir lejantı en alta koyuyoruz; böylece noktaların ya da eksen yazılarının
    üstüne binmiyor. Kareler sınıfı, daire ve üçgen seti gösteriyor."""
    h = [Line2D([], [], ls="", marker="s", color=CLASS_COLORS[c], label=c) for c in ("ALL", "AML")]
    h += [Line2D([], [], ls="", marker=MARKERS[s], mfc=SET_COLORS[s] if set_colors else "white",
                 mec="black", label=SET_TR[s]) for s in ("train", "test")]
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.33)  # Lejanta altta yer açıyoruz
    fig.legend(handles=h, frameon=False, fontsize=6, handletextpad=0.2, columnspacing=1.2,
               loc="lower center", ncol=len(h))


def plot_variance(pca):
    ratio = 100 * pca.explained_variance_ratio_[:N_PCS]
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 1.9))
    k = np.arange(1, N_PCS + 1)
    ax.bar(k, ratio, color="#777777", label="Tek bileşen")
    ax.plot(k, np.cumsum(ratio), color="black", marker="o", ms=2, lw=0.8, label="Kümülatif")
    ax.set_xlabel("Temel bileşen")
    ax.set_ylabel("Açıklanan varyans (%)")
    ax.set_title("PCA açıklanan varyans")
    ax.set_xticks(k[::2] + 0)
    ax.legend(frameon=False)
    fig.tight_layout()
    return save_fig(fig, "fig04a_pca_varyans")


def plot_pca(Z, pca, y, split):
    """Aynı PC1–PC2 düzlemini iki kez çiziyoruz: solda sınıfa göre, sağda sete göre renkli."""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH, 1.9), sharex=True, sharey=True)
    r = 100 * pca.explained_variance_ratio_
    for ax, by, title in zip(axes, ("class", "set"), ("(a) Sınıfa göre", "(b) Sete göre")):
        scatter(ax, Z, y, split, by)
        ax.set_title(title)
        ax.set_xlabel(f"PC1 (%{r[0]:.1f})")
    axes[0].set_ylabel(f"PC2 (%{r[1]:.1f})")
    legend(fig, set_colors=True)  # Sağ paneldeki gri/yeşil renkler lejantta da görünsün
    return save_fig(fig, "fig04b_pca_pc1_pc2")


def plot_embed(T, U, y, split):
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH, 1.9))
    for ax, Z, title in zip(axes, (T, U), ("(a) t-SNE", "(b) UMAP")):
        scatter(ax, Z, y, split, "class")
        ax.set_title(title)
        ax.set_xticks([])  # Bu yöntemlerde eksen değerlerinin bir anlamı yok, o yüzden göstermiyoruz
        ax.set_yticks([])
        ax.set_xlabel("Boyut 1")
    axes[0].set_ylabel("Boyut 2")
    legend(fig, set_colors=False)
    return save_fig(fig, "fig04c_tsne_umap")


def dimred() -> dict:
    L, y, split = prepare()
    # PCA'yı ölçeklemeden, sadece ortalamayı çıkararak yapıyoruz. Log2 sonrası bütün genler zaten
    # aynı birimde; ölçekleseydik gürültü düzeyindeki genler de önemli genler kadar ağırlık kazanırdı.
    pca = PCA(random_state=SEED)
    Z = pca.fit_transform(L.to_numpy())
    cum = np.cumsum(pca.explained_variance_ratio_)

    out = {"n_genes": L.shape[1],
           "fig_var": plot_variance(pca),
           "fig_pca": plot_pca(Z, pca, y, split)}
    out["pc_var"] = [100 * v for v in pca.explained_variance_ratio_[:5]]
    for t in (50, 80, 90):
        out[f"n_pc_{t}"] = int(np.searchsorted(cum, t / 100) + 1)  # Bu orana ulaşmak için kaç bileşen gerekiyor

    # İlk 10 bileşenden hangisi ALL ile AML'yi en iyi ayırıyor? Her bileşen için iki sınıfın
    # değerlerini Mann–Whitney testiyle karşılaştırıyoruz. Bu sadece betimleme; gen seçmek için kullanmıyoruz.
    pvals = [mannwhitneyu(Z[(y == "ALL").to_numpy(), i], Z[(y == "AML").to_numpy(), i]).pvalue for i in range(10)]
    out["best_pc_class"] = int(np.argmin(pvals) + 1)
    out["best_pc_class_p"] = float(min(pvals))
    pvals_set = [mannwhitneyu(Z[(split == "train").to_numpy(), i], Z[(split == "test").to_numpy(), i]).pvalue
                 for i in range(10)]
    out["best_pc_set"] = int(np.argmin(pvals_set) + 1)
    out["best_pc_set_p"] = float(min(pvals_set))

    # t-SNE ve UMAP: 72 hasta az olduğu için komşu sayısını küçük tutuyoruz (varsayılan 30 bu veri için fazla).
    # İkisine de önce PCA'nın ilk 50 bileşenini veriyoruz; gürültüyü azaltıyor ve yaygın bir uygulama.
    Z50 = Z[:, :50]
    T = TSNE(n_components=2, perplexity=15, random_state=SEED, init="pca").fit_transform(Z50)
    import umap  # Yüklenmesi yavaş olduğu için sadece burada çağırıyoruz
    U = umap.UMAP(n_neighbors=15, min_dist=0.3, random_state=SEED).fit_transform(Z50)
    out["fig_embed"] = plot_embed(T, U, y, split)

    # Siluet skoru: noktalar kendi grubuna ne kadar yakın, öteki gruptan ne kadar uzak?
    # 1'e yakınsa gruplar net ayrık, 0 civarındaysa iç içe. Sınıf ve set için ayrı ayrı hesaplıyoruz.
    for name, E in (("pca2", Z[:, :2]), ("tsne", T), ("umap", U)):
        out[f"sil_class_{name}"] = float(silhouette_score(E, y))
        out[f"sil_set_{name}"] = float(silhouette_score(E, split))
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in dimred().items():
        print(f"{k}: {v}")
