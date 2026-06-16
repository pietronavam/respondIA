import os
from openai import OpenAI
from ..database import get_history, get_business_setting

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM_TEMPLATE = """Eres el asistente virtual de {business_name}, atendiendo clientes por WhatsApp.
Responde de forma amigable, breve y directa (máximo 3-4 líneas por mensaje).

CATÁLOGO Y SERVICIOS DEL NEGOCIO:
{catalog}

HORARIO DE ATENCIÓN:
{hours}

REGLAS:
- Responde siempre en español peruano natural
- Si un producto no está en el catálogo, dilo honestamente
- Para pedidos, confirma: producto, cantidad y datos de entrega
- Si no puedes resolver algo, ofrece escalar con el dueño
- Usa emojis con moderación (1-2 por mensaje máximo)
"""


async def get_bot_response(user_message: str, customer_id: str) -> str:
    catalog = get_business_setting("catalog", "Sin catálogo cargado aún.")
    business_name = get_business_setting("business_name", os.getenv("BUSINESS_NAME", "el negocio"))
    hours = get_business_setting("hours", "Lunes a sábado 9am-7pm")

    system = SYSTEM_TEMPLATE.format(
        business_name=business_name,
        catalog=catalog,
        hours=hours,
    )

    history = get_history(customer_id, limit=8)
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": user_message}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=300,
    )

    return response.choices[0].message.content
