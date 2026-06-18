# RespondIA 🤖

> Agente de IA que atiende clientes por WhatsApp 24/7 para pymes peruanas, entrenado en minutos con el catálogo del negocio.

**Curso:** Data Science con Python 2026-I — Universidad del Pacífico  
**Autor:** Pietro Marcelo Nava Montenegro  
**Landing:** [pietronavam.github.io/respondIA](https://pietronavam.github.io/respondIA)  
**Panel:** [respond-ia.streamlit.app](https://respond-ia.streamlit.app/)  
**Backend API:** [respondia.onrender.com](https://respondia.onrender.com)

---

## El problema

El 95.6% de las pymes peruanas formales no vende por e-commerce y muchas gestionan pedidos por WhatsApp manualmente (EEA 2024, INEI). Un dueño de bodega o tienda pasa 4-6 horas al día respondiendo los mismos mensajes: precios, disponibilidad, horarios, delivery.

**Evidencia propia:** [Nava Montenegro (2026)](docs/) documenta que empresas con servicios digitales tienen 33% más productividad laboral que sus pares no-digitales (PSM, n=10,275), con una brecha que no se cierra sola.

## La solución

RespondIA conecta el WhatsApp del negocio con un agente de IA entrenado en el catálogo propio. En 5 minutos el dueño sube su lista de precios y el bot empieza a responder clientes automáticamente.

## Demo en vivo

Para probar el bot en WhatsApp:
1. Envía `join protection-memory` al número **+1 415 523 8886** (WhatsApp)
2. Escríbele al bot como si fueras un cliente (ej: "¿tienen polos talla M?")
3. Verifica la conversación en el [panel de control](https://respond-ia.streamlit.app/)

**Video demo (2 min):** _[completar]_

## Herramientas del curso utilizadas

| Herramienta | Uso en el proyecto | Lectura |
|---|---|---|
| **DeepSeek API** | LLM que genera respuestas inteligentes al cliente (compatible OpenAI SDK) | 12-14 |
| **PaddleOCR** | Extrae texto de PDFs/imágenes del catálogo | 14 |
| **Whisper (OpenAI)** | Transcribe notas de voz de WhatsApp en español | — |
| **FastAPI** | Backend REST + webhook Twilio | 8-10 |
| **Streamlit** | Dashboard de control para el dueño del negocio | 11 |
| **SQLite** | Historial de conversaciones por cliente | 9 |
| **Twilio** | Integración con WhatsApp Sandbox | — |

## Arquitectura

```
[Cliente WhatsApp]
      │ mensaje texto / audio
      ▼
[Twilio WhatsApp Sandbox]
      │ HTTP POST /webhook/whatsapp
      ▼
[FastAPI Backend — Render]
      ├── audio? → Whisper → transcripción
      ├── recupera historial de SQLite
      ├── carga catálogo del negocio
      └── DeepSeek API → genera respuesta
      │
      ▼
[Respuesta → Twilio → Cliente WhatsApp]

[Streamlit Dashboard — Streamlit Cloud]
      ├── Catálogo: sube PDF → PaddleOCR / texto manual
      ├── Configuración: nombre negocio, horario, webhook URL
      └── Conversaciones: historial en tiempo real
```

## Cómo correr localmente

```bash
# 1. Clonar repo
git clone https://github.com/pietronavam/respondIA.git
cd respondIA

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus keys (ver sección Variables de entorno)

# 3. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. Frontend (nueva terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Variables de entorno

```env
DEEPSEEK_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## Deploy

| Servicio | Plataforma | Config |
|---|---|---|
| Backend API | Render.com | Web Service · Python · rootDir=`backend` |
| Dashboard | Streamlit Community Cloud | branch `main` · file `frontend/app.py` |
| Landing page | GitHub Pages | branch `main` · folder `/docs` |

## Estructura del repositorio

```
respondIA/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── database.py              # SQLite — historial + settings
│   │   ├── routes/
│   │   │   ├── webhook.py           # Twilio WhatsApp webhook
│   │   │   ├── catalog.py           # Upload y gestión de catálogo
│   │   │   └── conversations.py     # Historial de chats
│   │   └── services/
│   │       ├── claude_service.py    # DeepSeek API (OpenAI-compatible)
│   │       ├── ocr.py               # PaddleOCR + PyMuPDF
│   │       └── whisper_service.py   # Whisper transcripción de audio
│   └── requirements.txt
├── frontend/
│   └── app.py                       # Streamlit dashboard
├── docs/
│   └── index.html                   # Landing page (GitHub Pages)
├── data/
├── .env.example
└── render.yaml
```

---

*Construido con Claude Code como co-founder técnico virtual.*
