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
