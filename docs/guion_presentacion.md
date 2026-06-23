# Guión de Presentación — RespondIA
**Pietro Marcelo Nava Montenegro · Slot #2 · 7:45 AM · 24-jun-2026**
**7 minutos de pitch + 3 minutos de preguntas**

---

> **Cómo usar este guión:** Las palabras en cursiva son lo que dices. Los corchetes son instrucciones de escena. Practica en voz alta al menos 2 veces antes de dormir.

---

## ANTES DE EMPEZAR

*[Mientras el anterior presentador termina y tú te preparas:]*
- Celular con WhatsApp abierto, listo para escribir al sandbox
- Panel de Streamlit abierto en otra pestaña: respond-ia.streamlit.app (email: nabila@demo.com / pass: demo1234)
- Pitch deck en pantalla en slide 1
- Silencia el celular EXCEPTO las notificaciones de WhatsApp

---

## SLIDE 1 — COVER (0:00 – 0:20)

*[Pasa al frente. Pausa de 2 segundos. Mira al público antes de abrir la boca.]*

*"Buenos días. Voy a hacerles una pregunta rápida."*

*[Pausa]*

*"¿Alguno de ustedes ha mandado un mensaje a una tienda por WhatsApp y esperó más de un día para que le contestaran?"*

*[Espera 2 segundos, mira las caras]*

*"Eso que acaban de imaginar... le pasa a miles de tiendas en Lima todos los días. Y ese es el problema que RespondIA resuelve."*

---

## SLIDE 2 — PROBLEMA (0:20 – 1:30)

*[Cambia a slide 2]*

*"El 95.6% de las microempresas peruanas formales no vende por e-commerce. ¿Cómo gestionan sus pedidos entonces? Por WhatsApp. Manualmente."*

*[Pausa breve]*

*"Yo hablé con una dueña de boutique en Miraflores el mes pasado. Me dijo algo que me quedó grabado: 'Pietro, yo paso entre 3 y 5 horas al día respondiendo mensajes de WhatsApp. Los mismos mensajes. Siempre los mismos: ¿cuánto cuesta?, ¿hay talla M?, ¿hacen delivery a Surco?'. Cinco horas. Cada día."*

*[Pausa]*

*"Y esto no es solo un tema de tiempo perdido. En mi investigación apliqué Propensity Score Matching sobre la Encuesta Económica Anual 2024 del INEI, con una muestra de 10,275 empresas. Encontré que las empresas con servicios digitales tienen 33% más productividad laboral que sus pares no digitalizadas, con p-valor menor a 0.01. Esa brecha no se cierra sola — requiere herramientas accesibles."*

*[Pausa — deja que el dato aterrice]*

*"El problema existe. Está medido. Y nadie en el mercado peruano lo ha resuelto de forma accesible."*

---

## SLIDE 3 — SOLUCIÓN (1:30 – 2:10)

*[Cambia a slide 3]*

*"RespondIA es el empleado de atención al cliente que nunca descansa."*

*[Pausa de 1 segundo]*

*"El dueño de la tienda sube su catálogo en texto plano — sin código, sin técnicos, en 5 minutos — y desde ese momento el bot hace el trabajo completo."*

*"No es solo un chatbot. RespondIA gestiona el flujo entero: responde preguntas de catálogo en lenguaje natural, incluyendo notas de voz que transcribe con Whisper. Cuando el cliente confirma un pedido, genera automáticamente un código único — '#RESPIA-0042'. Luego el cliente manda la foto de su Yape o Plin, y la IA la verifica al instante. Si un cliente pregunta pero no compra, el sistema guarda ese interés y le envía un seguimiento automático personalizado. Y el dueño recibe notificaciones en su WhatsApp cuando llega un pago."*

*"Todo esto sin que el dueño mueva un dedo."*

---

## SLIDE 4 — DEMO EN VIVO (2:10 – 4:15)

*[Cambia a slide 4. Toma el celular.]*

*"Pero en vez de contarles más, se los voy a mostrar en vivo. Esto no es una simulación — es el sistema funcionando en producción ahora mismo."*

*[Abre WhatsApp y muestra el celular a la cámara o pantalla]*

---

**[DEMO PASO 1 — CONSULTA]**

*"Voy a escribirle al bot como si fuera un cliente."*

*[Escribe: "hola! tienen polos talla M?"]*

*"Mandado."*

*[Espera la respuesta — máximo 3-4 segundos]*

*"¿Ven? Menos de 2 segundos. El bot respondió con los precios del catálogo real de la tienda Nabila Home. Lenguaje natural, precios correctos, directo al grano."*

---

**[DEMO PASO 2 — PEDIDO]**

