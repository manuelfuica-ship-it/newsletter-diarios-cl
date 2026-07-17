# 📰 Newsletter Diarios — Sistema Automático

Sistema completo para recopilar noticias diarias de cuatro medios de prensa chilenos y distribuir un newsletter automático por email y Slack.

**Medios soportados:** El Mercurio, La Tercera, La Segunda, DF (Diario Financiero)

---

## 🚀 Quick Start

### 1. Configurar credenciales (Local)

1. Abre `credenciales.html` en tu navegador (doble-click o `python3 -m http.server`)
2. Ingresa una contraseña maestra fuerte
3. Agrega credenciales para cada uno de los 4 diarios
4. Copia el JSON cifrado que se genera

### 2. Crear repositorio en GitHub

```bash
# En GitHub.com:
# - Nombre: newsletter-diarios-cl
# - Público: Sí
# - Agregar .gitignore: Python
```

### 3. Agregar Secrets en GitHub

Ve a `Settings > Secrets and variables > Actions` y agrega:

| Secret | Valor |
|--------|-------|
| `CREDENTIALS_ENCRYPTED` | El JSON cifrado del paso 1 |
| `ENCRYPTION_PASSWORD` | Tu contraseña maestra |
| `SMTP_SERVER` | `smtp.gmail.com` (o tu servidor) |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | tu@gmail.com |
| `SMTP_PASSWORD` | Contraseña o app password |
| `RECIPIENT_EMAIL` | Donde enviar el newsletter |
| `SLACK_WEBHOOK_URL` | URL del webhook de Slack |

### 4. Estructura de archivos en GitHub

```
newsletter-diarios-cl/
├── .github/workflows/
│   └── newsletter.yml        ← Copiar el archivo AQUÍ
├── src/
│   ├── scraper.py
│   ├── email_sender.py
│   ├── slack_sender.py
│   └── __init__.py
├── requirements.txt
├── .env.example
└── README.md
```

### 5. Probar ejecución

En GitHub > Actions > Newsletter > "Run workflow"

---

## 🔧 Desarrollo Local

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Editar .env

```env
CREDENTIALS_ENCRYPTED=U2FsdGVkX1...
ENCRYPTION_PASSWORD=MiContraseña
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@gmail.com
SMTP_PASSWORD=app-password
RECIPIENT_EMAIL=tu@email.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

### Ejecutar

```bash
python3 src/scraper.py
```

---

## 📧 Configurar Email (Gmail)

1. **Habilitar 2FA** en tu cuenta Google
2. **Generar App Password:**
   - Ve a https://myaccount.google.com/apppasswords
   - Selecciona "Mail" y "Windows Computer" (o tu dispositivo)
   - Copia la contraseña generada
3. **Usar en SMTP_PASSWORD**

---

## 💬 Configurar Slack

1. **Crear Slack App:**
   - Ve a https://api.slack.com/apps
   - Click "Create New App" > "From scratch"
   - Nombre: Newsletter Diarios
   - Workspace: Tu workspace

2. **Habilitar Incoming Webhooks:**
   - Left menu > "Incoming Webhooks"
   - Click "Add New Webhook to Workspace"
   - Selecciona el canal destino (ej: #noticias)
   - Copia la URL

3. **Usar en SLACK_WEBHOOK_URL**

---

## ⏰ Programación

El workflow ejecuta **lunes-viernes a las 06:00 UTC-3** (08:00 UTC).

Para cambiar:
- Edita `.github/workflows/newsletter.yml`
- Modifica la línea `cron: '0 8 * * 1-5'`
- Referencia: https://crontab.guru

---

## 🔒 Seguridad

- **Credenciales:** Encriptadas AES-256 en el cliente (crypto-js)
- **Contraseña maestra:** No se almacena, solo en tu máquina local
- **GitHub Secrets:** Encriptados por GitHub, solo accesibles en workflows
- **Code:** No contiene datos sensibles, es público

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| "Invalid encrypted format" | Regenera credenciales en `credenciales.html` |
| Email no llega | Verifica App Password, puertos SMTP, firewall |
| Slack vacío | Verifica webhook URL, permisos del canal |
| Pocas noticias | Algunos sitios requieren login; edita `src/scraper.py` |

---

## 📝 Actualizar Credenciales

Si cambias contraseñas de los diarios:

1. Abre `credenciales.html`
2. Edita o reemplaza la credencial
3. Copia el nuevo JSON cifrado
4. Actualiza `CREDENTIALS_ENCRYPTED` en GitHub Secrets

---

## 📚 Archivos

- **credenciales.html** — Gestor local de credenciales (UI web)
- **src/scraper.py** — Lógica de scraping (4 diarios)
- **src/email_sender.py** — Envío por email SMTP
- **src/slack_sender.py** — Envío a Slack
- **newsletter.yml** — Workflow de GitHub Actions
- **contexto.md** — Documentación del proyecto

---

## 🔄 Roadmap (Fase 2)

- [ ] Base de datos (Supabase) para histórico
- [ ] Clasificación temática de noticias
- [ ] Web view con archivo de noticias
- [ ] Alertas por palabra clave
- [ ] Dashboard de estadísticas

---

**Última actualización:** 2026-01-17  
**Maintainer:** Manuel Fuica
