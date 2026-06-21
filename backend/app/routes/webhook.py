import os
from fastapi import APIRouter, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from ..services.claude_service import get_bot_response
from ..services.whisper_service import transcribe_audio_url
from ..database import (
    save_message, get_tenant_by_phone, get_tenant_by_slug, get_tenant_by_id,
    get_customer_session, upsert_customer_session,
    create_order, get_pending_order, mark_order_paid, get_setting,
)
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
    # Routing tier 1: real WhatsApp number (production path)
    tenant = get_tenant_by_phone(To)

    # Routing tier 2: sandbox — keyword takes priority (allows switching tenants)
    if not tenant:
        keyword = Body.strip().upper()
        kw_tenant = get_tenant_by_slug(keyword) if keyword else None
        if kw_tenant:
            upsert_customer_session(From, kw_tenant.id)
            biz_name = get_setting(kw_tenant.id, "business_name") or kw_tenant.name
            hours = get_setting(kw_tenant.id, "hours") or ""
            welcome = (
                f"¡Hola! Soy el asistente virtual de *{biz_name}*. 😊\n"
                f"¿En qué te puedo ayudar hoy?"
            )
            if hours:
                welcome += f"\n\n🕐 Atendemos: {hours}"
            save_message(kw_tenant.id, From, keyword, welcome)
            resp = MessagingResponse()
            resp.message(welcome)
            return Response(content=str(resp), media_type="application/xml")

    # Routing tier 3: sandbox — resume existing session
    if not tenant:
        session = get_customer_session(From)
        if session:
            tenant = get_tenant_by_id(session.tenant_id)

    if not tenant:
        resp = MessagingResponse()
        resp.message(
            "Hola 👋 Para chatear con un negocio, envía su *código único*.\n"
            "El negocio debe compartirte ese código."
        )
        return Response(content=str(resp), media_type="application/xml")

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
                    f"¡Pago verificado! ✅ Tu pedido *{pending.code}* está confirmado. "
                    f"Te avisamos cuando esté listo para envío. 🙌"
                )
                # Notify owner via WhatsApp
                owner_wa = get_setting(tenant.id, "owner_whatsapp") or ""
                if owner_wa:
                    try:
                        from twilio.rest import Client as TwilioClient
                        twilio = TwilioClient(ACCOUNT_SID, AUTH_TOKEN)
                        customer_short = From.replace("whatsapp:", "")
                        twilio.messages.create(
                            body=(
                                f"💰 *Pago recibido* — {pending.code}\n"
                                f"Cliente: {customer_short}\n"
                                f"Productos: {pending.items}\n"
                                f"Total: S/{pending.total}\n\n"
                                f"Pendiente de envío 🚚"
                            ),
                            from_=os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"),
                            to=f"whatsapp:{owner_wa}",
                        )
                    except Exception as e:
                        print(f"[OWNER NOTIFY ERROR] {e}")
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

    if not order_data:
        import re as _re
        price_matches = _re.findall(r'S/(\d+)', bot_reply)
        has_payment = any(kw in bot_reply.lower() for kw in ["yape", "plin", "paga", "comprobante"])
        has_confirm = any(kw in bot_reply.lower() for kw in ["pedido", "confirm", "procesar"])
        if price_matches and has_payment and has_confirm and not get_pending_order(tenant.id, From):
            total_val = max(int(p) for p in price_matches)
            order_data = {"items": "Pedido", "total": total_val}

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
            bot_reply = f"{bot_reply}\n\n📦 Código de pedido: *{order.code}*"
        except Exception as e:
            import traceback
            print(f"[ORDER ERROR] {e}\n{traceback.format_exc()}")

    save_message(tenant.id, From, user_message, bot_reply)

    resp = MessagingResponse()
    resp.message(bot_reply)
    return Response(content=str(resp), media_type="application/xml")
