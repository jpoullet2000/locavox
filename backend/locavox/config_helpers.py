"""Helper functions for configuration management, especially for testing"""

from . import config

# Use a simple global dict for test overrides instead of thread-local storage
# This is more reliable across test scenarios with FastAPI's TestClient
_test_values = {}


def set_test_value(key, value):
    """Set a configuration value specifically for tests"""
    global _test_values
    _test_values[key] = value

    # Directly update the config module's attribute as well for maximum compatibility
    if hasattr(config, key):
        setattr(config, key, value)


def get_message_limit():
    """Get the message limit, respecting test overrides if present"""
    # Check for an override first
    if "MAX_MESSAGES_PER_USER" in _test_values:
        return _test_values["MAX_MESSAGES_PER_USER"]

    # Otherwise use the config value
    return config.MAX_MESSAGES_PER_USER


def reset_test_values():
    """Reset all test configuration values"""
    global _test_values
    # Store the keys to reset in config module
    keys_to_reset = list(_test_values.keys())

    # Clear the test values dictionary
    _test_values.clear()

    # Reset any directly modified config attributes
    # (Note: This requires knowing the original values)
    # For now, just set MAX_MESSAGES_PER_USER back to its default
    if "MAX_MESSAGES_PER_USER" in keys_to_reset:
        config.MAX_MESSAGES_PER_USER = 100  # Default value
