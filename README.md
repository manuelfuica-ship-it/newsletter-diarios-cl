# Newsletter Diarios 📰

Sistema automático de recopilación de noticias de diarios chilenos con suscripción, incluyendo descarga diaria de ediciones digitales en PDF.

## ✨ Características Principales

### 1. 📰 Noticias Automáticas
- **Recopilación diaria** de artículos de 4 diarios chilenos
- **Extracción de contenido completo** desde páginas pagadas
- **Categorización automática** de noticias (Política, Economía, Deporte, etc.)
- **Búsqueda avanzada** con filtros por fecha, diario y categoría
- **Visualización en modal** con contenido formateado

**Diarios soportados:**
- El Mercurio
- La Tercera
- La Segunda
- DF

### 2. 📖 Lector de Ediciones Digitales
Una app web completa para descargar y leer las ediciones digitales en PDF:

✅ **Descarga automática** de PDFs desde GitHub (sin intermediarios)
✅ **Almacenamiento local** en el navegador (IndexedDB)
✅ **Lectura offline** sin necesidad de conexión
✅ **Navegación por páginas** con controles intuitivos
✅ **Gestión de almacenamiento** (ver espacio usado)
✅ **Sincronización manual** para obtener nuevos PDFs

**Acceso:** Haz clic en "📖 Mis Ediciones" en la app principal

### 3. ⚙️ Gestor de Credenciales
Una página segura para guardar tus credenciales de los diarios:

✅ **Encriptación local** (AES-256)
✅ **Almacenamiento en navegador** (solo tú puedes acceder)
✅ **Backup/Restauración** de credenciales (export/import JSON)
✅ **Gestión centralizada** de todos tus accesos

**Acceso:** Haz clic en "⚙️ Configuración" en la app principal

### 4. 📊 Estadísticas y Análisis
- Gráficos de noticias por diario
- Distribución por categoría
- Tendencias a lo largo del tiempo
- Estadísticas totales

---

## 🚀 Cómo Usar

### Opción A: Usar la App en GitHub Pages (Recomendado)

1. **Abre la app:**
   - Accede a: `https://manuelfuica-ship-it.github.io/newsletter-diarios-cl/`

2. **Configura tus credenciales:**
   - Haz clic en "⚙️ Configuración"
   - Ingresa usuario y contraseña para cada diario
   - Haz clic en "💾 Guardar" para cada uno
   - Las credenciales se guardan encriptadas en tu navegador

3. **Descarga ediciones digitales:**
   - Haz clic en "📖 Mis Ediciones"
   - Haz clic en "🔄 Sincronizar" para ver PDFs disponibles
   - Descarga los que desees (se guardan localmente)
   - Abre y lee sin conexión

4. **Lee las noticias:**
   - En la sección "📰 Noticias" verás todos los artículos
   - Usa los filtros para buscar por palabra, fecha o categoría
   - Haz clic en "Leer más" para ver el contenido completo

### Opción B: Ejecutar Localmente

```bash
# 1. Clona el repositorio
git clone https://github.com/manuelfuica-ship-it/newsletter-diarios-cl.git
cd newsletter-diarios-cl

# 2. Instala dependencias
pip3 install -r requirements.txt

# 3. Configura variables de entorno
export CREDENTIALS_JSON='[{"diary":"mercurio","username":"tu@email.com","password":"tucontraseña"},...]'
export SLACK_WEBHOOK_URL='https://hooks.slack.com/...'

# 4. Ejecuta el scraper
python3 src/scraper.py

# 5. Sirve la app web
cd web
python3 -m http.server 8000
# Abre http://localhost:8000 en tu navegador
```

---

## 🔄 Automatización Diaria (GitHub Actions)

El proyecto incluye un workflow automático que:

1. **Ejecuta diariamente** (por defecto desactivado, puedes activar)
2. **Descarga ediciones PDF** de los 4 diarios
3. **Extrae noticias** de cada periódico
4. **Envía notificación** a Slack
5. **Actualiza la web app** con nuevos artículos

### Para activar la automatización:

1. **Crear credenciales en GitHub Secrets:**
   - Ve a tu repositorio → Settings → Secrets and variables → Actions
   - Crear dos secrets:
     - `CREDENTIALS_JSON`: JSON con credenciales de los diarios
     - `SLACK_WEBHOOK_URL`: URL del webhook de Slack (opcional)

2. **Formato de CREDENTIALS_JSON:**
   ```json
   [
     {"diary":"mercurio","username":"tu@email.com","password":"contraseña"},
     {"diary":"tercera","username":"tu@email.com","password":"contraseña"},
     {"diary":"segunda","username":"tu@email.com","password":"contraseña"},
     {"diary":"df","username":"tu@email.com","password":"contraseña"}
   ]
   ```

