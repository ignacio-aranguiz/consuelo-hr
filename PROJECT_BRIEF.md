# PROJECT_BRIEF.md — Consuelo Aránguiz RRHH
> Estado actual del proyecto. Actualizar al cierre de cada sesión.

**Última actualización:** 22 marzo 2026

---

## Cliente

**Consuelo Aránguiz Soto** — Psicóloga Laboral, consultora independiente de selección de personal.
- Email profesional: `consuelo@cvas-consultora.cl` → redirige a `seleccion.cvas@gmail.com`
- WhatsApp: +56 9 8929 7668
- LinkedIn: linkedin.com/in/consuelo-aranguiz-soto-11209222/

---

## Stack

| Componente | Tecnología | Estado |
|------------|------------|--------|
| Frontend | HTML/CSS/JS vanilla | Deployado en GitHub Pages |
| Hosting | GitHub Pages (`docs/` branch main) | Activo |
| Dominio | `www.cvas-consultora.cl` (NIC Chile) | DNS propagándose |
| DNS | Cloudflare (Free plan) | Nameservers configurados, pendiente propagación |
| Backend formulario | Google Apps Script | Deployado y funcional |
| CRM | Google Sheets | Activo con 5 tabs |
| Email routing | Cloudflare Email Routing | Configurado, activo cuando DNS propague |

---

## URLs y IDs clave

- **Repo GitHub:** `https://github.com/ignacio-aranguiz/consuelo-hr`
- **GitHub Pages (URL directa):** `https://ignacio-aranguiz.github.io/consuelo-hr/` (funciona ahora)
- **Dominio custom:** `https://www.cvas-consultora.cl` (activo cuando DNS propague)
- **Google Sheets CRM:** `https://docs.google.com/spreadsheets/d/1V_DKFsHz3Qv6IsgrrOdNJXH_JR1vpsYqnOBzsJXSx6U`
- **Apps Script Deployment ID:** `AKfycbx_95spFvepVEm_b8i3cdvWzJKuo3egVuww_j6enGgywG-KCWhqwvwdssCJiujbNeGa`
- **Apps Script Script ID:** `1TCZPSVvpeIkXd42PQaL2TSksWmwyiEiQNcfDIfDh1oFD3kR1rYSndhIB`
- **GCP Project:** `110294388018` (vinculado al Apps Script para acceso anónimo)

---

## Estado actual (lo que está funcionando HOY)

- [x] Landing page completa deployada en GitHub Pages
- [x] Formulario web → Apps Script → Google Sheets (tab "Leads") + email de notificación
- [x] CRM en Google Sheets con 5 tabs: Asesorías, Leads, Clientes, Contabilidad, Estrategia Captación
- [x] Dominio `www.cvas-consultora.cl` comprado en NIC Chile
- [x] Cloudflare configurado como DNS intermediario (nameservers + 5 registros DNS para GitHub Pages)
- [x] Email routing: `consuelo@cvas-consultora.cl` → `seleccion.cvas@gmail.com`
- [x] Página web muestra `consuelo@cvas-consultora.cl` como email de contacto

---

## Lo que NO existe aún / pendiente

- [ ] DNS propagación completada (NIC Chile → Cloudflare) — estimado 1–24h desde 22 mar 2026
- [ ] HTTPS activo en dominio custom (se activa automático al propagar DNS)
- [ ] WhatsApp Business configurado (Consuelo debe hacerlo desde su celular)
- [ ] Google Workspace (correo propio para envío — decisión diferida hasta tener tracción >50 leads/mes)

---

## Próximos 3 pasos

1. **Esperar DNS** (~1-24h): verificar que `www.cvas-consultora.cl` carga y habilitar "Enforce HTTPS" en GitHub Pages Settings → Pages
2. **WhatsApp Business**: Consuelo descarga la app, registra su número +56 9 8929 7668, configura perfil y mensajes automáticos
3. **Primer contenido LinkedIn**: ejecutar el plan de 30 días documentado en la tab "Estrategia Captación" del CRM

---

## Decisiones técnicas tomadas

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| Cloudflare como DNS | NIC Chile directo | NIC Chile no permite editar A records, solo nameservers |
| Cloudflare Email Routing (gratis) | Google Workspace ($8/mes) | Sin tracción aún — diferir costo |
| Apps Script vinculado a GCP 110294388018 | Proyecto GCP por defecto de clasp | El proyecto default no permite acceso anónimo al web app |
| Frontend en `/docs` (no `/web`) | Carpeta raíz | GitHub Pages solo acepta `/` o `/docs` |

---

## Estructura de archivos

```
consuelo-hr/
├── PROJECT_BRIEF.md          ← este archivo
├── docs/
│   ├── index.html            ← landing page (fuente de verdad del frontend)
│   └── CNAME                 ← www.cvas-consultora.cl
├── appscript/
│   ├── Código.js             ← backend formulario (EN PRODUCCIÓN — cambios requieren deploy manual)
│   ├── appsscript.json       ← config Apps Script
│   └── .clasp.json           ← scriptId del proyecto
├── setup_crm.py              ← script de creación del CRM (ya ejecutado, no volver a correr)
├── add_estrategia_tab.py     ← script que agregó tab Estrategia al CRM (ya ejecutado)
├── fetch_email.py            ← script para bajar adjuntos de Gmail (ya ejecutado)
├── crm_sheet_id.txt          ← ID del Google Sheet
└── inputs/                   ← adjuntos del email original (CV, propuestas)
```

---

## Workflow de deploy

### Frontend
```bash
cd ~/Projects/consuelo-hr
git add docs/index.html
git commit -m "descripción"
git push
# GitHub Pages actualiza en ~30 segundos
```

### Backend (Apps Script)
```bash
cd ~/Projects/consuelo-hr/appscript
export PATH="/opt/homebrew/opt/node@18/bin:$PATH"  # o node actual
clasp push --force
clasp deploy --deploymentId AKfycbx_95spFvepVEm_b8i3cdvWzJKuo3egVuww_j6enGgywG-KCWhqwvwdssCJiujbNeGa --description "descripción"
```
