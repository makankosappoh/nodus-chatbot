"""
scripts/backup_db.py
--------------------
Exports leads and conversation logs to CSV files.
Run from backend/ directory:
    python scripts/backup_db.py

Output saved to: backend/exports/
"""

import sys
import csv
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from app.core.config import settings

EXPORT_DIR = Path(__file__).parent.parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
ENGINE = create_engine(settings.database_url)


def export(table_name, query, filename):
    with ENGINE.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())

    filepath = EXPORT_DIR / f"{filename}_{TODAY}.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(columns)
        csv.writer(f).writerows(rows)

    print(f" {table_name}: {len(rows)} rows → {filepath}")


def main():
    print("\nNodus Decoded — Database Backup\n")
    export(
        table_name="Leads",
        query="SELECT * FROM leads ORDER BY created_at DESC",
        filename="leads_backup"
    )
    export(
        table_name="Conversation Logs",
        query="SELECT * FROM conversation_logs ORDER BY created_at DESC",
        filename="conversation_logs_backup"
    )
    print("\nDone. Files saved in backend/exports/")


if __name__ == "__main__":
    main()