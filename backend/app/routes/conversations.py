import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from ..auth import require_tenant
from ..database import Tenant, get_all_messages, save_owner_message

router = APIRouter(prefix="/conversations")

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN", "")
SANDBOX_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")


@router.get("/")
def list_conversations(tenant: Tenant = Depends(require_tenant)):
    return get_all_messages(tenant.id)


class OwnerMessage(BaseModel):
    customer: str   # whatsapp:+51xxxxxxxxx
    text: str


@router.post("/send")
def owner_send(body: OwnerMessage, tenant: Tenant = Depends(require_tenant)):
    if not body.text.strip():
        raise HTTPException(400, "El mensaje no puede estar vacío")
    try:
        twilio = Client(ACCOUNT_SID, AUTH_TOKEN)
        from_number = (
            tenant.phone_number
            if tenant.phone_number.startswith("whatsapp:")
            else SANDBOX_NUMBER
        )
        # Sandbox tenants use the shared sandbox number
        if tenant.phone_number.startswith("sandbox:"):
            from_number = SANDBOX_NUMBER
        twilio.messages.create(
            from_=from_number,
            to=body.customer,
            body=body.text,
        )
    except Exception as e:
        raise HTTPException(502, f"Error al enviar mensaje: {e}")

    save_owner_message(tenant.id, body.customer, body.text)
    return {"status": "sent"}
