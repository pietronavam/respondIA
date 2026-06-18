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
    html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 16px;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.10);">

      <!-- HEADER -->
      <tr>
        <td style="background:#0f172a;padding:36px 40px 28px;text-align:center;">
          <div style="display:inline-block;margin-bottom:16px;">
            <span style="font-size:28px;font-weight:800;letter-spacing:-0.5px;color:#ffffff;">Respond</span><span style="font-size:28px;font-weight:800;letter-spacing:-0.5px;color:#6366f1;">IA</span>
          </div>
          <p style="margin:0;color:#94a3b8;font-size:14px;letter-spacing:0.3px;">Tu agente de IA para WhatsApp</p>
        </td>
      </tr>

      <!-- HERO BAND -->
      <tr>
        <td style="background:#6366f1;padding:18px 40px;text-align:center;">
          <p style="margin:0;color:#ffffff;font-size:15px;font-weight:600;letter-spacing:0.2px;">🎉 ¡Bienvenido/a a bordo!</p>
        </td>
      </tr>

      <!-- BODY -->
      <tr>
        <td style="background:#ffffff;padding:40px 40px 32px;">
          <p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#0f172a;">Hola, <span style="color:#6366f1;">{business_name}</span></p>
          <p style="margin:0 0 28px;font-size:15px;color:#475569;line-height:1.6;">Tu cuenta en RespondIA está lista. A partir de ahora tu negocio puede atender clientes por WhatsApp las 24 horas, sin que tengas que estar pendiente.</p>

          <!-- FEATURES -->
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
            <tr>
              <td style="background:#f8fafc;border-radius:12px;padding:20px 24px;border-left:4px solid #6366f1;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="padding-bottom:14px;">
                      <span style="font-size:18px;">💬</span>
                      <span style="font-size:14px;font-weight:600;color:#1e293b;margin-left:8px;">Bot responde automáticamente</span>
                      <p style="margin:4px 0 0 26px;font-size:13px;color:#64748b;">Precios, disponibilidad y pedidos sin que hagas nada.</p>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-bottom:14px;">
                      <span style="font-size:18px;">📦</span>
                      <span style="font-size:14px;font-weight:600;color:#1e293b;margin-left:8px;">Gestión de pedidos</span>
                      <p style="margin:4px 0 0 26px;font-size:13px;color:#64748b;">Registra y sigue cada venta desde tu panel.</p>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <span style="font-size:18px;">💳</span>
                      <span style="font-size:14px;font-weight:600;color:#1e293b;margin-left:8px;">Cobra por Yape, Plin o Culqi</span>
                      <p style="margin:4px 0 0 26px;font-size:13px;color:#64748b;">Configura tus métodos de pago en minutos.</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>

          <!-- CTA -->
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td align="center">
                <a href="{PANEL_URL}" style="display:inline-block;background:#6366f1;color:#ffffff;font-weight:700;font-size:16px;padding:16px 40px;border-radius:12px;text-decoration:none;letter-spacing:0.2px;">
                  Ir a mi panel →
                </a>
              </td>
            </tr>
          </table>
          <p style="margin:20px 0 0;text-align:center;font-size:13px;color:#94a3b8;">Ingresa con tu correo y la contraseña que elegiste.</p>
        </td>
      </tr>

      <!-- FOOTER -->
      <tr>
        <td style="background:#0f172a;padding:24px 40px;text-align:center;">
          <p style="margin:0 0 6px;font-size:13px;color:#475569;">© 2026 RespondIA — Hecho en Perú 🇵🇪</p>
          <p style="margin:0;font-size:12px;color:#334155;">Recibiste este correo porque te registraste en respondia.pe</p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""
    msg.attach(MIMEText(html, "html"))
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
