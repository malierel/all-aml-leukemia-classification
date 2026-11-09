"""Tüm EDA adımlarını sırayla çalıştırır ve reports/eda_sonuclari.md dosyasını baştan üretir.

Kullanım:  python scripts/run_eda.py
Rapordaki her sayı bu betiğin çıktısından gelir (yönerge 6.9).
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.validate_golub import validate

REPORT = ROOT / "reports" / "eda_sonuclari.md"


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
    # Windows konsolu varsayılan cp1254; Türkçe/matematik karakterleri bozulmasın diye UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    md = ["# EDA Sonuçları", "", "Bu dosya `python scripts/run_eda.py` ile otomatik üretilir; elle düzenlemeyin.", ""]
    md += step1()
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"\nYazıldı: {REPORT}")
