#!/usr/bin/env python3
"""
Helper script to run the database lock fixer tool in different ways
"""

import os
import sys
import subprocess
import logging


def main():
    """Run the database lock fixer tool"""
    print("Database Lock Fixer Tool Runner")
    print("===============================")

    # Configure root logger to show all messages
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,  # Override any existing configuration
    )

    # First, ensure we can import the fix_db_lock module
    try:
        from locavox.tools import fix_db_lock

        print("✅ Successfully imported fix_db_lock module")

        # Make sure the fix_db_lock logger is set to INFO level
        fix_db_lock_logger = logging.getLogger("db_lock_fixer")
        fix_db_lock_logger.setLevel(logging.INFO)

        # Make sure handler exists and passes messages through
        if not fix_db_lock_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            fix_db_lock_logger.addHandler(handler)

        # Print current logger status
        print(f"Logger level: {fix_db_lock_logger.level}")
        print(f"Logger propagate: {fix_db_lock_logger.propagate}")
        print(f"Logger handlers: {len(fix_db_lock_logger.handlers)}")
    except ImportError as e:
        print(f"❌ Could not import fix_db_lock module: {e}")
        print("Try running this script from the project root directory")
        return 1

    # Get the module path for direct execution
    module_path = os.path.abspath(fix_db_lock.__file__)
    print(f"Module path: {module_path}")

    # Different ways to run the tool
    methods = [
        {
            "name": "Using direct invocation",
            "cmd": lambda args: subprocess.run(
                [sys.executable, module_path] + args,
                check=True,
                # Capture outputs to ensure logging is displayed
                text=True,
            ),
            "success_likely": True,
        },
        {
            "name": "Using module import",
            "cmd": lambda args: fix_db_lock.main(),
            "success_likely": True,
        },
    ]

    # Get command line arguments to pass to the tool
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    else:
        # Default to these arguments if none provided
        args = ["--check", "--identify"]

    print(f"Arguments to pass: {args}")

    # Try each method
    success = False
    for method in methods:
        print(f"\nTrying method: {method['name']}")
        try:
            result = method["cmd"](args)
            print(f"✅ Method succeeded: {method['name']}")
            success = True
            break
        except Exception as e:
            print(f"❌ Method failed: {method['name']}")
            print(f"Error: {e}")

            if method["success_likely"]:
                print(
                    "This method should have worked. Something is wrong with the environment or script."
                )

    if not success:
        print("\n❌ All methods failed to run the tool.")
        print("Try running the script directly:")
        print(f"python {module_path} --check --identify")

        # If we couldn't run the tool, provide a direct fallback solution
        print("\nAs a fallback, you can try to fix database locks manually:")
        print("1. Stop all running instances of the application")
        print("2. Find and delete journal files:")

        # Try to locate sqlite files in the project
        sqlite_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".db") or file.endswith(".sqlite"):
                    sqlite_files.append(os.path.join(root, file))

        if sqlite_files:
            print("Found SQLite database files:")
            for db_file in sqlite_files:
                print(f"  - {db_file}")
                # List related journal files
                db_dir = os.path.dirname(db_file)
                db_name = os.path.basename(db_file)
                journal_files = [
                    f"{db_file}-journal",
                    f"{db_file}-wal",
                    f"{db_file}-shm",
                ]
                for jf in journal_files:
                    if os.path.exists(jf):
                        print(f"    Journal file: {jf}")
                        print(f"    Delete with: rm {jf}")

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
