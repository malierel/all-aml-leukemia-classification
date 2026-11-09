# EDA Sonuçları

Bu dosya `python scripts/run_eda.py` ile otomatik üretilir; elle düzenlemeyin.

## 1. Yükleme ve doğrulama

| Bulgu | Sayı | Kaynak |
|---|---|---|
| Etiket dosyasındaki hasta sayısı | 72 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Eğitim matrisi (hasta × prob) | 38 × 7129 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Test matrisi (hasta × prob) | 34 × 7129 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Eğitim sınıfları (ALL / AML) | 27 / 11 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Test sınıfları (ALL / AML) | 20 / 14 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Eğitim hasta no aralığı | 1–38 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Test hasta no aralığı | 39–72 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Eğitim sütunları numara sırasında mı? | Hayır | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Test sütunları numara sırasında mı? | Hayır | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Sıraya göre eşlenseydi yanlış etiketlenecek hasta (eğitim) | 0 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Sıraya göre eşlenseydi yanlış etiketlenecek hasta (test) | 14 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Eğitim–test ortak hasta sayısı | 0 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Eğitim ∪ test = 1–72 hastaları | Evet | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| İki sette prob listesi/sırası aynı | Evet | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| AFFX kontrol probu sayısı | 58 | `src/validate_golub.py` (`load_golub.py` üzerinden) |
| Call sütunu değerleri | A, M, P | `src/validate_golub.py` (`load_golub.py` üzerinden) |

Eğitim CSV ham sütun sırası: `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 34, 35, 36, 37, 38, 28, 29, 30, 31, 32, 33]`

Test CSV ham sütun sırası: `[39, 40, 42, 47, 48, 49, 41, 43, 44, 45, 46, 70, 71, 72, 68, 69, 67, 55, 56, 59, 52, 53, 51, 50, 54, 57, 58, 60, 61, 65, 66, 63, 64, 62]`

## 2. Veri kalitesi

| Bulgu | Sayı | Kaynak |
|---|---|---|
| Toplam prob / AFFX kontrol probu | 7129 / 58 | `src/eda_quality.py` |
| Değer tipi | Tamamı tam sayı (int64) | `src/eda_quality.py` |
| NaN / INF sayısı (72 hasta) | 0 / 0 | `src/eda_quality.py` |
| Eğitim: negatif değer oranı | %28.49 | `src/eda_quality.py` |
| Eğitim: <20 oranı / >16000 oranı | %32.37 / %0.86 | `src/eda_quality.py` |
| Eğitim: min / medyan / max | -28400 / 127 / 61228 | `src/eda_quality.py` |
| Test: negatif değer oranı | %28.88 | `src/eda_quality.py` |
| Test: <20 oranı / >16000 oranı | %33.11 / %0.80 | `src/eda_quality.py` |
| Test: min / medyan / max | -26775 / 114 / 71369 | `src/eda_quality.py` |
| Genler (AFFX hariç): negatif değer oranı | %28.52 | `src/eda_quality.py` |
| Genler (AFFX hariç): <20 oranı / >16000 oranı | %32.57 / %0.79 | `src/eda_quality.py` |
| Genler (AFFX hariç): min / medyan / max | -28400 / 121 / 71369 | `src/eda_quality.py` |
| AFFX kontrol probları: negatif değer oranı | %47.58 | `src/eda_quality.py` |
| AFFX kontrol probları: <20 oranı / >16000 oranı | %50.84 / %5.94 | `src/eda_quality.py` |
| AFFX kontrol probları: min / medyan / max | -3766 / 14 / 43858 | `src/eda_quality.py` |
| Negatif değerlerin call dağılımı (A / M / P) | %99.28 / %0.22 / %0.50 | `src/eda_quality.py` |
| Hiçbir hastada P olmayan prob (72 hasta) | 1971 | `src/eda_quality.py` |
| Hiçbir hastada P olmayan prob (yalnız eğitim) | 2366 | `src/eda_quality.py` |
| Hiçbir hastada P olmayan AFFX probu | 34 / 58 | `src/eda_quality.py` |
| Test ALL: P / M / A | %28.55 / %1.58 / %69.87 | `figures/fig02_pma_dagilimi.pdf` |
| Test AML: P / M / A | %25.59 / %1.65 / %72.77 | `figures/fig02_pma_dagilimi.pdf` |
| Eğitim ALL: P / M / A | %29.68 / %1.60 / %68.72 | `figures/fig02_pma_dagilimi.pdf` |
| Eğitim AML: P / M / A | %27.43 / %1.65 / %70.92 | `figures/fig02_pma_dagilimi.pdf` |

