"""Nº 04 · Un agente en 60 líneas."""
from diseno import (ACENTO, ACENTO_CLARO, GRIS, LINEA, M, MONO, SUAVE, TINTA, VENTANA, VERDE, VERDE_CLARO, W,
                    Ritmo, bloque_consola, caja, icono, parrafo, t, texto_consola, titulo, ventana)

PROYECTO = "04-agente-en-60-lineas"
# La portada ya muestra la pregunta: en el video se salta ese paso (en el carrusel sigue).
FUERA_DEL_VIDEO = ["paso-1"]
NUMERO = "04"
ETIQUETA = "AGENTES"
PREGUNTA = "¿Qué cliente compró más arroz en marzo?"


# ── Portada ───────────────────────────────────────────────────────────────
# El título se lee desde el primer cuadro; debajo, un punto recorre el bucle
# Tú → LLM → Tool → LLM (dos vueltas) mientras la terminal muestra cada llamada,
# y al final aparece la respuesta.

portada = {
    "etiquetas": ["Python", "OpenAI", "Function calling"],
    "lineas": ["Un agente de IA", "no es magia:"],
    "acento": "es un bucle.",
    "tam": 90,
}

FIN_PORTADA = 4.3
NODOS_Y = 895
NODOS = [(M + 110, "persona", "Tú"), (W / 2, "chat", "LLM"), (W - M - 110, "llave", "Tool")]
# (inicio, fin, desde, hasta, por_el_bucle)
RECORRIDO = [(0.55, 0.9, 0, 1, False), (1.05, 1.4, 1, 2, False), (1.5, 1.95, 2, 1, True),
             (2.05, 2.4, 1, 2, False), (2.5, 2.95, 2, 1, True)]
TERMINAL = [
    ("cmd", f'uv run main.py "{PREGUNTA}"', 0.25),
    ("tool", "→ ver_esquema {}", 1.4),
    ("tool", '→ consultar {"sql": "SELECT …"}', 2.4),
]


def curva_bucle(k):
    """Punto k (0..1) sobre la curva que va de Tool a LLM por arriba."""
    (x0, _, _), (x1, _, _) = NODOS[2], NODOS[1]
    y = NODOS_Y - 62
    cx0, cy0, cx1, cy1 = x0, y - 150, x1, y - 150
    u = 1 - k
    return (u ** 3 * x0 + 3 * u * u * k * cx0 + 3 * u * k * k * cx1 + k ** 3 * x1,
            u ** 3 * y + 3 * u * u * k * cy0 + 3 * u * k * k * cy1 + k ** 3 * y)


