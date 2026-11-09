"""EDA 6. adım: eğitim ve test setleri arasında batch (teknik) farkı var mı?

Golub'un eğitim ve test hastaları farklı zamanlarda, farklı koşullarda toplanmış. Eğer iki set arasında
teknik bir fark varsa, eğitimde öğrenilen kurallar test setinde aynı şekilde işlemeyebilir.

Dikkat etmemiz gereken bir tuzak var: test setinde AML oranı daha yüksek (eğitimde 11/38, testte 14/34).
İki seti doğrudan karşılaştırırsak sınıf farkını batch farkı sanabiliriz. Bu yüzden en temiz
karşılaştırmayı sadece ALL hastaları arasında (27'ye 20) yapıyoruz.

Test setini burada sadece betimlemek için kullanıyoruz; hiçbir gen ya da parametre seçmiyoruz.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, mannwhitneyu
from sklearn.decomposition import PCA
from statsmodels.stats.multitest import multipletests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH, SEED, SET_COLORS
from src.eda_dimred import prepare
from src.plotting import save_fig

FDR = 0.05
SET_TR = {"train": "Eğitim", "test": "Test"}


def median_center(L: pd.DataFrame) -> pd.DataFrame:
    """Her hastanın değerlerinden o hastanın kendi medyanını çıkarıyoruz.
    Bu, hastalar arasındaki genel ölçek farkını siliyor. Her hasta sadece kendi değerlerine
    bakılarak düzeltildiği için sızıntı yok. Bunu, batch farkının ne kadarının basit bir
    ölçek kayması olduğunu görmek için deniyoruz."""
    return L.sub(L.median(axis=1), axis=0)


def ks_per_gene(L, split, mask) -> pd.DataFrame:
    """Her gen için eğitim ve test dağılımlarını Kolmogorov–Smirnov testiyle karşılaştırıyoruz.
    KS sadece ortalamaya değil, dağılımın bütün şekline bakıyor."""
    a = L[mask & (split == "train")].to_numpy()
    b = L[mask & (split == "test")].to_numpy()
    p = np.array([ks_2samp(a[:, j], b[:, j]).pvalue for j in range(L.shape[1])])
    q = multipletests(p, method="fdr_bh")[1]
    return pd.DataFrame({"p": p, "q": q}, index=L.columns)


def plot_distributions(L, y, split, means):
    """(a) ALL hastalarında eğitim ve test değer dağılımı, (b) hasta ortalamaları set ve sınıfa göre."""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH, 1.9), gridspec_kw={"width_ratios": [1.2, 1]})
    bins = np.linspace(L.to_numpy().min(), L.to_numpy().max(), 50)
    for s in ("train", "test"):
        v = L[(y == "ALL") & (split == s)].to_numpy().ravel()
        axes[0].hist(v, bins=bins, density=True, histtype="step", color=SET_COLORS[s], lw=1, label=SET_TR[s])
    axes[0].set_xlabel("log$_2$ ifade")
    axes[0].set_ylabel("Yoğunluk")
    axes[0].set_title("(a) Yalnız ALL hastaları")
    axes[0].legend(frameon=False)

    groups = [("train", "ALL"), ("test", "ALL"), ("train", "AML"), ("test", "AML")]
    data = [means[(split == s) & (y == c)].to_numpy() for s, c in groups]
    bp = axes[1].boxplot(data, patch_artist=True, widths=0.6, medianprops={"color": "black", "lw": 0.8},
                         flierprops={"markersize": 2})
    for patch, (s, c) in zip(bp["boxes"], groups):
        patch.set_facecolor(CLASS_COLORS[c])
        patch.set_hatch("" if s == "train" else "////")  # Test kutularını taralı çiziyoruz
    axes[1].set_xticks(range(1, 5))
    axes[1].set_xticklabels([f"{SET_TR[s][:3]}.\n{c}" for s, c in groups])
    axes[1].set_ylabel("Hasta ortalaması (log$_2$)")
    axes[1].set_title("(b) Hasta ortalamaları")
    fig.tight_layout()
    return save_fig(fig, "fig06a_batch_dagilim")


def plot_ks(p_raw, p_norm):
    """Batch farkı yoksa p-değerleri 0 ile 1 arasında düz (eşit) dağılır. Sola (0'a) yığılma varsa
    birçok gende eğitim ile test farklı demektir. Medyan düzeltmesinden önce ve sonra karşılaştırıyoruz."""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 1.9))
    bins = np.linspace(0, 1, 21)
    ax.hist(p_raw, bins=bins, histtype="step", color="black", lw=1, label="Ham log$_2$")
    ax.hist(p_norm, bins=bins, histtype="step", color="black", lw=1, ls="--", label="Hasta medyanına göre ortalanmış")
    ax.axhline(len(p_raw) / 20, color="#999999", lw=0.6, ls=":", label="Fark yoksa beklenen")
    ax.set_xlabel("KS testi p-değeri (eğitim vs. test, yalnız ALL)")
    ax.set_ylabel("Gen sayısı")
    ax.set_title("Gen bazında eğitim–test farkı")
    ax.legend(frameon=False, fontsize=6)
    fig.tight_layout()
    return save_fig(fig, "fig06b_ks_pdegerleri")


def batch() -> dict:
    L, y, split = prepare()
    all_mask = y == "ALL"
    means = L.mean(axis=1)
    out = {"n_ALL_train": int((all_mask & (split == "train")).sum()),
           "n_ALL_test": int((all_mask & (split == "test")).sum()),
           "aml_frac_train": 100 * float((y[split == "train"] == "AML").mean()),
           "aml_frac_test": 100 * float((y[split == "test"] == "AML").mean())}

    # 1) Hasta ortalamaları: sınıf karışmasın diye her sınıf içinde ayrı ayrı karşılaştırıyoruz
    for c in ("ALL", "AML"):
        a, b = means[(y == c) & (split == "train")], means[(y == c) & (split == "test")]
        out[f"mean_{c}_train"], out[f"mean_{c}_test"] = float(a.mean()), float(b.mean())
        out[f"mw_p_{c}"] = float(mannwhitneyu(a, b).pvalue)
    out["fig_dist"] = plot_distributions(L, y, split, means)

    # 2) PCA'da set ayrışması, yine sadece ALL hastalarında: hangi bileşen eğitimi testten ayırıyor?
    Z = PCA(random_state=SEED).fit_transform(L[all_mask].to_numpy())
    sp = split[all_mask].to_numpy()
    pv = [mannwhitneyu(Z[sp == "train", i], Z[sp == "test", i]).pvalue for i in range(10)]
    out["pca_all_best_pc"], out["pca_all_best_p"] = int(np.argmin(pv) + 1), float(min(pv))
    # Bu ayrışma hasta ortalamasıyla mı ilgili? Öyleyse sorun basit bir ölçek kayması demektir.
    best = Z[:, int(np.argmin(pv))]
    out["pca_all_best_corr_mean"] = float(np.corrcoef(best, means[all_mask])[0, 1])

    # 3) Gen bazında KS testi. Önce "ifade edilen" genleri seçiyoruz: değerlerinin çoğu 20'ye kırpılmış
    # genler iki sette de aynı sabit değeri taşıyor ve p = 1 çıkıp grafiği bozuyor; bilgi taşımıyorlar.
    # Ölçüt: ALL hastalarının en az yarısında kırpma sınırının üstünde olmak. Hangi sete ait olduğuna
    # bakmadığımız için bu filtre sonucu eğitim ya da test lehine çarpıtmıyor.
    floor = L.to_numpy().min()
    expressed = (L[all_mask] > floor).mean() >= 0.5
    Le = L.loc[:, expressed]
    ks_raw = ks_per_gene(Le, split, all_mask)
    ks_norm = ks_per_gene(median_center(L).loc[:, expressed], split, all_mask)  # Medyanı bütün genlerden alıyoruz
    for name, ks in (("raw", ks_raw), ("norm", ks_norm)):
        out[f"ks_{name}_p05"] = int((ks["p"] < 0.05).sum())
        out[f"ks_{name}_q05"] = int((ks["q"] < FDR).sum())
    out["n_genes"] = L.shape[1]
    out["n_expressed"] = int(expressed.sum())
    out["ks_expected"] = 0.05 * out["n_expressed"]
    out["fig_ks"] = plot_ks(ks_raw["p"], ks_norm["p"])

    # 4) Batch farkı gösteren genler, 5. adımdaki ayırt edici genlerle çakışıyor mu?
    # Çakışıyorsa o genlerle kurulan model test setinde kayabilir.
    from src.config import PROCESSED
    de = pd.read_csv(PROCESSED / "golub_train_welch.csv", index_col=0)
    de_sig = set(de.index[de["q"] < FDR])
    batch_sig = set(ks_raw.index[ks_raw["q"] < FDR])
    out["batch_and_de"] = len(de_sig & batch_sig)
    top50 = set(de.index[:50])
    out["batch_in_top50"] = len(top50 & batch_sig)
    # Hangi genler olduklarını da yazıyoruz ki rapora ismen geçebilelim
    out["batch_top50_genes"] = [f"{g} ({str(de.loc[g, 'description'])[:30]})" for g in sorted(top50 & batch_sig)]
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in batch().items():
        print(f"{k}: {v}")
