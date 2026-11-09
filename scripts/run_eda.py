"""Bütün EDA adımlarını sırayla çalıştırıp reports/eda_sonuclari.md dosyasını her seferinde baştan yazıyor.

Kullanım:  python scripts/run_eda.py
Rapora koyduğumuz her sayı bu betiğin çıktısından geliyor (yönerge 6.9).
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.eda_batch import batch
from src.eda_compare import compare
from src.eda_degenes import FC, FDR, TOP, degenes
from src.eda_dimred import dimred
from src.eda_distribution import distribution
from src.eda_mile import mile_eda
from src.eda_quality import HIGH, LOW, quality
from src.report_summary import latex, summary_md
from src.validate_golub import validate

REPORT = ROOT / "reports" / "eda_sonuclari.md"
R = {}  # Her adımın sonuç sözlüğü: R[1] ... R[8]
LATEX = ROOT / "reports" / "eda_latex_taslak.tex"


def pct(x: float) -> str:
    """Yüzdeleri raporda hep aynı biçimde, iki basamakla yazıyoruz."""
    return f"%{x:.2f}"


def step2() -> list[str]:
    r = quality()
    R[2] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
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
    R[3] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
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
    R[4] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
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


def step5() -> list[str]:
    r = degenes()
    R[5] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
    src = "`src/eda_degenes.py`"
    fv, fh = f"`{r['fig_volcano']}`", f"`{r['fig_heat']}`"
    tab = r["cluster_tab"]
    rows = [
        ("Kullanılan veri", f"Yalnızca eğitim seti ({r['n_train']} hasta), AFFX hariç {r['n_genes']} gen", src),
        ("Test edilen gen (sıfır varyanslı çıkarıldıktan sonra)", f"{r['n_tested']} (çıkarılan: {r['n_const']})", src),
        ("Ham p < 0.05 olan gen / şans eseri beklenen", f"{r['n_raw_p05']} / {r['expected_by_chance']:.0f}", src),
        (f"BH-FDR q < {FDR} anlamlı gen", r["n_sig_05"], fv),
        ("BH-FDR q < 0.01 anlamlı gen", r["n_sig_01"], src),
        (f"Anlamlı ve mutlak log2FC ≥ {FC:g} (≥ 2 kat) gen", r["n_sig_big"], fv),  # "|" tabloyu bozduğu için yazıyla
        ("Anlamlı genlerden AML'de yüksek / ALL'de yüksek", f"{r['n_up_AML']} / {r['n_up_ALL']}", fv),
        (f"En iyi {TOP} gen: AML'de yüksek / ALL'de yüksek", f"{r['top_up_AML']} / {TOP - r['top_up_AML']}", fh),
        (f"En iyi {TOP} gendeki en büyük q", f"{r['top_q_max']:.1e}", fh),
        ("Hasta kümelemesi (2 küme) – sınıf uyumu (düzeltilmiş Rand)", f"{r['ari']:.2f}", fh),
        ("Küme 1 (ALL / AML)", f"{tab.loc[1, 'ALL']} / {tab.loc[1, 'AML']}", fh),
        ("Küme 2 (ALL / AML)", f"{tab.loc[2, 'ALL']} / {tab.loc[2, 'AML']}", fh),
        ("Golub (1999) 50 gen listesiyle örtüşme", "Yapılmadı: liste makine tarafından okunabilir bir kaynaktan alınamadı", "—"),
    ]
    lines = ["## 5. Ayırt edici genler (yalnızca eğitim seti)", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    lines += ["", "En anlamlı 10 gen (Welch t-testi, eğitim seti):", "",
              "| Prob | Açıklama | log2FC (AML − ALL) | q |", "|---|---|---|---|"]
    lines += [f"| {g} | {d} | {fc} | {q:.1e} |" for g, d, fc, q in r["top10"]]
    lines += ["", "Bütün genlerin sonuçları: `data/processed/golub_train_welch.csv`", ""]
    return lines


def step6() -> list[str]:
    r = batch()
    R[6] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
    src = "`src/eda_batch.py`"
    fd, fk = f"`{r['fig_dist']}`", f"`{r['fig_ks']}`"
    rows = [
        ("AML oranı: eğitim / test", f"{pct(r['aml_frac_train'])} / {pct(r['aml_frac_test'])}", src),
        ("Karşılaştırma grubu (sınıf karışmasın diye)",
         f"Yalnız ALL: eğitim {r['n_ALL_train']}, test {r['n_ALL_test']}", src),
        ("ALL hasta ortalaması: eğitim / test (Mann–Whitney p)",
         f"{r['mean_ALL_train']:.3f} / {r['mean_ALL_test']:.3f} (p = {r['mw_p_ALL']:.3f})", fd),
        ("AML hasta ortalaması: eğitim / test (Mann–Whitney p)",
         f"{r['mean_AML_train']:.3f} / {r['mean_AML_test']:.3f} (p = {r['mw_p_AML']:.3f})", fd),
        ("Yalnız ALL PCA'sında seti en iyi ayıran bileşen (p)",
         f"PC{r['pca_all_best_pc']} (p = {r['pca_all_best_p']:.1e})", src),
        ("Bu bileşenin hasta ortalamasıyla korelasyonu", f"{r['pca_all_best_corr_mean']:.2f}", src),
        ("KS testine giren ifade edilen gen", f"{r['n_expressed']} / {r['n_genes']}", src),
        ("KS p < 0.05 gen (ham log2) / şans eseri beklenen", f"{r['ks_raw_p05']} / {r['ks_expected']:.0f}", fk),
        (f"KS BH-FDR q < {FDR} gen (ham log2)", r["ks_raw_q05"], fk),
        ("KS p < 0.05 gen (hasta medyanına göre ortalanmış)", r["ks_norm_p05"], fk),
        (f"KS BH-FDR q < {FDR} gen (hasta medyanına göre ortalanmış)", r["ks_norm_q05"], fk),
        ("Batch anlamlı (q < 0.05) ∩ ayırt edici gen (5. adım)", r["batch_and_de"], src),
        (f"Batch anlamlı ∩ en iyi {TOP} gen", f"{r['batch_in_top50']} ({', '.join(r['batch_top50_genes']) or '—'})", src),
    ]
    lines = ["## 6. Batch analizi (Golub eğitim vs. test)", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    return lines + [""]


def step7() -> list[str]:
    r = mile_eda()
    R[7] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
    src = "`src/eda_mile.py`"
    fs, fc = f"`{r['fig_sub']}`", f"`{r['fig_scale']}`"
    a80, a570 = r["annot80"], r["annot570"]
    g, m = r["golub_collapse"], r["mile_collapse"]
    tis = r["tissue_counts"]
    rows = [
        ("MILE toplam hasta / seçilen ALL+AML", f"{r['n_total']} / {r['n_all'] + r['n_aml']}", src),
        ("ALL (C1–C8 toplamı) / AML", f"{r['n_all']} / {r['n_aml']}", fs),
        ("ALL / AML oranı", f"{pct(100 * r['n_all'] / (r['n_all'] + r['n_aml']))} / "
                            f"{pct(100 * r['n_aml'] / (r['n_all'] + r['n_aml']))}", src),
        ("Doku: kemik iliği / periferik kan (ALL)",
         f"{tis.loc[('ALL', 'bone marrow')]} / {tis.loc[('ALL', 'peripheral blood')]}", src),
        ("Doku: kemik iliği / periferik kan (AML)",
         f"{tis.loc[('AML', 'bone marrow')]} / {tis.loc[('AML', 'peripheral blood')]}", src),
        ("Matristeki prob sayısı", r["n_probes_raw"], src),
        ("Bütün hastalarda boş (NaN) prob (hepsi AFFX)", f"{r['n_all_nan']} ({r['all_nan_affx']} AFFX)", src),
        ("Bu problar atıldıktan sonra kalan NaN", r["n_nan_left"], src),
        ("Değer aralığı (min / max) ve negatif değer sayısı", f"{r['min']:g} / {r['max']:g}, negatif: {r['n_neg']}", fc),
        ("Hasta medyanı aralığı", f"{r['sample_median_min']:.4f} – {r['sample_median_max']:.4f}", fc),
        ("Sıralı hasta değerlerinin ortak sıralamadan en büyük sapması", f"{r['sorted_max_diff']:.4f}", fc),
        ("Çarpıklık: MILE değerleri / bir kez daha log2 alınırsa", f"{r['skew']:.2f} / {r['skew_after_log']:.2f}", fc),
        ("Ölçek kararı", "Ham değil; log benzeri sıkıştırılmış, 0–1'e ölçeklenmiş, quantile normalize. "
                         "Kırpma + log2 uygulanmamalı.", fc),
        ("GPL80 (Golub): prob / sembolsüz / çok genli / eşlenen",
         f"{a80['n_probes']} / {a80['n_empty']} / {a80['n_multi']} / {a80['n_mapped']}", src),
        ("GPL570 (MILE): prob / sembolsüz / çok genli / eşlenen",
         f"{a570['n_probes']} / {a570['n_empty']} / {a570['n_multi']} / {a570['n_mapped']}", src),
        ("Golub: kullanılan prob → benzersiz gen (birden çok problu gen; gen başına en fazla prob)",
         f"{g['n_probes_used']} → {g['n_genes']} ({g['n_genes_multi_probe']}; {g['max_probes_per_gene']})", src),
        ("MILE: kullanılan prob → benzersiz gen (birden çok problu gen; gen başına en fazla prob)",
         f"{m['n_probes_used']} → {m['n_genes']} ({m['n_genes_multi_probe']}; {m['max_probes_per_gene']})", src),
        ("Çoklu prob kuralı", "Ortalama ifadesi en yüksek prob (Golub'da ortalama yalnız eğitim setinden)", src),
        ("**Golub–MILE ortak gen sayısı**", f"**{r['n_common']}**", src),
    ]
    lines = ["## 7. MILE (GSE13159) ve gen eşlemesi", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    lines += ["", "MILE alt sınıfları:", "", "| Sınıf | Alt sınıf | Hasta |", "|---|---|---|"]
    lines += [f"| {c} | {s} | {n} |" for (c, s), n in r["subclass_counts"].items()]
    return lines + [""]


def step8() -> list[str]:
    r = compare()
    R[8] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
    src = "`src/eda_compare.py`"
    fs, fp, fd = f"`{r['fig_scale']}`", f"`{r['fig_pca']}`", f"`{r['fig_dir']}`"
    rows = [
        ("Ortak gen / Golub hasta / MILE hasta", f"{r['n_common']} / {r['n_golub']} / {r['n_mile']}", src),
        ("Gen ortalamalarının sıralama uyumu (Spearman ρ)", f"{r['rho_means']:.2f}", fs),
        ("Ham birleştirme PCA: PC1 açıklanan varyans", pct(r["pc1_raw"]), fp),
        ("Ham birleştirme PCA: siluet (veri seti / sınıf)", f"{r['sil_ds_raw']:.2f} / {r['sil_class_raw']:.2f}", fp),
        ("Gen bazında z-skor PCA: PC1 açıklanan varyans", pct(r["pc1_z"]), fp),
        ("Gen bazında z-skor PCA: siluet (veri seti / sınıf)", f"{r['sil_ds_z']:.2f} / {r['sil_class_z']:.2f}", fp),
        (f"z-skor PCA'da sınıfı en iyi ayıran bileşen", f"PC{r['z_best_pc']}", fp),
        (f"Bu bileşende AML − ALL medyan farkı (Mann–Whitney p): Golub",
         f"{r['z_best_pc_Golub_diff']:.1f} (p = {r['z_best_pc_Golub_p']:.1e})", fp),
        (f"Bu bileşende AML − ALL medyan farkı (Mann–Whitney p): MILE",
         f"{r['z_best_pc_MILE_diff']:.1f} (p = {r['z_best_pc_MILE_p']:.1e})", fp),
        ("Kendi PCA'sında sınıf siluet skoru: Golub / MILE",
         f"{r['sil_class_own_Golub']:.2f} / {r['sil_class_own_MILE']:.2f}", src),
        ("Golub eğitimde anlamlı gen (ortak genlerde, q < 0.05)", r["golub_sig"], fd),
        ("MILE'da anlamlı gen (q < 0.05)", r["mile_sig"], src),
        ("Bütün ortak genlerde aynı yön oranı (kıyas)", pct(r["same_dir_all"]), fd),
        ("Golub'da anlamlı genlerde MILE ile aynı yön oranı", pct(r["same_dir_sig"]), fd),
        ("Golub'da anlamlı → MILE'da aynı yönde anlamlı / ters yönde anlamlı",
         f"{r['same_dir_sig_mile_sig']} / {r['opp_dir_sig_mile_sig']}", fd),
        ("Golub t ile MILE t sıralama uyumu (Spearman ρ)", f"{r['rho_t']:.2f}", fd),
        (f"Golub en iyi {TOP} gen: MILE'da aynı yön / aynı yönde anlamlı",
         f"{r['top_same_dir']} / {r['top_same_dir_mile_sig']}", fd),
        (f"Golub en iyi {TOP} genden ters yönde olanlar", ", ".join(r["top_opposite"]) or "—", fd),
    ]
    lines = ["## 8. Golub vs. MILE (ortak genler)", "", "| Bulgu | Sayı | Kaynak |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {s} |" for k, v, s in rows]
    return lines + [""]


def step1() -> list[str]:
    r = validate()
    R[1] = r  # Özet ve LaTeX taslağı için sonucu saklıyoruz
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
    md += step5()
    md += step6()
    md += step7()
    md += step8()
    # 9. adım: bütün adımların sonuçlarından özet ve LaTeX taslağı. Sayılar R sözlüğünden geliyor.
    md += summary_md(R)
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(md), encoding="utf-8")
    LATEX.write_text(latex(R), encoding="utf-8")
    print("\n".join(md))
    print(f"\nYazıldı: {REPORT}\nYazıldı: {LATEX}")
