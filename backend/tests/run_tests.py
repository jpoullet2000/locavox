#!/usr/bin/env python3
import pytest
import os
import sys
import warnings


def run_tests():
    """Run tests with RuntimeWarnings as errors to catch unhandled coroutines"""

    # Make RuntimeWarnings errors by default to catch coroutine issues
    warnings.filterwarnings("error", category=RuntimeWarning)

    # Adjust paths for imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Environment setup for tests
    os.environ["LOCAVOX_LOG_LEVEL"] = "DEBUG"  # Set higher log level for tests

    # Run pytest with common options
    args = [
        "-xvs",  # Exit on first failure, verbose, don't capture output
        "--asyncio-mode=auto",  # Handle asyncio properly
    ]

    # Add any command line arguments
    args.extend(sys.argv[1:])

    print(f"Running tests with args: {args}")
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_tests())
