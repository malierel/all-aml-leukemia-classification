# Proje: ALL/AML Lösemi Alt Tip Sınıflandırması (Dönem Projesi)

Bu, bireysel bir ders projesidir. Şu an **ara rapor** aşamasındayız: yalnızca EDA (keşifsel veri analizi)
yapılacak. **Model eğitimi bu aşamada yapılmaz ve puanlanmaz.**

## Referans dosyalar (önce bunları oku)
- `Donem_projesi_rapor_rehber.pdf`: dersin yönergesi. Bölüm A1 (EDA) maddeleri bu işin kapsamıdır.
- `reports/ara_rapor.tex`: ara rapor (IEEEtran, Türkçe). EDA bölümü `\todo{}` ile boş bırakıldı;
  doldurulacak sayılar da `\todo{koddan}` olarak işaretli.
- `src/config.py`, `src/load_golub.py`, `scripts/download_data.py`: mevcut iskelet.

## Çalışma kuralları (özgünlük, yönerge gereği)
1. **Git commit ATMA.** Commit'leri öğrenci kendisi atar; Git geçmişi özgünlük kanıtı olarak puanlanıyor.
   Her adımın sonunda bir commit mesajı **öner**, o kadar.
2. **Küçük adımlarla ilerle.** Bir adımı bitir, ne yaptığını ve **neden** yaptığını sade Türkçeyle açıkla,
   sonra dur ve onay bekle. Öğrenci videoda kodu kendi sesiyle anlatacak; anlamadığı kod işine yaramaz.
3. **Sayı uydurma.** Rapora girecek her sayı (örnek sayıları, ortak gen sayısı, PCA varyansı, anlamlı gen
   sayısı vb.) koddan gelmeli. Her adımda bu sayıları `reports/eda_sonuclari.md` dosyasına ekle
   (bulgu · sayı · hangi betik/şekil üretti).
4. Bir varsayım (sütun yapısı, ölçek, dosya biçimi) doğrulanmadan kullanılmaz: önce veriyi aç ve kontrol et.
   Mevcut `load_golub.py` "call sütunu hasta sütununun hemen sağındadır" varsayımını `assert` ile kontrol
   ediyor; çalıştırıp doğrula.

## Teknik kurallar
- Ortam: Windows + VS Code + `.venv`. Bağımlılıklar `requirements.txt` içinde sabit; yeni paket gerekirse
  sürümüyle oraya ekle. EDA için GPU/PyTorch gerekmez.
- Sabit seed: `src/config.py` içindeki `SEED` (t-SNE, UMAP ve her rastgele işlemde kullan).
- Ham veri `data/raw/` altında kalır, git'e girmez. İşlenmiş ara çıktılar `data/processed/` altına.
- Kod `src/` (yeniden kullanılabilir fonksiyonlar) ve `scripts/` (çalıştırılabilir adımlar) altında.
  Notebook kullanılacaksa yalnızca `notebooks/` içinde, `src/` fonksiyonlarını çağıran ince bir katman olarak.
- `python scripts/run_eda.py` tek komutla tüm şekilleri ve `eda_sonuclari.md` dosyasını yeniden üretebilmeli.
- Şekiller: `figures/` altına **PDF** (vektörel) + 300 dpi PNG; eksen etiketleri ve başlıklar Türkçe;
  IEEE tek sütun genişliğine (~3.5 inç) uygun boyut; sınıf renkleri tüm şekillerde aynı (ALL ve AML).
- Kod yorumları Türkçe, kısa ve "neden"i anlatan türden.
- Etiket kodlaması: ALL = 0, AML = 1. Eğitim/test etiketleri hasta **numarasına** göre eşlenir, sütun sırasına
  göre değil (yönergenin özel uyarısı).
- EDA'da bile sızıntıya dikkat: Golub test seti yalnızca betimleme ve batch karşılaştırması için kullanılır;
  "ayırt edici gen" analizi eğitim seti üzerinde yapılır, test seti bu analizden gen seçmek için kullanılmaz.

## EDA kapsamı (yönerge A1, sırayla)
1. **Yükleme ve doğrulama:** Golub eğitim (38) ve test (34) setlerini yükle; sınıf sayıları 27/11 ve 20/14.
2. **Veri kalitesi:** eksik/NaN/INF, negatif değer oranı, alt-üst uç değerler, P/A/M çağrı dağılımı
   (sınıf ve set bazında), hiç "Present" olmayan prob sayısı. Kontrol probları (AFFX-) ayrıca raporlanır.
3. **Dağılım ve dönüşüm:** ham dağılım vs. kırpma (ör. 20–16.000, Dudoit 2002) + log2 sonrası dağılım;
   örnek bazında kutu grafiği (örnekler arası ölçek farkı var mı?).
4. **Boyut indirgeme:** PCA (açıklanan varyans eğrisi + PC1–PC2, sınıfa ve sete göre renk), t-SNE ve UMAP.
5. **Ayırt edici genler (yalnızca eğitim seti):** Welch t-testi + Benjamini–Hochberg FDR; anlamlı gen sayısı;
   volcano grafiği; en iyi 50 gen için ısı haritası + hiyerarşik kümeleme. Golub'un 50 gen listesiyle örtüşme
   kontrol edilebilir.
6. **Batch analizi (Golub eğitim vs. test):** dağılım karşılaştırması, PCA'da set ayrışması, gen bazında
   eğitim–test farkı (ör. KS testi). Bulgu modelleme kararlarını (ölçekleme, normalizasyon) nasıl etkiler?
7. **MILE (GSE13159):** indir; örnek metadatasından ALL ve AML alt sınıflarını seç (ALL C1–C8 toplamı 750
   olmalı, AML sayısını raporla); veri ölçeğini kontrol et (log mu, ham mı?). GPL80 ve GPL570 anotasyonlarıyla
   prob → gen sembolü eşlemesi; aynı gene düşen birden fazla prob için kuralı açıkça seç ve gerekçelendir
   (ör. en yüksek ortalama ifade); ortak gen sayısını raporla. Bellek: matris ~2.096 × 54.613; gerekirse
   önce ALL/AML örneklerini süz.
8. **Golub vs. MILE karşılaştırması (ortak genlerde):** dağılımlar, birleşik PCA (veri setine ve sınıfa göre
   renk), ALL/AML ayrımının her iki sette de görülüp görülmediği; Golub'da bulunan ayırt edici genlerin MILE'da
   da aynı yönde farklı olup olmadığı.
9. **Özet:** `reports/eda_sonuclari.md` sonuna numaralı bulgular listesi ve her bulgunun modelleme için
   çıkarımı (ölçekleme, öznitelik seçimi, dengesizlik, batch). Rapordaki `\todo{koddan}` alanlarına girecek
   sayıları ayrı bir tabloda topla.

## Bitince
`reports/ara_rapor.tex` dosyasını **değiştirme**; EDA bölümü için önerilen LaTeX metnini ve
`\includegraphics` bloklarını `reports/eda_latex_taslak.tex` dosyasına yaz. Öğrenci kendi diline
uyarlayıp rapora ekleyecek.
