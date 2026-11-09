"""EDA 9. adım: bütün adımların sonuçlarından numaralı bulgular, rapordaki boş alanlar için sayı tablosu
ve LaTeX taslağı üretiyoruz.

Buradaki metinlerde hiçbir sayıyı elle yazmıyoruz; hepsi R sözlüğünden, yani analizlerin kendi
çıktısından geliyor. Böylece analizi yeniden çalıştırınca rapor metnindeki sayılar da kendiliğinden güncelleniyor.
R[1] ... R[8], run_eda.py'deki her adımın sonuç sözlüğü.
"""


import re

# Sayının okunuşundaki son kelime. Türkçede sayıdan sonra gelen ek bu kelimeye göre değişiyor:
# "%28,67'si" (yirmi sekiz virgül altmış yedi → yedi'si), "410'u" (dört yüz on → on'u) gibi.
_BIRLER = ["sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def _son_kelime(sayi: str) -> str:
    """'28,67' → 'yedi', '4.975' → 'beş', '50' → 'elli', '86,0' → 'sıfır'."""
    sayi = sayi.replace(".", "")
    parca = sayi.split(",")[-1]  # Ondalıklıysa okunuş virgülden sonraki kısımla bitiyor
    if int(parca) == 0:
        return "sıfır"
    sifir = len(parca) - len(parca.rstrip("0"))  # Sondaki sıfır sayısı hangi basamakta bittiğini söylüyor
    rakam = int(parca.rstrip("0")[-1])
    if sifir == 0:
        return _BIRLER[rakam]
    if sifir == 1:
        return _ONLAR[rakam]
    return "yüz" if sifir == 2 else "bin"


def _ek(kelime: str, tur: str) -> str:
    """Büyük ve küçük ünlü uyumuna göre eki kuruyoruz."""
    unluler = [c for c in kelime if c in "aıoueiöü"]
    son, unluyle_biter = unluler[-1], kelime[-1] in "aıoueiöü"
    dar = {"a": "ı", "ı": "ı", "o": "u", "u": "u", "e": "i", "i": "i", "ö": "ü", "ü": "ü"}[son]
    genis = "a" if son in "aıou" else "e"
    if tur == "iyelik":            # %28,67'si, 14'ü
        return ("s" if unluyle_biter else "") + dar
    if tur == "iyelik_belirtme":   # %17,67'sini
        return ("s" if unluyle_biter else "") + dar + "n" + dar
    if tur == "iyelik_ilgi":       # %86'sının
        return ("s" if unluyle_biter else "") + dar + "n" + dar + "n"
    return ("y" if unluyle_biter else "") + genis  # yönelme: 0,55'e, 2'ye


_EK_TURU = {**{e: "iyelik" for e in ["i", "ı", "u", "ü", "si", "sı", "su", "sü"]},
            **{e: "iyelik_belirtme" for e in ["ini", "ını", "unu", "ünü", "sini", "sını", "sunu", "sünü"]},
            **{e: "iyelik_ilgi" for e in ["inin", "ının", "unun", "ünün", "sinin", "sının", "sunun", "sünün"]},
            **{e: "yonelme" for e in ["e", "a", "ye", "ya"]}}


def ekleri_duzelt(metin: str) -> str:
    """Metindeki her "sayı'ek" kalıbını bulup eki sayının okunuşuna göre yeniden yazıyoruz.
    Böylece analiz yeniden çalışıp sayılar değişse de Türkçe ekler doğru kalıyor."""
    def duzelt(m):
        sayi, ek = m.group(1), m.group(2)
        return f"{sayi}'{_ek(_son_kelime(sayi), _EK_TURU[ek])}"
    kalip = "|".join(sorted(_EK_TURU, key=len, reverse=True))  # Uzun ekler önce denensin
    return re.sub(rf"(\d[\d.,]*\d|\d)'({kalip})(?![a-zçğıöşü])", duzelt, metin)


def tr(x: float, d: int = 2) -> str:
    """Sayıyı Türkçe biçimde yazıyoruz: ondalık ayırıcı virgül (0,29)."""
    return f"{x:.{d}f}".replace(".", ",")


def tr_int(n: int) -> str:
    """Binlik ayırıcı nokta (4.975), raporun geri kalanıyla aynı biçim."""
    return f"{n:,}".replace(",", ".")


def sci(x: float) -> str:
    """Küçük p-değerlerini LaTeX'te 4,5 \\times 10^{-12} biçiminde yazıyoruz."""
    m, e = f"{x:.1e}".split("e")
    return f"${m.replace('.', '{,}')} \\times 10^{{{int(e)}}}$"


def findings(R: dict) -> list[tuple[str, str]]:
    """Her bulgu: (ne gördük, modellemeye etkisi)."""
    r1, r2, r3, r4, r5, r6, r7, r8 = (R[i] for i in range(1, 9))
    n_golub = sum(r1["train_counts"].values()) + sum(r1["test_counts"].values())
    n_all_golub = r1["train_counts"]["ALL"] + r1["test_counts"]["ALL"]
    return [
        (f"Golub etiketleri hasta numarasıyla eşlendi; sınıflar {r1['train_counts']['ALL']}/{r1['train_counts']['AML']} "
         f"(eğitim) ve {r1['test_counts']['ALL']}/{r1['test_counts']['AML']} (test). Sütun sırasına göre eşleseydik "
         f"testte {r1['test_naive_mislabeled']} hasta yanlış etiketlenirdi.",
         "Etiketler her zaman hasta numarasıyla eşlenmeli; yükleyicideki assert kontrolleri korunmalı."),
        (f"Golub'da NaN/INF yok ({r2['vals_all']['n_nan']}/{r2['vals_all']['n_inf']}); değerlerin "
         f"%{tr(r2['vals_all']['neg_pct'])}'i negatif ve negatiflerin %{tr(r2['neg_call_dist'].get('A', 0))}'i 'Absent'.",
         "Modüldeki INF doldurma adımına bu veride gerek yok; negatifler ölçüm gürültüsü olduğu için alttan kırpılmalı."),
        (f"Ham değerler çok çarpık (çarpıklık {tr(r3['skew_raw'])}); 20–16.000 kırpma + log2 sonrası {tr(r3['skew_log'])}. "
         f"Değerlerin %{tr(r3['clipped_low_pct'])}'i alt sınıra yığılıyor.",
         "Kırpma + log2 Golub için standart ön işleme olmalı; her değere ayrı uygulandığı için sızıntı yaratmaz."),
        (f"{tr_int(r2['never_P_all'])} prob hiçbir hastada 'Present' değil; 58 AFFX kontrol probunun "
         f"{r2['never_P_affx']}'ü de öyle.",
         "AFFX probları atılmalı; düşük ifade/varyans filtresi uygulanmalı ama yalnızca CV eğitim katlarında öğrenilmeli."),
        (f"Hasta ortalamaları arasında yaklaşık {tr(r3['log_mean_fold'])} kat fark var (log2 sonrası medyanlar "
         f"{tr(r3['log_median_min'])}–{tr(r3['log_median_max'])}); bu fark sınıfla ilişkili değil.",
         "Hasta bazında normalizasyon (ör. medyana göre ortalama) pipeline'da ablasyonla denenmeli."),
        (f"PCA'da sınıf bilgisi verilmeden PC1 ALL ile AML'yi ayırıyor (p = {r4['best_pc_class_p']:.1e}); ancak PC1+PC2 "
         f"varyansın yalnızca %{tr(r4['pc_var'][0] + r4['pc_var'][1])}'ini açıklıyor ve sınıf siluet skoru "
         f"{tr(r4['sil_class_pca2'])}–{tr(r4['sil_class_umap'])}.",
         "Sınıf sinyali güçlü ama tek yöne sığmıyor; öznitelik seçimi ya da çok bileşenli doğrusal modeller uygun."),
        (f"Yalnız eğitim setinde {tr_int(r5['n_sig_05'])} gen BH-FDR q < 0,05 ile anlamlı "
         f"({tr_int(r5['n_sig_big'])}'i en az 2 kat farklı); en iyi 50 genle kümeleme sınıflarla ARI = {tr(r5['ari'])} uyumlu.",
         "Az genle iyi ayrım mümkün; ama gen seçimi nested CV'nin her katında ayrı yapılmalı (seçim yanlılığı)."),
        (f"Sınıf oranları dengesiz: Golub'da %{tr(100 * n_all_golub / n_golub, 1)} ALL; test setinde AML oranı "
         f"eğitimden yüksek (eğitimde %{tr(r6['aml_frac_train'], 1)}, testte %{tr(r6['aml_frac_test'], 1)}).",
         "Stratified bölme, class_weight ve dengeli doğruluk/ROC-AUC gibi dengesizliğe duyarlı metrikler kullanılmalı."),
        (f"Golub eğitim–test arasında hafif ama yaygın batch farkı: yalnız ALL'de {r6['ks_raw_p05']} gen KS p < 0,05 "
         f"(beklenen {r6['ks_expected']:.0f}), FDR ile {r6['ks_raw_q05']}; hasta medyanına göre ortalayınca "
         f"{r6['ks_norm_q05']}'ye iniyor.",
         "Batch farkının çoğu ölçek kayması; hasta bazında normalizasyon bunu büyük ölçüde gideriyor."),
        (f"MILE'da {r7['n_all']} ALL ve {r7['n_aml']} AML var; veri quantile normalize, 0–1 ölçeğinde ve log benzeri "
         f"(çarpıklık {tr(r7['skew'])}). Ortak gen sayısı {tr_int(r7['n_common'])}.",
         "MILE'a kırpma + log2 uygulanmamalı; iki veri seti ortak genler üzerinden, her biri kendi içinde ölçeklenerek kullanılmalı."),
        (f"Ham birleştirmede veri seti farkı her şeyi bastırıyor (veri seti siluet {tr(r8['sil_ds_raw'])}, sınıf "
         f"{tr(r8['sil_class_raw'])}); gen bazında z-skor sonrası sınıf siluet {tr(r8['sil_class_z'])}, veri seti "
         f"{tr(r8['sil_ds_z'])}.",
         "Golub'da eğitilen model MILE'a uygulanacaksa genler her veri setinde ayrı ölçeklenmeli."),
        (f"Golub eğitimde anlamlı genlerin %{tr(r8['same_dir_sig'], 1)}'i MILE'da da aynı yönde farklı; en iyi 50 genin "
         f"{r8['top_same_dir']}'si tutarlı. Ters çıkanlar: {', '.join(s.split(' (')[0] for s in r8['top_opposite'])}.",
         "Golub'da seçilen genler platformlar arası büyük ölçüde geçerli (AS2 için olumlu işaret); tutarsız genler "
         "yorumlanabilirlik bölümünde tartışılmalı."),
    ]


def todo_table(R: dict) -> list[tuple[str, str, str]]:
    """ara_rapor.tex'teki \\todo{koddan} ve ilgili boş alanlar: (yer, değer, kaynak)."""
    r1, r7 = R[1], R[7]
    n_golub = sum(r1["train_counts"].values()) + sum(r1["test_counts"].values())
    n_all_golub = r1["train_counts"]["ALL"] + r1["test_counts"]["ALL"]
    return [
        ("Tablo III, MILE $n$ (ALL+AML)", tr_int(r7["n_all"] + r7["n_aml"]), "src/eda_mile.py"),
        ("Tablo III, MILE AML sayısı", tr_int(r7["n_aml"]), "src/eda_mile.py"),
        ("Tablo III, MILE ölçeği", "Quantile normalize, 0–1 ölçeğinde, log benzeri", "src/eda_mile.py"),
        ("Bölüm III-D, ortak gen sayısı", tr_int(r7["n_common"]), "src/eda_mile.py"),
        ("Tablo III, MILE $p$ (doğrulama)", f"{tr_int(r7['n_probes_raw'])} prob seti (raporda 54.613 yazıyor)",
         "src/eda_mile.py"),
        ("AS3, Golub sınıf oranı (doğrulama)",
         f"%{100 * n_all_golub / n_golub:.0f} ALL / %{100 * (n_golub - n_all_golub) / n_golub:.0f} AML",
         "src/validate_golub.py"),
    ]


def summary_md(R: dict) -> list[str]:
    lines = ["## 9. Özet: numaralı bulgular ve modelleme için çıkarımlar", ""]
    for i, (f, imp) in enumerate(findings(R), 1):
        lines += [f"{i}. **Bulgu:** {f}", f"   **Çıkarım:** {imp}", ""]
    lines += ["### Rapordaki `\\todo{koddan}` alanları", "", "| Raporda yeri | Değer | Kaynak |", "|---|---|---|"]
    lines += [f"| {a} | {b} | `{c}` |" for a, b, c in todo_table(R)]
    lines += ["", "LaTeX taslağı: `reports/eda_latex_taslak.tex`", ""]
    return [ekleri_duzelt(s) for s in lines]  # Sayıdan sonra gelen ekleri okunuşa göre düzeltiyoruz


def fig(path: str, caption: str, label: str, wide: bool = False, optional: bool = False) -> str:
    """Bir şekil bloğu yazıyoruz. İki sütunluk şekiller figure* ile. İsteğe bağlı olanlar yorum satırı."""
    env = "figure*" if wide else "figure"
    width = "\\textwidth" if wide else "\\columnwidth"
    # Sadece dosya adını yazıyoruz; klasörü raporun başındaki \graphicspath buluyor.
    # Böylece aynı metin hem Overleaf'te (figures/) hem yerelde (../figures/) çalışıyor.
    name = path.split("/")[-1]
    block = (f"\\begin{{{env}}}[t]\n\\centering\n\\includegraphics[width={width}]{{{name}}}\n"
             f"\\caption{{{caption}}}\n\\label{{{label}}}\n\\end{{{env}}}")
    if optional:
        block = "\n".join("% " + ln for ln in block.splitlines())
    return block


def latex(R: dict) -> str:
    r1, r2, r3, r4, r5, r6, r7, r8 = (R[i] for i in range(1, 9))
    p = lambda x, d=2: f"\\%{tr(x, d)}"  # LaTeX'te yüzde işaretinin önüne ters bölü gerekiyor
    opp = ", ".join(s.split(" (")[0] for s in r8["top_opposite"])
    out = []
    out.append(r"""% =====================================================================
% EDA bölümü için ÖNERİLEN taslak metin. Otomatik üretildi: python scripts/run_eda.py
% Bütün sayılar kodun çıktısından geliyor. Kendi cümlelerinle uyarlayıp ara_rapor.tex'e ekle.
% Şekillerde sadece dosya adı var; rapor önsözüne \graphicspath{{figures/}{../figures/}} eklenmeli.
% 6 sayfa sınırı için ana metne 5-6 şekil yeter; isteğe bağlı şekiller yorum satırı olarak duruyor.
% =====================================================================

% ---------------------------------------------------------------------
% 1) ÖZET (abstract) içindeki \todo{EDA bulgularının 1--2 cümlelik özeti.} yerine öneri:
% ---------------------------------------------------------------------""")
    out.append(
        f"% EDA, Golub verisinde sınıf bilgisi kullanılmadan PCA'nın ALL ve AML'yi ayırdığını, eğitim setinde "
        f"{tr_int(r5['n_sig_05'])} genin FDR düzeltmesi sonrası anlamlı olduğunu ve bu genlerin "
        f"{p(r8['same_dir_sig'], 0)}'sının bağımsız MILE verisinde de aynı yönde farklılaştığını göstermiştir; "
        f"buna karşın iki platform arasındaki ölçek farkı, veri setine özgü normalizasyonu zorunlu kılmaktadır.")
    out.append(r"""
% ---------------------------------------------------------------------
% 2) Bölüm III-D "Seçim Gerekçesi ve Uyumluluk" için öneriler
% ---------------------------------------------------------------------
% "Ortak gen sayısı: \todo{koddan}." yerine:""")
    out.append(
        f"% Sembolü olmayan ve birden fazla gene eşlenen problar atıldıktan, aynı gene düşen problardan ortalama "
        f"ifadesi en yüksek olan seçildikten sonra iki platformda {tr_int(r7['n_common'])} ortak gen kalmıştır.")
    out.append(
        "% \"İki sete aynı dönüşüm (kırpma ve log$_2$) uygulanacaktır.\" cümlesi EDA bulgusuyla çelişiyor. Yerine:\n"
        "% Golub verisine kırpma (20--16.000) ve log$_2$ dönüşümü uygulanacaktır. MILE verisi ise GEO'da quantile "
        "normalize edilmiş ve 0--1 aralığına ölçeklenmiş olarak yayımlandığından bu dönüşüm ona uygulanmayacak; iki "
        "veri seti ortak genler üzerinde, her biri kendi içinde ölçeklenerek karşılaştırılacaktır.\n"
        f"% Tablo III, MILE satırları: $n$ = {tr_int(r7['n_all'] + r7['n_aml'])}, AML = {tr_int(r7['n_aml'])}, "
        f"Ölçek = Quantile normalize, 0--1, log benzeri.")

    out.append(r"""
% ---------------------------------------------------------------------
% 3) EDA BÖLÜMÜ
% ---------------------------------------------------------------------
\section{Keşifsel Veri Analizi (EDA)}
Bütün analizler Python ile yapılmış ve tek komutla (\texttt{python scripts/run\_eda.py}) yeniden üretilebilir. Golub test seti yalnızca betimleme ve batch karşılaştırması için kullanılmış; ayırt edici gen analizi yalnızca eğitim seti üzerinde yapılmıştır.

\subsection{Veri Kalitesi}""")
    out.append(
        f"Golub etiketleri \\texttt{{actual.csv}} dosyasından hasta numarasına göre eşlenmiş ve sınıf sayıları "
        f"{r1['train_counts']['ALL']}/{r1['train_counts']['AML']} (eğitim) ve "
        f"{r1['test_counts']['ALL']}/{r1['test_counts']['AML']} (test) olarak doğrulanmıştır. Test dosyasında hasta "
        f"sütunları numara sırasında olmadığından, etiketler sütun sırasına göre atansaydı 34 test hastasının "
        f"{r1['test_naive_mislabeled']}'ü yanlış etiketlenecekti. Veride eksik ya da sonsuz değer yoktur. Değerlerin "
        f"{p(r2['vals_all']['neg_pct'])}'i negatiftir (en küçük {tr_int(r2['vals_all']['min'])}); negatif değerlerin "
        f"{p(r2['neg_call_dist'].get('A', 0))}'i Affymetrix tarafından ``Absent'' olarak işaretlenmiştir, yani bu değerler "
        f"arka plan çıkarımından kaynaklanan ölçüm gürültüsüdür. P/A/M çağrıları sınıf ve setler arasında benzerdir "
        f"(``Present'' oranı {p(r2['call_table']['P'].min(), 1)}--{p(r2['call_table']['P'].max(), 1)}). "
        f"{tr_int(r2['never_P_all'])} prob hiçbir hastada ``Present'' değildir; 58 AFFX kontrol probunun "
        f"{r2['never_P_affx']}'ü de bu gruptadır.")
    # MILE'ın veri kalitesi: yönerge EDA'yı iki veri seti için de istiyor
    tis = r7["tissue_counts"]
    bm = int(tis.xs("bone marrow", level="tissue").sum())
    pb = int(tis.xs("peripheral blood", level="tissue").sum())
    out.append(
        f"\nMILE matrisinde {tr_int(r7['n_probes_raw'])} prob bulunmaktadır; bunların {r7['n_all_nan']}'i (tamamı AFFX "
        f"kontrol probu) bütün hastalarda boştur ve çıkarıldıktan sonra eksik değer kalmamaktadır. Değerler 0--1 "
        f"aralığındadır ve negatif değer yoktur. Her hastanın medyanı aynıdır ({tr(r7['sample_median_min'], 4)}) ve "
        f"sıralanmış hasta değerleri ortak sıralamadan en fazla {tr(r7['sorted_max_diff'], 4)} sapmaktadır; bu, verinin "
        f"quantile normalize edildiğini göstermektedir. Çarpıklık {tr(r7['skew'])} ile Golub'un log$_2$ sonrası "
        f"değerine yakındır, bir kez daha log alındığında ise {tr(r7['skew_after_log'])} olmaktadır; bu nedenle MILE "
        f"verisinin zaten log benzeri bir ölçekte olduğu ve kırpma ile log$_2$ dönüşümünün uygulanmaması gerektiği "
        f"sonucuna varılmıştır. Seçilen ALL ve AML hastalarının {tr_int(bm)}'i kemik iliği, {pb}'i periferik kan "
        f"örneğidir.")
    out.append(fig("figures/fig02_pma_dagilimi.pdf", "Set ve sınıfa göre P/M/A çağrı dağılımı.", "fig:pma",
                   optional=True))

    out.append("\n\\subsection{Betimsel İstatistikler ve Dönüşüm}")
    # Sınıf dağılımı: yönergenin "betimsel istatistikler ve sınıf dağılımı" maddesi için
    g_all = r1["train_counts"]["ALL"] + r1["test_counts"]["ALL"]
    g_aml = r1["train_counts"]["AML"] + r1["test_counts"]["AML"]
    m_n = r7["n_all"] + r7["n_aml"]
    out.append(
        f"Sınıf dağılımı iki veri setinde de dengesizdir: Golub'da {g_all} ALL ve {g_aml} AML "
        f"({p(100 * g_all / (g_all + g_aml), 1)} ALL), MILE'da {r7['n_all']} ALL ve {r7['n_aml']} AML "
        f"({p(100 * r7['n_all'] / m_n, 1)} ALL) bulunmaktadır. Golub test setinde AML oranı eğitim setinden "
        f"yüksektir ({p(r6['aml_frac_train'], 1)} ve {p(r6['aml_frac_test'], 1)}). MILE'da AML grubunun "
        f"{r7['subclass_counts'].loc[('AML', 'AML with normal karyotype + other abnormalities')]}'i tek bir alt sınıfa "
        f"(normal karyotip ve diğer anomaliler) aittir.\n")
    out.append(
        f"Ham ifade değerleri aşırı sağa çarpıktır (çarpıklık {tr(r3['skew_raw'])}). Dudoit ve ark.~\\cite{{dudoit2002}} "
        f"izlenerek değerler 20--16.000 aralığına kırpılmış ve log$_2$ dönüşümü uygulanmıştır; çarpıklık "
        f"{tr(r3['skew_log'])}'e inmiştir (Şekil~\\ref{{fig:dagilim}}). Değerlerin {p(r3['clipped_low_pct'])}'i alt "
        f"sınıra kırpılmaktadır. Dönüşümden sonra da hastalar arasında ölçek farkı sürmektedir: hasta medyanları "
        f"{tr(r3['log_median_min'])}--{tr(r3['log_median_max'])} aralığında, en uç iki hastanın ortalamaları arasında "
        f"yaklaşık {tr(r3['log_mean_fold'])} kat fark vardır. ALL ve AML ortalamaları neredeyse aynı olduğundan "
        f"({tr(r3['log_mean_ALL'], 3)} ve {tr(r3['log_mean_AML'], 3)}) bu fark teknik kaynaklıdır.")
    out.append(fig("figures/fig03a_dagilim_ham_log.pdf",
                   "(a) Ham ifade değerleri (kesikli çizgiler kırpma sınırları), (b) kırpma ve log$_2$ sonrası sınıf "
                   "bazında dağılım.", "fig:dagilim"))
    out.append(fig("figures/fig03b_ornek_kutu.pdf", "Kırpma ve log$_2$ sonrası hasta bazında kutu grafiği.",
                   "fig:kutu", wide=True, optional=True))

    out.append("\n\\subsection{Boyut İndirgeme}")
    out.append(
        f"AFFX probları çıkarılmış {tr_int(r4['n_genes'])} gen üzerinde yapılan PCA'da ilk iki bileşen varyansın "
        f"{p(r4['pc_var'][0] + r4['pc_var'][1])}'ini açıklamaktadır; varyansın \\%50'si için {r4['n_pc_50']}, "
        f"\\%90'ı için {r4['n_pc_90']} bileşen gerekmektedir. Sınıf bilgisi kullanılmadığı halde PC1 ALL ve AML'yi "
        f"ayırmaktadır (Mann--Whitney {sci(r4['best_pc_class_p'])}; Şekil~\\ref{{fig:pca}}), bu da Golub ve "
        f"ark.~\\cite{{golub1999}}'nin gözlemiyle uyumludur. Ancak ayrım kısmidir: sınıf siluet skoru PCA, t-SNE ve "
        f"UMAP'te {tr(r4['sil_class_tsne'])}--{tr(r4['sil_class_umap'])} aralığındadır. Eğitim ve test hastaları "
        f"büyük ölçüde iç içedir (set siluet skoru {tr(r4['sil_set_pca2'])}--{tr(r4['sil_set_tsne'])}). t-SNE ve "
        f"UMAP'te eğitim setindeki AML hastaları sıkı bir küme oluştururken test setindeki AML hastaları daha "
        f"dağınıktır (Şekil~\\ref{{fig:tsne}}); bu, test AML'lerinin daha heterojen olduğuna işaret etmektedir. "
        f"MILE'da da ortak genler üzerinde yapılan PCA iki sınıfı ayırmakta, sınıf siluet skoru Golub'dakinden "
        f"yüksektir ({tr(r8['sil_class_own_MILE'])} ve {tr(r8['sil_class_own_Golub'])}).")
    out.append(fig("figures/fig04b_pca_pc1_pc2.pdf", "PC1--PC2 düzlemi: (a) sınıfa göre, (b) sete göre.", "fig:pca"))
    out.append(fig("figures/fig04a_pca_varyans.pdf", "PCA açıklanan varyans.", "fig:pcavar", optional=True))
    out.append(fig("figures/fig04c_tsne_umap.pdf",
                   "Golub verisinin (a) t-SNE ve (b) UMAP gömmeleri; daireler eğitim, üçgenler test hastaları.",
                   "fig:tsne"))

    out.append("\n\\subsection{Ayırt Edici Genler}")
    out.append(
        f"Yalnızca eğitim setinde (38 hasta), iki sınıfta da sabit olan {r5['n_const']} gen çıkarıldıktan sonra kalan "
        f"{tr_int(r5['n_tested'])} gene Welch t-testi ve Benjamini--Hochberg FDR düzeltmesi uygulanmıştır. "
        f"{tr_int(r5['n_sig_05'])} gen $q<0{{,}}05$ ile anlamlıdır ({r5['n_up_AML']}'ü AML'de, {r5['n_up_ALL']}'i "
        f"ALL'de yüksek); bunların {r5['n_sig_big']}'u en az iki kat fark göstermektedir. En anlamlı 50 genle yapılan "
        f"hiyerarşik kümeleme hastaları sınıflarıyla yüksek uyumla ayırmaktadır (düzeltilmiş Rand indeksi "
        f"{tr(r5['ari'])}; Şekil~\\ref{{fig:isi}}). Listenin başında CST3, Zyxin, CD33 (AML) ve CD19, TCF3 (ALL) gibi "
        f"soy belirteçleri yer almaktadır. Bu genler tüm eğitim seti üzerinde seçildiğinden kümeleme sonucu iyimserdir; "
        f"modellemede gen seçimi çapraz doğrulama katları içinde yapılacaktır~\\cite{{ambroise2002}}.")
    out.append(fig("figures/fig05b_isi_haritasi_top50.pdf",
                   "Eğitim setinde en anlamlı 50 genin z-skor ısı haritası ve hiyerarşik kümeleme.", "fig:isi"))
    out.append(fig("figures/fig05a_volcano.pdf", "Volcano grafiği (eğitim seti).", "fig:volcano", optional=True))

    out.append("\n\\subsection{Batch Analizi}")
    out.append(
        f"Test setinde AML oranı daha yüksek olduğundan ({p(r6['aml_frac_train'], 1)} ve {p(r6['aml_frac_test'], 1)}) "
        f"eğitim--test karşılaştırması yalnızca ALL hastaları arasında yapılmıştır. Test hastalarının genel ifade "
        f"düzeyi her iki sınıfta da biraz daha düşüktür ve ALL hastalarının PCA'sında PC2 setleri ayırmaktadır "
        f"(p = {sci(r6['pca_all_best_p'])}). Gen bazında KS testinde {r6['ks_raw_p05']} gen $p<0{{,}}05$ vermektedir "
        f"(şans eseri beklenen {r6['ks_expected']:.0f}), ancak FDR sonrası yalnızca {r6['ks_raw_q05']} gen anlamlı "
        f"kalmaktadır; her hasta kendi medyanına göre ortalandığında bu sayı {r6['ks_norm_q05']}'ye düşmektedir. "
        f"Batch farkı zayıf, yaygın ve büyük ölçüde ölçek kaymasından kaynaklıdır.")
    out.append(
        f"\nGolub ve MILE ortak {tr_int(r7['n_common'])} gen üzerinde karşılaştırılmıştır. MILE {tr_int(r7['n_all'])} "
        f"ALL ve {tr_int(r7['n_aml'])} AML hastası içermekte ve quantile normalize edilmiş 0--1 ölçeğinde "
        f"yayımlanmaktadır. Ham değerler doğrudan birleştirildiğinde PC1 varyansın {p(r8['pc1_raw'], 1)}'ini açıklamakta "
        f"ve yalnızca veri setini ayırmaktadır (veri seti siluet {tr(r8['sil_ds_raw'])}, sınıf siluet "
        f"{tr(r8['sil_class_raw'])}). Her gen kendi veri seti içinde z-skora çevrildiğinde veri seti farkı kaybolmakta, "
        f"ALL/AML ayrımı ise iki veri setinde de aynı yönde ortaya çıkmaktadır (Şekil~\\ref{{fig:birlesik}}). "
        f"Golub eğitim setinde anlamlı bulunan genlerin {p(r8['same_dir_sig'], 1)}'i MILE'da da aynı yönde farklıdır "
        f"(tüm genlerde bu oran {p(r8['same_dir_all'], 1)}); en anlamlı 50 genin {r8['top_same_dir']}'si tutarlıdır. "
        f"Ters yönde çıkan genler ({opp}) arasındaki CDC25A, Golub eğitim--test karşılaştırmasında da batch farkı "
        f"gösteren tek ``en iyi 50'' genidir (Şekil~\\ref{{fig:yon}}).")
    out.append(fig("figures/fig08b_birlesik_pca.pdf",
                   "Golub ve MILE ortak genlerde birleşik PCA: (a) ham değerler, (b)--(c) gen bazında veri seti içi "
                   "z-skor.", "fig:birlesik", wide=True))
    out.append(fig("figures/fig08c_yon_tutarliligi.pdf",
                   "Golub eğitim ve MILE t istatistikleri; renkli noktalar Golub'da anlamlı genler.", "fig:yon"))
    out.append(fig("figures/fig06a_batch_dagilim.pdf", "Golub eğitim--test karşılaştırması.", "fig:batch",
                   optional=True))
    out.append(fig("figures/fig06b_ks_pdegerleri.pdf", "Gen bazında eğitim--test KS p-değerleri.", "fig:ks",
                   optional=True))
    out.append(fig("figures/fig07a_mile_alt_siniflar.pdf", "MILE ALL ve AML alt sınıfları.", "fig:mile",
                   optional=True))
    out.append(fig("figures/fig07b_mile_olcek.pdf", "MILE değer dağılımı ve hasta bazında kutu grafiği.",
                   "fig:mileolcek", optional=True))
    out.append(fig("figures/fig08a_golub_mile_olcek.pdf", "Golub ve MILE ölçek karşılaştırması.", "fig:olcek",
                   wide=True, optional=True))

    out.append("\n\\subsection{Bulguların Özeti ve Modelleme İçin Çıkarımlar}\n\\begin{enumerate}[leftmargin=*]")
    for f_, imp in findings(R):
        # Markdown için yazılmış metni LaTeX'e çeviriyoruz: % ve _ LaTeX'te özel karakter, önlerine \ gerekiyor
        esc = lambda s: s.replace("%", "\\%").replace("_", "\\_")
        out.append(f"  \\item {esc(f_)} \\textit{{Çıkarım:}} {esc(imp)}")
    out.append("\\end{enumerate}\n")
    return ekleri_duzelt("\n".join(out))  # Sayıdan sonra gelen ekleri okunuşa göre düzeltiyoruz
