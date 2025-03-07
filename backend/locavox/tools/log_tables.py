#!/usr/bin/env python3
"""
Tool to log all tables in the database with their columns and constraints.
Useful for confirming that all expected tables have been created properly.
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add the parent directory to sys.path to import modules from the main application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import inspect, text
from locavox.database import engine, init_db
from locavox.logger import setup_logger

logger = setup_logger(__name__)


async def log_tables(
    verbose: bool = False, show_data: bool = False, rows_limit: int = 5
):
    """
    Log information about all tables in the database.

    Args:
        verbose: If True, show detailed information about columns and constraints
        show_data: If True, show sample data from each table
        rows_limit: Maximum number of rows to show when show_data is True
    """
    try:
        # Initialize the database
        await init_db()

        # Create a connection to the database
        async with engine.connect() as connection:
            # Get table names using run_sync with a function that uses inspect
            def get_table_info(conn):
                inspector = inspect(conn)
                return {"tables": inspector.get_table_names(), "inspector": inspector}

            table_info = await connection.run_sync(get_table_info)
            table_names = table_info["tables"]

            if not table_names:
                logger.info("No tables found in the database.")
                return True

            logger.info(f"Found {len(table_names)} tables in the database:")

            for table_name in sorted(table_names):
                logger.info(f"  • {table_name}")

                if verbose:
                    # Get columns
                    def get_table_details(conn, tbl_name=table_name):
                        inspector = inspect(conn)
                        return {
                            "columns": inspector.get_columns(tbl_name),
                            "pk": inspector.get_pk_constraint(tbl_name),
                            "fks": inspector.get_foreign_keys(tbl_name),
                        }

                    details = await connection.run_sync(get_table_details)

                    # Show columns
                    columns = details["columns"]
                    logger.info(f"    Columns ({len(columns)}):")
                    for column in columns:
                        nullable = "NULL" if column["nullable"] else "NOT NULL"
                        default = (
                            f"DEFAULT {column['default']}"
                            if column.get("default") is not None
                            else ""
                        )
                        logger.info(
                            f"      - {column['name']}: {column['type']} {nullable} {default}"
                        )

                    # Show primary key
                    pk = details["pk"]
                    if pk and pk.get("constrained_columns"):
                        logger.info(
                            f"    Primary Key: {', '.join(pk['constrained_columns'])}"
                        )

                    # Show foreign keys
                    fks = details["fks"]
                    if fks:
                        logger.info(f"    Foreign Keys ({len(fks)}):")
                        for fk in fks:
                            src_cols = ", ".join(fk["constrained_columns"])
                            ref_cols = ", ".join(fk["referred_columns"])
                            logger.info(
                                f"      - {src_cols} -> {fk['referred_table']}.{ref_cols}"
                            )

                # Show sample data if requested
                if show_data:
                    try:
                        query = text(f"SELECT * FROM {table_name} LIMIT {rows_limit}")
                        result = await connection.execute(query)
                        rows = result.fetchall()

                        if rows:
                            logger.info(
                                f"    Sample Data ({min(len(rows), rows_limit)} rows):"
                            )
                            for row in rows:
                                logger.info(f"      - {dict(row)}")
                        else:
                            logger.info("    Table is empty")
                    except Exception as e:
                        logger.error(f"    Error fetching sample data: {str(e)}")

    except Exception as e:
        logger.error(f"Failed to log database tables: {str(e)}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Log database tables and their structure"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed information about columns and constraints",
    )
    parser.add_argument(
        "--data", "-d", action="store_true", help="Show sample data from each table"
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=5,
        help="Maximum number of rows to show per table",
    )

    args = parser.parse_args()

    success = asyncio.run(
        log_tables(verbose=args.verbose, show_data=args.data, rows_limit=args.limit)
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
