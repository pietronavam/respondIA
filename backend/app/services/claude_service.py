import os
import re
import json
from openai import OpenAI
from ..database import get_history, get_setting

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

PAGOS:
{payment_info}

REGLAS GENERALES:
- Responde siempre en español peruano natural
- Si un producto no está en el catálogo, dilo honestamente
- Usa emojis con moderación (1-2 por mensaje máximo)
- Si no puedes resolver algo, ofrece escalar con el dueño

REGLAS PARA PEDIDOS:
Cuando un cliente quiera comprar uno o más productos:
1. Confirma los productos, cantidades y calcula el total en soles
2. Envía las instrucciones de pago (Yape y/o link de pago si están disponibles)
3. Pide confirmación del pago (foto o captura del comprobante)
4. Al FINAL de tu respuesta agrega esta línea exacta (no la muestres visualmente, va al sistema):
   [PEDIDO:{{"items":"{items_placeholder}","total":{total_placeholder}}}]
   Reemplaza items con descripción del pedido y total con el monto numérico en soles.

Cuando el cliente mande foto de comprobante de pago, responde que ya lo recibiste y que procederás con el envío.
"""

ORDER_RE = re.compile(r'\[PEDIDO:(\{.*?\})\]', re.DOTALL)


async def get_bot_response(
    user_message: str, customer_id: str, tenant_id: str
) -> tuple[str, dict | None]:
    """Returns (visible_reply, order_data | None)"""
    catalog = get_setting(tenant_id, "catalog", "Sin catálogo cargado aún.")
    business_name = get_setting(tenant_id, "business_name", "el negocio")
    hours = get_setting(tenant_id, "hours", "Lunes a sábado 9am-7pm")
    yape_number = get_setting(tenant_id, "yape_number", "")
    plin_number = get_setting(tenant_id, "plin_number", "")
    culqi_link = get_setting(tenant_id, "culqi_link", "")

    payment_lines = []
    if yape_number:
        payment_lines.append(f"- Yape: {yape_number}")
    if plin_number:
        payment_lines.append(f"- Plin: {plin_number}")
    if culqi_link:
        payment_lines.append(f"- Link de pago con tarjeta: {culqi_link}")
    if not payment_lines:
        payment_lines.append("- (Sin método de pago configurado aún)")
    payment_info = "\n".join(payment_lines)

    system = SYSTEM_TEMPLATE.format(
        business_name=business_name,
        catalog=catalog,
        hours=hours,
        payment_info=payment_info,
        items_placeholder="ITEMS_DEL_PEDIDO",
        total_placeholder=0,
    )

    history = get_history(tenant_id, customer_id, limit=8)
    messages = [{"role": "system", "content": system}] + history + [
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=400,
    )

    raw = response.choices[0].message.content or ""

    order_data = None
    match = ORDER_RE.search(raw)
    if match:
        try:
            order_data = json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
        raw = ORDER_RE.sub("", raw).strip()

    return raw, order_data
