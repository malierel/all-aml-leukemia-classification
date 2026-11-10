# ALL / AML Lösemi Alt Tip Sınıflandırması

Makine Öğrenmesi ve Anomali Tespiti dersi dönem projesi. Gen ifadesi mikrodizi verisinden iki lösemi alt tipini, ALL ve AML'yi ayırmaya çalışıyorum. Ana veri seti Golub ve ark. (1999), dış doğrulama için kullandığım veri seti MILE (GEO GSE13159).

Şu an ara rapor aşamasındayım: literatür taraması, veri setleri ve keşifsel veri analizi (EDA) tamam. Modelleri (sızıntısız nested CV ile en az üç yöntem) final aşamasında ekleyeceğim. Ara rapor `reports/ara_rapor.tex` dosyasında.

## Veri setleri

| Veri seti | Kaynak | Platform | Lisans |
|---|---|---|---|
| Golub ve ark. (1999) | Kaggle `crawford/gene-expression` | Affymetrix Hu6800 (GPL80) | CC0 |
| MILE Aşama I | GEO GSE13159 | Affymetrix HG-U133 Plus 2.0 (GPL570) | GEO kamuya açık veri |

Ham veriyi depoya koymadım. Aşağıdaki dosyaları elle indirip tablodaki klasörlere, aynı adlarla koymanız yeterli.

| Klasör | Dosya | Nereden |
|---|---|---|
| `data/raw/golub/` | `data_set_ALL_AML_train.csv`, `data_set_ALL_AML_independent.csv`, `actual.csv` | [Kaggle: crawford/gene-expression](https://www.kaggle.com/datasets/crawford/gene-expression) |
| `data/raw/mile/` | `GSE13159_series_matrix.txt.gz` (sıkıştırılmış haliyle kalsın) | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE13nnn/GSE13159/matrix/ |
| `data/raw/mile/` | `GPL570-55999.txt` | [GEO GPL570](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL570) sayfasının altındaki *Download full table* düğmesi |
| `data/raw/mile/` | `GPL80-30376.txt` | [GEO GPL80](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL80) sayfasının altındaki *Download full table* düğmesi |

Dosyaların yerinde olup olmadığını şu komut kontrol ediyor; eksik varsa nereden indirileceğini yazıyor:

```bash
python scripts/download_data.py
```

Kaggle API anahtarınız (`~/.kaggle/kaggle.json`) varsa Golub dosyalarını `python scripts/download_data.py golub` ile otomatik de indirebilirsiniz.

## Kurulum

Python 3.12 ile çalıştırdım. Daha yeni sürümlerde `requirements.txt` içindeki sabit numpy sürümü kurulmayabilir.

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS'ta ortamı `source .venv/bin/activate` ile açın.

## EDA'yı çalıştırma

```bash
python scripts/run_eda.py
```

Bu komut bütün EDA adımlarını sırayla çalıştırıyor ve şunları üretiyor:

- `figures/`: bütün şekiller, PDF ve 300 dpi PNG olarak
- `reports/eda_sonuclari.md`: her sayının değeri ve hangi betikten ya da şekilden geldiği
- `reports/eda_latex_taslak.tex`: kod çıktılarından otomatik oluşan EDA metni taslağı
- `data/processed/`: ara çıktılar (MILE önbelleği, ortak gen matrisleri, t-testi sonuçları)

İlk çalıştırmada 850 MB'lık MILE matrisi okunup `data/processed/` altında önbelleğe alınıyor. Benim bilgisayarımda bütün adımlar, önbellek boşken bile, yaklaşık bir dakika sürdü.

Adımlar ve ilgili kod dosyaları:

| EDA adımı | Dosya |
|---|---|
| 1. Yükleme ve etiket doğrulaması | `src/load_golub.py`, `src/validate_golub.py` |
| 2. Veri kalitesi | `src/eda_quality.py` |
| 3. Dağılım, kırpma ve log2 | `src/preprocess.py`, `src/eda_distribution.py` |
| 4. PCA, t-SNE, UMAP | `src/eda_dimred.py` |
| 5. Ayırt edici genler (yalnızca eğitim seti) | `src/eda_degenes.py` |
| 6. Golub eğitim–test batch analizi | `src/eda_batch.py` |
| 7. MILE ve prob → gen eşlemesi | `src/load_mile.py`, `src/gene_mapping.py`, `src/eda_mile.py` |
| 8. Golub–MILE karşılaştırması | `src/eda_compare.py` |
| 9. Özet ve LaTeX taslağı | `src/report_summary.py` |

## Tekrarlanabilirlik

- Rastgelelik içeren her işlem `src/config.py` içindeki `SEED = 42` ile çalışıyor.
- Kütüphane sürümleri `requirements.txt` içinde sabit.
- Rapordaki bütün şekiller ve sayılar bu depodaki kodun çıktısı. Kodu yeniden çalıştırınca aynı şekiller birebir aynı çıkıyor.
- Golub test setini yalnızca betimleme ve batch karşılaştırması için kullandım; gen seçimi gibi analizlerde sadece eğitim seti var.

## Klasörler

```
scripts/   veri kontrolü ve EDA'yı tek komutla çalıştıran betikler
src/       yükleme, ön işleme ve analiz kodu
figures/   üretilen şekiller
reports/   ara rapor ve EDA çıktıları
data/      ham ve işlenmiş veri (git'e eklenmiyor)
```

## GenAI kullanımı

EDA kodunun ve rapor metninin hazırlanmasında Claude Opus 5.5'ten, literatürdeki makalelerden bilgi edinmede Google NotebookLM'den yararlandım. Kodu ve sonuçları gözden geçirip doğruladım.