def portada_animacion(a):
    cuerpo = ""

    # 1. Los tres nodos y sus conexiones
    for n, (cx, nombre, etiqueta) in enumerate(NODOS):
        nodo = (f'<circle cx="{cx}" cy="{NODOS_Y}" r="62" fill="#FFFFFF" stroke="{LINEA}" stroke-width="2"/>'
                + icono(nombre, cx, NODOS_Y, TINTA, 1.0))
        cuerpo += a.pop(nodo, cx, NODOS_Y, 0.05 + n * 0.1, 0.45)
        cuerpo += a.entra(t(cx, NODOS_Y + 106, etiqueta, 28, peso=600, color=GRIS, ancla="middle"), 0.15 + n * 0.1, 0.4, 10)
    for (x0, _, _), (x1, _, _) in zip(NODOS, NODOS[1:]):
        cuerpo += a.entra(f'<path d="M{x0 + 76} {NODOS_Y} H{x1 - 76}" stroke="{SUAVE}" stroke-width="4" '
                          f'stroke-dasharray="2 10" stroke-linecap="round"/>', 0.3, 0.3, 0)
    x0, y0 = curva_bucle(0)
    x1, y1 = curva_bucle(1)
    arco = (f'<path d="M{x0} {y0} C{x0} {y0 - 150} {x1} {y1 - 150} {x1} {y1}" stroke="{ACENTO}" stroke-width="4" '
            f'fill="none" stroke-dasharray="10 10"/>'
            + t(W / 2 + 160, NODOS_Y - 190, "se repite", 26, peso=600, color=ACENTO, ancla="middle"))
    cuerpo += a.entra(arco, 1.5, 0.4, 0)

    # 2. El punto que viaja por el bucle
    if a.t is not None:
        for inicio, fin, desde, hasta, por_bucle in RECORRIDO:
            if inicio <= a.t <= fin:
                k = a.p(inicio, fin - inicio)
                if por_bucle:
                    px, py = curva_bucle(k)
                else:
                    px = NODOS[desde][0] + (NODOS[hasta][0] - NODOS[desde][0]) * k
                    py = NODOS_Y
                cuerpo += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="15" fill="{ACENTO}"/>'
    listo = a.p(3.0, 0.3)
    if listo > 0:
        cuerpo += f'<circle cx="{NODOS[1][0]}" cy="{NODOS_Y}" r="62" fill="none" stroke="{ACENTO}" stroke-width="{5 * listo:.1f}"/>'

    # 3. La terminal, al ritmo del punto
    tx, ty, ancho = M - 16, 1040, W - 2 * (M - 16)
    lineas = [(tipo, texto) for tipo, texto, _ in TERMINAL]
    alto = 110 + 4 * 28 * 1.55
    cuerpo += a.entra(ventana(tx, ty, ancho, alto, "terminal"), 0.1, 0.4, 30)
    visibles = []
    for tipo, texto, inicio in TERMINAL:
        if a.t is None:
            visibles.append((tipo, texto))
        elif a.t >= inicio:
            if tipo == "cmd":
                for letra in range(0, len(texto), 3):
                    a.sonar("tecla", inicio + letra / len(texto) * 0.9)
                visibles.append((tipo, texto[:int(len(texto) * min(1.0, (a.t - inicio) / 0.9))]))
            else:
                visibles.append((tipo, texto, a.p(inicio, 0.25)))
    cuerpo += texto_consola(tx, ty, ancho, visibles, tam=28)

    # 4. La respuesta
    ry = 1342
    respuesta = (caja(M, ry, W - 2 * M, 158, VENTANA, None, 28)
                 + t(M + 44, ry + 52, "RESPUESTA", 22, peso=700, color="#7FD1D9", espacio=2.5)
                 + t(M + 44, ry + 124, "Bodega Don Lucho", 56, peso=700, color="#F28A54", espacio=-1.5))
    cuerpo += a.entra(respuesta, 3.15, 0.45, 40)
    a.sonar("ding", 3.15)
    cifra = caja(W - M - 250, ry + 78, 210, 60, "#F5F2EC", None, 30) + t(W - M - 145, ry + 118, "147 unid.", 28, peso=700, ancla="middle")
    cuerpo += a.pop(cifra, W - M - 145, ry + 108, 3.45, 0.45)
    return cuerpo


diagrama = {
    "titulo": ["El bucle"],
    "acento": "de un agente.",
    "bucle": (3, 2),
    "pasos": [
        ("persona", "Input", "Tu pregunta más la lista de tools."),
        ("chat", "El LLM decide", "Responde, o pide una tool con function_call."),
        ("llave", "Tu código ejecuta", "Corre la función y devuelve function_call_output."),
        ("chat", "Respuesta final", "Sin más function_call, el bucle termina."),
    ],
}


# ── Concepto: las herramientas ────────────────────────────────────────────

HERRAMIENTAS = [
    ("ver_esquema()", "Devuelve las tablas y columnas de la base."),
    ("consultar(sql)", "Ejecuta un SELECT y devuelve las filas."),
]
EXPLICACION = "El modelo no ejecuta nada: solo pide. Tu código decide."
SEGURIDAD = "La base se abre en solo lectura. Si la IA intenta borrar algo, falla:"

_ritmo = Ritmo(0.4)
MOMENTOS_HERRAMIENTAS = [_ritmo.siguiente(segundos=0.9) for _ in HERRAMIENTAS]
MOMENTO_EXPLICACION = _ritmo.siguiente(EXPLICACION, extra=-0.4)
MOMENTO_SEGURIDAD = _ritmo.siguiente(segundos=1.0)
MOMENTO_DELETE = _ritmo.siguiente(segundos=1.5)
FIN_CONCEPTO = _ritmo.reloj


