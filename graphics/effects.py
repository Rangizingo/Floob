"""
Floob 2.0 Visual Effects Module.

Provides visual effects for enhancing the blob sprites:
- Glow effects (for egg, level up, mystic forms)
- Shadow underneath blob
- Thought/speech bubbles
- Stat indicator icons
- Particle effect helpers
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple

from graphics.sprites import lighten_color, darken_color

# Import colors
try:
    from core.config import Colors
except ImportError:
    class Colors:
        SOFT_PINK = "#FFD6E0"
        SOFT_BLUE = "#A2D2FF"
        SOFT_PURPLE = "#CDB4DB"
        SOFT_GREEN = "#B5E48C"
        SOFT_YELLOW = "#FFF3B0"
        SOFT_ORANGE = "#FFB5A7"
        SOFT_CREAM = "#FFF8F0"
        SOFT_GRAY = "#E8E8E8"
        WHITE = "#FFFFFF"
        BLACK = "#2D2D2D"
        UI_BACKGROUND = "#FEFEFE"
        UI_BORDER = "#D0D0D0"
        UI_TEXT = "#404040"
        HUNGER_BAR = "#FFB5A7"
        HAPPINESS_BAR = "#FFF3B0"
        ENERGY_BAR = "#A2D2FF"


class StatType(Enum):
    """Types of stats that can be displayed."""
    HUNGER = auto()
    HAPPINESS = auto()
    ENERGY = auto()
    XP = auto()


# Stat icons (Unicode characters)
STAT_ICONS = {
    StatType.HUNGER: "\U0001F356",  # Meat on bone
    StatType.HAPPINESS: "\U0001F60A",  # Smiling face
    StatType.ENERGY: "\u26A1",  # Lightning bolt
    StatType.XP: "\u2B50",  # Star
}

# Stat colors
STAT_COLORS = {
    StatType.HUNGER: Colors.SOFT_ORANGE,
    StatType.HAPPINESS: Colors.SOFT_YELLOW,
    StatType.ENERGY: Colors.SOFT_BLUE,
    StatType.XP: Colors.SOFT_GREEN,
}


def draw_glow(
    canvas: tk.Canvas,
    x: float,
    y: float,
    radius: float,
    color: str,
    intensity: float = 1.0,
    layers: int = 3,
) -> List[int]:
    """
    Draw a soft glow effect.

    Creates multiple layered ovals with decreasing opacity
    to simulate a glowing effect.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        radius: Base radius of the glow.
        color: Glow color in hex format.
        intensity: Glow intensity (0.0-1.0).
        layers: Number of glow layers.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    for i in range(layers, 0, -1):
        # Each layer is larger but more transparent
        layer_radius = radius * (1 + (i - 1) * 0.3)
        layer_color = lighten_color(color, 0.1 + (i - 1) * 0.2)

        glow_id = canvas.create_oval(
            x - layer_radius, y - layer_radius,
            x + layer_radius, y + layer_radius,
            fill=layer_color,
            outline="",
        )
        items.append(glow_id)

    return items


def draw_pulsing_glow(
    canvas: tk.Canvas,
    x: float,
    y: float,
    base_radius: float,
    color: str,
    phase: float,
    pulse_amount: float = 0.15,
) -> List[int]:
    """
    Draw a pulsing glow effect.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        base_radius: Base radius of the glow.
        color: Glow color in hex format.
        phase: Animation phase (0.0-2*pi for full cycle).
        pulse_amount: How much the glow pulses (0.0-1.0).

    Returns:
        List of canvas item IDs created.
    """
    # Calculate pulsing radius
    pulse = 1.0 + math.sin(phase) * pulse_amount
    radius = base_radius * pulse

    return draw_glow(canvas, x, y, radius, color)


