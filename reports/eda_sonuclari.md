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
| Test edilen gen (sıfır varyanslı çıkarıldıktan sonra) | 6595 (çıkarılan: 476) | `src/eda_degenes.py` |
| Ham p < 0.05 olan gen / şans eseri beklenen | 1499 / 330 | `src/eda_degenes.py` |
| BH-FDR q < 0.05 anlamlı gen | 602 | `figures/fig05a_volcano.pdf` |
| BH-FDR q < 0.01 anlamlı gen | 224 | `src/eda_degenes.py` |
| Anlamlı ve mutlak log2FC ≥ 1 (≥ 2 kat) gen | 410 | `figures/fig05a_volcano.pdf` |
| Anlamlı genlerden AML'de yüksek / ALL'de yüksek | 274 / 328 | `figures/fig05a_volcano.pdf` |
| En iyi 50 gen: AML'de yüksek / ALL'de yüksek | 27 / 23 | `figures/fig05b_isi_haritasi_top50.pdf` |
| En iyi 50 gendeki en büyük q | 5.7e-04 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Hasta kümelemesi (2 küme) – sınıf uyumu (düzeltilmiş Rand) | 0.79 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Küme 1 (ALL / AML) | 2 / 11 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Küme 2 (ALL / AML) | 25 / 0 | `figures/fig05b_isi_haritasi_top50.pdf` |
| Golub (1999) 50 gen listesiyle örtüşme | Yapılmadı: liste makine tarafından okunabilir bir kaynaktan alınamadı | — |

En anlamlı 10 gen (Welch t-testi, eğitim seti):

