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
