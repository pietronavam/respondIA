import os
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..database import create_tenant, save_setting, get_tenant_by_email
from ..auth import hash_password

router = APIRouter()

GMAIL_USER     = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
PANEL_URL      = "https://respond-ia.streamlit.app/"


def _send_welcome_email(to_email: str, business_name: str):
    if not GMAIL_USER or not GMAIL_PASSWORD:
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Bienvenido a RespondIA — {business_name}"
    msg["From"]    = f"RespondIA <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:32px;color:#1e293b">
      <h1 style="color:#312E81;margin-bottom:4px">⚡ RespondIA</h1>
      <p style="color:#64748b;margin-top:0">Tu agente de IA para WhatsApp</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0"/>
      <p>Hola, <strong>{business_name}</strong>. Tu cuenta está lista.</p>
      <p>Ingresa con tu correo y contraseña en el panel:</p>
      <a href="{PANEL_URL}" style="display:inline-block;background:#25D366;color:white;
         font-weight:700;padding:14px 28px;border-radius:10px;text-decoration:none;font-size:16px">
        Ir a mi panel →
      </a>
      <p style="margin-top:24px;font-size:13px;color:#94a3b8">— El equipo de RespondIA 🇵🇪</p>
    </div>
    """, "html"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_USER, GMAIL_PASSWORD)
            s.sendmail(GMAIL_USER, to_email, msg.as_string())
        return True
    except Exception:
        return False


class RegisterForm(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/register")
def register(data: RegisterForm):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "El nombre del negocio es requerido")
    if len(data.password) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")
    if get_tenant_by_email(data.email):
        raise HTTPException(409, "Ya existe una cuenta con ese correo")

    hashed = hash_password(data.password)
    placeholder = f"sandbox:{uuid.uuid4()}"
    tenant = create_tenant(
        name=name,
        phone_number=placeholder,
        email=data.email,
        hashed_password=hashed,
    )
    save_setting(tenant.id, "business_name", name)
    _send_welcome_email(data.email, name)

    return {"status": "ok"}
