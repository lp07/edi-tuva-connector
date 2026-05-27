import duckdb
import pandas as pd
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)
logger = logging.getLogger(__name__)


def get_db_path():
    return Path(__file__).parent / "dev.duckdb"


def get_source_path():
    source = os.getenv(
        "EDI_SOURCE_PATH",
        str(Path(__file__).parent / "seeds" / "reconciliation_report.csv")
    )
    return Path(source)


def load_reconciliation_report(conn, source_path):
    logger.info(f"Reading source data from {source_path}")

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {source_path}\n"
            "Set the EDI_SOURCE_PATH environment variable to point to your parsed EDI output."
        )

    df = pd.read_csv(source_path)
    logger.info(f"Loaded {len(df)} records from source file")

    conn.execute("CREATE SCHEMA IF NOT EXISTS main_edi_raw")
    conn.execute("DROP TABLE IF EXISTS main_edi_raw.reconciliation_report")
    conn.execute(
        "CREATE TABLE main_edi_raw.reconciliation_report AS SELECT * FROM df"
    )

    count = conn.execute(
        "SELECT COUNT(*) FROM main_edi_raw.reconciliation_report"
    ).fetchone()[0]

    logger.info(f"Loaded {count} records into main_edi_raw.reconciliation_report")


def main():
    db_path = get_db_path()
    source_path = get_source_path()

    logger.info(f"Connecting to DuckDB at {db_path}")

    with duckdb.connect(str(db_path)) as conn:
        load_reconciliation_report(conn, source_path)

    logger.info("Ingestion complete. Run dbt run to build the connector models.")


if __name__ == "__main__":
    main()