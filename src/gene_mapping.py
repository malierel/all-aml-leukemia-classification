"""Prob adlarını gen sembollerine çeviren dosya.

Golub ve MILE farklı yongalarla ölçülmüş; prob adları birbirini tutmuyor. İki veri setini yan yana
koyabilmek için her probu bir gen sembolüne (ör. CD19) çeviriyoruz ve iki sette ortak olan genlerle çalışıyoruz.

Verdiğimiz üç karar ve nedenleri:
1. Gen sembolü boş olan problar atılıyor: hangi geni ölçtüğünü bilmiyoruz.
2. Birden fazla gene işaret eden problar ("DDR1 /// MIR4640" gibi) atılıyor: ölçülen sinyalin
   hangi genden geldiği belirsiz, yanlış gene atamak istemiyoruz.
3. Aynı gene birden fazla prob düşüyorsa ortalama ifadesi en yüksek olan prob seçiliyor.
   Gerekçe: düşük ifadeli problar çoğunlukla gürültü düzeyinde kalıyor; en yüksek sinyalli prob
   genin ifadesini en güvenilir biçimde yansıtıyor. Bu seçim etiketlere hiç bakmıyor, o yüzden sınıf
   bilgisi sızdırmıyor. Golub'da ortalamayı sadece eğitim setinden hesaplıyoruz ki test seti hiçbir
   seçimde rol oynamasın.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.config import MILE_DIR

ANNOT = {"GPL80": MILE_DIR / "GPL80-30376.txt", "GPL570": MILE_DIR / "GPL570-55999.txt"}


def probe_to_symbol(platform: str) -> tuple[pd.Series, dict]:
    """Anotasyon dosyasından prob → gen sembolü tablosu çıkarıyoruz. '#' ile başlayan satırlar açıklama."""
    a = pd.read_csv(ANNOT[platform], sep="\t", comment="#", usecols=["ID", "Gene Symbol"], dtype=str)
    a = a.set_index("ID")["Gene Symbol"]
    stats = {"n_probes": len(a), "n_empty": int(a.isna().sum()),
             "n_multi": int(a.str.contains("///", na=False).sum())}
    a = a.dropna()
    a = a[~a.str.contains("///")].str.strip()
    stats["n_mapped"] = len(a)
    return a, stats


def collapse(X: pd.DataFrame, symbols: pd.Series, ref: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Her gen için tek bir prob bırakıyoruz: ref verisinde ortalaması en yüksek olanı.
    X: hasta × prob. ref: ortalamanın hesaplanacağı hastalar (Golub'da yalnız eğitim seti)."""
    probes = [p for p in X.columns if p in symbols.index]
    sym = symbols.loc[probes]
    means = ref[probes].mean()
    # Her gen sembolü için ortalaması en büyük probun adını buluyoruz
    best = means.groupby(sym).idxmax()
    out = X[best.values].copy()
    out.columns = best.index
    counts = sym.value_counts()
    stats = {"n_probes_used": len(probes), "n_genes": len(best),
             "n_genes_multi_probe": int((counts > 1).sum()), "max_probes_per_gene": int(counts.max())}
    return out, stats
