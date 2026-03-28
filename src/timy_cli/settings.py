import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".local/share/timy/settings.json"

DEFAULT_SETTINGS = {
    "MainZone": "local",
    "TimeZone1": "local",
    "TimeZone2": "UTC",
    "TimeZone3": "America/New_York",
    "TimeZone4": "Europe/London",
    "stretch_x": True
}



def load_or_create_settings():
    if not os.path.exists(CONFIG_FILE):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4) # Create file with defaults
        return DEFAULT_SETTINGS
    else:
        with open(CONFIG_FILE, 'r') as f:
            user_settings = json.load(f) # Load user settings

        # Merge user settings with defaults (user settings take precedence)
        settings = DEFAULT_SETTINGS.copy()
        settings.update(user_settings)
        return settings
