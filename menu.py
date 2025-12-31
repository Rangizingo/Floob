"""
Right-click context menu for the Desktop Virtual Pet.

Provides options to interact with the pet including customization.
"""

import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from typing import Callable, Optional

from pet import (
    Pet, PetCustomization, EarStyle, TailStyle, Accessory, COLOR_PALETTE
)


class CustomizationDialog:
    """
    Dialog for customizing pet appearance.

    Allows user to change body color, ears, tail, and accessories.
    """

    def __init__(
        self,
        parent: tk.Tk,
        pet: Pet,
        on_save: Optional[Callable[[PetCustomization], None]] = None
    ) -> None:
        """
        Initialize customization dialog.

        Args:
            parent: Parent Tkinter window.
            pet: Pet instance to customize.
            on_save: Callback when customization is saved.
        """
        self.parent = parent
        self.pet = pet
        self.on_save = on_save
        self.customization = PetCustomization(
            body_color=pet.customization.body_color,
            ear_style=pet.customization.ear_style,
            tail_style=pet.customization.tail_style,
            accessory=pet.customization.accessory
        )

        self._create_dialog()

    def _create_dialog(self) -> None:
        """Create the customization dialog window."""
        self.dialog = Toplevel(self.parent)
        self.dialog.title(f"Customize {self.pet.name}")
        self.dialog.geometry("320x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Make dialog appear on top
        self.dialog.attributes("-topmost", True)

        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"Customize {self.pet.name}",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))

        # Color selection
        color_frame = ttk.LabelFrame(main_frame, text="Body Color", padding="10")
        color_frame.pack(fill=tk.X, pady=5)

        self.color_var = tk.StringVar(value=self.customization.body_color)
        color_inner_frame = ttk.Frame(color_frame)
        color_inner_frame.pack()

        colors = list(COLOR_PALETTE.keys())
        for i, color_name in enumerate(colors):
            row = i // 3
            col = i % 3

            # Create a colored button for each color
            color_btn = tk.Button(
                color_inner_frame,
                width=8,
                bg=COLOR_PALETTE[color_name],
                activebackground=COLOR_PALETTE[color_name],
                text=color_name.title(),
                font=("Arial", 8),
                relief=tk.RAISED if color_name != self.customization.body_color else tk.SUNKEN,
                command=lambda c=color_name: self._select_color(c)
            )
            color_btn.grid(row=row, column=col, padx=3, pady=3)
            setattr(self, f"color_btn_{color_name}", color_btn)

        # Ear style selection
        ear_frame = ttk.LabelFrame(main_frame, text="Ear Style", padding="10")
        ear_frame.pack(fill=tk.X, pady=5)

        self.ear_var = tk.StringVar(value=self.customization.ear_style.value)

        ear_options = [
            ("Cat", EarStyle.CAT.value),
            ("Bunny", EarStyle.BUNNY.value),
            ("Bear", EarStyle.BEAR.value),
            ("Antenna", EarStyle.ANTENNA.value)
        ]

        ear_inner_frame = ttk.Frame(ear_frame)
        ear_inner_frame.pack()

        for i, (text, value) in enumerate(ear_options):
            rb = ttk.Radiobutton(
                ear_inner_frame,
                text=text,
                value=value,
                variable=self.ear_var,
                command=self._on_ear_change
            )
            rb.grid(row=0, column=i, padx=5)

        # Tail style selection
        tail_frame = ttk.LabelFrame(main_frame, text="Tail Style", padding="10")
        tail_frame.pack(fill=tk.X, pady=5)

        self.tail_var = tk.StringVar(value=self.customization.tail_style.value)

        tail_options = [
            ("Cat", TailStyle.CAT.value),
            ("Bunny", TailStyle.BUNNY.value),
            ("Dog", TailStyle.DOG.value),
            ("None", TailStyle.NONE.value)
        ]

        tail_inner_frame = ttk.Frame(tail_frame)
        tail_inner_frame.pack()

        for i, (text, value) in enumerate(tail_options):
            rb = ttk.Radiobutton(
                tail_inner_frame,
                text=text,
                value=value,
                variable=self.tail_var,
                command=self._on_tail_change
            )
            rb.grid(row=0, column=i, padx=5)

        # Accessory selection
        accessory_frame = ttk.LabelFrame(main_frame, text="Accessory", padding="10")
        accessory_frame.pack(fill=tk.X, pady=5)

        self.accessory_var = tk.StringVar(value=self.customization.accessory.value)

        accessory_options = [
            ("None", Accessory.NONE.value),
            ("Bow", Accessory.BOW.value),
            ("Hat", Accessory.HAT.value),
            ("Glasses", Accessory.GLASSES.value)
        ]

        accessory_inner_frame = ttk.Frame(accessory_frame)
        accessory_inner_frame.pack()

        for i, (text, value) in enumerate(accessory_options):
            rb = ttk.Radiobutton(
                accessory_inner_frame,
                text=text,
                value=value,
                variable=self.accessory_var,
                command=self._on_accessory_change
            )
            rb.grid(row=0, column=i, padx=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        save_btn = ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _select_color(self, color_name: str) -> None:
        """Handle color selection."""
        self.customization.body_color = color_name
        self.color_var.set(color_name)

        # Update button appearances
        for name in COLOR_PALETTE.keys():
            btn = getattr(self, f"color_btn_{name}", None)
            if btn:
                btn.config(relief=tk.SUNKEN if name == color_name else tk.RAISED)

    def _on_ear_change(self) -> None:
        """Handle ear style change."""
        self.customization.ear_style = EarStyle(self.ear_var.get())

    def _on_tail_change(self) -> None:
        """Handle tail style change."""
        self.customization.tail_style = TailStyle(self.tail_var.get())

    def _on_accessory_change(self) -> None:
        """Handle accessory change."""
        self.customization.accessory = Accessory(self.accessory_var.get())

    def _on_cancel(self) -> None:
        """Handle cancel button."""
        self.dialog.destroy()

    def _on_save(self) -> None:
        """Handle save button."""
        if self.on_save:
            self.on_save(self.customization)
        self.dialog.destroy()


class PetMenu:
    """
    Right-click context menu for pet interactions.

    Provides feed, play, sleep, customize, change floob, stats, auto-care toggle, and quit options.
    """

    def __init__(
        self,
        parent: tk.Tk,
        pet: Pet,
        on_feed: Optional[Callable[[], None]] = None,
        on_play: Optional[Callable[[], None]] = None,
        on_sleep: Optional[Callable[[], None]] = None,
        on_customize: Optional[Callable[[PetCustomization], None]] = None,
        on_change_floob: Optional[Callable[[], None]] = None,
        on_auto_care_toggle: Optional[Callable[[bool], None]] = None,
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
            on_customize: Callback when customization is saved.
            on_change_floob: Callback when Change Floob is selected.
            on_auto_care_toggle: Callback when auto-care is toggled (receives new state).
            on_quit: Callback when Quit is selected.
        """
        self.parent = parent
        self.pet = pet
        self.on_feed = on_feed
        self.on_play = on_play
        self.on_sleep = on_sleep
        self.on_customize = on_customize
        self.on_change_floob = on_change_floob
        self.on_auto_care_toggle = on_auto_care_toggle
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

        # Customize option
        self.menu.add_command(
            label="Customize",
            command=self._handle_customize
        )

        # Change Floob option
        self.menu.add_command(
            label="Change Floob",
            command=self._handle_change_floob
        )

        # Stats option
        self.menu.add_command(
            label="Stats",
            command=self._show_stats
        )

        self.menu.add_separator()

        # Auto-care toggle (checkbutton style)
        self._auto_care_index = self.menu.index(tk.END) + 1
        self.menu.add_command(
            label=self._get_auto_care_label(),
            command=self._handle_auto_care_toggle
        )

        self.menu.add_separator()

        # Quit option
        self.menu.add_command(
            label="Quit",
            command=self._handle_quit
        )

    def _get_auto_care_label(self) -> str:
        """Get the label for the auto-care toggle based on current state."""
        status = "ON" if self.pet.auto_care_enabled else "OFF"
        return f"Auto-Care: {status}"

    def _handle_auto_care_toggle(self) -> None:
        """Handle auto-care toggle selection."""
        new_state = self.pet.toggle_auto_care()

        # Update the menu label
        self.menu.entryconfig(self._auto_care_index, label=self._get_auto_care_label())

        # Notify callback
        if self.on_auto_care_toggle:
            self.on_auto_care_toggle(new_state)

        # Show confirmation
        status = "enabled" if new_state else "disabled"
        messagebox.showinfo(
            "Auto-Care",
            f"Auto-care has been {status}.\n\n"
            f"When enabled, {self.pet.name} will automatically eat, "
            f"play, and sleep when stats get low."
        )

    def show(self, x: int, y: int) -> None:
        """
        Display the context menu at the given position.

        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
        """
        # Update auto-care label before showing (in case it changed)
        self.menu.entryconfig(self._auto_care_index, label=self._get_auto_care_label())

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

    def _handle_customize(self) -> None:
        """Handle Customize menu selection."""
        CustomizationDialog(
            self.parent,
            self.pet,
            on_save=self._on_customization_saved
        )

    def _on_customization_saved(self, customization: PetCustomization) -> None:
        """Handle customization being saved."""
        self.pet.customization = customization
        if self.on_customize:
            self.on_customize(customization)

    def _handle_change_floob(self) -> None:
        """Handle Change Floob menu selection."""
        if self.on_change_floob:
            self.on_change_floob()

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

        auto_care_status = "ON" if self.pet.auto_care_enabled else "OFF"

        stats_text = f"""
{self.pet.name}'s Stats

Hunger:    {make_bar(self.pet.stats.hunger)} {self.pet.stats.hunger:.0f}%
Happiness: {make_bar(self.pet.stats.happiness)} {self.pet.stats.happiness:.0f}%
Energy:    {make_bar(self.pet.stats.energy)} {self.pet.stats.energy:.0f}%

Current Mood: {mood.name.title()}
Auto-Care: {auto_care_status}
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
