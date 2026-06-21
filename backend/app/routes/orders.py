import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth import require_tenant
from ..database import (
    Tenant, get_orders, update_order_status, get_order_by_id,
    get_interests, delete_interest, mark_followed_up,
    get_setting, get_history,
)

router = APIRouter(prefix="/orders")

STATUS_OPTIONS = {"pendiente", "pagado", "enviado", "entregado"}


@router.get("/")
def list_orders(tenant: Tenant = Depends(require_tenant)):
    orders = get_orders(tenant.id)
    return [
        {
            "id": o.id,
            "code": o.code,
            "customer": o.customer,
            "items": o.items,
            "total": o.total,
            "status": o.status,
            "created_at": str(o.created_at),
        }
        for o in orders
    ]


@router.get("/interests")
def list_interests(tenant: Tenant = Depends(require_tenant)):
    return [
        {
            "customer":       i.customer,
            "last_product":   i.last_product or "",
            "created_at":     str(i.created_at),
            "followed_up_at": str(i.followed_up_at) if i.followed_up_at else None,
        }
        for i in get_interests(tenant.id)
    ]


@router.delete("/interests/{customer:path}")
def remove_interest(customer: str, tenant: Tenant = Depends(require_tenant)):
    delete_interest(tenant.id, customer)
    return {"status": "removed"}


@router.post("/interests/followup")
async def send_interest_followup(customer: str, tenant: Tenant = Depends(require_tenant)):
    from ..services.followup_service import generate_followup_message, send_followup, SANDBOX_FROM

    try:
        interests = get_interests(tenant.id)
        interest = next((i for i in interests if i.customer == customer), None)
        if not interest:
            return {"status": "error", "message": "", "detail": "Interés no encontrado"}

        raw = interest.last_product or ""
        try:
            d = json.loads(raw)
            product = d.get("product", "") or "producto"
            talla   = d.get("talla", "")
            color   = d.get("color", "")
        except Exception:
            product, talla, color = raw or "producto", "", ""

        days_since    = (datetime.utcnow() - interest.updated_at).days if interest.updated_at else 0
        business_name = get_setting(tenant.id, "business_name") or "la tienda"
        catalog       = get_setting(tenant.id, "catalog") or ""

        message = await asyncio.to_thread(
            generate_followup_message,
            business_name=business_name,
            product=product,
            talla=talla,
            color=color,
            days_since=days_since,
            catalog_snippet=catalog,
        )

        phone   = tenant.phone_number or ""
        from_wa = phone if (phone.startswith("whatsapp:") and "sandbox" not in phone) else SANDBOX_FROM
        sent    = await asyncio.to_thread(send_followup, customer, message, from_wa)

        if sent:
            mark_followed_up(tenant.id, customer)

        return {"status": "sent" if sent else "error", "message": message}

    except Exception as e:
        print(f"[FOLLOWUP ERROR] {e}")
        return {"status": "error", "message": "", "detail": str(e)}


class StatusUpdate(BaseModel):
    status: str


def _detect_shipping_zone(tenant_id: str, customer: str) -> tuple[str, str]:
    """
    Returns (zone_name, delivery_time) by checking conversation history for
    keywords matching the configured shipping zones (JSON list).
    Falls back to first zone (or Lima Metropolitana) if no match.
    """
    import json as _json, unicodedata, re

    raw = get_setting(tenant_id, "shipping_zones", "")
    try:
        zones = _json.loads(raw) if raw else []
    except Exception:
        zones = []
    if not zones:
        zones = [
            {"name": "Lima Metropolitana", "time": "1 a 2 días hábiles"},
            {"name": "Provincias",         "time": "3 a 5 días hábiles"},
        ]

    history   = get_history(tenant_id, customer, limit=20)
    full_text = " ".join(m["content"] for m in history)

    def normalize(t: str) -> str:
        return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()

    norm_text = normalize(full_text)
    # Check zones from last to first — more specific zones (provinces) should come after Lima
    for zone in reversed(zones[1:]):
        keywords = {w for w in re.findall(r'[a-z]+', normalize(zone["name"])) if len(w) >= 4}
        if any(kw in norm_text for kw in keywords):
            return zone["name"], zone.get("time", "")
    return zones[0]["name"], zones[0].get("time", "")


@router.patch("/{order_id}")
async def patch_order(order_id: int, body: StatusUpdate, tenant: Tenant = Depends(require_tenant)):
    if body.status not in STATUS_OPTIONS:
        raise HTTPException(400, f"Estado inválido. Opciones: {STATUS_OPTIONS}")

    order = get_order_by_id(order_id, tenant.id)
    if not order:
        raise HTTPException(404, "Pedido no encontrado")

    ok = update_order_status(order_id, tenant.id, body.status)
    if not ok:
        raise HTTPException(404, "Pedido no encontrado")

    # Notify customer via WhatsApp
    if body.status in ("enviado", "entregado"):
        try:
            from ..services.followup_service import send_followup, SANDBOX_FROM
            phone = tenant.phone_number or ""
            from_wa = phone if (phone.startswith("whatsapp:") and "sandbox" not in phone) else SANDBOX_FROM
            business_name = get_setting(tenant.id, "business_name") or tenant.name

            if body.status == "enviado":
                zone_name, delivery_time = await asyncio.to_thread(
                    _detect_shipping_zone, tenant.id, order.customer
                )
                message = (
                    f"🚚 ¡Tu pedido *{order.code}* está en camino!\n"
                    f"Zona de entrega: *{zone_name}*\n"
                    f"Tiempo estimado: *{delivery_time}*\n\n"
                    f"Cualquier consulta por aquí. ¡Gracias por tu compra! 🙌"
                )
            else:  # entregado
                message = (
                    f"✅ ¡Tu pedido *{order.code}* ha sido entregado!\n"
                    f"Esperamos que lo disfrutes mucho 😊\n"
                    f"Si tienes alguna consulta, escríbenos. — *{business_name}*"
                )

            print(f"[ORDER NOTIFY] Sending '{body.status}' notification to {order.customer}")
            sent = await asyncio.to_thread(send_followup, order.customer, message, from_wa)
            print(f"[ORDER NOTIFY] Result: {'sent' if sent else 'FAILED'} — {order.code}")
        except Exception as e:
            print(f"[ORDER NOTIFY ERROR] {body.status} / {order_id}: {e}")

    return {"status": "updated"}
