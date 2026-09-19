"""Prepara la locución grabada con el celular para montarla en el video.

No se toca el sonido: nada de ecualizar, comprimir ni quitar ruido. Solo se recortan
los silencios del principio y del final, para que cada frase entre justo cuando empieza
su escena.
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Silencio por debajo de este nivel se considera "nada" al recortar los extremos.
UMBRAL_SILENCIO = "-38dB"
COLA = 0.12  # segundos de aire que se dejan al final

CADENA = (
    # Solo se recortan los silencios de los extremos: primero el del inicio y
    # luego el del final, dando la vuelta al audio. La voz queda tal como se grabó.
    f"silenceremove=start_periods=1:start_silence=0.08:start_threshold={UMBRAL_SILENCIO}:detection=peak,"
    "areverse,"
    f"silenceremove=start_periods=1:start_silence=0.08:start_threshold={UMBRAL_SILENCIO}:detection=peak,"
    "areverse,"
    f"apad=pad_dur={COLA}"
)


def duracion(ruta):
    salida = subprocess.run([FFMPEG, "-i", str(ruta)], capture_output=True, text=True).stderr
    horas, minutos, segundos = salida.split("Duration: ")[1].split(",")[0].split(":")
    return int(horas) * 3600 + int(minutos) * 60 + float(segundos)


def limpiar(origen, destino):
    """Deja el clip limpio y nivelado en `destino` (WAV 48 kHz mono)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_mtime > Path(origen).stat().st_mtime:
        return duracion(destino)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(origen),
                    "-af", CADENA, "-ar", "48000", "-ac", "1", str(destino)], check=True)
    return duracion(destino)


def preparar(carpeta_audios, carpeta_limpios, archivos):
    """{nombre de escena: (ruta limpia, duración)} para los clips indicados."""
    listo = {}
    for escena, archivo in archivos.items():
        origen = Path(carpeta_audios) / archivo
        if not origen.exists():
            continue
        destino = Path(carpeta_limpios) / f"{Path(archivo).stem}.wav"
        listo[escena] = (destino, limpiar(origen, destino))
    return listo
