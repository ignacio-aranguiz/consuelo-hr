"""
setup_crm.py — Crea el Google Sheets CRM de Consuelo Aránguiz

Crea un spreadsheet con 4 hojas:
  1. Asesorías   — gestión de procesos activos
  2. Leads       — contactos del sitio web y referencias
  3. Clientes    — empresas con historial
  4. Contabilidad — ingresos y boletas mensuales

Uso:
    source ~/Projects/health-mvp/.venv/bin/activate
    python setup_crm.py
"""

import sys
sys.path.insert(0, "/Users/ignacio_aranguiz/Projects")

from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CREDENTIALS_FILE = Path.home() / ".config" / "google" / "credentials.json"
TOKEN_FILE       = Path.home() / ".config" / "google" / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_credentials():
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
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
    return creds

# ── Sheet definitions ─────────────────────────────────────────────────────────

SHEETS = [
    {
        "name": "Asesorías",
        "headers": [
            "ID", "Empresa / Cliente", "Cargo a cubrir", "Tipo de cargo",
            "Estado", "Fecha inicio", "Fecha entrega estimada", "Fecha entrega real",
            "Honorarios (UF)", "Honorarios ($CLP)", "% Cobrado", "Observaciones"
        ],
        "tab_color": {"red": 0.17, "green": 0.42, "blue": 0.42},  # teal
    },
    {
        "name": "Leads",
        "headers": [
            "Fecha", "Nombre", "Empresa", "Email", "Teléfono",
            "Servicio interesado", "Cómo llegó", "Estado", "Próximo paso", "Observaciones"
        ],
        "tab_color": {"red": 0.77, "green": 0.44, "blue": 0.31},  # terracota
    },
    {
        "name": "Clientes",
        "headers": [
            "Empresa", "Rubro", "Contacto principal", "Email contacto",
            "Teléfono", "N° procesos realizados", "Última asesoría", "Estado relación", "Observaciones"
        ],
        "tab_color": {"red": 0.37, "green": 0.62, "blue": 0.37},  # verde
    },
    {
        "name": "Contabilidad",
        "headers": [
            "Mes", "Empresa / Cliente", "Servicio", "Honorarios (UF)",
            "Valor UF del mes", "Monto ($CLP)", "N° boleta", "Fecha cobro", "Estado pago"
        ],
        "tab_color": {"red": 0.42, "green": 0.42, "blue": 0.72},  # azul
    },
]

ESTADO_ASESORIAS  = ["Prospecto", "En proceso", "Informe enviado", "Cerrado", "Cancelado"]
ESTADO_LEADS      = ["Nuevo", "Contactado", "En conversación", "Propuesta enviada", "Ganado", "Perdido"]
ESTADO_RELACION   = ["Activo", "Potencial", "Inactivo"]
ESTADO_PAGO       = ["Pendiente", "50% cobrado", "Pagado completo"]
TIPO_CARGO        = ["Administrativo/Técnico", "Profesional Junior", "Jefatura", "Subgerencia"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def col_letter(n):
    """Convierte número de columna (1-based) a letra(s). 1→A, 27→AA"""
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result

def header_range(sheet_name, n_cols):
    return f"'{sheet_name}'!A1:{col_letter(n_cols)}1"

def make_dropdown(sheet_id, row_start, row_end, col_idx, values):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_start,
                "endRowIndex": row_end,
                "startColumnIndex": col_idx,
                "endColumnIndex": col_idx + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in values],
                },
                "showCustomUi": True,
                "strict": False,
            },
        }
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Autenticando...")
    creds    = get_credentials()
    sheets   = build("sheets", "v4", credentials=creds)
    api      = sheets.spreadsheets()

    # 1. Crear el spreadsheet
    print("Creando spreadsheet 'Consuelo Aránguiz — CRM RRHH'...")
    body = {
        "properties": {"title": "Consuelo Aránguiz — CRM RRHH"},
        "sheets": [
            {"properties": {"title": s["name"], "tabColor": s["tab_color"]}}
            for s in SHEETS
        ],
    }
    ss = api.create(body=body).execute()
    ss_id = ss["spreadsheetId"]
    print(f"  ✓ Creado: https://docs.google.com/spreadsheets/d/{ss_id}")

    # Mapa name→sheetId
    sheet_ids = {
        sh["properties"]["title"]: sh["properties"]["sheetId"]
        for sh in ss["sheets"]
    }

    # 2. Escribir headers y formatearlos
    value_data = []
    for s in SHEETS:
        value_data.append({
            "range": header_range(s["name"], len(s["headers"])),
            "values": [s["headers"]],
        })

    api.values().batchUpdate(
        spreadsheetId=ss_id,
        body={"valueInputOption": "RAW", "data": value_data},
    ).execute()
    print("  ✓ Headers escritos")

    # 3. Formato: headers en negrita + color de fondo teal, columnas anchas
    format_requests = []
    for s in SHEETS:
        sid   = sheet_ids[s["name"]]
        ncols = len(s["headers"])

        # Header row: bold + background
        format_requests.append({
            "repeatCell": {
                "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1,
                           "startColumnIndex": 0, "endColumnIndex": ncols},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.17, "green": 0.42, "blue": 0.42},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                        "horizontalAlignment": "CENTER",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
            }
        })
        # Freeze header row
        format_requests.append({
            "updateSheetProperties": {
                "properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount",
            }
        })
        # Auto-resize columns
        format_requests.append({
            "autoResizeDimensions": {
                "dimensions": {"sheetId": sid, "dimension": "COLUMNS",
                               "startIndex": 0, "endIndex": ncols}
            }
        })

    # 4. Dropdowns
    sid_a    = sheet_ids["Asesorías"]
    sid_l    = sheet_ids["Leads"]
    sid_c    = sheet_ids["Clientes"]
    sid_cont = sheet_ids["Contabilidad"]

    # Asesorías: Estado (col 5, idx 4), Tipo cargo (col 4, idx 3)
    format_requests.append(make_dropdown(sid_a, 1, 500, 4, ESTADO_ASESORIAS))
    format_requests.append(make_dropdown(sid_a, 1, 500, 3, TIPO_CARGO))
    # Leads: Estado (col 8, idx 7)
    format_requests.append(make_dropdown(sid_l, 1, 500, 7, ESTADO_LEADS))
    # Clientes: Estado relación (col 8, idx 7)
    format_requests.append(make_dropdown(sid_c, 1, 500, 7, ESTADO_RELACION))
    # Contabilidad: Estado pago (col 9, idx 8)
    format_requests.append(make_dropdown(sid_cont, 1, 500, 8, ESTADO_PAGO))

    api.batchUpdate(
        spreadsheetId=ss_id,
        body={"requests": format_requests},
    ).execute()
    print("  ✓ Formato y dropdowns aplicados")

    # 5. Guardar el ID para usarlo en el Apps Script
    id_file = Path(__file__).parent / "crm_sheet_id.txt"
    id_file.write_text(ss_id)
    print(f"\n✅ CRM listo.")
    print(f"   Sheet ID guardado en: {id_file}")
    print(f"   URL: https://docs.google.com/spreadsheets/d/{ss_id}")

if __name__ == "__main__":
    main()
