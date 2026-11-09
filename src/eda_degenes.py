"""EDA 5. adım: ALL ile AML arasında ifadesi farklı olan genleri buluyoruz.

ÖNEMLİ: Bu analizde SADECE eğitim setini (38 hasta) kullanıyoruz. Test setini burada kullanırsak
genleri test hastalarına bakarak seçmiş oluruz; o zaman test seti artık "hiç görülmemiş veri" olmaz.
Literatürde %100 doğruluk bildiren birçok çalışmanın düştüğü hata tam olarak bu.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import fcluster
from scipy.stats import ttest_ind
from sklearn.metrics import adjusted_rand_score
from statsmodels.stats.multitest import multipletests

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import CLASS_COLORS, FIG_WIDTH, PROCESSED
from src.load_golub import load_split
from src.plotting import save_fig
from src.preprocess import clip_log2

FDR = 0.05     # Yanlış keşif oranı eşiği: "anlamlı" dediğimiz genlerin en fazla %5'i şans eseri olabilir
FC = 1.0       # log2 farkı 1 = iki kat fark; volcano grafiğinde "büyük fark" sınırı olarak kullanıyoruz
TOP = 50       # Isı haritasında gösterilecek gen sayısı (Golub da 50 gen kullanmıştı)
INV = {0: "ALL", 1: "AML"}


def load_train():
    X, y, _, gene_info = load_split("train")
    L = clip_log2(X)
    L = L.loc[:, ~L.columns.str.startswith("AFFX")]  # Kontrol problarını yine dışarıda bırakıyoruz
    names = gene_info.set_index("Gene Accession Number")["Gene Description"]
    return L, y.map(INV), names


def welch(L: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Her gen için iki sınıfın ortalamalarını Welch t-testiyle karşılaştırıyoruz.

    Neden Welch? Normal t-testi iki sınıfın varyansının eşit olduğunu varsayıyor. Burada ALL'da 27,
    AML'de 11 hasta var ve varyanslar da farklı olabilir; Welch bu varsayımı yapmıyor.
    """
    a, b = L[y == "ALL"], L[y == "AML"]
    # Her iki sınıfta da bütün değerleri 20'ye kırpılmış genler tamamen sabit; aslında hiç fark yok.
    # Bunları testten çıkarıp sayılarını ayrıca raporluyoruz.
    # Dikkat: "std() == 0" diye kontrol etmek işe yaramıyor. Bilgisayardaki yuvarlama yüzünden sabit
    # bir sütunun standart sapması tam 0 değil, çok küçük bir sayı çıkıyor; t-testi de bunu sahte bir
    # büyük farka (t ≈ -5,1) çeviriyordu. O yüzden "en büyük değer = en küçük değer" diye bakıyoruz.
    const = (a.max() == a.min()) & (b.max() == b.min())
    a, b = a.loc[:, ~const], b.loc[:, ~const]

    t, p = ttest_ind(b, a, equal_var=False)  # AML - ALL: pozitif t "AML'de daha yüksek" demek
    # 7 binden fazla gen test ediyoruz. Hiç fark olmasa bile %5 eşikle ~350 gen şans eseri anlamlı çıkardı.
    # Benjamini–Hochberg düzeltmesi bu şans eseri bulguları kontrol altında tutuyor.
    q = multipletests(p, method="fdr_bh")[1]
    res = pd.DataFrame({"t": t, "p": p, "q": q,
                        "log2fc": b.mean() - a.mean(),  # log ölçekte ortalama farkı = kat farkının logu
                        "mean_ALL": a.mean(), "mean_AML": b.mean()}, index=a.columns)
    res.attrs["n_const"] = int(const.sum())
    return res.sort_values("p")


def plot_volcano(res: pd.DataFrame):
    """x ekseni farkın büyüklüğü, y ekseni ne kadar güvenilir olduğu. Sağ ve sol üst köşeler en ilginç genler."""
    sig = res["q"] < FDR
    big = sig & (res["log2fc"].abs() >= FC)
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, 2.4))
    y = -np.log10(res["p"])
    ax.scatter(res.loc[~sig, "log2fc"], y[~sig], s=2, c="#bbbbbb", lw=0, label=f"q ≥ {FDR}")
    ax.scatter(res.loc[sig & ~big, "log2fc"], y[sig & ~big], s=2, c="#555555", lw=0,
               label=f"q < {FDR}, |log$_2$FC| < {FC:g}")
    # Büyük ve anlamlı farkları, hangi sınıfta yüksekse o sınıfın rengine boyuyoruz
    for c, m in (("AML", res["log2fc"] > 0), ("ALL", res["log2fc"] < 0)):
        ax.scatter(res.loc[big & m, "log2fc"], y[big & m], s=3, c=CLASS_COLORS[c], lw=0,
                   label=f"{c}'de yüksek")
    ax.axvline(FC, color="black", lw=0.5, ls="--")
    ax.axvline(-FC, color="black", lw=0.5, ls="--")
    ax.set_xlabel("log$_2$ kat değişimi (AML − ALL)")
    ax.set_ylabel("−log$_{10}$(p)")
    ax.set_title("Volcano grafiği (eğitim seti, Welch t-testi)")
    ax.legend(frameon=False, markerscale=3, fontsize=6, loc="upper left")
    fig.tight_layout()
    return save_fig(fig, "fig05a_volcano")


