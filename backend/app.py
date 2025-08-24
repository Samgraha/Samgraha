import streamlit as st
from router import handle_user_input

st.set_page_config(page_title="Chatbot KTP Test", page_icon="📝")

st.title("Chatbot KTP & Tanya Jawab")

# Simpan riwayat chat di session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_id = "test_user_001"

# Area upload file (mendukung beberapa file)
uploaded_files = st.file_uploader(
    "Unggah dokumen persyaratan (PDF/JPG/PNG)", 
    type=["pdf", "jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

# Area input teks
user_message = st.chat_input("Ketik pesan Anda...")

if user_message or uploaded_files:
    # Siapkan dictionary files untuk dikirim ke handler
    files_dict = {}
    if uploaded_files:
        for f in uploaded_files:
            files_dict[f.name] = f.read()  # Membaca isi file dalam bytes

    # Panggil handler
    response = handle_user_input(user_id=user_id, message=user_message or "", files=files_dict)
    if user_message:
        st.session_state.chat_history.append(("user", user_message))
    if uploaded_files:
        st.session_state.chat_history.append(("user", f"📎 Mengunggah {len(uploaded_files)} file"))
    st.session_state.chat_history.append(("bot", str(response)))

# Tampilkan riwayat chat
for sender, text in st.session_state.chat_history:
    if sender == "user":
        st.chat_message("user").markdown(text)
    else:
        st.chat_message("assistant").markdown(text)
