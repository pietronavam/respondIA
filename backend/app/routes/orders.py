import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth import require_tenant
from ..database import (
    Tenant, get_orders, update_order_status,
    get_interests, delete_interest, mark_followed_up,
    get_setting,
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

    interests = get_interests(tenant.id)
    interest = next((i for i in interests if i.customer == customer), None)
    if not interest:
        raise HTTPException(404, "Interés no encontrado")

    raw = interest.last_product or ""
    try:
        d = json.loads(raw)
        product = d.get("product", "") or "producto"
        talla   = d.get("talla", "")
        color   = d.get("color", "")
    except Exception:
        product, talla, color = raw or "producto", "", ""

    days_since     = (datetime.utcnow() - interest.updated_at).days if interest.updated_at else 0
    business_name  = get_setting(tenant.id, "business_name") or "la tienda"
    catalog        = get_setting(tenant.id, "catalog") or ""

    message = await asyncio.to_thread(
        generate_followup_message,
        business_name=business_name,
        product=product,
        talla=talla,
        color=color,
        days_since=days_since,
        catalog_snippet=catalog,
    )

    phone = tenant.phone_number or ""
    from_wa = phone if (phone.startswith("whatsapp:") and "sandbox" not in phone) else SANDBOX_FROM
    sent = await asyncio.to_thread(send_followup, customer, message, from_wa)

    if sent:
        mark_followed_up(tenant.id, customer)

    return {"status": "sent" if sent else "error", "message": message}


class StatusUpdate(BaseModel):
    status: str


@router.patch("/{order_id}")
def patch_order(order_id: int, body: StatusUpdate, tenant: Tenant = Depends(require_tenant)):
    if body.status not in STATUS_OPTIONS:
        raise HTTPException(400, f"Estado inválido. Opciones: {STATUS_OPTIONS}")
    ok = update_order_status(order_id, tenant.id, body.status)
    if not ok:
        raise HTTPException(404, "Pedido no encontrado")
    return {"status": "updated"}
