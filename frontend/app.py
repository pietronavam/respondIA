import requests
import streamlit as st
import pandas as pd

API_URL = "https://respondia.onrender.com"

st.set_page_config(
    page_title="RespondIA — Panel de Control",
    page_icon="🤖",
    layout="wide",
)

# ── AUTH ──────────────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["X-API-Key"] = st.session_state.api_key
    return requests.request(method, f"{API_URL}{path}", headers=headers, timeout=60, **kwargs)


def login_screen():
    st.title("🤖 RespondIA")
    st.markdown("### Ingresa tu API Key para acceder al panel")

    col, _ = st.columns([1, 1])
    with col:
        key_input = st.text_input(
            "API Key",
            type="password",
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        )
        if st.button("Conectar", type="primary", use_container_width=True):
            if not key_input.strip():
                st.error("Ingresa tu API Key")
                return
            try:
                r = requests.get(
                    f"{API_URL}/catalog/config",
                    headers={"X-API-Key": key_input.strip()},
                    timeout=10,
                )
                if r.status_code == 200:
                    st.session_state.api_key = key_input.strip()
                    st.session_state.business_cfg = r.json()
                    st.rerun()
                elif r.status_code == 401:
                    st.error("API Key inválida. Verifica con tu administrador.")
                else:
                    st.error(f"Error al conectar ({r.status_code})")
            except Exception as e:
                st.error(f"No se pudo conectar al backend: {e}")

        st.divider()
        st.caption("¿No tienes una cuenta? Contacta a RespondIA para registrar tu pyme.")


if "api_key" not in st.session_state:
    login_screen()
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🤖 RespondIA")
    cfg = st.session_state.get("business_cfg", {})
    st.markdown(f"**{cfg.get('business_name', 'Mi Negocio')}**")
    st.caption(f"API Key: `{st.session_state.api_key[:8]}…`")
    st.divider()
    if st.button("Cerrar sesión", use_container_width=True):
        del st.session_state.api_key
        if "business_cfg" in st.session_state:
            del st.session_state.business_cfg
        st.rerun()

# ── TABS ──────────────────────────────────────────────────────────────────────

st.title("Panel de Control")
tab_catalog, tab_config, tab_chat = st.tabs(["📦 Catálogo", "⚙️ Configuración", "💬 Conversaciones"])

# ── CATÁLOGO ──────────────────────────────────────────────────────────────────
with tab_catalog:
    st.header("Catálogo del negocio")
    st.markdown(
        "Sube tu lista de precios en **PDF o imagen** — RespondIA extrae el texto "
        "y lo usa para responder a tus clientes automáticamente."
    )

    col_upload, col_manual = st.columns(2, gap="large")

    with col_upload:
        st.subheader("Subir archivo")
        uploaded = st.file_uploader(
            "Lista de precios, catálogo o brochure",
            type=["pdf", "png", "jpg", "jpeg"],
        )
        if uploaded and st.button("Procesar ✨", type="primary"):
            with st.spinner("Extrayendo texto..."):
                try:
                    res = api("POST", "/catalog/upload",
                              files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)})
                    res.raise_for_status()
                    data = res.json()
                    st.success(f"Catálogo cargado — {data['characters']} caracteres extraídos")
                    st.text_area("Vista previa:", data["preview"], height=250)
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_manual:
        st.subheader("Escribir manualmente")
        current = ""
        try:
            r = api("GET", "/catalog/")
            current = r.json().get("catalog", "")
        except Exception:
            pass

        manual_text = st.text_area(
            "Escribe o pega tu catálogo:",
            value=current,
            height=300,
            placeholder="Polo básico talla S/M/L — S/30\nJean slim fit — S/89\n...",
        )
        if st.button("Guardar catálogo"):
            try:
                api("POST", "/catalog/manual", json={"text": manual_text})
                st.success("Catálogo guardado correctamente")
            except Exception as e:
                st.error(f"Error: {e}")

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
with tab_config:
    st.header("Configuración del negocio")

    try:
        cfg = api("GET", "/catalog/config").json()
    except Exception:
        cfg = {"business_name": "", "hours": ""}

    business_name = st.text_input("Nombre del negocio", value=cfg.get("business_name", ""))
    hours = st.text_input(
        "Horario de atención",
        value=cfg.get("hours", "Lunes a sábado 9am-7pm"),
    )

    if st.button("Guardar configuración", type="primary"):
        try:
            api("POST", "/catalog/config",
                json={"business_name": business_name, "hours": hours})
            st.session_state.business_cfg = {"business_name": business_name, "hours": hours}
            st.success("Configuración guardada")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.subheader("Número de WhatsApp asignado")
    st.info(
        "Tu número de WhatsApp está configurado automáticamente. "
        "El webhook apunta a `https://respondia.onrender.com/webhook/whatsapp`."
    )

# ── CONVERSACIONES ────────────────────────────────────────────────────────────
with tab_chat:
    st.header("Conversaciones recientes")

    if st.button("Actualizar 🔄"):
        st.rerun()

    try:
        msgs = api("GET", "/conversations/").json()
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
