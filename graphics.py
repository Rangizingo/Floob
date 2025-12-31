"""
Programmatic pet graphics using Tkinter Canvas.

Creates 10 unique properly-shaped creatures with distinct animal silhouettes.
Supports idle, walking, eating, playing, sleeping poses and particle effects.
All creatures use a soft PASTEL color palette.
"""

import tkinter as tk
from typing import Optional
import math
import random

from core.pet import (
    PetCustomization, EarStyle, TailStyle, Accessory,
    COLOR_PALETTE, ThoughtBubble
)
from selection import CREATURES


def darken_color(hex_color: str, factor: float = 0.85) -> str:
    """Darken a hex color by a factor (higher = lighter)."""
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

    Supports 10 unique creature types with proper animal anatomy.
    All creatures use soft pastel colors.
    """

    # Default colors - pastel versions
    EYE_WHITE = "#FFFFFF"
    EYE_PUPIL = "#2F2F2F"
    EYE_HIGHLIGHT = "#FFFFFF"
    BLUSH_COLOR = "#FFD6E0"      # Soft pink blush
    NOSE_COLOR = "#FFADAD"       # Soft red/pink

    def __init__(
        self,
        canvas: tk.Canvas,
        center_x: int = 75,
        center_y: int = 75,
        customization: Optional[PetCustomization] = None,
        creature_type: str = "fennix"
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
        self.body_size = 45

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
            color_name = self.customization.body_color
            self.body_color = COLOR_PALETTE.get(color_name, "#CDB4DB")
            self.secondary_color = darken_color(self.body_color)
            self.accent_color = "#F3E8FF"

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
        """Draw a thought bubble above the pet."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset

        bubble_x = cx + 25
        bubble_y = cy - self.body_size - 45

        opacity = thought.get_opacity()

        if opacity < 1.0:
            gray_val = int(255 * (1 - opacity) + 240 * opacity)
            fill_color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
            text_gray = int(255 * (1 - opacity) + 50 * opacity)
            text_color = f"#{text_gray:02x}{text_gray:02x}{text_gray:02x}"
        else:
            fill_color = "#F5F5F5"
            text_color = "#333333"

        self.canvas.create_oval(
            bubble_x - 35, bubble_y - 18,
            bubble_x + 35, bubble_y + 18,
            fill=fill_color, outline="#CCCCCC", width=1
        )

        dot_positions = [(bubble_x - 20, bubble_y + 22), (bubble_x - 28, bubble_y + 30)]
        for i, (dx, dy) in enumerate(dot_positions):
            size = 5 - i * 2
            self.canvas.create_oval(dx - size, dy - size, dx + size, dy + size, fill=fill_color, outline="#CCCCCC")

        if thought.icon:
            self.canvas.create_text(bubble_x - 15, bubble_y, text=thought.icon, font=("Segoe UI Emoji", 12), fill=text_color)
            self.canvas.create_text(bubble_x + 8, bubble_y, text=thought.text, font=("Arial", 8), fill=text_color, anchor="w")
        else:
            self.canvas.create_text(bubble_x, bubble_y, text=thought.text, font=("Arial", 9), fill=text_color)

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
        draw_method = getattr(self, method_name, self._draw_fennix)
        draw_method(
            happy=happy, sad=sad, tired=tired, sleeping=sleeping,
            eating=eating, playing=playing, trick=trick,
            walking=walking, direction=direction, phase=phase
        )

    def _draw_creature_particles_idle(self) -> None:
        """Draw idle particles based on creature type."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        phase = self.particle_phase

        # Fire creatures: soft flame particles
        if self.creature_type == "fennix":
            for i in range(2):
                if (phase + i * 0.3) % 1.0 < 0.4:
                    flame_x = cx + random.randint(-15, 15)
                    flame_y = cy - s + random.randint(-20, 0)
                    self.canvas.create_oval(flame_x - 3, flame_y - 3, flame_x + 3, flame_y + 3, fill="#FFCDB2", outline="")

        # Water creatures: soft bubbles
        elif self.creature_type == "drizzpup":
            for i in range(2):
                bubble_offset = (phase * 20 + i * 15) % 40
                bubble_x = cx + 35 + i * 8
                bubble_y = cy - bubble_offset
                size = 3 + i
                self.canvas.create_oval(bubble_x - size, bubble_y - size, bubble_x + size, bubble_y + size, fill="", outline="#BDE0FE", width=1)

        # Electric creatures: soft sparks
        elif self.creature_type == "sparkrat":
            for i in range(3):
                if (phase + i * 0.5) % 1.0 < 0.3:
                    spark_x = cx + random.randint(-40, 40)
                    spark_y = cy + random.randint(-30, 30)
                    self.canvas.create_text(spark_x, spark_y, text="*", font=("Arial", 8), fill="#FFF3B0")

        # Ghost creature: soft wisps
        elif self.creature_type == "shimi":
            for i in range(2):
                wisp_angle = phase + i * math.pi
                wisp_x = cx + math.cos(wisp_angle) * 50
                wisp_y = cy + math.sin(wisp_angle) * 20
                self.canvas.create_oval(wisp_x - 4, wisp_y - 4, wisp_x + 4, wisp_y + 4, fill=lighten_color(self.body_color, 0.5), outline="")

        # Spirit fox: soft aura
        elif self.creature_type == "kitsumi":
            glow_size = s + 10 + math.sin(phase) * 5
            self.canvas.create_oval(cx - glow_size, cy - glow_size, cx + glow_size, cy + glow_size, fill="", outline=lighten_color(self.secondary_color, 0.5), width=2, dash=(4, 4))

        # Dragon: soft smoke puffs
        elif self.creature_type == "drakeling":
            for i in range(2):
                smoke_offset = (phase * 25 + i * 18) % 45
                smoke_x = cx - 5 + i * 15
                smoke_y = cy - s * 0.7 - smoke_offset
                smoke_size = 4 + i * 2
                if smoke_offset < 35:
                    self.canvas.create_oval(smoke_x - smoke_size, smoke_y - smoke_size, smoke_x + smoke_size, smoke_y + smoke_size, fill="#D4D4D4", outline="")

        # Grass kitten: soft leaf particles
        elif self.creature_type == "leafkit":
            for i in range(2):
                if (phase + i * 0.4) % 1.0 < 0.3:
                    leaf_x = cx + random.randint(-35, 35)
                    leaf_y = cy + random.randint(-35, 25)
                    self.canvas.create_text(leaf_x, leaf_y, text="*", font=("Arial", 6), fill="#95D5B2")

    # ==================== INDIVIDUAL CREATURE DRAWINGS ====================

    def _draw_fennix(self, **kwargs) -> None:
        """Draw Fennix - Fire Fennec Fox with HUGE ears (pastel coral)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        flame = self.secondary_color
        belly = self.accent_color
        outline = self.body_shadow

        # Tail wagging animation
        wag = math.sin(phase * 5) * 10 if playing or happy else 0

        # Fluffy tail curled around (behind body) - properly attached
        tail_points = [
            cx + s * 0.45, cy + s * 0.25,
            cx + s * 0.85 + wag * 0.3, cy + s * 0.05,
            cx + s * 0.8 + wag * 0.5, cy - s * 0.3,
            cx + s * 0.55, cy - s * 0.1,
        ]
        self.canvas.create_polygon(tail_points, fill=body, outline=outline, smooth=True, width=2)
        # Flame tip on tail
        self.canvas.create_oval(cx + s * 0.6 + wag * 0.3, cy - s * 0.4, cx + s * 0.9 + wag * 0.3, cy - s * 0.1, fill=flame, outline="")

        # Body - horizontal oval (sitting fox body)
        self.canvas.create_oval(cx - s * 0.6, cy - s * 0.1, cx + s * 0.5, cy + s * 0.55, fill=body, outline=outline, width=2)

        # Belly - centered on body
        self.canvas.create_oval(cx - s * 0.38, cy + s * 0.02, cx + s * 0.32, cy + s * 0.45, fill=belly, outline="")

        # Head - centered above body
        head_cx = cx - s * 0.02
        head_cy = cy - s * 0.2
        self.canvas.create_oval(head_cx - s * 0.42, head_cy - s * 0.35, head_cx + s * 0.42, head_cy + s * 0.2, fill=body, outline=outline, width=2)

        # HUGE fennec ears (triangles) - properly centered on head
        ear_base_y = head_cy - s * 0.2
        ear_tip_y = head_cy - s * 1.0

        # Left ear
        ear_l = [head_cx - s * 0.32, ear_base_y, head_cx - s * 0.45, ear_tip_y, head_cx - s * 0.05, ear_base_y]
        self.canvas.create_polygon(ear_l, fill=body, outline=outline, width=2)
        inner_l = [head_cx - s * 0.28, ear_base_y, head_cx - s * 0.4, ear_tip_y + s * 0.15, head_cx - s * 0.1, ear_base_y]
        self.canvas.create_polygon(inner_l, fill=flame, outline="")

        # Right ear
        ear_r = [head_cx + s * 0.05, ear_base_y, head_cx + s * 0.45, ear_tip_y, head_cx + s * 0.32, ear_base_y]
        self.canvas.create_polygon(ear_r, fill=body, outline=outline, width=2)
        inner_r = [head_cx + s * 0.1, ear_base_y, head_cx + s * 0.4, ear_tip_y + s * 0.15, head_cx + s * 0.28, ear_base_y]
        self.canvas.create_polygon(inner_r, fill=flame, outline="")

        # Eyes - centered on head
        self._draw_fox_eyes(head_cx, head_cy, s, sleeping=sleeping, happy=happy, sad=sad)

        # Small black nose - centered
        nose_y = head_cy + s * 0.05
        self.canvas.create_oval(head_cx - 4, nose_y - 3, head_cx + 4, nose_y + 3, fill="#2F2F2F", outline="")

        # Mouth
        if eating:
            self._draw_eating_mouth(head_cx, head_cy, s, phase)
        elif happy:
            self._draw_big_smile(head_cx, head_cy, s)
        elif sad:
            self._draw_frown(head_cx, head_cy, s)
        else:
            self._draw_smile(head_cx, head_cy, s)

        # Front paws - positioned at bottom
        paw_y = cy + s * 0.42
        self.canvas.create_oval(cx - s * 0.38, paw_y, cx - s * 0.15, paw_y + s * 0.18, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.08, paw_y, cx + s * 0.32, paw_y + s * 0.18, fill=body, outline=outline)

    def _draw_hopplet(self, **kwargs) -> None:
        """Draw Hopplet - Chubby bunny with floppy ears (soft cream/pink)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        inner = self.secondary_color
        belly_c = self.accent_color
        outline = self.body_shadow

        # Cotton puff tail (behind) - properly positioned
        self.canvas.create_oval(cx + s * 0.42, cy + s * 0.12, cx + s * 0.7, cy + s * 0.45, fill=belly_c, outline=outline)

        # Round chubby body
        self.canvas.create_oval(cx - s * 0.55, cy - s * 0.3, cx + s * 0.55, cy + s * 0.6, fill=body, outline=outline, width=2)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.38, cy - s * 0.08, cx + s * 0.38, cy + s * 0.45, fill=belly_c, outline="")

        # Head - centered above body
        head_cy = cy - s * 0.35
        self.canvas.create_oval(cx - s * 0.42, head_cy - s * 0.32, cx + s * 0.42, head_cy + s * 0.32, fill=body, outline=outline, width=2)

        # Long floppy ears (hanging down) with twitch animation - properly attached
        ear_twitch = math.sin(phase * 8) * 3 if playing else 0
        ear_top_y = head_cy - s * 0.22
        ear_bottom_y = cy + s * 0.3

        # Left ear
        self.canvas.create_oval(cx - s * 0.58, ear_top_y + ear_twitch, cx - s * 0.26, ear_bottom_y, fill=body, outline=outline)
        self.canvas.create_oval(cx - s * 0.52, ear_top_y + s * 0.1 + ear_twitch, cx - s * 0.32, ear_bottom_y - s * 0.12, fill=inner, outline="")

        # Right ear
        self.canvas.create_oval(cx + s * 0.26, ear_top_y - ear_twitch, cx + s * 0.58, ear_bottom_y, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.32, ear_top_y + s * 0.1 - ear_twitch, cx + s * 0.52, ear_bottom_y - s * 0.12, fill=inner, outline="")

        # Big oval feet in front - positioned at bottom
        feet_y = cy + s * 0.38
        self.canvas.create_oval(cx - s * 0.48, feet_y, cx - s * 0.1, feet_y + s * 0.25, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.1, feet_y, cx + s * 0.48, feet_y + s * 0.25, fill=body, outline=outline)

        # Eyes - centered on head
        self._draw_round_eyes(cx, head_cy, s, sleeping=sleeping, happy=happy, sad=sad)

        # Twitchy nose (pink oval with animation) - centered
        nose_y = head_cy + s * 0.18 + (math.sin(phase * 10) * 2 if not sleeping else 0)
        self.canvas.create_oval(cx - 5, nose_y - 4, cx + 5, nose_y + 4, fill=inner, outline="")

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, head_cy + s * 0.12, s, phase)
        elif happy:
            self._draw_big_smile(cx, head_cy + s * 0.12, s)
        elif sad:
            self._draw_frown(cx, head_cy + s * 0.12, s)
        else:
            self._draw_smile(cx, head_cy + s * 0.12, s)

    def _draw_drizzpup(self, **kwargs) -> None:
        """Draw Drizzpup - Water puppy with fin ears (soft sky blue)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        fins = self.secondary_color
        belly = self.accent_color
        outline = self.body_shadow

        # Wagging water droplet tail - smooth animation
        wag = math.sin(phase * 6) * 15 if playing or happy else 0
        tail_pts = [cx + s * 0.45, cy + s * 0.2, cx + s * 0.8 + wag * 0.5, cy - s * 0.1, cx + s * 0.75 + wag * 0.3, cy + s * 0.35]
        self.canvas.create_polygon(tail_pts, fill=body, outline=outline, smooth=True)
        self.canvas.create_oval(cx + s * 0.6 + wag * 0.3, cy - s * 0.25, cx + s * 0.85 + wag * 0.3, cy + s * 0.02, fill=fins, outline="")

        # Body - sitting puppy
        self.canvas.create_oval(cx - s * 0.52, cy - s * 0.15, cx + s * 0.52, cy + s * 0.55, fill=body, outline=outline, width=2)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.32, cy, cx + s * 0.32, cy + s * 0.42, fill=belly, outline="")

        # Head - centered above body
        head_cy = cy - s * 0.28
        self.canvas.create_oval(cx - s * 0.42, head_cy - s * 0.3, cx + s * 0.42, head_cy + s * 0.28, fill=body, outline=outline, width=2)

        # Floppy fin-like ears - properly positioned
        fin_l = [cx - s * 0.38, head_cy - s * 0.12, cx - s * 0.72, head_cy - s * 0.35, cx - s * 0.68, head_cy + s * 0.08, cx - s * 0.38, head_cy + s * 0.15]
        self.canvas.create_polygon(fin_l, fill=fins, outline=darken_color(fins), smooth=True)

        fin_r = [cx + s * 0.38, head_cy - s * 0.12, cx + s * 0.72, head_cy - s * 0.35, cx + s * 0.68, head_cy + s * 0.08, cx + s * 0.38, head_cy + s * 0.15]
        self.canvas.create_polygon(fin_r, fill=darken_color(fins), smooth=True)

        # Eyes - centered on head
        self._draw_puppy_eyes(cx, head_cy - s * 0.05, s, sleeping=sleeping, happy=happy or playing, sad=sad)

        # Nose - centered
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 5, nose_y, cx + 5, nose_y + s * 0.1, fill="#2F2F2F", outline="")

        # Tongue out when happy/playing
        if (happy or playing) and not sleeping and not eating:
            tongue_y = head_cy + s * 0.25
            self.canvas.create_oval(cx - 5, tongue_y, cx + 5, tongue_y + s * 0.15, fill="#FFADAD", outline="#2F2F2F")

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, head_cy + s * 0.08, s, phase)
        elif not (happy or playing):
            if sad:
                self._draw_frown(cx, head_cy + s * 0.08, s)
            else:
                self._draw_smile(cx, head_cy + s * 0.08, s)

        # Front paws - positioned at bottom
        paw_y = cy + s * 0.42
        self.canvas.create_oval(cx - s * 0.38, paw_y, cx - s * 0.15, paw_y + s * 0.18, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.15, paw_y, cx + s * 0.38, paw_y + s * 0.18, fill=body, outline=outline)

    def _draw_owlette(self, **kwargs) -> None:
        """Draw Owlette - Baby owl with huge round eyes (soft tan/cream)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        feathers = self.secondary_color
        belly = self.accent_color
        outline = self.body_shadow
        beak_color = "#FFCB77"  # Soft yellow beak

        # Wing stubs (behind body) with flap animation
        wing_flap = math.sin(phase * 4) * 8 if playing else 0
        self.canvas.create_oval(cx - s * 0.72, cy - s * 0.1 - wing_flap, cx - s * 0.38, cy + s * 0.38, fill=feathers, outline=outline)
        self.canvas.create_oval(cx + s * 0.38, cy - s * 0.1 + wing_flap, cx + s * 0.72, cy + s * 0.38, fill=feathers, outline=outline)

        # Round owl body - centered
        self.canvas.create_oval(cx - s * 0.48, cy - s * 0.42, cx + s * 0.48, cy + s * 0.55, fill=body, outline=outline, width=2)

        # Belly/chest feathers - centered
        self.canvas.create_oval(cx - s * 0.32, cy - s * 0.18, cx + s * 0.32, cy + s * 0.42, fill=belly, outline="")

        # Small triangular ear tufts - centered on head
        tuft_base_y = cy - s * 0.35
        tuft_tip_y = cy - s * 0.68

        tuft_l = [cx - s * 0.28, tuft_base_y, cx - s * 0.38, tuft_tip_y, cx - s * 0.1, tuft_base_y]
        self.canvas.create_polygon(tuft_l, fill=body, outline=outline)

        tuft_r = [cx + s * 0.1, tuft_base_y, cx + s * 0.38, tuft_tip_y, cx + s * 0.28, tuft_base_y]
        self.canvas.create_polygon(tuft_r, fill=body, outline=outline)

        # HUGE circular eyes - centered
        self._draw_owl_eyes(cx, cy - s * 0.02, s, sleeping=sleeping, happy=happy, sad=sad, feathers=feathers)

        # Small beak - centered below eyes
        beak_y = cy + s * 0.18
        if eating:
            open_amt = abs(math.sin(phase * math.pi * 4)) * 5
            beak_pts = [cx, beak_y - s * 0.05, cx - 8, beak_y + s * 0.1 + open_amt, cx + 8, beak_y + s * 0.1 + open_amt]
        else:
            beak_pts = [cx, beak_y - s * 0.05, cx - 6, beak_y + s * 0.1, cx + 6, beak_y + s * 0.1]
        self.canvas.create_polygon(beak_pts, fill=beak_color, outline=darken_color(beak_color))

        # Tiny feet - centered at bottom
        feet_y = cy + s * 0.48
        self.canvas.create_oval(cx - s * 0.2, feet_y, cx - s * 0.05, feet_y + s * 0.12, fill=beak_color, outline="")
        self.canvas.create_oval(cx + s * 0.05, feet_y, cx + s * 0.2, feet_y + s * 0.12, fill=beak_color, outline="")

    def _draw_kitsumi(self, **kwargs) -> None:
        """Draw Kitsumi - Spirit fox with multiple wispy tails (soft lavender)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        glow = self.secondary_color
        light = self.accent_color
        outline = self.body_shadow

        # Multiple wispy tails (3 tails - behind) with elegant sway
        sway = math.sin(phase * 2) * 10
        for i, angle in enumerate([-30, 0, 30]):
            rad = math.radians(angle + sway)
            tail_pts = [
                cx + s * 0.42, cy + s * 0.2,
                cx + s * 0.7 + math.cos(rad) * s * 0.22, cy + math.sin(rad) * s * 0.32,
                cx + s * 0.9 + math.cos(rad) * s * 0.28, cy - s * 0.22 + math.sin(rad) * s * 0.22,
            ]
            self.canvas.create_line(tail_pts, fill=glow if i == 1 else body, width=8 - i * 2, smooth=True)

        # Elegant fox body - slender
        self.canvas.create_oval(cx - s * 0.48, cy - s * 0.12, cx + s * 0.48, cy + s * 0.5, fill=body, outline=outline, width=2)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.28, cy, cx + s * 0.28, cy + s * 0.38, fill=light, outline="")

        # Head - elegant and centered
        head_cy = cy - s * 0.32
        self.canvas.create_oval(cx - s * 0.38, head_cy - s * 0.28, cx + s * 0.38, head_cy + s * 0.25, fill=body, outline=outline, width=2)

        # Pointed elegant ears - symmetrical
        ear_base_y = head_cy - s * 0.15
        ear_tip_y = head_cy - s * 0.72

        ear_l = [cx - s * 0.28, ear_base_y, cx - s * 0.42, ear_tip_y, cx - s * 0.05, ear_base_y]
        self.canvas.create_polygon(ear_l, fill=body, outline=outline)
        self.canvas.create_polygon([cx - s * 0.24, ear_base_y, cx - s * 0.36, ear_tip_y + s * 0.12, cx - s * 0.1, ear_base_y], fill=glow, outline="")

        ear_r = [cx + s * 0.05, ear_base_y, cx + s * 0.42, ear_tip_y, cx + s * 0.28, ear_base_y]
        self.canvas.create_polygon(ear_r, fill=body, outline=outline)
        self.canvas.create_polygon([cx + s * 0.1, ear_base_y, cx + s * 0.36, ear_tip_y + s * 0.12, cx + s * 0.24, ear_base_y], fill=glow, outline="")

        # Glowing eyes - centered
        self._draw_glowing_eyes(cx, head_cy - s * 0.02, s, sleeping=sleeping, happy=happy, sad=sad, glow_color=glow)

        # Small nose - centered
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 4, nose_y, cx + 4, nose_y + s * 0.08, fill="#2F2F2F", outline="")

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, head_cy + s * 0.1, s, phase)
        elif happy:
            self._draw_big_smile(cx, head_cy + s * 0.1, s)
        elif sad:
            self._draw_frown(cx, head_cy + s * 0.1, s)
        else:
            self._draw_smile(cx, head_cy + s * 0.1, s)

        # Front paws - positioned at bottom
        paw_y = cy + s * 0.38
        self.canvas.create_oval(cx - s * 0.28, paw_y, cx - s * 0.1, paw_y + s * 0.15, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.1, paw_y, cx + s * 0.28, paw_y + s * 0.15, fill=body, outline=outline)

    def _draw_pengi(self, **kwargs) -> None:
        """Draw Pengi - Tiny penguin standing upright (soft blue-gray)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        walking = kwargs.get("walking", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        belly = self.secondary_color
        accent = self.accent_color
        outline = self.body_shadow
        cheek_color = "#FFD6E0"  # Soft pink cheeks
        feet_color = "#FFB997"   # Soft coral feet

        # Waddle animation
        waddle = math.sin(phase * 8) * 5 if walking or playing else 0

        # Body - oval standing upright, centered
        self.canvas.create_oval(cx - s * 0.42 + waddle, cy - s * 0.5, cx + s * 0.42 + waddle, cy + s * 0.52, fill=body, outline=outline, width=2)

        # White belly (distinctive penguin marking) - centered
        self.canvas.create_oval(cx - s * 0.3 + waddle, cy - s * 0.32, cx + s * 0.3 + waddle, cy + s * 0.42, fill=belly, outline="")

        # Flippers out to sides with wave animation
        flip_wave = math.sin(phase * 5) * 10 if playing else 0
        flip_l = [cx - s * 0.38 + waddle, cy - s * 0.12, cx - s * 0.68 + waddle, cy + s * 0.08 - flip_wave, cx - s * 0.58 + waddle, cy + s * 0.38, cx - s * 0.38 + waddle, cy + s * 0.22]
        self.canvas.create_polygon(flip_l, fill=body, outline=outline, smooth=True)

        flip_r = [cx + s * 0.38 + waddle, cy - s * 0.12, cx + s * 0.68 + waddle, cy + s * 0.08 + flip_wave, cx + s * 0.58 + waddle, cy + s * 0.38, cx + s * 0.38 + waddle, cy + s * 0.22]
        self.canvas.create_polygon(flip_r, fill=body, outline=outline, smooth=True)

        # Eyes - centered
        self._draw_round_eyes(cx + waddle, cy - s * 0.12, s * 0.8, sleeping=sleeping, happy=happy, sad=sad)

        # Orange beak - centered
        beak_y = cy + s * 0.05
        if eating:
            open_amt = abs(math.sin(phase * math.pi * 4)) * 5
            beak_pts = [cx + waddle, beak_y - s * 0.08, cx - 8 + waddle, beak_y + s * 0.08 + open_amt, cx + 8 + waddle, beak_y + s * 0.08 + open_amt]
        else:
            beak_pts = [cx + waddle, beak_y - s * 0.08, cx - 7 + waddle, beak_y + s * 0.08, cx + 7 + waddle, beak_y + s * 0.08]
        self.canvas.create_polygon(beak_pts, fill=accent, outline=darken_color(accent))

        # Rosy cheeks - symmetrical
        cheek_y = cy - s * 0.02
        self.canvas.create_oval(cx - s * 0.28 + waddle, cheek_y - s * 0.05, cx - s * 0.12 + waddle, cheek_y + s * 0.05, fill=cheek_color, outline="")
        self.canvas.create_oval(cx + s * 0.12 + waddle, cheek_y - s * 0.05, cx + s * 0.28 + waddle, cheek_y + s * 0.05, fill=cheek_color, outline="")

        # Orange feet - centered at bottom
        feet_y = cy + s * 0.42
        self.canvas.create_oval(cx - s * 0.28 + waddle, feet_y, cx - s * 0.05 + waddle, feet_y + s * 0.18, fill=feet_color, outline=darken_color(feet_color))
        self.canvas.create_oval(cx + s * 0.05 + waddle, feet_y, cx + s * 0.28 + waddle, feet_y + s * 0.18, fill=feet_color, outline=darken_color(feet_color))

    def _draw_leafkit(self, **kwargs) -> None:
        """Draw Leafkit - Grass kitten with leaf ears and vine tail (soft green/mint)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        stripes = self.secondary_color
        flower = self.accent_color
        outline = self.body_shadow

        # Vine tail with leaf (behind) - sway animation, properly attached
        sway = math.sin(phase * 3) * 8
        self.canvas.create_line(cx + s * 0.38, cy + s * 0.2, cx + s * 0.62 + sway * 0.3, cy + s * 0.02, cx + s * 0.82 + sway * 0.5, cy + s * 0.12, fill=stripes, width=5, smooth=True)
        # Leaf at end - properly shaped
        leaf_pts = [cx + s * 0.78 + sway * 0.5, cy + s * 0.08, cx + s * 1.0 + sway * 0.5, cy - s * 0.1, cx + s * 0.88 + sway * 0.5, cy + s * 0.22]
        self.canvas.create_polygon(leaf_pts, fill=body, outline=stripes)

        # Cat body curled - centered
        self.canvas.create_oval(cx - s * 0.48, cy - s * 0.12, cx + s * 0.42, cy + s * 0.52, fill=body, outline=outline, width=2)

        # Stripes on body
        self.canvas.create_arc(cx - s * 0.32, cy + s * 0.02, cx + s * 0.22, cy + s * 0.32, start=0, extent=180, style=tk.ARC, outline=stripes, width=3)

        # Head - centered
        head_cy = cy - s * 0.32
        self.canvas.create_oval(cx - s * 0.38, head_cy - s * 0.28, cx + s * 0.38, head_cy + s * 0.25, fill=body, outline=outline, width=2)

        # Leaf-shaped ears - properly shaped
        ear_base_y = head_cy - s * 0.15

        leaf_ear_l = [cx - s * 0.28, ear_base_y, cx - s * 0.48, ear_base_y - s * 0.38, cx - s * 0.18, ear_base_y - s * 0.3, cx - s * 0.05, ear_base_y]
        self.canvas.create_polygon(leaf_ear_l, fill=body, outline=stripes, smooth=True)

        leaf_ear_r = [cx + s * 0.05, ear_base_y, cx + s * 0.18, ear_base_y - s * 0.3, cx + s * 0.48, ear_base_y - s * 0.38, cx + s * 0.28, ear_base_y]
        self.canvas.create_polygon(leaf_ear_r, fill=body, outline=stripes, smooth=True)

        # Flower bud on head (blooms when happy) - centered
        flower_y = head_cy - s * 0.52
        if happy:
            # Bloomed flower
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                px = cx + math.cos(rad) * 8
                py = flower_y + math.sin(rad) * 8
                self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill=flower, outline="")
            self.canvas.create_oval(cx - 4, flower_y - 4, cx + 4, flower_y + 4, fill="#FFF3B0", outline="")
        else:
            self.canvas.create_oval(cx - s * 0.1, flower_y - s * 0.08, cx + s * 0.1, flower_y + s * 0.08, fill=flower, outline=darken_color(flower))

        # Cat eyes (green with slit pupils) - centered
        self._draw_cat_eyes(cx, head_cy - s * 0.02, s, sleeping=sleeping, happy=happy, sad=sad, iris_color=stripes)

        # Pink nose - centered
        nose_y = head_cy + s * 0.12
        nose_pts = [cx, nose_y - s * 0.05, cx - 5, nose_y + s * 0.05, cx + 5, nose_y + s * 0.05]
        self.canvas.create_polygon(nose_pts, fill="#FFB6C1", outline="")

        # Whiskers
        for side in [-1, 1]:
            for dy in [-4, 0, 4]:
                self.canvas.create_line(cx + side * s * 0.18, head_cy + s * 0.12 + dy, cx + side * s * 0.55, head_cy + s * 0.08 + dy * 1.2, fill="#666666", width=1)

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, head_cy + s * 0.1, s, phase)
        elif happy:
            self._draw_big_smile(cx, head_cy + s * 0.1, s)
        elif sad:
            self._draw_frown(cx, head_cy + s * 0.1, s)
        else:
            self._draw_smile(cx, head_cy + s * 0.1, s)

        # Front paws - positioned at bottom
        paw_y = cy + s * 0.38
        self.canvas.create_oval(cx - s * 0.32, paw_y, cx - s * 0.1, paw_y + s * 0.16, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.1, paw_y, cx + s * 0.32, paw_y + s * 0.16, fill=body, outline=outline)

    def _draw_sparkrat(self, **kwargs) -> None:
        """Draw Sparkrat - Electric mouse standing on hind legs (soft yellow/cream)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        light = self.secondary_color
        cheeks = self.accent_color
        outline = self.body_shadow

        # Zigzag tail (behind) with spark animation - properly shaped
        spark_offset = math.sin(phase * 8) * 5 if playing or happy else 0
        tail_pts = [
            cx + s * 0.32, cy + s * 0.2,
            cx + s * 0.52, cy + s * 0.1 + spark_offset,
            cx + s * 0.48, cy + s * 0.32,
            cx + s * 0.72, cy + s * 0.18 - spark_offset,
            cx + s * 0.62, cy + s * 0.42,
            cx + s * 0.88, cy + s * 0.28 + spark_offset,
        ]
        self.canvas.create_line(tail_pts, fill=body, width=6)

        # Chubby body (standing upright) - centered
        self.canvas.create_oval(cx - s * 0.42, cy - s * 0.22, cx + s * 0.42, cy + s * 0.52, fill=body, outline=outline, width=2)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.28, cy - s * 0.08, cx + s * 0.28, cy + s * 0.38, fill=light, outline="")

        # Head - centered
        head_cy = cy - s * 0.32
        self.canvas.create_oval(cx - s * 0.38, head_cy - s * 0.28, cx + s * 0.38, head_cy + s * 0.25, fill=body, outline=outline, width=2)

        # Round ears with black inside - symmetrically positioned
        ear_y = head_cy - s * 0.18

        # Left ear
        self.canvas.create_oval(cx - s * 0.48, ear_y - s * 0.22, cx - s * 0.15, ear_y + s * 0.08, fill=body, outline=outline)
        self.canvas.create_oval(cx - s * 0.42, ear_y - s * 0.16, cx - s * 0.22, ear_y + s * 0.02, fill="#2F2F2F", outline="")

        # Right ear
        self.canvas.create_oval(cx + s * 0.15, ear_y - s * 0.22, cx + s * 0.48, ear_y + s * 0.08, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.22, ear_y - s * 0.16, cx + s * 0.42, ear_y + s * 0.02, fill="#2F2F2F", outline="")

        # Red cheek circles (can spark when happy) - symmetrically positioned
        cheek_glow = 8 if happy or playing else 6
        cheek_y = head_cy + s * 0.02
        for side in [-1, 1]:
            cheek_x = cx + side * s * 0.3
            self.canvas.create_oval(cheek_x - cheek_glow, cheek_y - cheek_glow * 0.7, cheek_x + cheek_glow, cheek_y + cheek_glow * 0.7, fill=cheeks, outline="")

        # Eyes - centered
        self._draw_round_eyes(cx, head_cy - s * 0.05, s * 0.9, sleeping=sleeping, happy=happy, sad=sad)

        # Nose - centered
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 3, nose_y - 2, cx + 3, nose_y + 3, fill="#2F2F2F", outline="")

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, head_cy + s * 0.08, s, phase)
        elif happy:
            self._draw_big_smile(cx, head_cy + s * 0.08, s)
        elif sad:
            self._draw_frown(cx, head_cy + s * 0.08, s)
        else:
            self._draw_smile(cx, head_cy + s * 0.08, s)

        # Little arms/paws raised - symmetrical
        arm_y = cy - s * 0.02
        self.canvas.create_oval(cx - s * 0.38, arm_y, cx - s * 0.2, arm_y + s * 0.16, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.2, arm_y, cx + s * 0.38, arm_y + s * 0.16, fill=body, outline=outline)

        # Feet - centered at bottom
        feet_y = cy + s * 0.42
        self.canvas.create_oval(cx - s * 0.3, feet_y, cx - s * 0.08, feet_y + s * 0.16, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.08, feet_y, cx + s * 0.3, feet_y + s * 0.16, fill=body, outline=outline)

    def _draw_drakeling(self, **kwargs) -> None:
        """Draw Drakeling - Baby dragon with tiny wings (soft teal-green/mint)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        scales = self.secondary_color
        wings = self.accent_color
        outline = scales
        horn_color = "#E4C9B4"  # Soft tan horns

        # Curled tail with arrow tip (behind) - wagging
        wag = math.sin(phase * 4) * 10 if playing or happy else 0
        tail_pts = [cx + s * 0.38, cy + s * 0.32, cx + s * 0.62 + wag * 0.3, cy + s * 0.48, cx + s * 0.82 + wag * 0.5, cy + s * 0.32, cx + s * 0.68 + wag * 0.3, cy + s * 0.22]
        self.canvas.create_polygon(tail_pts, fill=body, outline=scales, smooth=True)
        # Arrow tip
        arrow_pts = [cx + s * 0.78 + wag * 0.5, cy + s * 0.28, cx + s * 0.98 + wag * 0.5, cy + s * 0.22, cx + s * 0.82 + wag * 0.5, cy + s * 0.38]
        self.canvas.create_polygon(arrow_pts, fill=scales, outline="")

        # Tiny bat-like wings (behind body) - flap animation, attached at shoulders
        wing_flap = math.sin(phase * 5) * 12 if playing else 0
        wing_y = cy - s * 0.12
        wing_l = [cx - s * 0.32, wing_y, cx - s * 0.68, wing_y - s * 0.38 - wing_flap, cx - s * 0.58, wing_y, cx - s * 0.48, wing_y - s * 0.28 - wing_flap * 0.5, cx - s * 0.38, wing_y + s * 0.08]
        self.canvas.create_polygon(wing_l, fill=wings, outline=scales)

        wing_r = [cx + s * 0.32, wing_y, cx + s * 0.68, wing_y - s * 0.38 + wing_flap, cx + s * 0.58, wing_y, cx + s * 0.48, wing_y - s * 0.28 + wing_flap * 0.5, cx + s * 0.38, wing_y + s * 0.08]
        self.canvas.create_polygon(wing_r, fill=wings, outline=scales)

        # Dragon body sitting - centered
        self.canvas.create_oval(cx - s * 0.42, cy - s * 0.18, cx + s * 0.42, cy + s * 0.52, fill=body, outline=scales, width=2)

        # Belly scales - centered
        self.canvas.create_oval(cx - s * 0.24, cy, cx + s * 0.24, cy + s * 0.38, fill=lighten_color(body, 0.3), outline="")

        # Head - centered
        head_cy = cy - s * 0.32
        self.canvas.create_oval(cx - s * 0.36, head_cy - s * 0.25, cx + s * 0.36, head_cy + s * 0.22, fill=body, outline=scales, width=2)

        # Small horns on top of head - symmetrical
        horn_base_y = head_cy - s * 0.18
        horn_tip_y = head_cy - s * 0.55

        horn_l = [cx - s * 0.22, horn_base_y, cx - s * 0.32, horn_tip_y, cx - s * 0.1, horn_base_y + s * 0.05]
        self.canvas.create_polygon(horn_l, fill=horn_color, outline=darken_color(horn_color))

        horn_r = [cx + s * 0.1, horn_base_y + s * 0.05, cx + s * 0.32, horn_tip_y, cx + s * 0.22, horn_base_y]
        self.canvas.create_polygon(horn_r, fill=horn_color, outline=darken_color(horn_color))

        # Dragon eyes (golden with slit pupils) - centered
        self._draw_dragon_eyes(cx, head_cy - s * 0.02, s, sleeping=sleeping, happy=happy, sad=sad)

        # Snout/nose with nostrils - centered
        nose_y = head_cy + s * 0.1
        self.canvas.create_oval(cx - 5, nose_y, cx + 5, nose_y + s * 0.1, fill=scales, outline="")
        self.canvas.create_oval(cx - 6, nose_y + s * 0.02, cx - 3, nose_y + s * 0.07, fill="#2F2F2F", outline="")
        self.canvas.create_oval(cx + 3, nose_y + s * 0.02, cx + 6, nose_y + s * 0.07, fill="#2F2F2F", outline="")

        # Smoke puff when happy (fire breath hint)
        if happy and not sleeping:
            smoke_y = head_cy + s * 0.08 - (phase * 10) % 20
            self.canvas.create_oval(cx - 4, smoke_y - 4, cx + 4, smoke_y + 4, fill="#D4D4D4", outline="")

        # Mouth
        if eating:
            self._draw_eating_mouth(cx, head_cy + s * 0.1, s, phase)
        elif happy:
            self._draw_big_smile(cx, head_cy + s * 0.1, s)
        elif sad:
            self._draw_frown(cx, head_cy + s * 0.1, s)
        else:
            self._draw_smile(cx, head_cy + s * 0.1, s)

        # Front claws - centered at bottom
        claw_y = cy + s * 0.38
        self.canvas.create_oval(cx - s * 0.3, claw_y, cx - s * 0.1, claw_y + s * 0.16, fill=body, outline=scales)
        self.canvas.create_oval(cx + s * 0.1, claw_y, cx + s * 0.3, claw_y + s * 0.16, fill=body, outline=scales)

    def _draw_shimi(self, **kwargs) -> None:
        """Draw Shimi - Ghost cat with fading wispy bottom (soft purple/lavender)."""
        cx = self.center_x
        cy = self.center_y - self.bounce_offset
        s = self.body_size
        happy = kwargs.get("happy", False)
        sad = kwargs.get("sad", False)
        sleeping = kwargs.get("sleeping", False)
        eating = kwargs.get("eating", False)
        playing = kwargs.get("playing", False)
        phase = kwargs.get("phase", 0)

        body = self.body_color
        glow = self.secondary_color
        white = self.accent_color

        # Ghostly aura (outer glow) - pulsing
        aura_pulse = math.sin(phase * 2) * 5
        self.canvas.create_oval(cx - s * 0.62 - aura_pulse, cy - s * 0.72 - aura_pulse, cx + s * 0.62 + aura_pulse, cy + s * 0.58 + aura_pulse, fill=lighten_color(body, 0.6), outline="")

        # Wispy fading tail (to the side and fading)
        for i in range(4):
            alpha_fade = lighten_color(body, i * 0.15)
            self.canvas.create_oval(
                cx + s * 0.38 + i * 10, cy + s * 0.12 - i * 4,
                cx + s * 0.58 + i * 10, cy + s * 0.32 - i * 4,
                fill=alpha_fade, outline=""
            )

        # Cat silhouette body (fades at bottom - no legs) - centered
        self.canvas.create_oval(cx - s * 0.42, cy - s * 0.48, cx + s * 0.42, cy + s * 0.28, fill=body, outline="")

        # Wispy bottom (fading triangle instead of legs) - properly shaped for ghostly effect
        float_offset = math.sin(phase * 2) * 3
        wisps = [cx - s * 0.38, cy + s * 0.18, cx, cy + s * 0.58 + float_offset, cx + s * 0.38, cy + s * 0.18]
        self.canvas.create_polygon(wisps, fill=body, outline="", smooth=True)

        # Pointed cat ears - centered
        ear_base_y = cy - s * 0.38
        ear_tip_y = cy - s * 0.78

        ear_l = [cx - s * 0.32, ear_base_y, cx - s * 0.48, ear_tip_y, cx - s * 0.1, ear_base_y]
        self.canvas.create_polygon(ear_l, fill=glow, outline=body)

        ear_r = [cx + s * 0.1, ear_base_y, cx + s * 0.48, ear_tip_y, cx + s * 0.32, ear_base_y]
        self.canvas.create_polygon(ear_r, fill=glow, outline=body)

        # Glowing white/blue eyes - pulse effect, centered
        glow_pulse = 2 + math.sin(phase * 3) * 2
        eye_y = cy - s * 0.12
        for offset in [-s * 0.18, s * 0.18]:
            # Glow effect
            self.canvas.create_oval(cx + offset - 8 - glow_pulse, eye_y - 6 - glow_pulse, cx + offset + 8 + glow_pulse, eye_y + 6 + glow_pulse, fill=white, outline="")
            if not sleeping:
                # Eye core
                self.canvas.create_oval(cx + offset - 5, eye_y - 4, cx + offset + 5, eye_y + 4, fill="#87CEEB", outline="")
            else:
                self.canvas.create_arc(cx + offset - 5, eye_y - 2, cx + offset + 5, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline="#87CEEB", width=2)

        # No mouth normally (ethereal), small one when eating
        if eating:
            self._draw_eating_mouth(cx, cy + s * 0.08, s, phase)

    # ==================== EYE HELPER METHODS ====================

    def _draw_fox_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False):
        """Draw fox-style eyes."""
        eye_y = cy - s * 0.08
        eye_spacing = s * 0.26
        for offset in [-eye_spacing, eye_spacing]:
            if sleeping:
                self.canvas.create_arc(cx + offset - 6, eye_y - 2, cx + offset + 6, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline="#2F2F2F", width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 6, eye_y - 4, cx + offset + 6, eye_y + 6, start=0, extent=180, style=tk.ARC, outline="#2F2F2F", width=2)
            else:
                self.canvas.create_oval(cx + offset - 5, eye_y - 5, cx + offset + 5, eye_y + 5, fill="#2F2F2F", outline="")
                self.canvas.create_oval(cx + offset - 2, eye_y - 3, cx + offset + 1, eye_y, fill="white", outline="")

    def _draw_round_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False):
        """Draw round cute eyes."""
        eye_y = cy - s * 0.1
        eye_spacing = s * 0.24
        for offset in [-eye_spacing, eye_spacing]:
            if sleeping:
                self.canvas.create_arc(cx + offset - 6, eye_y - 2, cx + offset + 6, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline="#2F2F2F", width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 6, eye_y - 4, cx + offset + 6, eye_y + 6, start=0, extent=180, style=tk.ARC, outline="#2F2F2F", width=2)
            else:
                self.canvas.create_oval(cx + offset - 6, eye_y - 6, cx + offset + 6, eye_y + 6, fill="#2F2F2F", outline="")
                self.canvas.create_oval(cx + offset - 3, eye_y - 4, cx + offset, eye_y - 1, fill="white", outline="")

    def _draw_puppy_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False):
        """Draw puppy eyes (happy arcs when excited)."""
        eye_y = cy - s * 0.05
        eye_spacing = s * 0.24
        for offset in [-eye_spacing, eye_spacing]:
            if sleeping:
                self.canvas.create_arc(cx + offset - 6, eye_y - 2, cx + offset + 6, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline="#2F2F2F", width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 7, eye_y - 5, cx + offset + 7, eye_y + 7, start=0, extent=180, style=tk.ARC, outline="#2F2F2F", width=3)
            else:
                self.canvas.create_oval(cx + offset - 7, eye_y - 7, cx + offset + 7, eye_y + 7, fill="white", outline="#2F2F2F")
                self.canvas.create_oval(cx + offset - 4, eye_y - 4, cx + offset + 4, eye_y + 4, fill="#2F2F2F", outline="")
                self.canvas.create_oval(cx + offset - 2, eye_y - 5, cx + offset + 1, eye_y - 2, fill="white", outline="")

    def _draw_owl_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False, feathers="#F2E2D2"):
        """Draw huge owl eyes."""
        eye_y = cy
        eye_spacing = s * 0.22
        for offset in [-eye_spacing, eye_spacing]:
            # Eye disk
            self.canvas.create_oval(cx + offset - 12, eye_y - 12, cx + offset + 12, eye_y + 12, fill=feathers, outline=self.body_shadow)
            if sleeping:
                self.canvas.create_arc(cx + offset - 8, eye_y - 2, cx + offset + 8, eye_y + 6, start=0, extent=-180, style=tk.ARC, outline="#2F2F2F", width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 8, eye_y - 6, cx + offset + 8, eye_y + 8, start=0, extent=180, style=tk.ARC, outline="#2F2F2F", width=2)
            else:
                self.canvas.create_oval(cx + offset - 9, eye_y - 9, cx + offset + 9, eye_y + 9, fill="white", outline="#2F2F2F")
                self.canvas.create_oval(cx + offset - 5, eye_y - 5, cx + offset + 5, eye_y + 5, fill="#2F2F2F", outline="")
                self.canvas.create_oval(cx + offset - 2, eye_y - 6, cx + offset + 2, eye_y - 2, fill="white", outline="")

    def _draw_cat_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False, iris_color="#95D5B2"):
        """Draw cat eyes with slit pupils."""
        eye_y = cy
        eye_spacing = s * 0.2
        for offset in [-eye_spacing, eye_spacing]:
            self.canvas.create_oval(cx + offset - 8, eye_y - 8, cx + offset + 8, eye_y + 8, fill=iris_color, outline="#2F2F2F")
            if sleeping:
                self.canvas.create_arc(cx + offset - 6, eye_y - 2, cx + offset + 6, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline="#2F2F2F", width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 6, eye_y - 4, cx + offset + 6, eye_y + 6, start=0, extent=180, style=tk.ARC, outline="#2F2F2F", width=2)
            else:
                # Slit pupil
                self.canvas.create_oval(cx + offset - 2, eye_y - 6, cx + offset + 2, eye_y + 6, fill="#2F2F2F", outline="")
                self.canvas.create_oval(cx + offset - 3, eye_y - 5, cx + offset, eye_y - 2, fill="white", outline="")

    def _draw_glowing_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False, glow_color="#E2C2FF"):
        """Draw glowing mystic eyes."""
        eye_y = cy
        eye_spacing = s * 0.18
        for offset in [-eye_spacing, eye_spacing]:
            # Glow
            self.canvas.create_oval(cx + offset - 7, eye_y - 7, cx + offset + 7, eye_y + 7, fill=glow_color, outline="")
            if sleeping:
                self.canvas.create_arc(cx + offset - 5, eye_y - 2, cx + offset + 5, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline=self.body_color, width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 5, eye_y - 4, cx + offset + 5, eye_y + 6, start=0, extent=180, style=tk.ARC, outline=self.body_color, width=2)
            else:
                self.canvas.create_oval(cx + offset - 5, eye_y - 5, cx + offset + 5, eye_y + 5, fill="white", outline="")
                self.canvas.create_oval(cx + offset - 2, eye_y - 2, cx + offset + 2, eye_y + 2, fill=self.body_color, outline="")

    def _draw_dragon_eyes(self, cx, cy, s, sleeping=False, happy=False, sad=False):
        """Draw dragon eyes with golden irises and slit pupils."""
        eye_y = cy
        eye_spacing = s * 0.16
        for offset in [-eye_spacing, eye_spacing]:
            self.canvas.create_oval(cx + offset - 7, eye_y - 7, cx + offset + 7, eye_y + 7, fill="#FFD700", outline="#2F2F2F")
            if sleeping:
                self.canvas.create_arc(cx + offset - 5, eye_y - 2, cx + offset + 5, eye_y + 4, start=0, extent=-180, style=tk.ARC, outline="#2F2F2F", width=2)
            elif happy:
                self.canvas.create_arc(cx + offset - 5, eye_y - 4, cx + offset + 5, eye_y + 6, start=0, extent=180, style=tk.ARC, outline="#2F2F2F", width=2)
            else:
                # Vertical slit pupil
                self.canvas.create_oval(cx + offset - 2, eye_y - 5, cx + offset + 2, eye_y + 5, fill="#2F2F2F", outline="")
                self.canvas.create_oval(cx + offset - 2, eye_y - 4, cx + offset + 1, eye_y - 1, fill="white", outline="")

    # ==================== MOUTH HELPER METHODS ====================

    def _draw_smile(self, cx, cy, s):
        """Draw a simple smile."""
        smile_y = cy + s * 0.22
        self.canvas.create_arc(cx - 10, smile_y, cx + 10, smile_y + s * 0.2, start=200, extent=140, style=tk.ARC, outline="#2F2F2F", width=2)

    def _draw_big_smile(self, cx, cy, s):
        """Draw a big happy smile."""
        smile_y = cy + s * 0.2
        self.canvas.create_arc(cx - 14, smile_y, cx + 14, smile_y + s * 0.28, start=200, extent=140, style=tk.CHORD, fill="#FFADAD", outline="#2F2F2F", width=2)

    def _draw_frown(self, cx, cy, s):
        """Draw a sad frown."""
        frown_y = cy + s * 0.32
        self.canvas.create_arc(cx - 8, frown_y, cx + 8, frown_y + s * 0.15, start=20, extent=140, style=tk.ARC, outline="#2F2F2F", width=2)

    def _draw_eating_mouth(self, cx, cy, s, phase):
        """Draw eating/chomping mouth."""
        open_amount = abs(math.sin(phase * math.pi * 4)) * 10 + 5
        mouth_y = cy + s * 0.22
        self.canvas.create_oval(cx - 10, mouth_y - open_amount // 2, cx + 10, mouth_y + open_amount, fill="#FFADAD", outline="#2F2F2F", width=2)

    # ==================== EFFECT HELPER METHODS ====================

    def _draw_shadow(self):
        """Draw shadow beneath pet."""
        shadow_y = self.center_y + self.body_size + 10 - self.bounce_offset * 0.5
        shadow_width = self.body_size * 0.8
        shadow_height = 8
        self.canvas.create_oval(self.center_x - shadow_width, shadow_y - shadow_height, self.center_x + shadow_width, shadow_y + shadow_height, fill="#D4D4D4", outline="")

    def _draw_hearts(self):
        """Draw floating hearts around pet."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        positions = [(-45, -35), (50, -30), (-40, 25)]
        for px, py in positions:
            self.canvas.create_text(cx + px, cy + py, text="\u2665", font=("Arial", 14), fill="#FFADAD")

    def _draw_sparkles(self, phase):
        """Draw sparkle effects."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        positions = [(-50, -20), (50, -15), (-40, 30), (45, 25), (0, -50)]
        for i, (px, py) in enumerate(positions):
            if (phase + i * 0.5) % 1.0 < 0.5:
                self.canvas.create_text(cx + px, cy + py, text="\u2734", font=("Arial", 10), fill="#FFF3B0")

    def _draw_stars(self, phase):
        """Draw star effects for tricks."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        for i in range(5):
            angle = phase + i * (math.pi * 2 / 5)
            radius = 60 + math.sin(phase * 3 + i) * 10
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
            self.canvas.create_text(x, y, text="\u2605", font=("Arial", 12), fill="#FFF3B0")

    def _draw_sweat_drop(self):
        """Draw sweat drop for hungry/worried state."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        drop_x, drop_y = cx + 45, cy - 25
        self.canvas.create_polygon(drop_x, drop_y - 12, drop_x - 6, drop_y, drop_x, drop_y + 6, drop_x + 6, drop_y, fill="#BDE0FE", outline="#A2D2FF", smooth=True)

    def _draw_zzz(self, offset):
        """Draw floating ZZZ for sleeping."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        base_x, base_y = cx + 40, cy - 35
        sizes = [8, 10, 12]
        for i, size in enumerate(sizes):
            y_offset = -i * 15 - (offset * 20) % 45
            alpha_sim = max(0, 1 - abs(y_offset) / 50)
            if alpha_sim > 0.3:
                self.canvas.create_text(base_x + i * 5, base_y + y_offset, text="Z", font=("Arial", size, "bold"), fill="#CDB4DB")

    def _draw_food_particles(self, phase):
        """Draw food particle effects when eating."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        for i in range(3):
            if (phase * 4 + i * 0.3) % 1.0 < 0.3:
                offset_x = random.randint(-25, 25)
                offset_y = random.randint(18, 30)
                self.canvas.create_oval(cx + offset_x - 4, cy + offset_y - 4, cx + offset_x + 4, cy + offset_y + 4, fill="#FFF3B0", outline="")

    def _draw_dust(self, direction):
        """Draw dust particles behind walking pet."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        dust_x = cx - direction * 50
        dust_y = cy + self.body_size + 5
        for i in range(3):
            offset = random.randint(-6, 6)
            size = random.randint(2, 5)
            self.canvas.create_oval(dust_x + offset - size, dust_y + offset - size, dust_x + offset + size, dust_y + offset + size, fill="#D4D4D4", outline="")
