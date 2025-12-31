"""
Floob 2.0 Persistence Module.

Handles saving and loading game state, including:
    - Pet stats and state
    - Evolution data (XP, level, form, history)
    - Care tracker data
    - Settings and preferences

Supports migration from older save formats.
"""

from persistence.save_manager import (
    SaveManager,
    SaveData,
    SaveVersion,
    CURRENT_SAVE_VERSION,
    migrate_save,
)

__all__ = [
    "SaveManager",
    "SaveData",
    "SaveVersion",
    "CURRENT_SAVE_VERSION",
    "migrate_save",
]
