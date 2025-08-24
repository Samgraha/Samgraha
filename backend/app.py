import streamlit as st
import google.generativeai as genai
from router import handle_user_input

# -------------------------------
# Konfigurasi Gemini dari Streamlit Secrets
# -------------------------------
GEMINI_API_KEY = st.secrets["gemini"]["API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# -------------------------------
# Setup Streamlit Page
# -------------------------------
st.set_page_config(page_title="Chatbot KTP Test", page_icon="📝")
st.title("Chatbot KTP & Tanya Jawab")

# -------------------------------
# Fungsi untuk merapikan response dari Gemini
# -------------------------------
def refine_with_gemini(raw_response):
    """
    Mengubah response JSON menjadi teks natural yang ramah dan jelas.
    """
    prompt = f"""
    Ubah response JSON berikut menjadi teks jawaban chatbot yang jelas, ramah, dan mudah dipahami.
    Jangan tampilkan kurung kurawal atau struktur JSON.

    Response:
    {raw_response}
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        result = model.generate_content(prompt)
        return result.text.strip() if result and result.text else str(raw_response)
    except Exception as e:
        return f"Terjadi kesalahan saat memproses respons: {e}"

# -------------------------------
# Session State untuk chat history
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_id = "test_user_001"

# -------------------------------
# Upload File
# -------------------------------
uploaded_files = st.file_uploader(
    "Unggah dokumen persyaratan (PDF/JPG/PNG)",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# -------------------------------
# Input Chat
# -------------------------------
user_message = st.chat_input("Ketik pesan Anda...")

# -------------------------------
# Proses Input
# -------------------------------
if user_message or uploaded_files:
    files_dict = {}
    if uploaded_files:
        for f in uploaded_files:
            files_dict[f.name] = f.read()

    # Ambil response mentah dari handler
    raw_response = handle_user_input(
        user_id=user_id,
        message=user_message or "",
        files=files_dict
    )

    # Ubah response JSON jadi teks natural
    bot_message = refine_with_gemini(raw_response)

    # Simpan ke session_state
    if user_message:
        st.session_state.chat_history.append(("user", user_message))
    if uploaded_files:
        st.session_state.chat_history.append(("user", f"📎 Mengunggah {len(uploaded_files)} file"))
    st.session_state.chat_history.append(("bot", bot_message))

# -------------------------------
# Tampilkan riwayat chat
# -------------------------------
for sender, text in st.session_state.chat_history:
    if sender == "user":
        st.chat_message("user").markdown(text)
    else:
        st.chat_message("assistant").markdown(text)
