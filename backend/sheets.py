from typing import Optional, Dict
from datetime import datetime
from config import sheets_client, SHEET_ID

SHEET_NAME = "KTP_Submissions"  # buat sheet/tab ini di Spreadsheet Anda

REQUIRED_COLUMNS = [
    "timestamp", "user_id", "flow", "status",
    "kk_link", "akta_link", "surat_pengantar_link",
    "notes"
]


def _get_worksheet():
    sh = sheets_client.open_by_key(SHEET_ID)
    try:
        ws = sh.worksheet(SHEET_NAME)
    except Exception:
        ws = sh.add_worksheet(title=SHEET_NAME, rows=1000, cols=len(REQUIRED_COLUMNS))
        ws.append_row(REQUIRED_COLUMNS)
    return ws


def append_or_update_submission(user_id: str, links: Dict[str, Optional[str]], status: str, notes: str = ""):
    ws = _get_worksheet()
    timestamp = datetime.utcnow().isoformat()

    row = [
        timestamp,
        user_id,
        "ktp",
        status,
        links.get("kk_link"),
        links.get("akta_link"),
        links.get("surat_pengantar_link"),
        notes,
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")