def plot_heatmap(L, y, res, names):
    """En anlamlı 50 gen için ısı haritası. Hem genleri hem hastaları hiyerarşik kümeleme ile sıralıyoruz.
    Kümeleme etiketleri görmüyor; hastalar yine de sınıflarına göre gruplanıyorsa bu genler gerçekten ayırt edici."""
    genes = res.index[:TOP]
    # Her geni kendi içinde z-skora çeviriyoruz. Yoksa genel olarak yüksek ifade edilen genler
    # bütün haritayı kırmızıya boyar ve hastalar arasındaki farkları göremeyiz.
    Z = L[genes].T
    Z = Z.sub(Z.mean(axis=1), axis=0).div(Z.std(axis=1), axis=0)
    # Satır adı olarak gen açıklamasının ilk birkaç kelimesini kullanıyoruz; sadece kod yazınca okunmuyor
    Z.index = [f"{str(names[g])[:22]}" for g in genes]

    g = sns.clustermap(Z, method="average", metric="correlation", cmap="RdBu_r", center=0, vmin=-3, vmax=3,
                       col_colors=y.map(CLASS_COLORS).rename("Sınıf"), figsize=(FIG_WIDTH, 5.2),
                       dendrogram_ratio=(0.12, 0.08), cbar_pos=(0.06, 0.9, 0.025, 0.07),
                       xticklabels=True, yticklabels=True)
    g.ax_heatmap.tick_params(axis="y", labelsize=3.5, length=0)
    g.ax_heatmap.tick_params(axis="x", labelsize=4, length=0)
    g.ax_heatmap.set_xlabel("Hasta numarası")
    g.ax_heatmap.set_ylabel("")
    g.ax_cbar.set_title("z", fontsize=6)
    # Renk ölçeğinin sayılarını sola alıyoruz ki sağdaki sınıf şeridinin üstüne binmesin
    g.ax_cbar.yaxis.set_ticks_position("left")
    g.ax_cbar.set_yticks([-3, 0, 3])
    g.ax_cbar.tick_params(labelsize=5)
    g.ax_col_colors.tick_params(axis="y", labelsize=6, length=0)
    g.fig.suptitle(f"En anlamlı {TOP} gen (eğitim seti)", y=1.0, fontsize=8)

    # Hastaların ağacını en üstten ikiye kesiyoruz ve çıkan iki grubun gerçek sınıflarla ne kadar
    # örtüştüğüne bakıyoruz. Düzeltilmiş Rand indeksi: 1 = birebir aynı, 0 = rastgele.
    clusters = fcluster(g.dendrogram_col.linkage, 2, criterion="maxclust")
    ari = adjusted_rand_score(y, clusters)
    tab = pd.crosstab(pd.Series(clusters, index=y.index, name="küme"), y)
    return save_fig(g.fig, "fig05b_isi_haritasi_top50"), ari, tab


def degenes() -> dict:
    L, y, names = load_train()
    res = welch(L, y)

    # Sonuçları kaydediyoruz; 8. adımda bu genlerin MILE'da da aynı yönde farklı olup olmadığına bakacağız
    PROCESSED.mkdir(parents=True, exist_ok=True)
    res.assign(description=names.reindex(res.index).values).to_csv(PROCESSED / "golub_train_welch.csv")

    sig = res["q"] < FDR
    out = {
        "n_train": len(L), "n_genes": L.shape[1], "n_const": res.attrs["n_const"], "n_tested": len(res),
        "n_sig_05": int(sig.sum()),
        "n_sig_01": int((res["q"] < 0.01).sum()),
        "n_sig_big": int((sig & (res["log2fc"].abs() >= FC)).sum()),
        "n_up_AML": int((sig & (res["log2fc"] > 0)).sum()),
        "n_up_ALL": int((sig & (res["log2fc"] < 0)).sum()),
        # Hiç gerçek fark olmasaydı p < 0.05 ile kaç gen şans eseri çıkardı? Kıyas için.
        "n_raw_p05": int((res["p"] < 0.05).sum()),
        "expected_by_chance": 0.05 * len(res),
        "fig_volcano": plot_volcano(res),
    }
    out["fig_heat"], out["ari"], out["cluster_tab"] = plot_heatmap(L, y, res, names)
    top = res.head(TOP)
    out["top_up_AML"] = int((top["log2fc"] > 0).sum())
    out["top_q_max"] = float(top["q"].max())
    out["top10"] = [(g, str(names[g])[:40], round(r.log2fc, 2), float(f"{r.q:.1e}"))
                    for g, r in res.head(10).iterrows()]
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in degenes().items():
        print(f"{k}: {v}")
