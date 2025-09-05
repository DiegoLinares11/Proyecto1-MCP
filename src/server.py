import os
import json
import typer
from typing import Optional
from .adapters.sqlite_adapter import SQLiteAdapter
from .analyzer.sql_rules import diagnose
from .analyzer.suggest import suggest_from_findings
from .utils.formatting import table


app = typer.Typer(help="SQLScout Server — CLI demo y stub MCP")

DB_PATH: Optional[str] = None

@app.callback()
def main(db: Optional[str] = typer.Option(None, help="Ruta al archivo SQLite (default: sqlscout.db)")):
    """
    Permite elegir la BD por línea de comandos con --db.
    """
    global DB_PATH
    DB_PATH = db or "sqlscout.db"

def get_adapter() -> SQLiteAdapter:
    return SQLiteAdapter(DB_PATH or "sqlscout.db")

@app.command()
def load(schema_path: str):
    """Carga un esquema SQL en SQLite persistente."""
    adapter = get_adapter()
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    adapter.load_schema(schema)
    typer.echo(f"Esquema cargado en SQLite → {DB_PATH}")


@app.command()
def explain(query: str):
    """Muestra EXPLAIN QUERY PLAN (SQLite)."""
    adapter = get_adapter()
    plan = adapter.explain(query)
    typer.echo(table(plan))


@app.command()
def diagnose_cmd(query: str):
    """Aplica reglas estáticas (sqlglot)."""
    findings = [f.__dict__ for f in diagnose(query)]
    typer.echo(table(findings, headers=["rule","severity","message","detail"]))


@app.command()
def optimize(
    query: str,
    create_index: Optional[str] = typer.Option(None, help="DDL para crear índice y comparar plan antes/después"),
):
    """
    Diagnóstico estático + (opcional) crear índice y comparar plan antes/después.
    """
    adapter = get_adapter()

    # Diagnóstico estático
    findings = diagnose(query)
    sugg = suggest_from_findings(findings)

    typer.echo("# Diagnóstico")
    typer.echo(table([f.__dict__ for f in findings], headers=["rule","severity","message","detail"]))

    typer.echo("\n# Sugerencias")
    typer.echo(table(sugg, headers=["type","message","ddl"]))

    if not create_index:
        return

    # Comparación de plan
    typer.echo("\n# Comparación de plan (antes → después)")
    plan_before = adapter.explain(query)

    # Aplicar índice
    adapter.create_index(create_index)

    plan_after = adapter.explain(query)

    # Mostrar comparación
    def simplify(plan_rows):
        # SQLite devuelve columnas: id, parent, notused, detail
        return [row["detail"] for row in plan_rows]

    rows = []
    before = simplify(plan_before)
    after = simplify(plan_after)
    maxlen = max(len(before), len(after))
    for i in range(maxlen):
        rows.append({
            "before": before[i] if i < len(before) else "",
            "after":  after[i]  if i < len(after)  else "",
        })
    typer.echo(table(rows, headers=["before", "after"]))



# === Stub MCP (JSON-RPC por stdin/stdout) ===
# Deja listo el esqueleto para conectar con el SDK oficial sin cambiar lógica.
@app.command()
def mcp_stdio():
    """Sirve JSON-RPC simple por stdin/stdout (stub de MCP)."""
    import sys
    for line in sys.stdin:
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {})
            if method == "sql.load":
                adapter.load_schema(params.get("schema", ""))
                res = {"ok": True}
            elif method == "sql.explain":
                res = adapter.explain(params["query"])
            elif method == "sql.diagnose":
                res = [f.__dict__ for f in diagnose(params["query"])]
            elif method == "sql.optimize":
                findings = diagnose(params["query"])
                res = {"findings": [f.__dict__ for f in findings], "suggestions": suggest_from_findings(findings)}
            else:
                res = {"error": f"Método no soportado: {method}"}
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":req.get("id"),"result":res})+"\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)})+"\n")
            sys.stdout.flush()


if __name__ == "__main__":
    app()