def draw_shadow(
    canvas: tk.Canvas,
    x: float,
    y: float,
    width: float,
    height: float = 0.0,
    opacity: float = 0.2,
) -> List[int]:
    """
    Draw an oval shadow underneath a sprite.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate of shadow.
        y: Center Y coordinate of shadow.
        width: Width of the shadow.
        height: Height of shadow (default: width * 0.3).
        opacity: Shadow opacity (affects color darkness).

    Returns:
        List of canvas item IDs created.
    """
    items = []

    if height == 0.0:
        height = width * 0.3

    # Shadow color based on opacity
    gray_value = int(200 - opacity * 80)
    shadow_color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"

    shadow_id = canvas.create_oval(
        x - width * 0.5, y - height * 0.5,
        x + width * 0.5, y + height * 0.5,
        fill=shadow_color,
        outline="",
    )
    items.append(shadow_id)

    return items


def draw_thought_bubble(
    canvas: tk.Canvas,
    x: float,
    y: float,
    text: str,
    icon: Optional[str] = None,
    width: float = 80.0,
    height: float = 40.0,
    opacity: float = 1.0,
) -> List[int]:
    """
    Draw a thought/speech bubble.

    Args:
        canvas: Tkinter canvas to draw on.
        x: X coordinate of bubble center.
        y: Y coordinate of bubble center.
        text: Text to display in bubble.
        icon: Optional emoji/icon to show before text.
        width: Bubble width.
        height: Bubble height.
        opacity: Bubble opacity (for fade effects).

    Returns:
        List of canvas item IDs created.
    """
    items = []

    # Adjust colors for opacity
    if opacity < 1.0:
        gray_val = int(255 * (1 - opacity) + 245 * opacity)
        fill_color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
        text_gray = int(255 * (1 - opacity) + 64 * opacity)
        text_color = f"#{text_gray:02x}{text_gray:02x}{text_gray:02x}"
        border_gray = int(255 * (1 - opacity) + 200 * opacity)
        border_color = f"#{border_gray:02x}{border_gray:02x}{border_gray:02x}"
    else:
        fill_color = Colors.UI_BACKGROUND
        text_color = Colors.UI_TEXT
        border_color = Colors.UI_BORDER

    # Main bubble (rounded rectangle via oval)
    bubble_id = canvas.create_oval(
        x - width * 0.5, y - height * 0.5,
        x + width * 0.5, y + height * 0.5,
        fill=fill_color,
        outline=border_color,
        width=1,
    )
    items.append(bubble_id)

    # Thought bubble dots (leading to pet)
    dot_positions = [
        (x - width * 0.4, y + height * 0.6),
        (x - width * 0.55, y + height * 0.85),
    ]
    for i, (dx, dy) in enumerate(dot_positions):
        size = 5 - i * 2
        dot_id = canvas.create_oval(
            dx - size, dy - size,
            dx + size, dy + size,
            fill=fill_color,
            outline=border_color,
        )
        items.append(dot_id)

    # Text content
    if icon:
        # Icon + text layout
        icon_id = canvas.create_text(
            x - width * 0.25, y,
            text=icon,
            font=("Segoe UI Emoji", 12),
            fill=text_color,
        )
        items.append(icon_id)

        text_id = canvas.create_text(
            x + width * 0.1, y,
            text=text,
            font=("Arial", 8),
            fill=text_color,
            anchor="w",
            width=int(width * 0.5),
        )
        items.append(text_id)
    else:
        # Text only (centered)
        text_id = canvas.create_text(
            x, y,
            text=text,
            font=("Arial", 9),
            fill=text_color,
            width=int(width * 0.85),
        )
        items.append(text_id)

    return items


