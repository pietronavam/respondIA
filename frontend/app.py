import os
import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="RespondIA — Panel de Control",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 RespondIA")
st.caption("Agente de IA que atiende clientes por WhatsApp para tu pyme")

tab_catalog, tab_config, tab_chat = st.tabs(["📦 Catálogo", "⚙️ Configuración", "💬 Conversaciones"])

# ── CATÁLOGO ──────────────────────────────────────────────────────────────────
with tab_catalog:
    st.header("Carga el catálogo de tu negocio")
    st.markdown(
        "Sube tu lista de precios en **PDF o imagen** — RespondIA extrae el texto "
        "con **PaddleOCR** y lo usa para responder a tus clientes automáticamente."
    )

    col_upload, col_manual = st.columns(2, gap="large")

    with col_upload:
        st.subheader("Opción 1 — Subir archivo")
        uploaded = st.file_uploader(
            "Lista de precios, catálogo o brochure",
            type=["pdf", "png", "jpg", "jpeg"],
        )
        if uploaded and st.button("Procesar con PaddleOCR ✨", type="primary"):
            with st.spinner("Extrayendo texto con PaddleOCR..."):
                try:
                    res = requests.post(
                        f"{API_URL}/catalog/upload",
                        files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                        timeout=60,
                    )
                    res.raise_for_status()
                    data = res.json()
                    st.success(f"Catálogo cargado — {data['characters']} caracteres extraídos")
                    st.text_area("Vista previa del texto extraído:", data["preview"], height=250)
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_manual:
        st.subheader("Opción 2 — Escribir manualmente")
        current = ""
        try:
            r = requests.get(f"{API_URL}/catalog/", timeout=5)
            current = r.json().get("catalog", "")
        except Exception:
            pass

        manual_text = st.text_area(
            "Escribe o pega aquí tu catálogo:",
            value=current,
            height=300,
            placeholder="Polo básico talla S/M/L — S/30\nJean slim fit — S/89\nEntrega: Lima Metropolitana, costo S/10\n...",
        )
        if st.button("Guardar catálogo"):
            try:
                requests.post(f"{API_URL}/catalog/manual", json={"text": manual_text}, timeout=10)
                st.success("Catálogo guardado correctamente")
            except Exception as e:
                st.error(f"Error: {e}")

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
with tab_config:
    st.header("Configuración del negocio")

    try:
        cfg = requests.get(f"{API_URL}/catalog/config", timeout=5).json()
    except Exception:
        cfg = {"business_name": "", "hours": ""}

    business_name = st.text_input("Nombre del negocio", value=cfg.get("business_name", ""))
    hours = st.text_input(
        "Horario de atención",
        value=cfg.get("hours", "Lunes a sábado 9am-7pm"),
    )

    if st.button("Guardar configuración", type="primary"):
        try:
            requests.post(
                f"{API_URL}/catalog/config",
                json={"business_name": business_name, "hours": hours},
                timeout=10,
            )
            st.success("Configuración guardada")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.subheader("Conectar WhatsApp (Twilio Sandbox)")
    st.markdown(
        """
**Pasos para activar el bot en WhatsApp:**

1. Ve a [console.twilio.com](https://console.twilio.com) → Messaging → Try it out → Send a WhatsApp message
2. Escanea el QR o envía el código al número sandbox
3. En "Sandbox Settings", pega esta URL en el campo **When a message comes in**:
"""
    )
    backend_url = st.text_input("URL pública de tu backend (Render)", placeholder="https://respondIA.onrender.com")
    if backend_url:
        webhook_url = f"{backend_url.rstrip('/')}/webhook/whatsapp"
        st.code(webhook_url, language="text")
        st.success("Copia esta URL y pégala en Twilio Sandbox Settings")

# ── CONVERSACIONES ────────────────────────────────────────────────────────────
with tab_chat:
    st.header("Conversaciones recientes")

    if st.button("Actualizar 🔄"):
        st.rerun()

    try:
        res = requests.get(f"{API_URL}/conversations/", timeout=10)
        msgs = res.json()
    except Exception:
        msgs = []

    if not msgs:
        st.info("Aún no hay conversaciones. Manda un mensaje al bot por WhatsApp para empezar.")
    else:
        df = pd.DataFrame(msgs)
        customers = df["customer"].unique().tolist()
        selected = st.selectbox("Selecciona un cliente", customers)

        thread = df[df["customer"] == selected].sort_values("ts")
        for _, row in thread.iterrows():
            if row["role"] == "user":
                st.chat_message("user").write(row["content"])
            else:
                st.chat_message("assistant").write(row["content"])
