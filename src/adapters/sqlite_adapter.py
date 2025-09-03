import sqlite3
from typing import List, Tuple, Dict, Any, Optional


class SQLiteAdapter:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row


    def load_schema(self, schema_sql: str):
        cur = self.conn.cursor()
        cur.executescript(schema_sql)
        self.conn.commit()


    def explain(self, query: str) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(f"EXPLAIN QUERY PLAN {query}")
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


    def run(self, query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
        cur = self.conn.cursor()
        cur.execute(query)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return cols, rows


    def create_index(self, ddl: str):
        cur = self.conn.cursor()
        cur.execute(ddl)
        self.conn.commit()