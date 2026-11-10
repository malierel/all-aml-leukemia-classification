"""EDA 8. adım: Golub ile MILE'ı ortak genler üzerinden karşılaştırıyoruz.

Sorular:
1. İki veri setinin değerleri aynı ölçekte mi? (7. adımda öyle olmadığını gördük; burada ne kadar farklı olduklarına bakıyoruz.)
2. İki seti doğrudan birleştirip PCA yaparsak ne olur? Her geni kendi veri seti içinde ölçeklersek ne değişir?
3. ALL/AML ayrımı her iki veri setinde de görülüyor mu?
4. Golub'da ALL ile AML arasında farklı bulduğumuz genler MILE'da da AYNI YÖNDE farklı mı?
   Bu, Golub'da öğrenilen bir modelin MILE'a aktarılabilir olup olmadığına dair en önemli ipucu.

Golub'da ayırt edici genleri yine SADECE eğitim setinden buluyoruz. MILE ise tamamen bağımsız bir veri seti;
onu bu karşılaştırmada kullanmak Golub modeline sızıntı yaratmıyor.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.stats import mannwhitneyu, spearmanr, ttest_ind
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from statsmodels.stats.multitest import multipletests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH, PROCESSED, SEED
from src.plotting import save_fig

FDR = 0.05
TOP = 50
DS_COLORS = {"Golub": "#7b3294", "MILE": "#999999"}  # Veri seti renkleri; sınıf renkleriyle karışmasın diye mor/gri
DS_MARKERS = {"Golub": "*", "MILE": "o"}


def load_common():
    g = pd.read_pickle(PROCESSED / "golub_common_genes.pkl")
    m = pd.read_pickle(PROCESSED / "mile_common_genes.pkl")
    g_set, g_y = g.pop("_set"), g.pop("_cancer")
    m_y = m.pop("_cancer")
    return g, g_y, g_set, m, m_y


def zscore_genes(X: pd.DataFrame) -> pd.DataFrame:
    """Her geni kendi veri seti içinde ortalaması 0, standart sapması 1 olacak şekilde ölçekliyoruz.
    Böylece Golub'un log2 ölçeği ile MILE'ın 0–1 ölçeği arasındaki fark ortadan kalkıyor; geriye
    sadece "bu hasta, bu gende, kendi veri setinin ortalamasına göre ne kadar yüksek" bilgisi kalıyor.
    Sabit genlerde bölme hatası olmasın diye standart sapma 0 ise 1 alıyoruz."""
    sd = X.std().replace(0, 1)
    return (X - X.mean()) / sd


def welch(X, y):
    """Her gen için AML − ALL farkını Welch t-testiyle ölçüyoruz (5. adımdaki yöntemin aynısı)."""
    a, b = X[y == "ALL"], X[y == "AML"]
    t, p = ttest_ind(b, a, equal_var=False)
    # İki sınıfta da tamamen sabit olan genlerde gerçek bir fark yok. Yuvarlama hatası sahte bir t
    # üretmesin diye bunları elle "fark yok" (t = 0, p = 1) yapıyoruz (5. adımdaki uyarının aynısı).
    const = ((a.max() == a.min()) & (b.max() == b.min())).to_numpy()
    t, p = np.where(const, 0.0, np.nan_to_num(t)), np.where(const, 1.0, np.nan_to_num(p, nan=1.0))
    return pd.DataFrame({"t": t, "p": p, "q": multipletests(p, method="fdr_bh")[1],
                         "diff": b.mean() - a.mean()}, index=X.columns)


def plot_scales(g, m):
    """(a)-(b) İki veri setinin değer dağılımları kendi ölçeklerinde, (c) gen ortalamalarının karşılaştırması."""
    fig, axes = plt.subplots(1, 3, figsize=(FIG_WIDTH * 2, 1.9))
    axes[0].hist(g.to_numpy().ravel(), bins=50, density=True, color=DS_COLORS["Golub"])
    axes[0].set_xlabel("log$_2$(kırpılmış değer)")
    axes[0].set_title("(a) Golub")
    axes[1].hist(m.to_numpy().ravel(), bins=50, density=True, color=DS_COLORS["MILE"])
    axes[1].set_xlabel("MILE değeri (0–1)")
    axes[1].set_title("(b) MILE")
    for ax in axes[:2]:
        ax.set_ylabel("Yoğunluk")
    # Bir gen Golub'da yüksek ifade ediliyorsa MILE'da da yüksek mi? Ölçekler farklı olsa da sıralama tutarlı olmalı.
    gm, mm = g.mean(), m.mean()
    rho = spearmanr(gm, mm).statistic
    axes[2].scatter(gm, mm, s=1, c="black", alpha=0.3, lw=0)
    axes[2].set_xlabel("Golub gen ortalaması (log$_2$)")
    axes[2].set_ylabel("MILE gen ortalaması")
    axes[2].set_title(f"(c) Gen ortalamaları (Spearman ρ = {rho:.2f})")
    fig.tight_layout()
    return save_fig(fig, "fig08a_golub_mile_olcek"), float(rho)


def scatter(ax, Z, ds, y, color_by):
    # Önce MILE'ı, sonra Golub'u çiziyoruz ki az sayıdaki Golub hastası MILE'ın altında kaybolmasın
    for d in ("MILE", "Golub"):
        for c in ("ALL", "AML"):
            mk = ((ds == d) & (y == c)).to_numpy()
            color = CLASS_COLORS[c] if color_by == "class" else DS_COLORS[d]
            ax.scatter(Z[mk, 0], Z[mk, 1], c=color, marker=DS_MARKERS[d],
                       s=30 if d == "Golub" else 4, lw=0.3 if d == "Golub" else 0,
                       edgecolors="black", alpha=1 if d == "Golub" else 0.5)


def plot_pca(Z_raw, Z_z, pca_raw, pca_z, ds, y):
    # Rapor sütununa sığsın diye iki panel: solda ham birleştirme (veri setine göre renkli),
    # sağda z-skor sonrası (sınıfa göre renkli; yıldız/daire hangi veri setinden geldiğini gösteriyor)
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH, 2.1))
    panels = [(Z_raw, pca_raw, "dataset", "(a) Ham birleştirme"),
              (Z_z, pca_z, "class", "(b) Veri seti içi z-skor")]
    for ax, (Z, pca, by, title) in zip(axes, panels):
        scatter(ax, Z, ds, y, by)
        r = 100 * pca.explained_variance_ratio_
        ax.set_xlabel(f"PC1 (%{r[0]:.1f})")
        ax.set_ylabel(f"PC2 (%{r[1]:.1f})")
        ax.set_title(title)
    h = [Line2D([], [], ls="", marker="s", color=DS_COLORS[d], label=d) for d in ("Golub", "MILE")]
    h += [Line2D([], [], ls="", marker="s", color=CLASS_COLORS[c], label=c) for c in ("ALL", "AML")]
    h += [Line2D([], [], ls="", marker=DS_MARKERS[d], mfc="white", mec="black", label=f"{d} hastası")
          for d in ("Golub", "MILE")]
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.36)  # Lejant iki satır olacağı için altta biraz daha yer açıyoruz
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=6, columnspacing=0.8)
    return save_fig(fig, "fig08b_birlesik_pca")


def plot_direction(dg, dm, sig):
    """Her nokta bir gen: x = Golub eğitim setindeki t, y = MILE'daki t. Sağ üst ve sol alt köşeler
    'iki veri setinde aynı yönde' demek. Golub'da anlamlı genleri sınıf rengine boyuyoruz."""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 2.4))
    ax.scatter(dg.loc[~sig, "t"], dm.loc[~sig, "t"], s=1, c="#cccccc", lw=0, label="Golub'da anlamlı değil")
    for c, mk in (("AML", dg["t"] > 0), ("ALL", dg["t"] < 0)):
        k = sig & mk
        ax.scatter(dg.loc[k, "t"], dm.loc[k, "t"], s=2, c=CLASS_COLORS[c], lw=0,
                   label=f"Golub'da {c}'de anlamlı yüksek")
    ax.axhline(0, color="black", lw=0.4)
    ax.axvline(0, color="black", lw=0.4)
    rho = spearmanr(dg["t"], dm["t"]).statistic
    ax.set_xlabel("Golub eğitim t istatistiği (AML − ALL)")
    ax.set_ylabel("MILE t istatistiği (AML − ALL)")
    ax.set_title(f"Ayırt edici genlerin yön tutarlılığı (ρ = {rho:.2f})")
    ax.legend(frameon=False, markerscale=4, fontsize=6, loc="upper left")
    fig.tight_layout()
    return save_fig(fig, "fig08c_yon_tutarliligi"), float(rho)


