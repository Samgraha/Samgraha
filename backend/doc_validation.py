from typing import Tuple
from pypdf import PdfReader


REQUIRED = {
    "kk": ["kartu keluarga", "nomor kk", "nik"],
    "akta": ["akta kelahiran", "tempat/tanggal lahir", "nama ayah", "nama ibu"],
    "surat_pengantar": ["rt", "rw", "kelurahan", "kecamatan"],
}


def extract_text_from_pdf(path: str) -> str:
    """Mengambil teks dari file PDF dan mengembalikan sebagai string."""
    text = []
    reader = PdfReader(path)
    for page in reader.pages:
        txt = page.extract_text() or ""
        text.append(txt)
    return "\n".join(text)


def quick_sanity(kind: str, text: str) -> bool:
    tokens = text.lower()
    must = REQUIRED.get(kind, [])
    return all(tok in tokens for tok in must[:2])  # minimal 2 sinyal kuat  