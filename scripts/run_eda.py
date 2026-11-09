"""Bütün EDA adımlarını sırayla çalıştırıp reports/eda_sonuclari.md dosyasını her seferinde baştan yazıyor.

Kullanım:  python scripts/run_eda.py
Rapora koyduğumuz her sayı bu betiğin çıktısından geliyor (yönerge 6.9).
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.eda_dimred import dimred
from src.eda_distribution import distribution
from src.eda_quality import HIGH, LOW, quality
from src.validate_golub import validate

REPORT = ROOT / "reports" / "eda_sonuclari.md"


def pct(x: float) -> str:
    """Yüzdeleri raporda hep aynı biçimde, iki basamakla yazıyoruz."""
    return f"%{x:.2f}"


def step2() -> list[str]:
    r = quality()
    src = "`src/eda_quality.py`"
    fig = f"`{r['fig']}`"
    rows = [
        ("Toplam prob / AFFX kontrol probu", f"{r['n_probes']} / {r['n_affx']}", src),
        ("Değer tipi", "Tamamı tam sayı (int64)", src),
        ("NaN / INF sayısı (72 hasta)", f"{r['vals_all']['n_nan']} / {r['vals_all']['n_inf']}", src),
    ]
    for key, name in [("vals_train", "Eğitim"), ("vals_test", "Test"), ("vals_genes", "Genler (AFFX hariç)"),
                      ("vals_affx", "AFFX kontrol probları")]:
        v = r[key]
        rows += [
            (f"{name}: negatif değer oranı", pct(v["neg_pct"]), src),
            (f"{name}: <{LOW} oranı / >{HIGH} oranı", f"{pct(v['below_low_pct'])} / {pct(v['above_high_pct'])}", src),
            (f"{name}: min / medyan / max", f"{v['min']} / {v['median']:g} / {v['max']}", src),
        ]
    nd = r["neg_call_dist"]
    rows += [
        ("Negatif değerlerin call dağılımı (A / M / P)",
         f"{pct(nd.get('A', 0))} / {pct(nd.get('M', 0))} / {pct(nd.get('P', 0))}", src),
        ("Hiçbir hastada P olmayan prob (72 hasta)", r["never_P_all"], src),
        ("Hiçbir hastada P olmayan prob (yalnız eğitim)", r["never_P_train"], src),
        ("Hiçbir hastada P olmayan AFFX probu", f"{r['never_P_affx']} / {r['n_affx']}", src),
    ]
    names = {"train": "Eğitim", "test": "Test"}
    for (s, c), t in r["call_table"].iterrows():
        rows.append((f"{names[s]} {c}: P / M / A", f"{pct(t['P'])} / {pct(t['M'])} / {pct(t['A'])}", fig))

    lines = ["## 2. Veri kalitesi", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    return lines + [""]


def step3() -> list[str]:
    r = distribution()
    src = "`src/eda_distribution.py`"
    fa, fb = f"`{r['fig_hist']}`", f"`{r['fig_box']}`"
    rows = [
        ("Çarpıklık: ham / kırpma + log2", f"{r['skew_raw']:.2f} / {r['skew_log']:.2f}", fa),
        (f"Alttan {LOW}'ye kırpılan değer oranı", pct(r["clipped_low_pct"]), src),
        (f"Üstten {HIGH}'e kırpılan değer oranı", pct(r["clipped_high_pct"]), src),
        ("Ham ölçekte hasta ortalaması: en düşük / en yüksek",
         f"{r['raw_mean_min']:.1f} (hasta {r['raw_mean_min_id']}) / {r['raw_mean_max']:.1f} (hasta {r['raw_mean_max_id']})", src),
        ("Ham ölçekte en yüksek / en düşük hasta ortalaması oranı", f"{r['raw_mean_ratio']:.2f} kat", src),
        ("log2 sonrası hasta medyanı aralığı", f"{r['log_median_min']:.2f} – {r['log_median_max']:.2f}", fb),
        ("log2 sonrası hasta ortalaması aralığı", f"{r['log_mean_min']:.2f} – {r['log_mean_max']:.2f}", fb),
        ("log2 sonrası en uç iki hasta ortalaması farkı (kat)", f"{r['log_mean_fold']:.2f} kat", src),
        ("log2 hasta ortalamalarının ortalaması: eğitim / test",
         f"{r['log_mean_train']:.3f} / {r['log_mean_test']:.3f}", src),
        ("log2 hasta ortalamalarının ortalaması: ALL / AML",
         f"{r['log_mean_ALL']:.3f} / {r['log_mean_AML']:.3f}", src),
    ]
    lines = ["## 3. Dağılım ve dönüşüm", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    return lines + [""]


def step4() -> list[str]:
    r = dimred()
    src = "`src/eda_dimred.py`"
    fv, fp, fe = f"`{r['fig_var']}`", f"`{r['fig_pca']}`", f"`{r['fig_embed']}`"
    v = r["pc_var"]
    rows = [
        ("Analize giren gen sayısı (AFFX hariç, kırpma + log2)", r["n_genes"], src),
        ("PC1 / PC2 / PC3 açıklanan varyans", f"{pct(v[0])} / {pct(v[1])} / {pct(v[2])}", fv),
        ("PC1 + PC2 toplam", pct(v[0] + v[1]), fv),
        ("%50 / %80 / %90 varyans için gereken bileşen", f"{r['n_pc_50']} / {r['n_pc_80']} / {r['n_pc_90']}", fv),
        ("ALL/AML'yi en iyi ayıran bileşen (ilk 10 içinde, Mann–Whitney p)",
         f"PC{r['best_pc_class']} (p = {r['best_pc_class_p']:.1e})", fp),
        ("Eğitim/testi en iyi ayıran bileşen (ilk 10 içinde, Mann–Whitney p)",
         f"PC{r['best_pc_set']} (p = {r['best_pc_set_p']:.1e})", fp),
        ("Siluet (sınıf): PCA-2B / t-SNE / UMAP",
         f"{r['sil_class_pca2']:.2f} / {r['sil_class_tsne']:.2f} / {r['sil_class_umap']:.2f}", fe),
        ("Siluet (set): PCA-2B / t-SNE / UMAP",
         f"{r['sil_set_pca2']:.2f} / {r['sil_set_tsne']:.2f} / {r['sil_set_umap']:.2f}", fe),
    ]
    lines = ["## 4. Boyut indirgeme", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    return lines + [""]


def step1() -> list[str]:
    r = validate()
    src = "`src/validate_golub.py` (`load_golub.py` üzerinden)"
    rows = [
        ("Etiket dosyasındaki hasta sayısı", r["n_label_rows"]),
        ("Eğitim matrisi (hasta × prob)", f"{r['train_shape'][0]} × {r['train_shape'][1]}"),
        ("Test matrisi (hasta × prob)", f"{r['test_shape'][0]} × {r['test_shape'][1]}"),
        ("Eğitim sınıfları (ALL / AML)", f"{r['train_counts']['ALL']} / {r['train_counts']['AML']}"),
        ("Test sınıfları (ALL / AML)", f"{r['test_counts']['ALL']} / {r['test_counts']['AML']}"),
        ("Eğitim hasta no aralığı", f"{r['train_ids'][0]}–{r['train_ids'][1]}"),
        ("Test hasta no aralığı", f"{r['test_ids'][0]}–{r['test_ids'][1]}"),
        ("Eğitim sütunları numara sırasında mı?", "Evet" if r["train_is_sorted"] else "Hayır"),
        ("Test sütunları numara sırasında mı?", "Evet" if r["test_is_sorted"] else "Hayır"),
        ("Sıraya göre eşlenseydi yanlış etiketlenecek hasta (eğitim)", r["train_naive_mislabeled"]),
        ("Sıraya göre eşlenseydi yanlış etiketlenecek hasta (test)", r["test_naive_mislabeled"]),
        ("Eğitim–test ortak hasta sayısı", r["overlap"]),
        ("Eğitim ∪ test = 1–72 hastaları", "Evet" if r["union_is_1_72"] else "Hayır"),
        ("İki sette prob listesi/sırası aynı", "Evet" if r["same_genes"] else "Hayır"),
        ("AFFX kontrol probu sayısı", r["train_n_affx"]),
        ("Call sütunu değerleri", ", ".join(r["train_call_values"])),
    ]
    lines = ["## 1. Yükleme ve doğrulama", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {src} |" for k, v in rows]
    lines += ["", f"Eğitim CSV ham sütun sırası: `{r['train_raw_order']}`", "",
              f"Test CSV ham sütun sırası: `{r['test_raw_order']}`", ""]
    return lines


if __name__ == "__main__":
    # Windows konsolu Türkçe karakterleri ve bazı matematik işaretlerini bozuyor, o yüzden çıktıyı UTF-8 yapıyoruz
    sys.stdout.reconfigure(encoding="utf-8")
    md = ["# EDA Sonuçları", "", "Bu dosya `python scripts/run_eda.py` ile otomatik üretilir; elle düzenlemeyin.", ""]
    md += step1()
    md += step2()
    md += step3()
    md += step4()
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"\nYazıldı: {REPORT}")
