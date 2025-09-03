from tabulate import tabulate
from typing import List, Dict


def table(rows: List[Dict], headers: "list[str] | None" = None) -> str:
    if not rows:
        return "(sin filas)"
    if headers is None:
        headers = list(rows[0].keys())
    data = [[r.get(h, "") for h in headers] for r in rows]
    return tabulate(data, headers=headers, tablefmt="github")