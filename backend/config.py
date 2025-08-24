import streamlit as st
import gspread
from google.oauth2.service_account import Credentials as GoogleCredentials
from googleapiclient.discovery import build

# -------------------------------
# Scopes untuk Sheets dan Drive
# -------------------------------
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

# -------------------------------
# Setup Sheets Client via Secrets
# -------------------------------
sheets_creds_info = st.secrets["sheets"]  # pastikan di Streamlit Secrets ada [sheets] dengan isi JSON
sheets_creds = GoogleCredentials.from_service_account_info(
    sheets_creds_info,
    scopes=SHEETS_SCOPES
)
sheets_client = gspread.authorize(sheets_creds)

# -------------------------------
# Setup Drive Client via Secrets
# -------------------------------
drive_creds_info = st.secrets["drive"]  # pastikan di Streamlit Secrets ada [drive] dengan isi JSON
drive_creds = GoogleCredentials.from_service_account_info(
    drive_creds_info,
    scopes=DRIVE_SCOPES
)
drive_service = build('drive', 'v3', credentials=drive_creds)

# -------------------------------
# Variabel lain dari Secrets
# -------------------------------
SHEET_ID = st.secrets["vars"]["SHEET_ID"]  # Contoh: simpan di [vars] di Secrets
GEMINI_API_KEY = st.secrets["vars"]["GEMINI_API_KEY"]
DRIVE_PARENT_FOLDER_ID = st.secrets["vars"]["DRIVE_PARENT_FOLDER_ID"]
