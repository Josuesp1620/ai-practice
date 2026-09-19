# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastembed", "openai", "pgvector", "psycopg[binary]",
#   "pypdf", "python-dotenv",
# ]
# ///
"""
Pregúntale a tu PDF
===================

Haz preguntas a un PDF y recibe la respuesta con la página de donde sale.
Es un RAG (Retrieval-Augmented Generation) en tres pasos:

  1. INDEXAR    Leer el PDF, dividirlo en fragmentos y guardar cada
                uno como un vector (una lista de números que
                representa su significado).
  2. BUSCAR     Convertir la pregunta en vector y traer los fragmentos
                más parecidos.
  3. PREGUNTAR  Enviar esos fragmentos a la IA para que responda citando
                la página.

Uso:
    uv run main.py indexar ejemplos/codigo-consumidor.pdf
    uv run main.py buscar "¿Cuánto tiempo tiene una tienda para responder mi reclamo?"
    uv run main.py preguntar "¿Cuánto tiempo tiene una tienda para responder mi reclamo?"
"""
import os
import sys
import warnings
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastembed import TextEmbedding
from openai import OpenAI
from pgvector.psycopg import register_vector
from pypdf import PdfReader


# ─────────────────────────────────────────────────────────────
# 0. Configuración
# ─────────────────────────────────────────────────────────────

load_dotenv()  # lee OPENAI_API_KEY y demás variables del archivo .env

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/ia"
)
MODELO_IA = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

PALABRAS_POR_FRAGMENTO = 100  # tamaño de cada fragmento
PALABRAS_DE_SOLAPE = 25       # palabras que comparten dos seguidos
RESULTADOS = 5                # cuántos fragmentos se envían a la IA

# Modelo de embeddings: corre en tu PC, gratis, y entiende español.
# Convierte cualquier texto en un vector de 384 números.
warnings.filterwarnings("ignore", message=".*mean pooling.*")
embeddings = TextEmbedding(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# ─────────────────────────────────────────────────────────────
# 1. Base de datos: Postgres + pgvector
# ─────────────────────────────────────────────────────────────

def conectar():
    """Abre la conexión y crea la tabla la primera vez."""
    conexion = psycopg.connect(DATABASE_URL, autocommit=True)

    # pgvector añade a Postgres el tipo "vector" y la búsqueda
    # por similitud.
    conexion.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conexion)

    # Cada fila es un fragmento del PDF, con su página y su vector.
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS fragmentos (
            id        bigserial PRIMARY KEY,
            archivo   text,
            pagina    int,
            texto     text,
            embedding vector(384)
        )
    """)
    return conexion


# ─────────────────────────────────────────────────────────────
# 2. Paso 1: indexar el PDF
# ─────────────────────────────────────────────────────────────

def fragmentar(texto):
    """Divide un texto en fragmentos de palabras que se solapan.

    El solape evita cortar una idea por la mitad: el final de un
    fragmento se repite al inicio del siguiente.
    """
    palabras = texto.split()
    avance = PALABRAS_POR_FRAGMENTO - PALABRAS_DE_SOLAPE
    fragmentos = []
    for inicio in range(0, len(palabras), avance):
        fragmento = palabras[inicio:inicio + PALABRAS_POR_FRAGMENTO]
        fragmentos.append(" ".join(fragmento))
    return fragmentos


def indexar(ruta_pdf):
    archivo = Path(ruta_pdf).name

    # 1. Leer cada página y fragmentarla, recordando su número.
    fragmentos = []
    for numero, pagina in enumerate(PdfReader(ruta_pdf).pages, 1):
        for texto in fragmentar(pagina.extract_text() or ""):
            fragmentos.append((numero, texto))

    # 2. Convertir todos los fragmentos en vectores de una sola vez.
    textos = [texto for _, texto in fragmentos]
    vectores = list(embeddings.embed(textos))

    # 3. Guardar en la base (borrando antes una versión anterior).
    conexion = conectar()
    conexion.execute(
        "DELETE FROM fragmentos WHERE archivo = %s", (archivo,)
    )
    filas = [
        (archivo, numero, texto, vector)
        for (numero, texto), vector in zip(fragmentos, vectores)
    ]
    conexion.cursor().executemany(
        "INSERT INTO fragmentos (archivo, pagina, texto, embedding) "
        "VALUES (%s, %s, %s, %s)",
        filas,
    )
    print(f"{archivo}: {len(filas)} fragmentos indexados")


# ─────────────────────────────────────────────────────────────
# 3. Paso 2: buscar los fragmentos más parecidos
# ─────────────────────────────────────────────────────────────

def buscar(pregunta):
    # 1. La pregunta se convierte en vector con el mismo modelo.
    vector = next(embeddings.query_embed(pregunta))

    # 2. "<=>" mide qué tan lejos está cada fragmento de la pregunta.
    #    Menos distancia = significado más parecido.
    return conectar().execute(
        """
        SELECT pagina,
               texto,
               1 - (embedding <=> %s) AS similitud
        FROM fragmentos
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (vector, vector, RESULTADOS),
    ).fetchall()


# ─────────────────────────────────────────────────────────────
# 4. Paso 3: la IA responde con esos fragmentos
# ─────────────────────────────────────────────────────────────

INSTRUCCIONES = (
    "Responde solo con la información de los fragmentos. "
    "Cita la página de cada dato así: [p. 12]. "
    "Si la respuesta no está en los fragmentos, dilo."
)


def preguntar(pregunta):
    # 1. Buscar el contexto relevante.
    resultados = buscar(pregunta)

    # 2. Armar el contexto: cada fragmento con su página delante.
    contexto = "\n\n".join(
        f"[p. {pagina}]\n{texto}" for pagina, texto, _ in resultados
    )

    # 3. Pedir la respuesta al modelo.
    respuesta = OpenAI().responses.create(
        model=MODELO_IA,
        instructions=INSTRUCCIONES,
        input=f"Fragmentos:\n{contexto}\n\nPregunta: {pregunta}",
    )
    print(respuesta.output_text)


# ─────────────────────────────────────────────────────────────
# 5. Línea de comandos
# ─────────────────────────────────────────────────────────────

def mostrar_resultados(resultados):
    for pagina, texto, similitud in resultados:
        print(f"p. {pagina:<3} {similitud:.2f}  {texto[:36]}…")


if __name__ == "__main__":
    match sys.argv[1:]:
        case ["indexar", ruta_pdf]:
            indexar(ruta_pdf)
        case ["buscar", pregunta]:
            mostrar_resultados(buscar(pregunta))
        case ["preguntar", pregunta]:
            preguntar(pregunta)
        case _:
            print(__doc__)
