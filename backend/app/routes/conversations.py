from fastapi import APIRouter, Depends
from ..auth import require_tenant
from ..database import Tenant, get_all_messages

router = APIRouter(prefix="/conversations")


@router.get("/")
def list_conversations(tenant: Tenant = Depends(require_tenant)):
    return get_all_messages(tenant.id)
