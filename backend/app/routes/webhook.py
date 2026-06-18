import os
from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from ..services.claude_service import get_bot_response
from ..services.whisper_service import transcribe_audio_url
from ..database import save_message, get_tenant_by_phone

router = APIRouter()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(default=""),
    From: str = Form(...),
    To: str = Form(...),
    NumMedia: int = Form(default=0),
    MediaUrl0: str = Form(default=None),
    MediaContentType0: str = Form(default=None),
):
    tenant = get_tenant_by_phone(To)
    if not tenant:
        # Número no registrado — respuesta silenciosa para no exponer info
        resp = MessagingResponse()
        return Response(content=str(resp), media_type="application/xml")

    if NumMedia > 0 and MediaContentType0 and "audio" in MediaContentType0 and MediaUrl0:
        try:
            transcribed = await transcribe_audio_url(MediaUrl0, ACCOUNT_SID, AUTH_TOKEN)
            user_message = f"[Nota de voz]: {transcribed}"
        except Exception:
            user_message = Body or "[Audio no procesable]"
    else:
        user_message = Body.strip() if Body.strip() else "[Mensaje vacío]"

    bot_reply = await get_bot_response(user_message, customer_id=From, tenant_id=tenant.id)
    save_message(tenant.id, From, user_message, bot_reply)

    resp = MessagingResponse()
    resp.message(bot_reply)
    return Response(content=str(resp), media_type="application/xml")
