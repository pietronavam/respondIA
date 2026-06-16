# RespondIA 🤖

> Agente de IA que atiende clientes por WhatsApp 24/7 para pymes peruanas, entrenado en minutos con el catálogo del negocio.

**Curso:** Data Science con Python 2026-I — Universidad del Pacífico  
**Autor:** Pietro Marcelo Nava Montenegro  
**Demo:** _[URL del deploy — completar]_

---

## El problema

El 95.6% de las pymes peruanas formales no vende por e-commerce y muchas gestionan pedidos por WhatsApp manualmente (EEA 2024, INEI). Un dueño de bodega o tienda pasa 4-6 horas al día respondiendo los mismos mensajes: precios, disponibilidad, horarios, delivery.

**Evidencia propia:** [Nava Montenegro (2026)](docs/) documenta que empresas con servicios digitales tienen 33% más productividad laboral que sus pares no-digitales (PSM, n=10,275), con una brecha que no se cierra sola.

## La solución

RespondIA conecta el WhatsApp del negocio con un agente de IA entrenado en el catálogo propio. En 5 minutos el dueño sube su lista de precios y el bot empieza a responder clientes automáticamente.

## Demo

**URL pública:** _[completar tras el deploy]_  
**Video demo (2 min):** _[completar]_

Para probar el bot en WhatsApp:
1. Envía `join <código-sandbox>` al número `+1 415 523 8886`
2. Escríbele al bot como si fueras un cliente

## Herramientas del curso utilizadas

| Herramienta | Uso en el proyecto | Lectura |
|---|---|---|
| **PaddleOCR** | Extrae texto de PDFs/imágenes del catálogo | 14 |
| **Claude API (Anthropic)** | Genera respuestas inteligentes al cliente | 12-14 |
| **Whisper** | Transcribe notas de voz de WhatsApp en español | - |

## Arquitectura

```
[Cliente WhatsApp]
      │ mensaje texto / audio
      ▼
[Twilio WhatsApp Sandbox]
      │ HTTP POST webhook
      ▼
[FastAPI Backend — Render]
      ├── audio? → Whisper → transcripción
      ├── busca contexto en catálogo del negocio
      └── Claude Haiku → genera respuesta
      │
      ▼
[Respuesta → Twilio → Cliente]

[Streamlit Dashboard — Streamlit Cloud]
      └── Dueño sube PDF → PaddleOCR → catálogo
```

## Cómo correr localmente

```bash
# 1. Clonar repo
git clone https://github.com/tu-usuario/respondIA.git
cd respondIA

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus keys

# 3. Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. Frontend (nueva terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

- **Backend:** Render.com (Web Service, Python, rootDir=backend)
- **Frontend:** Streamlit Community Cloud (branch main, file frontend/app.py)

## Estructura del repositorio

```
respondIA/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── database.py       # SQLite
│   │   ├── routes/
│   │   │   ├── webhook.py    # Twilio WhatsApp webhook
│   │   │   ├── catalog.py    # Upload y gestión de catálogo
│   │   │   └── conversations.py
│   │   └── services/
│   │       ├── claude_service.py   # Claude API
│   │       ├── ocr.py              # PaddleOCR + PyMuPDF
│   │       └── whisper_service.py  # Whisper transcripción
│   └── requirements.txt
├── frontend/
│   └── app.py                # Streamlit dashboard
├── docs/                     # Paper, pitch deck, diagramas
├── data/
├── .env.example
└── render.yaml
```

---

*Construido con Claude Code como co-founder técnico virtual.*