*[Escribe: "quiero uno negro, cuánto es en total?"]*

*[Cuando responda:]*

*"El bot calculó el total incluyendo delivery, me pidió los datos de envío, y me dio las instrucciones de pago por Yape. Todo automático, en una respuesta."*

---

**[DEMO PASO 3 — VERIFICACIÓN DE PAGO]**

*"Ahora el cliente manda la captura de su Yape."*

*[Si tienes una captura de prueba guardada, mándala. Si no, describe lo que pasa:]*

*"Cuando el cliente manda la foto del comprobante, la IA de visión extrae el monto, verifica que coincide con el pedido, y responde al cliente confirmando su pedido con el código único. En ese mismo momento, la dueña recibe una notificación en su WhatsApp: '💰 Pago recibido — #RESPIA-0042, S/40 total'. Sin que ella haya hecho nada."*

---

**[DEMO PASO 4 — PANEL]**

*[Cambia a la pestaña de Streamlit]*

*"Y aquí en el panel de control — que también está en producción en respond-ia.streamlit.app — la dueña puede ver todas las conversaciones, los pedidos con su estado, y los intereses de los clientes que todavía no compraron."*

*[Señala la pantalla brevemente]*

*"Multi-tenant, tiempo real, desde cualquier dispositivo."*

---

## SLIDE 5 — MERCADO (4:15 – 4:50)

*[Cambia a slide 5]*

*"¿Cuán grande es el mercado? El TAM de software para pymes en Latinoamérica es de 2.1 mil millones de dólares. Nuestro SAM son las 450,000 pymes peruanas con WhatsApp activo — a S/70 de ticket promedio, son 378 millones de soles al año."*

*"Y la competencia no llega a este segmento. ManyChat, WATI, Respond.io — todos cobran entre 49 y 299 dólares al mes, están en inglés, y requieren configuración técnica. No existe nada en el mercado peruano, en español, con onboarding en 5 minutos, que verifique Yape o Plin."*

*"Nuestra meta año 1 es 2,500 clientes — eso es capturar menos del 1% del SAM."*

---

## SLIDE 7 — MODELO DE NEGOCIO (4:50 – 5:20)

*[Cambia a slide 7 — salta el 6 si vas justo de tiempo]*

*"El modelo es SaaS mensual. Dos planes: S/49 básico y S/99 pro. ARPU proyectado de S/70."*

*"El costo de la API de DeepSeek para un cliente activo promedio es de aproximadamente S/3 al mes. Eso nos da un margen bruto del 93%. LTV a 24 meses de S/1,330. CAC estimado de S/200. LTV/CAC de 6.6x — muy saludable para SaaS en etapa inicial."*

---

## SLIDE 8 — TRACCIÓN (5:20 – 5:50)

*[Cambia a slide 8]*

*"No estamos vendiendo una idea. Esto ya existe y ya funciona."*

*"El backend está en producción en Render desde junio 2026 con 99.9% de uptime. Tenemos un tenant beta activo — Nabila Home — con el flujo completo validado: desde la consulta hasta la verificación del pago. El panel de control está live en Streamlit Cloud. La landing page está en GitHub Pages. Y el código es público en github.com/pietronavam/respondIA."*

*"Lo que acaban de ver en la demo — eso es producción real, no un prototipo."*

---

## SLIDE 9 — VISIÓN (5:50 – 6:15)

*[Cambia a slide 9]*

*"Para Q3 2026: WhatsApp Business API oficial de Meta, registro self-service, pasarela de pago con Culqi, y 10 clientes pagantes."*

*"Para Q1 2027: expansión a Colombia y Ecuador — mismo idioma, mismo problema, mismo producto."*

*"Largo plazo: soporte en quechua para mercados rurales, integraciones con sistemas POS, y app móvil para el dueño."*

---

## SLIDE 10 — CIERRE (6:15 – 6:45)

*[Cambia a slide 10. Deja el celular. Mira al público.]*

*"2.5 millones de pymes peruanas merecen atender a sus clientes sin perder horas de su día."*

*[Pausa de 2 segundos]*

*"RespondIA ya existe. Ya funciona. Ya está en producción."*

*[Pausa]*

*"Si quieren probarlo ahora mismo — manden 'NABILA' al número de Twilio que está en pantalla. Les responde el bot en menos de 2 segundos."*

*[Pausa final]*

*"Gracias."*

*[Sonríe. No digas nada más. Espera las preguntas.]*

---

## PREGUNTAS — RESPUESTAS PREPARADAS (3 minutos)

