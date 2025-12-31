"""
Floob 2.0 UI Module.

Contains the user interface components:
- window: Main transparent overlay window
- menu: Right-click context menu with all interactions
- dialogs: Stats dialog, Evolution History dialog, Evolution Notification, Settings
"""

from ui.window import PetWindow
from ui.menu import PetMenu
from ui.dialogs import (
    StatsDialog,
    EvolutionHistoryDialog,
    EvolutionNotificationDialog,
    SettingsDialog,
)

__all__ = [
    "PetWindow",
    "PetMenu",
    "StatsDialog",
    "EvolutionHistoryDialog",
    "EvolutionNotificationDialog",
    "SettingsDialog",
]
