# ALL / AML Lösemi Alt Tip Sınıflandırması (Golub 1999 + MILE GSE13159)

Dönem projesi: gen ifadesi mikrodizi verisinden ALL ve AML alt tip sınıflandırması.
Ara rapor: EDA, literatür, veri setleri. Final: sızıntısız nested CV ile ML karşılaştırması.

## Veri setleri
| Veri seti | Kaynak | Platform | Lisans |
|---|---|---|---|
| Golub ve ark. (1999) | Kaggle `crawford/gene-expression` | Affymetrix Hu6800 (GPL80) | CC0 |
| MILE Aşama I | GEO GSE13159 | Affymetrix HG-U133 Plus 2.0 (GPL570) | GEO kamuya açık veri |

Ham veri depoya konmaz; aşağıdaki betikle indirilir.

## Kurulum
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```
Golub verisi için Kaggle API anahtarı gerekir: Kaggle > Settings > API > *Create New Token*,
inen `kaggle.json` dosyasını `~/.kaggle/` (Windows: `C:\Users\<ad>\.kaggle\`) içine koyun.

## Çalıştırma
```bash
python scripts/download_data.py golub
python src/load_golub.py          # temizleme + etiket eşleştirme doğrulaması
python scripts/download_data.py mile
```

## Tekrarlanabilirlik
- Sabit seed: `src/config.py` içinde `SEED = 42`
- Kütüphane sürümleri `requirements.txt` içinde sabitlenmiştir.
- Rapordaki tüm şekil ve tablolar bu depodaki betiklerden üretilir.

## Depo yapısı
```
scripts/   veri indirme ve tek komutluk çalıştırma betikleri
src/       yükleme, ön işleme ve analiz modülleri
notebooks/ keşif amaçlı notebook'lar
figures/   üretilen şekiller
reports/   ara ve final rapor
data/      ham ve işlenmiş veri (git'e eklenmez)
```

## GenAI kullanımı
Bu projede kullanılan GenAI araçları rapordaki GenAI Kullanım Beyanı'nda listelenmiştir.