### "¿Por qué DeepSeek y no ChatGPT?"
*"DeepSeek-chat cuesta 95% menos por token que GPT-4, con rendimiento comparable para español conversacional. Para el caso de uso específico de atención al cliente con catálogo fijo, es la decisión correcta técnica y económicamente. Además, el backend está desacoplado del modelo — puedo cambiar a cualquier LLM sin tocar el negocio."*

### "¿Qué pasa si Meta cierra el acceso a WhatsApp?"
*"Twilio Sandbox es para prototipado. El roadmap de Q3 2026 incluye migrar a WhatsApp Business API oficial de Meta, que tiene un SLA de 99.9% y un contrato formal. Además, la arquitectura está desacoplada del canal — si WhatsApp cerrara, podríamos migrar a SMS o Telegram sin reescribir el negocio."*

### "¿Cómo consigues los primeros clientes?"
*"Primeros 10: contacto directo con dueñas de boutiques en Miraflores y San Isidro, demo en vivo por WhatsApp, primer mes gratis. Tengo 3 conversaciones calificadas ya abiertas de las entrevistas que hice para validar el problema. Para llegar a 100: Facebook e Instagram Ads segmentados a 'dueños de tienda Lima', CPC estimado en S/15, CAC de S/200."*

### "¿No hay un problema de protección de datos?"
*"Cada negocio tiene su propia base de datos aislada — no compartimos datos entre tenants. Las conversaciones se guardan en PostgreSQL en Render con acceso únicamente por API key del negocio. No vendemos ni usamos los datos de los clientes de un negocio para entrenar modelos ni para nada más."*

### "¿Cómo escalas siendo solo founder?"
*"Claude Code como CTO virtual me permite construir en días lo que antes tomaba semanas a un equipo. Para escalar más allá del MVP, el primer uso de fondos sería contratar 1 developer junior para soporte técnico y features, mientras yo me enfoco en ventas y crecimiento."*

### "¿Cuánto tiempo tarda en configurarse?"
*"5 minutos. Registro, pegar el catálogo en texto plano, escanear el QR de Twilio. Eso es todo. No necesitas saber programar, no necesitas contratar a nadie."*

### "¿Funciona para negocios que no son tiendas de ropa?"
*"Sí. El catálogo es texto libre — funciona para cualquier rubro que venda por WhatsApp: ferretería, pastelería, veterinaria, inmobiliaria, lo que sea. Nabila Home es el primer caso, pero el sistema es completamente agnóstico al rubro."*

---

## PLAN B — SI EL DEMO FALLA

*Si el bot no responde en 5 segundos:*
> *"Render tiene un cold start de hasta 30 segundos cuando lleva un rato sin tráfico. Mientras arranca, les muestro el panel de control y les mando el chat del pitch deck que refleja una conversación real."*

*[Cambia a slide 4 del pitch deck y apunta al chat animado]*
> *"Este es exactamente el flujo que acabo de intentar mostrarles en vivo — el bot responde en menos de 2 segundos cuando está caliente, como lo estará mañana en producción real."*

*Si el panel de Streamlit no carga:*
> *"Streamlit Community Cloud tiene cold starts también — en 30 segundos está listo. Mientras tanto, les muestro los números de tracción."*

---

## CHECKLIST DE LA MAÑANA (7:00 AM)

- [ ] Despertar el backend: visitar `respondia.onrender.com/docs` — esperar que cargue
- [ ] Despertar el panel: abrir `respond-ia.streamlit.app` — esperar que cargue
- [ ] Enviar `NABILA` al +1 415 523 8886 desde tu WhatsApp para hacer warm-up del bot
- [ ] Confirmar que el bot responde correctamente
- [ ] Celular cargado al 100%
- [ ] Tener el PDF del dossier listo para compartir si te lo piden
- [ ] Llegar 10 minutos antes para verificar proyector/pantalla

---

## TIMING RESUMEN

| Slide | Contenido | Tiempo | Acumulado |
|---|---|---|---|
| 1 | Cover + hook | 0:20 | 0:20 |
| 2 | Problema + datos | 1:10 | 1:30 |
| 3 | Solución (6 features) | 0:40 | 2:10 |
| 4 | Demo en vivo | 2:05 | 4:15 |
| 5 | Mercado TAM/SAM/SOM | 0:35 | 4:50 |
| 7 | Modelo + unit economics | 0:30 | 5:20 |
| 8 | Tracción | 0:30 | 5:50 |
| 9 | Visión + roadmap | 0:25 | 6:15 |
| 10 | Cierre | 0:30 | 6:45 |
| — | Buffer | 0:15 | 7:00 |

---

*Tip final: habla más despacio de lo que crees que debes. En las presentaciones siempre se habla más rápido de lo normal por los nervios. El silencio después de una frase fuerte es tu mejor herramienta.*
