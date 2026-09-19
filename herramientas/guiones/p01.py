"""Nº 01 · Pregúntale a tu PDF (con el Código de Protección y Defensa del Consumidor)."""
from diseno import (ACENTO, ACENTO_CLARO, GRIS, LINEA, M, MONO, SUAVE, TINTA, VENTANA, VERDE, VERDE_CLARO, W,
                    Ritmo, caja, icono, parrafo, t, titulo)

PROYECTO = "01-pregunta-a-tu-pdf"
# La portada ya muestra el indexado: en el video se salta ese paso (en el carrusel sigue).
FUERA_DEL_VIDEO = ["paso-1"]
NUMERO = "01"
ETIQUETA = "RAG"
PREGUNTA = "¿Cuánto tiempo tiene una tienda para responder mi reclamo?"

# Locución grabada, una frase por escena (assets/audios). Se limpia y nivela sola.
LOCUCION = {
    "portada": "1.ogg",
    "como-funciona": "2.ogg",
    "concepto": "3.ogg",
    "paso-2": "4.ogg",
    "paso-3": "5.ogg",
    "codigo": "6.ogg",
    "pruebalo": "7.ogg",
}


# ── Portada ───────────────────────────────────────────────────────────────
# El título se lee desde el primer cuadro; debajo se cuenta la historia en ~3,5 s:
# el PDF se escanea → se vuelve vectores → llega la pregunta → se enciende el vector que
# coincide → aparece la respuesta con su página.

portada = {
    "etiquetas": ["Python", "pgvector", "OpenAI"],
    "lineas": ["Le pregunto a un", "PDF de 86 páginas"],
    "acento": "y me cita la página.",
    "tam": 90,
}

FIN_PORTADA = 4.1
COLUMNAS, FILAS, COINCIDE = 8, 5, (1, 5)


def portada_animacion(a):
    cuerpo = ""

    # 1. El PDF
    px, py, pw, ph = M, 740, 270, 290
    pagina = caja(px, py, pw, ph) + t(px + 24, py + 46, "codigo-consumidor.pdf", 16, fuente=MONO, color=GRIS)
    for i in range(8):
        largo = pw - 48 - (70 if i % 3 == 2 else 0)
        pagina += f'<rect x="{px + 24}" y="{py + 74 + i * 20}" width="{largo}" height="8" rx="4" fill="#E4DED4"/>'
    pagina += (caja(px + 24, py + ph - 60, 124, 40, ACENTO_CLARO, None, 20)
               + t(px + 86, py + ph - 33, "86 págs", 21, peso=700, color=ACENTO, ancla="middle"))
    cuerpo += a.entra(pagina, 0.0, 0.45, 50)
    escaneo = a.p(0.4, 0.7)
    if a.t is not None and 0 < escaneo < 1:
        cuerpo += f'<rect x="{px + 12}" y="{py + 62 + escaneo * 170:.1f}" width="{pw - 24}" height="30" rx="6" fill="{ACENTO}" opacity=".2"/>'

    # 2. Los vectores: una ola de puntos que se encienden
    gx, gy, paso_x, paso_y = px + pw + 110, py + 40, 70, 48
    k = a.p(0.55, 0.35)
    if k > 0:
        x0 = px + pw + 18
        cuerpo += (f'<path d="M{x0} {py + ph / 2} H{x0 + 64 * k:.1f}" stroke="{SUAVE}" stroke-width="4" '
                   f'stroke-dasharray="2 10" stroke-linecap="round"/>')
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            cx, cy = gx + col * paso_x, gy + fila * paso_y
            punto = f'<circle cx="{cx}" cy="{cy}" r="10" fill="#CFC8BE"/>'
            cuerpo += a.pop(punto, cx, cy, 0.8 + (fila + col) * 0.04, 0.35)
    cuerpo += a.entra(t(gx - 10, gy + FILAS * paso_y + 18, "524 vectores · 384 dim", 22, fuente=MONO, color=GRIS), 1.3, 0.4, 10)

    # 3. La pregunta, escrita
    qy = 1080
    cuerpo += a.entra(caja(M, qy, W - 2 * M, 150) + icono("persona", M + 62, qy + 75, TINTA, 0.85), 1.45, 0.4, 30)
    escrito = PREGUNTA if a.t is None else PREGUNTA[:int(len(PREGUNTA) * a.p(1.6, 0.8, lambda x: min(max(x, 0), 1)))]
    if escrito:
        cuerpo += parrafo(M + 120, qy + 64, escrito, 40, 32, peso=600)[0]

    # 4. Se enciende el vector que coincide
    fila, col = COINCIDE
    cx, cy = gx + col * paso_x, gy + fila * paso_y
    encendido = a.p(2.45, 0.3)
    if encendido > 0:
        cuerpo += f'<circle cx="{cx}" cy="{cy}" r="{10 + 4 * encendido:.1f}" fill="{ACENTO}"/>'
        onda = a.p(2.45, 0.8)
        if a.t is not None and onda < 1:
            cuerpo += f'<circle cx="{cx}" cy="{cy}" r="{14 + 40 * onda:.1f}" fill="none" stroke="{ACENTO}" stroke-width="3" opacity="{1 - onda:.3f}"/>'

    # 5. La respuesta, con su página
    ry = 1262
    respuesta = (caja(M, ry, W - 2 * M, 210, VENTANA, None, 28)
                 + t(M + 44, ry + 62, "RESPUESTA", 22, peso=700, color="#7FD1D9", espacio=2.5)
                 + t(M + 44, ry + 150, "15 días hábiles", 70, peso=700, color="#F28A54", espacio=-2))
    cuerpo += a.entra(respuesta, 2.75, 0.45, 40)
    a.sonar("ding", 2.75)
    cita = caja(W - M - 290, ry + 102, 250, 64, "#F5F2EC", None, 32) + t(W - M - 165, ry + 144, "p. 18 · Art. 24", 27, peso=700, ancla="middle")
    cuerpo += a.pop(cita, W - M - 165, ry + 134, 3.05, 0.45)
    return cuerpo