## 3. Dağılım ve dönüşüm

| Bulgu | Sayı | Kaynak |
|---|---|---|
| Çarpıklık: ham / kırpma + log2 | 7.08 / 0.55 | `figures/fig03a_dagilim_ham_log.pdf` |
| Alttan 20'ye kırpılan değer oranı | %32.72 | `src/eda_distribution.py` |
| Üstten 16000'e kırpılan değer oranı | %0.83 | `src/eda_distribution.py` |
| Ham ölçekte hasta ortalaması: en düşük / en yüksek | 492.6 (hasta 12) / 954.4 (hasta 20) | `src/eda_distribution.py` |
| Ham ölçekte en yüksek / en düşük hasta ortalaması oranı | 1.94 kat | `src/eda_distribution.py` |
| log2 sonrası hasta medyanı aralığı | 6.09 – 7.65 | `figures/fig03b_ornek_kutu.pdf` |
| log2 sonrası hasta ortalaması aralığı | 6.52 – 7.54 | `figures/fig03b_ornek_kutu.pdf` |
| log2 sonrası en uç iki hasta ortalaması farkı (kat) | 2.03 kat | `src/eda_distribution.py` |
| log2 hasta ortalamalarının ortalaması: eğitim / test | 7.026 / 6.911 | `src/eda_distribution.py` |
| log2 hasta ortalamalarının ortalaması: ALL / AML | 6.965 / 6.985 | `src/eda_distribution.py` |

## 4. Boyut indirgeme

| Bulgu | Sayı | Kaynak |
|---|---|---|
| Analize giren gen sayısı (AFFX hariç, kırpma + log2) | 7071 | `src/eda_dimred.py` |
| PC1 / PC2 / PC3 açıklanan varyans | %9.38 / %8.29 / %5.92 | `figures/fig04a_pca_varyans.pdf` |
| PC1 + PC2 toplam | %17.67 | `figures/fig04a_pca_varyans.pdf` |
| %50 / %80 / %90 varyans için gereken bileşen | 13 / 41 / 54 | `figures/fig04a_pca_varyans.pdf` |
| ALL/AML'yi en iyi ayıran bileşen (ilk 10 içinde, Mann–Whitney p) | PC1 (p = 1.8e-10) | `figures/fig04b_pca_pc1_pc2.pdf` |
| Eğitim/testi en iyi ayıran bileşen (ilk 10 içinde, Mann–Whitney p) | PC2 (p = 6.4e-03) | `figures/fig04b_pca_pc1_pc2.pdf` |
| Siluet (sınıf): PCA-2B / t-SNE / UMAP | 0.29 / 0.27 / 0.30 | `figures/fig04c_tsne_umap.pdf` |
| Siluet (set): PCA-2B / t-SNE / UMAP | 0.04 / 0.05 / 0.04 | `figures/fig04c_tsne_umap.pdf` |

## 5. Ayırt edici genler (yalnızca eğitim seti)

