import os
import sys
import argparse
import sqlite3
import logging
import signal
import psutil
from pathlib import Path

# Set up logging - ensure output goes to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,  # Force configuration to override any existing settings
)
logger = logging.getLogger("db_lock_fixer")
logger.setLevel(logging.INFO)

# Ensure the logger is properly configured
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Make sure the logger propagates to the root logger
logger.propagate = True


def find_db_path():
    """Find the SQLite database file path from the config"""
    try:
        from locavox import config

        # Check different possible configuration variable names
        if hasattr(config, "SQLITE_FILE"):
            db_file = config.SQLITE_FILE
        elif hasattr(config, "DATABASE_FILE"):
            db_file = config.DATABASE_FILE
        else:
            # Try to find database file by inspecting config attributes
            logger.info("Searching for database file in config...")
            for attr in dir(config):
                if attr.upper().endswith("_FILE") and not attr.startswith("__"):
                    value = getattr(config, attr)
                    if isinstance(value, str) and (
                        value.endswith(".db") or value.endswith(".sqlite")
                    ):
                        logger.info(f"Found potential database file: {attr}={value}")
                        db_file = value
                        break
            else:
                # Default fallback if we can't find a specific config variable
                db_file = "locavox.db"
                logger.warning(
                    f"Could not determine database filename from config, using default: {db_file}"
                )

        # Find the database directory
        if hasattr(config, "DATABASE_PATH"):
            db_path = os.path.join(config.DATABASE_PATH, db_file)
        else:
            # Try to find the database in the current directory and parent directories
            current_dir = os.getcwd()
            possible_locations = [
                current_dir,
                os.path.join(current_dir, "data"),
                os.path.join(current_dir, "instance"),
                os.path.dirname(current_dir),
            ]

            for location in possible_locations:
                test_path = os.path.join(location, db_file)
                if os.path.exists(test_path):
                    db_path = test_path
                    logger.info(f"Found database at: {db_path}")
                    break
            else:
                # Default to current directory if not found
                db_path = os.path.join(current_dir, db_file)
                logger.warning(f"Could not find database, will use path: {db_path}")

        logger.info(f"Using database path: {db_path}")
        return db_path
    except ImportError as e:
        logger.error(f"Could not import locavox config: {e}")
        logger.error("Please specify the database path with --db-path parameter")
        return None


def check_db_lock(db_path):
    """Check if the database is locked and try to identify processes holding locks"""
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False

    try:
        # Try to open and immediately close the database in exclusive mode
        logger.info(f"Checking lock status on database: {db_path}")
        conn = sqlite3.connect(db_path, timeout=1)

        # Try to execute PRAGMA query to check lock status
        try:
            conn.execute("PRAGMA query_only = 1;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("SELECT count(*) FROM sqlite_master;")
            logger.info("Database is not locked - able to execute queries")

            # Check for active connections (this isn't perfect but helps)
            locks = conn.execute("PRAGMA lock_status;").fetchall()
            logger.info(f"Current lock status: {locks}")
        except sqlite3.OperationalError as e:
            logger.error(f"Database is locked: {e}")
            return True
        finally:
            conn.close()

        return False
    except Exception as e:
        logger.error(f"Error checking database lock: {e}")
        return True


def identify_locking_processes(db_path):
    """Try to identify processes that might be locking the database"""
    logger.info("Searching for processes with the database file open...")

    # Normalize the path for comparison
    db_path = os.path.abspath(db_path)

    found_processes = []

    # Iterate through all processes
    for proc in psutil.process_iter(["pid", "name", "cmdline", "open_files"]):
        try:
            # Check if this process has the database file open
            open_files = proc.open_files()
            if open_files:
                for file in open_files:
                    if os.path.abspath(file.path) == db_path:
                        proc_info = {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "cmdline": proc.cmdline() if proc.cmdline() else [],
                        }
                        found_processes.append(proc_info)
                        logger.info(
                            f"Found process: PID {proc.pid} - {proc.name()} - {' '.join(proc.cmdline() if proc.cmdline() else [])}"
                        )
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            # Skip processes we can't access
            continue

    if not found_processes:
        logger.info("No processes found with the database file open.")

    return found_processes


def release_lock(db_path, force=False):
    """Try to release the lock on the database"""
    if not force:
        logger.info("Attempting to release lock by optimizing database...")
        try:
            # Try the VACUUM command which might help release locks
            conn = sqlite3.connect(db_path, timeout=5)
            conn.execute("PRAGMA journal_mode = DELETE;")
            conn.execute("VACUUM;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.close()
            logger.info("Database optimized, lock might be released.")
            return True
        except sqlite3.OperationalError as e:
            logger.error(f"Could not VACUUM database: {e}")

    if force:
        logger.warning("Attempting to force release lock by deleting journal files...")
        # Try removing -journal and -wal files
        db_dir = os.path.dirname(db_path)
        db_name = os.path.basename(db_path)

        journal_files = [f"{db_path}-journal", f"{db_path}-wal", f"{db_path}-shm"]

        for jf in journal_files:
            if os.path.exists(jf):
                try:
                    os.remove(jf)
                    logger.info(f"Removed journal file: {jf}")
                except OSError as e:
                    logger.error(f"Could not remove file {jf}: {e}")

        return True

    return False


def kill_locking_processes(processes, force=False):
    """Kill processes that are locking the database"""
    if not processes:
        logger.info("No processes to kill.")
        return

    logger.warning(
        f"Attempting to kill {len(processes)} process(es) locking the database..."
    )

    for proc in processes:
        pid = proc["pid"]
        name = proc["name"]

        if not force:
            logger.info(
                f"Would kill process PID {pid} ({name}) but --force not specified."
            )
            continue

        try:
            # Try SIGTERM first (graceful)
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to PID {pid} ({name})")
        except OSError as e:
            logger.error(f"Failed to terminate process {pid}: {e}")

            if force:
                try:
                    # Try SIGKILL if SIGTERM failed
                    os.kill(pid, signal.SIGKILL)
                    logger.info(f"Sent SIGKILL to PID {pid} ({name})")
                except OSError as e2:
                    logger.error(f"Failed to kill process {pid}: {e2}")


def repair_database(db_path, force=False):
    """Attempt to repair the database if it's corrupted"""
    logger.info(f"Attempting to repair database at {db_path}...")

    # Create a backup first
    backup_path = f"{db_path}.backup"
    try:
        import shutil

        shutil.copy2(db_path, backup_path)
        logger.info(f"Created database backup at {backup_path}")
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        if not force:
            logger.error(
                "Aborting repair due to backup failure. Use --force to override."
            )
            return False

    try:
        # Try to recover the database using the SQLite recovery mode
        logger.info("Attempting database recovery...")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA integrity_check;")
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        conn.execute("VACUUM;")
        conn.close()
        logger.info("Database recovery completed successfully")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database recovery failed: {e}")

        if force:
            logger.warning(
                "Trying more aggressive recovery options due to --force flag..."
            )
            try:
                # Export the schema and data and recreate
                temp_db = f"{db_path}.new"
                if os.path.exists(temp_db):
                    os.remove(temp_db)

                # Create a new database with the same schema
                source_conn = sqlite3.connect(db_path)
                target_conn = sqlite3.connect(temp_db)

                # Get schema from the old database
                schema = source_conn.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table';"
                ).fetchall()

                # Recreate tables in the new database
                for table_sql in schema:
                    if table_sql[0] and not table_sql[0].startswith(
                        "CREATE TABLE sqlite_"
                    ):
                        target_conn.execute(table_sql[0])

                # Copy data table by table
                tables = source_conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
                ).fetchall()

                for table in tables:
                    table_name = table[0]
                    try:
                        data = source_conn.execute(
                            f"SELECT * FROM {table_name};"
                        ).fetchall()
                        if data:
                            # Get column count for this table
                            cols = source_conn.execute(
                                f"PRAGMA table_info({table_name});"
                            ).fetchall()
                            placeholders = ",".join(["?"] * len(cols))

                            # Insert data into new database
                            target_conn.executemany(
                                f"INSERT INTO {table_name} VALUES ({placeholders});",
                                data,
                            )
                    except sqlite3.Error:
                        logger.warning(f"Could not copy data from table {table_name}")

                target_conn.commit()
                source_conn.close()
                target_conn.close()

                # Replace the old database with the new one
                os.rename(db_path, f"{db_path}.corrupted")
                os.rename(temp_db, db_path)

                logger.info(
                    "Database has been recreated from schema and available data"
                )
                return True

            except Exception as deep_e:
                logger.error(f"Deep recovery failed: {deep_e}")
                return False
        return False