diagrama = {
    "titulo": ["Cómo funciona"],
    "acento": "en 4 pasos.",
    "pasos": [
        ("fragmentos", "Chunking", "Fragmentos de 100 palabras, con 25 de solape y su número de página."),
        ("vector", "Embeddings", "Cada fragmento, un vector de 384 dimensiones. Modelo local con fastembed."),
        ("db", "pgvector", "Los 524 vectores en una columna vector(384) de Postgres."),
        ("chat", "Retrieval + LLM", "Trae los 5 fragmentos más parecidos. El LLM responde citando la página."),
    ],
}


# ── Concepto: buscar por significado ──────────────────────────────────────

TROZOS = [
    (0.69, "p. 18 · Art. 24", "«…dar respuesta a los mismos en un plazo no mayor de quince (15) días hábiles improrrogables.»", True),
    (0.52, "p. 21 · Art. 42", "«…actualización de su registro en una central de riesgo, dentro de un plazo no mayor a cinco (5) días hábiles…»", False),
]
CONCLUSION = "Las mismas palabras, distinto tema. Gana el fragmento que habla de reclamos."

_ritmo = Ritmo(0.4)
MOMENTO_PREGUNTA = _ritmo.siguiente(segundos=1.1)
MOMENTOS_TROZOS = [_ritmo.siguiente(segundos=1.9) for _ in TROZOS]
MOMENTO_CONCLUSION = _ritmo.siguiente(CONCLUSION)
FIN_CONCEPTO = _ritmo.reloj


