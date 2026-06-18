import requests
import streamlit as st
import pandas as pd

API_URL = "https://respondia.onrender.com"

st.set_page_config(
    page_title="RespondIA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1050px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #312E81 0%, #1E1B4B 100%) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {color: #C7D2FE !important;}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {color: #FFFFFF !important;}
[data-testid="stSidebar"] hr {border-color: rgba(255,255,255,0.12) !important;}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: rgba(255,255,255,0.08) !important;
    color: #E0E7FF !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.16) !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
[data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #6366F1 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    color: #64748B !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 2px solid #E2E8F0;
    gap: 0;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    padding: 0.75rem 1.5rem;
    font-weight: 500;
    font-size: 0.9rem;
    color: #64748B;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #6366F1 !important;
    border-bottom-color: #6366F1 !important;
    background: transparent !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border-color: #CBD5E1 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* Buttons */
.stButton > button {border-radius: 8px; font-weight: 500;}

/* Login */
.login-header {text-align: center; padding: 1rem 0 1.5rem;}
.login-header h1 {font-size: 2.2rem; font-weight: 800; color: #312E81; letter-spacing: -0.02em; margin: 0;}
.login-header p {color: #64748B; margin-top: 0.4rem; font-size: 0.95rem;}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["X-API-Key"] = st.session_state.api_key
    return requests.request(method, f"{API_URL}{path}", headers=headers, timeout=60, **kwargs)


# ── LOGIN ─────────────────────────────────────────────────────────────────────

def login_screen():
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div class="login-header">
            <h1>⚡ RespondIA</h1>
            <p>Agente de IA que atiende a tus clientes por WhatsApp</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("**Código de acceso**")
            key_input = st.text_input(
                "código",
                type="password",
                placeholder="Pega aquí tu código",
                label_visibility="collapsed",
            )
            if st.button("Entrar →", type="primary", use_container_width=True):
                if not key_input.strip():
                    st.error("Ingresa tu código de acceso")
                    return
                with st.spinner("Verificando..."):
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
                            st.error("Código inválido. Verifica con tu administrador.")
                        else:
                            st.error(f"Error al conectar ({r.status_code})")
                    except Exception as e:
                        st.error(f"No se pudo conectar: {e}")

        st.markdown(
            "<p style='text-align:center;color:#94A3B8;font-size:0.8rem;margin-top:1rem'>"
            "¿Sin cuenta? Escríbenos para registrar tu pyme.</p>",
            unsafe_allow_html=True,
        )


if "api_key" not in st.session_state:
    login_screen()
    st.stop()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ RespondIA")
    st.divider()
    cfg_side = st.session_state.get("business_cfg", {})
    biz_name = cfg_side.get("business_name") or "Mi Negocio"
    st.markdown(f"### {biz_name}")
    st.caption(f"Código: `{st.session_state.api_key[:8]}…`")
    st.divider()
    if st.button("Cerrar sesión"):
        del st.session_state.api_key
        st.session_state.pop("business_cfg", None)
        st.rerun()


# ── STATS ─────────────────────────────────────────────────────────────────────

try:
    msgs = api("GET", "/conversations/").json()
    if not isinstance(msgs, list):
        msgs = []
except Exception:
    msgs = []

c1, c2, c3 = st.columns(3)
c1.metric("Mensajes totales", len(msgs))
c2.metric("Clientes atendidos", len({m["customer"] for m in msgs}) if msgs else 0)
c3.metric("Última actividad", msgs[0]["ts"][:10] if msgs else "—")

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────

tab_catalog, tab_config, tab_chat = st.tabs(["📦  Catálogo", "⚙️  Configuración", "💬  Conversaciones"])

# ── CATÁLOGO ──────────────────────────────────────────────────────────────────
with tab_catalog:
    st.markdown("### Catálogo del negocio")
    st.caption("El bot usa este contenido para responder las preguntas de tus clientes.")
    st.markdown("<br>", unsafe_allow_html=True)

    col_up, col_man = st.columns(2, gap="large")

    with col_up:
        with st.container(border=True):
            st.markdown("**Subir archivo**")
            st.caption("PDF, PNG o JPG — el texto se extrae automáticamente")
            uploaded = st.file_uploader("archivo", type=["pdf", "png", "jpg", "jpeg"],
                                        label_visibility="collapsed")
            if uploaded and st.button("Procesar ✨", type="primary", use_container_width=True):
                with st.spinner("Extrayendo texto..."):
                    try:
                        res = api("POST", "/catalog/upload",
                                  files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)})
                        res.raise_for_status()
                        data = res.json()
                        st.success(f"{data['characters']} caracteres extraídos")
                        st.text_area("Vista previa", data["preview"], height=180)
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col_man:
        with st.container(border=True):
            st.markdown("**Escribir manualmente**")
            st.caption("Lista de productos, precios y políticas de envío")
            current = ""
            try:
                current = api("GET", "/catalog/").json().get("catalog", "")
            except Exception:
                pass
            manual_text = st.text_area(
                "catálogo", value=current, height=200,
                placeholder="Polo básico S/M/L — S/30\nJean slim fit — S/89\nEnvíos Lima: S/10",
                label_visibility="collapsed",
            )
            if st.button("Guardar catálogo", use_container_width=True):
                try:
                    api("POST", "/catalog/manual", json={"text": manual_text})
                    st.success("Catálogo guardado")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
with tab_config:
    st.markdown("### Configuración del negocio")
    st.caption("El bot usará estos datos al presentarse con tus clientes.")
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        cfg_data = api("GET", "/catalog/config").json()
    except Exception:
        cfg_data = {}

    with st.container(border=True):
        biz_input = st.text_input("Nombre del negocio",
                                   value=cfg_data.get("business_name", ""),
                                   placeholder="Ej: Boutique Lucía")
        hours_input = st.text_input("Horario de atención",
                                     value=cfg_data.get("hours", ""),
                                     placeholder="Ej: Lunes a sábado 9am – 7pm")
        if st.button("Guardar configuración", type="primary"):
            try:
                api("POST", "/catalog/config",
                    json={"business_name": biz_input, "hours": hours_input})
                st.session_state.business_cfg = {"business_name": biz_input, "hours": hours_input}
                st.success("Configuración guardada")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Estado del bot**")
        st.info("Webhook activo → `https://respondia.onrender.com/webhook/whatsapp`", icon="✅")
        st.caption("Tu bot responde automáticamente en el número asignado a tu cuenta.")

# ── CONVERSACIONES ────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("### Conversaciones recientes")

    col_r, _ = st.columns([1, 6])
    with col_r:
        if st.button("Actualizar 🔄"):
            st.rerun()

    if not msgs:
        st.info("Aún no hay conversaciones. Envía un mensaje al bot para empezar.", icon="💬")
    else:
        df = pd.DataFrame(msgs)
        customers = df["customer"].unique().tolist()
        with st.container(border=True):
            selected = st.selectbox("Cliente", customers, label_visibility="collapsed")
            thread = df[df["customer"] == selected].sort_values("ts")
            st.divider()
            for _, row in thread.iterrows():
                role = "user" if row["role"] == "user" else "assistant"
                st.chat_message(role).write(row["content"])
