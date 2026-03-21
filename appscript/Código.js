// ============================================================
// Consuelo Aránguiz — Apps Script Backend
// Recibe leads del formulario web → Sheets + email de notificación
// ============================================================

var SHEET_ID   = "1V_DKFsHz3Qv6IsgrrOdNJXH_JR1vpsYqnOBzsJXSx6U";
var HOJA_LEADS = "Leads";
var EMAIL_NOTIF = "seleccion.cvas@gmail.com";

// ── Punto de entrada del formulario web ──────────────────────

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    registrarLead(data);
    enviarNotificacion(data);
    return respuesta(true, "Mensaje recibido. Te contactaré pronto.");
  } catch (err) {
    return respuesta(false, "Error interno: " + err.message);
  }
}

// Permite probar desde el navegador sin formulario
function doGet(e) {
  return respuesta(true, "Backend activo ✓");
}

// ── Guardar lead en Sheets ───────────────────────────────────

function registrarLead(data) {
  var ss    = SpreadsheetApp.openById(SHEET_ID);
  var hoja  = ss.getSheetByName(HOJA_LEADS);
  var fecha = Utilities.formatDate(new Date(), "America/Santiago", "dd/MM/yyyy HH:mm");

  hoja.appendRow([
    fecha,
    data.nombre      || "",
    data.empresa     || "",
    data.email       || "",
    data.telefono    || "",
    data.servicio    || "",
    "Sitio web",       // Cómo llegó
    "Nuevo",           // Estado (dropdown)
    "",                // Próximo paso
    data.mensaje     || ""
  ]);
}

// ── Notificación por email ───────────────────────────────────

function enviarNotificacion(data) {
  var asunto = "🔔 Nuevo lead — " + (data.nombre || "sin nombre") +
               " (" + (data.empresa || "sin empresa") + ")";

  var cuerpo = [
    "Nuevo contacto desde tu sitio web:",
    "",
    "Nombre:   " + (data.nombre   || "—"),
    "Empresa:  " + (data.empresa  || "—"),
    "Email:    " + (data.email    || "—"),
    "Teléfono: " + (data.telefono || "—"),
    "Servicio: " + (data.servicio || "—"),
    "",
    "Mensaje:",
    data.mensaje || "—",
    "",
    "—",
    "Ver en Sheets: https://docs.google.com/spreadsheets/d/" + SHEET_ID
  ].join("\n");

  MailApp.sendEmail(EMAIL_NOTIF, asunto, cuerpo);
}

// ── Helper respuesta CORS ────────────────────────────────────

function respuesta(ok, mensaje) {
  var payload = JSON.stringify({ ok: ok, mensaje: mensaje });
  return ContentService
    .createTextOutput(payload)
    .setMimeType(ContentService.MimeType.JSON);
}
