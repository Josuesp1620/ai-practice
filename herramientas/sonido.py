"""Efectos de sonido sintetizados para el video: sin archivos externos ni derechos de terceros.

Se usan con moderación: whoosh suave entre escenas, teclas bajas al escribir y una campanita
solo cuando aparece una respuesta.

Cada efecto es una función que devuelve una muestra corta (numpy, mono, 44,1 kHz). `mezclar`
los coloca en su instante, evita que el mismo efecto suene varias veces seguidas y guarda un WAV.
"""
import wave

import numpy as np

FRECUENCIA = 44_100
AZAR = np.random.default_rng(7)  # misma semilla: el mismo video suena siempre igual


def envolvente(n, ataque, caida):
    """Sube en `ataque` segundos y cae de forma exponencial con constante `caida`."""
    tiempo = np.arange(n) / FRECUENCIA
    return np.minimum(1.0, tiempo / ataque) * np.exp(-tiempo / caida)


def pop():
    """Burbuja corta: un tono que baja rápido de 950 a 520 Hz."""
    n = int(0.09 * FRECUENCIA)
    tiempo = np.arange(n) / FRECUENCIA
    frecuencia = 520 + 430 * np.exp(-tiempo / 0.02)
    fase = 2 * np.pi * np.cumsum(frecuencia) / FRECUENCIA
    return 0.22 * np.sin(fase) * envolvente(n, 0.003, 0.03)


def aparece():
    """Más suave que el pop: para tarjetas y líneas que entran."""
    n = int(0.07 * FRECUENCIA)
    tiempo = np.arange(n) / FRECUENCIA
    frecuencia = 700 + 250 * np.exp(-tiempo / 0.02)
    fase = 2 * np.pi * np.cumsum(frecuencia) / FRECUENCIA
    return 0.10 * np.sin(fase) * envolvente(n, 0.004, 0.025)


def tecla():
    """Clic de teclado: ruido muy corto sin graves, con pequeña variación de volumen."""
    n = int(0.018 * FRECUENCIA)
    ruido = np.diff(AZAR.normal(size=n + 1))
    return AZAR.uniform(0.025, 0.04) * ruido * envolvente(n, 0.001, 0.004)


def cambio():
    """Whoosh: ruido que se abre y se cierra, filtrado para que suene a aire."""
    n = int(0.42 * FRECUENCIA)
    ruido = AZAR.normal(size=n)
    corte = 0.02 + 0.25 * np.sin(np.linspace(0, np.pi, n)) ** 2  # coeficiente del filtro
    salida, previo = np.zeros(n), 0.0
    for i in range(n):
        previo += corte[i] * (ruido[i] - previo)
        salida[i] = previo
    return 0.22 * salida * np.sin(np.linspace(0, np.pi, n)) ** 1.5


def ding():
    """Campanita: tono limpio (Do6) con dos armónicos suaves que se apagan antes que la nota."""
    n = int(0.8 * FRECUENCIA)
    tiempo = np.arange(n) / FRECUENCIA
    base = 1046.5
    campana = (np.sin(2 * np.pi * base * tiempo) * np.exp(-tiempo / 0.35)
               + 0.35 * np.sin(2 * np.pi * 2 * base * tiempo) * np.exp(-tiempo / 0.12)
               + 0.12 * np.sin(2 * np.pi * 3 * base * tiempo) * np.exp(-tiempo / 0.06))
    ataque = np.minimum(1.0, tiempo / 0.002)
    return 0.14 * campana * ataque


EFECTOS = {"pop": pop, "aparece": aparece, "tecla": tecla, "cambio": cambio, "ding": ding}
# Solo suenan los momentos puntuales: cambios de escena, teclas y la campanita de las respuestas.
# Las animaciones siguen anotando "pop" y "aparece", pero no se mezclan para no saturar.
AUDIBLES = {"tecla", "cambio", "ding"}
SEPARACION = {"pop": 0.09, "aparece": 0.12, "tecla": 0.03, "cambio": 0.3, "ding": 0.5}


def mezclar(eventos, duracion, destino):
    """`eventos` = [(tipo, segundo)] ordenados. Escribe un WAV mono de `duracion` segundos."""
    pista = np.zeros(int(duracion * FRECUENCIA) + FRECUENCIA)
    ultimo = {}
    for tipo, segundo in eventos:
        if tipo not in AUDIBLES:
            continue
        # Si el mismo efecto acaba de sonar (varios elementos entran juntos), no se repite.
        if segundo - ultimo.get(tipo, -10) < SEPARACION[tipo]:
            continue
        ultimo[tipo] = segundo
        muestra = EFECTOS[tipo]()
        inicio = int(segundo * FRECUENCIA)
        fin = min(len(pista), inicio + len(muestra))
        pista[inicio:fin] += muestra[:fin - inicio]
    pista = np.clip(pista, -0.95, 0.95)  # solo por seguridad: sin distorsionar los sonidos
    pista = pista[:int(duracion * FRECUENCIA)]
    with wave.open(str(destino), "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(FRECUENCIA)
        archivo.writeframes((pista * 32767 * 0.9).astype(np.int16).tobytes())
