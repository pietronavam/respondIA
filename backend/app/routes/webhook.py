import os
import re as _re
import asyncio
import traceback
from datetime import datetime, timezone

from fastapi import APIRouter, Form, Response, BackgroundTasks
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient

from ..services.claude_service import get_bot_response
from ..services.whisper_service import transcribe_audio_url
from ..database import (
    save_message, get_tenant_by_phone, get_tenant_by_slug, get_tenant_by_id,
    get_customer_session, upsert_customer_session,
    create_order, get_pending_order, mark_order_paid, get_setting,
    append_to_buffer, get_and_clear_buffer,
    upsert_interest, delete_interest,
)
from ..services.vision_service import verify_payment_screenshot

router = APIRouter()

ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN", "")
SANDBOX_FROM  = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
DEBOUNCE_SECS = 7.0
_INTEREST_PRICE   = _re.compile(r'S/\d+')
_INTEREST_PRODUCT = _re.compile(r'polo|jean|blusa|vestido|talla|color|disponible|precio|stock|conjunto|short', _re.I)
_TALLA_RE  = _re.compile(r'talla\s+(XS|S|M|L|XL|XXL|[0-9]+)|(?<!\w)(XS|S|M|L|XL|XXL)(?!\w)', _re.I)
_COLOR_RE  = _re.compile(
    r'\b(negro|negra|blanco|blanca|rojo|roja|azul|verde oliva|verde|amarillo|amarilla|'
    r'rosado|rosada|gris|morado|morada|beige|crema|naranja|celeste|marino|oliva|nude)\b', _re.I)


def _extract_interest(bot_reply: str) -> str:
    import json
    line = bot_reply.split('\n')[0]
    # Talla and color from the full line (most reliable source)
    tm = _TALLA_RE.search(line)
    talla = (tm.group(1) or tm.group(2)).upper() if tm else ""
    cm = _COLOR_RE.search(line)
    color = cm.group(1).capitalize() if cm else ""
    # Product: prefer bold text (*Polo básico*), then fallback to keyword search
    bold = _re.search(r'\*([^*]+)\*', line)
    if bold:
        product = bold.group(1).strip()
        # If bold is just a descriptor ("wide leg"), prepend the product type found before it
        type_before = _re.search(
            r'\b(jean|polo|blusa|vestido|conjunto|short|falda)\w*\b',
            line[:bold.start()], _re.I
        )
        if type_before and type_before.group(0).lower() not in product.lower():
            product = f"{type_before.group(0).title()} {product}"
    else:
        m = _re.search(r'(jean\s+\w+\s*\w*|polo\s+\w+\s*\w*|blusa\s*\w*|vestido\s*\w*|conjunto\s*\w*|short|falda)\b', line, _re.I)
        product = m.group(0).strip().title() if m else ""
    # Strip talla/color suffixes from product name
    product = _re.sub(r'\s+talla\s+\S+', '', product, flags=_re.I).strip()
    product = _re.sub(r'\s+color\s+\S+', '', product, flags=_re.I).strip()
    product = _re.sub(r'\s+(XS|S|M|L|XL|XXL)\b', '', product, flags=_re.I).strip()
    return json.dumps({"product": product[:60], "talla": talla, "color": color}, ensure_ascii=False)


def _empty_twiml():
    return Response(content=str(MessagingResponse()), media_type="application/xml")


def _twilio_from(tenant) -> str:
    p = tenant.phone_number or ""
    if p.startswith("whatsapp:") and not p.startswith("whatsapp:sandbox"):
        return p
    return SANDBOX_FROM


async def _send_whatsapp(to: str, body: str, from_: str):
    def _sync():
        TwilioClient(ACCOUNT_SID, AUTH_TOKEN).messages.create(body=body, from_=from_, to=to)
    await asyncio.to_thread(_sync)


async def _process_and_send(customer: str, tenant_id: str, user_message: str):
    """Run bot, handle orders, send reply via Twilio API."""
    try:
        await _do_process_and_send(customer, tenant_id, user_message)
    except Exception as e:
        print(f"[PROCESS ERROR] {customer}: {e}\n{traceback.format_exc()}")