def draw_stat_icon(
    canvas: tk.Canvas,
    x: float,
    y: float,
    stat_type: StatType,
    value: float,
    size: float = 20.0,
    show_bar: bool = True,
) -> List[int]:
    """
    Draw a small stat indicator icon with optional bar.

    Args:
        canvas: Tkinter canvas to draw on.
        x: X coordinate.
        y: Y coordinate.
        stat_type: Type of stat to display.
        value: Current stat value (0-100).
        size: Icon size.
        show_bar: Whether to show a progress bar.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    icon = STAT_ICONS.get(stat_type, "\u2022")
    color = STAT_COLORS.get(stat_type, Colors.SOFT_GRAY)

    # Draw icon
    icon_id = canvas.create_text(
        x, y,
        text=icon,
        font=("Segoe UI Emoji", int(size * 0.6)),
        fill=color,
    )
    items.append(icon_id)

    if show_bar:
        # Draw mini progress bar below icon
        bar_width = size * 1.2
        bar_height = size * 0.2
        bar_y = y + size * 0.5

        # Background bar
        bg_id = canvas.create_rectangle(
            x - bar_width * 0.5, bar_y - bar_height * 0.5,
            x + bar_width * 0.5, bar_y + bar_height * 0.5,
            fill=Colors.SOFT_GRAY,
            outline="",
        )
        items.append(bg_id)

        # Fill bar
        fill_width = bar_width * (value / 100.0)
        if fill_width > 0:
            fill_id = canvas.create_rectangle(
                x - bar_width * 0.5, bar_y - bar_height * 0.5,
                x - bar_width * 0.5 + fill_width, bar_y + bar_height * 0.5,
                fill=color,
                outline="",
            )
            items.append(fill_id)

    return items


def draw_stat_bar(
    canvas: tk.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    value: float,
    color: str,
    show_outline: bool = True,
) -> List[int]:
    """
    Draw a horizontal stat bar.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Left X coordinate.
        y: Top Y coordinate.
        width: Bar width.
        height: Bar height.
        value: Current value (0-100).
        color: Fill color for the bar.
        show_outline: Whether to show outline.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    # Background
    bg_id = canvas.create_rectangle(
        x, y,
        x + width, y + height,
        fill=Colors.SOFT_GRAY,
        outline=Colors.UI_BORDER if show_outline else "",
    )
    items.append(bg_id)

    # Fill
    fill_width = width * (max(0, min(100, value)) / 100.0)
    if fill_width > 0:
        fill_id = canvas.create_rectangle(
            x, y,
            x + fill_width, y + height,
            fill=color,
            outline="",
        )
        items.append(fill_id)

    return items