| Prob | Açıklama | log2FC (AML − ALL) | q |
|---|---|---|---|
| M27891_at | CST3 Cystatin C (amyloid angiopathy and  | 5.92 | 2.9e-06 |
| X95735_at | Zyxin | 3.6 | 4.0e-06 |
| M55150_at | FAH Fumarylacetoacetate | 1.31 | 8.8e-06 |
| M28170_at | CD19 CD19 antigen | -2.63 | 1.8e-05 |
| X52142_at | CTPS CTP synthetase | -2.37 | 2.1e-05 |
| Y12670_at | LEPR Leptin receptor | 1.75 | 3.7e-05 |
| M81933_at | CDC25A Cell division cycle 25A | 1.76 | 3.7e-05 |
| U50136_rna1_at | Leukotriene C4 synthase (LTC4S) gene | 1.4 | 3.7e-05 |
| M31523_at | TCF3 Transcription factor 3 (E2A immunog | -1.95 | 3.7e-05 |
| U12471_cds1_at | Thrombospondin-p50 gene extracted from H | 1.03 | 6.0e-05 |

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

## 7. MILE (GSE13159) ve gen eşlemesi

| Bulgu | Sayı | Kaynak |
|---|---|---|
| MILE toplam hasta / seçilen ALL+AML | 2096 / 1292 | `src/eda_mile.py` |
| ALL (C1–C8 toplamı) / AML | 750 / 542 | `figures/fig07a_mile_alt_siniflar.pdf` |
| ALL / AML oranı | %58.05 / %41.95 | `src/eda_mile.py` |
| Doku: kemik iliği / periferik kan (ALL) | 710 / 40 | `src/eda_mile.py` |
| Doku: kemik iliği / periferik kan (AML) | 501 / 41 | `src/eda_mile.py` |
| Matristeki prob sayısı | 54675 | `src/eda_mile.py` |
| Bütün hastalarda boş (NaN) prob (hepsi AFFX) | 45 (45 AFFX) | `src/eda_mile.py` |
| Bu problar atıldıktan sonra kalan NaN | 0 | `src/eda_mile.py` |
| Değer aralığı (min / max) ve negatif değer sayısı | 0 / 1, negatif: 0 | `figures/fig07b_mile_olcek.pdf` |
| Hasta medyanı aralığı | 0.2496 – 0.2496 | `figures/fig07b_mile_olcek.pdf` |
| Sıralı hasta değerlerinin ortak sıralamadan en büyük sapması | 0.0057 | `figures/fig07b_mile_olcek.pdf` |
| Çarpıklık: MILE değerleri / bir kez daha log2 alınırsa | 0.70 / -0.89 | `figures/fig07b_mile_olcek.pdf` |
| Ölçek kararı | Ham değil; log benzeri sıkıştırılmış, 0–1'e ölçeklenmiş, quantile normalize. Kırpma + log2 uygulanmamalı. | `figures/fig07b_mile_olcek.pdf` |
| GPL80 (Golub): prob / sembolsüz / çok genli / eşlenen | 7129 / 1032 / 377 / 5720 | `src/eda_mile.py` |
| GPL570 (MILE): prob / sembolsüz / çok genli / eşlenen | 54675 / 8893 / 2796 / 42986 | `src/eda_mile.py` |
| Golub: kullanılan prob → benzersiz gen (birden çok problu gen; gen başına en fazla prob) | 5701 → 5033 (556; 6) | `src/eda_mile.py` |
| MILE: kullanılan prob → benzersiz gen (birden çok problu gen; gen başına en fazla prob) | 42976 → 21655 (10747; 15) | `src/eda_mile.py` |
| Çoklu prob kuralı | Ortalama ifadesi en yüksek prob (Golub'da ortalama yalnız eğitim setinden) | `src/eda_mile.py` |
| **Golub–MILE ortak gen sayısı** | **4975** | `src/eda_mile.py` |

MILE alt sınıfları:

| Sınıf | Alt sınıf | Hasta |
|---|---|---|
| ALL | ALL with hyperdiploid karyotype | 40 |
| ALL | ALL with t(12;21) | 58 |
| ALL | ALL with t(1;19) | 36 |
| ALL | Pro-B-ALL with t(11q23)/MLL | 70 |
| ALL | T-ALL | 174 |
| ALL | c-ALL/Pre-B-ALL with t(9;22) | 122 |
| ALL | c-ALL/Pre-B-ALL without t(9;22) | 237 |
| ALL | mature B-ALL with t(8;14) | 13 |
| AML | AML complex aberrant karyotype | 48 |
| AML | AML with inv(16)/t(16;16) | 28 |
| AML | AML with normal karyotype + other abnormalities | 351 |
| AML | AML with t(11q23)/MLL | 38 |
| AML | AML with t(15;17) | 37 |
| AML | AML with t(8;21) | 40 |

## 8. Golub vs. MILE (ortak genler)

| Bulgu | Sayı | Kaynak |
|---|---|---|
| Ortak gen / Golub hasta / MILE hasta | 4975 / 72 / 1292 | `src/eda_compare.py` |
| Gen ortalamalarının sıralama uyumu (Spearman ρ) | 0.52 | `figures/fig08a_golub_mile_olcek.pdf` |
| Ham birleştirme PCA: PC1 açıklanan varyans | %97.19 | `figures/fig08b_birlesik_pca.pdf` |
| Ham birleştirme PCA: siluet (veri seti / sınıf) | 0.99 / -0.00 | `figures/fig08b_birlesik_pca.pdf` |
| Gen bazında z-skor PCA: PC1 açıklanan varyans | %9.28 | `figures/fig08b_birlesik_pca.pdf` |
| Gen bazında z-skor PCA: siluet (veri seti / sınıf) | -0.18 / 0.35 | `figures/fig08b_birlesik_pca.pdf` |
| z-skor PCA'da sınıfı en iyi ayıran bileşen | PC1 | `figures/fig08b_birlesik_pca.pdf` |
| Bu bileşende AML − ALL medyan farkı (Mann–Whitney p): Golub | 19.0 (p = 4.5e-12) | `figures/fig08b_birlesik_pca.pdf` |
| Bu bileşende AML − ALL medyan farkı (Mann–Whitney p): MILE | 36.3 (p = 2.5e-175) | `figures/fig08b_birlesik_pca.pdf` |
| Kendi PCA'sında sınıf siluet skoru: Golub / MILE | 0.29 / 0.44 | `src/eda_compare.py` |
| Golub eğitimde anlamlı gen (ortak genlerde, q < 0.05) | 480 | `figures/fig08c_yon_tutarliligi.pdf` |
| MILE'da anlamlı gen (q < 0.05) | 3922 | `src/eda_compare.py` |
| Bütün ortak genlerde aynı yön oranı (kıyas) | %59.68 | `figures/fig08c_yon_tutarliligi.pdf` |
| Golub'da anlamlı genlerde MILE ile aynı yön oranı | %86.04 | `figures/fig08c_yon_tutarliligi.pdf` |
| Golub'da anlamlı → MILE'da aynı yönde anlamlı / ters yönde anlamlı | 388 / 45 | `figures/fig08c_yon_tutarliligi.pdf` |
| Golub t ile MILE t sıralama uyumu (Spearman ρ) | 0.44 | `figures/fig08c_yon_tutarliligi.pdf` |
| Golub en iyi 50 gen: MILE'da aynı yön / aynı yönde anlamlı | 47 / 46 | `figures/fig08c_yon_tutarliligi.pdf` |
| Golub en iyi 50 genden ters yönde olanlar | CDC25A (Golub t=6.9, MILE t=-4.8), DYNLL1 (Golub t=-5.9, MILE t=3.4), UBE2V2 (Golub t=-6.0, MILE t=4.4) | `figures/fig08c_yon_tutarliligi.pdf` |

## 9. Özet: numaralı bulgular ve modelleme için çıkarımlar

1. **Bulgu:** Golub etiketleri hasta numarasıyla eşlendi; sınıflar 27/11 (eğitim) ve 20/14 (test). Sütun sırasına göre eşleseydik testte 14 hasta yanlış etiketlenirdi.
   **Çıkarım:** Etiketler her zaman hasta numarasıyla eşlenmeli; yükleyicideki assert kontrolleri korunmalı.

2. **Bulgu:** Golub'da NaN/INF yok (0/0); değerlerin %28,67'si negatif ve negatiflerin %99,28'i 'Absent'.
   **Çıkarım:** Modüldeki INF doldurma adımına bu veride gerek yok; negatifler ölçüm gürültüsü olduğu için alttan kırpılmalı.

3. **Bulgu:** Ham değerler çok çarpık (çarpıklık 7,08); 20–16.000 kırpma + log2 sonrası 0,55. Değerlerin %32,72'si alt sınıra yığılıyor.
   **Çıkarım:** Kırpma + log2 Golub için standart ön işleme olmalı; her değere ayrı uygulandığı için sızıntı yaratmaz.

4. **Bulgu:** 1.971 prob hiçbir hastada 'Present' değil; 58 AFFX kontrol probunun 34'ü de öyle.
   **Çıkarım:** AFFX probları atılmalı; düşük ifade/varyans filtresi uygulanmalı ama yalnızca CV eğitim katlarında öğrenilmeli.

5. **Bulgu:** Hasta ortalamaları arasında yaklaşık 2,03 kat fark var (log2 sonrası medyanlar 6,09–7,65); bu fark sınıfla ilişkili değil.
   **Çıkarım:** Hasta bazında normalizasyon (ör. medyana göre ortalama) pipeline'da ablasyonla denenmeli.

6. **Bulgu:** PCA'da sınıf bilgisi verilmeden PC1 ALL ile AML'yi ayırıyor (p = 1.8e-10); ancak PC1+PC2 varyansın yalnızca %17,67'sini açıklıyor ve sınıf siluet skoru 0,29–0,30.
   **Çıkarım:** Sınıf sinyali güçlü ama tek yöne sığmıyor; öznitelik seçimi ya da çok bileşenli doğrusal modeller uygun.

7. **Bulgu:** Yalnız eğitim setinde 602 gen BH-FDR q < 0,05 ile anlamlı (410'u en az 2 kat farklı); en iyi 50 genle kümeleme sınıflarla ARI = 0,79 uyumlu.
   **Çıkarım:** Az genle iyi ayrım mümkün; ama gen seçimi nested CV'nin her katında ayrı yapılmalı (seçim yanlılığı).

8. **Bulgu:** Sınıf oranları dengesiz: Golub'da %65,3 ALL; test setinde AML oranı eğitimden yüksek (eğitimde %28,9, testte %41,2).
   **Çıkarım:** Stratified bölme, class_weight ve dengeli doğruluk/ROC-AUC gibi dengesizliğe duyarlı metrikler kullanılmalı.

9. **Bulgu:** Golub eğitim–test arasında hafif ama yaygın batch farkı: yalnız ALL'de 834 gen KS p < 0,05 (beklenen 245), FDR ile 22; hasta medyanına göre ortalayınca 2'ye iniyor.
   **Çıkarım:** Batch farkının çoğu ölçek kayması; hasta bazında normalizasyon bunu büyük ölçüde gideriyor.

10. **Bulgu:** MILE'da 750 ALL ve 542 AML var; veri quantile normalize, 0–1 ölçeğinde ve log benzeri (çarpıklık 0,70). Ortak gen sayısı 4.975.
   **Çıkarım:** MILE'a kırpma + log2 uygulanmamalı; iki veri seti ortak genler üzerinden, her biri kendi içinde ölçeklenerek kullanılmalı.

11. **Bulgu:** Ham birleştirmede veri seti farkı her şeyi bastırıyor (veri seti siluet 0,99, sınıf -0,00); gen bazında z-skor sonrası sınıf siluet 0,35, veri seti -0,18.
   **Çıkarım:** Golub'da eğitilen model MILE'a uygulanacaksa genler her veri setinde ayrı ölçeklenmeli.

12. **Bulgu:** Golub eğitimde anlamlı genlerin %86,0'ı MILE'da da aynı yönde farklı; en iyi 50 genin 47'si tutarlı. Ters çıkanlar: CDC25A, DYNLL1, UBE2V2.
   **Çıkarım:** Golub'da seçilen genler platformlar arası büyük ölçüde geçerli (AS2 için olumlu işaret); tutarsız genler yorumlanabilirlik bölümünde tartışılmalı.

### Rapordaki `\todo{koddan}` alanları

| Raporda yeri | Değer | Kaynak |
|---|---|---|
| Tablo III, MILE $n$ (ALL+AML) | 1.292 | `src/eda_mile.py` |
| Tablo III, MILE AML sayısı | 542 | `src/eda_mile.py` |
| Tablo III, MILE ölçeği | Quantile normalize, 0–1 ölçeğinde, log benzeri | `src/eda_mile.py` |
| Bölüm III-D, ortak gen sayısı | 4.975 | `src/eda_mile.py` |
| Tablo III, MILE $p$ (doğrulama) | 54.675 prob seti (raporda 54.613 yazıyor) | `src/eda_mile.py` |
| AS3, Golub sınıf oranı (doğrulama) | %65 ALL / %35 AML | `src/validate_golub.py` |

LaTeX taslağı: `reports/eda_latex_taslak.tex`
