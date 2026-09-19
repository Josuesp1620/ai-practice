# /// script
# requires-python = ">=3.11"
# dependencies = ["openai", "python-dotenv"]
# ///
"""
Un agente de IA escrito a mano
==============================

Un agente es un bucle:

  1. El modelo recibe tu pregunta y la lista de herramientas.
  2. Si necesita un dato, pide usar una herramienta.
  3. Tu código ejecuta esa herramienta y le devuelve el resultado.
  4. Se repite hasta que el modelo ya no pide nada y responde.

Aquí el agente responde preguntas sobre las ventas de una tienda
consultando una base SQLite (tienda.db, se crea sola).

Uso:
    uv run main.py "¿Qué cliente compró más arroz en marzo?"
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import datos


# ─────────────────────────────────────────────────────────────
# 0. Configuración
# ─────────────────────────────────────────────────────────────

load_dotenv()  # lee OPENAI_API_KEY del archivo .env

MODELO_IA = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
BASE_DE_DATOS = Path(__file__).with_name("tienda.db")
MAXIMO_DE_VUELTAS = 10  # para que el agente nunca quede en bucle


# ─────────────────────────────────────────────────────────────
# 1. Herramientas: qué puede pedir el modelo
# ─────────────────────────────────────────────────────────────
# El modelo no ejecuta nada. Solo ve el nombre, la descripción
# y los parámetros de cada herramienta, y decide cuál pedir.

HERRAMIENTAS = [
    {
        "type": "function",
        "name": "ver_esquema",
        "description": "Devuelve las tablas y columnas de la base.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "consultar",
        "description": "Ejecuta una consulta SELECT de SQLite.",
        "parameters": {
            "type": "object",
            "properties": {"sql": {"type": "string"}},
            "required": ["sql"],
            "additionalProperties": False,
        },
    },
]


# ─────────────────────────────────────────────────────────────
# 2. Ejecutar la herramienta que pidió el modelo
# ─────────────────────────────────────────────────────────────

def ejecutar(nombre, argumentos):
    # "mode=ro" abre la base en solo lectura:
    # aunque la IA intente un DELETE, falla.
    conexion = sqlite3.connect(f"file:{BASE_DE_DATOS}?mode=ro", uri=True)

    if nombre == "ver_esquema":
        tablas = conexion.execute("SELECT sql FROM sqlite_master")
        return "\n".join(sql for (sql,) in tablas)

    if nombre == "consultar":
        filas = conexion.execute(argumentos["sql"]).fetchall()
        return json.dumps(filas[:50], ensure_ascii=False)

    return f"No existe la herramienta {nombre}"


# ─────────────────────────────────────────────────────────────
# 3. El bucle del agente
# ─────────────────────────────────────────────────────────────

def agente(pregunta):
    cliente = OpenAI()
    historial = [{"role": "user", "content": pregunta}]

    for _ in range(MAXIMO_DE_VUELTAS):
        # 1. El modelo ve la conversación y las herramientas.
        respuesta = cliente.responses.create(
            model=MODELO_IA, tools=HERRAMIENTAS, input=historial
        )
        historial += respuesta.output

        # 2. ¿Pidió alguna herramienta? Si no, ya respondió.
        llamadas = [
            item for item in respuesta.output
            if item.type == "function_call"
        ]
        if not llamadas:
            return respuesta.output_text

        # 3. Ejecutar cada herramienta y devolver el resultado.
        for llamada in llamadas:
            print(f"→ {llamada.name} {llamada.arguments}")
            resultado = ejecutar_con_errores(llamada)
            historial.append({
                "type": "function_call_output",
                "call_id": llamada.call_id,
                "output": resultado,
            })

    return "Me detuve: llegué al máximo de vueltas."


def ejecutar_con_errores(llamada):
    """Si la consulta falla, el error vuelve al modelo para que
    pueda corregir su SQL en la siguiente vuelta."""
    try:
        argumentos = json.loads(llamada.arguments or "{}")
        return ejecutar(llamada.name, argumentos)
    except sqlite3.Error as error:
        return f"Error: {error}"


# ─────────────────────────────────────────────────────────────
# 4. Línea de comandos
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not BASE_DE_DATOS.exists():
        datos.crear(BASE_DE_DATOS)

    pregunta = " ".join(sys.argv[1:]) or (
        "¿Qué cliente compró más arroz en marzo?"
    )
    print(agente(pregunta))
