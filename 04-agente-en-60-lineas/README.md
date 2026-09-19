# 04 · Un agente en 60 líneas

Un agente de IA no es magia: es un bucle. El modelo decide qué herramienta usar, tu código la ejecuta y le devuelve el resultado, hasta que tiene la respuesta.

Aquí el agente responde preguntas sobre una tienda consultando una base SQLite con dos herramientas: `ver_esquema` y `consultar`.

## Ejecutarlo

```bash
cp .env.example .env          # pon tu OPENAI_API_KEY
uv run main.py "¿Qué cliente compró más arroz en marzo?"
```

La primera vez crea `tienda.db` con 5 clientes, 5 productos y 500 ventas de ejemplo (`datos.py`). Verás cada herramienta que usa el agente:

```
→ ver_esquema {}
→ consultar {"sql": "SELECT ..."}
Bodega Don Lucho, con 147 unidades.
```

## Leer el código

`main.py` está dividido en secciones numeradas:

| Sección | Qué hace |
|---|---|
| 0. Configuración | Modelo, base de datos y máximo de vueltas |
| 1. Herramientas | Qué puede pedir el modelo: `ver_esquema` y `consultar` |
| 2. Ejecutar | `ejecutar()`: corre la herramienta en solo lectura |
| 3. El bucle | `agente()`: pregunta → herramientas → resultado → repite |
| 4. Línea de comandos | Crea `tienda.db` si no existe y lanza el agente |

## Tres detalles que importan

- **Solo lectura:** la base se abre con `mode=ro`, así que el agente no puede modificar datos aunque lo intente.
- **Tope de vueltas:** como máximo 10 vueltas, para que nunca quede en un bucle infinito.
- **Los errores vuelven al modelo:** si una consulta falla, el agente recibe el error y puede corregir su SQL.

