"""
Run all SQL files against a fresh SQLite database built from local CSVs.

Outputs:
- data/chd_analytics.db
- sql/results/*_result.csv
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import re

import pandas as pd

import _bootstrap_path  # noqa: F401
from chd_analytics.paths import MART_CLEANED, ROOT, TABLES

DB_PATH = ROOT / "data" / "chd_analytics.db"
SQL_DIR = ROOT / "sql"
RESULTS_DIR = SQL_DIR / "results"


def table_name_for_csv(path: Path) -> str:
    name = path.stem
    if name == "patients(Main Table)":
        name = "patients"
    return "stg_" + "".join(ch if ch.isalnum() else "_" for ch in name).strip("_").lower()


def load_tables(conn: sqlite3.Connection) -> None:
    pd.read_csv(MART_CLEANED).to_sql("mart_delay_scored_cleaned", conn, if_exists="replace", index=False)
    for path in sorted(TABLES.glob("*.csv")):
        pd.read_csv(path).to_sql(table_name_for_csv(path), conn, if_exists="replace", index=False)


def result_query(sql_text: str) -> str:
    """Return the final SELECT statement from a SQL file."""
    text = sql_text.lstrip("\ufeff")
    statements = [stmt.strip() for stmt in re.split(r";\s*(?:\r?\n|$)", text) if stmt.strip()]
    select_statements = [stmt for stmt in statements if "select" in stmt.lower()]
    if not select_statements:
        raise ValueError("No SELECT statement found")
    return select_statements[-1]


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as conn:
        load_tables(conn)
        for sql_path in sorted(SQL_DIR.glob("*.sql")):
            query = result_query(sql_path.read_text(encoding="utf-8"))
            result = pd.read_sql_query(query, conn)
            out_path = RESULTS_DIR / f"{sql_path.stem}_result.csv"
            result.to_csv(out_path, index=False)
            print(f"Wrote {out_path}")

    print(f"Built SQLite database -> {DB_PATH}")


if __name__ == "__main__":
    main()
