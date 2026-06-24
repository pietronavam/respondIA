# Draft del Pitch — RespondIA
**Presentador:** Pietro Marcelo Nava Montenegro · Slot #2 · 7:45 AM · 24-jun-2026
**Duración objetivo:** 7 minutos + 3 min preguntas

---

## [SLIDE 1 — COVER] Apertura (0:00 – 0:30)

*Pausa breve. Mirar al público antes de hablar.*

"¿Cuántos de ustedes han esperado más de un día para que una tienda les conteste por WhatsApp?"

*Esperar reacción.*

"Eso les cuesta ventas a miles de pymes en Perú todos los días. Y ese es exactamente el problema que RespondIA resuelve."

---

## [SLIDE 2 — PROBLEMA] El problema (0:30 – 1:30)

"El 95.6% de las microempresas peruanas formales no vende por e-commerce. Gestionan todo por WhatsApp — manualmente.

Una dueña de boutique en Miraflores me contó que pasa entre 3 y 5 horas diarias respondiendo mensajes con las mismas preguntas: *¿cuánto cuesta?*, *¿hay talla M?*, *¿hacen delivery?*.

Y hay evidencia de que esto importa: en mi investigación con 10,275 empresas del sector manufactura y comercio, usando *Propensity Score Matching* sobre la EEA 2024 del INEI, encontré que las empresas con servicios digitales tienen **33% más productividad laboral** que sus pares no digitales. Y esa brecha no se cierra sola."

---

## [SLIDE 3 — SOLUCIÓN] La solución (1:30 – 2:30)

"RespondIA es el empleado de atención al cliente que nunca descansa.

El dueño sube su catálogo en texto — sin código, sin técnicos — y desde ese momento el bot atiende solo por WhatsApp.

Pero no es solo un chatbot. RespondIA hace el flujo completo:
- Responde preguntas de catálogo en lenguaje natural, incluyendo **notas de voz** que transcribe con Whisper
- Cuando el cliente confirma, crea un **pedido con código único** automáticamente
- Verifica el **pago de Yape o Plin** cuando el cliente manda la foto del comprobante — con IA de visión
- Si el cliente queda interesado pero no compra, guarda ese interés y envía **mensajes de seguimiento automáticos**
- Y en todo momento **notifica al dueño por WhatsApp** cuando llega un pago o se confirma un envío"

---

## [SLIDE 4 — DEMO] Demo en vivo (2:30 – 4:30)

*Abrir WhatsApp en el celular y el panel en la pantalla, o mostrar el chat animado del pitch deck.*

"Les voy a mostrar el flujo real. Esto es el sandbox de Twilio funcionando en producción."

*Enviar: "hola tienen polos talla M?"*
"El bot responde en menos de 2 segundos con los precios del catálogo real."

*Enviar: "uno negro, cuánto es el total?"*
"Calcula el total incluyendo delivery, pide el pago por Yape."

*Enviar foto de captura:*
"La IA verifica la captura — monto, cuenta destino — y confirma el pedido con su código. En paralelo, le llega una notificación al dueño en su WhatsApp: 💰 *Pago recibido — #RESPIA-0042*."

*Mostrar panel de Streamlit:*
"Y aquí en el panel aparece el pedido con su estado. Todo automático, todo registrado."

---

## [SLIDE 5 — MERCADO] Mercado (4:30 – 5:10)

"El mercado es enorme y no tiene competencia local accesible.

El TAM es de 2.1 mil millones de dólares en software para pymes en Latinoamérica. El SAM son aproximadamente 450 mil pymes peruanas con WhatsApp activo.

Las soluciones que existen — ManyChat, WATI, Respond.io — cuestan entre 49 y 299 dólares al mes, están en inglés, y requieren configuración técnica. No existe nada pensado para el mercado peruano, en español, con onboarding en 5 minutos.

Nuestra meta año 1 es 2,500 clientes — menos del 1% del SAM. A S/76 de ARPU, eso es S/190,000 de MRR y S/2.3 millones de ARR."

---

## [SLIDE 7 — MODELO] Modelo de negocio (5:10 – 5:45)

"Es SaaS mensual. Dos planes:
- **Básico S/59.99**: hasta 2,000 mensajes, gestión automática de pedidos, panel simplificado (el dueño solo ve pedidos por despachar).
- **Pro S/79.99**: mensajes ilimitados, audio con Whisper, imágenes con Vision, seguimiento de leads. Próximamente: followup post-venta y gestión de quejas.

Esperamos una distribución 20% / 80% entre ambos planes. Eso da un ARPU de S/76. Costo variable por cliente: ~S/5 (API + Twilio + infra). **Margen de contribución: 93%.** LTV: S/1,520. CAC: S/200. LTV/CAC: 7.6x."

---

## [SLIDE 8 — TRACCIÓN] Tracción (5:45 – 6:20)

"El MVP está en producción hoy.

El backend responde en Render 24/7. El flujo completo — consulta, pedido, verificación Yape/Plin, seguimiento de leads, notificación al dueño — fue probado internamente con usuarios de prueba (amigos y familia simulando clientes). No tenemos clientes de pago todavía, pero el sistema funciona de punta a punta.

El panel está live en Streamlit Cloud. La landing en GitHub Pages. Código público en GitHub."

---

## [SLIDE 9 — VISIÓN] Visión y roadmap (6:20 – 6:45)

"Lo que tienen hoy es un MVP completo. Para el lanzamiento en Q3 2026: WhatsApp Business API oficial de Meta, URL propia, opción de número dedicado por cliente, Vision API con Anthropic Claude, y expansión interprovincial con foco en Gamarra. Registro self-service con pasarela Culqi.

A largo plazo: app móvil para el dueño, automatizaciones con bancos y plataformas de las propias empresas, más funcionalidades e integraciones. Meta: 2,500 clientes en año 1 — MRR de S/190,000."

---

## [SLIDE 10 — CIERRE] Cierre (6:45 – 7:00)

"2.5 millones de pymes peruanas merecen atender a sus clientes sin perder horas de su día.

RespondIA ya existe, ya funciona, y está listo para escalar.

Pueden probarlo ahora mismo: manden *NABILA* al número de Twilio que aparece en pantalla.

Gracias."

---

## Preguntas probables — respuestas preparadas

**"¿Por qué DeepSeek y no GPT-4?"**
DeepSeek-chat tiene precio 95% menor por token con rendimiento comparable para español conversacional. Para el caso de uso de atención al cliente con catálogo fijo, es la decisión correcta. Podemos cambiar de modelo sin tocar el negocio.

**"¿Qué pasa si Twilio cae?"**
Twilio tiene SLA de 99.9%. En producción migraremos a WhatsApp Business API directa (Meta) que elimina la dependencia del sandbox.

**"¿Cómo protegen los datos de los clientes?"**
Todo corre en bases de datos separadas por tenant. Las conversaciones se guardan en PostgreSQL en Render con acceso solo por API key del negocio. No compartimos datos entre tenants.

**"¿Cuánto tiempo tarda en configurarse?"**
5 minutos: registro, pega el catálogo en texto plano, escanea el QR de Twilio. Eso es todo.

**"¿Funciona con cualquier tipo de negocio?"**
Validado con tienda de ropa. El catálogo es texto libre — funciona con cualquier rubro que venda por WhatsApp: ferretería, pastelería, veterinaria.

---

*Tip de presentación: habla despacio en el problema y más rápido en la solución/traction. La demo es el corazón — si algo falla, muestra el chat animado del pitch deck. Lleva el celular cargado al 100%.*
