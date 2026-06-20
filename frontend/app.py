import requests
import streamlit as st
import pandas as pd

API_URL = "https://respondia.onrender.com"

st.set_page_config(
    page_title="RespondIA",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
header {visibility: visible;}
header [data-testid="stToolbar"] {visibility: hidden;}

.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1050px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 60%, #0d3320 100%) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {color: #94a3b8 !important;}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {color: #FFFFFF !important;}
[data-testid="stSidebar"] hr {border-color: rgba(255,255,255,0.10) !important;}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: rgba(37,211,102,0.10) !important;
    color: #25D366 !important;
    border: 1px solid rgba(37,211,102,0.25) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(37,211,102,0.20) !important;
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
    color: #25D366 !important;
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
    color: #25D366 !important;
    border-bottom-color: #25D366 !important;
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
    border-color: #25D366 !important;
    box-shadow: 0 0 0 3px rgba(37,211,102,0.12) !important;
}

/* Buttons */
.stButton > button {border-radius: 8px; font-weight: 500;}

/* Login */
.login-header {text-align: center; padding: 1rem 0 1.5rem;}
.login-header h1 {font-size: 2.2rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; margin: 0;}
.login-header p {color: #64748B; margin-top: 0.4rem; font-size: 0.95rem;}

/* Order table */
.order-table-header {
    display: grid;
    grid-template-columns: 70px 130px 1fr 1fr 70px 110px 130px;
    gap: 0;
    padding: 0.5rem 1rem;
    background: #F1F5F9;
    border-radius: 8px 8px 0 0;
    border: 1px solid #E2E8F0;
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.order-row {
    display: grid;
    grid-template-columns: 70px 130px 1fr 1fr 70px 110px 130px;
    gap: 0;
    padding: 0.75rem 1rem;
    border: 1px solid #E2E8F0;
    border-top: none;
    background: white;
    font-size: 0.875rem;
    color: #1E293B;
    align-items: center;
}
.order-row:last-child {border-radius: 0 0 8px 8px;}
.order-row:hover {background: #F8FAFC;}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-pendiente {background: #FEF9C3; color: #854D0E;}
.badge-pagado    {background: #DCFCE7; color: #166534;}
.badge-enviado   {background: #DBEAFE; color: #1E40AF;}
.badge-entregado {background: #F0FDF4; color: #15803D;}
.order-code {font-weight: 700; color: #6366F1; font-size: 0.875rem;}
.order-meta {font-size: 0.8rem; color: #64748B;}
.order-total {font-weight: 700; color: #0F172A;}

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
            <h1><span style="color:#0f172a">Respond</span><span style="color:#25D366">IA</span></h1>
            <p>Agente de IA que atiende a tus clientes por WhatsApp</p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            email_input = st.text_input("Correo electrónico", placeholder="tucorreo@gmail.com")
            pass_input  = st.text_input("Contraseña", type="password", placeholder="••••••••")
            if st.button("Entrar →", type="primary", use_container_width=True):
                if not email_input.strip() or not pass_input:
                    st.error("Ingresa tu correo y contraseña")
                    return
                with st.spinner("Verificando..."):
                    try:
                        r = requests.post(
                            f"{API_URL}/login",
                            json={"email": email_input.strip(), "password": pass_input},
                            timeout=10,
                        )
                        if r.status_code == 200:
                            data = r.json()
                            st.session_state.api_key = data["api_key"]
                            st.session_state.business_cfg = {"business_name": data["business_name"]}
                            st.rerun()
                        elif r.status_code == 401:
                            st.error("Correo o contraseña incorrectos")
                        else:
                            st.error(f"Error al conectar ({r.status_code})")
                    except Exception as e:
                        st.error(f"No se pudo conectar: {e}")

        st.markdown(
            "<p style='text-align:center;color:#94A3B8;font-size:0.8rem;margin-top:1rem'>"
            "¿Sin cuenta? <a href='https://pietronavam.github.io/respondIA/#registro' "
            "style='color:#6366F1'>Regístrate gratis</a></p>",
            unsafe_allow_html=True,
        )


if "api_key" not in st.session_state:
    login_screen()
    st.stop()


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## <span style='color:#ffffff'>Respond</span><span style='color:#25D366'>IA</span>", unsafe_allow_html=True)
    st.divider()
    cfg_side = st.session_state.get("business_cfg", {})
    biz_name = cfg_side.get("business_name") or "Mi Negocio"
    st.markdown(f"### {biz_name}")
    st.caption(f"Código: `{st.session_state.api_key[:8]}…`")

    # Fetch and cache tenant info (phone number)
    if "tenant_info" not in st.session_state:
        try:
            info = api("GET", "/tenants/me").json()
            st.session_state.tenant_info = info
        except Exception:
            st.session_state.tenant_info = {}
    info = st.session_state.get("tenant_info", {})
    phone = info.get("phone_number", "")
    if phone and not phone.startswith("sandbox:"):
        digits = phone.replace("whatsapp:", "").replace("+", "").replace(" ", "")
        display = phone.replace("whatsapp:", "")
        wa_link = f"https://wa.me/{digits}"
        st.markdown(f"""
        <div style='margin-top:4px'>
          <div style='font-size:0.68rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px'>Número WhatsApp</div>
          <div style='background:rgba(37,211,102,0.12);border:1px solid rgba(37,211,102,0.3);border-radius:8px;padding:8px 10px;font-family:monospace;font-size:0.82rem;color:#25D366;font-weight:700'>{display}</div>
          <a href='{wa_link}' target='_blank' style='display:block;margin-top:6px;text-align:center;background:#25D366;color:#0f172a;font-weight:700;font-size:0.78rem;padding:7px 10px;border-radius:7px;text-decoration:none;'>
            💬 Abrir chat en WhatsApp
          </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        slug = info.get("slug") or ""
        wa_link = f"https://wa.me/14155238886?text={slug}" if slug else "https://wa.me/14155238886"
        st.markdown("""
        <div style='font-size:0.68rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px'>
          Link de WhatsApp de tu negocio
        </div>
        <div style='font-size:0.7rem;color:#475569;margin-bottom:8px;line-height:1.5'>
          Comparte este link en tu Instagram, web o tarjeta. Tus clientes solo tocan el link y el bot ya los atiende.
        </div>
        """, unsafe_allow_html=True)
        if slug:
            st.code(wa_link, language=None)
        st.markdown(f"""
        <a href='{wa_link}' target='_blank' style='display:block;text-align:center;background:#25D366;color:#0f172a;font-weight:700;font-size:0.82rem;padding:10px 10px;border-radius:8px;text-decoration:none;margin-bottom:8px'>
          💬 Probar mi bot
        </a>
        """, unsafe_allow_html=True)
        if slug:
            st.markdown(f"""
            <div style='background:rgba(99,102,241,0.10);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:8px 12px'>
              <div style='font-size:0.65rem;color:#818cf8;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px'>Tu código único</div>
              <div style='font-size:1.05rem;font-weight:800;color:#c7d2fe;font-family:monospace;letter-spacing:3px'>{slug}</div>
              <div style='font-size:0.65rem;color:#64748b;margin-top:3px'>Plan Pro incluye número exclusivo sin código.</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    if st.button("Cerrar sesión"):
        del st.session_state.api_key
        st.session_state.pop("business_cfg", None)
        st.session_state.pop("tenant_info", None)
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

tab_catalog, tab_config, tab_orders, tab_chat = st.tabs(["📦  Catálogo", "⚙️  Configuración", "🛒  Pedidos", "💬  Conversaciones"])

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
        st.markdown("**Datos del negocio**")
        biz_input = st.text_input("Nombre del negocio",
                                   value=cfg_data.get("business_name", ""),
                                   placeholder="Ej: Boutique Lucía")
        hours_input = st.text_input("Horario de atención",
                                     value=cfg_data.get("hours", ""),
                                     placeholder="Ej: Lunes a sábado 9am – 7pm")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Métodos de pago**")
        st.caption("El bot los enviará automáticamente cuando un cliente quiera comprar.")
        col_y, col_p = st.columns(2)
        with col_y:
            yape_input = st.text_input("Número Yape",
                                        value=cfg_data.get("yape_number", ""),
                                        placeholder="Ej: 987654321")
        with col_p:
            plin_input = st.text_input("Número Plin",
                                        value=cfg_data.get("plin_number", ""),
                                        placeholder="Ej: 987654321")
        culqi_input = st.text_input("Link de pago Culqi (opcional)",
                                     value=cfg_data.get("culqi_link", ""),
                                     placeholder="https://checkout.culqi.com/...")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Guardar configuración", type="primary"):
        try:
            api("POST", "/catalog/config", json={
                "business_name": biz_input,
                "hours": hours_input,
                "yape_number": yape_input,
                "plin_number": plin_input,
                "culqi_link": culqi_input,
            })
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

# ── PEDIDOS ───────────────────────────────────────────────────────────────────
with tab_orders:
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.markdown("### Pedidos")
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Actualizar 🔄", key="refresh_orders", use_container_width=True):
            st.rerun()

    try:
        order_list = api("GET", "/orders/").json()
        if not isinstance(order_list, list):
            order_list = []
    except Exception:
        order_list = []

    if not order_list:
        st.info("Aún no hay pedidos. Cuando un cliente compre por WhatsApp aparecerá aquí.", icon="🛒")
    else:
        STATUS_OPTIONS = ["pendiente", "pagado", "enviado", "entregado"]
        BADGE_CLASS = {
            "pendiente": "badge-pendiente",
            "pagado":    "badge-pagado",
            "enviado":   "badge-enviado",
            "entregado": "badge-entregado",
        }

        # Table header — same column proportions as data rows
        COLS = [1, 1.8, 1.5, 2, 0.9, 1.5, 1.8]
        HEADERS = ["PEDIDO", "FECHA", "CLIENTE", "PRODUCTO", "TOTAL", "ESTADO", "ACCIÓN"]
        h_cols = st.columns(COLS)
        for col, label in zip(h_cols, HEADERS):
            col.markdown(
                f"<div style='text-align:center;font-size:0.72rem;font-weight:700;"
                f"color:#64748B;letter-spacing:0.06em;padding:6px 0;"
                f"background:#F1F5F9;border-bottom:1px solid #E2E8F0'>{label}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        for order in order_list:
            badge = BADGE_CLASS.get(order["status"], "badge-pendiente")
            date_str = order["created_at"][:16].replace("T", " ") if order["created_at"] else "—"
            customer_short = order["customer"].replace("whatsapp:+51", "+51 ").replace("whatsapp:", "")

            # Static row (HTML) + interactive action (Streamlit columns)
            C = "<div style='text-align:center;padding-top:6px'>"
            E = "</div>"
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 1.8, 1.5, 2, 0.9, 1.5, 1.8])
            with c1:
                st.markdown(f"{C}<span class='order-code'>{order['code']}</span>{E}", unsafe_allow_html=True)
            with c2:
                st.markdown(f"{C}<span class='order-meta'>{date_str}</span>{E}", unsafe_allow_html=True)
            with c3:
                st.markdown(f"{C}<span class='order-meta'>{customer_short}</span>{E}", unsafe_allow_html=True)
            with c4:
                st.markdown(f"{C}<span style='font-size:0.875rem'>{order['items']}</span>{E}", unsafe_allow_html=True)
            with c5:
                st.markdown(f"{C}<span class='order-total'>S/{order['total']}</span>{E}", unsafe_allow_html=True)
            with c6:
                st.markdown(f"{C}<span class='badge {badge}'>{order['status']}</span>{E}", unsafe_allow_html=True)
            with c7:
                new_status = st.selectbox(
                    "estado",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(order["status"]),
                    key=f"sel_{order['id']}",
                    label_visibility="collapsed",
                )
                if new_status != order["status"]:
                    if st.button("✓", key=f"upd_{order['id']}", help="Guardar cambio"):
                        try:
                            api("PATCH", f"/orders/{order['id']}", json={"status": new_status})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            st.markdown("<hr style='margin:4px 0;border-color:#F1F5F9'>", unsafe_allow_html=True)

# ── CONVERSACIONES ────────────────────────────────────────────────────────────
with tab_chat:
    col_title2, col_r = st.columns([5, 1])
    with col_title2:
        st.markdown("### Conversaciones")
    with col_r:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Actualizar 🔄", use_container_width=True):
            st.rerun()

    if not msgs:
        st.info("Aún no hay conversaciones. Envía un mensaje al bot para empezar.", icon="💬")
    else:
        df = pd.DataFrame(msgs)
        customers = df["customer"].unique().tolist()
        customer_labels = [c.replace("whatsapp:+51", "+51 ").replace("whatsapp:", "") for c in customers]
        label_to_raw = dict(zip(customer_labels, customers))

        selected_label = st.selectbox("Cliente", customer_labels, label_visibility="collapsed")
        selected = label_to_raw[selected_label]
        thread = df[df["customer"] == selected].sort_values("ts")

        # WhatsApp-style chat window
        st.markdown("""
        <div style="background:#128C7E;padding:12px 16px;border-radius:12px 12px 0 0;
                    display:flex;align-items:center;gap:10px">
          <div style="width:36px;height:36px;border-radius:50%;background:#25D366;
                      display:flex;align-items:center;justify-content:center;
                      color:white;font-weight:700;font-size:1rem">C</div>
          <div>
            <div style="color:white;font-weight:600;font-size:0.9rem">Cliente</div>
            <div style="color:#d1fae5;font-size:0.75rem">WhatsApp</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        chat_html = '<div style="background:#ECE5DD;padding:16px;min-height:300px;max-height:480px;overflow-y:auto;border-left:1px solid #ddd;border-right:1px solid #ddd">'
        for _, row in thread.iterrows():
            ts = str(row.get("ts", ""))[:16].replace("T", " ")
            content = str(row["content"]).replace("<", "&lt;").replace(">", "&gt;")
            role = row["role"]

            if role == "user":
                chat_html += f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:8px">
                  <div style="background:#DCF8C6;border-radius:12px 12px 2px 12px;
                              padding:8px 12px;max-width:70%;box-shadow:0 1px 2px rgba(0,0,0,0.1)">
                    <div style="font-size:0.875rem;color:#1a1a1a">{content}</div>
                    <div style="font-size:0.68rem;color:#667781;text-align:right;margin-top:2px">{ts} ✓✓</div>
                  </div>
                </div>"""
            elif role == "assistant":
                chat_html += f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:8px">
                  <div style="background:white;border-radius:12px 12px 12px 2px;
                              padding:8px 12px;max-width:70%;box-shadow:0 1px 2px rgba(0,0,0,0.1)">
                    <div style="font-size:0.68rem;color:#25D366;font-weight:600;margin-bottom:2px">🤖 RespondIA</div>
                    <div style="font-size:0.875rem;color:#1a1a1a">{content}</div>
                    <div style="font-size:0.68rem;color:#667781;text-align:right;margin-top:2px">{ts}</div>
                  </div>
                </div>"""
            else:  # owner
                chat_html += f"""
                <div style="display:flex;justify-content:flex-start;margin-bottom:8px">
                  <div style="background:#FFF9C4;border-radius:12px 12px 12px 2px;
                              padding:8px 12px;max-width:70%;box-shadow:0 1px 2px rgba(0,0,0,0.1);
                              border-left:3px solid #F59E0B">
                    <div style="font-size:0.68rem;color:#D97706;font-weight:600;margin-bottom:2px">👤 Tú</div>
                    <div style="font-size:0.875rem;color:#1a1a1a">{content}</div>
                    <div style="font-size:0.68rem;color:#667781;text-align:right;margin-top:2px">{ts}</div>
                  </div>
                </div>"""
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Owner reply box
        st.markdown("""
        <div style="background:#F0F0F0;padding:8px 12px;border-radius:0 0 12px 12px;
                    border:1px solid #ddd;border-top:none;font-size:0.75rem;color:#667781">
            Escribe un mensaje para intervenir en la conversación como dueño del negocio
        </div>""", unsafe_allow_html=True)

        col_msg, col_send = st.columns([5, 1])
        with col_msg:
            owner_text = st.text_input("mensaje", placeholder="Escribe tu respuesta...",
                                        label_visibility="collapsed", key="owner_msg")
        with col_send:
            if st.button("Enviar →", type="primary", use_container_width=True):
                if owner_text.strip():
                    try:
                        api("POST", "/conversations/send",
                            json={"customer": selected, "text": owner_text})
                        st.success("Mensaje enviado")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