def main():
    parser = argparse.ArgumentParser(
        description="SQLite Database Lock Diagnostic and Repair Tool"
    )
    parser.add_argument("--db-path", help="Path to the SQLite database file")
    parser.add_argument(
        "--check", action="store_true", help="Check if the database is locked"
    )
    parser.add_argument(
        "--identify", action="store_true", help="Identify processes holding locks"
    )
    parser.add_argument("--release", action="store_true", help="Try to release locks")
    parser.add_argument(
        "--kill", action="store_true", help="Kill processes holding locks"
    )
    parser.add_argument(
        "--repair", action="store_true", help="Attempt to repair the database"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force operations (use with caution)"
    )

    args = parser.parse_args()

    # Print argument values to verify the script is running with correct parameters
    logger.info(f"Args: {args}")

    # Find the database path if not specified
    db_path = args.db_path or find_db_path()
    if not db_path:
        logger.error("No database path specified and couldn't determine from config.")
        return 1

    if not os.path.exists(db_path):
        logger.error(f"Database file not found at: {db_path}")
        logger.info("Searching for database files in the current directory...")
        db_files = [
            f for f in os.listdir(".") if f.endswith(".db") or f.endswith(".sqlite")
        ]
        if db_files:
            logger.info(f"Found potential database files: {db_files}")
            logger.info(f"Try running the tool with --db-path={db_files[0]}")
        return 1

    logger.info(f"Working with database at: {db_path}")

    # If no specific action is requested, do all checks
    if not any([args.check, args.identify, args.release, args.kill, args.repair]):
        args.check = True
        args.identify = True

    # Check if the database is locked
    if args.check:
        is_locked = check_db_lock(db_path)
        if is_locked:
            logger.warning("Database appears to be locked.")
        else:
            logger.info("Database is not locked.")

    # Identify processes that might be locking the database
    processes = []
    if args.identify:
        processes = identify_locking_processes(db_path)

    # Kill processes if requested
    if args.kill and processes:
        kill_locking_processes(processes, args.force)

    # Try to release the lock
    if args.release:
        release_lock(db_path, args.force)

    # Repair database if requested
    if args.repair:
        repair_database(db_path, args.force)

    # Check the lock status again after operations
    if args.check or args.release or args.kill or args.repair:
        is_locked = check_db_lock(db_path)
        if is_locked:
            logger.warning("Database is still locked after operations.")
        else:
            logger.info("Database is now unlocked!")

    return 0


if __name__ == "__main__":
    try:
        print("Running fix_db_lock as a script...")
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)