async def _do_process_and_send(customer: str, tenant_id: str, user_message: str):
    tenant = get_tenant_by_id(tenant_id)
    if not tenant:
        return

    bot_reply, order_data = await get_bot_response(
        user_message, customer_id=customer, tenant_id=tenant_id
    )

    if not order_data:
        price_matches = _re.findall(r'S/(\d+)', bot_reply)
        has_payment = any(kw in bot_reply.lower() for kw in ["yape", "plin", "paga", "comprobante"])
        has_confirm = any(kw in bot_reply.lower() for kw in ["pedido", "confirm", "procesar"])
        if price_matches and has_payment and has_confirm and not get_pending_order(tenant_id, customer):
            order_data = {"items": "Pedido", "total": max(int(p) for p in price_matches)}

    if order_data:
        try:
            total = int(float(str(order_data.get("total", 0))))
            items = str(order_data.get("items", "Pedido"))
            order = create_order(tenant_id=tenant_id, customer=customer, items=items, total=total)
            bot_reply = f"{bot_reply}\n\n📦 Código de pedido: *{order.code}*"
            delete_interest(tenant_id, customer)   # moved to pendiente de pago
        except Exception as e:
            print(f"[ORDER ERROR] {e}\n{traceback.format_exc()}")
    elif _INTEREST_PRICE.search(bot_reply) and _INTEREST_PRODUCT.search(bot_reply):
        upsert_interest(tenant_id, customer, _extract_interest(bot_reply))

    try:
        save_message(tenant_id, customer, user_message, bot_reply)
    except Exception as e:
        print(f"[SAVE MSG ERROR] {e}")
    try:
        await _send_whatsapp(customer, bot_reply, _twilio_from(tenant))
    except Exception as e:
        print(f"[TWILIO SEND ERROR] {e}")


async def _debounced(customer: str, tenant_id: str, received_at: datetime):
    """Wait DEBOUNCE_SECS; if no newer message arrived, process the whole buffer."""
    await asyncio.sleep(DEBOUNCE_SECS)
    messages = get_and_clear_buffer(customer, tenant_id, received_at)
    if not messages:
        return  # A newer message arrived — its task will handle it
    combined = "\n".join(messages)
    await _do_process_and_send(customer, tenant_id, combined)


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(default=""),
    From: str = Form(...),
    To: str = Form(...),
    NumMedia: int = Form(default=0),
    MediaUrl0: str = Form(default=None),
    MediaContentType0: str = Form(default=None),
):
    # ── Routing ───────────────────────────────────────────────────────────────

    # Tier 1: real number (production)
    tenant = get_tenant_by_phone(To)

    # Tier 2: sandbox keyword → immediate welcome, no debounce
    if not tenant:
        keyword = Body.strip().upper()
        kw_tenant = get_tenant_by_slug(keyword) if keyword else None
        if kw_tenant:
            upsert_customer_session(From, kw_tenant.id)
            biz_name = get_setting(kw_tenant.id, "business_name") or kw_tenant.name
            hours    = get_setting(kw_tenant.id, "hours") or ""
            welcome  = f"¡Hola! Soy el asistente virtual de *{biz_name}*. 😊\n¿En qué te puedo ayudar hoy?"
            if hours:
                welcome += f"\n\n🕐 Atendemos: {hours}"
            save_message(kw_tenant.id, From, keyword, welcome)
            resp = MessagingResponse()
            resp.message(welcome)
            return Response(content=str(resp), media_type="application/xml")

    # Tier 3: existing session
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

    # ── Images (payment screenshots) — process immediately, no debounce ───────
    is_image = NumMedia > 0 and MediaContentType0 and "image" in MediaContentType0
    if is_image and MediaUrl0:
        pending = get_pending_order(tenant.id, From)
        if pending:
            yape      = get_setting(tenant.id, "yape_number") or ""
            yape_name = get_setting(tenant.id, "yape_name")  or ""
            plin      = get_setting(tenant.id, "plin_number") or ""
            verified, reason = await verify_payment_screenshot(
                image_url=MediaUrl0,
                twilio_sid=ACCOUNT_SID,
                twilio_token=AUTH_TOKEN,
                expected_total=pending.total,
                yape_number=yape,
                yape_name=yape_name,
                plin_number=plin,
            )
            if verified:
                mark_order_paid(pending.id)
                bot_reply = (
                    f"¡Pago verificado! ✅ Tu pedido *{pending.code}* está confirmado. "
                    f"Te avisamos cuando esté listo para envío. 🙌"
                )
                owner_wa = get_setting(tenant.id, "owner_whatsapp") or ""
                if owner_wa:
                    try:
                        customer_short = From.replace("whatsapp:", "")
                        await _send_whatsapp(
                            f"whatsapp:{owner_wa}",
                            (
                                f"💰 *Pago recibido* — {pending.code}\n"
                                f"Cliente: {customer_short}\n"
                                f"Productos: {pending.items}\n"
                                f"Total: S/{pending.total}\n\n"
                                f"Pendiente de envío 🚚"
                            ),
                            SANDBOX_FROM,
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
        # Image but no pending order — fall through to debounced text path
        user_message = "[Imagen]"
    elif NumMedia > 0 and MediaContentType0 and "audio" in MediaContentType0 and MediaUrl0:
        try:
            transcribed = await transcribe_audio_url(MediaUrl0, ACCOUNT_SID, AUTH_TOKEN)
            user_message = f"[Nota de voz]: {transcribed}"
        except Exception:
            user_message = Body or "[Audio no procesable]"
    else:
        user_message = Body.strip() or "[Mensaje vacío]"

    # ── Debounced text/audio path ─────────────────────────────────────────────
    received_at = datetime.utcnow()
    append_to_buffer(From, tenant.id, user_message, received_at)
    background_tasks.add_task(_debounced, From, tenant.id, received_at)
    return _empty_twiml()