3. **Activar el workflow:**
   - Ve a GitHub → Actions → Newsletter Diarios
   - Haz clic en "Run workflow"

---

## 🔒 Seguridad

### Credenciales Locales
- Se guardan **encriptadas** en tu navegador
- **Solo tú** puedes acceder (no se envían a servidores)
- Puedes exportar/importar para respaldar

### En GitHub Actions
- Las credenciales se almacenan en GitHub Secrets (encriptadas)
- Se usan **solo para la automatización**
- Nunca se registran en los logs

### PDFs
- Se descargan desde GitHub
- Se guardan en **IndexedDB** (almacenamiento local del navegador)
- Puedes leer offline sin conexión

---

## 📁 Estructura del Proyecto

```
newsletter-diarios-cl/
├── src/
│   ├── scraper.py              # Orquestador principal
│   ├── playwright_scraper.py   # Scraper con navegador
│   ├── pdf_exporter.py         # Descargador de PDFs
│   ├── pdf_manifest.py         # Generador de índice
│   └── slack_sender.py         # Envío a Slack
├── web/
│   ├── index.html              # App principal (noticias)
│   ├── pdfs-reader.html        # Lector de PDFs
│   ├── settings.html           # Gestor de credenciales
│   ├── pdfs/                   # PDFs descargados
│   ├── data/
│   │   ├── news.json           # Noticias guardadas
│   │   └── pdfs-manifest.json  # Índice de PDFs
│   ├── styles.css              # Estilos compartidos
│   └── app.js                  # JavaScript de la app
├── .github/
│   └── workflows/
│       └── newsletter.yml      # Automatización diaria
└── requirements.txt            # Dependencias Python
```

---

## 🛠️ Tecnologías Usadas

**Backend:**
- Python 3.11
- Playwright (navegación web)
- BeautifulSoup4 (parsing HTML)
- feedparser (feeds RSS)
- requests (HTTP)

**Frontend:**
- HTML5, CSS3, JavaScript
- PDF.js (visualización de PDFs)
- crypto-js (encriptación)
- Chart.js (gráficos)
- IndexedDB (almacenamiento local)

**Hosting:**
- GitHub Pages (web app)
- GitHub Actions (automatización)
- GitHub (almacenamiento de PDFs)

---

## 📚 Guía de Uso - Paso a Paso

### Paso 1: Abre la App
```
https://manuelfuica-ship-it.github.io/newsletter-diarios-cl/
```

### Paso 2: Guarda tus Credenciales
1. Haz clic en "⚙️ Configuración" (arriba a la derecha)
2. Para cada diario:
   - Ingresa tu email/usuario
   - Ingresa tu contraseña
   - Haz clic en "💾 Guardar"
3. Las credenciales se guardan encriptadas en tu navegador

### Paso 3: Descarga Ediciones
1. Haz clic en "📖 Mis Ediciones"
2. Haz clic en "🔄 Sincronizar" (abajo a la izquierda)
3. Espera a que aparezcan los PDFs disponibles
4. Haz clic en cualquier edición para descargarla
5. Una vez descargada, haz clic para leerla

### Paso 4: Lee las Noticias
1. Vuelve a "📰 Noticias" (pestaña principal)
2. Usa los filtros:
   - **Buscar:** Escribe palabras clave
   - **Fecha:** Selecciona rango de fechas
   - **Diario:** Haz clic en un diario para filtrar
   - **Categoría:** Selecciona una categoría
3. Haz clic en "Leer más" para ver el contenido completo

### Paso 5: Ve las Estadísticas
1. Haz clic en "📊 Estadísticas"
2. Observa gráficos de:
   - Noticias por diario
   - Distribución por categoría
   - Tendencias en el tiempo

---

## ❓ Preguntas Frecuentes

**P: ¿Dónde se guardan mis credenciales?**
R: En el almacenamiento local de tu navegador, encriptadas con AES-256. Solo tú puedes acceder.

**P: ¿Puedo leer offline?**
R: Sí. Los PDFs se descargan y guardan localmente. Puedes leerlos sin conexión.

**P: ¿Qué pasa si borro el almacenamiento del navegador?**
R: Se pierden las credenciales y PDFs. Puedes exportar un backup desde Configuración.

**P: ¿Puedo usar esto en múltiples dispositivos?**
R: Sí. Exporta tus credenciales desde Configuración e importa en otro dispositivo.

**P: ¿Se envían datos a servidores externos?**
R: No. Todo funciona localmente. Solo se conecta a GitHub para descargar PDFs.

**P: ¿Puedo pausar la automatización?**
R: Sí. En GitHub → Actions → Newsletter Diarios → Disable workflow

---

## 📞 Soporte

Para reportar problemas o sugerencias:
- Abre un issue en GitHub
- Revisa el log de GitHub Actions

---

**Última actualización:** 2026-07-21
**Versión:** 2.0
