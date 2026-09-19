# /// script
# requires-python = ">=3.11"
# dependencies = ["cairosvg", "pygments", "imageio-ffmpeg", "numpy"]
# ///
"""Genera el carrusel (PNG 1080×1920) y el video animado (MP4, 60 fps) de TikTok de cada proyecto.

    uv run herramientas/generar.py              # todos los proyectos con guion
    uv run herramientas/generar.py 01           # solo el 01
    uv run herramientas/generar.py 01 --sin-video

Cada proyecto se describe en herramientas/guiones/pNN.py. Sale en <proyecto>/assets/tiktok/.
Necesita las fuentes Inter, Instrument Serif y Fira Code instaladas.

Ritmo del video
---------------
- Cada texto aparece cuando toca leerlo y dura lo que se tarda en leerlo (diseno.lectura).
- El elemento que se está leyendo lleva el foco (borde o marca naranja); el foco avanza solo.
- Las escenas se encadenan con una salida corta; la portada es el primer cuadro.

Sonido
------
Solo efectos, generados en sonido.py y sincronizados con la animación: whoosh al cambiar de
escena, pop al aparecer elementos, teclas al escribir y un ding en las respuestas. La música se
pone en la app de TikTok al publicar.
"""
import hashlib
import importlib
import os
import shutil
import subprocess
import sys
import tempfile
from multiprocessing import Pool
from pathlib import Path

import cairosvg
import imageio_ffmpeg

import sonido
import voz

from diseno import (ACENTO, ACENTO_CLARO, GRIS, LIMITE, M, MONO, SERIF, SUAVE, TINTA, W, H, Anim, Ritmo,
                    alto_consola, bloque_codigo, caja, flecha_abajo, fondo, fragmento, icono, lectura,
                    numero_circulo, parrafo, resaltar, suave, svg, t, texto_consola, titulo, ventana)

RAIZ = Path(__file__).resolve().parent.parent
MARGEN_VOZ = 0.8        # aire que se deja después de cada frase
ENTRADA_VOZ = 0.35      # cuánto tarda en empezar a hablar dentro de la escena
VOLUMEN_EFECTOS = 0.45  # los efectos bajan cuando hay locución
REPO = "github.com/Josuesp1620/ai-practice"
FPS = 60
SALIDA = 0.3            # transición de salida al final de cada escena
TECLEO = 45             # caracteres por segundo al escribir comandos
ZOOM = 0.0              # acercamiento de cámara (desactivado: hacía que el texto pareciera crecer)


# ── Escenas ───────────────────────────────────────────────────────────────
# Cada escena es una función escena_x(g) que devuelve (dibujar, fin):
#   dibujar(a) -> (fijo, variable)   "fijo" se mantiene entre escenas seguidas del mismo tipo
#   fin                              segundo en que termina su contenido (sin la salida)

def escena_portada(g):
    p = g.portada

    def dibujar(a):
        x, cuerpo = M, ""
        for etiqueta in p["etiquetas"]:
            ancho = len(etiqueta) * 15.6 + 48
            cuerpo += (f'<rect x="{x:.0f}" y="276" width="{ancho:.0f}" height="54" rx="27" fill="none" stroke="{TINTA}" stroke-width="2"/>'
                       + t(x + ancho / 2, 312, etiqueta, 26, fuente=MONO, peso=600, ancla="middle"))
            x += ancho + 14
        tam = p.get("tam", 88)
        cuerpo += "".join(t(M, 450 + i * tam * 1.05, l, tam, peso=600, espacio=-tam * 0.035)
                          for i, l in enumerate(p["lineas"]))
        cuerpo += t(M, 450 + len(p["lineas"]) * tam * 1.05 + 6, p["acento"], tam + 8, fuente=SERIF, cursiva=True, color=ACENTO)
        return "", cuerpo + g.portada_animacion(a)

    return dibujar, g.FIN_PORTADA


