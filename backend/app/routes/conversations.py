from fastapi import APIRouter
from ..database import get_all_messages

router = APIRouter(prefix="/conversations")


@router.get("/")
def list_conversations():
    rows = get_all_messages()
    return [
        {"customer": r[0], "role": r[1], "content": r[2], "ts": r[3]}
        for r in rows
    ]
