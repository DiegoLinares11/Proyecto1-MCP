# SQLScout MCP (MVP)


## Requisitos
- Python 3.10+


```bash
pip install -r requirements.txt
```
Uso (CLI demo)
```bash
python -m src.server load examples/demo_schema.sql
python -m src.server explain "SELECT * FROM orders ORDER BY created_at DESC"
python -m src.server diagnose-cmd "SELECT * FROM orders WHERE LOWER(email) LIKE '%gmail.com'"
python -m src.server optimize "SELECT * FROM orders ORDER BY created_at DESC" --create-index "CREATE INDEX idx_orders_created ON orders(created_at DESC)"
```
