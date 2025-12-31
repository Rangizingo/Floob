"""
Floob 2.0 Dialog Windows.

Contains dialog classes for:
- StatsDialog: Shows pet stats, level progress, and evolution info
- EvolutionHistoryDialog: Shows timeline of all evolutions
- EvolutionNotificationDialog: Modal shown when evolution occurs
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Dict, Tuple
from datetime import datetime
import math

from core.config import Colors, hex_to_rgb


def create_progress_bar(value: float, max_value: float = 100.0) -> str:
    """
    Create a text-based progress bar.

    Args:
        value: Current value.
        max_value: Maximum value.

    Returns:
        String representation of progress bar.
    """
    percent = min(100, max(0, (value / max_value) * 100))
    filled = int(percent / 10)
    empty = 10 - filled
    return f"[{'#' * filled}{'-' * empty}]"


class StatsDialog:
    """
    Dialog showing pet statistics, level progress, and evolution info.

    Displays:
    - Pet Info: Name, Form name, Evolution stage
    - Stats Bars: Hunger, Happiness, Energy with visual bars
    - Level Progress: Level, XP, next evolution level
    - Care Style: Current calculated care style
    - Time with pet: Days/hours since birth
    - Auto-Care indicator
    """

    def __init__(
        self,
        parent: tk.Tk,
        pet_data: Dict,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the stats dialog.

        Args:
            parent: Parent Tkinter window.
            pet_data: Dictionary containing pet information:
                - name: Pet name
                - form_name: Current form name
                - stage: Evolution stage name
                - hunger, happiness, energy: Current stats
                - level: Current level
                - xp: Current XP
                - xp_to_next: XP needed for next level
                - next_evolution_level: Level for next evolution
                - care_style: Current care style name
                - birth_time: Unix timestamp of birth
                - auto_care_enabled: Boolean
            on_close: Optional callback when dialog is closed.
        """
        self.parent = parent
        self.pet_data = pet_data
        self.on_close = on_close

        self._create_dialog()

    def _create_dialog(self) -> None:
        """Create the stats dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"{self.pet_data.get('name', 'Pet')} - Stats")
        self.dialog.geometry("350x480")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Make dialog appear on top
        self.dialog.attributes("-topmost", True)

        # Set dialog colors
        bg_color = Colors.UI_BACKGROUND
        text_color = Colors.UI_TEXT
        self.dialog.configure(bg=bg_color)

        # Main frame with padding
        main_frame = tk.Frame(self.dialog, bg=bg_color, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title with pet name and form
        name = self.pet_data.get("name", "Unknown")
        form_name = self.pet_data.get("form_name", "Unknown")
        stage = self.pet_data.get("stage", "Unknown")

        title_label = tk.Label(
            main_frame,
            text=f"{name}",
            font=("Arial", 16, "bold"),
            bg=bg_color,
            fg=text_color,
        )
        title_label.pack(pady=(0, 2))

        subtitle_label = tk.Label(
            main_frame,
            text=f"{form_name} ({stage})",
            font=("Arial", 11),
            bg=bg_color,
            fg=Colors.UI_TEXT_LIGHT,
        )
        subtitle_label.pack(pady=(0, 15))

        # Separator
        sep1 = tk.Frame(main_frame, height=1, bg=Colors.UI_BORDER)
        sep1.pack(fill=tk.X, pady=5)

        # Stats section
        stats_label = tk.Label(
            main_frame,
            text="Stats",
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg=text_color,
        )
        stats_label.pack(anchor="w", pady=(10, 5))

        self._create_stat_bar(main_frame, "Hunger", self.pet_data.get("hunger", 0), Colors.HUNGER_BAR, bg_color, text_color)
        self._create_stat_bar(main_frame, "Happiness", self.pet_data.get("happiness", 0), Colors.HAPPINESS_BAR, bg_color, text_color)
        self._create_stat_bar(main_frame, "Energy", self.pet_data.get("energy", 0), Colors.ENERGY_BAR, bg_color, text_color)

        # Level Progress section
        sep2 = tk.Frame(main_frame, height=1, bg=Colors.UI_BORDER)
        sep2.pack(fill=tk.X, pady=10)

        level_label = tk.Label(
            main_frame,
            text="Level Progress",
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg=text_color,
        )
        level_label.pack(anchor="w", pady=(5, 5))

        level = self.pet_data.get("level", 1)
        xp = self.pet_data.get("xp", 0)
        xp_to_next = self.pet_data.get("xp_to_next", 100)
        next_evo_level = self.pet_data.get("next_evolution_level", None)

        level_info = tk.Label(
            main_frame,
            text=f"Level: {level}",
            font=("Arial", 11),
            bg=bg_color,
            fg=text_color,
        )
        level_info.pack(anchor="w")

        xp_percent = (xp / xp_to_next * 100) if xp_to_next > 0 else 0
        self._create_stat_bar(main_frame, f"XP: {xp}/{xp_to_next}", xp_percent, Colors.XP_BAR, bg_color, text_color)

        if next_evo_level:
            next_evo_label = tk.Label(
                main_frame,
                text=f"Next evolution at: Level {next_evo_level}",
                font=("Arial", 10),
                bg=bg_color,
                fg=Colors.UI_TEXT_LIGHT,
            )
            next_evo_label.pack(anchor="w", pady=(2, 0))

        # Care Style section
        sep3 = tk.Frame(main_frame, height=1, bg=Colors.UI_BORDER)
        sep3.pack(fill=tk.X, pady=10)

        care_style = self.pet_data.get("care_style", "Balanced")
        care_label = tk.Label(
            main_frame,
            text=f"Care Style: {care_style}",
            font=("Arial", 11),
            bg=bg_color,
            fg=text_color,
        )
        care_label.pack(anchor="w")

        # Time with pet
        birth_time = self.pet_data.get("birth_time", None)
        if birth_time:
            elapsed = datetime.now().timestamp() - birth_time
            days = int(elapsed // 86400)
            hours = int((elapsed % 86400) // 3600)
            time_text = f"Time with pet: {days} days, {hours} hours"
        else:
            time_text = "Time with pet: Unknown"

        time_label = tk.Label(
            main_frame,
            text=time_text,
            font=("Arial", 10),
            bg=bg_color,
            fg=Colors.UI_TEXT_LIGHT,
        )
        time_label.pack(anchor="w", pady=(5, 0))

        # Auto-Care indicator
        auto_care = self.pet_data.get("auto_care_enabled", True)
        auto_care_text = f"Auto-Care: {'ON' if auto_care else 'OFF'}"
        auto_label = tk.Label(
            main_frame,
            text=auto_care_text,
            font=("Arial", 10),
            bg=bg_color,
            fg=Colors.SOFT_GREEN if auto_care else Colors.SOFT_ORANGE,
        )
        auto_label.pack(anchor="w", pady=(5, 0))

        # Close button
        close_btn = tk.Button(
            main_frame,
            text="Close",
            command=self._on_close,
            font=("Arial", 10),
            bg=Colors.SOFT_BLUE,
            fg=text_color,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        )
        close_btn.pack(pady=(20, 0))

        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_stat_bar(
        self,
        parent: tk.Frame,
        label: str,
        value: float,
        bar_color: str,
        bg_color: str,
        text_color: str,
    ) -> None:
        """Create a visual stat bar with label."""
        frame = tk.Frame(parent, bg=bg_color)
        frame.pack(fill=tk.X, pady=3)

        # Label
        lbl = tk.Label(
            frame,
            text=f"{label}:",
            font=("Arial", 10),
            bg=bg_color,
            fg=text_color,
            width=12,
            anchor="w",
        )
        lbl.pack(side=tk.LEFT)

        # Bar background
        bar_bg = tk.Frame(frame, bg=Colors.UI_BORDER, height=16, width=150)
        bar_bg.pack(side=tk.LEFT, padx=(5, 5))
        bar_bg.pack_propagate(False)

        # Bar fill
        fill_width = int(value / 100 * 150)
        bar_fill = tk.Frame(bar_bg, bg=bar_color, height=16, width=fill_width)
        bar_fill.place(x=0, y=0)

        # Percentage text
        pct_lbl = tk.Label(
            frame,
            text=f"{int(value)}%",
            font=("Arial", 10),
            bg=bg_color,
            fg=text_color,
            width=5,
        )
        pct_lbl.pack(side=tk.LEFT)

    def _on_close(self) -> None:
        """Handle dialog close."""
        if self.on_close:
            self.on_close()
        self.dialog.destroy()


class EvolutionHistoryDialog:
    """
    Dialog showing the evolution history timeline.

    Displays all evolutions with form names, dates, and icons.
    """

    # Icons for each stage
    STAGE_ICONS = {
        "EGG": "\U0001F95A",      # Egg emoji
        "BABY": "\U0001F423",     # Hatching chick
        "CHILD": "\U0001F31F",    # Star
        "TEEN": "\U0001F525",     # Fire
        "ADULT": "\U0001F451",    # Crown
    }

    def __init__(
        self,
        parent: tk.Tk,
        evolution_history: List[Dict],
        current_form: str,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the evolution history dialog.

        Args:
            parent: Parent Tkinter window.
            evolution_history: List of evolution events, each containing:
                - form_id: Form identifier
                - form_name: Display name
                - stage: Evolution stage name
                - timestamp: Unix timestamp of evolution
            current_form: ID of the current form.
            on_close: Optional callback when dialog is closed.
        """
        self.parent = parent
        self.evolution_history = evolution_history
        self.current_form = current_form
        self.on_close = on_close

        self._create_dialog()

    def _create_dialog(self) -> None:
        """Create the evolution history dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Evolution History")
        self.dialog.geometry("320x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Make dialog appear on top
        self.dialog.attributes("-topmost", True)

        # Set dialog colors
        bg_color = Colors.UI_BACKGROUND
        text_color = Colors.UI_TEXT
        self.dialog.configure(bg=bg_color)

        # Main frame with padding
        main_frame = tk.Frame(self.dialog, bg=bg_color, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Evolution History",
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg=text_color,
        )
        title_label.pack(pady=(0, 10))

        # Separator
        sep = tk.Frame(main_frame, height=2, bg=Colors.UI_BORDER)
        sep.pack(fill=tk.X, pady=5)

        # Scrollable canvas for history
        canvas_frame = tk.Frame(main_frame, bg=bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        canvas = tk.Canvas(canvas_frame, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add evolution entries
        for i, entry in enumerate(self.evolution_history):
            self._create_history_entry(
                scrollable_frame,
                entry,
                is_current=(entry.get("form_id") == self.current_form),
                is_last=(i == len(self.evolution_history) - 1),
                bg_color=bg_color,
                text_color=text_color,
            )

        # If no history, show message
        if not self.evolution_history:
            no_history = tk.Label(
                scrollable_frame,
                text="No evolution history yet.\nYour pet is still growing!",
                font=("Arial", 11),
                bg=bg_color,
                fg=Colors.UI_TEXT_LIGHT,
                justify=tk.CENTER,
            )
            no_history.pack(pady=30)

        # Close button
        close_btn = tk.Button(
            main_frame,
            text="Close",
            command=self._on_close,
            font=("Arial", 10),
            bg=Colors.SOFT_BLUE,
            fg=text_color,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        )
        close_btn.pack(pady=(10, 0))

        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _create_history_entry(
        self,
        parent: tk.Frame,
        entry: Dict,
        is_current: bool,
        is_last: bool,
        bg_color: str,
        text_color: str,
    ) -> None:
        """Create a single history entry in the timeline."""
        frame = tk.Frame(parent, bg=bg_color)
        frame.pack(fill=tk.X, pady=5)

        stage = entry.get("stage", "UNKNOWN")
        form_name = entry.get("form_name", "Unknown")
        timestamp = entry.get("timestamp", 0)

        # Icon
        icon = self.STAGE_ICONS.get(stage, "\U0001F31F")
        icon_label = tk.Label(
            frame,
            text=icon,
            font=("Segoe UI Emoji", 16),
            bg=bg_color,
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        # Content frame
        content = tk.Frame(frame, bg=bg_color)
        content.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Form name with current indicator
        name_text = f"{form_name} ({stage})"
        if is_current:
            name_text += " <- Current"
        name_label = tk.Label(
            content,
            text=name_text,
            font=("Arial", 11, "bold" if is_current else "normal"),
            bg=bg_color,
            fg=Colors.SOFT_PURPLE if is_current else text_color,
            anchor="w",
        )
        name_label.pack(anchor="w")

        # Timestamp
        if timestamp > 0:
            dt = datetime.fromtimestamp(timestamp)
            date_str = dt.strftime("%b %d, %Y at %H:%M")
            action = "Hatched" if stage == "BABY" else "Evolved"
        else:
            date_str = "Unknown date"
            action = "Appeared"

        date_label = tk.Label(
            content,
            text=f"{action}: {date_str}",
            font=("Arial", 9),
            bg=bg_color,
            fg=Colors.UI_TEXT_LIGHT,
            anchor="w",
        )
        date_label.pack(anchor="w")

        # Connector line (except for last entry)
        if not is_last:
            connector = tk.Label(
                parent,
                text="   |",
                font=("Arial", 12),
                bg=bg_color,
                fg=Colors.UI_BORDER,
            )
            connector.pack(anchor="w", padx=(10, 0))

    def _on_close(self) -> None:
        """Handle dialog close."""
        if self.on_close:
            self.on_close()
        self.dialog.destroy()


class EvolutionNotificationDialog:
    """
    Modal dialog shown when evolution occurs.

    Shows celebration with new form name and animation.
    """

    def __init__(
        self,
        parent: tk.Tk,
        new_form_name: str,
        new_stage: str,
        on_dismiss: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the evolution notification dialog.

        Args:
            parent: Parent Tkinter window.
            new_form_name: Name of the new form.
            new_stage: New evolution stage.
            on_dismiss: Callback when dialog is dismissed.
        """
        self.parent = parent
        self.new_form_name = new_form_name
        self.new_stage = new_stage
        self.on_dismiss = on_dismiss
        self._animation_phase = 0.0
        self._particles: List[Dict] = []

        self._create_dialog()
        self._start_animation()

    def _create_dialog(self) -> None:
        """Create the evolution notification dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Evolution!")
        self.dialog.geometry("350x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Make dialog appear on top
        self.dialog.attributes("-topmost", True)

        # Set dialog colors - celebration theme
        bg_color = Colors.SOFT_LAVENDER
        self.dialog.configure(bg=bg_color)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Celebration header
        header = tk.Label(
            main_frame,
            text="\U0001F389 Congratulations! \U0001F389",
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg=Colors.UI_TEXT,
        )
        header.pack(pady=(0, 15))

        # Canvas for animation
        self.canvas = tk.Canvas(
            main_frame,
            width=310,
            height=100,
            bg=bg_color,
            highlightthickness=0,
        )
        self.canvas.pack(pady=10)

        # Evolution message
        message = tk.Label(
            main_frame,
            text="Your pet evolved into",
            font=("Arial", 12),
            bg=bg_color,
            fg=Colors.UI_TEXT,
        )
        message.pack()

        # New form name (with glow effect via colored background)
        form_frame = tk.Frame(main_frame, bg=Colors.SOFT_YELLOW, padx=15, pady=8)
        form_frame.pack(pady=10)

        form_name = tk.Label(
            form_frame,
            text=f"\U0001F31F {self.new_form_name} \U0001F31F",
            font=("Arial", 16, "bold"),
            bg=Colors.SOFT_YELLOW,
            fg=Colors.UI_TEXT,
        )
        form_name.pack()

        stage_label = tk.Label(
            main_frame,
            text=f"Stage: {self.new_stage}",
            font=("Arial", 10),
            bg=bg_color,
            fg=Colors.UI_TEXT_LIGHT,
        )
        stage_label.pack()

        # OK button
        ok_btn = tk.Button(
            main_frame,
            text="Wonderful!",
            command=self._on_dismiss,
            font=("Arial", 12, "bold"),
            bg=Colors.SOFT_GREEN,
            fg=Colors.UI_TEXT,
            relief=tk.FLAT,
            padx=30,
            pady=8,
        )
        ok_btn.pack(pady=(20, 0))

        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Initialize particles for celebration
        self._init_particles()

    def _init_particles(self) -> None:
        """Initialize celebration particles."""
        import random

        colors = [
            Colors.SOFT_PINK,
            Colors.SOFT_YELLOW,
            Colors.SOFT_BLUE,
            Colors.SOFT_GREEN,
            Colors.SOFT_ORANGE,
        ]

        for _ in range(20):
            self._particles.append({
                "x": random.randint(0, 310),
                "y": random.randint(-50, 0),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(1, 3),
                "size": random.randint(4, 8),
                "color": random.choice(colors),
                "rotation": random.uniform(0, 360),
                "rot_speed": random.uniform(-5, 5),
            })

    def _start_animation(self) -> None:
        """Start the celebration animation."""
        self._animate()

    def _animate(self) -> None:
        """Animation loop for particles."""
        if not self.dialog.winfo_exists():
            return

        self._animation_phase += 0.1

        # Clear canvas
        self.canvas.delete("all")

        # Draw and update particles
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["rotation"] += p["rot_speed"]

            # Reset if off screen
            if p["y"] > 110:
                import random
                p["y"] = random.randint(-20, 0)
                p["x"] = random.randint(0, 310)

            # Draw confetti (rectangle rotated)
            size = p["size"]
            self.canvas.create_rectangle(
                p["x"] - size,
                p["y"] - size // 2,
                p["x"] + size,
                p["y"] + size // 2,
                fill=p["color"],
                outline="",
            )

        # Draw sparkle stars
        for i in range(5):
            angle = self._animation_phase + i * (math.pi * 2 / 5)
            x = 155 + math.cos(angle) * 80
            y = 50 + math.sin(angle) * 30
            self.canvas.create_text(
                x, y,
                text="\U00002728",  # Sparkle
                font=("Segoe UI Emoji", 12),
            )

        # Schedule next frame
        self.dialog.after(50, self._animate)

    def _on_dismiss(self) -> None:
        """Handle dialog dismissal."""
        if self.on_dismiss:
            self.on_dismiss()
        self.dialog.destroy()


class SettingsDialog:
    """
    Settings dialog for configuring pet behavior.

    Allows toggling:
    - Auto-care mode (pet takes care of itself)
    - Sound effects (future feature)
    - Other customization options
    """

    def __init__(
        self,
        parent: tk.Tk,
        auto_care_enabled: bool = True,
        on_auto_care_toggle: Optional[Callable[[bool], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the settings dialog.

        Args:
            parent: Parent Tkinter window.
            auto_care_enabled: Current auto-care state.
            on_auto_care_toggle: Callback when auto-care is toggled.
            on_close: Optional callback when dialog is closed.
        """
        self.parent = parent
        self.auto_care_enabled = auto_care_enabled
        self.on_auto_care_toggle = on_auto_care_toggle
        self.on_close = on_close

        # Tkinter variables for checkboxes
        self.auto_care_var = tk.BooleanVar(value=auto_care_enabled)

        self._create_dialog()

    def _create_dialog(self) -> None:
        """Create the settings dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("280x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Make dialog appear on top
        self.dialog.attributes("-topmost", True)

        # Set dialog colors
        bg_color = Colors.UI_BACKGROUND
        text_color = Colors.UI_TEXT
        self.dialog.configure(bg=bg_color)

        # Main frame with padding
        main_frame = tk.Frame(self.dialog, bg=bg_color, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Settings",
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg=text_color,
        )
        title_label.pack(pady=(0, 15))

        # Separator
        sep = tk.Frame(main_frame, height=1, bg=Colors.UI_BORDER)
        sep.pack(fill=tk.X, pady=5)

        # Settings options frame
        options_frame = tk.Frame(main_frame, bg=bg_color)
        options_frame.pack(fill=tk.X, pady=10)

        # Auto-care toggle
        auto_care_frame = tk.Frame(options_frame, bg=bg_color)
        auto_care_frame.pack(fill=tk.X, pady=5)

        auto_care_check = tk.Checkbutton(
            auto_care_frame,
            text="Auto-Care Mode",
            variable=self.auto_care_var,
            command=self._toggle_auto_care,
            font=("Arial", 11),
            bg=bg_color,
            fg=text_color,
            activebackground=bg_color,
            activeforeground=text_color,
            selectcolor=Colors.SOFT_GREEN,
        )
        auto_care_check.pack(anchor="w")

        auto_care_desc = tk.Label(
            auto_care_frame,
            text="Pet will automatically eat, play, and\nsleep when stats get low.",
            font=("Arial", 9),
            bg=bg_color,
            fg=Colors.UI_TEXT_LIGHT,
            justify=tk.LEFT,
        )
        auto_care_desc.pack(anchor="w", padx=(20, 0))

        # Second separator
        sep2 = tk.Frame(main_frame, height=1, bg=Colors.UI_BORDER)
        sep2.pack(fill=tk.X, pady=15)

        # Additional info
        info_label = tk.Label(
            main_frame,
            text="More settings coming soon!",
            font=("Arial", 10),
            bg=bg_color,
            fg=Colors.UI_TEXT_LIGHT,
        )
        info_label.pack()

        # Close button
        close_btn = tk.Button(
            main_frame,
            text="Close",
            command=self._on_close,
            font=("Arial", 10),
            bg=Colors.SOFT_BLUE,
            fg=text_color,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        )
        close_btn.pack(pady=(20, 0))

        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def _toggle_auto_care(self) -> None:
        """Handle auto-care toggle."""
        new_state = self.auto_care_var.get()
        self.auto_care_enabled = new_state

        if self.on_auto_care_toggle:
            self.on_auto_care_toggle(new_state)

    def _on_close(self) -> None:
        """Handle dialog close."""
        if self.on_close:
            self.on_close()
        self.dialog.destroy()
