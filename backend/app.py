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
# Ganti fungsi lama Anda dengan yang ini di app.py

def refine_with_gemini(raw_response: str) -> str:
    """
    Mengubah respons JSON atau teks mentah menjadi jawaban natural yang ramah.
    Dibuat lebih tangguh untuk menangani JSON kosong atau kegagalan API.
    """
    # 1. Penanganan Cepat untuk JSON Kosong atau tidak valid
    # Jika respons adalah string '{}' atau None/kosong, langsung beri pesan default.
    if not raw_response or raw_response == '{}':
        return "Saat ini tidak ada pembaruan atau tindakan yang perlu dilakukan. Anda bisa bertanya atau mengunggah dokumen."

    # Cek apakah responsnya bukan JSON, jika ya, kembalikan langsung
    try:
        json.loads(raw_response)
    except (json.JSONDecodeError, TypeError):
        return raw_response # Ini sudah teks biasa, tidak perlu diubah

    # 2. Perbaikan Prompt untuk Gemini
    # Beri instruksi yang lebih jelas, termasuk cara menangani data minimal.
    prompt = f"""
Anda adalah asisten AI yang bertugas mengubah data JSON menjadi kalimat yang sangat ramah dan mudah dimengerti untuk pengguna awam di Indonesia.

Tugas Anda:
- Ubah data JSON di bawah ini menjadi satu paragraf singkat yang informatif.
- Gunakan bahasa yang sopan, positif, dan jelas.
- Jangan pernah menampilkan nama kunci JSON seperti "is_valid", "status", "missing_docs".
- Jika sebuah file dinyatakan valid, berikan pujian singkat. Contoh: "Dokumen KK Anda berhasil divalidasi, bagus sekali!"
- Jika ada dokumen yang kurang, sebutkan dengan jelas apa saja yang masih dibutuhkan.

Contoh 1:
JSON: {{"status": "menunggu dokumen", "missing": ["kk", "akta"]}}
Jawaban Ideal: Tentu, proses pembuatan KTP Anda sedang berjalan. Saat ini kami masih menunggu dokumen Kartu Keluarga (KK) dan Akta Kelahiran dari Anda. Silakan diunggah ya.

Contoh 2:
JSON: {{"file": "surat_rt_rw.pdf", "is_valid": true, "reason": "Terdeteksi kop surat dan tanda tangan."}}
Jawaban Ideal: Terima kasih! Dokumen surat_rt_rw.pdf Anda sudah kami terima dan berhasil divalidasi karena kop surat dan tanda tangannya sudah sesuai.

Sekarang, ubah JSON ini menjadi jawaban yang ramah:
{raw_response}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5, # Sedikit diturunkan agar lebih konsisten
                max_output_tokens=500
            )
        )

        # 3. Logika Fallback yang Lebih Baik
        # Jika respons ada isinya, kembalikan. Jika tidak, beri tahu ada masalah
        # dan tunjukkan data mentahnya agar mudah di-debug.
        if response and response.text:
            return response.text.strip()
        else:
            return f"Terjadi sedikit kendala saat merangkum status. Berikut adalah data teknisnya: `{raw_response}`"

    except Exception as e:
        st.error(f"Error pada API Gemini: {e}")
        return f"Maaf, terjadi kesalahan saat memproses respons. Berikut adalah data teknisnya: `{raw_response}`"

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