def concepto(a):
    cuerpo, y = titulo(["Herramientas:"], "funciones que la IA pide.", tam=72, a=a)
    y += 60
    for n, (nombre, texto) in enumerate(HERRAMIENTAS):
        inicio = MOMENTOS_HERRAMIENTAS[n]
        tarjeta = (caja(M, y, W - 2 * M, 170) + t(M + 140, y + 72, nombre, 36, fuente=MONO, peso=600)
                   + parrafo(M + 140, y + 120, texto, 50, 28, color=GRIS)[0])
        cuerpo += a.entra(tarjeta, inicio, 0.5, 40)
        cuerpo += a.pop(icono("llave", M + 75, y + 85, ACENTO, 0.9), M + 75, y + 85, inicio + 0.15)
        y += 200
    parr, y2 = parrafo(M, y + 50, EXPLICACION, 50, 32, peso=500)
    cuerpo += a.entra(parr, MOMENTO_EXPLICACION, 0.5, 20)
    y = y2 + 30
    escudo = (caja(M, y, W - 2 * M, 150, VERDE_CLARO, None)
              + t(M + 140, y + 66, "La base se abre en solo lectura", 32, peso=600, color=VERDE)
              + t(M + 140, y + 110, "Si la IA intenta borrar algo, falla:", 27, color=GRIS))
    cuerpo += a.entra(escudo, MOMENTO_SEGURIDAD, 0.5, 40)
    cuerpo += a.pop(icono("escudo", M + 75, y + 75, VERDE, 0.9), M + 75, y + 75, MOMENTO_SEGURIDAD + 0.15)
    lineas = [("tool", "→ consultar DELETE FROM ventas"), ("out", "attempt to write a readonly database")]
    if a.t is not None:
        lineas = [(tipo, texto, a.p(MOMENTO_DELETE + i * 0.5, 0.35)) for i, (tipo, texto) in enumerate(lineas)]
    consola, _ = bloque_consola(M - 16, y + 185, W - 2 * (M - 16), lineas, tam=28, alto_min=190)
    return cuerpo + a.entra(consola, MOMENTO_DELETE - 0.3, 0.4, 30)


consola = {
    "titulo": ["Míralo"],
    "acento": "vuelta por vuelta.",
    "pasos": [
        {
            "titulo": "Haces una pregunta normal",
            "texto": "El agente recibe tu pregunta y las tools que puede pedir.",
            "lineas": [("cmd", 'uv run main.py "¿Qué cliente compró más arroz en marzo?"')],
        },
        {
            "titulo": "Vuelta 1: pide ver la base",
            "texto": "No conoce tus tablas: pide el esquema y tu código se lo devuelve.",
            "lineas": [
                ("cmd", 'uv run main.py "¿Qué cliente compró más arroz en marzo?"'),
                ("tool", "→ ver_esquema {}"),
                ("dim", "CREATE TABLE clientes (id, nombre)"),
                ("dim", "CREATE TABLE productos (id, nombre, precio)"),
                ("dim", "CREATE TABLE ventas (cliente_id, producto_id, cantidad, fecha)"),
            ],
        },
        {
            "titulo": "Vuelta 2: escribe el SQL",
            "texto": "Ya sabe qué consultar. Tu código corre el SELECT en solo lectura.",
            "lineas": [
                ("tool", '→ consultar {"sql": "SELECT c.nombre, SUM(v.cantidad) FROM ventas v JOIN … WHERE p.nombre LIKE \'Arroz%\' AND strftime(\'%m\', v.fecha) = \'03\' …"}'),
                ("dim", '[["Bodega Don Lucho", 147], ["Tienda Rosita", 71], ["Ferretería Lima", 56]]'),
            ],
        },
        {
            "titulo": "Vuelta 3: responde",
            "texto": "Ya tiene el dato, no pide más tools y el bucle termina.",
            "lineas": [("ai", "Bodega Don Lucho: 147 unidades de arroz en marzo.")],
            "nota": "Simulación con los datos reales de tienda.db; la redacción puede variar.",
        },
    ],
}

codigo = {
    "titulo": ["El bucle,"],
    "acento": "línea por línea.",
    "archivo": "main.py",
    "objetivo": "agente@1-18",
    "marcas": {5: 1, 7: 2, 13: 3, 17: 4},
    "notas": [
        "Máximo 10 vueltas: nunca queda en bucle.",
        "El modelo ve la conversación y las herramientas.",
        "¿Pidió alguna herramienta?",
        "Si no pidió nada, ya tiene la respuesta.",
    ],
}

cierre = {
    "comandos": [
        "cp .env.example .env",
        'uv run main.py "¿Qué producto se vende más?"',
    ],
    "siguiente": "Nº 05 · RAG contra un agente con grep",
}
