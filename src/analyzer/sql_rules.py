from dataclasses import dataclass
from typing import List, Dict
import sqlglot
from sqlglot import parse_one, exp


@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    detail: Dict


SEV_INFO="INFO"; SEV_WARN="WARN"; SEV_ERR="ERROR"


def diagnose(query: str) -> List[Finding]:
    try:
        tree = parse_one(query)
    except Exception as e:
        return [Finding("parse_error", SEV_ERR, f"No se pudo parsear SQL: {e}", {})]


    findings: List[Finding] = []


    # 1) SELECT *
    for sel in tree.find_all(exp.Select):
        if any(isinstance(p, exp.Star) for p in sel.expressions):
            findings.append(Finding(
            "select_star", SEV_WARN,
            "SELECT * detectado: especifica columnas para reducir ancho y E/S",
            {}
        ))


    # 2) LIKE '%...'
    for like in tree.find_all(exp.Like):
        pat = like.args.get("expression")
        esc = like.args.get("this")
        # patrón literal con wildcard inicial
        if isinstance(pat, exp.Literal) and pat.this.startswith("%"):
            findings.append(Finding(
                "leading_wildcard", SEV_WARN,
                "LIKE con comodín inicial ('%texto'): no sargable y rompe índice",
                {"pattern": pat.this}
            ))


    # 3) Función sobre columna en WHERE: LOWER(col) = ...
    for where in tree.find_all(exp.Where):
        for f in where.find_all(exp.Func):
            findings.append(Finding(
                "function_in_predicate", SEV_WARN,
                "Función en predicado WHERE puede impedir uso de índice (ej. LOWER(col))",
                {"func": f.sql()}
            ))


    # 4) ORDER BY no indexado (heurística superficial)
    # Nota: sin estadísticas/índices reales, solo avisamos.
    ob = next(tree.find_all(exp.Order), None)
    if ob:
        findings.append(Finding(
            "order_by_cost", SEV_INFO,
            "ORDER BY puede requerir sort si no existe índice compatible",
            {"order": ob.sql()}
        ))


    # 5) JOIN sin condición (cross join accidental)
    for join in tree.find_all(exp.Join):
        if join.args.get("on") is None and not join.kind == "CROSS":
            findings.append(Finding(
                "join_without_on", SEV_ERR,
                "JOIN sin condición ON: posible producto cartesiano no intencional",
                {"join": join.sql()}
        ))


    return findings