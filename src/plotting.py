"""Bütün şekillerin ortak ayarları ve kaydetme fonksiyonu burada.
Her şekli aynı yazı boyutuyla, aynı biçimde kaydetmek için bunu tek yere topladık."""
import matplotlib

matplotlib.use("Agg")  # Ekrana pencere açmadan doğrudan dosyaya çiziyoruz
import matplotlib.pyplot as plt

from src.config import FIGURES

# IEEE sütunu dar olduğu için yazıları küçük tutuyoruz; yine de basılı halde okunabilir kalıyor
plt.rcParams.update({
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "pdf.fonttype": 42,  # PDF'te yazılar metin olarak kalsın, LaTeX'te düzgün görünsün
})


def save_fig(fig, name: str):
    """Şekli hem PDF (vektörel, rapor için) hem de 300 dpi PNG (video ve önizleme için) olarak kaydediyoruz."""
    FIGURES.mkdir(exist_ok=True)
    # PDF'in içine oluşturma tarihi yazılmasın: yoksa içerik aynı olsa bile her çalıştırmada dosya
    # "değişmiş" görünüyor ve git geçmişi gereksiz yere kirleniyor
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(FIGURES / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return f"figures/{name}.pdf"
