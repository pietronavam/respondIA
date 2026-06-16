import os
from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from ..services.claude_service import get_bot_response
from ..services.whisper_service import transcribe_audio_url
from ..database import save_message

router = APIRouter()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(default=""),
    From: str = Form(...),
    NumMedia: int = Form(default=0),
    MediaUrl0: str = Form(default=None),
    MediaContentType0: str = Form(default=None),
):
    customer_id = From

    # Transcribe audio if the message is a voice note
    if NumMedia > 0 and MediaContentType0 and "audio" in MediaContentType0 and MediaUrl0:
        try:
            transcribed = await transcribe_audio_url(MediaUrl0, ACCOUNT_SID, AUTH_TOKEN)
            user_message = f"[Nota de voz]: {transcribed}"
        except Exception as e:
            user_message = Body or "[Audio no procesable]"
    else:
        user_message = Body.strip() if Body.strip() else "[Mensaje vacío]"

    bot_reply = await get_bot_response(user_message, customer_id)
    save_message(customer_id, user_message, bot_reply)

    resp = MessagingResponse()
    resp.message(bot_reply)
    return Response(content=str(resp), media_type="application/xml")
