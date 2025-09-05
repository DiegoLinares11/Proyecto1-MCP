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

2. Ver plan de ejecución (EXPLAIN)

Muestra el plan de ejecución de una consulta usando SQLite:
```bash
python -m src.server --db sqlscout.db explain "SELECT * FROM orders ORDER BY created_at DESC"
```
Ejemplo de salida:

```bash
|   id | parent | notused | detail                                           |
|------|--------|---------|--------------------------------------------------|
|    4 |      0 |       0 | SCAN TABLE orders USING INDEX idx_orders_created |
```

3. Diagnóstico con reglas estáticas

Analiza la consulta con reglas estáticas (independientes del motor de BD):
```bash
python -m src.server --db sqlscout.db diagnose-cmd "SELECT * FROM orders WHERE LOWER(email) LIKE '%gmail.com' ORDER BY created_at DESC"
```
Ejemplo de salida:
```bash
| rule                  | severity | message                                                                 | detail                                |
|-----------------------|----------|-------------------------------------------------------------------------|---------------------------------------|
| select_star           | WARN     | SELECT * detectado: especifica columnas para reducir ancho y E/S        | {}                                    |
| leading_wildcard      | WARN     | LIKE con comodín inicial ('%texto'): no sargable y rompe índice         | {'pattern': '%gmail.com'}             |
| function_in_predicate | WARN     | Función en predicado WHERE puede impedir uso de índice (ej. LOWER(col)) | {'func': 'LOWER(email)'}              |
| order_by_cost         | INFO     | ORDER BY puede requerir sort si no existe índice compatible             | {'order': 'ORDER BY created_at DESC'} |
```

4. Optimización (antes y después)

Ejecuta diagnóstico + sugerencias y aplica un índice para comparar el plan antes y después:
```bash
python -m src.server --db sqlscout.db optimize "SELECT * FROM orders ORDER BY created_at DESC" --create-index "CREATE INDEX idx_orders_created ON orders(created_at DESC)"
```

Ejemplo de salida:
```bash
# Diagnóstico
| rule        | severity | message                                                          | detail                                |
|-------------|----------|------------------------------------------------------------------|---------------------------------------|
| select_star | WARN     | SELECT * detectado: especifica columnas para reducir ancho y E/S | {}                                    |
| order_by... | INFO     | ORDER BY puede requerir sort si no existe índice compatible      | {'order': 'ORDER BY created_at DESC'} |

# Sugerencias
| type  | message                                          | ddl                                             |
|-------|--------------------------------------------------|-------------------------------------------------|
| index | Crear índice que cubra ORDER BY para evitar sort | -- CREATE INDEX idx_tbl_col ON tabla(col DESC); |

# Comparación de plan (antes → después)
| before                       | after                                           |
|------------------------------|-------------------------------------------------|
| SCAN TABLE orders            | SCAN TABLE orders USING INDEX idx_orders_created|
| USE TEMP B-TREE FOR ORDER BY |                                                 |
```

Modo MCP (stub JSON-RPC)

El servidor también puede correr en modo MCP stdio (para conectarse a un host MCP):
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"sql.diagnose","params":{"query":"SELECT * FROM orders"}}' | python -m src.server mcp-stdio
```
Ejemplo de salida:
```bash
{"jsonrpc":"2.0","id":1,"result":[{"rule":"select_star","severity":"WARN","message":"SELECT * detectado","detail":{}}]}
```
Esto permite integrarlo con cualquier cliente MCP que hable JSON-RPC por stdin/stdout.

Funcionalidades soportadas

1. sql.load(schema_path)

  Carga un esquema SQL en SQLite.

  Persiste en un archivo .db.

2. sql.explain(query)

  Devuelve el plan de ejecución estimado (EXPLAIN QUERY PLAN).

3. sql.diagnose(query)

  Aplica reglas estáticas:

  SELECT *

  LIKE '%texto'

  Función en WHERE (ej. LOWER(col))

  ORDER BY sin índice

  JOIN sin condición

4. sql.optimize(query, create_index)

  Combina diagnóstico + sugerencias.

  Permite aplicar un índice (--create-index) y compara plan antes vs después.

