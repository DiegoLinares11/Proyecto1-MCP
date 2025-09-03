import os
import typer
from typing import Optional
from .adapters.sqlite_adapter import SQLiteAdapter
from .analyzer.sql_rules import diagnose
from .analyzer.suggest import suggest_from_findings
from .utils.formatting import table


app = typer.Typer(help="SQLScout Server — CLI demo y stub MCP")


# Sesión única en memoria (MVP)
adapter = SQLiteAdapter("sqlscout.db")


@app.command()
def load(schema_path: str):
    """Carga un esquema SQL en SQLite embebido."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    adapter.load_schema(schema)
    typer.echo("Esquema cargado en SQLite (memoria).")


@app.command()
def explain(query: str):
    """Muestra EXPLAIN QUERY PLAN (SQLite)."""
    plan = adapter.explain(query)
    typer.echo(table(plan))


@app.command()
def diagnose_cmd(query: str):
    """Aplica reglas estáticas (sqlglot)."""
    findings = [f.__dict__ for f in diagnose(query)]
    typer.echo(table(findings, headers=["rule","severity","message","detail"]))


@app.command()
def optimize(query: str, create_index: Optional[str] = typer.Option(None, help="DDL opcional para crear índice y comparar")):
    """Diagnóstico + (opcional) índice sugerido y comparación básica."""
    findings = diagnose(query)
    sugg = suggest_from_findings(findings)


    typer.echo("# Diagnóstico")
    typer.echo(table([f.__dict__ for f in findings], headers=["rule","severity","message","detail"]))


    typer.echo("\n# Sugerencias")
    typer.echo(table(sugg, headers=["type","message","ddl"]))


    if create_index:
        adapter.create_index(create_index)
        typer.echo("\n# Índice aplicado. Nuevo plan:")
        plan = adapter.explain(query)
        typer.echo(table(plan))


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