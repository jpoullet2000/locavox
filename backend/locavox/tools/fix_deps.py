import subprocess
import sys


def fix_bcrypt_issue():
    """Fix the bcrypt/passlib compatibility issue by reinstalling the correct versions."""
    print("Fixing bcrypt/passlib compatibility issue...")

    # Uninstall current versions
    subprocess.check_call(
        [sys.executable, "-m", "pip", "uninstall", "-y", "bcrypt", "passlib"]
    )

    # Install the compatible versions
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "bcrypt==4.0.1", "passlib==1.7.4"]
    )

    print("Dependencies updated successfully!")
    print("Please restart your application for changes to take effect.")


if __name__ == "__main__":
    fix_bcrypt_issue()
