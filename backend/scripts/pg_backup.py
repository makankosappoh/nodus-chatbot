"""
scripts/pg_backup.py
--------------------
Creates a full PostgreSQL database backup using pg_dump.
Output is a .sql file that can restore the entire database.

Run from backend/ directory:
    python scripts/pg_backup.py

Requires pg_dump to be installed (comes with PostgreSQL).
Output saved to: backend/exports/
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings

EXPORT_DIR = Path(__file__).parent.parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d_%H-%M")

def parse_db_url(url):
    """Extract connection details from DATABASE_URL."""
    parsed = urlparse(url)
    return {
        "host":     parsed.hostname,
        "port":     str(parsed.port or 5432),
        "user":     parsed.username,
        "password": parsed.password,
        "dbname":   parsed.path.lstrip("/"),
    }

def run_backup():
    db = parse_db_url(settings.database_url)
    output_file = EXPORT_DIR / f"nodus_chatbot_backup_{TODAY}.sql"

    print("\nNodus Decoded — PostgreSQL Database Backup")
    print(f"Database : {db['dbname']}")
    print(f"Host     : {db['host']}")
    print(f"Output   : {output_file}\n")

    # Set password in environment so pg_dump doesn't prompt
    env = os.environ.copy()
    env["PGPASSWORD"] = db["password"]

    command = [
        "pg_dump",
        "-h", db["host"],
        "-p", db["port"],
        "-U", db["user"],
        "-d", db["dbname"],
        "--no-password",
        "--clean",         
        "--if-exists",      
        "--format=plain",   
        "-f", str(output_file),
    ]

    result = subprocess.run(command, env=env, capture_output=True, text=True)
    if result.returncode == 0:
        size = output_file.stat().st_size / 1024
        print(f"✅ Backup complete — {size:.1f} KB")
        print(f"   Saved to: {output_file}")
        print(f"\nTo restore this backup run:")
        print(f"   psql -h {db['host']} -U {db['user']} -d {db['dbname']} -f {output_file.name}")
    else:
        print(f"❌ Backup failed")
        print(f"   Error: {result.stderr}")


if __name__ == "__main__":
    run_backup()