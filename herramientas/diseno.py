"""Piezas visuales de la serie para TikTok (1080×1920): fondo, títulos, ventanas, diagramas."""
import ast
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from pygments.lexers import PythonLexer
from pygments.token import Comment, Keyword, Name, Number, Operator, String

W, H, M = 1080, 1920, 64
LIMITE = 1500  # debajo queda la descripción y los botones de TikTok

PAPEL, TINTA, GRIS, SUAVE, LINEA = "#F5F2EC", "#171513", "#5E5850", "#9C958B", "#DDD6CC"
ACENTO, ACENTO_CLARO, VERDE, VERDE_CLARO = "#C4562A", "#F6E3D8", "#1F6F78", "#DDEBEC"
VENTANA, TEXTO = "#16161A", "#E7E2DA"
SANS, SERIF, MONO = "Inter", "Instrument Serif", "Fira Code"

COLORES = [
    (Comment, "#8A857D"), (String, "#A8D8A0"), (Number, "#D2A8FF"), (Keyword, "#F28A54"),
    (Name.Function, "#7FD1D9"), (Name.Builtin, "#7FD1D9"), (Operator, "#F28A54"),
]
CONSOLA = {"cmd": TEXTO, "out": "#CFC8BE", "tool": "#F28A54", "ai": "#A8D8A0", "dim": "#8A857D"}


def t(x, y, valor, tam=28, fuente=SANS, peso=400, color=TINTA, ancla="start", cursiva=False, opacidad=1, espacio=0):
    estilo = ' font-style="italic"' if cursiva else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fuente}" font-size="{tam}" font-weight="{peso}" '
            f'fill="{color}" text-anchor="{ancla}" letter-spacing="{espacio}" opacity="{opacidad}"'
            f'{estilo} xml:space="preserve">{escape(valor)}</text>')


def parrafo(x, y, valor, columnas, tam=30, salto=None, **opciones):
    salto = salto or tam * 1.4
    lineas = textwrap.wrap(valor, columnas)
    return "".join(t(x, y + i * salto, linea, tam, **opciones) for i, linea in enumerate(lineas)), y + len(lineas) * salto


def svg(cuerpo):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{cuerpo}</svg>'


def fondo(numero, etiqueta, pagina, total):
    progreso = (W - 2 * M) * pagina / total
    return (f'<rect width="{W}" height="{H}" fill="{PAPEL}"/>'
            + t(M, 190, "IA PRÁCTICA", 24, peso=700, espacio=3)
            + t(W - M, 190, f"Nº {numero} · {etiqueta}", 24, peso=700, color=ACENTO, ancla="end", espacio=2.5)
            + f'<rect x="{M}" y="218" width="{W - 2 * M}" height="4" rx="2" fill="{LINEA}"/>'
            + f'<rect x="{M}" y="218" width="{progreso:.1f}" height="4" rx="2" fill="{TINTA}"/>')


def titulo(lineas, acento, y=340, tam=84, a=None, inicio=0.0):
    """Líneas en sans y una línea de acento en serif cursiva; con `a`, entran una tras otra."""
    a = a or Anim()
    cuerpo = "".join(a.entra(t(M, y + i * tam * 1.05, l, tam, peso=600, espacio=-tam * 0.035), inicio + i * 0.1, 0.7, 50)
                     for i, l in enumerate(lineas))
    ya = y + len(lineas) * tam * 1.05 + 4
    cuerpo += a.entra(t(M, ya, acento, tam + 8, fuente=SERIF, cursiva=True, color=ACENTO),
                      inicio + len(lineas) * 0.1 + 0.08, 0.7, 50)
    return cuerpo, ya + 30


def caja(x, y, w, h, relleno="#FFFFFF", borde=LINEA, radio=24):
    trazo = f' stroke="{borde}" stroke-width="2"' if borde else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radio}" fill="{relleno}"{trazo}/>'


