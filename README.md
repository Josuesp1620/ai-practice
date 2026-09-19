# AI Practice · IA práctica

Proyectos pequeños de IA en Python, cada uno con su demo. Cada proyecto:

- tiene menos de 150 líneas,
- se ejecuta con [uv](https://docs.astral.sh/uv/) sin instalar nada a mano (las dependencias van dentro de `main.py`),
- usa [pgvector](https://github.com/pgvector/pgvector) en Docker cuando necesita una base vectorial,
- genera embeddings en local con [fastembed](https://github.com/qdrant/fastembed), sin gastar en API,
- usa la API de OpenAI cuando necesita un modelo.

## Proyectos

| # | Proyecto | Qué aprendes | Estado |
|---|---|---|---|
| 01 | [Pregúntale a tu PDF](01-pregunta-a-tu-pdf) | RAG: fragmentar, vectorizar, buscar y responder citando la página | Listo |
| 02 | Buscador de imágenes por texto | Embeddings de imágenes con CLIP en pgvector | Próximamente |
| 03 | Detector de tickets duplicados | Similitud de vectores con umbral | Próximamente |
| 04 | [Un agente en 60 líneas](04-agente-en-60-lineas) | El bucle de un agente con herramientas, escrito a mano | Listo |
| 05 | RAG vs. agente que busca con grep | Dos enfoques respondiendo la misma pregunta | Próximamente |
| 06 | Chat con memoria a largo plazo | Guardar y recuperar recuerdos con pgvector | Próximamente |
| 07 | Ocultar datos personales antes de enviarlos a la IA | Enmascarado reversible | Próximamente |
| 08 | Clasificador de correos con salida estructurada | JSON garantizado para automatizar | Próximamente |
| 09 | Agente con tope de presupuesto | Contar tokens y detenerse antes de gastar de más | Próximamente |
| 10 | Recomendador de productos | Recomendaciones por similitud con pgvector | Próximamente |

## Requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker (solo en los proyectos con base vectorial)
- Una API key de OpenAI en `.env` (copia `.env.example`)

## Contenido para TikTok

Cada proyecto con guion genera, en `assets/tiktok/`, un carrusel de imágenes de 1080×1920 y un video MP4 animado a 60 fps de unos 40 segundos:

1. **Portada** con el gancho.
2. **Cómo funciona:** diagrama del flujo paso a paso.
3. **Concepto clave** explicado con un ejemplo real.
4. **Consola paso a paso:** qué se ejecuta y qué pasa en cada paso.
5. **Código** con marcadores numerados y su explicación.
6. **Pruébalo:** los comandos para correrlo y el enlace al código.

En el video cada elemento entra con su animación (desliza, aparece o crece), las barras se llenan, la consola se escribe en vivo con cursor, las marcas del código se revelan una a una y las escenas pasan con transiciones suaves.

```bash
uv run herramientas/generar.py                # todos los proyectos con guion
uv run herramientas/generar.py 01             # solo el 01
uv run herramientas/generar.py 01 --sin-video # solo el carrusel
```

- **Guiones:** cada proyecto se describe en `herramientas/guiones/pNN.py` (textos, pasos de la consola, qué líneas de código marcar).
- **Diseño:** las piezas visuales están en `herramientas/diseno.py`.
- **Zona libre:** el contenido queda por encima de la parte que tapa la interfaz de TikTok.

Necesita las fuentes Inter, Instrument Serif y Fira Code instaladas.

El material generado (imágenes, video y locución) no se versiona: se queda en local.