def escena_diagrama(g):
    d = g.diagrama
    pasos = d["pasos"]
    # Las tarjetas entran en cascada rápida; después el foco recorre cada paso.
    entradas = [0.25 + i * 0.12 for i in range(len(pasos))]
    ritmo = Ritmo(entradas[-1] + 0.35)
    inicios = [ritmo.siguiente(segundos=0.7) for _ in pasos]
    fin = ritmo.reloj + 0.2
    arriba, alto, hueco = 540, 200, 44
    ancho = W - 2 * M - (90 if d.get("bucle") else 0)

    def dibujar(a):
        cuerpo, _ = titulo(d["titulo"], d["acento"], a=a)
        for i, (nombre, encabezado, texto) in enumerate(pasos):
            inicio = entradas[i]
            siguiente = inicios[i + 1] if i + 1 < len(pasos) else fin + 10
            foco = a.foco(inicios[i], siguiente)
            y = arriba + i * (alto + hueco)
            ultimo = i == len(pasos) - 1
            tarjeta = caja(M, y, ancho, alto)
            if foco > 0:
                tarjeta += (f'<rect x="{M}" y="{y}" width="{ancho}" height="{alto}" rx="24" fill="none" '
                            f'stroke="{ACENTO}" stroke-width="4" opacity="{foco:.3f}"/>')
            tarjeta += t(M + 180, y + 78, encabezado, 38, peso=600)
            tarjeta += parrafo(M + 180, y + 124, texto, 48, 27, color=GRIS)[0]
            cuerpo += a.entra(tarjeta, inicio, 0.5, 50)
            resaltado = ultimo or foco > 0.5
            circulo = (f'<circle cx="{M + 90}" cy="{y + alto / 2}" r="54" fill="{ACENTO_CLARO if resaltado else "#F1EDE6"}"/>'
                       + icono(nombre, M + 90, y + alto / 2, ACENTO if resaltado else TINTA, 0.95))
            cuerpo += a.pop(circulo, M + 90, y + alto / 2, inicio + 0.1)
            cuerpo += a.pop(numero_circulo(M + 130, y + 52, i + 1, TINTA, 20), M + 130, y + 52, inicio + 0.2)
            if not ultimo:
                k = a.p(entradas[i + 1] - 0.1, 0.3)
                if k > 0:
                    cuerpo += f'<g opacity="{k:.3f}">{flecha_abajo(M + 90, y + alto + 6, y + alto + 6 + (hueco - 10) * k)}</g>'
        if d.get("bucle"):
            cuerpo += bucle(a, d["bucle"], inicios, arriba, alto, hueco)
        for inicio in inicios:
            a.sonar("aparece", inicio)
        return "", cuerpo

    return dibujar, fin


