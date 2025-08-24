from typing import Dict, Optional, List
import os

from ai import classify_intent, qa_bandung, validate_doc
from sheets import append_or_update_submission
from drive import ensure_user_folder, upload_to_drive
from doc_validation import extract_text_from_pdf, quick_sanity

REQUIRED_FILES = {
    "kk": "Fotokopi KK terbaru",
    "akta": "Akta Kelahiran (asli & fotokopi)",
    "surat_pengantar": "Surat Pengantar RT/RW dan Kelurahan/Desa",
}


class KTPFlowResult(dict):
    """Helper just for typing in responses."""
    pass


def _ktp_missing_list(provided: Dict[str, Optional[str]]) -> List[str]:
    """Cek dokumen yang belum diunggah oleh user."""
    return [k for k in REQUIRED_FILES.keys() if not provided.get(k)]


def handle_user_input(user_id: str, message: str, files: Dict[str, str]) -> Dict:
    """
    Entry-point untuk frontend.

    Params:
      - user_id: ID unik user dari aplikasi Anda
      - message: teks terakhir dari user
      - files: mapping {"kk"|"akta"|"surat_pengantar": local_file_path}, boleh kosong jika belum upload

    Returns JSON-like dict untuk ditampilkan di frontend.
    """
    # 1) Intent routing
    intent = classify_intent(message)

    if intent == "tanya":
        answer = qa_bandung(message)
        return {
            "mode": "tanya",
            "answer": answer,
        }

    # 2) Flow untuk pembuatan KTP
    provided = {k: files.get(k) for k in REQUIRED_FILES.keys()}
    missing = _ktp_missing_list(provided)

    if missing:
        return {
            "mode": "ktp",
            "status": "need_more_docs",
            "needed": [
                {"kind": k, "description": REQUIRED_FILES[k]} for k in missing
            ],
        }

    # 3) Validasi dokumen (jika semua sudah ada)
    validation_results = {}
    for kind, path in provided.items():
        try:
            text = extract_text_from_pdf(path)
            sanity = quick_sanity(text)
            # update: panggil validate_doc versi GenAI terbaru
            is_valid = validate_doc(kind, text, os.path.basename(path))
            validation_results[kind] = {"sanity": sanity, "valid": is_valid}
        except Exception as e:
            validation_results[kind] = {"sanity": False, "valid": False, "error": str(e)}

    # 4) Upload ke Google Drive
    folder_id = ensure_user_folder(user_id)
    drive_links = {}
    for kind, path in provided.items():
        if path and os.path.exists(path):
            drive_links[kind] = upload_to_drive(path, folder_id)

    # 5) Simpan ke Google Sheets
    append_or_update_submission(user_id, drive_links, validation_results)

    return {
        "mode": "ktp",
        "status": "complete",
        "drive_links": drive_links,
        "validation": validation_results,
    }
