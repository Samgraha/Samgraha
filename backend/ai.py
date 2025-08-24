from typing import Literal, Tuple, Dict, Optional
import google.generativeai as genai
from config import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY tidak ditemukan di .env")

genai.configure(api_key=GEMINI_API_KEY)

# Model teks
_MODEL = "gemini-1.5-flash"

SYSTEM_INTENT = (
    "Anda adalah router untuk dua mode: (1) 'ktp' jika pengguna ingin membuat KTP baru, "
    "(2) 'tanya' jika pengguna bertanya tentang administrasi publik di Bandung. "
    "Jika ragu tapi mengarah ke pengumpulan dokumen KTP (KK, Akta Kelahiran, Surat Pengantar), pilih 'ktp'. "
    "Jika kalimat berisi upload/unggah dokumen KTP, tetap 'ktp'. Selain itu 'tanya'. "
    "Balas hanya salah satu kata: ktp atau tanya."
)

SYSTEM_QA = (
    "Anda adalah asisten administrasi publik wilayah Bandung. "
    "Jawab singkat, akurat, dengan langkah praktis dan rujukan instansi/layanan terkait (Disdukcapil, kecamatan, kelurahan). "
    "Gunakan Bahasa Indonesia. Jika informasi berbeda antar kecamatan, jelaskan variasinya secara umum."
)

SYSTEM_DOC_CHECK = (
    "Tugas Anda adalah memverifikasi apakah isi teks dari dokumen memenuhi jenis yang diminta. "
    "Jenis bisa: 'kk', 'akta', 'surat_pengantar'. "
    "Gunakan bukti berbasis teks (nama dokumen, frasa khas, nomor, kop surat). "
    "Jawab dalam JSON: {\"is_valid\": bool, \"reason\": str, \"confidence\": 0..1}."
)


def classify_intent(message: str) -> Literal["ktp", "tanya"]:
    prompt = f"{SYSTEM_INTENT}\n\nUser: {message}"
    resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
    text = (resp.text or "").strip().lower()
    return "ktp" if "ktp" in text else "tanya"


def qa_bandung(question: str) -> str:
    prompt = f"{SYSTEM_QA}\n\nPertanyaan: {question}\nJawaban:"
    resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
    return (resp.text or "Maaf, saya belum menemukan jawabannya.").strip()


def validate_doc(kind: str, extracted_text: str, filename: str) -> Dict:
    """kind in {"kk", "akta", "surat_pengantar"}.
    Returns dict: {is_valid: bool, reason: str, confidence: float}
    """
    # Sedikit konteks untuk model: sertakan nama file & cuplikan teks
    snippet = extracted_text[:4000]
    prompt = (
        f"{SYSTEM_DOC_CHECK}\n\n"
        f"Jenis diminta: {kind}\n"
        f"Nama file: {filename}\n"
        f"Isi (potongan):\n{snippet}\n\n"
        f"Keluarkan JSON."
    )
    resp = genai.GenerativeModel(_MODEL).generate_content(prompt)
    import json
    raw = resp.text or "{}"
    try:
        data = json.loads(raw)
    except Exception:
        data = {"is_valid": False, "reason": "Gagal parsing respons model", "confidence": 0.0}
    # fallback sederhana bila model tidak yakin
    if not isinstance(data, dict) or "is_valid" not in data:
        data = {"is_valid": False, "reason": "Format model tidak sesuai", "confidence": 0.0}
    return data