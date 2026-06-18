import os
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from twilio.rest import Client
from ..database import create_tenant, list_tenants

router = APIRouter(prefix="/tenants")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "https://respondia.onrender.com")
ADMIN_KEY = os.getenv("ADMIN_KEY", "")


def _check_admin(x_admin_key: str):
    if not ADMIN_KEY or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")


class TenantCreate(BaseModel):
    name: str
    phone_number: str | None = None  # si ya tiene un número en Twilio (e.g. "+51999xxxxxx")
    country_code: str = "US"         # para compra automática si phone_number es None


@router.post("/")
def create_new_tenant(data: TenantCreate, x_admin_key: str = Header(...)):
    _check_admin(x_admin_key)

    twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    webhook_url = f"{WEBHOOK_BASE_URL}/webhook/whatsapp"

    if data.phone_number:
        # Número ya existente — solo configura el webhook
        raw = data.phone_number.replace("whatsapp:", "")
        numbers = twilio.incoming_phone_numbers.list(phone_number=raw, limit=1)
        if not numbers:
            raise HTTPException(400, f"Número {raw} no encontrado en tu cuenta Twilio")
        numbers[0].update(sms_url=webhook_url, sms_method="POST")
        assigned_number = f"whatsapp:{raw}"
    else:
        # Compra un número nuevo
        available = twilio.available_phone_numbers(data.country_code).local.list(
            sms_enabled=True, limit=1
        )
        if not available:
            raise HTTPException(503, f"No hay números disponibles en {data.country_code}")
        purchased = twilio.incoming_phone_numbers.create(
            phone_number=available[0].phone_number,
            sms_url=webhook_url,
            sms_method="POST",
        )
        assigned_number = f"whatsapp:{purchased.phone_number}"

    tenant = create_tenant(name=data.name, phone_number=assigned_number)

    return {
        "tenant_id": tenant.id,
        "api_key": tenant.api_key,
        "phone_number": assigned_number,
        "note": "Activa WhatsApp Business para este número desde Twilio Console → Messaging → Senders.",
    }


@router.get("/")
def get_all_tenants(x_admin_key: str = Header(...)):
    _check_admin(x_admin_key)
    tenants = list_tenants()
    return [
        {
            "id": t.id,
            "name": t.name,
            "phone_number": t.phone_number,
            "plan": t.plan,
            "is_active": t.is_active,
            "created_at": str(t.created_at),
        }
        for t in tenants
    ]
