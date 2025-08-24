import streamlit as st
from typing import Dict
from google import genai
from google.genai import types
from PyPDF2 import PdfReader
import json
from config import GEMINI_API_KEY

# --- Setup GenAI ---
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY tidak ditemukan di .env")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)
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

# --- Fungsi GenAI ---
def classify_intent(message: str) -> str:
    prompt = f"{SYSTEM_INTENT}\n\nUser: {message}"
    resp = client.models.generate_content(
        model=_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0))
    )
    text = (resp.output[0].content[0].text or "").strip().lower()
    return "ktp" if "ktp" in text else "tanya"

def qa_bandung(question: str) -> str:
    prompt = f"{SYSTEM_QA}\n\nPertanyaan: {question}\nJawaban:"
    resp = client.models.generate_content(
        model=_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0))
    )
    return (resp.output[0].content[0].text or "Maaf, saya belum menemukan jawabannya.").strip()

def validate_doc(kind: str, extracted_text: str, filename: str) -> Dict:
    snippet = extracted_text[:4000]
    prompt = (
        f"{SYSTEM_DOC_CHECK}\n\n"
        f"Jenis diminta: {kind}\n"
        f"Nama file: {filename}\n"
        f"Isi (potongan):\n{snippet}\n\n"
        f"Keluarkan JSON."
    )
    resp = client.models.generate_content(
        model=_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_budget=0))
    )
    raw = (resp.output[0].content[0].text or "{}").strip()
    try:
        data = json.loads(raw)
    except Exception:
        data = {"is_valid": False, "reason": "Gagal parsing respons model", "confidence": 0.0}

    if not isinstance(data, dict) or "is_valid" not in data:
        data = {"is_valid": False, "reason": "Format model tidak sesuai", "confidence": 0.0}

    return data

def extract_text_from_pdf(file) -> str:
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Streamlit UI ---
st.title("Asisten Administrasi Publik Bandung")

user_message = st.text_area("Tulis pertanyaan atau instruksi:")

uploaded_files = st.file_uploader(
    "Unggah dokumen KTP (KK, Akta, Surat Pengantar)", accept_multiple_files=True, type=["pdf"]
)

if st.button("Proses"):
    if not user_message and not uploaded_files:
        st.warning("Silakan isi pesan atau unggah dokumen.")
    else:
        # 1) Tentukan intent
        intent = classify_intent(user_message)
        st.info(f"Intent terdeteksi: {intent}")

        # 2) Jika tanya
        if intent == "tanya" and user_message:
            jawaban = qa_bandung(user_message)
            st.success("Jawaban:")
            st.write(jawaban)

        # 3) Jika KTP, cek dokumen
        if intent == "ktp" and uploaded_files:
            for f in uploaded_files:
                text = extract_text_from_pdf(f)
                # Bisa coba cek semua jenis, atau minta input user jenis dokumen
                for kind in ["kk", "akta", "surat_pengantar"]:
                    result = validate_doc(kind, text, f.name)
                    st.write(f"File: {f.name}, Jenis cek: {kind}")
                    st.json(result)
