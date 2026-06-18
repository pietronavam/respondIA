import os
from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from ..services.claude_service import get_bot_response
from ..services.whisper_service import transcribe_audio_url
from ..database import save_message, get_tenant_by_phone, create_order, get_pending_order, mark_order_paid, get_setting
from ..services.vision_service import verify_payment_screenshot

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
        return Response(content=str(MessagingResponse()), media_type="application/xml")

    is_image = NumMedia > 0 and MediaContentType0 and "image" in MediaContentType0

    if NumMedia > 0 and MediaContentType0 and "audio" in MediaContentType0 and MediaUrl0:
        try:
            transcribed = await transcribe_audio_url(MediaUrl0, ACCOUNT_SID, AUTH_TOKEN)
            user_message = f"[Nota de voz]: {transcribed}"
        except Exception:
            user_message = Body or "[Audio no procesable]"
    else:
        user_message = Body.strip() if Body.strip() else "[Mensaje vacío]"

    # Image received → verify if it's a valid payment screenshot
    if is_image and MediaUrl0:
        pending = get_pending_order(tenant.id, From)
        if pending:
            yape   = get_setting(tenant.id, "yape_number") or ""
            plin   = get_setting(tenant.id, "plin_number") or ""
            verified, reason = await verify_payment_screenshot(
                image_url=MediaUrl0,
                twilio_sid=ACCOUNT_SID,
                twilio_token=AUTH_TOKEN,
                expected_total=pending.total,
                yape_number=yape,
                plin_number=plin,
            )
            if verified:
                mark_order_paid(pending.id)
                bot_reply = (
                    f"¡Pago verificado! ✅ Tu pedido {pending.code} está confirmado. "
                    f"Te avisamos cuando esté listo para envío. 🙌"
                )
            else:
                bot_reply = (
                    f"No pude verificar el pago 🤔 {reason}. "
                    f"Por favor envía la captura completa de Yape/Plin "
                    f"mostrando el monto de S/{pending.total}."
                )
            save_message(tenant.id, From, "[Imagen]", bot_reply)
            resp = MessagingResponse()
            resp.message(bot_reply)
            return Response(content=str(resp), media_type="application/xml")

    bot_reply, order_data = await get_bot_response(
        user_message, customer_id=From, tenant_id=tenant.id
    )

    if order_data:
        try:
            total = int(float(str(order_data.get("total", 0))))
            items = str(order_data.get("items", "Pedido"))
            order = create_order(
                tenant_id=tenant.id,
                customer=From,
                items=items,
                total=total,
            )
            # Append order code to the bot reply so the customer sees it
            bot_reply = f"{bot_reply}\n\nTu código de pedido: {order.code} 📦"
        except Exception:
            pass

    save_message(tenant.id, From, user_message, bot_reply)

    resp = MessagingResponse()
    resp.message(bot_reply)
    return Response(content=str(resp), media_type="application/xml")