def concepto(a):
    cuerpo, y = titulo(["Busca por significado,"], "no por palabras.", tam=72, a=a)
    y += 60
    pregunta = (caja(M, y, W - 2 * M, 176, "#FFFFFF") + icono("persona", M + 70, y + 88, TINTA, 0.9)
                + t(M + 130, y + 56, "TU PREGUNTA", 20, peso=700, color=SUAVE, espacio=2)
                + parrafo(M + 130, y + 98, PREGUNTA, 38, 32, peso=600)[0])
    cuerpo += a.entra(pregunta, MOMENTO_PREGUNTA, 0.5, 40)
    y += 200
    for n, (similitud, pagina, texto, gana) in enumerate(TROZOS):
        inicio = MOMENTOS_TROZOS[n]
        color = VERDE if gana else SUAVE
        ancho = W - 2 * M - 80
        tarjeta = (caja(M, y, W - 2 * M, 290, VERDE_CLARO if gana else "#FFFFFF", None if gana else LINEA)
                   + t(M + 40, y + 60, pagina, 28, peso=700, color=color)
                   + parrafo(M + 40, y + 112, texto, 46, 29, color=TINTA if gana else GRIS)[0]
                   + f'<rect x="{M + 40}" y="{y + 236}" width="{ancho}" height="18" rx="9" fill="#FFFFFF" opacity=".8"/>')
        cuerpo += a.entra(tarjeta, inicio, 0.5, 40)
        k = a.p(inicio + 0.35, 1.0)
        if k > 0:
            cuerpo += f'<rect x="{M + 40}" y="{y + 236}" width="{max(18, ancho * similitud * k):.1f}" height="18" rx="9" fill="{color}"/>'
            cuerpo += t(W - M - 40, y + 60, f"similitud {similitud * k:.2f}", 28, peso=700, color=color, ancla="end")
        y += 320
    texto, _ = parrafo(M, y + 40, CONCLUSION, 50, 31, color=TINTA, peso=500)
    return cuerpo + a.entra(texto, MOMENTO_CONCLUSION, 0.5, 20)


consola = {
    "titulo": ["Míralo"],
    "acento": "paso a paso.",
    "pasos": [
        {
            "titulo": "Indexas la ley una sola vez",
            "texto": "86 páginas fragmentadas y vectorizadas en tu PC, en segundos.",
            "lineas": [
                ("cmd", "uv run main.py indexar ejemplos/codigo-consumidor.pdf"),
                ("out", "codigo-consumidor.pdf: 524 fragmentos indexados"),
            ],
        },
        {
            "titulo": "Buscas sin gastar en IA",
            "texto": "La pregunta se vuelve vector y pgvector ordena por cercanía. Gana la página 18.",
            "lineas": [
                ("cmd", f'uv run main.py buscar "{PREGUNTA}"'),
                ("out", "p. 18  0.69  obligados a atender los reclamos pre…"),
                ("dim", "p. 46  0.59  fuera de los límites de tolerancia f…"),
                ("dim", "p. 17  0.59  consumidor puede dejar en dicho docu…"),
                ("dim", "p. 28  0.58  a la restitución El consumidor tiene…"),
                ("dim", "p. 23  0.57  La redacción y términos utilizados d…"),
            ],
        },
        {
            "titulo": "La IA responde y cita la página",
            "texto": "Recibe solo esos 5 fragmentos y cita de dónde saca cada dato.",
            "lineas": [
                ("cmd", f'uv run main.py preguntar "{PREGUNTA}"'),
                ("ai", "La tienda debe responder tu reclamo en un plazo no mayor de quince (15) días hábiles improrrogables [p. 18]."),
            ],
            "nota": "Respuesta de ejemplo: la redacción puede variar.",
        },
    ],
}

codigo = {
    "titulo": ["La búsqueda,"],
    "acento": "línea por línea.",
    "archivo": "main.py",
    "objetivo": "buscar",
    "marcas": {3: 1, 11: 2, 13: 3, 14: 4},
    "notas": [
        "La pregunta se convierte en un vector.",
        "Qué tan parecido es cada fragmento (de 0 a 1).",
        "Ordena los fragmentos por cercanía de significado.",
        "Se queda con los 5 más parecidos.",
    ],
}

cierre = {
    "comandos": [
        "cp .env.example .env",
        "docker compose up -d",
        "uv run main.py indexar ejemplos/codigo-consumidor.pdf",
        'uv run main.py preguntar "¿Cuánto tiempo tiene..."',
    ],
    "siguiente": "Nº 02 · Buscar fotos con palabras",
}
