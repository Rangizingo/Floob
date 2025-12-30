"""
Programmatic pet graphics using Tkinter Canvas.

Creates unique creatures with customizable appearance and thought bubbles.
Supports 15 different creature types with distinct visual designs.
"""

import tkinter as tk
from typing import Optional
import math
import random

from pet import (
    PetCustomization, EarStyle, TailStyle, Accessory,
    COLOR_PALETTE, ThoughtBubble
)
from selection import CREATURES


def darken_color(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color by a factor."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color by a factor."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


class PetGraphics:
    """
    Draws the pet programmatically on a Tkinter Canvas.

    The pet is a cute creature with customizable appearance based on
    creature type.
    """

    # Default colors (used when no customization)
    EYE_WHITE = "#FFFFFF"
    EYE_PUPIL = "#2F2F2F"
    EYE_HIGHLIGHT = "#FFFFFF"
    BLUSH_COLOR = "#FFB6C1"  # Light pink
    NOSE_COLOR = "#FF6B6B"

    def __init__(
        self,
        canvas: tk.Canvas,
        center_x: int = 75,
        center_y: int = 75,
        customization: Optional[PetCustomization] = None,
        creature_type: str = "kibble"
    ) -> None:
        """
        Initialize pet graphics.

        Args:
            canvas: Tkinter canvas to draw on.
            center_x: X coordinate of pet center.
            center_y: Y coordinate of pet center.
            customization: Pet customization options.
            creature_type: Type of creature to draw.
        """
        self.canvas = canvas
        self.center_x = center_x
        self.center_y = center_y
        self.body_size = 45  # Base radius

        # Customization
        self.customization = customization or PetCustomization()
        self.creature_type = creature_type
        self._update_colors()

        # Animation state
        self.bounce_offset = 0
        self.blink_state = False
        self.eye_direction = (0, 0)
        self.tail_wag_phase = 0
        self.particle_phase = 0.0

        # Effect items
        self.effects: list[int] = []

        # Store canvas item IDs
        self.body_items: list[int] = []
        self.eye_items: list[int] = []
        self.mouth_item: Optional[int] = None
        self.ear_items: list[int] = []
        self.tail_items: list[int] = []
        self.accessory_items: list[int] = []

    def _update_colors(self) -> None:
        """Update color scheme based on creature type."""
        if self.creature_type in CREATURES:
            data = CREATURES[self.creature_type]
            self.body_color = data["primary"]
            self.secondary_color = data["secondary"]
            self.accent_color = data["accent"]
        else:
            # Fallback to customization colors
            color_name = self.customization.body_color
            self.body_color = COLOR_PALETTE.get(color_name, "#7B68EE")
            self.secondary_color = darken_color(self.body_color)
            self.accent_color = "#FFD700"

        self.body_highlight = lighten_color(self.body_color)
        self.body_shadow = darken_color(self.body_color)

    def set_customization(self, customization: PetCustomization) -> None:
        """Update the pet's customization."""
        self.customization = customization
        self._update_colors()

    def set_creature_type(self, creature_type: str) -> None:
        """Update the creature type."""
        self.creature_type = creature_type
        self._update_colors()

    def clear(self) -> None:
        """Clear all drawn items from canvas."""
        self.canvas.delete("all")
        self.body_items.clear()
        self.eye_items.clear()
        self.mouth_item = None
        self.ear_items.clear()
        self.tail_items.clear()
        self.accessory_items.clear()
        self.effects.clear()

    def draw_thought_bubble(self, thought: ThoughtBubble) -> None:
        """
        Draw a thought bubble above the pet.

        Args:
            thought: ThoughtBubble object with text and icon.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        # Position above pet
        bubble_x = cx + 25
        bubble_y = cy - self.body_size - 45

        opacity = thought.get_opacity()

        # Choose color based on opacity (fade effect via gray)
        if opacity < 1.0:
            gray_val = int(255 * (1 - opacity) + 240 * opacity)
            fill_color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
            text_gray = int(255 * (1 - opacity) + 50 * opacity)
            text_color = f"#{text_gray:02x}{text_gray:02x}{text_gray:02x}"
        else:
            fill_color = "#F5F5F5"
            text_color = "#333333"

        # Draw cloud-like bubble
        # Main bubble
        self.canvas.create_oval(
            bubble_x - 35, bubble_y - 18,
            bubble_x + 35, bubble_y + 18,
            fill=fill_color,
            outline="#CCCCCC",
            width=1
        )

        # Small connecting circles (thought dots)
        dot_positions = [(bubble_x - 20, bubble_y + 22), (bubble_x - 28, bubble_y + 30)]
        for i, (dx, dy) in enumerate(dot_positions):
            size = 5 - i * 2
            self.canvas.create_oval(
                dx - size, dy - size,
                dx + size, dy + size,
                fill=fill_color,
                outline="#CCCCCC"
            )

        # Draw icon if present
        if thought.icon:
            self.canvas.create_text(
                bubble_x - 15, bubble_y,
                text=thought.icon,
                font=("Segoe UI Emoji", 12),
                fill=text_color
            )
            # Draw text to the right of icon
            self.canvas.create_text(
                bubble_x + 8, bubble_y,
                text=thought.text,
                font=("Arial", 8),
                fill=text_color,
                anchor="w"
            )
        else:
            # Center the text
            self.canvas.create_text(
                bubble_x, bubble_y,
                text=thought.text,
                font=("Arial", 9),
                fill=text_color
            )

    # ==================== MAIN DRAWING METHODS ====================

    def draw_idle(self, bounce: float = 0) -> None:
        """Draw pet in idle state."""
        self.clear()
        self.bounce_offset = bounce
        self.particle_phase += 0.1

        self._draw_shadow()
        self._draw_creature_base()
        self._draw_creature_particles_idle()

    def draw_happy(self, bounce: float = 0) -> None:
        """Draw pet in happy state with hearts."""
        self.clear()
        self.bounce_offset = bounce
        self.particle_phase += 0.15

        self._draw_shadow()
        self._draw_creature_base(happy=True)
        self._draw_hearts()

    def draw_hungry(self, bounce: float = 0) -> None:
        """Draw pet in hungry state."""
        self.clear()
        self.bounce_offset = bounce

        self._draw_shadow()
        self._draw_creature_base(sad=True)
        self._draw_sweat_drop()

    def draw_tired(self, bounce: float = 0) -> None:
        """Draw pet in tired state."""
        self.clear()
        self.bounce_offset = bounce

        self._draw_shadow()
        self._draw_creature_base(tired=True)

    def draw_sleeping(self, zzz_offset: float = 0) -> None:
        """Draw pet in sleeping state."""
        self.clear()
        self.particle_phase = zzz_offset

        self._draw_shadow()
        self._draw_creature_base(sleeping=True)
        self._draw_zzz(zzz_offset)

    def draw_eating(self, chomp_phase: float = 0) -> None:
        """Draw pet eating."""
        self.clear()
        self.particle_phase = chomp_phase

        self._draw_shadow()
        self._draw_creature_base(eating=True, phase=chomp_phase)
        self._draw_food_particles(chomp_phase)

    def draw_playing(self, spin_angle: float = 0) -> None:
        """Draw pet playing/spinning."""
        self.clear()
        self.particle_phase = spin_angle

        self._draw_shadow()

        offset_x = math.sin(spin_angle) * 5
        offset_y = math.cos(spin_angle * 2) * 3

        self._draw_creature_base(playing=True, phase=spin_angle)
        self._draw_sparkles(spin_angle)

    def draw_trick(self, spin_angle: float = 0) -> None:
        """Draw pet doing a trick."""
        self.clear()
        self.particle_phase = spin_angle

        self._draw_shadow()
        self._draw_creature_base(trick=True, phase=spin_angle)
        self._draw_stars(spin_angle)

    def draw_walking(self, walk_phase: float = 0, direction: int = 1) -> None:
        """Draw pet walking."""
        self.clear()

        bounce = math.sin(walk_phase * math.pi * 2) * 3
        self.bounce_offset = bounce
        self.particle_phase = walk_phase

        self._draw_shadow()
        self._draw_creature_base(walking=True, direction=direction, phase=walk_phase)

        if walk_phase > 0.5:
            self._draw_dust(direction)

    # ==================== CREATURE BASE DRAWING ====================

    def _draw_creature_base(
        self,
        happy: bool = False,
        sad: bool = False,
        tired: bool = False,
        sleeping: bool = False,
        eating: bool = False,
        playing: bool = False,
        trick: bool = False,
        walking: bool = False,
        direction: int = 1,
        phase: float = 0
    ) -> None:
        """Draw the creature based on its type."""
        method_name = f"_draw_{self.creature_type}"
        draw_method = getattr(self, method_name, self._draw_kibble)
        draw_method(
            happy=happy,
            sad=sad,
            tired=tired,
            sleeping=sleeping,
            eating=eating,
            playing=playing,
            trick=trick,
            walking=walking,
            direction=direction,
            phase=phase
        )

    def _draw_creature_particles_idle(self) -> None:
        """Draw idle particles based on creature type."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        phase = self.particle_phase

        # Electric creatures: sparks
        if self.creature_type in ["sparkit", "flickett"]:
            for i in range(3):
                if (phase + i * 0.5) % 1.0 < 0.3:
                    spark_x = cx + random.randint(-40, 40)
                    spark_y = cy + random.randint(-30, 30)
                    self.canvas.create_text(
                        spark_x, spark_y,
                        text="*",
                        font=("Arial", 8),
                        fill="#FFD700"
                    )

        # Fire creatures: embers
        elif self.creature_type in ["fumewl", "emberpup", "charrix"]:
            for i in range(2):
                if (phase + i * 0.3) % 1.0 < 0.4:
                    ember_x = cx + random.randint(-20, 20)
                    ember_y = cy - s + random.randint(-20, 5)
                    self.canvas.create_oval(
                        ember_x - 2, ember_y - 2,
                        ember_x + 2, ember_y + 2,
                        fill="#FF6B35",
                        outline=""
                    )

        # Water creatures: bubbles
        elif self.creature_type in ["drophin", "tidekit"]:
            for i in range(2):
                bubble_offset = (phase * 20 + i * 15) % 40
                bubble_x = cx + 30 + i * 10
                bubble_y = cy - bubble_offset
                size = 3 + i
                self.canvas.create_oval(
                    bubble_x - size, bubble_y - size,
                    bubble_x + size, bubble_y + size,
                    fill="",
                    outline="#87CEEB",
                    width=1
                )

        # Ghost creature: wisps
        elif self.creature_type == "wispurr":
            for i in range(2):
                wisp_angle = phase + i * math.pi
                wisp_x = cx + math.cos(wisp_angle) * 50
                wisp_y = cy + math.sin(wisp_angle) * 20
                self.canvas.create_oval(
                    wisp_x - 4, wisp_y - 4,
                    wisp_x + 4, wisp_y + 4,
                    fill=lighten_color(self.body_color, 0.5),
                    outline=""
                )

        # Crystal creature: sparkles
        elif self.creature_type == "gemling":
            for i in range(3):
                if (phase + i * 0.4) % 1.0 < 0.25:
                    sparkle_x = cx + random.randint(-40, 40)
                    sparkle_y = cy + random.randint(-40, 30)
                    self.canvas.create_text(
                        sparkle_x, sparkle_y,
                        text="\u2734",
                        font=("Arial", 6),
                        fill="#FF69B4"
                    )

        # Psychic creature: aura
        elif self.creature_type == "soochi":
            glow_size = s + 10 + math.sin(phase) * 5
            self.canvas.create_oval(
                cx - glow_size, cy - glow_size,
                cx + glow_size, cy + glow_size,
                fill="",
                outline=lighten_color(self.accent_color, 0.5),
                width=2,
                dash=(4, 4)
            )

    # ==================== INDIVIDUAL CREATURE DRAWINGS ====================

    def _draw_sparkit(self, **kwargs) -> None:
        """Draw Sparkit - Electric mouse."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        phase = kwargs.get("phase", 0)

        # Tail (behind body)
        self._draw_lightning_tail(cx, cy, s, kwargs.get("playing", False) or kwargs.get("happy", False))

        # Body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Belly highlight
        self.canvas.create_oval(
            cx - s * 0.6, cy - s * 0.1,
            cx + s * 0.6, cy + s * 0.7,
            fill=self.body_highlight,
            outline=""
        )

        # Ears (round with black tips)
        for side in [-1, 1]:
            ear_x = cx + side * s * 0.65
            ear_y = cy - s * 0.65
            # Outer ear
            self.canvas.create_oval(
                ear_x - s * 0.35, ear_y - s * 0.45,
                ear_x + s * 0.35, ear_y + s * 0.25,
                fill=self.body_color,
                outline=self.body_shadow
            )
            # Black tip
            self.canvas.create_oval(
                ear_x - s * 0.2, ear_y - s * 0.45,
                ear_x + s * 0.2, ear_y - s * 0.05,
                fill="#000000",
                outline=""
            )

        # Rosy cheeks that can "glow"
        cheek_color = "#FF1493" if happy else self.accent_color
        for side in [-1, 1]:
            self.canvas.create_oval(
                cx + side * s * 0.5 - 8, cy + s * 0.05 - 6,
                cx + side * s * 0.5 + 8, cy + s * 0.05 + 6,
                fill=cheek_color,
                outline=""
            )

        # Eyes
        self._draw_eyes_standard(cx, cy, s, sleeping=sleeping, happy=happy, sad=sad)

        # Nose
        self.canvas.create_oval(
            cx - 3, cy + s * 0.2 - 2,
            cx + 3, cy + s * 0.2 + 2,
            fill="#FF6B6B",
            outline=""
        )

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, cy, s, phase)
        elif happy:
            self._draw_big_smile(cx, cy, s)
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_fumewl(self, **kwargs) -> None:
        """Draw Fumewl - Fire owl."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sleeping = kwargs.get("sleeping", False)
        phase = kwargs.get("phase", 0)

        # Wing stubs (behind body)
        for side in [-1, 1]:
            self.canvas.create_arc(
                cx + side * s * 0.4, cy - s * 0.2,
                cx + side * s * 1.2, cy + s * 0.6,
                start=90 if side == 1 else 0,
                extent=90,
                style=tk.CHORD,
                fill=self.body_shadow,
                outline=""
            )

        # Body (oval)
        self.canvas.create_oval(
            cx - s * 0.9, cy - s * 0.95,
            cx + s * 0.9, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Belly (lighter flame gradient)
        self.canvas.create_oval(
            cx - s * 0.55, cy - s * 0.2,
            cx + s * 0.55, cy + s * 0.75,
            fill=self.body_highlight,
            outline=""
        )

        # Ear tufts (flame-like)
        for side in [-1, 1]:
            tuft_x = cx + side * s * 0.45
            tuft_y = cy - s * 0.8
            points = [
                tuft_x - side * 5, tuft_y + 12,
                tuft_x, tuft_y - 15,
                tuft_x + side * 8, tuft_y + 8,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=""
            )

        # Big round eyes with ember-orange irises
        eye_y = cy - s * 0.15
        for offset in [-s * 0.3, s * 0.3]:
            # Eye white
            self.canvas.create_oval(
                cx + offset - 12, eye_y - 14,
                cx + offset + 12, eye_y + 14,
                fill="white",
                outline="#2F2F2F"
            )
            if not sleeping:
                # Ember iris
                self.canvas.create_oval(
                    cx + offset - 7, eye_y - 7,
                    cx + offset + 7, eye_y + 7,
                    fill="#FF8C00",
                    outline=""
                )
                # Pupil
                self.canvas.create_oval(
                    cx + offset - 4, eye_y - 4,
                    cx + offset + 4, eye_y + 4,
                    fill="#2F2F2F",
                    outline=""
                )
                # Highlight
                self.canvas.create_oval(
                    cx + offset - 2, eye_y - 6,
                    cx + offset + 2, eye_y - 2,
                    fill="white",
                    outline=""
                )
            else:
                # Sleeping eyes
                self.canvas.create_arc(
                    cx + offset - 8, eye_y - 3,
                    cx + offset + 8, eye_y + 5,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Small beak
        self.canvas.create_polygon(
            cx, cy + s * 0.1,
            cx - 6, cy + s * 0.3,
            cx + 6, cy + s * 0.3,
            fill="#FFD700",
            outline=darken_color("#FFD700")
        )

        # Smoke wisps when idle
        if not kwargs.get("sleeping") and not kwargs.get("eating"):
            for i in range(2):
                smoke_offset = (phase * 30 + i * 20) % 50
                smoke_x = cx - 10 + i * 20
                smoke_y = cy - s - smoke_offset
                smoke_size = 4 + i * 2
                alpha = max(0, 1 - smoke_offset / 50)
                if alpha > 0.3:
                    self.canvas.create_oval(
                        smoke_x - smoke_size, smoke_y - smoke_size,
                        smoke_x + smoke_size, smoke_y + smoke_size,
                        fill="#AAAAAA",
                        outline=""
                    )

    def _draw_drophin(self, **kwargs) -> None:
        """Draw Drophin - Water sprite."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)

        # Wavy tail (behind)
        tail_x = cx + s * 0.6
        tail_y = cy + s * 0.5
        self.canvas.create_line(
            tail_x, tail_y,
            tail_x + 15, tail_y + 5,
            tail_x + 25, tail_y - 5,
            tail_x + 35, tail_y + 3,
            fill=self.secondary_color,
            width=6,
            smooth=True,
            capstyle=tk.ROUND
        )

        # Teardrop body
        points = [
            cx, cy - s,
            cx + s * 0.85, cy + s * 0.3,
            cx + s * 0.55, cy + s,
            cx, cy + s * 0.85,
            cx - s * 0.55, cy + s,
            cx - s * 0.85, cy + s * 0.3,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.body_color,
            outline=self.secondary_color,
            width=2,
            smooth=True
        )

        # Highlight
        self.canvas.create_oval(
            cx - s * 0.3, cy - s * 0.6,
            cx + s * 0.1, cy - s * 0.2,
            fill=self.body_highlight,
            outline=""
        )

        # Forehead gem
        self.canvas.create_oval(
            cx - 6, cy - s * 0.65 - 5,
            cx + 6, cy - s * 0.65 + 5,
            fill=self.accent_color,
            outline=darken_color(self.accent_color)
        )
        # Gem highlight
        self.canvas.create_oval(
            cx - 2, cy - s * 0.65 - 3,
            cx + 1, cy - s * 0.65,
            fill="white",
            outline=""
        )

        # Fin ears
        for side in [-1, 1]:
            self.canvas.create_polygon(
                cx + side * s * 0.4, cy - s * 0.35,
                cx + side * s * 0.65, cy - s * 0.7,
                cx + side * s * 0.85, cy - s * 0.25,
                fill=self.body_color,
                outline=self.secondary_color
            )

        # Eyes
        self._draw_eyes_standard(cx, cy, s, sleeping=sleeping, happy=happy, sad=sad, eye_color=self.secondary_color)

        # Dolphin snout / smile
        if happy:
            self._draw_big_smile(cx, cy, s)
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self.canvas.create_arc(
                cx - s * 0.25, cy + s * 0.15,
                cx + s * 0.25, cy + s * 0.45,
                start=200, extent=140,
                style=tk.ARC,
                outline="#2F2F2F",
                width=2
            )

        # Tiny flipper feet
        for side in [-1, 1]:
            self.canvas.create_oval(
                cx + side * s * 0.3 - 5, cy + s * 0.85,
                cx + side * s * 0.3 + 5, cy + s + 5,
                fill=self.secondary_color,
                outline=""
            )

    def _draw_clovekit(self, **kwargs) -> None:
        """Draw Clovekit - Lucky cat."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        playing = kwargs.get("playing", False)

        # Four-leaf clover tail (behind)
        tail_x = cx + s * 0.9
        tail_y = cy + s * 0.15
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            leaf_cx = tail_x + math.cos(rad) * 10
            leaf_cy = tail_y + math.sin(rad) * 10
            self.canvas.create_oval(
                leaf_cx - 6, leaf_cy - 6,
                leaf_cx + 6, leaf_cy + 6,
                fill=self.secondary_color,
                outline=""
            )
        # Stem
        self.canvas.create_line(
            cx + s * 0.7, cy + s * 0.15,
            tail_x, tail_y,
            fill=self.secondary_color,
            width=3
        )

        # Round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.6, cy - s * 0.1,
            cx + s * 0.6, cy + s * 0.7,
            fill=self.body_highlight,
            outline=""
        )

        # Cat ears (one up, one flopped)
        # Left ear (up)
        points_left = [
            cx - s * 0.5, cy - s * 0.55,
            cx - s * 0.3, cy - s * 1.15,
            cx - s * 0.1, cy - s * 0.55,
        ]
        self.canvas.create_polygon(points_left, fill=self.body_color, outline=self.body_shadow)
        self.canvas.create_polygon(
            cx - s * 0.45, cy - s * 0.55,
            cx - s * 0.3, cy - s * 0.95,
            cx - s * 0.15, cy - s * 0.55,
            fill="#FFB6C1", outline=""
        )

        # Right ear (flopped)
        points_right = [
            cx + s * 0.1, cy - s * 0.55,
            cx + s * 0.45, cy - s * 0.75,
            cx + s * 0.6, cy - s * 0.35,
        ]
        self.canvas.create_polygon(points_right, fill=self.body_color, outline=self.body_shadow)

        # Big golden eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 8, eye_y - 10,
                cx + offset + 8, eye_y + 10,
                fill=self.accent_color,
                outline="#2F2F2F"
            )
            if not sleeping:
                # Vertical pupil
                self.canvas.create_oval(
                    cx + offset - 2, eye_y - 7,
                    cx + offset + 2, eye_y + 7,
                    fill="#2F2F2F",
                    outline=""
                )
                # Highlight
                self.canvas.create_oval(
                    cx + offset - 3, eye_y - 6,
                    cx + offset, eye_y - 2,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 6, eye_y - 2,
                    cx + offset + 6, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Small pink nose
        self.canvas.create_polygon(
            cx, cy + s * 0.15,
            cx - 4, cy + s * 0.25,
            cx + 4, cy + s * 0.25,
            fill="#FFB6C1",
            outline=""
        )

        # Whiskers
        for side in [-1, 1]:
            for dy in [-4, 0, 4]:
                self.canvas.create_line(
                    cx + side * s * 0.2, cy + s * 0.25 + dy,
                    cx + side * s * 0.7, cy + s * 0.2 + dy * 1.3,
                    fill="#333333",
                    width=1
                )

        # Mouth
        if happy:
            self._draw_big_smile(cx, cy, s)
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_emberpup(self, **kwargs) -> None:
        """Draw Emberpup - Fire dog."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        # Wagging flame tail (behind)
        wag = math.sin(phase * 5) * 15 if playing or happy else 0
        tail_x = cx + s * 0.7
        tail_y = cy + s * 0.2
        points = [
            tail_x, tail_y,
            tail_x + 12 + wag, tail_y - 20,
            tail_x + 18 + wag, tail_y - 8,
            tail_x + 8, tail_y,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.secondary_color,
            outline="",
            smooth=True
        )

        # Round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.55, cy - s * 0.05,
            cx + s * 0.55, cy + s * 0.7,
            fill=self.body_highlight,
            outline=""
        )

        # Floppy dog ears with flame tips
        for side in [-1, 1]:
            # Ear base
            self.canvas.create_oval(
                cx + side * s * 0.5, cy - s * 0.75,
                cx + side * s * 1.15, cy + s * 0.05,
                fill=self.body_color,
                outline=self.body_shadow
            )
            # Flame tip
            tip_x = cx + side * s * 0.9
            tip_y = cy - s * 0.6
            self.canvas.create_polygon(
                tip_x - 6, tip_y + 8,
                tip_x, tip_y - 12,
                tip_x + 6, tip_y + 8,
                fill=self.secondary_color,
                outline=""
            )

        # Eyes (happy arcs or open)
        eye_y = cy - s * 0.1
        if happy or playing:
            for offset in [-s * 0.3, s * 0.3]:
                self.canvas.create_arc(
                    cx + offset - 7, eye_y - 7,
                    cx + offset + 7, eye_y + 7,
                    start=0, extent=180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=3
                )
        else:
            self._draw_eyes_standard(cx, cy, s, sleeping=sleeping, sad=sad)

        # Coal black nose
        self.canvas.create_oval(
            cx - 6, cy + s * 0.12 - 4,
            cx + 6, cy + s * 0.12 + 4,
            fill=self.accent_color,
            outline=""
        )

        # Mouth
        if happy or playing:
            # Happy panting
            self.canvas.create_arc(
                cx - 12, cy + s * 0.2,
                cx + 12, cy + s * 0.55,
                start=200, extent=140,
                style=tk.CHORD,
                fill="#FF6B6B",
                outline="#2F2F2F"
            )
            # Tongue
            self.canvas.create_oval(
                cx - 4, cy + s * 0.4,
                cx + 4, cy + s * 0.6,
                fill="#FF6B6B",
                outline=""
            )
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_lunavee(self, **kwargs) -> None:
        """Draw Lunavee - Moon rabbit."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)

        # Fluffy cotton tail (behind)
        tail_x = cx + s * 0.85
        tail_y = cy + s * 0.35
        for i in range(3):
            dx = random.uniform(-3, 3) if not sleeping else i - 1
            dy = random.uniform(-3, 3) if not sleeping else i - 1
            self.canvas.create_oval(
                tail_x + dx - 8, tail_y + dy - 8,
                tail_x + dx + 8, tail_y + dy + 8,
                fill=self.secondary_color,
                outline=""
            )

        # Silvery-blue body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Body highlight
        self.canvas.create_oval(
            cx - s * 0.6, cy - s * 0.1,
            cx + s * 0.6, cy + s * 0.65,
            fill=self.body_highlight,
            outline=""
        )

        # Long upright rabbit ears with star tips
        for side in [-1, 1]:
            ear_x = cx + side * s * 0.3
            # Outer ear
            self.canvas.create_oval(
                ear_x - s * 0.22, cy - s * 1.6,
                ear_x + s * 0.22, cy - s * 0.35,
                fill=self.body_color,
                outline=self.body_shadow
            )
            # Inner ear
            self.canvas.create_oval(
                ear_x - s * 0.12, cy - s * 1.4,
                ear_x + s * 0.12, cy - s * 0.45,
                fill=self.secondary_color,
                outline=""
            )
            # Star tip
            self.canvas.create_text(
                ear_x, cy - s * 1.65,
                text="\u2605",
                font=("Arial", 10),
                fill=self.accent_color
            )

        # Crescent moon marking on forehead
        self.canvas.create_arc(
            cx - 10, cy - s * 0.6,
            cx + 10, cy - s * 0.25,
            start=30, extent=200,
            style=tk.ARC,
            outline=self.accent_color,
            width=3
        )

        # Big sparkly eyes
        eye_y = cy - s * 0.05
        for offset in [-s * 0.3, s * 0.3]:
            # Eye base
            self.canvas.create_oval(
                cx + offset - 9, eye_y - 11,
                cx + offset + 9, eye_y + 11,
                fill="#FFFFFF",
                outline="#2F2F2F"
            )
            if not sleeping:
                # Iris
                self.canvas.create_oval(
                    cx + offset - 5, eye_y - 5,
                    cx + offset + 5, eye_y + 5,
                    fill="#4169E1",
                    outline=""
                )
                # Sparkles
                self.canvas.create_oval(
                    cx + offset - 2, eye_y - 7,
                    cx + offset + 2, eye_y - 3,
                    fill="white",
                    outline=""
                )
                self.canvas.create_oval(
                    cx + offset + 2, eye_y + 2,
                    cx + offset + 4, eye_y + 4,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 7, eye_y - 2,
                    cx + offset + 7, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Small smile
        if happy:
            self._draw_big_smile(cx, cy, s)
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_puffox(self, **kwargs) -> None:
        """Draw Puffox - Cloud fox."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        phase = kwargs.get("phase", 0)

        # Big fluffy tail (behind)
        tail_x = cx + s * 0.8
        tail_y = cy
        for i, (dx, dy, tsz) in enumerate([(0, 0, 15), (8, -12, 12), (15, 5, 10)]):
            color_choice = self.secondary_color if i % 2 else self.body_color
            self.canvas.create_oval(
                tail_x + dx - tsz, tail_y + dy - tsz,
                tail_x + dx + tsz, tail_y + dy + tsz,
                fill=color_choice,
                outline=""
            )

        # Fluffy cloud-shaped body (multiple overlapping ovals)
        for dx, dy, sz in [(-s*0.3, 0, 0.95), (s*0.3, 0, 0.95), (0, -s*0.25, 0.9), (0, s*0.25, 0.9)]:
            self.canvas.create_oval(
                cx + dx - s * sz, cy + dy - s * sz * 0.85,
                cx + dx + s * sz, cy + dy + s * sz * 0.85,
                fill=self.body_color,
                outline=""
            )
        # Main body overlay
        self.canvas.create_oval(
            cx - s * 0.85, cy - s * 0.75,
            cx + s * 0.85, cy + s * 0.85,
            fill=lighten_color(self.body_color, 0.3),
            outline=self.body_shadow
        )

        # Pointy fox ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.55,
                cx + side * s * 0.25, cy - s * 1.1,
                cx + side * s * 0.7, cy - s * 0.45,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=darken_color(self.secondary_color)
            )

        # Swirl patterns on cheeks
        for side in [-1, 1]:
            self.canvas.create_arc(
                cx + side * s * 0.3, cy - s * 0.1,
                cx + side * s * 0.65, cy + s * 0.25,
                start=0 if side == 1 else 180,
                extent=270,
                style=tk.ARC,
                outline=self.accent_color,
                width=2
            )

        # Dreamy half-closed eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.28, s * 0.28]:
            if not sleeping:
                self.canvas.create_arc(
                    cx + offset - 8, cy - s * 0.18,
                    cx + offset + 8, cy + s * 0.05,
                    start=0, extent=180,
                    style=tk.CHORD,
                    fill="#2F2F2F",
                    outline=""
                )
                # Highlight on closed part
                self.canvas.create_arc(
                    cx + offset - 8, cy - s * 0.13,
                    cx + offset + 8, cy + s * 0.05,
                    start=0, extent=180,
                    style=tk.ARC,
                    outline="white",
                    width=1
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 7, eye_y - 2,
                    cx + offset + 7, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Small smile
        self._draw_smile(cx, cy, s)

    def _draw_gemling(self, **kwargs) -> None:
        """Draw Gemling - Crystal creature."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)

        # Faceted tail (behind)
        tail_x = cx + s * 0.75
        tail_y = cy + s * 0.15
        self.canvas.create_polygon(
            tail_x, tail_y,
            tail_x + 12, tail_y - 12,
            tail_x + 25, tail_y,
            tail_x + 12, tail_y + 12,
            fill=self.secondary_color,
            outline=darken_color(self.secondary_color)
        )

        # Crystalline body (hexagonal shape)
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 90)
            points.extend([
                cx + math.cos(angle) * s * 0.95,
                cy + math.sin(angle) * s * 0.95
            ])
        self.canvas.create_polygon(
            points,
            fill=self.body_color,
            outline=self.secondary_color,
            width=2
        )

        # Crystal facet highlights
        self.canvas.create_line(
            cx - s * 0.35, cy - s * 0.5,
            cx, cy + s * 0.25,
            fill=lighten_color(self.body_color, 0.6),
            width=3
        )
        self.canvas.create_line(
            cx + s * 0.35, cy - s * 0.5,
            cx, cy + s * 0.25,
            fill=lighten_color(self.body_color, 0.6),
            width=3
        )

        # Angular crystal ears
        for side in [-1, 1]:
            ear_points = [
                cx + side * s * 0.55, cy - s * 0.65,
                cx + side * s * 0.4, cy - s * 1.2,
                cx + side * s * 0.8, cy - s * 0.85,
            ]
            self.canvas.create_polygon(
                ear_points,
                fill=self.secondary_color,
                outline=darken_color(self.secondary_color)
            )

        # Glowing gem in chest
        self.canvas.create_oval(
            cx - 10, cy + s * 0.05,
            cx + 10, cy + s * 0.4,
            fill=self.accent_color,
            outline=darken_color(self.accent_color),
            width=2
        )
        # Gem glow effect
        self.canvas.create_oval(
            cx - 14, cy + s * 0.01,
            cx + 14, cy + s * 0.44,
            fill="",
            outline=lighten_color(self.accent_color, 0.5),
            width=2,
            dash=(3, 3)
        )
        # Gem highlight
        self.canvas.create_oval(
            cx - 4, cy + s * 0.1,
            cx + 1, cy + s * 0.22,
            fill="white",
            outline=""
        )

        # Crystal eyes (diamond shaped)
        eye_y = cy - s * 0.25
        for offset in [-s * 0.28, s * 0.28]:
            self.canvas.create_polygon(
                cx + offset, eye_y - 8,
                cx + offset - 6, eye_y,
                cx + offset, eye_y + 8,
                cx + offset + 6, eye_y,
                fill=self.accent_color if not sleeping else self.body_color,
                outline="#2F2F2F"
            )
            if not sleeping:
                # Inner sparkle
                self.canvas.create_polygon(
                    cx + offset, eye_y - 4,
                    cx + offset - 2, eye_y,
                    cx + offset, eye_y + 4,
                    cx + offset + 2, eye_y,
                    fill="white",
                    outline=""
                )

        # Small smile
        if happy:
            self._draw_big_smile(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_thornpaw(self, **kwargs) -> None:
        """Draw Thornpaw - Grass cat."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)

        # Vine tail with flower bud (behind)
        self.canvas.create_line(
            cx + s * 0.7, cy + s * 0.1,
            cx + s * 0.9, cy - s * 0.1,
            cx + s * 1.1, cy + s * 0.05,
            fill=self.secondary_color,
            width=5,
            smooth=True
        )
        # Flower bud at end
        self.canvas.create_oval(
            cx + s * 1.0, cy - s * 0.05,
            cx + s * 1.2, cy + s * 0.15,
            fill=self.accent_color,
            outline=darken_color(self.accent_color)
        )

        # Round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.55, cy - s * 0.05,
            cx + s * 0.55, cy + s * 0.7,
            fill=self.body_highlight,
            outline=""
        )

        # Petal collar around neck
        for angle in range(0, 360, 40):
            rad = math.radians(angle)
            petal_cx = cx + math.cos(rad) * s * 0.7
            petal_cy = cy + s * 0.1 + math.sin(rad) * s * 0.45
            self.canvas.create_oval(
                petal_cx - 7, petal_cy - 5,
                petal_cx + 7, petal_cy + 5,
                fill=self.accent_color,
                outline=""
            )

        # Body overlay (to cover petal stems)
        self.canvas.create_oval(
            cx - s * 0.65, cy - s * 0.55,
            cx + s * 0.65, cy + s * 0.65,
            fill=self.body_color,
            outline=""
        )

        # Leaf-shaped ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.35, cy - s * 0.55,
                cx + side * s * 0.2, cy - s * 1.1,
                cx + side * s * 0.5, cy - s * 0.95,
                cx + side * s * 0.65, cy - s * 0.45,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=darken_color(self.secondary_color),
                smooth=True
            )
            # Leaf vein
            self.canvas.create_line(
                cx + side * s * 0.35, cy - s * 0.55,
                cx + side * s * 0.35, cy - s * 0.9,
                fill=darken_color(self.secondary_color),
                width=1
            )

        # Green cat eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 8, eye_y - 8,
                cx + offset + 8, eye_y + 8,
                fill=self.secondary_color,
                outline="#2F2F2F"
            )
            if not sleeping:
                # Vertical pupil
                self.canvas.create_oval(
                    cx + offset - 2, eye_y - 6,
                    cx + offset + 2, eye_y + 6,
                    fill="#2F2F2F",
                    outline=""
                )
                # Highlight
                self.canvas.create_oval(
                    cx + offset - 3, eye_y - 5,
                    cx + offset, eye_y - 1,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 6, eye_y - 2,
                    cx + offset + 6, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Cat nose
        self.canvas.create_polygon(
            cx, cy + s * 0.12,
            cx - 4, cy + s * 0.22,
            cx + 4, cy + s * 0.22,
            fill="#FFB6C1",
            outline=""
        )

        # Whiskers
        for side in [-1, 1]:
            for dy in [-4, 0, 4]:
                self.canvas.create_line(
                    cx + side * s * 0.2, cy + s * 0.25 + dy,
                    cx + side * s * 0.65, cy + s * 0.2 + dy * 1.2,
                    fill="#333333",
                    width=1
                )

        # Mouth
        if happy:
            self._draw_big_smile(cx, cy, s)
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_flickett(self, **kwargs) -> None:
        """Draw Flickett - Electric bunny."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        playing = kwargs.get("playing", False)

        # Lightning bolt feet (behind/at base)
        for side in [-1, 1]:
            foot_x = cx + side * s * 0.4
            foot_y = cy + s * 0.9
            points = [
                foot_x - 4, foot_y - 5,
                foot_x + 5 * side, foot_y - 12,
                foot_x, foot_y - 2,
                foot_x + 8 * side, foot_y + 8,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=""
            )

        # Body with static-fuzzy outline
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2,
            dash=(4, 2) if playing or happy else None
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.55, cy - s * 0.05,
            cx + s * 0.55, cy + s * 0.65,
            fill=self.body_highlight,
            outline=""
        )

        # Long zigzag-tipped rabbit ears
        for side in [-1, 1]:
            ear_x = cx + side * s * 0.3
            # Main ear
            self.canvas.create_oval(
                ear_x - s * 0.2, cy - s * 1.4,
                ear_x + s * 0.2, cy - s * 0.35,
                fill=self.body_color,
                outline=self.body_shadow
            )
            # Inner ear
            self.canvas.create_oval(
                ear_x - s * 0.1, cy - s * 1.2,
                ear_x + s * 0.1, cy - s * 0.45,
                fill=self.body_highlight,
                outline=""
            )
            # Zigzag tip
            tip_y = cy - s * 1.4
            points = [
                ear_x - 6, tip_y + 8,
                ear_x - 3, tip_y - 5,
                ear_x + 3, tip_y + 3,
                ear_x + 6, tip_y - 8,
            ]
            self.canvas.create_line(
                points,
                fill=self.accent_color,
                width=3
            )

        # Spark marks on cheeks
        for side in [-1, 1]:
            spark_x = cx + side * s * 0.55
            spark_y = cy + s * 0.08
            self.canvas.create_text(
                spark_x, spark_y,
                text="\u26A1",
                font=("Segoe UI Emoji", 10),
                fill=self.accent_color
            )

        # Energetic wide eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 8, eye_y - 10,
                cx + offset + 8, eye_y + 10,
                fill="white",
                outline="#2F2F2F"
            )
            if not sleeping:
                self.canvas.create_oval(
                    cx + offset - 5, eye_y - 5,
                    cx + offset + 5, eye_y + 5,
                    fill="#2F2F2F",
                    outline=""
                )
                # Multiple sparkles for energetic look
                self.canvas.create_oval(
                    cx + offset - 2, eye_y - 6,
                    cx + offset + 2, eye_y - 2,
                    fill="white",
                    outline=""
                )
                self.canvas.create_oval(
                    cx + offset + 2, eye_y + 1,
                    cx + offset + 4, eye_y + 3,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 6, eye_y - 2,
                    cx + offset + 6, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Excited open smile
        if not sleeping:
            self.canvas.create_arc(
                cx - 10, cy + s * 0.15,
                cx + 10, cy + s * 0.45,
                start=200, extent=140,
                style=tk.CHORD,
                fill="#FF6B6B",
                outline="#2F2F2F"
            )
        else:
            self._draw_smile(cx, cy, s)

    def _draw_soochi(self, **kwargs) -> None:
        """Draw Soochi - Psychic fox."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        phase = kwargs.get("phase", 0)

        # Wispy floating tail tendrils (behind)
        tail_base_x = cx + s * 0.65
        tail_base_y = cy + s * 0.15
        for i, (curve, length) in enumerate([(15, 30), (-8, 22), (20, 26)]):
            self.canvas.create_line(
                tail_base_x, tail_base_y,
                tail_base_x + length * 0.5, tail_base_y + curve,
                tail_base_x + length, tail_base_y + curve * 0.4,
                fill=self.secondary_color if i % 2 else self.body_color,
                width=5 - i,
                smooth=True
            )

        # Purple gradient body (simulated with overlapping ovals)
        self.canvas.create_oval(
            cx - s, cy - s * 0.9,
            cx + s, cy + s,
            fill=self.secondary_color,
            outline=darken_color(self.secondary_color),
            width=2
        )
        self.canvas.create_oval(
            cx - s * 0.85, cy - s * 0.75,
            cx + s * 0.85, cy + s * 0.88,
            fill=self.body_color,
            outline=""
        )

        # Fox ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.55,
                cx + side * s * 0.2, cy - s * 1.15,
                cx + side * s * 0.7, cy - s * 0.55,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=darken_color(self.secondary_color)
            )
            # Inner ear
            inner_points = [
                cx + side * s * 0.4, cy - s * 0.55,
                cx + side * s * 0.25, cy - s * 0.95,
                cx + side * s * 0.6, cy - s * 0.55,
            ]
            self.canvas.create_polygon(
                inner_points,
                fill=self.body_color,
                outline=""
            )

        # Third eye gem on forehead
        self.canvas.create_oval(
            cx - 6, cy - s * 0.55,
            cx + 6, cy - s * 0.35,
            fill=self.accent_color,
            outline=darken_color(self.accent_color),
            width=2
        )
        # Gem glow
        glow_radius = 3 + math.sin(phase * 2) * 2
        self.canvas.create_oval(
            cx - glow_radius - 6, cy - s * 0.55 - glow_radius + 10,
            cx + glow_radius + 6, cy - s * 0.35 + glow_radius - 10,
            fill="",
            outline=lighten_color(self.accent_color, 0.5),
            width=1
        )

        # Mysterious glowing eyes
        eye_y = cy - s * 0.08
        for offset in [-s * 0.3, s * 0.3]:
            # Glow effect
            self.canvas.create_oval(
                cx + offset - 11, eye_y - 11,
                cx + offset + 11, eye_y + 11,
                fill=lighten_color(self.accent_color, 0.5),
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 8, eye_y - 8,
                cx + offset + 8, eye_y + 8,
                fill="white",
                outline=""
            )
            if not sleeping:
                self.canvas.create_oval(
                    cx + offset - 4, eye_y - 4,
                    cx + offset + 4, eye_y + 4,
                    fill=self.accent_color,
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 6, eye_y - 2,
                    cx + offset + 6, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline=self.accent_color,
                    width=2
                )

        # Mysterious smile
        self._draw_smile(cx, cy, s)

    def _draw_kibble(self, **kwargs) -> None:
        """Draw Kibble - Normal type cutie."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        playing = kwargs.get("playing", False)

        # Curly tail (behind)
        tail_x = cx + s * 0.75
        tail_y = cy + s * 0.15
        self.canvas.create_arc(
            tail_x - 12, tail_y - 12,
            tail_x + 12, tail_y + 12,
            start=0, extent=300,
            style=tk.ARC,
            outline=self.secondary_color,
            width=6
        )

        # Cream round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.secondary_color,
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.6, cy - s * 0.1,
            cx + s * 0.6, cy + s * 0.7,
            fill=lighten_color(self.body_color, 0.4),
            outline=""
        )

        # One floppy ear, one perked ear
        # Left ear (perked)
        points_left = [
            cx - s * 0.5, cy - s * 0.55,
            cx - s * 0.3, cy - s * 1.05,
            cx - s * 0.1, cy - s * 0.55,
        ]
        self.canvas.create_polygon(points_left, fill=self.body_color, outline=self.secondary_color)
        # Inner ear
        self.canvas.create_polygon(
            cx - s * 0.45, cy - s * 0.55,
            cx - s * 0.3, cy - s * 0.85,
            cx - s * 0.15, cy - s * 0.55,
            fill="#FFB6C1", outline=""
        )

        # Right ear (floppy)
        self.canvas.create_oval(
            cx + s * 0.2, cy - s * 0.65,
            cx + s * 0.85, cy + s * 0.05,
            fill=self.body_color,
            outline=self.secondary_color
        )

        # Simple happy eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 6, eye_y - 6,
                cx + offset + 6, eye_y + 6,
                fill="#2F2F2F" if not sleeping else self.body_color,
                outline="#2F2F2F"
            )
            if not sleeping:
                self.canvas.create_oval(
                    cx + offset - 3, eye_y - 4,
                    cx + offset, eye_y - 1,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 5, eye_y - 2,
                    cx + offset + 5, eye_y + 3,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Heart-shaped pink nose
        self.canvas.create_text(
            cx, cy + s * 0.18,
            text="\u2665",
            font=("Arial", 10),
            fill=self.accent_color
        )

        # Tongue out
        if not sleeping and (happy or playing):
            self.canvas.create_oval(
                cx - 5, cy + s * 0.38,
                cx + 5, cy + s * 0.55,
                fill="#FF6B6B",
                outline="#2F2F2F"
            )

        # Mouth
        if sad:
            self._draw_frown(cx, cy, s)
        elif not (happy or playing):
            self._draw_smile(cx, cy, s)

    def _draw_wispurr(self, **kwargs) -> None:
        """Draw Wispurr - Ghost cat."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        phase = kwargs.get("phase", 0)

        # Ghostly aura (outer glow)
        aura_pulse = math.sin(phase * 2) * 5
        self.canvas.create_oval(
            cx - s * 1.15 - aura_pulse, cy - s * 1.05 - aura_pulse,
            cx + s * 1.15 + aura_pulse, cy + s * 1.15 + aura_pulse,
            fill=lighten_color(self.body_color, 0.7),
            outline=""
        )

        # Wispy tail that fades (behind main body but in front of aura)
        tail_x = cx + s * 0.55
        tail_y = cy + s * 0.3
        for i in range(4):
            fade_color = lighten_color(self.body_color, i * 0.15)
            width = 6 - i
            self.canvas.create_line(
                tail_x + i * 8, tail_y,
                tail_x + i * 8 + 15, tail_y - 15 + i * 6,
                fill=fade_color,
                width=width,
                smooth=True
            )

        # Semi-transparent purple body
        self.canvas.create_oval(
            cx - s, cy - s * 0.9,
            cx + s, cy + s * 0.55,
            fill=self.body_color,
            outline=""
        )
        # Wispy bottom (fading triangle)
        points = [
            cx - s * 0.85, cy + s * 0.35,
            cx, cy + s * 1.25,
            cx + s * 0.85, cy + s * 0.35,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.body_color,
            outline="",
            smooth=True
        )

        # Cat ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.55,
                cx + side * s * 0.2, cy - s * 1.05,
                cx + side * s * 0.65, cy - s * 0.55,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=self.body_color
            )

        # Glowing white eyes
        eye_y = cy - s * 0.15
        for offset in [-s * 0.3, s * 0.3]:
            # Glow
            glow_size = 10 + math.sin(phase * 3) * 2
            self.canvas.create_oval(
                cx + offset - glow_size, eye_y - glow_size,
                cx + offset + glow_size, eye_y + glow_size,
                fill=self.accent_color,
                outline=""
            )
            if not sleeping:
                self.canvas.create_oval(
                    cx + offset - 6, eye_y - 6,
                    cx + offset + 6, eye_y + 6,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 5, eye_y - 2,
                    cx + offset + 5, eye_y + 3,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="white",
                    width=2
                )

        # Ghostly smile
        self._draw_smile(cx, cy, s)

    def _draw_tidekit(self, **kwargs) -> None:
        """Draw Tidekit - Water kitten."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)

        # Fish-like tail (behind)
        tail_x = cx + s * 0.75
        tail_y = cy + s * 0.15
        points = [
            tail_x, tail_y,
            tail_x + 22, tail_y - 15,
            tail_x + 15, tail_y,
            tail_x + 22, tail_y + 15,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.secondary_color,
            outline=darken_color(self.secondary_color)
        )

        # Light blue round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.secondary_color,
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.55, cy - s * 0.05,
            cx + s * 0.55, cy + s * 0.65,
            fill=self.body_highlight,
            outline=""
        )

        # Bubble patterns on body
        bubble_positions = [(-s * 0.5, -s * 0.35), (s * 0.45, s * 0.18), (-s * 0.35, s * 0.4), (s * 0.2, -s * 0.15)]
        for bx, by in bubble_positions:
            self.canvas.create_oval(
                cx + bx - 5, cy + by - 5,
                cx + bx + 5, cy + by + 5,
                fill=lighten_color(self.body_color, 0.5),
                outline=self.accent_color
            )

        # Fin-shaped ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.55,
                cx + side * s * 0.2, cy - s * 0.95,
                cx + side * s * 0.5, cy - s * 0.75,
                cx + side * s * 0.75, cy - s * 0.45,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.secondary_color,
                outline=darken_color(self.secondary_color),
                smooth=True
            )

        # Cat eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 8, eye_y - 8,
                cx + offset + 8, eye_y + 8,
                fill=self.secondary_color,
                outline="#2F2F2F"
            )
            if not sleeping:
                self.canvas.create_oval(
                    cx + offset - 3, eye_y - 3,
                    cx + offset + 3, eye_y + 3,
                    fill="#2F2F2F",
                    outline=""
                )
                # Highlight
                self.canvas.create_oval(
                    cx + offset - 3, eye_y - 5,
                    cx + offset, eye_y - 1,
                    fill="white",
                    outline=""
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 6, eye_y - 2,
                    cx + offset + 6, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Cat nose
        self.canvas.create_polygon(
            cx, cy + s * 0.12,
            cx - 4, cy + s * 0.22,
            cx + 4, cy + s * 0.22,
            fill="#FFB6C1",
            outline=""
        )

        # Whiskers
        for side in [-1, 1]:
            for dy in [-3, 3]:
                self.canvas.create_line(
                    cx + side * s * 0.18, cy + s * 0.22 + dy,
                    cx + side * s * 0.65, cy + s * 0.18 + dy * 1.5,
                    fill="#333333",
                    width=1
                )

        # Mouth
        if happy:
            self._draw_big_smile(cx, cy, s)
        elif sad:
            self._draw_frown(cx, cy, s)
        else:
            self._draw_smile(cx, cy, s)

    def _draw_charrix(self, **kwargs) -> None:
        """Draw Charrix - Fire fox."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        sleeping = kwargs.get("sleeping", False)
        happy = kwargs.get("happy", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        # Multiple small flame tails (behind)
        tail_base_x = cx + s * 0.65
        tail_base_y = cy + s * 0.1
        wag = math.sin(phase * 4) * 8 if playing or happy else 0
        for i, (angle, length, width) in enumerate([
            (-35, 28, 6), (0, 35, 8), (35, 28, 6), (-18, 22, 4), (18, 22, 4)
        ]):
            rad = math.radians(angle)
            end_x = tail_base_x + math.cos(rad) * length + wag * math.cos(rad)
            end_y = tail_base_y - math.sin(rad) * length * 0.5
            color_choice = self.secondary_color if i % 2 == 0 else self.accent_color
            self.canvas.create_line(
                tail_base_x, tail_base_y,
                end_x, end_y,
                fill=color_choice,
                width=width,
                capstyle=tk.ROUND
            )

        # Orange-red body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.body_color,
            outline=self.body_shadow,
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.55, cy - s * 0.05,
            cx + s * 0.55, cy + s * 0.65,
            fill=self.body_highlight,
            outline=""
        )

        # Large fox ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.6,
                cx + side * s * 0.15, cy - s * 1.25,
                cx + side * s * 0.7, cy - s * 0.6,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.body_color,
                outline=self.body_shadow
            )
            # Inner ear
            inner_points = [
                cx + side * s * 0.4, cy - s * 0.6,
                cx + side * s * 0.22, cy - s * 1.0,
                cx + side * s * 0.6, cy - s * 0.6,
            ]
            self.canvas.create_polygon(
                inner_points,
                fill=self.secondary_color,
                outline=""
            )

        # Ember freckle marks on cheeks
        for side in [-1, 1]:
            for i in range(3):
                fx = cx + side * (s * 0.42 + i * 6)
                fy = cy + s * 0.02 + (i % 2) * 4
                self.canvas.create_oval(
                    fx - 3, fy - 3,
                    fx + 3, fy + 3,
                    fill=self.accent_color,
                    outline=""
                )

        # Fierce but cute eyes
        eye_y = cy - s * 0.12
        for side_idx, offset in enumerate([-s * 0.3, s * 0.3]):
            self.canvas.create_oval(
                cx + offset - 8, eye_y - 8,
                cx + offset + 8, eye_y + 8,
                fill="white",
                outline="#2F2F2F"
            )
            if not sleeping:
                self.canvas.create_oval(
                    cx + offset - 5, eye_y - 3,
                    cx + offset + 5, eye_y + 6,
                    fill=self.accent_color,
                    outline=""
                )
                self.canvas.create_oval(
                    cx + offset - 2, eye_y,
                    cx + offset + 2, eye_y + 3,
                    fill="#2F2F2F",
                    outline=""
                )
                # Determined eyebrows
                side = -1 if side_idx == 0 else 1
                self.canvas.create_line(
                    cx + offset - 7, eye_y - 12,
                    cx + offset + 7, eye_y - 9 + side * 3,
                    fill=self.body_shadow,
                    width=3
                )
            else:
                self.canvas.create_arc(
                    cx + offset - 6, eye_y - 2,
                    cx + offset + 6, eye_y + 4,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline="#2F2F2F",
                    width=2
                )

        # Small nose
        self.canvas.create_oval(
            cx - 4, cy + s * 0.15 - 3,
            cx + 4, cy + s * 0.15 + 3,
            fill="#2F2F2F",
            outline=""
        )

        # Confident smirk or smile
        if happy:
            self._draw_big_smile(cx, cy, s)
        else:
            self.canvas.create_arc(
                cx - 8, cy + s * 0.2,
                cx + 12, cy + s * 0.45,
                start=200, extent=120,
                style=tk.ARC,
                outline="#2F2F2F",
                width=2
            )

    # ==================== HELPER DRAWING METHODS ====================

    def _draw_shadow(self) -> None:
        """Draw shadow beneath pet."""
        shadow_y = self.center_y + self.body_size + 10 - self.bounce_offset * 0.5
        shadow_width = self.body_size * 0.8
        shadow_height = 8

        self.canvas.create_oval(
            self.center_x - shadow_width,
            shadow_y - shadow_height,
            self.center_x + shadow_width,
            shadow_y + shadow_height,
            fill="#CCCCCC",
            outline=""
        )

    def _draw_lightning_tail(self, cx: int, cy: int, s: float, wagging: bool = False) -> None:
        """Draw a lightning bolt tail for Sparkit."""
        wag = math.sin(self.particle_phase * 5) * 10 if wagging else 0
        tail_x = cx + s * 0.85
        tail_y = cy
        points = [
            tail_x, tail_y - 5,
            tail_x + 12 + wag, tail_y - 12,
            tail_x + 8 + wag * 0.5, tail_y,
            tail_x + 22 + wag, tail_y + 8,
            tail_x + 5, tail_y + 4,
            tail_x + 10, tail_y + 15,
            tail_x, tail_y + 5,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.body_color,
            outline=self.body_shadow
        )

    def _draw_eyes_standard(
        self,
        cx: int,
        cy: int,
        s: float,
        sleeping: bool = False,
        happy: bool = False,
        sad: bool = False,
        eye_color: str = "#2F2F2F"
    ) -> None:
        """Draw standard eyes."""
        eye_y = cy - s * 0.1
        eye_spacing = s * 0.3

        if happy:
            # Happy arc eyes
            for offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_arc(
                    cx + offset - 8, eye_y - 6,
                    cx + offset + 8, eye_y + 8,
                    start=0, extent=180,
                    style=tk.ARC,
                    outline=eye_color,
                    width=3
                )
        elif sleeping:
            # Closed eyes
            for offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_arc(
                    cx + offset - 8, eye_y - 3,
                    cx + offset + 8, eye_y + 5,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline=eye_color,
                    width=2
                )
        else:
            # Open eyes
            for offset in [-eye_spacing, eye_spacing]:
                # Eye white
                self.canvas.create_oval(
                    cx + offset - 8, eye_y - 10,
                    cx + offset + 8, eye_y + 10,
                    fill="white",
                    outline="#2F2F2F"
                )
                # Pupil
                self.canvas.create_oval(
                    cx + offset - 5, eye_y - 5,
                    cx + offset + 5, eye_y + 5,
                    fill=eye_color,
                    outline=""
                )
                # Highlight
                self.canvas.create_oval(
                    cx + offset - 2, eye_y - 6,
                    cx + offset + 2, eye_y - 2,
                    fill="white",
                    outline=""
                )

            # Sad eyebrows
            if sad:
                for idx, offset in enumerate([-eye_spacing, eye_spacing]):
                    brow_dir = 1 if idx == 0 else -1
                    self.canvas.create_line(
                        cx + offset - 8, eye_y - 14,
                        cx + offset + 8, eye_y - 14 + brow_dir * 6,
                        fill=self.body_shadow,
                        width=2
                    )

    def _draw_smile(self, cx: int, cy: int, s: float) -> None:
        """Draw a simple smile."""
        self.canvas.create_arc(
            cx - 10, cy + s * 0.22,
            cx + 10, cy + s * 0.45,
            start=200, extent=140,
            style=tk.ARC,
            outline="#2F2F2F",
            width=2
        )

    def _draw_big_smile(self, cx: int, cy: int, s: float) -> None:
        """Draw a big happy smile."""
        self.canvas.create_arc(
            cx - 14, cy + s * 0.18,
            cx + 14, cy + s * 0.48,
            start=200, extent=140,
            style=tk.CHORD,
            fill="#FF6B6B",
            outline="#2F2F2F",
            width=2
        )

    def _draw_frown(self, cx: int, cy: int, s: float) -> None:
        """Draw a sad frown."""
        self.canvas.create_arc(
            cx - 8, cy + s * 0.35,
            cx + 8, cy + s * 0.5,
            start=20, extent=140,
            style=tk.ARC,
            outline="#2F2F2F",
            width=2
        )

    def _draw_eating_mouth(self, cx: int, cy: int, s: float, phase: float) -> None:
        """Draw eating/chomping mouth."""
        open_amount = abs(math.sin(phase * math.pi * 4)) * 10 + 5

        self.canvas.create_oval(
            cx - 10, cy + s * 0.22 - open_amount // 2,
            cx + 10, cy + s * 0.22 + open_amount,
            fill="#FF6B6B",
            outline="#2F2F2F",
            width=2
        )

    # ==================== EFFECT DRAWINGS ====================

    def _draw_hearts(self) -> None:
        """Draw floating hearts around pet."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        positions = [(-45, -35), (50, -30), (-40, 25)]

        for px, py in positions:
            x, y = cx + px, cy + py
            self.canvas.create_text(
                x, y,
                text="\u2665",
                font=("Arial", 14),
                fill="#FF69B4"
            )

    def _draw_sparkles(self, phase: float) -> None:
        """Draw sparkle effects."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        positions = [
            (-50, -20), (50, -15), (-40, 30), (45, 25), (0, -50)
        ]

        for i, (px, py) in enumerate(positions):
            if (phase + i * 0.5) % 1.0 < 0.5:
                x, y = cx + px, cy + py
                self.canvas.create_text(
                    x, y,
                    text="\u2734",
                    font=("Arial", 10),
                    fill="#FFD700"
                )

    def _draw_stars(self, phase: float) -> None:
        """Draw star effects for tricks."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        for i in range(5):
            angle = phase + i * (math.pi * 2 / 5)
            radius = 60 + math.sin(phase * 3 + i) * 10
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius

            self.canvas.create_text(
                x, y,
                text="\u2605",
                font=("Arial", 12),
                fill="#FFD700"
            )

    def _draw_sweat_drop(self) -> None:
        """Draw sweat drop for hungry/worried state."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        drop_x = cx + 45
        drop_y = cy - 25

        self.canvas.create_polygon(
            drop_x, drop_y - 12,
            drop_x - 6, drop_y,
            drop_x, drop_y + 6,
            drop_x + 6, drop_y,
            fill="#87CEEB",
            outline="#4169E1",
            smooth=True
        )

    def _draw_zzz(self, offset: float) -> None:
        """Draw floating ZZZ for sleeping."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        base_x = cx + 40
        base_y = cy - 35

        sizes = [8, 10, 12]
        for i, size in enumerate(sizes):
            y_offset = -i * 15 - (offset * 20) % 45
            alpha_sim = max(0, 1 - abs(y_offset) / 50)

            if alpha_sim > 0.3:
                self.canvas.create_text(
                    base_x + i * 5, base_y + y_offset,
                    text="Z",
                    font=("Arial", size, "bold"),
                    fill="#6A5ACD"
                )

    def _draw_food_particles(self, phase: float) -> None:
        """Draw food particle effects when eating."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        for i in range(3):
            if (phase * 4 + i * 0.3) % 1.0 < 0.3:
                offset_x = random.randint(-25, 25)
                offset_y = random.randint(18, 30)
                self.canvas.create_oval(
                    cx + offset_x - 4, cy + offset_y - 4,
                    cx + offset_x + 4, cy + offset_y + 4,
                    fill="#FFD700",
                    outline=""
                )

    def _draw_dust(self, direction: int) -> None:
        """Draw dust particles behind walking pet."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        dust_x = cx - direction * 50
        dust_y = cy + self.body_size + 5

        for i in range(3):
            offset = random.randint(-6, 6)
            size = random.randint(2, 5)
            self.canvas.create_oval(
                dust_x + offset - size, dust_y + offset - size,
                dust_x + offset + size, dust_y + offset + size,
                fill="#CCCCCC",
                outline=""
            )