def draw_level_up_burst(
    canvas: tk.Canvas,
    x: float,
    y: float,
    radius: float,
    phase: float,
    color: str = Colors.SOFT_YELLOW,
) -> List[int]:
    """
    Draw a level-up burst effect (expanding ring with sparkles).

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        radius: Current radius of the burst.
        phase: Animation phase.
        color: Burst color.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    # Expanding ring
    ring_id = canvas.create_oval(
        x - radius, y - radius,
        x + radius, y + radius,
        fill="",
        outline=color,
        width=3,
    )
    items.append(ring_id)

    # Sparkles around ring
    num_sparkles = 8
    for i in range(num_sparkles):
        angle = (i / num_sparkles) * 2 * math.pi + phase
        spark_x = x + math.cos(angle) * radius
        spark_y = y + math.sin(angle) * radius

        spark_id = canvas.create_text(
            spark_x, spark_y,
            text="\u2734",
            font=("Arial", 10),
            fill=color,
        )
        items.append(spark_id)

    return items


def draw_hearts(
    canvas: tk.Canvas,
    x: float,
    y: float,
    count: int = 3,
    spread: float = 50.0,
    phase: float = 0.0,
) -> List[int]:
    """
    Draw floating heart particles.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        count: Number of hearts.
        spread: How spread out the hearts are.
        phase: Animation phase.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    heart_color = Colors.SOFT_PINK

    for i in range(count):
        # Offset each heart
        offset_x = math.sin(phase + i * 1.5) * spread * 0.3
        offset_y = -spread * 0.5 - (phase * 10 + i * 15) % 40

        heart_id = canvas.create_text(
            x + offset_x + (i - count // 2) * 20,
            y + offset_y,
            text="\u2665",
            font=("Arial", 14),
            fill=heart_color,
        )
        items.append(heart_id)

    return items


def draw_zzz(
    canvas: tk.Canvas,
    x: float,
    y: float,
    phase: float = 0.0,
) -> List[int]:
    """
    Draw floating ZZZ sleep particles.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Base X coordinate.
        y: Base Y coordinate.
        phase: Animation phase.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    zzz_color = Colors.SOFT_PURPLE
    sizes = [8, 10, 12]

    for i, size in enumerate(sizes):
        # Float upward
        y_offset = -i * 15 - (phase * 20) % 45
        x_offset = i * 5

        # Fade out at top
        if abs(y_offset) < 50:
            z_id = canvas.create_text(
                x + x_offset, y + y_offset,
                text="Z",
                font=("Arial", size, "bold"),
                fill=zzz_color,
            )
            items.append(z_id)

    return items


def draw_sparkles(
    canvas: tk.Canvas,
    x: float,
    y: float,
    count: int = 5,
    spread: float = 50.0,
    phase: float = 0.0,
) -> List[int]:
    """
    Draw sparkle particles.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        count: Number of sparkles.
        spread: How spread out the sparkles are.
        phase: Animation phase.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    sparkle_color = Colors.SOFT_YELLOW

    positions = [
        (-0.8, -0.6),
        (0.9, -0.5),
        (-0.7, 0.5),
        (0.8, 0.6),
        (0.0, -0.9),
    ]

    for i in range(min(count, len(positions))):
        px, py = positions[i]
        # Show/hide based on phase
        if (phase + i * 0.5) % 1.0 < 0.5:
            spark_id = canvas.create_text(
                x + px * spread,
                y + py * spread,
                text="\u2734",
                font=("Arial", 10),
                fill=sparkle_color,
            )
            items.append(spark_id)

    return items


def draw_sweat_drops(
    canvas: tk.Canvas,
    x: float,
    y: float,
    count: int = 2,
    phase: float = 0.0,
) -> List[int]:
    """
    Draw falling sweat drop particles.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Base X coordinate.
        y: Base Y coordinate.
        count: Number of drops.
        phase: Animation phase.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    drop_color = Colors.SOFT_BLUE

    for i in range(count):
        # Fall downward
        drop_phase = (phase + i * 0.5) % 1.0
        drop_y = y + drop_phase * 30
        drop_x = x + (i - 0.5) * 20

        if drop_phase < 0.8:  # Fade out near end
            # Teardrop shape
            points = [
                drop_x, drop_y - 5,
                drop_x - 3, drop_y + 2,
                drop_x, drop_y + 5,
                drop_x + 3, drop_y + 2,
            ]
            drop_id = canvas.create_polygon(
                points,
                fill=drop_color,
                outline="",
                smooth=True,
            )
            items.append(drop_id)

    return items


def draw_music_notes(
    canvas: tk.Canvas,
    x: float,
    y: float,
    count: int = 3,
    phase: float = 0.0,
) -> List[int]:
    """
    Draw bouncing music note particles.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        count: Number of notes.
        phase: Animation phase.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    note_color = Colors.SOFT_PURPLE
    notes = ["\u266A", "\u266B", "\u266C"]

    for i in range(count):
        note_phase = phase + i * 0.7
        # Bounce motion
        bounce_y = y - 20 - abs(math.sin(note_phase * 2)) * 15
        bounce_x = x + (i - 1) * 25 + math.sin(note_phase) * 5

        note_id = canvas.create_text(
            bounce_x, bounce_y,
            text=notes[i % len(notes)],
            font=("Arial", 12),
            fill=note_color,
        )
        items.append(note_id)

    return items


def draw_food_crumbs(
    canvas: tk.Canvas,
    x: float,
    y: float,
    count: int = 4,
    phase: float = 0.0,
) -> List[int]:
    """
    Draw falling food crumb particles.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X coordinate.
        y: Center Y coordinate.
        count: Number of crumbs.
        phase: Animation phase.

    Returns:
        List of canvas item IDs created.
    """
    items = []

    crumb_color = Colors.SOFT_ORANGE

    for i in range(count):
        crumb_phase = (phase * 2 + i * 0.3) % 1.0
        # Fall with slight sideways drift
        crumb_y = y + crumb_phase * 25
        crumb_x = x + (i - count / 2) * 10 + math.sin(crumb_phase * 4) * 3
        crumb_size = 3 + (i % 2)

        if crumb_phase < 0.9:  # Fade near end
            crumb_id = canvas.create_oval(
                crumb_x - crumb_size, crumb_y - crumb_size,
                crumb_x + crumb_size, crumb_y + crumb_size,
                fill=crumb_color,
                outline="",
            )
            items.append(crumb_id)

    return items


@dataclass
class EffectState:
    """
    State tracking for visual effects.

    Used to manage effect animations and cleanup.
    """
    items: List[int] = None
    phase: float = 0.0
    duration: float = 0.0
    elapsed: float = 0.0

    def __post_init__(self):
        if self.items is None:
            self.items = []

    def update(self, delta_time: float) -> bool:
        """
        Update effect state.

        Args:
            delta_time: Time elapsed since last update.

        Returns:
            True if effect is still active, False if expired.
        """
        self.elapsed += delta_time
        self.phase += delta_time

        if self.duration > 0 and self.elapsed >= self.duration:
            return False
        return True

    def get_progress(self) -> float:
        """Get effect progress (0.0-1.0)."""
        if self.duration <= 0:
            return 0.0
        return min(1.0, self.elapsed / self.duration)


class Effects:
    """
    Visual effects manager for blob sprites.

    Provides a unified interface for drawing various visual effects:
    - Glow effects (for egg, level up, mystic forms)
    - Shadow underneath blob
    - Thought/speech bubbles
    - Stat indicator icons
    - Particle effect coordination

    Usage:
        effects = Effects(canvas)
        effects.draw_shadow(x, y, width)
        effects.draw_glow(x, y, size, color, intensity)
        effects.clear()
    """

    def __init__(self, canvas: tk.Canvas) -> None:
        """
        Initialize the effects manager.

        Args:
            canvas: Tkinter canvas to draw on.
        """
        self.canvas = canvas
        self.items: List[int] = []

    def draw_shadow(
        self,
        x: float,
        y: float,
        width: float,
        opacity: float = 0.3,
    ) -> List[int]:
        """
        Draw oval shadow under pet.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            width: Shadow width.
            opacity: Shadow opacity (0.0-1.0).

        Returns:
            List of canvas item IDs created.
        """
        items = draw_shadow(self.canvas, x, y, width, 0.0, opacity)
        self.items.extend(items)
        return items

    def draw_glow(
        self,
        x: float,
        y: float,
        size: float,
        color: str,
        intensity: float,
    ) -> List[int]:
        """
        Draw glowing aura (for evolution, level up).

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            size: Glow radius.
            color: Glow color in hex format.
            intensity: Glow intensity (0.0-1.0).

        Returns:
            List of canvas item IDs created.
        """
        items = draw_glow(self.canvas, x, y, size, color, intensity)
        self.items.extend(items)
        return items

    def draw_pulsing_glow_effect(
        self,
        x: float,
        y: float,
        base_radius: float,
        color: str,
        phase: float,
        pulse_amount: float = 0.15,
    ) -> List[int]:
        """
        Draw a pulsing glow effect.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            base_radius: Base radius of the glow.
            color: Glow color in hex format.
            phase: Animation phase for pulsing.
            pulse_amount: How much the glow pulses.

        Returns:
            List of canvas item IDs created.
        """
        items = draw_pulsing_glow(self.canvas, x, y, base_radius, color, phase, pulse_amount)
        self.items.extend(items)
        return items

    def draw_thought_bubble_effect(
        self,
        x: float,
        y: float,
        text: str,
        icon: Optional[str] = None,
    ) -> List[int]:
        """
        Draw thought bubble with text/icon.

        Args:
            x: Bubble X coordinate.
            y: Bubble Y coordinate.
            text: Text to display.
            icon: Optional emoji/icon.

        Returns:
            List of canvas item IDs created.
        """
        items = draw_thought_bubble(self.canvas, x, y, text, icon)
        self.items.extend(items)
        return items

    def draw_stat_icon_effect(
        self,
        x: float,
        y: float,
        stat_type: StatType,
        value: float,
    ) -> List[int]:
        """
        Draw small stat indicator (heart for hunger, etc.).

        Args:
            x: Icon X coordinate.
            y: Icon Y coordinate.
            stat_type: Type of stat to display.
            value: Current stat value (0-100).

        Returns:
            List of canvas item IDs created.
        """
        items = draw_stat_icon(self.canvas, x, y, stat_type, value)
        self.items.extend(items)
        return items

    def draw_hearts_effect(
        self,
        x: float,
        y: float,
        count: int = 3,
        spread: float = 50.0,
        phase: float = 0.0,
    ) -> List[int]:
        """
        Draw floating heart particles.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            count: Number of hearts.
            spread: How spread out the hearts are.
            phase: Animation phase.

        Returns:
            List of canvas item IDs created.
        """
        items = draw_hearts(self.canvas, x, y, count, spread, phase)
        self.items.extend(items)
        return items

    def draw_zzz_effect(
        self,
        x: float,
        y: float,
        phase: float = 0.0,
    ) -> List[int]:
        """
        Draw floating ZZZ sleep particles.

        Args:
            x: Base X coordinate.
            y: Base Y coordinate.
            phase: Animation phase.

        Returns:
            List of canvas item IDs created.
        """
        items = draw_zzz(self.canvas, x, y, phase)
        self.items.extend(items)
        return items

    def draw_sparkles_effect(
        self,
        x: float,
        y: float,
        count: int = 5,
        spread: float = 50.0,
        phase: float = 0.0,
    ) -> List[int]:
        """
        Draw sparkle particles.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            count: Number of sparkles.
            spread: How spread out the sparkles are.
            phase: Animation phase.

        Returns:
            List of canvas item IDs created.
        """
        items = draw_sparkles(self.canvas, x, y, count, spread, phase)
        self.items.extend(items)
        return items

    def draw_confetti(
        self,
        x: float,
        y: float,
        count: int = 10,
        spread: float = 80.0,
        phase: float = 0.0,
    ) -> List[int]:
        """
        Draw falling confetti particles.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            count: Number of confetti pieces.
            spread: How spread out the confetti is.
            phase: Animation phase.

        Returns:
            List of canvas item IDs created.
        """
        items = []
        confetti_colors = [
            Colors.SOFT_PINK,
            Colors.SOFT_BLUE,
            Colors.SOFT_YELLOW,
            Colors.SOFT_GREEN,
            Colors.SOFT_PURPLE,
            Colors.SOFT_ORANGE,
        ]

        for i in range(count):
            confetti_phase = (phase * 0.8 + i * 0.2) % 2.0
            # Fall downward with drift
            fall_y = y + confetti_phase * 40 - 20
            drift_x = x + math.sin(confetti_phase * 3 + i) * spread * 0.5 + (i - count // 2) * 15
            rotation = confetti_phase * 180

            if confetti_phase < 1.8:  # Fade near end
                color = confetti_colors[i % len(confetti_colors)]
                size = 4 + (i % 3)

                # Draw rotated rectangle (simplified as oval)
                confetti_id = self.canvas.create_oval(
                    drift_x - size, fall_y - size * 0.5,
                    drift_x + size, fall_y + size * 0.5,
                    fill=color,
                    outline="",
                )
                items.append(confetti_id)

        self.items.extend(items)
        return items

    def draw_stars_burst(
        self,
        x: float,
        y: float,
        count: int = 8,
        radius: float = 60.0,
        phase: float = 0.0,
    ) -> List[int]:
        """
        Draw a burst pattern of stars.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            count: Number of stars.
            radius: Burst radius.
            phase: Animation phase.

        Returns:
            List of canvas item IDs created.
        """
        items = []
        star_color = Colors.SOFT_YELLOW

        for i in range(count):
            angle = (i / count) * 2 * math.pi + phase * 0.5
            # Expand outward
            current_radius = radius * (0.3 + (phase % 1.0) * 0.7)
            star_x = x + math.cos(angle) * current_radius
            star_y = y + math.sin(angle) * current_radius

            # Fade out as expanding
            if (phase % 1.0) < 0.9:
                star_id = self.canvas.create_text(
                    star_x, star_y,
                    text="\u2734",  # Star character
                    font=("Arial", 10),
                    fill=star_color,
                )
                items.append(star_id)

        self.items.extend(items)
        return items

    def clear(self) -> None:
        """Clear all rendered items from canvas."""
        for item_id in self.items:
            self.canvas.delete(item_id)
        self.items.clear()
