# Validación del Problema — RespondIA

## Evidencia cuantitativa

### 1. Brecha de digitalización en pymes peruanas (INEI / EEA 2024)
- **Fuente:** Encuesta Económica Anual 2024, INEI
- **Hallazgo:** El 95.6% de las microempresas formales peruanas no vende por e-commerce
- **Relevancia:** La mayoría gestiona pedidos por WhatsApp de forma manual, sin automatización

### 2. Impacto de la digitalización en productividad (Nava Montenegro, 2026)
- **Metodología:** Propensity Score Matching (PSM), n = 10,275 empresas del sector manufactura y comercio (EEA 2024)
- **Hallazgo:** Las empresas con presencia digital tienen **33% más productividad laboral** que sus pares no digitales
- **p-valor:** < 0.01 (significativo al 1%)
- **Conclusión:** La brecha no se cierra sola — requiere herramientas accesibles para el segmento MYPE

### 3. Tiempo perdido en atención manual (entrevista estructurada)
- **Entrevistada:** Dueña de boutique de ropa, Miraflores, Lima
- **Fecha:** Junio 2026
- **Hallazgo:** Pasa entre 3-5 horas diarias respondiendo mensajes de WhatsApp con preguntas repetitivas (precios, tallas, disponibilidad, horarios)
- **Costo de oportunidad estimado:** S/45-75 diarios en tiempo no dedicado a otras actividades de negocio

### 4. Competencia actual: sin solución accesible para MYPE
- **Observación:** Las soluciones existentes (ManyChat, Respond.io, WATI) tienen precios de $49-$299/mes USD
- **Barrera:** Requieren configuración técnica o contratar un desarrollador
- **Oportunidad:** No existe una solución en español, pensada para el mercado peruano, con onboarding en menos de 5 minutos

### 5. Validación del prototipo
- **Usuario beta:** Boutique Nabila Home (tenant de prueba activo)
- **Resultado:** Bot configurado y operativo en WhatsApp Sandbox; responde consultas de catálogo, procesa pedidos, detecta intereses de clientes y notifica al dueño
- **Flujo completo validado:** Consulta → respuesta automática → detección de interés → seguimiento → pedido → verificación de pago Yape/Plin → notificación de envío

## Segmento objetivo validado

**Cliente primario:** Dueño de tienda de ropa, calzado, accesorios o productos similares con venta por WhatsApp en Lima Metropolitana, con 1-5 empleados, que no tiene presupuesto para un community manager.

**Dolor principal:** Tiempo en mensajes repetitivos que no agregan valor; clientes sin respuesta fuera del horario laboral.

**Cómo lo resuelven hoy:** WhatsApp manual, respuestas guardadas en "Mensajes rápidos" de WhatsApp Business, o simplemente dejando mensajes sin contestar.
