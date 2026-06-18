from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth import require_tenant
from ..database import Tenant, get_orders, update_order_status

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
