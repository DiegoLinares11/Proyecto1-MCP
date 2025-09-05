# SQLScout MCP 

SQLScout MCP es un servidor MCP local desarrollado en Python que permite analizar y optimizar consultas SQL de manera simple.

El objetivo es ofrecer a un chatbot host (cliente MCP) herramientas para:

  Explicar planes de ejecución (EXPLAIN QUERY PLAN) sobre SQLite.

  Diagnosticar consultas con reglas estáticas (ej. SELECT *, LIKE '%...', funciones en predicados, JOIN sin condición).

  Sugerir optimizaciones (ej. creación de índices, reescrituras de predicados).

  Comparar planes antes y después de aplicar índices sugeridos.

Este servidor es no trivial: encapsula análisis SQL y lógica de optimización básica, y se comunica vía CLI o mediante el protocolo MCP (stub JSON-RPC ya incluido).

### Estructura del repositorio
```bash
mcp-sqlscout-server/
  src/
    server.py                # CLI principal y stub MCP por stdio
    adapters/
      sqlite_adapter.py      # Conexión a SQLite, explain, índices
    analyzer/
      sql_rules.py           # Reglas estáticas de diagnóstico
      suggest.py             # Heurísticas de sugerencias
    utils/
      formatting.py          # Tablas bonitas con tabulate
  examples/
    demo_schema.sql          # Esquema y datos de ejemplo
  requirements.txt           # Dependencias
  README.md                  # Este archivo
```

## Requisitos
- Python 3.10+
Instalar dependencias:
```bash
pip install -r requirements.txt
```
Uso básico
1. Cargar un esquema en SQLite

Carga las tablas y datos de ejemplo en un archivo SQLite (sqlscout.db):

```bash
python -m src.server --db sqlscout.db load examples/demo_schema.sql
```
Salida esperada:
```bash
Esquema cargado en SQLite → sqlscout.db
```


