# Samgraha – Agen AI Untuk Pelayanan Publik

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MIT License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Samgraha adalah proyek **Agen AI** berbasis **Kota Cerdas** yang membantu warga dalam pengurusan layanan administrasi publik seperti pembuatan **KTP**, **KK**, dan **izin usaha**. Sistem ini mengintegrasikan chatbot AI dengan antarmuka modern dan basis data menggunakan **Google Spreadsheet**.

---

## 🚀 Fitur Utama

- **Chatbot AI** dengan pemrosesan bahasa alami untuk melayani masyarakat sepanjang waktu.
- **Memori Sementara Percakapan** agar chatbot dapat mengingat konteks diskusi sebelumnya.
- **Login dan Registrasi Pengguna** untuk mengakses layanan administrasi publik.
- **Integrasi Google Spreadsheet** sebagai basis data penyimpanan pengguna, permohonan layanan, serta riwayat interaksi.
- **Antar Muka Website Interaktif** berbasis JavaScript untuk pengalaman pengguna yang nyaman.

---

## 🏗️ Arsitektur Sistem

Proyek Samgraha terdiri dari dua komponen utama berikut:

1. **Lapis Belakang (Backend, Python)**
   - Dibangun dengan kerangka kerja seperti FastAPI atau Flask.
   - Meliputi modul chatbot, logika intent, dan memori percakapan.
   - Terhubung ke **Google Sheets API** sebagai penyimpanan data.

2. **Lapis Depan (Frontend, JavaScript)**
   - Dibangun menggunakan React.
   - Menyediakan halaman login, registrasi, serta chatbot interaktif.

---

## 📁 Struktur Folder

```

Samgraha/
│
├── backend/ \# Logika AI \& API (Python)
│   ├── aplikasi/
│   │   ├── utama.py \# Titik masuk backend
│   │   ├── autentikasi/
│   │   ├── chatbot/
│   │   │   ├── penangan_intent.py
│   │   │   ├── manajer_memori.py
│   │   │   ├── layanan_ktp.py
│   │   │   ├── layanan_kk.py
│   │   │   └── layanan_izin.py
│   │   ├── basisdata/
│   │   │   ├── klien_sheets.py
│   │   │   └── model.py
│   │   └── utilitas/
│   ├── pengujian/
│   └── kebutuhan.txt
│
├── frontend/ \# Antar Muka (JavaScript)
│   ├── publik/
│   ├── src/
│   │   ├── aset/
│   │   ├── komponen/
│   │   ├── halaman/
│   │   │   ├── HalamanLogin.js
│   │   │   ├── HalamanRegistrasi.js
│   │   │   └── HalamanChatbot.js
│   │   └── layanan/api.js
│   ├── paket.json
│
├── dokumentasi/
│   ├── referensi_api.md
│   └── desain/
│
├── .gitignore
└── README.md

```

---

## 🧪 Teknologi yang Digunakan

- **Backend**: Python, FastAPI / Flask, gspread (Google Sheets API), pustaka NLP.
- **Frontend**: JavaScript, React, TailwindCSS.
- **AI/NLP**: spaCy / Transformers (HuggingFace).
- **Basis Data**: Google Spreadsheet (gspread).

---

## ⚙️ Cara Menjalankan Proyek

### 1. Backend

```

cd backend
pip install -r kebutuhan.txt
python aplikasi/utama.py

```

### 2. Frontend

```

cd frontend
npm install
npm start

```

---

## 🧠 Fitur Chatbot Memori Sementara

- Mengingat percakapan dan melanjutkan layanan tanpa mengulang.
- Menyimpan konteks secara sementara di runtime Python atau Google Sheets.

---

## 👥 Tim Pengembang

| Peran                   | Nama        |
|-------------------------|------------|
| Logika AI (Python)      | Fauzan     |
| Antar Muka (JavaScript) | Syaifuddin |
| Desainer UI/UX          | Faixal     |

---
