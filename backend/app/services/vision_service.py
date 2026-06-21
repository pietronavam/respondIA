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
    yape_name: str = "",
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

    # Build verification parameters
    yape_last3 = yape_number[-3:] if yape_number else ""
    plin_last3  = plin_number[-3:]  if plin_number  else ""

    phone_check = ""
    if yape_last3:
        phone_check += f"- Yape: los últimos 3 dígitos del número deben ser {yape_last3} (el resto aparece como ***). "
    if plin_last3:
        phone_check += f"- Plin: los últimos 3 dígitos deben ser {plin_last3}. "
    if not phone_check:
        phone_check = "- No hay número configurado, omite esta verificación."

    name_check = ""
    if yape_name:
        name_check = (f"El nombre del destinatario debe parecerse a '{yape_name}'. "
                      f"Yape muestra el nombre abreviado/truncado (ej: 'Nabila Gar*'). "
                      f"Acepta si las primeras letras del nombre o apellido coinciden.")
    else:
        name_check = "No hay nombre configurado, omite esta verificación."

    prompt = f"""Analiza esta captura de pantalla de pago por Yape o Plin.

Verifica en este orden:
1. AUTENTICIDAD: ¿Es un comprobante genuino de Yape o Plin? Rechaza si parece editado o falsificado.
2. MONTO: ¿El monto es exactamente S/{expected_total}? Si no coincide → rechaza.
3. NÚMERO DESTINO: {phone_check}
   Yape oculta los primeros 6 dígitos con ***. Solo compara los últimos 3 visibles.
   Si los últimos 3 dígitos son distintos a los esperados → rechaza.
   Si el número no es visible → acepta.
4. NOMBRE: {name_check}
   Si el nombre visible no tiene ninguna similitud con el esperado → rechaza.
   Si no hay nombre visible → acepta.
5. FECHA/HORA: ¿La transacción fue hoy o en las últimas 24 horas? Si no se ve → acepta.

Regla general: en caso de duda razonable → acepta (no bloquees pagos reales).

Responde ÚNICAMENTE con este JSON (sin texto extra):
{{"verificado": true/false, "motivo": "explicación breve en español", "monto_detectado": <número o null>, "numero_detectado": "<últimos 3 dígitos o null>"}}"""

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
