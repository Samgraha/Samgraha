import os
import gspread
from google.oauth2.service_account import Credentials as GoogleCredentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Scope Sheets dan Drive
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path ke dua credentials
SHEETS_CREDENTIALS_PATH = os.path.join(BASE_DIR, "sheets_credentials.json")
DRIVE_CREDENTIALS_PATH = os.path.join(BASE_DIR, "drive_credentials.json")

# Setup Sheets Client
sheets_creds = GoogleCredentials.from_service_account_file(
    SHEETS_CREDENTIALS_PATH,
    scopes=SHEETS_SCOPES
)
sheets_client = gspread.authorize(sheets_creds)

# Setup Drive Client
drive_creds = GoogleCredentials.from_service_account_file(
    DRIVE_CREDENTIALS_PATH,
    scopes=DRIVE_SCOPES
)
drive_service = build('drive', 'v3', credentials=drive_creds)

# Variabel dari .env
SHEET_ID = os.getenv("SHEET_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DRIVE_PARENT_FOLDER_ID = os.getenv("DRIVE_PARENT_FOLDER_ID")
