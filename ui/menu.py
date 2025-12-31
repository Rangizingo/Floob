"""
Floob 2.0 Context Menu.

Redesigned right-click context menu with evolution-aware features.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional, Dict, List

from core.config import Colors


class PetMenu:
    """
    Right-click context menu for pet interactions.

    Menu structure:
    - Pet Name (Form) - header
    - ---
    - Feed - (+hunger, +XP)
    - Play - (+happiness, +XP, -energy)
    - Sleep/Wake - Toggle sleep state
    - ---
    - Stats - Open stats dialog
    - Evolution History - Show evolution timeline
    - ---
    - Settings submenu:
      - Auto-Care: ON/OFF toggle
    - ---
    - Quit - Save and exit
    """

    def __init__(
        self,
        parent: tk.Tk,
        pet_name: str = "Pet",
        form_name: str = "",
        auto_care_enabled: bool = True,
        is_sleeping: bool = False,
        on_feed: Optional[Callable[[], None]] = None,
        on_play: Optional[Callable[[], None]] = None,
        on_sleep: Optional[Callable[[], None]] = None,
        on_wake: Optional[Callable[[], None]] = None,
        on_stats: Optional[Callable[[], None]] = None,
        on_evolution_history: Optional[Callable[[], None]] = None,
        on_auto_care_toggle: Optional[Callable[[bool], None]] = None,
        on_settings: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the context menu.

        Args:
            parent: Parent Tkinter window.
            pet_name: Pet's name.
            form_name: Current evolution form name.
            auto_care_enabled: Whether auto-care is enabled.
            is_sleeping: Whether pet is currently sleeping.
            on_feed: Callback when Feed is selected.
            on_play: Callback when Play is selected.
            on_sleep: Callback when Sleep is selected.
            on_wake: Callback when Wake is selected.
            on_stats: Callback when Stats is selected.
            on_evolution_history: Callback when Evolution History is selected.
            on_auto_care_toggle: Callback when auto-care is toggled (receives new state).
            on_settings: Callback when Settings is selected.
            on_quit: Callback when Quit is selected.
        """
        self.parent = parent
        self.pet_name = pet_name
        self.form_name = form_name
        self.auto_care_enabled = auto_care_enabled
        self.is_sleeping = is_sleeping

        # Callbacks
        self.on_feed = on_feed
        self.on_play = on_play
        self.on_sleep = on_sleep
        self.on_wake = on_wake
        self.on_stats = on_stats
        self.on_evolution_history = on_evolution_history
        self.on_auto_care_toggle = on_auto_care_toggle
        self.on_settings = on_settings
        self.on_quit = on_quit

        self._create_menu()

    def _create_menu(self) -> None:
        """Create the context menu."""
        self.menu = tk.Menu(self.parent, tearoff=0)

        # Pet name and form as header
        header_text = self._get_header_text()
        self.menu.add_command(
            label=header_text,
            state=tk.DISABLED,
            font=("Arial", 10, "bold"),
        )
        self.menu.add_separator()

        # Interaction options
        self.menu.add_command(
            label="\U0001F35E  Feed",  # Bread emoji
            command=self._handle_feed,
        )
        self.menu.add_command(
            label="\U0001F3BE  Play",  # Tennis ball emoji
            command=self._handle_play,
        )

        # Sleep/Wake toggle
        self._sleep_index = self.menu.index(tk.END) + 1
        sleep_label = self._get_sleep_label()
        self.menu.add_command(
            label=sleep_label,
            command=self._handle_sleep_toggle,
        )

        self.menu.add_separator()

        # Stats and Evolution History
        self.menu.add_command(
            label="\U0001F4CA  Stats",  # Chart emoji
            command=self._handle_stats,
        )
        self.menu.add_command(
            label="\U0001F4DC  Evolution History",  # Scroll emoji
            command=self._handle_evolution_history,
        )

        self.menu.add_separator()

        # Settings option (opens full dialog)
        self.menu.add_command(
            label="\U00002699  Settings",  # Gear emoji
            command=self._handle_settings,
        )

        # Quick auto-care toggle submenu
        self.settings_menu = tk.Menu(self.menu, tearoff=0)
        self._auto_care_menu_index = 0
        self.settings_menu.add_command(
            label=self._get_auto_care_label(),
            command=self._handle_auto_care_toggle,
        )
        self.menu.add_cascade(
            label="\U0001F504  Quick Toggle",  # Refresh emoji
            menu=self.settings_menu,
        )

        self.menu.add_separator()

        # Quit option
        self.menu.add_command(
            label="\U0001F6AA  Quit",  # Door emoji
            command=self._handle_quit,
        )

    def _get_header_text(self) -> str:
        """Get the header text showing pet name and form."""
        if self.form_name:
            return f"-- {self.pet_name} ({self.form_name}) --"
        return f"-- {self.pet_name} --"

    def _get_sleep_label(self) -> str:
        """Get the label for sleep/wake toggle."""
        if self.is_sleeping:
            return "\U0001F31E  Wake"  # Sun emoji
        return "\U0001F4A4  Sleep"  # ZZZ emoji

    def _get_auto_care_label(self) -> str:
        """Get the label for auto-care toggle."""
        status = "ON" if self.auto_care_enabled else "OFF"
        checkmark = "\U00002705" if self.auto_care_enabled else "\U0000274C"  # Check or X
        return f"Auto-Care: {status} {checkmark}"

    def show(self, x: int, y: int) -> None:
        """
        Display the context menu at the given position.

        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
        """
        # Update dynamic menu items before showing
        self._update_menu_state()

        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def _update_menu_state(self) -> None:
        """Update menu items to reflect current state."""
        # Update header
        self.menu.entryconfig(0, label=self._get_header_text())

        # Update sleep/wake label
        self.menu.entryconfig(self._sleep_index, label=self._get_sleep_label())

        # Update auto-care label
        self.settings_menu.entryconfig(
            self._auto_care_menu_index,
            label=self._get_auto_care_label()
        )

    def update_pet_info(
        self,
        pet_name: Optional[str] = None,
        form_name: Optional[str] = None,
        is_sleeping: Optional[bool] = None,
        auto_care_enabled: Optional[bool] = None,
    ) -> None:
        """
        Update pet information displayed in menu.

        Args:
            pet_name: New pet name (if changed).
            form_name: New form name (if changed).
            is_sleeping: New sleep state (if changed).
            auto_care_enabled: New auto-care state (if changed).
        """
        if pet_name is not None:
            self.pet_name = pet_name
        if form_name is not None:
            self.form_name = form_name
        if is_sleeping is not None:
            self.is_sleeping = is_sleeping
        if auto_care_enabled is not None:
            self.auto_care_enabled = auto_care_enabled

    def _handle_feed(self) -> None:
        """Handle Feed menu selection."""
        if self.on_feed:
            self.on_feed()

    def _handle_play(self) -> None:
        """Handle Play menu selection."""
        if self.on_play:
            self.on_play()

    def _handle_sleep_toggle(self) -> None:
        """Handle Sleep/Wake toggle."""
        if self.is_sleeping:
            if self.on_wake:
                self.on_wake()
            self.is_sleeping = False
        else:
            if self.on_sleep:
                self.on_sleep()
            self.is_sleeping = True

    def _handle_stats(self) -> None:
        """Handle Stats menu selection."""
        if self.on_stats:
            self.on_stats()

    def _handle_evolution_history(self) -> None:
        """Handle Evolution History menu selection."""
        if self.on_evolution_history:
            self.on_evolution_history()

    def _handle_settings(self) -> None:
        """Handle Settings menu selection."""
        if self.on_settings:
            self.on_settings()

    def _handle_auto_care_toggle(self) -> None:
        """Handle auto-care toggle."""
        self.auto_care_enabled = not self.auto_care_enabled

        if self.on_auto_care_toggle:
            self.on_auto_care_toggle(self.auto_care_enabled)

        # Show confirmation
        status = "enabled" if self.auto_care_enabled else "disabled"
        messagebox.showinfo(
            "Auto-Care",
            f"Auto-care has been {status}.\n\n"
            f"When enabled, {self.pet_name} will automatically eat, "
            f"play, and sleep when stats get low."
        )

    def _handle_quit(self) -> None:
        """Handle Quit menu selection."""
        if self.on_quit:
            self.on_quit()
