# 01 · Pregúntale a tu PDF

Haz preguntas a un PDF y recibe la respuesta con la página exacta de donde sale.

La demo usa un documento real: el **Código de Protección y Defensa del Consumidor del Perú (Ley N.° 29571)**, 86 páginas.

## Cómo funciona

1. **Indexar:** lee el PDF página por página, lo divide en fragmentos de 100 palabras que se solapan y guarda cada fragmento con su vector en Postgres (pgvector).
2. **Buscar:** convierte la pregunta en vector y trae los 5 fragmentos más parecidos (el operador `<=>` de pgvector mide qué tan lejos está cada fragmento).
3. **Preguntar:** envía esos fragmentos a la IA con la instrucción de responder solo con ellos y citar la página.

Los vectores (embeddings) se calculan en tu PC con `paraphrase-multilingual-MiniLM-L12-v2`, que entiende español y ocupa 220 MB. Solo el paso 3 usa la API de OpenAI.

## Ejecutarlo

Necesitas [uv](https://docs.astral.sh/uv/getting-started/installation/) y Docker.

```bash
cp .env.example .env          # pon tu OPENAI_API_KEY
docker compose up -d          # Postgres con pgvector en el puerto 5433

uv run main.py indexar ejemplos/codigo-consumidor.pdf
uv run main.py buscar "¿Cuánto tiempo tiene una tienda para responder mi reclamo?"
uv run main.py preguntar "¿Cuánto tiempo tiene una tienda para responder mi reclamo?"
```

`buscar` no usa IA: solo muestra los fragmentos encontrados. Deberías ver exactamente esto:

```
codigo-consumidor.pdf: 524 fragmentos indexados

p. 18  0.69  obligados a atender los reclamos pre…
p. 46  0.59  fuera de los límites de tolerancia f…
p. 17  0.59  consumidor puede dejar en dicho docu…
p. 28  0.58  a la restitución El consumidor tiene…
p. 23  0.57  La redacción y términos utilizados d…
```

La página 18 es el artículo 24: *"…dar respuesta a los mismos en un plazo no mayor de quince (15) días hábiles improrrogables."*

Otras preguntas que puedes probar:

| Pregunta | Página esperada |
|---|---|
| ¿Las tiendas deben tener libro de reclamaciones? | 64 (art. 150) |
| ¿Qué pasa si me discriminan en una tienda? | 20 (art. 38) |
| ¿Deben mostrar los precios de los productos? | 12 (art. 5) |

Para usar tu propio documento, cambia la ruta del PDF.

## Leer el código

`main.py` está dividido en secciones numeradas, en el mismo orden en que corre el programa:

| Sección | Qué hace |
|---|---|
| 0. Configuración | Variables, tamaño de los fragmentos y modelo de embeddings |
| 1. Base de datos | Conexión y creación de la tabla `fragmentos` |
| 2. Paso 1: indexar | `fragmentar()` e `indexar()` |
| 3. Paso 2: buscar | `buscar()`: la consulta de similitud |
| 4. Paso 3: preguntar | `preguntar()`: arma el contexto y llama a la IA |
| 5. Línea de comandos | Los comandos `indexar`, `buscar` y `preguntar` |

## Fuente del PDF

`ejemplos/codigo-consumidor.pdf` es la edición 2023 del Código de Protección y Defensa del Consumidor publicada por el Indecopi en [gob.pe](https://cdn.www.gob.pe/uploads/document/file/4265044/Co%CC%81digo%20de%20Proteccio%CC%81n%20y%20Defensa%20del%20Consumidor%20-%202023%20(1).pdf.pdf). Es un texto legal oficial, de acceso público.
