"""
fetch_email.py — Descarga el correo con adjuntos de Consuelo desde Gmail

Uso:
    cd ~/Projects/consuelo-hr
    source ../health-mvp/.venv/bin/activate
    python fetch_email.py

Credenciales: ~/.config/google/credentials.json
Token (separado para no tocar el token de Drive/Docs): ~/.config/google/token_gmail.json
"""

import os
import base64
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ── Config ────────────────────────────────────────────────────────────────────

CREDENTIALS_FILE = Path.home() / ".config" / "google" / "credentials.json"
TOKEN_FILE       = Path.home() / ".config" / "google" / "token_gmail.json"
OUTPUT_DIR       = Path(__file__).parent / "inputs"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Query de búsqueda — mismo término que usaste en Gmail, con adjuntos
SEARCH_QUERY = "consuelo has:attachment"

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"No se encontró credentials.json en {CREDENTIALS_FILE}\n"
                    "Descárgalo desde Google Cloud Console > APIs & Services > Credentials"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds

# ── Gmail helpers ─────────────────────────────────────────────────────────────

def get_body_text(payload: dict) -> str:
    """Extrae texto plano del mensaje (recursivo para multipart)."""
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""
    if mime.startswith("multipart/"):
        parts = payload.get("parts", [])
        for part in parts:
            text = get_body_text(part)
            if text:
                return text
    return ""

def download_attachments(service, message_id: str, payload: dict) -> list[str]:
    """Descarga todos los adjuntos en OUTPUT_DIR. Retorna lista de paths."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = []
    parts = payload.get("parts", [])

    def process_parts(parts):
        for part in parts:
            filename = part.get("filename")
            body     = part.get("body", {})
            att_id   = body.get("attachmentId")

            if filename and att_id:
                att = service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=att_id
                ).execute()
                data = base64.urlsafe_b64decode(att["data"] + "==")
                out_path = OUTPUT_DIR / filename
                out_path.write_bytes(data)
                downloaded.append(str(out_path))
                print(f"  ✓ {filename} ({len(data):,} bytes)")

            # Recursivo para partes anidadas
            if part.get("parts"):
                process_parts(part["parts"])

    process_parts(parts)
    return downloaded

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Autenticando con Gmail...")
    creds   = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    # Buscar mensajes por query
    print(f"Buscando: '{SEARCH_QUERY}'...")
    results  = service.users().messages().list(userId="me", q=SEARCH_QUERY, maxResults=10).execute()
    msg_list = results.get("messages", [])
    if not msg_list:
        print("No se encontraron mensajes. Ajusta SEARCH_QUERY.")
        return
    print(f"  {len(msg_list)} mensaje(s) encontrado(s). Procesando el más reciente...")

    # Fetch el mensaje completo (el primero = más reciente)
    msg_id   = msg_list[0]["id"]
    messages = [service.users().messages().get(userId="me", id=msg_id, format="full").execute()]

    all_files = []
    for i, msg in enumerate(messages):
        payload = msg["payload"]
        headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

        print(f"\n── Mensaje {i+1} ──────────────────────────────────")
        print(f"De:     {headers.get('From', '?')}")
        print(f"Para:   {headers.get('To', '?')}")
        print(f"Fecha:  {headers.get('Date', '?')}")
        print(f"Asunto: {headers.get('Subject', '?')}")

        body = get_body_text(payload)
        if body:
            print(f"\n{body[:3000]}")

        print(f"\n── Adjuntos ──────────────────────────────────────")
        files = download_attachments(service, msg["id"], payload)
        if not files:
            print("  (sin adjuntos)")
        all_files.extend(files)

    print(f"\nListo. {len(all_files)} adjuntos descargados en {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
