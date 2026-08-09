import os

# Ensure external pytest plugins (e.g., ROS launch testing) are not auto‑loaded.
# This must be set before pytest starts importing plugins.
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
