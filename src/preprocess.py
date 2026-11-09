"""Ham değerleri analize uygun hale getiren dönüşümler.

Bu dönüşüm her değere tek tek uygulanıyor, veriden bir şey "öğrenmiyor" (ortalama, varyans gibi).
O yüzden bütün veriye uygulamak sızıntıya yol açmıyor. Bir değeri değiştirmek için başka hastalara
bakmasına gerek yok.
"""
import numpy as np
import pandas as pd

# Dudoit ve ark. (2002) ile aynı sınırlar:
# 20'nin altındaki değerler (negatifler dahil) gürültü sayılıyor, hepsini 20'ye çekiyoruz.
# 16.000'in üstünde cihaz doyuma ulaşıyor, yani daha büyük değerlere güvenemiyoruz.
LOW, HIGH = 20, 16000


def clip_log2(X: pd.DataFrame, low: int = LOW, high: int = HIGH) -> pd.DataFrame:
    """Önce değerleri [20, 16000] aralığına kırpıyoruz, sonra log2 alıyoruz.

    Neden log2? Ham değerler çok çarpık: çoğu küçük, birkaçı çok büyük. Log alınca
    dağılım daha simetrik oluyor ve "iki kat fazla ifade" farkı her düzeyde 1 birime denk geliyor.
    Neden önce kırpma? Negatif sayının logu alınamıyor; ayrıca gürültü düzeyindeki değerler
    log alınınca yapay olarak büyük farklar gibi görünüyor.
    """
    return np.log2(X.clip(lower=low, upper=high))
