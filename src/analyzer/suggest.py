from typing import List, Dict
from .sql_rules import Finding, SEV_WARN

# Heurísticas mínimas:
# - si hay ORDER BY <col>, sugerir índice en <col>
# - si hay igualdad sobre <col>, sugerir índice en <col>
# - si hay patrón LIKE no sargable sobre email, sugerir columna normalizada + índice compuesto

def suggest_from_findings(findings: List[Finding]) -> List[Dict]:
    suggestions = []
    for f in findings:
        if f.rule == "leading_wildcard":
            suggestions.append({
                "type": "rewrite",
                "message": "Evita LIKE '%texto'. Considera columna normalizada y prefijo 'texto%'",
                "ddl": "-- crear índice en columna normalizada si aplica"
        })
    if f.rule == "order_by_cost":
        suggestions.append({
            "type": "index",
            "message": "Crear índice que cubra ORDER BY para evitar sort",
            "ddl": "-- CREATE INDEX idx_tbl_col ON tabla(col DESC);"
        })
    if f.rule == "function_in_predicate":
        suggestions.append({
            "type": "rewrite",
            "message": "Mover función fuera del predicado (usar columna derivada/persistida)",
            "ddl": "-- ALTER TABLE ... ADD COLUMN col_norm ...; CREATE INDEX ..."
        })
    return suggestions