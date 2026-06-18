import os
import base64
import json
import re
import httpx
from openai import OpenAI

_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


async def verify_payment_screenshot(
    image_url: str,
    twilio_sid: str,
    twilio_token: str,
    expected_total: int,
    yape_number: str = "",
    plin_number: str = "",
) -> tuple[bool, str]:
    """
    Downloads the Twilio image and asks DeepSeek VL2 whether it's a valid
    Yape/Plin payment for the expected amount.

    Returns (verified: bool, reason: str)
    """
    try:
        async with httpx.AsyncClient(timeout=15) as http:
            r = await http.get(image_url, auth=(twilio_sid, twilio_token))
            r.raise_for_status()
            image_b64 = base64.standard_b64encode(r.content).decode()
            media_type = r.headers.get("content-type", "image/jpeg").split(";")[0]
    except Exception as e:
        # If image can't be downloaded, accept payment to avoid blocking real customers
        return True, "No se pudo descargar la imagen, pago aceptado por defecto"

    recipients = []
    if yape_number:
        recipients.append(f"Yape: {yape_number}")
    if plin_number:
        recipients.append(f"Plin: {plin_number}")
    recipient_str = " o ".join(recipients) if recipients else "el número del negocio"

    prompt = f"""Analiza esta imagen. Es una supuesta captura de pago por Yape o Plin.

Verifica:
1. ¿Es un comprobante real de Yape o Plin?
2. ¿El monto es S/{expected_total}? (acepta ±1 sol de diferencia)
3. ¿El destinatario coincide con {recipient_str}? (si no se ve el número, acepta igual)

Responde ÚNICAMENTE con JSON:
{{"verificado": true/false, "motivo": "explicación breve en español"}}"""

    try:
        response = _client.chat.completions.create(
            model="deepseek-vl2",
            max_tokens=120,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_b64}"
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        raw = response.choices[0].message.content or ""
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return bool(data.get("verificado")), data.get("motivo", "")
        # If model doesn't return proper JSON, accept the payment
        return True, "Verificación no concluyente, pago aceptado"
    except Exception:
        # DeepSeek VL2 unavailable → accept payment, don't block the customer
        return True, "Verificación no disponible, pago aceptado"
