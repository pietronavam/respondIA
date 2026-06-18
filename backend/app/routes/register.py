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
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
</style>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Inter',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 16px;">
  <tr><td align="center">
    <table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.5);">

      <!-- HEADER -->
      <tr>
        <td style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0d3320 100%);padding:44px 40px 36px;text-align:center;">
          <div style="margin-bottom:12px;">
            <span style="font-size:32px;font-weight:800;letter-spacing:-1px;color:#ffffff;font-family:'Inter',Arial,sans-serif;">Respond</span><span style="font-size:32px;font-weight:800;letter-spacing:-1px;color:#25D366;font-family:'Inter',Arial,sans-serif;">IA</span>
          </div>
          <p style="margin:0;color:#64748b;font-size:13px;letter-spacing:1px;text-transform:uppercase;font-weight:600;">Tu agente de IA para WhatsApp</p>
        </td>
      </tr>

      <!-- GREEN BAND -->
      <tr>
        <td style="background:#25D366;padding:14px 40px;text-align:center;">
          <p style="margin:0;color:#0f172a;font-size:14px;font-weight:700;letter-spacing:0.3px;">🎉 ¡Bienvenido/a a bordo, {business_name}!</p>
        </td>
      </tr>

      <!-- BODY -->
      <tr>
        <td style="background:#1e293b;padding:40px 40px 36px;">
          <p style="margin:0 0 12px;font-size:24px;font-weight:700;color:#f8fafc;font-family:'Inter',Arial,sans-serif;">Tu cuenta está lista ✅</p>
          <p style="margin:0 0 32px;font-size:15px;color:#94a3b8;line-height:1.7;">A partir de ahora tu negocio puede atender clientes por WhatsApp las <strong style="color:#f8fafc;">24 horas</strong>, sin que tengas que estar pendiente.</p>

          <!-- FEATURES -->
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:36px;">
            <tr><td style="padding-bottom:12px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:12px;padding:16px 20px;border-left:3px solid #25D366;">
                <tr><td>
                  <p style="margin:0 0 2px;font-size:14px;font-weight:600;color:#f1f5f9;">💬 Bot responde automáticamente</p>
                  <p style="margin:0;font-size:13px;color:#64748b;">Precios, stock y pedidos sin que hagas nada.</p>
                </td></tr>
              </table>
            </td></tr>
            <tr><td style="padding-bottom:12px;">
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:12px;padding:16px 20px;border-left:3px solid #25D366;">
                <tr><td>
                  <p style="margin:0 0 2px;font-size:14px;font-weight:600;color:#f1f5f9;">📦 Gestión de pedidos en tiempo real</p>
                  <p style="margin:0;font-size:13px;color:#64748b;">Registra y sigue cada venta desde tu panel.</p>
                </td></tr>
              </table>
            </td></tr>
            <tr><td>
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:12px;padding:16px 20px;border-left:3px solid #25D366;">
                <tr><td>
                  <p style="margin:0 0 2px;font-size:14px;font-weight:600;color:#f1f5f9;">💳 Cobra por Yape, Plin o Culqi</p>
                  <p style="margin:0;font-size:13px;color:#64748b;">Configura tus métodos de pago en minutos.</p>
                </td></tr>
              </table>
            </td></tr>
          </table>

          <!-- CTA -->
          <table width="100%" cellpadding="0" cellspacing="0">
            <tr><td align="center">
              <a href="{PANEL_URL}" style="display:inline-block;background:#25D366;color:#0f172a;font-weight:800;font-size:16px;padding:18px 48px;border-radius:14px;text-decoration:none;letter-spacing:0.3px;font-family:'Inter',Arial,sans-serif;">
                Ir a mi panel →
              </a>
            </td></tr>
          </table>
          <p style="margin:16px 0 0;text-align:center;font-size:13px;color:#475569;">Ingresa con tu correo y la contraseña que elegiste.</p>
        </td>
      </tr>

      <!-- FOOTER -->
      <tr>
        <td style="background:#0a0f1a;padding:24px 40px;text-align:center;border-top:1px solid #1e293b;">
          <p style="margin:0 0 4px;font-size:12px;color:#334155;font-weight:600;">© 2026 RespondIA — Hecho en Perú 🇵🇪</p>
          <p style="margin:0;font-size:11px;color:#1e293b;">Recibiste este correo porque te registraste en respondia.pe</p>
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
