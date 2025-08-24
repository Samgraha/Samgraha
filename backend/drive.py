from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import drive_creds, DRIVE_PARENT_FOLDER_ID


def _drive_service():
    return build("drive", "v3", credentials=drive_creds)


def ensure_user_folder(user_id: str) -> Optional[str]:
    service = _drive_service()
    # Cari folder user di bawah parent
    query = (
        f"mimeType='application/vnd.google-apps.folder' and "
        f"name='{user_id}' and '{DRIVE_PARENT_FOLDER_ID}' in parents and trashed=false"
    )
    res = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    # Buat baru jika belum ada
    file_metadata = {
        "name": user_id,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_PARENT_FOLDER_ID] if DRIVE_PARENT_FOLDER_ID else None,
    }
    folder = service.files().create(body=file_metadata, fields="id").execute()
    return folder.get("id")


def upload_to_drive(local_path: str, filename: str, user_folder_id: str) -> Optional[str]:
    service = _drive_service()
    media = MediaFileUpload(local_path, resumable=True)
    file_metadata = {"name": filename, "parents": [user_folder_id] if user_folder_id else None}
    try:
        f = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
        return f.get("webViewLink")
    except HttpError as e:
        print("Drive upload error:", e)
        return None