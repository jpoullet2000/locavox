#!/usr/bin/env python3

from pathlib import Path
import re
import shutil


def update_imports():
    """
    Update imports in the main.py file to consistently use locavox.routers
    instead of locavox.endpoints.
    """
    backend_dir = Path("/home/jbp/projects/locavox/backend")
    main_file = backend_dir / "main.py"

    if not main_file.exists():
        print(f"Error: Main file {main_file} not found.")
        return

    # Create a backup of the main file
    backup_file = main_file.with_suffix(".py.bak")
    print(f"Creating backup of {main_file} at {backup_file}")
    shutil.copy2(main_file, backup_file)

    # Read the content of the main file
    with open(main_file, "r") as f:
        content = f.read()

    # Update the import statement
    updated_content = re.sub(
        r"from locavox\.endpoints import (.*)",
        r"from locavox.routers import \1  # Updated import path",
        content,
    )

    # Write the updated content back to the file
    with open(main_file, "w") as f:
        f.write(updated_content)

    print(f"Updated imports in {main_file}")
    print("\nIMPORTANT STEPS:")
    print(
        "1. Test your application thoroughly to ensure it works with the updated imports"
    )
    print("2. Once verified, you can run the script to remove the endpoints folder")


def remove_endpoints_folder():
    """
    Remove the endpoints folder after confirming that the application works
    with the updated imports.
    """
    endpoints_dir = Path("/home/jbp/projects/locavox/backend/locavox/endpoints")

    if not endpoints_dir.exists():
        print("The endpoints directory does not exist.")
        return

    # Create a backup of the endpoints directory
    backup_dir = Path("/home/jbp/projects/locavox/backend/locavox/endpoints_backup")

    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    print(f"Creating backup of endpoints directory at {backup_dir}")
    shutil.copytree(endpoints_dir, backup_dir)

    # Remove the endpoints directory
    print(f"Removing {endpoints_dir}")
    shutil.rmtree(endpoints_dir)

    print("\nEndpoints directory has been removed.")
    print("The backup is available at:", backup_dir)


if __name__ == "__main__":
    action = input(
        "Select action:\n1. Update imports\n2. Remove endpoints folder\nChoice (1/2): "
    )

    if action == "1":
        update_imports()
    elif action == "2":
        confirm = input(
            "Are you sure you want to remove the endpoints folder? This action cannot be undone. (y/n): "
        )
        if confirm.lower() == "y":
            remove_endpoints_folder()
        else:
            print("Operation cancelled.")
    else:
        print("Invalid choice.")
