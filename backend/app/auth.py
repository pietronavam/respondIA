import hashlib
import hmac
import secrets

from fastapi import Header, HTTPException
from .database import get_tenant_by_api_key, Tenant


async def require_tenant(x_api_key: str = Header(...)) -> Tenant:
    tenant = get_tenant_by_api_key(x_api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="API key inválida")
    if not tenant.is_active:
        raise HTTPException(status_code=403, detail="Cuenta inactiva")
    return tenant


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000)
    return f"pbkdf2:sha256:260000:{salt}:{key.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    try:
        _, algo, iterations, salt, stored_key = stored.split(":")
        key = hashlib.pbkdf2_hmac(algo, plain.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(key.hex(), stored_key)
    except Exception:
        return False
