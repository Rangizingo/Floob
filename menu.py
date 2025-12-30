"""
Right-click context menu for the Desktop Virtual Pet.

Provides options to interact with the pet.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from pet import Pet


class PetMenu:
    """
    Right-click context menu for pet interactions.

    Provides feed, play, sleep, stats, and quit options.
    """

    def __init__(
        self,
        parent: tk.Tk,
        pet: Pet,
        on_feed: Optional[Callable[[], None]] = None,
        on_play: Optional[Callable[[], None]] = None,
        on_sleep: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Initialize the context menu.

        Args:
            parent: Parent Tkinter window.
            pet: Pet instance for stat display.
            on_feed: Callback when Feed is selected.
            on_play: Callback when Play is selected.
            on_sleep: Callback when Sleep is selected.
            on_quit: Callback when Quit is selected.
        """
        self.parent = parent
        self.pet = pet
        self.on_feed = on_feed
        self.on_play = on_play
        self.on_sleep = on_sleep
        self.on_quit = on_quit

        self._create_menu()

    def _create_menu(self) -> None:
        """Create the context menu."""
        self.menu = tk.Menu(self.parent, tearoff=0)

        # Pet name as header (disabled)
        self.menu.add_command(
            label=f"-- {self.pet.name} --",
            state=tk.DISABLED
        )
        self.menu.add_separator()

        # Interaction options
        self.menu.add_command(
            label="Feed",
            command=self._handle_feed
        )
        self.menu.add_command(
            label="Play",
            command=self._handle_play
        )
        self.menu.add_command(
            label="Sleep",
            command=self._handle_sleep
        )

        self.menu.add_separator()

        # Stats option
        self.menu.add_command(
            label="Stats",
            command=self._show_stats
        )

        self.menu.add_separator()

        # Quit option
        self.menu.add_command(
            label="Quit",
            command=self._handle_quit
        )

    def show(self, x: int, y: int) -> None:
        """
        Display the context menu at the given position.

        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
        """
        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def _handle_feed(self) -> None:
        """Handle Feed menu selection."""
        if self.on_feed:
            self.on_feed()

    def _handle_play(self) -> None:
        """Handle Play menu selection."""
        if self.pet.stats.energy < 10:
            messagebox.showinfo(
                "Too Tired",
                f"{self.pet.name} is too tired to play!\nLet them rest first."
            )
            return

        if self.on_play:
            self.on_play()

    def _handle_sleep(self) -> None:
        """Handle Sleep menu selection."""
        if self.on_sleep:
            self.on_sleep()

    def _handle_quit(self) -> None:
        """Handle Quit menu selection."""
        if self.on_quit:
            self.on_quit()

    def _show_stats(self) -> None:
        """Display pet stats in a dialog."""
        mood = self.pet.get_mood()

        # Create stat bars
        def make_bar(value: float) -> str:
            filled = int(value / 10)
            empty = 10 - filled
            return "[" + "#" * filled + "-" * empty + "]"

        stats_text = f"""
{self.pet.name}'s Stats

Hunger:    {make_bar(self.pet.stats.hunger)} {self.pet.stats.hunger:.0f}%
Happiness: {make_bar(self.pet.stats.happiness)} {self.pet.stats.happiness:.0f}%
Energy:    {make_bar(self.pet.stats.energy)} {self.pet.stats.energy:.0f}%

Current Mood: {mood.name.title()}
"""

        # Add warnings
        warnings = []
        if self.pet.is_hungry():
            warnings.append("Your pet is hungry!")
        if self.pet.is_tired():
            warnings.append("Your pet is tired!")
        if self.pet.is_sad():
            warnings.append("Your pet is sad!")

        if warnings:
            stats_text += "\nWarnings:\n" + "\n".join(f"- {w}" for w in warnings)

        messagebox.showinfo("Pet Stats", stats_text.strip())

    def update_pet_name(self, name: str) -> None:
        """
        Update the pet name displayed in menu.

        Args:
            name: New pet name.
        """
        self.menu.entryconfig(0, label=f"-- {name} --")