def ventana(x, y, w, h, nombre):
    return (f'<rect x="{x}" y="{y + 16:.1f}" width="{w}" height="{h:.1f}" rx="28" fill="{TINTA}" opacity=".16"/>'
            + caja(x, y, w, h, VENTANA, None, 28)
            + "".join(f'<circle cx="{x + 42 + i * 30}" cy="{y + 40:.1f}" r="9" fill="{c}"/>'
                      for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]))
            + t(x + w / 2, y + 48, nombre, 24, fuente=MONO, color="#8A857D", ancla="middle"))


def numero_circulo(cx, cy, n, color=ACENTO, r=26, texto_color="#FFFFFF"):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}"/>'
            + t(cx, cy + r * 0.36, str(n), r * 1.05, peso=700, color=texto_color, ancla="middle"))


def flecha_abajo(x, y1, y2, color=SUAVE):
    return (f'<path d="M{x} {y1} V{y2 - 4}" stroke="{color}" stroke-width="4" stroke-dasharray="2 10" stroke-linecap="round"/>'
            f'<path d="M{x - 12} {y2 - 16} L{x} {y2} L{x + 12} {y2 - 16}" stroke="{color}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


# ── Código ────────────────────────────────────────────────────────────────

def fragmento(ruta, objetivo):
    """"nombre" o "nombre@3-10": función o variable de un archivo, o solo ese tramo de líneas."""
    nombre, _, rango = objetivo.partition("@")
    fuente = Path(ruta).read_text()
    for nodo in ast.walk(ast.parse(fuente)):
        objetivos = [getattr(x, "id", None) for x in getattr(nodo, "targets", [])]
        if getattr(nodo, "name", None) == nombre or nombre in objetivos:
            lineas = fuente.splitlines()[nodo.lineno - 1:nodo.end_lineno]
            if rango:
                desde, hasta = map(int, rango.split("-"))
                lineas = lineas[desde - 1:hasta]
            return textwrap.dedent("\n".join(lineas))
    raise SystemExit(f"No encontré {nombre} en {ruta}")


def resaltar(codigo):
    lineas = [[]]
    for tipo, valor in PythonLexer().get_tokens(codigo):
        color = next((c for tt, c in COLORES if tipo in tt), TEXTO)
        for i, parte in enumerate(valor.split("\n")):
            if i:
                lineas.append([])
            if parte:
                lineas[-1].append((parte, color))
    while lineas and not lineas[-1]:
        lineas.pop()
    return lineas


def bloque_codigo(x, y, w, lineas, marcas=None, tam_max=34, a=None, momentos=None):
    """Ventana con código resaltado; `marcas` = {línea (1..n): número} pinta la línea y un círculo.

    Con `a` y `momentos` = {número: segundo}, cada marca se revela en su momento.
    """
    a = a or Anim()
    marcas = marcas or {}
    momentos = momentos or {}
    columnas = max(sum(len(p) for p, _ in l) for l in lineas)
    tam = min(tam_max, (w - 150) / (columnas * 0.6))
    salto = tam * 1.6
    h = 110 + len(lineas) * salto
    fondo_marcas, codigo, circulos = [], [], []
    for i, linea in enumerate(lineas, start=1):
        yl = y + 100 + (i - 1) * salto
        if i in marcas:
            inicio = momentos.get(marcas[i], 0.0)
            siguiente = momentos.get(marcas[i] + 1, inicio + 100)
            k = a.p(inicio, 0.45)
            # La marca que se está explicando brilla más que las ya vistas.
            intensidad = 0.16 if a.t is None else 0.08 + 0.18 * a.foco(inicio, siguiente)
            if k > 0:
                fondo_marcas.append(f'<rect x="{x + 8}" y="{yl - tam * 1.05:.1f}" width="{(w - 16) * k:.1f}" '
                                    f'height="{salto:.1f}" fill="#F28A54" opacity="{intensidad:.3f}"/>')
            circulos.append(a.pop(numero_circulo(x + w - 44, yl - tam * 0.32, marcas[i], r=20),
                                  x + w - 44, yl - tam * 0.32, inicio + 0.1))
        spans = "".join(f'<tspan fill="{c}">{escape(p)}</tspan>' for p, c in linea)
        codigo.append(f'<text x="{x + 40}" y="{yl:.1f}" font-family="{MONO}" font-size="{tam:.1f}" xml:space="preserve">{spans}</text>')
    return ventana(x, y, w, h, "main.py") + "".join(fondo_marcas + codigo + circulos), y + h


# ── Consola ───────────────────────────────────────────────────────────────

def filas_consola(lineas, w, tam):
    """Parte las líneas largas al ancho de la ventana. `lineas` = [(tipo, texto)] o [(tipo, texto, opacidad)]."""
    columnas = int((w - 80) / (tam * 0.6))
    filas = []
    for linea in lineas:
        tipo, texto = linea[0], linea[1]
        opacidad = linea[2] if len(linea) > 2 else 1
        prefijo = "$ " if tipo == "cmd" else ""
        partes = textwrap.wrap(prefijo + texto, columnas, drop_whitespace=False) or [prefijo]
        filas += [(tipo, p, opacidad) for p in partes]
    return filas


def alto_consola(lineas, w, tam=30):
    return 110 + len(filas_consola(lineas, w, tam)) * tam * 1.55


def texto_consola(x, y, w, lineas, tam=30, cursor=False):
    """Solo el texto de la consola (sin la ventana)."""
    filas = filas_consola(lineas, w, tam)
    salto = tam * 1.55
    cuerpo = []
    for i, (tipo, texto, opacidad) in enumerate(filas):
        if opacidad <= 0:
            continue
        yl = y + 105 + i * salto
        desplazamiento = (1 - opacidad) * 18
        if tipo == "cmd" and texto.startswith("$"):
            spans = f'<tspan fill="#7FD1D9">$ </tspan><tspan fill="{TEXTO}">{escape(texto[2:])}</tspan>'
        else:
            spans = f'<tspan fill="{CONSOLA[tipo]}">{escape(texto)}</tspan>'
        cuerpo.append(f'<text x="{x + 40}" y="{yl + desplazamiento:.1f}" opacity="{opacidad:.3f}" font-family="{MONO}" '
                      f'font-size="{tam}" xml:space="preserve">{spans}</text>')
        if cursor and i == len(filas) - 1:
            ancho = len(texto) * tam * 0.6
            cuerpo.append(f'<rect x="{x + 42 + ancho:.1f}" y="{yl - tam * 0.8:.1f}" width="{tam * 0.55:.1f}" '
                          f'height="{tam:.1f}" rx="3" fill="#F28A54"/>')
    return "".join(cuerpo)


def bloque_consola(x, y, w, lineas, tam=30, alto_min=0, cursor=False):
    h = max(alto_min, alto_consola(lineas, w, tam))
    return ventana(x, y, w, h, "terminal") + texto_consola(x, y, w, lineas, tam, cursor), y + h


# ── Animación ─────────────────────────────────────────────────────────────

def suave(k):
    """Ease-out cúbico."""
    k = min(max(k, 0.0), 1.0)
    return 1 - (1 - k) ** 3


def rebote(k):
    """Ease-out con un pequeño rebote al final."""
    k = min(max(k, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


PALABRAS_POR_SEGUNDO = 5.0  # lectura rápida de texto en pantalla (video corto, público técnico)


def lectura(texto, minimo=1.0):
    """Segundos para leer un texto: una base más un tiempo por palabra."""
    return max(minimo, 0.3 + len(texto.split()) / PALABRAS_POR_SEGUNDO)


class Ritmo:
    """Reparte momentos uno tras otro: cada elemento empieza cuando se termina de leer el anterior."""

    def __init__(self, inicio=0.0):
        self.reloj = inicio

    def siguiente(self, texto="", extra=0.0, segundos=None):
        momento = self.reloj
        self.reloj += (segundos if segundos is not None else lectura(texto)) + extra
        return momento


class Anim:
    """Tiempo de una escena. Con t=None todo se dibuja en su estado final (imágenes estáticas).

    Mientras se genera el video, `Anim.registro` = (conjunto, segundo de inicio de la escena):
    cada animación anota ahí un sonido en el cuadro en que empieza.
    """

    registro = None
    CUADRO = 1 / 60

    def __init__(self, t=None):
        self.t = t

    def sonar(self, tipo, instante):
        if self.t is None or Anim.registro is None:
            return
        if instante <= self.t < instante + Anim.CUADRO:
            eventos, desplazamiento = Anim.registro
            eventos.add((tipo, round(desplazamiento + instante, 3)))

    def p(self, inicio, dur=0.5, curva=suave):
        if self.t is None:
            return 1.0
        return curva((self.t - inicio) / dur)

    def entra(self, frag, inicio, dur=0.55, dy=40, dx=0):
        self.sonar("aparece", inicio)
        k = self.p(inicio, dur)
        if k >= 1:
            return frag
        if k <= 0:
            return ""
        return f'<g opacity="{min(k, 1):.3f}" transform="translate({dx * (1 - k):.1f},{dy * (1 - k):.1f})">{frag}</g>'

    def foco(self, inicio, fin, dur=0.25):
        """1 mientras el elemento es el que se está leyendo (entre inicio y fin), 0 antes y después."""
        if self.t is None:
            return 0.0
        return min(self.p(inicio, dur), 1 - self.p(fin, dur))

    def pop(self, frag, cx, cy, inicio, dur=0.5):
        self.sonar("pop", inicio)
        if self.p(inicio, 0.001) <= 0:
            return ""
        k = self.p(inicio, dur, rebote)
        if k == 1 and self.p(inicio, dur) >= 1:
            return frag
        opacidad = self.p(inicio, dur * 0.4)
        return (f'<g opacity="{opacidad:.3f}" transform="translate({cx:.1f},{cy:.1f}) scale({max(k, 0.01):.3f}) '
                f'translate({-cx:.1f},{-cy:.1f})">{frag}</g>')


# ── Iconos simples ────────────────────────────────────────────────────────

def icono(nombre, cx, cy, color=TINTA, s=1.0):
    g = f'<g transform="translate({cx},{cy}) scale({s})" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
    formas = {
        "pdf": '<path d="M-26 -36 H10 L28 -18 V36 H-26 Z"/><path d="M10 -36 V-18 H28"/><path d="M-14 0 H16 M-14 14 H16 M-14 -14 H2"/>',
        "fragmentos": '<rect x="-30" y="-34" width="60" height="18" rx="4"/><rect x="-30" y="-9" width="60" height="18" rx="4"/><rect x="-30" y="16" width="60" height="18" rx="4"/>',
        "vector": '<path d="M-30 30 L28 -28"/><path d="M8 -28 H28 V-8"/><circle cx="-30" cy="30" r="4"/>',
        "db": '<ellipse cx="0" cy="-24" rx="30" ry="11"/><path d="M-30 -24 V24 A30 11 0 0 0 30 24 V-24"/><path d="M-30 0 A30 11 0 0 0 30 0"/>',
        "chat": '<path d="M-32 -26 H32 V16 H-4 L-20 32 V16 H-32 Z"/><path d="M-16 -6 H16"/>',
        "lupa": '<circle cx="-6" cy="-6" r="22"/><path d="M10 10 L30 30"/>',
        "llave": '<circle cx="-16" cy="0" r="14"/><path d="M-2 0 H32 M20 0 V12 M30 0 V10"/>',
        "bucle": '<path d="M-24 -10 A28 28 0 1 1 -18 20"/><path d="M-34 -24 L-24 -10 L-10 -18"/>',
        "escudo": '<path d="M0 -34 L28 -22 V2 C28 20 14 30 0 36 C-14 30 -28 20 -28 2 V-22 Z"/><path d="M-12 0 L-2 10 L14 -8"/>',
        "persona": '<circle cx="0" cy="-16" r="14"/><path d="M-28 34 C-26 10 26 10 28 34"/>',
    }
    return g + formas[nombre] + "</g>"