| Bulgu | Sayı | Kaynak |
|---|---|---|
| Kullanılan veri | Yalnızca eğitim seti (38 hasta), AFFX hariç 7071 gen | `src/eda_degenes.py` |
| Test edilen gen (sıfır varyanslı çıkarıldıktan sonra) | 7071 (çıkarılan: 0) | `src/eda_degenes.py` |
| Ham p < 0.05 olan gen / şans eseri beklenen | 1975 / 354 | `src/eda_degenes.py` |
| BH-FDR q < 0.05 anlamlı gen | 1274 | `figures/fig05a_volcano.pdf` |
| BH-FDR q < 0.01 anlamlı gen | 815 | `src/eda_degenes.py` |
| Anlamlı ve mutlak log2FC ≥ 1 (≥ 2 kat) gen | 497 | `figures/fig05a_volcano.pdf` |
| Anlamlı genlerden AML'de yüksek / ALL'de yüksek | 369 / 905 | `figures/fig05a_volcano.pdf` |
| En iyi 50 gen: AML'de yüksek / ALL'de yüksek | 27 / 23 | `figures/fig05b_isi_haritasi_top50.pdf` |
| En iyi 50 gendeki en büyük q | 3.3e-04 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Hasta kümelemesi (2 küme) – sınıf uyumu (düzeltilmiş Rand) | 0.79 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Küme 1 (ALL / AML) | 2 / 11 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Küme 2 (ALL / AML) | 25 / 0 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Golub (1999) 50 gen listesiyle örtüşme | Yapılmadı: liste makine tarafından okunabilir bir kaynaktan alınamadı | — |

En anlamlı 10 gen (Welch t-testi, eğitim seti):

| Prob | Açıklama | log2FC (AML − ALL) | q |
|---|---|---|---|
| M27891_at | CST3 Cystatin C (amyloid angiopathy and  | 5.92 | 3.1e-06 |
| X95735_at | Zyxin | 3.6 | 4.3e-06 |
| M55150_at | FAH Fumarylacetoacetate | 1.31 | 9.4e-06 |
| M28170_at | CD19 CD19 antigen | -2.63 | 2.0e-05 |
| X52142_at | CTPS CTP synthetase | -2.37 | 2.2e-05 |
| Y12670_at | LEPR Leptin receptor | 1.75 | 3.9e-05 |
| M81933_at | CDC25A Cell division cycle 25A | 1.76 | 3.9e-05 |
| U50136_rna1_at | Leukotriene C4 synthase (LTC4S) gene | 1.4 | 3.9e-05 |
| M31523_at | TCF3 Transcription factor 3 (E2A immunog | -1.95 | 3.9e-05 |
| U12471_cds1_at | Thrombospondin-p50 gene extracted from H | 1.03 | 6.4e-05 |

Bütün genlerin sonuçları: `data/processed/golub_train_welch.csv`

## 6. Batch analizi (Golub eğitim vs. test)

| Bulgu | Sayı | Kaynak |
|---|---|---|
| AML oranı: eğitim / test | %28.95 / %41.18 | `src/eda_batch.py` |
| Karşılaştırma grubu (sınıf karışmasın diye) | Yalnız ALL: eğitim 27, test 20 | `src/eda_batch.py` |
| ALL hasta ortalaması: eğitim / test (Mann–Whitney p) | 7.020 / 6.895 (p = 0.072) | `figures/fig06a_batch_dagilim.pdf` |
| AML hasta ortalaması: eğitim / test (Mann–Whitney p) | 7.044 / 6.941 (p = 0.286) | `figures/fig06a_batch_dagilim.pdf` |
| Yalnız ALL PCA'sında seti en iyi ayıran bileşen (p) | PC2 (p = 4.3e-04) | `src/eda_batch.py` |
| Bu bileşenin hasta ortalamasıyla korelasyonu | -0.49 | `src/eda_batch.py` |
| KS testine giren ifade edilen gen | 4898 / 7071 | `src/eda_batch.py` |
| KS p < 0.05 gen (ham log2) / şans eseri beklenen | 834 / 245 | `figures/fig06b_ks_pdegerleri.pdf` |
| KS BH-FDR q < 0.05 gen (ham log2) | 22 | `figures/fig06b_ks_pdegerleri.pdf` |
| KS p < 0.05 gen (hasta medyanına göre ortalanmış) | 540 | `figures/fig06b_ks_pdegerleri.pdf` |
| KS BH-FDR q < 0.05 gen (hasta medyanına göre ortalanmış) | 2 | `figures/fig06b_ks_pdegerleri.pdf` |
| Batch anlamlı (q < 0.05) ∩ ayırt edici gen (5. adım) | 1 | `src/eda_batch.py` |
| Batch anlamlı ∩ en iyi 50 gen | 1 (M81933_at (CDC25A Cell division cycle 25A)) | `src/eda_batch.py` |