def compare() -> dict:
    g, g_y, g_set, m, m_y = load_common()
    out = {"n_common": g.shape[1], "n_golub": len(g), "n_mile": len(m)}
    out["fig_scale"], out["rho_means"] = plot_scales(g, m)

    # Birleşik PCA: önce ölçekleri hiç düzeltmeden, sonra her geni kendi veri seti içinde z-skorlayarak
    ds = pd.Series(["Golub"] * len(g) + ["MILE"] * len(m))
    y = pd.concat([g_y, m_y]).reset_index(drop=True)
    raw = pd.concat([g, m]).to_numpy()
    zz = pd.concat([zscore_genes(g), zscore_genes(m)]).to_numpy()
    pca_raw, pca_z = PCA(n_components=10, random_state=SEED), PCA(n_components=10, random_state=SEED)
    Z_raw, Z_z = pca_raw.fit_transform(raw), pca_z.fit_transform(zz)
    out["fig_pca"] = plot_pca(Z_raw, Z_z, pca_raw, pca_z, ds, y)
    for name, Z, pca in (("raw", Z_raw, pca_raw), ("z", Z_z, pca_z)):
        out[f"pc1_{name}"] = 100 * float(pca.explained_variance_ratio_[0])
        out[f"sil_ds_{name}"] = float(silhouette_score(Z[:, :2], ds))
        out[f"sil_class_{name}"] = float(silhouette_score(Z[:, :2], y))
    # z-skorlu birleşik PCA'da sınıfları en iyi ayıran bileşen, iki veri setinde ayrı ayrı ve aynı yönde mi?
    pv = [mannwhitneyu(Z_z[(y == "ALL").to_numpy(), i], Z_z[(y == "AML").to_numpy(), i]).pvalue for i in range(10)]
    best = int(np.argmin(pv))
    out["z_best_pc"] = best + 1
    for d in ("Golub", "MILE"):
        k = (ds == d).to_numpy()
        a = Z_z[k & (y == "ALL").to_numpy(), best]
        b = Z_z[k & (y == "AML").to_numpy(), best]
        out[f"z_best_pc_{d}_diff"] = float(np.median(b) - np.median(a))  # AML medyanı − ALL medyanı
        out[f"z_best_pc_{d}_p"] = float(mannwhitneyu(a, b).pvalue)

    # Her veri setinin kendi PCA'sında ALL/AML ne kadar ayrık? (Ortak genlerle, kendi ölçeğinde)
    for d, X, yy in (("Golub", g, g_y), ("MILE", m, m_y)):
        Zd = PCA(n_components=2, random_state=SEED).fit_transform(X.to_numpy())
        out[f"sil_class_own_{d}"] = float(silhouette_score(Zd, yy))

    # Yön tutarlılığı: Golub'da yalnız EĞİTİM setinde ayırt edici genler, MILE'da da aynı yönde mi?
    tr = (g_set == "train").to_numpy()
    dg = welch(g[tr], g_y[tr])
    dm = welch(m, m_y)
    sig = dg["q"] < FDR
    same = np.sign(dg["t"]) == np.sign(dm["t"])
    out["golub_sig"] = int(sig.sum())
    out["same_dir_all"] = 100 * float(same.mean())  # Bütün ortak genlerde aynı yön oranı (kıyas için)
    out["same_dir_sig"] = 100 * float(same[sig].mean())
    out["same_dir_sig_mile_sig"] = int((sig & same & (dm["q"] < FDR)).sum())
    out["opp_dir_sig_mile_sig"] = int((sig & ~same & (dm["q"] < FDR)).sum())
    top = dg.nsmallest(TOP, "p").index
    out["top_same_dir"] = int(same[top].sum())
    out["top_same_dir_mile_sig"] = int((same[top] & (dm.loc[top, "q"] < FDR)).sum())
    out["top_opposite"] = [f"{gname} (Golub t={dg.loc[gname, 't']:.1f}, MILE t={dm.loc[gname, 't']:.1f})"
                           for gname in top if not same[gname]]
    out["mile_sig"] = int((dm["q"] < FDR).sum())
    out["fig_dir"], out["rho_t"] = plot_direction(dg, dm, sig)
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in compare().items():
        print(f"{k}: {v}")
