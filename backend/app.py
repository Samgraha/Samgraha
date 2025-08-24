import streamlit as st
import json
from router import handle_user_input
# Menggunakan alias yang direkomendasikan
import google.generativeai as genai

st.set_page_config(page_title="Chatbot KTP Test", page_icon="📝")

# -------------------------------
# Konfigurasi Gemini dari Streamlit Secrets
# -------------------------------
try:
    # Cara yang direkomendasikan untuk mengkonfigurasi API key
    GEMINI_API_KEY = st.secrets["vars"]["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    # Inisialisasi model yang akan digunakan
    model = genai.GenerativeModel("gemini-1.5-flash")
except (KeyError, TypeError):
    st.error("GEMINI_API_KEY tidak ditemukan di Streamlit Secrets. Harap konfigurasikan.")
    st.stop()


# -------------------------------
# Setup Streamlit Page
# -------------------------------
st.title("Chatbot KTP & Tanya Jawab")

# -------------------------------
# Fungsi untuk merapikan response dari Gemini
# -------------------------------
def refine_with_gemini(raw_response: str) -> str:
    """
    Mengubah response JSON atau teks mentah menjadi jawaban natural yang ramah.
    """
    # Jika respons sudah berupa string non-JSON, kembalikan langsung
    try:
        # Coba parsing JSON untuk melihat apakah itu valid
        json.loads(raw_response)
    except (json.JSONDecodeError, TypeError):
        # Jika gagal, berarti itu bukan JSON, jadi kembalikan apa adanya
        return raw_response

    prompt = f"""
Ubah respons JSON berikut menjadi teks jawaban chatbot yang jelas, ramah, dan mudah dipahami dalam Bahasa Indonesia.
Jangan tampilkan ```json``` atau struktur JSON mentah. Langsung berikan jawabannya dalam bentuk kalimat.

Contoh:
JSON: {{"status": "dokumen diterima", "file": "ktp.jpg", "validasi": {{"is_valid": true, "reason": "Format KTP terdeteksi"}}}}
Jawaban: Dokumen ktp.jpg Anda sudah kami terima dan validasinya berhasil karena format KTP terdeteksi dengan baik.

Sekarang, ubah JSON ini:
{raw_response}
"""
    try:
        # PERBAIKAN: Menggunakan model.generate_content()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500
            )
        )
        # PERBAIKAN: Mengakses teks melalui response.text
        return response.text.strip() if response and response.text else str(raw_response)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi Gemini: {e}")
        return f"Terjadi kesalahan internal saat memproses respons. Coba lagi nanti."

# -------------------------------
# Session State untuk chat history
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Gunakan session_id Streamlit sebagai user_id unik per sesi
user_id = st.runtime.scriptrunner.get_script_run_ctx().session_id

# -------------------------------
# Tampilkan riwayat chat (diletakkan di atas agar input di bawah)
# -------------------------------
for sender, text in st.session_state.chat_history:
    with st.chat_message("user" if sender == "user" else "assistant"):
        st.markdown(text)

# -------------------------------
# Input Form (diletakkan di bawah chat history)
# -------------------------------
with st.container():
    uploaded_files = st.file_uploader(
        "Unggah dokumen persyaratan (PDF/JPG/PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="file_uploader" # Menambahkan key untuk stabilitas
    )
    user_message = st.chat_input("Ketik pesan Anda atau unggah file...")

# -------------------------------
# Proses Input
# -------------------------------
if user_message or uploaded_files:
    # Tambahkan pesan pengguna ke riwayat chat terlebih dahulu
    if user_message:
        st.session_state.chat_history.append(("user", user_message))
        with st.chat_message("user"):
            st.markdown(user_message)

    if uploaded_files:
        file_info = f"📎 Mengunggah {len(uploaded_files)} file: " + ", ".join([f.name for f in uploaded_files])
        st.session_state.chat_history.append(("user", file_info))
        with st.chat_message("user"):
            st.markdown(file_info)

    # Tampilkan status "thinking..."
    with st.chat_message("assistant"):
        with st.spinner("Memproses..."):
            files_dict = {}
            if uploaded_files:
                for f in uploaded_files:
                    files_dict[f.name] = f.getvalue() # Gunakan getvalue() untuk file di memori

            # Panggil backend untuk mendapatkan respons mentah
            raw_response = handle_user_input(
                user_id=user_id,
                message=user_message or "",
                files=files_dict
            )

            # Ubah respons mentah menjadi teks natural
            bot_message = refine_with_gemini(str(raw_response))

            # Tambahkan respons bot ke riwayat dan tampilkan
            st.session_state.chat_history.append(("bot", bot_message))
            st.markdown(bot_message)

            # Hapus file yang diunggah dari state agar tidak diproses ulang
            # Ini memerlukan sedikit trik di Streamlit, cara termudah adalah me-rerun
            st.rerun()