def bucle(a, tramo, inicios, arriba, alto, hueco):
    """Flecha "se repite" que se dibuja desde un paso hasta otro anterior."""
    desde, hasta = tramo
    inicio = inicios[desde - 1] + 0.2
    y1 = arriba + (desde - 1) * (alto + hueco) + alto / 2
    y2 = arriba + (hasta - 1) * (alto + hueco) + alto / 2
    x = W - M - 90
    largo = 50 + (y1 - y2) + 36
    k = a.p(inicio, 0.7)
    if k <= 0:
        return ""
    cuerpo = (f'<path d="M{x} {y1} H{x + 50} V{y2} H{x + 14}" stroke="{ACENTO}" stroke-width="5" fill="none" '
              f'stroke-linejoin="round" stroke-dasharray="{largo:.0f}" stroke-dashoffset="{largo * (1 - k):.1f}"/>')
    punta = (f'<path d="M{x + 28} {y2 - 12} L{x + 12} {y2} L{x + 28} {y2 + 12}" stroke="{ACENTO}" stroke-width="5" '
             f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    etiqueta = t(x + 70, (y1 + y2) / 2, "se repite", 24, peso=600, color=ACENTO, ancla="middle").replace(
        "<text ", f'<text transform="rotate(90 {x + 70} {(y1 + y2) / 2})" ')
    return cuerpo + a.entra(punta + etiqueta, inicio + 0.55, 0.4, 0)


def escena_concepto(g):
    return (lambda a: ("", g.concepto(a))), g.FIN_CONCEPTO


def ventana_consola(g):
    """Una sola altura para todos los pasos, así la ventana no salta entre uno y otro."""
    ancho = W - 2 * (M - 16)
    alto = max(520, *(alto_consola(p["lineas"], ancho) for p in g.consola["pasos"]))
    return M - 16, 600, ancho, alto


def escena_paso(g, i):
    c = g.consola
    paso = c["pasos"][i]
    x, y, ancho, alto = ventana_consola(g)

    # Momentos de cada línea: los comandos se escriben, las salidas aparecen una tras otra.
    momentos, reloj = [], 0.45
    for tipo, texto in paso["lineas"]:
        if tipo == "cmd":
            dur = len(texto) / TECLEO
            momentos.append((reloj, dur))
            reloj += dur + 0.3
        else:
            momentos.append((reloj, 0.3))
            reloj += 0.15 if tipo == "dim" else 0.45
    fin_consola = reloj
    fin = max(fin_consola + 0.7, lectura(f"{paso['titulo']} {paso['texto']}") - 0.6)

    def dibujar(a):
        fijo, _ = titulo(c["titulo"], c["acento"], tam=72, a=a)
        fijo += a.entra(ventana(x, y, ancho, alto, "terminal"), 0.1, 0.5, 40)

        variable = a.entra(t(M, 560, f"PASO {i + 1} DE {len(c['pasos'])}", 24, peso=700, color=ACENTO, espacio=2.5), 0.0, 0.4, 20)
        lineas, cursor = [], False
        for (tipo, texto), (inicio, dur) in zip(paso["lineas"], momentos):
            if a.t is None:
                lineas.append((tipo, texto))
                continue
            if a.t < inicio:
                break
            if tipo == "cmd":
                for letra in range(0, len(texto), 2):
                    a.sonar("tecla", inicio + letra / TECLEO)
                k = min(1.0, (a.t - inicio) / dur)
                lineas.append((tipo, texto[:int(len(texto) * k)]))
                cursor = k < 1 or int(a.t * 2.5) % 2 == 0
            else:
                a.sonar("ding" if tipo == "ai" else "aparece", inicio)
                lineas.append((tipo, texto, a.p(inicio, dur)))
                cursor = False
        variable += texto_consola(x, y, ancho, lineas, cursor=cursor)

        yc = max(y + alto + 50, 1170)
        alto_caja = LIMITE - yc
        texto, fin_texto = parrafo(M + 110, yc + 126, paso["texto"], 44, 28, color=GRIS)
        encabezado = caja(M, yc, W - 2 * M, alto_caja) + t(M + 110, yc + 78, paso["titulo"], 36, peso=600)
        variable += a.entra(encabezado, 0.05, 0.5, 50)
        variable += a.entra(texto, 0.35, 0.5, 20)
        if paso.get("nota"):
            variable += a.entra(t(M + 110, min(fin_texto + 18, yc + alto_caja - 26), paso["nota"], 22, color=SUAVE, cursiva=True),
                                fin_consola, 0.4, 10)
        variable += a.pop(numero_circulo(M + 60, yc + 66, i + 1), M + 60, yc + 66, 0.2)
        return fijo, variable

    return dibujar, fin


def escena_codigo(g):
    c = g.codigo
    ritmo = Ritmo(0.7)
    momentos = {n: ritmo.siguiente(segundos=0.45 + len(nota.split()) / 6) for n, nota in enumerate(c["notas"], start=1)}
    fin = ritmo.reloj
    lineas = resaltar(fragmento(RAIZ / g.PROYECTO / c["archivo"], c["objetivo"]))

    def dibujar(a):
        cuerpo, _ = titulo(c["titulo"], c["acento"], tam=72, a=a)
        bloque, final = bloque_codigo(M - 16, 520, W - 2 * (M - 16), lineas, c["marcas"], a=a, momentos=momentos)
        cuerpo += a.entra(bloque, 0.2, 0.6, 50)
        y = final + 60
        salto = (LIMITE - y) / len(c["notas"])
        for n, nota in enumerate(c["notas"], start=1):
            yn = y + (n - 1) * salto
            siguiente = momentos.get(n + 1, fin + 10)
            foco = 1.0 if a.t is None else a.foco(momentos[n], siguiente)
            color = TINTA if a.t is None or foco > 0 else GRIS
            cuerpo += a.pop(numero_circulo(M + 22, yn + 10, n, r=22), M + 22, yn + 10, momentos[n] + 0.1)
            cuerpo += a.entra(parrafo(M + 66, yn + 20, nota, 52, 29, color=color, peso=600 if foco > 0.5 else 400)[0],
                              momentos[n] + 0.18, 0.45, 0, dx=-30)
        return "", cuerpo

    return dibujar, fin


def escena_cierre(g):
    c = g.cierre
    comandos = [("cmd", x) for x in c["comandos"]]
    ritmo = Ritmo(0.5)
    momentos = [ritmo.siguiente(segundos=len(texto) / (TECLEO * 1.4), extra=0.15) for _, texto in comandos]
    repo, proximo = ritmo.reloj + 0.1, ritmo.reloj + 0.9
    fin = proximo + 1.4

    def dibujar(a):
        cuerpo, _ = titulo(["Pruébalo"], "en 5 minutos.", tam=96, a=a)
        visibles = []
        for (tipo, texto), inicio in zip(comandos, momentos):
            for letra in range(0, len(texto), 2):
                a.sonar("tecla", inicio + letra / (TECLEO * 1.4))
            if a.t is None or a.t >= inicio:
                k = 1.0 if a.t is None else min(1.0, (a.t - inicio) / (len(texto) / (TECLEO * 1.4)))
                visibles.append((tipo, texto[:int(len(texto) * k)]))
        x, y, ancho = M - 16, 560, W - 2 * (M - 16)
        alto = alto_consola(comandos, ancho, 28)
        cuerpo += a.entra(ventana(x, y, ancho, alto, "terminal"), 0.15, 0.5, 40)
        cuerpo += texto_consola(x, y, ancho, visibles, tam=28)
        ya = y + alto + 110
        cuerpo += a.entra(t(M, ya, "Código completo", 36, peso=600) + t(M, ya + 52, REPO, 30, fuente=MONO, color=GRIS)
                          + t(M, ya + 94, f"/{g.PROYECTO}", 30, fuente=MONO, color=GRIS), repo, 0.5, 30)
        cuerpo += a.entra(caja(M, ya + 160, W - 2 * M, 150, TINTA, None)
                          + t(M + 44, ya + 225, "PRÓXIMO", 22, peso=700, color="#F28A54", espacio=2.5)
                          + t(M + 44, ya + 272, c["siguiente"], 34, peso=600, color="#FFFFFF"), proximo, 0.6, 50)
        return "", cuerpo

    return dibujar, fin


def locucion(g):
    """{escena: (audio limpio, duración)} si el guion trae clips grabados."""
    archivos = getattr(g, "LOCUCION", None)
    if not archivos:
        return {}
    audios = RAIZ / g.PROYECTO / "assets" / "audios"
    return voz.preparar(audios, audios / "limpios", archivos)


def escenas(g):
    """(tipo, nombre, dibujar, duración) en orden.

    Si la escena tiene locución, dura al menos lo que la frase más un respiro.
    """
    lista = [
        ("portada", "portada", *escena_portada(g)),
        ("diagrama", "como-funciona", *escena_diagrama(g)),
        ("concepto", "concepto", *escena_concepto(g)),
    ]
    lista += [("consola", f"paso-{i + 1}", *escena_paso(g, i)) for i in range(len(g.consola["pasos"]))]
    lista += [("codigo", "codigo", *escena_codigo(g)), ("cierre", "pruebalo", *escena_cierre(g))]
    hablado = locucion(g)
    resultado = []
    for tipo, nombre, dibujar, fin in lista:
        dur = fin + SALIDA
        if nombre in hablado:
            dur = max(dur, ENTRADA_VOZ + hablado[nombre][1] + MARGEN_VOZ)
        resultado.append((tipo, nombre, dibujar, dur))
    return resultado


# ── Imágenes ──────────────────────────────────────────────────────────────

def png(documento, destino):
    cairosvg.svg2png(bytestring=documento.encode(), write_to=str(destino), output_width=W, output_height=H)


def escenas_video(g):
    """Las escenas del carrusel que entran en el video (el guion puede saltarse las repetidas)."""
    omitidas = getattr(g, "FUERA_DEL_VIDEO", [])
    return [escena for escena in escenas(g) if escena[1] not in omitidas]


def carrusel(g, salida):
    lista = escenas(g)
    for n, (_, nombre, dibujar, _) in enumerate(lista, start=1):
        fijo, variable = dibujar(Anim())
        destino = salida / f"{n:02d}-{nombre}.png"
        png(svg(fondo(g.NUMERO, g.ETIQUETA, n, len(lista)) + fijo + variable), destino)
        print(f"✓ {destino.relative_to(RAIZ)}")


# ── Video ─────────────────────────────────────────────────────────────────

def camara(contenido, progreso):
    """Acercamiento lento y continuo, centrado en la zona útil de la pantalla."""
    escala = 1 + ZOOM * progreso
    cx, cy = W / 2, 880
    return f'<g transform="translate({cx},{cy}) scale({escala:.5f}) translate({-cx},{-cy})">{contenido}</g>'


def cuadros(g, eventos):
    """SVG de cada cuadro del video. Los sonidos que disparan se anotan en `eventos`."""
    lista = escenas_video(g)
    total = len(lista)
    duraciones = [d for *_, d in lista]
    # Las escenas seguidas del mismo tipo comparten el recorrido de la cámara.
    grupos = []
    for n in range(total):
        primero = n
        while primero > 0 and lista[primero - 1][0] == lista[n][0]:
            primero -= 1
        ultimo = n
        while ultimo + 1 < total and lista[ultimo + 1][0] == lista[n][0]:
            ultimo += 1
        grupos.append((sum(duraciones[:primero]), sum(duraciones[primero:ultimo + 1])))

    transcurrido = 0.0
    for n, (tipo, _, dibujar, dur) in enumerate(lista):
        if n + 1 < total:
            eventos.add(("cambio", round(transcurrido + dur - SALIDA, 3)))
        anterior = lista[n - 1][0] if n else None
        siguiente = lista[n + 1][0] if n + 1 < total else None
        inicio_grupo, largo_grupo = grupos[n]
        for f in range(round(dur * FPS)):
            segundo = f / FPS
            Anim.registro = (eventos, transcurrido)
            a = Anim(segundo)
            fijo, _ = dibujar(a if tipo != anterior else Anim(segundo + 60))
            _, variable = dibujar(a)
            k = suave((segundo - (dur - SALIDA)) / SALIDA) if siguiente else 0.0
            if k > 0:
                variable = f'<g opacity="{1 - k:.3f}" transform="translate(0,{-40 * k:.1f})">{variable}</g>'
                if tipo != siguiente:
                    fijo = f'<g opacity="{1 - k:.3f}" transform="translate(0,{-40 * k:.1f})">{fijo}</g>'
            progreso_camara = (transcurrido + segundo - inicio_grupo) / largo_grupo
            progreso = min(n + 1 + segundo / dur, total)
            yield svg(fondo(g.NUMERO, g.ETIQUETA, progreso, total) + camara(fijo + variable, progreso_camara))
        transcurrido += dur
    Anim.registro = None


def renderizar(tarea):
    documento, destino = tarea
    png(documento, destino)


def video(g, destino):
    with tempfile.TemporaryDirectory() as tmp:
        tareas, vistos, enlaces, eventos = [], {}, [], set()
        for i, documento in enumerate(cuadros(g, eventos)):
            archivo = Path(tmp) / f"{i:05d}.png"
            huella = hashlib.md5(documento.encode()).hexdigest()
            if huella in vistos:
                enlaces.append((vistos[huella], archivo))
            else:
                vistos[huella] = archivo
                tareas.append((documento, archivo))
        with Pool(os.cpu_count()) as pool:
            for _ in pool.imap_unordered(renderizar, tareas, chunksize=4):
                pass
        for origen, copia in enlaces:
            copia.symlink_to(origen)
        total = len(tareas) + len(enlaces)
        efectos = Path(tmp) / "efectos.wav"
        sonido.mezclar(sorted(eventos, key=lambda e: e[1]), total / FPS, efectos)

        # La locución se coloca en el segundo en que empieza su escena.
        hablado = locucion(g)
        entradas, filtros, pistas = [], [], []
        reloj = 0.0
        for n, (_, nombre, _, dur) in enumerate(escenas(g)):
            if nombre in hablado:
                archivo, _ = hablado[nombre]
                indice = len(entradas) // 2 + 2
                entradas += ["-i", str(archivo)]
                retraso = int((reloj + ENTRADA_VOZ) * 1000)
                filtros.append(f"[{indice}:a]adelay={retraso}|{retraso}[v{n}]")
                pistas.append(f"[v{n}]")
            reloj += dur

        if pistas:
            mezcla = (";".join(filtros)
                      + f";{''.join(pistas)}amix=inputs={len(pistas)}:normalize=0[voz];"
                      f"[1:a]volume={VOLUMEN_EFECTOS}[efectos];"
                      "[voz][efectos]amix=inputs=2:normalize=0,alimiter=limit=0.95[audio]")
            mapa = ["-filter_complex", mezcla, "-map", "0:v", "-map", "[audio]"]
        else:
            mapa = ["-map", "0:v", "-map", "1:a"]

        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", str(Path(tmp) / "%05d.png"), "-i", str(efectos), *entradas, *mapa,
                        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(destino)], check=True)
        print(f"  {total / FPS:.1f} s, {len(tareas)} cuadros distintos de {total}, "
              f"{len(eventos)} sonidos, {len(pistas)} frases de locución")


# ── Principal ─────────────────────────────────────────────────────────────

def generar(modulo, con_video):
    g = importlib.import_module(f"guiones.{modulo}")
    salida = RAIZ / g.PROYECTO / "assets" / "tiktok"
    shutil.rmtree(salida, ignore_errors=True)
    salida.mkdir(parents=True)
    carrusel(g, salida)
    if con_video:
        destino = salida / "video.mp4"
        video(g, destino)
        print(f"✓ {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    argumentos = [x for x in sys.argv[1:] if not x.startswith("--")]
    filtro = argumentos[0] if argumentos else ""
    for modulo in sorted(p.stem for p in (Path(__file__).parent / "guiones").glob("p*.py")):
        if modulo[1:].startswith(filtro):
            generar(modulo, "--sin-video" not in sys.argv)
