from fastapi import Header, HTTPException
from .database import get_tenant_by_api_key, Tenant


async def require_tenant(x_api_key: str = Header(...)) -> Tenant:
    tenant = get_tenant_by_api_key(x_api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="API key inválida")
    if not tenant.is_active:
        raise HTTPException(status_code=403, detail="Cuenta inactiva")
    return tenant
