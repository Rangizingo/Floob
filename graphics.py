"""
Programmatic pet graphics using Tkinter Canvas.

Creates a cute blob creature with different visual states.
"""

import tkinter as tk
from typing import Optional
import math
import random


class PetGraphics:
    """
    Draws the pet programmatically on a Tkinter Canvas.

    The pet is a cute blob creature with expressive eyes,
    small antenna, and various visual effects for different states.
    """

    # Pet colors
    BODY_COLOR = "#7B68EE"  # Medium slate blue
    BODY_HIGHLIGHT = "#9370DB"  # Medium purple
    BODY_SHADOW = "#6A5ACD"  # Slate blue
    EYE_WHITE = "#FFFFFF"
    EYE_PUPIL = "#2F2F2F"
    EYE_HIGHLIGHT = "#FFFFFF"
    BLUSH_COLOR = "#FFB6C1"  # Light pink
    ANTENNA_COLOR = "#9370DB"
    ANTENNA_TIP = "#FFD700"  # Gold

    def __init__(self, canvas: tk.Canvas, center_x: int = 75, center_y: int = 75) -> None:
        """
        Initialize pet graphics.

        Args:
            canvas: Tkinter canvas to draw on.
            center_x: X coordinate of pet center.
            center_y: Y coordinate of pet center.
        """
        self.canvas = canvas
        self.center_x = center_x
        self.center_y = center_y
        self.body_size = 50  # Base radius

        # Animation state
        self.bounce_offset = 0
        self.blink_state = False
        self.eye_direction = (0, 0)  # Where eyes are looking

        # Effect items (particles, hearts, etc.)
        self.effects: list[int] = []

        # Store canvas item IDs for updates
        self.body_items: list[int] = []
        self.eye_items: list[int] = []
        self.mouth_item: Optional[int] = None
        self.antenna_items: list[int] = []
        self.accessory_items: list[int] = []

    def clear(self) -> None:
        """Clear all drawn items from canvas."""
        self.canvas.delete("all")
        self.body_items.clear()
        self.eye_items.clear()
        self.mouth_item = None
        self.antenna_items.clear()
        self.accessory_items.clear()
        self.effects.clear()

    def draw_idle(self, bounce: float = 0) -> None:
        """
        Draw pet in idle state.

        Args:
            bounce: Vertical bounce offset for animation.
        """
        self.clear()
        self.bounce_offset = bounce

        self._draw_shadow()
        self._draw_antenna()
        self._draw_body()
        self._draw_blush()
        self._draw_eyes(open_amount=1.0 if not self.blink_state else 0.1)
        self._draw_mouth_smile()

    def draw_happy(self, bounce: float = 0) -> None:
        """Draw pet in happy state with hearts."""
        self.clear()
        self.bounce_offset = bounce

        self._draw_shadow()
        self._draw_antenna(wiggle=True)
        self._draw_body()
        self._draw_blush(intense=True)
        self._draw_eyes(open_amount=0.7, happy=True)
        self._draw_mouth_big_smile()
        self._draw_hearts()

    def draw_hungry(self, bounce: float = 0) -> None:
        """Draw pet in hungry state with sweat drop."""
        self.clear()
        self.bounce_offset = bounce

        self._draw_shadow()
        self._draw_antenna(droopy=True)
        self._draw_body()
        self._draw_eyes(open_amount=0.8, sad=True)
        self._draw_mouth_frown()
        self._draw_sweat_drop()

    def draw_tired(self, bounce: float = 0) -> None:
        """Draw pet in tired state with droopy features."""
        self.clear()
        self.bounce_offset = bounce

        self._draw_shadow()
        self._draw_antenna(droopy=True)
        self._draw_body()
        self._draw_eyes(open_amount=0.4, droopy=True)
        self._draw_mouth_sleepy()

    def draw_sleeping(self, zzz_offset: float = 0) -> None:
        """
        Draw pet in sleeping state.

        Args:
            zzz_offset: Animation offset for floating ZZZs.
        """
        self.clear()

        self._draw_shadow()
        self._draw_antenna(droopy=True)
        self._draw_body()
        self._draw_eyes(open_amount=0.0)
        self._draw_mouth_sleepy()
        self._draw_zzz(zzz_offset)

    def draw_eating(self, chomp_phase: float = 0) -> None:
        """
        Draw pet eating.

        Args:
            chomp_phase: 0-1 animation phase for chomping.
        """
        self.clear()

        self._draw_shadow()
        self._draw_antenna()
        self._draw_body()
        self._draw_blush()
        self._draw_eyes(open_amount=0.7, happy=True)
        self._draw_mouth_eating(chomp_phase)
        self._draw_food_particles(chomp_phase)

    def draw_playing(self, spin_angle: float = 0) -> None:
        """
        Draw pet playing/spinning.

        Args:
            spin_angle: Rotation angle in radians.
        """
        self.clear()

        self._draw_shadow()

        # Apply spin transformation by adjusting positions
        offset_x = math.sin(spin_angle) * 5
        offset_y = math.cos(spin_angle * 2) * 3

        self._draw_antenna(wiggle=True)
        self._draw_body()
        self._draw_blush(intense=True)
        self._draw_eyes(open_amount=0.6, direction=(offset_x / 5, 0))
        self._draw_mouth_big_smile()
        self._draw_sparkles(spin_angle)

    def draw_trick(self, spin_angle: float = 0) -> None:
        """
        Draw pet doing a trick (spinning).

        Args:
            spin_angle: Rotation angle for spin effect.
        """
        self.clear()

        self._draw_shadow()

        # More dramatic spin
        squash = abs(math.cos(spin_angle))
        stretch = 2 - squash

        self._draw_body(squash_x=squash * 0.3 + 0.7, stretch_y=stretch * 0.15 + 0.85)
        self._draw_antenna(wiggle=True)
        self._draw_eyes(open_amount=0.5, dizzy=spin_angle > math.pi)
        self._draw_mouth_big_smile()
        self._draw_stars(spin_angle)

    def draw_walking(self, walk_phase: float = 0, direction: int = 1) -> None:
        """
        Draw pet walking.

        Args:
            walk_phase: 0-1 animation phase.
            direction: 1 for right, -1 for left.
        """
        self.clear()

        bounce = math.sin(walk_phase * math.pi * 2) * 3
        squash = 1 + math.sin(walk_phase * math.pi * 2) * 0.1

        self._draw_shadow()
        self._draw_antenna(wiggle=True)
        self._draw_body(squash_x=squash, stretch_y=1/squash)
        self._draw_blush()
        self._draw_eyes(open_amount=1.0, direction=(direction * 0.5, 0))
        self._draw_mouth_smile()

        # Draw little dust particles
        if walk_phase > 0.5:
            self._draw_dust(direction)

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

    def _draw_body(self, squash_x: float = 1.0, stretch_y: float = 1.0) -> None:
        """
        Draw the main body blob.

        Args:
            squash_x: Horizontal scale factor.
            stretch_y: Vertical scale factor.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        rx = self.body_size * squash_x
        ry = self.body_size * stretch_y

        # Main body
        body = self.canvas.create_oval(
            cx - rx, cy - ry,
            cx + rx, cy + ry,
            fill=self.BODY_COLOR,
            outline=self.BODY_SHADOW,
            width=2
        )
        self.body_items.append(body)

        # Highlight (glossy effect)
        highlight = self.canvas.create_oval(
            cx - rx * 0.6, cy - ry * 0.7,
            cx - rx * 0.1, cy - ry * 0.3,
            fill=self.BODY_HIGHLIGHT,
            outline=""
        )
        self.body_items.append(highlight)

    def _draw_antenna(self, wiggle: bool = False, droopy: bool = False) -> None:
        """
        Draw the pet's antenna.

        Args:
            wiggle: Whether antenna should wiggle.
            droopy: Whether antenna should droop.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        # Antenna positions
        wiggle_offset = random.uniform(-3, 3) if wiggle else 0
        droop_offset = 10 if droopy else 0

        # Left antenna
        left_tip_x = cx - 20 + wiggle_offset
        left_tip_y = cy - self.body_size - 20 + droop_offset

        self.canvas.create_line(
            cx - 15, cy - self.body_size + 10,
            left_tip_x, left_tip_y,
            fill=self.ANTENNA_COLOR,
            width=3,
            smooth=True
        )
        self.canvas.create_oval(
            left_tip_x - 5, left_tip_y - 5,
            left_tip_x + 5, left_tip_y + 5,
            fill=self.ANTENNA_TIP,
            outline=""
        )

        # Right antenna
        right_tip_x = cx + 20 - wiggle_offset
        right_tip_y = cy - self.body_size - 20 + droop_offset

        self.canvas.create_line(
            cx + 15, cy - self.body_size + 10,
            right_tip_x, right_tip_y,
            fill=self.ANTENNA_COLOR,
            width=3,
            smooth=True
        )
        self.canvas.create_oval(
            right_tip_x - 5, right_tip_y - 5,
            right_tip_x + 5, right_tip_y + 5,
            fill=self.ANTENNA_TIP,
            outline=""
        )

    def _draw_eyes(
        self,
        open_amount: float = 1.0,
        direction: tuple[float, float] = (0, 0),
        happy: bool = False,
        sad: bool = False,
        droopy: bool = False,
        dizzy: bool = False
    ) -> None:
        """
        Draw the pet's eyes.

        Args:
            open_amount: 0 (closed) to 1 (fully open).
            direction: Tuple of (x, y) for pupil direction.
            happy: Draw happy curved eyes.
            sad: Draw sad eyes.
            droopy: Draw tired droopy eyes.
            dizzy: Draw spiral dizzy eyes.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        eye_y = cy - 5
        eye_spacing = 20
        eye_width = 12
        eye_height = 15 * open_amount

        if happy:
            # Draw happy arc eyes
            for offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_arc(
                    cx + offset - eye_width, eye_y - 8,
                    cx + offset + eye_width, eye_y + 8,
                    start=0, extent=180,
                    style=tk.ARC,
                    outline=self.EYE_PUPIL,
                    width=3
                )
        elif dizzy:
            # Draw spiral dizzy eyes
            for offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_oval(
                    cx + offset - eye_width, eye_y - eye_width,
                    cx + offset + eye_width, eye_y + eye_width,
                    fill=self.EYE_WHITE,
                    outline=self.EYE_PUPIL,
                    width=1
                )
                # Spiral
                self.canvas.create_text(
                    cx + offset, eye_y,
                    text="@",
                    font=("Arial", 12, "bold"),
                    fill=self.EYE_PUPIL
                )
        elif open_amount > 0.1:
            # Draw normal eyes
            for offset in [-eye_spacing, eye_spacing]:
                # Eye white
                self.canvas.create_oval(
                    cx + offset - eye_width, eye_y - eye_height,
                    cx + offset + eye_width, eye_y + eye_height,
                    fill=self.EYE_WHITE,
                    outline=self.EYE_PUPIL,
                    width=1
                )

                # Pupil (follows direction)
                pupil_x = cx + offset + direction[0] * 4
                pupil_y = eye_y + direction[1] * 4
                pupil_size = 5

                if droopy:
                    pupil_y += 3

                self.canvas.create_oval(
                    pupil_x - pupil_size, pupil_y - pupil_size,
                    pupil_x + pupil_size, pupil_y + pupil_size,
                    fill=self.EYE_PUPIL,
                    outline=""
                )

                # Eye highlight
                self.canvas.create_oval(
                    pupil_x - 2, pupil_y - 3,
                    pupil_x + 1, pupil_y,
                    fill=self.EYE_HIGHLIGHT,
                    outline=""
                )

                # Sad eyebrows
                if sad:
                    brow_dir = 1 if offset < 0 else -1
                    self.canvas.create_line(
                        cx + offset - 10, eye_y - eye_height - 5,
                        cx + offset + 10, eye_y - eye_height - 5 + brow_dir * 5,
                        fill=self.BODY_SHADOW,
                        width=2
                    )
        else:
            # Draw closed eyes (sleeping)
            for offset in [-eye_spacing, eye_spacing]:
                self.canvas.create_arc(
                    cx + offset - eye_width, eye_y - 5,
                    cx + offset + eye_width, eye_y + 5,
                    start=0, extent=-180,
                    style=tk.ARC,
                    outline=self.EYE_PUPIL,
                    width=2
                )

    def _draw_blush(self, intense: bool = False) -> None:
        """
        Draw blush marks on cheeks.

        Args:
            intense: More prominent blush when happy.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        blush_y = cy + 5
        blush_spacing = 30
        blush_size = 8 if not intense else 10
        color = self.BLUSH_COLOR if not intense else "#FF69B4"

        for offset in [-blush_spacing, blush_spacing]:
            self.canvas.create_oval(
                cx + offset - blush_size, blush_y - blush_size // 2,
                cx + offset + blush_size, blush_y + blush_size // 2,
                fill=color,
                outline=""
            )

    def _draw_mouth_smile(self) -> None:
        """Draw a simple smile."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        self.canvas.create_arc(
            cx - 12, cy + 5,
            cx + 12, cy + 25,
            start=200, extent=140,
            style=tk.ARC,
            outline=self.EYE_PUPIL,
            width=2
        )

    def _draw_mouth_big_smile(self) -> None:
        """Draw a big happy smile."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        self.canvas.create_arc(
            cx - 15, cy + 3,
            cx + 15, cy + 28,
            start=200, extent=140,
            style=tk.CHORD,
            fill="#FF6B6B",
            outline=self.EYE_PUPIL,
            width=2
        )

    def _draw_mouth_frown(self) -> None:
        """Draw a sad frown."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        self.canvas.create_arc(
            cx - 10, cy + 15,
            cx + 10, cy + 30,
            start=20, extent=140,
            style=tk.ARC,
            outline=self.EYE_PUPIL,
            width=2
        )

    def _draw_mouth_sleepy(self) -> None:
        """Draw a sleepy mouth (small o)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        self.canvas.create_oval(
            cx - 5, cy + 12,
            cx + 5, cy + 22,
            fill="#FF6B6B",
            outline=self.EYE_PUPIL,
            width=1
        )

    def _draw_mouth_eating(self, phase: float) -> None:
        """
        Draw eating/chomping mouth.

        Args:
            phase: Animation phase 0-1.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        # Mouth opens and closes
        open_amount = abs(math.sin(phase * math.pi * 4)) * 10 + 5

        self.canvas.create_oval(
            cx - 10, cy + 10 - open_amount // 2,
            cx + 10, cy + 10 + open_amount,
            fill="#FF6B6B",
            outline=self.EYE_PUPIL,
            width=2
        )

    def _draw_hearts(self) -> None:
        """Draw floating hearts around pet."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        positions = [(-40, -30), (45, -25), (-35, 20)]

        for px, py in positions:
            x, y = cx + px, cy + py
            # Simple heart using two arcs and triangle
            self.canvas.create_text(
                x, y,
                text="\u2665",  # Heart symbol
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
            # Sparkles appear and disappear
            if (phase + i * 0.5) % 1.0 < 0.5:
                x, y = cx + px, cy + py
                self.canvas.create_text(
                    x, y,
                    text="\u2734",  # Sparkle
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
                text="\u2605",  # Star
                font=("Arial", 12),
                fill="#FFD700"
            )

    def _draw_sweat_drop(self) -> None:
        """Draw sweat drop for hungry/worried state."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        # Sweat drop on right side
        drop_x = cx + 40
        drop_y = cy - 20

        # Teardrop shape
        self.canvas.create_polygon(
            drop_x, drop_y - 10,
            drop_x - 5, drop_y,
            drop_x, drop_y + 5,
            drop_x + 5, drop_y,
            fill="#87CEEB",
            outline="#4169E1",
            smooth=True
        )

    def _draw_zzz(self, offset: float) -> None:
        """
        Draw floating ZZZ for sleeping.

        Args:
            offset: Animation offset for floating effect.
        """
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        base_x = cx + 35
        base_y = cy - 30

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
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(15, 25)
                self.canvas.create_oval(
                    cx + offset_x - 3, cy + offset_y - 3,
                    cx + offset_x + 3, cy + offset_y + 3,
                    fill="#FFD700",
                    outline=""
                )

    def _draw_dust(self, direction: int) -> None:
        """Draw dust particles behind walking pet."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        # Dust behind the pet
        dust_x = cx - direction * 45
        dust_y = cy + self.body_size + 5

        for i in range(3):
            offset = random.randint(-5, 5)
            size = random.randint(2, 4)
            self.canvas.create_oval(
                dust_x + offset - size, dust_y + offset - size,
                dust_x + offset + size, dust_y + offset + size,
                fill="#CCCCCC",
                outline=""
            )
