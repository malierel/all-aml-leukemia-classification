# ALL / AML Lösemi Alt Tip Sınıflandırması (Golub 1999 + MILE GSE13159)

Dönem projesi: gen ifadesi mikrodizi verisinden ALL ve AML alt tip sınıflandırması.
Ara rapor: EDA, literatür, veri setleri. Final: sızıntısız nested CV ile ML karşılaştırması.

## Veri setleri
| Veri seti | Kaynak | Platform | Lisans |
|---|---|---|---|
| Golub ve ark. (1999) | Kaggle `crawford/gene-expression` | Affymetrix Hu6800 (GPL80) | CC0 |
| MILE Aşama I | GEO GSE13159 | Affymetrix HG-U133 Plus 2.0 (GPL570) | GEO kamuya açık veri |

Ham veri depoya konmaz. Dosyaları aşağıdaki adreslerden elle indirip belirtilen klasörlere,
belirtilen adlarla koyun.

## Veriyi indirme
| Klasör | Dosya | Nereden |
|---|---|---|
| `data/raw/golub/` | `data_set_ALL_AML_train.csv`, `data_set_ALL_AML_independent.csv`, `actual.csv` | [Kaggle: crawford/gene-expression](https://www.kaggle.com/datasets/crawford/gene-expression) |
| `data/raw/mile/` | `GSE13159_series_matrix.txt.gz` (açmadan bırakın) | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE13nnn/GSE13159/matrix/ |
| `data/raw/mile/` | `GPL570-55999.txt` | [GEO GPL570](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL570) sayfasının altındaki *Download full table* |
| `data/raw/mile/` | `GPL80-30376.txt` | [GEO GPL80](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL80) sayfasının altındaki *Download full table* |

Dosyaların yerinde olup olmadığını kontrol etmek için:
```bash
python scripts/download_data.py
```
İsteğe bağlı: Kaggle API anahtarınız (`~/.kaggle/kaggle.json`) varsa Golub dosyaları
`python scripts/download_data.py golub` ile otomatik indirilebilir.

## Kurulum
Python 3.12 ile test edilmiştir.
```bash
py -3.12 -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

## Çalıştırma (EDA)
```bash
python scripts/run_eda.py
```
Bu tek komut bütün EDA adımlarını sırayla çalıştırır ve şunları üretir:
- `figures/`: bütün şekiller (PDF + 300 dpi PNG)
- `reports/eda_sonuclari.md`: her bulgunun sayısı ve hangi betik/şekilden geldiği
- `reports/eda_latex_taslak.tex`: ara raporun EDA bölümü için taslak metin
- `data/processed/`: ara çıktılar (MILE önbelleği, ortak gen matrisleri, t-testi sonuçları)

İlk çalıştırmada MILE matrisi okunup önbelleğe alındığı için birkaç dakika sürebilir.

| EDA adımı | Modül |
|---|---|
| 1. Yükleme ve etiket doğrulaması | `src/load_golub.py`, `src/validate_golub.py` |
| 2. Veri kalitesi | `src/eda_quality.py` |
| 3. Dağılım ve kırpma + log2 | `src/preprocess.py`, `src/eda_distribution.py` |
| 4. PCA, t-SNE, UMAP | `src/eda_dimred.py` |
| 5. Ayırt edici genler (yalnız eğitim seti) | `src/eda_degenes.py` |
| 6. Golub eğitim–test batch analizi | `src/eda_batch.py` |
| 7. MILE ve prob → gen eşlemesi | `src/load_mile.py`, `src/gene_mapping.py`, `src/eda_mile.py` |
| 8. Golub–MILE karşılaştırması | `src/eda_compare.py` |
| 9. Özet ve LaTeX taslağı | `src/report_summary.py` |

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
