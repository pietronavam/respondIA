import os
import uuid
import resend
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from ..database import create_tenant, save_setting

router = APIRouter()

resend.api_key = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
PANEL_URL = "https://respond-ia.streamlit.app/"


class RegisterForm(BaseModel):
    name: str
    email: EmailStr


def _send_welcome_email(to_email: str, business_name: str, api_key: str):
    resend.Emails.send({
        "from": f"RespondIA <{FROM_EMAIL}>",
        "to": [to_email],
        "subject": f"Tu acceso a RespondIA — {business_name}",
        "html": f"""
        <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:32px;color:#1e293b">
          <h1 style="color:#312E81;margin-bottom:4px">⚡ RespondIA</h1>
          <p style="color:#64748b;margin-top:0">Tu agente de IA para WhatsApp</p>
          <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0"/>

          <p>Hola, <strong>{business_name}</strong>.</p>
          <p>Tu cuenta está lista. Usa este código para acceder a tu panel de control:</p>

          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;
                      padding:20px;text-align:center;margin:24px 0">
            <p style="font-size:12px;color:#64748b;text-transform:uppercase;
                      letter-spacing:0.08em;margin:0 0 8px">Código de acceso</p>
            <p style="font-family:monospace;font-size:18px;font-weight:700;
                      color:#312E81;word-break:break-all;margin:0">{api_key}</p>
          </div>

          <a href="{PANEL_URL}" style="display:inline-block;background:#25D366;color:white;
             font-weight:700;padding:14px 28px;border-radius:10px;text-decoration:none;
             font-size:16px">Ir a mi panel →</a>

          <p style="margin-top:24px;font-size:13px;color:#94a3b8">
            Guarda este código en un lugar seguro. Si lo pierdes, contáctanos.<br/>
            — El equipo de RespondIA 🇵🇪
          </p>
        </div>
        """,
    })


@router.post("/register")
def register(data: RegisterForm):
    name = data.name.strip()
    if not name:
        raise HTTPException(400, "El nombre del negocio es requerido")
    if not resend.api_key:
        raise HTTPException(503, "Servicio de email no configurado")

    placeholder = f"sandbox:{uuid.uuid4()}"
    tenant = create_tenant(name=name, phone_number=placeholder)
    save_setting(tenant.id, "business_name", name)

    email_sent = False
    try:
        _send_welcome_email(data.email, name, tenant.api_key)
        email_sent = True
    except Exception:
        pass  # Email failed, return key directly as fallback

    if email_sent:
        return {"status": "email_sent", "email": data.email}
    else:
        return {"status": "show_key", "api_key": tenant.api_key, "email": data.email}
