"""
Creature selection screen for the Desktop Virtual Pet.

Displays a grid of 10 creatures for the user to choose from.
Features properly-shaped animal creatures with distinct silhouettes.
All creatures use a soft PASTEL color palette.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import math


# Creature data: 10 creature designs with soft PASTEL color palette
CREATURES = {
    "fennix": {
        "name": "Fennix",
        "description": "Fiery fennec fox",
        "type": "Fire",
        "primary": "#FFB5A7",      # Soft coral
        "secondary": "#FFCDB2",    # Pale orange (flame)
        "accent": "#FFF1E6",       # Cream belly
    },
    "hopplet": {
        "name": "Hopplet",
        "description": "Chubby bunny",
        "type": "Normal",
        "primary": "#FFF5EE",      # Soft white
        "secondary": "#FFCAD4",    # Light pink inner ears
        "accent": "#FFFFFF",       # White belly
    },
    "drizzpup": {
        "name": "Drizzpup",
        "description": "Water puppy",
        "type": "Water",
        "primary": "#A2D2FF",      # Soft sky blue
        "secondary": "#BDE0FE",    # Pale blue fins
        "accent": "#E2EAFC",       # Light lavender blue belly
    },
    "owlette": {
        "name": "Owlette",
        "description": "Baby owl",
        "type": "Flying",
        "primary": "#E4C9B4",      # Soft tan
        "secondary": "#F2E2D2",    # Cream feathers
        "accent": "#FFF8F0",       # Off-white belly
    },
    "kitsumi": {
        "name": "Kitsumi",
        "description": "Spirit fox",
        "type": "Mystic",
        "primary": "#CDB4DB",      # Soft lavender
        "secondary": "#E2C2FF",    # Light purple
        "accent": "#F3E8FF",       # Pale lavender belly
    },
    "pengi": {
        "name": "Pengi",
        "description": "Tiny penguin",
        "type": "Ice",
        "primary": "#89C2D9",      # Soft blue-gray
        "secondary": "#FFFFFF",    # White belly
        "accent": "#FFCB77",       # Soft orange beak/feet
    },
    "leafkit": {
        "name": "Leafkit",
        "description": "Grass kitten",
        "type": "Grass",
        "primary": "#B5E48C",      # Soft green
        "secondary": "#95D5B2",    # Sage green stripes
        "accent": "#FFB5C5",       # Soft pink flower
    },
    "sparkrat": {
        "name": "Sparkrat",
        "description": "Electric mouse",
        "type": "Electric",
        "primary": "#FFF3B0",      # Soft yellow
        "secondary": "#FFFBEB",    # Cream belly
        "accent": "#FFADAD",       # Soft pink cheeks
    },
    "drakeling": {
        "name": "Drakeling",
        "description": "Baby dragon",
        "type": "Dragon",
        "primary": "#99E2B4",      # Soft teal-green
        "secondary": "#88D4AB",    # Mint scales
        "accent": "#B5E48C",       # Soft green wings
    },
    "shimi": {
        "name": "Shimi",
        "description": "Ghost cat",
        "type": "Ghost",
        "primary": "#D4C1EC",      # Soft purple
        "secondary": "#E8DAEF",    # Pale lavender
        "accent": "#FFFFFF",       # White glow
    },
}


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


class CreaturePreview:
    """
    Draws a small preview of a creature for the selection screen.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        creature_type: str,
        center_x: int,
        center_y: int,
        size: int = 35
    ) -> None:
        """
        Initialize creature preview.

        Args:
            canvas: Tkinter canvas to draw on.
            creature_type: Type of creature to preview.
            center_x: X center coordinate.
            center_y: Y center coordinate.
            size: Size of the creature preview.
        """
        self.canvas = canvas
        self.creature_type = creature_type
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.bounce_offset = 0.0
        self.data = CREATURES.get(creature_type, CREATURES["fennix"])

    def draw(self, bounce: float = 0) -> None:
        """Draw the creature preview with optional bounce offset."""
        self.bounce_offset = bounce
        method_name = f"_draw_{self.creature_type}"
        draw_method = getattr(self, method_name, self._draw_fennix)
        draw_method()

    def _draw_fennix(self) -> None:
        """Draw Fennix - Fire Fennec Fox with HUGE ears (properly centered)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        flame = self.data["secondary"]
        belly = self.data["accent"]
        outline = darken_color(body)

        # Tail curled around (behind body) - positioned to connect to body
        tail_points = [
            cx + s * 0.4, cy + s * 0.2,
            cx + s * 0.75, cy + s * 0.0,
            cx + s * 0.7, cy - s * 0.25,
            cx + s * 0.5, cy - s * 0.1,
        ]
        self.canvas.create_polygon(tail_points, fill=body, outline=outline, smooth=True, width=1)
        # Flame tip on tail
        self.canvas.create_oval(cx + s * 0.55, cy - s * 0.35, cx + s * 0.8, cy - s * 0.1, fill=flame, outline="")

        # Body - horizontal oval (sitting fox body)
        self.canvas.create_oval(cx - s * 0.5, cy - s * 0.05, cx + s * 0.45, cy + s * 0.5, fill=body, outline=outline, width=1)

        # Belly - centered on body
        self.canvas.create_oval(cx - s * 0.3, cy + s * 0.05, cx + s * 0.25, cy + s * 0.4, fill=belly, outline="")

        # Head - centered above body
        head_cx = cx - s * 0.02
        head_cy = cy - s * 0.2
        self.canvas.create_oval(head_cx - s * 0.35, head_cy - s * 0.3, head_cx + s * 0.35, head_cy + s * 0.25, fill=body, outline=outline, width=1)

        # HUGE fennec ears (triangles) - properly centered on head
        ear_base_y = head_cy - s * 0.15
        ear_tip_y = head_cy - s * 0.9

        # Left ear - centered properly
        ear_l = [head_cx - s * 0.25, ear_base_y, head_cx - s * 0.35, ear_tip_y, head_cx - s * 0.05, ear_base_y]
        self.canvas.create_polygon(ear_l, fill=body, outline=outline, width=1)
        inner_l = [head_cx - s * 0.22, ear_base_y, head_cx - s * 0.3, ear_tip_y + s * 0.15, head_cx - s * 0.1, ear_base_y]
        self.canvas.create_polygon(inner_l, fill=flame, outline="")

        # Right ear - centered properly
        ear_r = [head_cx + s * 0.05, ear_base_y, head_cx + s * 0.35, ear_tip_y, head_cx + s * 0.25, ear_base_y]
        self.canvas.create_polygon(ear_r, fill=body, outline=outline, width=1)
        inner_r = [head_cx + s * 0.1, ear_base_y, head_cx + s * 0.3, ear_tip_y + s * 0.15, head_cx + s * 0.22, ear_base_y]
        self.canvas.create_polygon(inner_r, fill=flame, outline="")

        # Eyes - centered on head
        eye_y = head_cy
        for offset in [-s * 0.12, s * 0.12]:
            self.canvas.create_oval(head_cx + offset - 3, eye_y - 3, head_cx + offset + 3, eye_y + 3, fill="#2F2F2F", outline="")
            self.canvas.create_oval(head_cx + offset - 1, eye_y - 2, head_cx + offset + 1, eye_y, fill="white", outline="")

        # Small black nose - centered below eyes
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(head_cx - 2, nose_y - 2, head_cx + 2, nose_y + 2, fill="#2F2F2F", outline="")

        # Front paws - positioned at bottom of body
        paw_y = cy + s * 0.38
        self.canvas.create_oval(cx - s * 0.3, paw_y, cx - s * 0.1, paw_y + s * 0.15, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.05, paw_y, cx + s * 0.25, paw_y + s * 0.15, fill=body, outline=outline)

    def _draw_hopplet(self) -> None:
        """Draw Hopplet - Chubby bunny with floppy ears (properly aligned)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        inner = self.data["secondary"]
        belly_c = self.data["accent"]
        outline = darken_color(body)

        # Cotton puff tail (behind) - positioned correctly
        self.canvas.create_oval(cx + s * 0.35, cy + s * 0.1, cx + s * 0.6, cy + s * 0.35, fill=belly_c, outline=outline)

        # Round chubby body
        self.canvas.create_oval(cx - s * 0.5, cy - s * 0.25, cx + s * 0.5, cy + s * 0.55, fill=body, outline=outline, width=1)

        # Belly - centered on body
        self.canvas.create_oval(cx - s * 0.32, cy - s * 0.05, cx + s * 0.32, cy + s * 0.4, fill=belly_c, outline="")

        # Head - centered above body
        head_cy = cy - s * 0.3
        self.canvas.create_oval(cx - s * 0.38, head_cy - s * 0.3, cx + s * 0.38, head_cy + s * 0.3, fill=body, outline=outline, width=1)

        # Long floppy ears (hanging down) - properly attached to head
        ear_top_y = head_cy - s * 0.2
        ear_bottom_y = cy + s * 0.25

        # Left ear
        self.canvas.create_oval(cx - s * 0.55, ear_top_y, cx - s * 0.25, ear_bottom_y, fill=body, outline=outline)
        self.canvas.create_oval(cx - s * 0.5, ear_top_y + s * 0.1, cx - s * 0.3, ear_bottom_y - s * 0.1, fill=inner, outline="")

        # Right ear
        self.canvas.create_oval(cx + s * 0.25, ear_top_y, cx + s * 0.55, ear_bottom_y, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.3, ear_top_y + s * 0.1, cx + s * 0.5, ear_bottom_y - s * 0.1, fill=inner, outline="")

        # Big oval feet in front - positioned at bottom
        feet_y = cy + s * 0.35
        self.canvas.create_oval(cx - s * 0.42, feet_y, cx - s * 0.08, feet_y + s * 0.22, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.08, feet_y, cx + s * 0.42, feet_y + s * 0.22, fill=body, outline=outline)

        # Eyes - centered on head
        eye_y = head_cy - s * 0.05
        for offset in [-s * 0.15, s * 0.15]:
            self.canvas.create_oval(cx + offset - 3, eye_y - 4, cx + offset + 3, eye_y + 4, fill="#2F2F2F", outline="")
            self.canvas.create_oval(cx + offset - 1, eye_y - 2, cx + offset + 1, eye_y, fill="white", outline="")

        # Twitchy nose (pink oval) - centered on face
        nose_y = head_cy + s * 0.1
        self.canvas.create_oval(cx - 3, nose_y - 3, cx + 3, nose_y + 3, fill=inner, outline="")

    def _draw_drizzpup(self) -> None:
        """Draw Drizzpup - Water puppy with fin ears (properly aligned)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        fins = self.data["secondary"]
        belly = self.data["accent"]
        outline = darken_color(body)

        # Water droplet tail (behind) - properly attached
        tail_pts = [cx + s * 0.4, cy + s * 0.15, cx + s * 0.7, cy - s * 0.1, cx + s * 0.65, cy + s * 0.3]
        self.canvas.create_polygon(tail_pts, fill=body, outline=outline, smooth=True)
        self.canvas.create_oval(cx + s * 0.5, cy - s * 0.2, cx + s * 0.75, cy + s * 0.0, fill=fins, outline="")

        # Body - sitting puppy
        self.canvas.create_oval(cx - s * 0.48, cy - s * 0.12, cx + s * 0.48, cy + s * 0.5, fill=body, outline=outline, width=1)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.28, cy + s * 0.0, cx + s * 0.28, cy + s * 0.38, fill=belly, outline="")

        # Head - centered above body
        head_cy = cy - s * 0.25
        self.canvas.create_oval(cx - s * 0.38, head_cy - s * 0.28, cx + s * 0.38, head_cy + s * 0.28, fill=body, outline=outline, width=1)

        # Floppy fin-like ears - properly positioned on head sides
        fin_l = [cx - s * 0.32, head_cy - s * 0.1, cx - s * 0.65, head_cy - s * 0.3, cx - s * 0.6, head_cy + s * 0.1, cx - s * 0.32, head_cy + s * 0.15]
        self.canvas.create_polygon(fin_l, fill=fins, outline=darken_color(fins), smooth=True)

        fin_r = [cx + s * 0.32, head_cy - s * 0.1, cx + s * 0.65, head_cy - s * 0.3, cx + s * 0.6, head_cy + s * 0.1, cx + s * 0.32, head_cy + s * 0.15]
        self.canvas.create_polygon(fin_r, fill=fins, outline=darken_color(fins), smooth=True)

        # Happy eyes - centered on head
        eye_y = head_cy - s * 0.05
        for offset in [-s * 0.15, s * 0.15]:
            self.canvas.create_oval(cx + offset - 4, eye_y - 4, cx + offset + 4, eye_y + 4, fill="white", outline="#2F2F2F")
            self.canvas.create_oval(cx + offset - 2, eye_y - 2, cx + offset + 2, eye_y + 2, fill="#2F2F2F", outline="")

        # Nose - centered below eyes
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 3, nose_y - 2, cx + 3, nose_y + 2, fill="#2F2F2F", outline="")

        # Tongue out - below nose
        tongue_y = head_cy + s * 0.2
        self.canvas.create_oval(cx - 3, tongue_y, cx + 3, tongue_y + s * 0.1, fill="#FFADAD", outline="")

        # Front paws - positioned at bottom
        paw_y = cy + s * 0.35
        self.canvas.create_oval(cx - s * 0.32, paw_y, cx - s * 0.12, paw_y + s * 0.15, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.12, paw_y, cx + s * 0.32, paw_y + s * 0.15, fill=body, outline=outline)

    def _draw_owlette(self) -> None:
        """Draw Owlette - Baby owl with huge round eyes (properly centered)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        feathers = self.data["secondary"]
        belly = self.data["accent"]
        outline = darken_color(body)
        beak_color = "#FFCB77"  # Soft yellow beak

        # Wing stubs (behind body) - positioned at body sides
        self.canvas.create_oval(cx - s * 0.68, cy - s * 0.05, cx - s * 0.32, cy + s * 0.35, fill=feathers, outline=outline)
        self.canvas.create_oval(cx + s * 0.32, cy - s * 0.05, cx + s * 0.68, cy + s * 0.35, fill=feathers, outline=outline)

        # Round owl body - centered
        self.canvas.create_oval(cx - s * 0.42, cy - s * 0.35, cx + s * 0.42, cy + s * 0.52, fill=body, outline=outline, width=1)

        # Belly/chest feathers - centered on body
        self.canvas.create_oval(cx - s * 0.28, cy - s * 0.12, cx + s * 0.28, cy + s * 0.38, fill=belly, outline="")

        # Small triangular ear tufts - centered on top of head
        tuft_base_y = cy - s * 0.28
        tuft_tip_y = cy - s * 0.58

        tuft_l = [cx - s * 0.22, tuft_base_y, cx - s * 0.32, tuft_tip_y, cx - s * 0.08, tuft_base_y]
        self.canvas.create_polygon(tuft_l, fill=body, outline=outline)

        tuft_r = [cx + s * 0.08, tuft_base_y, cx + s * 0.32, tuft_tip_y, cx + s * 0.22, tuft_base_y]
        self.canvas.create_polygon(tuft_r, fill=body, outline=outline)

        # HUGE circular eyes - centered on face
        eye_y = cy - s * 0.1
        for offset in [-s * 0.18, s * 0.18]:
            # Eye disk (feather pattern around eye)
            self.canvas.create_oval(cx + offset - 8, eye_y - 8, cx + offset + 8, eye_y + 8, fill=feathers, outline=outline)
            # Eye white
            self.canvas.create_oval(cx + offset - 6, eye_y - 6, cx + offset + 6, eye_y + 6, fill="white", outline="#2F2F2F")
            # Pupil
            self.canvas.create_oval(cx + offset - 3, eye_y - 3, cx + offset + 3, eye_y + 3, fill="#2F2F2F", outline="")
            # Highlight
            self.canvas.create_oval(cx + offset - 1, eye_y - 4, cx + offset + 2, eye_y - 1, fill="white", outline="")

        # Small beak - centered below eyes
        beak_y = cy + s * 0.08
        beak_pts = [cx, beak_y - s * 0.05, cx - 4, beak_y + s * 0.08, cx + 4, beak_y + s * 0.08]
        self.canvas.create_polygon(beak_pts, fill=beak_color, outline=darken_color(beak_color))

        # Tiny feet - centered at bottom
        feet_y = cy + s * 0.42
        self.canvas.create_oval(cx - s * 0.18, feet_y, cx - s * 0.04, feet_y + s * 0.12, fill=beak_color, outline="")
        self.canvas.create_oval(cx + s * 0.04, feet_y, cx + s * 0.18, feet_y + s * 0.12, fill=beak_color, outline="")

    def _draw_kitsumi(self) -> None:
        """Draw Kitsumi - Spirit fox with multiple wispy tails (elegant and centered)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        glow = self.data["secondary"]
        light = self.data["accent"]
        outline = darken_color(body)

        # Multiple wispy tails (3 tails - behind) - spread nicely
        for i, angle in enumerate([-25, 0, 25]):
            rad = math.radians(angle)
            tail_pts = [
                cx + s * 0.35, cy + s * 0.15,
                cx + s * 0.6 + math.cos(rad) * s * 0.15, cy + math.sin(rad) * s * 0.25,
                cx + s * 0.75 + math.cos(rad) * s * 0.2, cy - s * 0.15 + math.sin(rad) * s * 0.15,
            ]
            self.canvas.create_line(tail_pts, fill=glow if i == 1 else body, width=5 - i, smooth=True)

        # Elegant fox body - slender
        self.canvas.create_oval(cx - s * 0.42, cy - s * 0.08, cx + s * 0.42, cy + s * 0.45, fill=body, outline=outline, width=1)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.24, cy + s * 0.0, cx + s * 0.24, cy + s * 0.32, fill=light, outline="")

        # Head - elegant and centered
        head_cy = cy - s * 0.28
        self.canvas.create_oval(cx - s * 0.32, head_cy - s * 0.25, cx + s * 0.32, head_cy + s * 0.25, fill=body, outline=outline, width=1)

        # Pointed elegant ears - symmetrical
        ear_base_y = head_cy - s * 0.12
        ear_tip_y = head_cy - s * 0.65

        ear_l = [cx - s * 0.22, ear_base_y, cx - s * 0.35, ear_tip_y, cx - s * 0.05, ear_base_y]
        self.canvas.create_polygon(ear_l, fill=body, outline=outline)
        self.canvas.create_polygon([cx - s * 0.2, ear_base_y, cx - s * 0.3, ear_tip_y + s * 0.12, cx - s * 0.1, ear_base_y], fill=glow, outline="")

        ear_r = [cx + s * 0.05, ear_base_y, cx + s * 0.35, ear_tip_y, cx + s * 0.22, ear_base_y]
        self.canvas.create_polygon(ear_r, fill=body, outline=outline)
        self.canvas.create_polygon([cx + s * 0.1, ear_base_y, cx + s * 0.3, ear_tip_y + s * 0.12, cx + s * 0.2, ear_base_y], fill=glow, outline="")

        # Glowing eyes - centered
        eye_y = head_cy
        for offset in [-s * 0.12, s * 0.12]:
            self.canvas.create_oval(cx + offset - 4, eye_y - 4, cx + offset + 4, eye_y + 4, fill=glow, outline="")
            self.canvas.create_oval(cx + offset - 3, eye_y - 3, cx + offset + 3, eye_y + 3, fill="white", outline="")
            self.canvas.create_oval(cx + offset - 1, eye_y - 1, cx + offset + 1, eye_y + 1, fill=body, outline="")

        # Small nose - centered
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 2, nose_y - 2, cx + 2, nose_y + 2, fill="#2F2F2F", outline="")

        # Front paws - positioned at bottom
        paw_y = cy + s * 0.32
        self.canvas.create_oval(cx - s * 0.22, paw_y, cx - s * 0.08, paw_y + s * 0.12, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.08, paw_y, cx + s * 0.22, paw_y + s * 0.12, fill=body, outline=outline)

    def _draw_pengi(self) -> None:
        """Draw Pengi - Tiny penguin standing upright (properly proportioned)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        belly = self.data["secondary"]
        accent = self.data["accent"]
        outline = darken_color(body)
        cheek_color = "#FFD6E0"  # Soft pink cheeks

        # Body - oval standing upright, centered
        self.canvas.create_oval(cx - s * 0.38, cy - s * 0.45, cx + s * 0.38, cy + s * 0.48, fill=body, outline=outline, width=1)

        # White belly (distinctive penguin marking) - properly centered
        self.canvas.create_oval(cx - s * 0.26, cy - s * 0.28, cx + s * 0.26, cy + s * 0.38, fill=belly, outline="")

        # Flippers out to sides - positioned at correct height on body
        flip_y = cy - s * 0.05
        flip_l = [cx - s * 0.32, flip_y - s * 0.1, cx - s * 0.6, flip_y + s * 0.05, cx - s * 0.5, flip_y + s * 0.3, cx - s * 0.32, flip_y + s * 0.2]
        self.canvas.create_polygon(flip_l, fill=body, outline=outline, smooth=True)

        flip_r = [cx + s * 0.32, flip_y - s * 0.1, cx + s * 0.6, flip_y + s * 0.05, cx + s * 0.5, flip_y + s * 0.3, cx + s * 0.32, flip_y + s * 0.2]
        self.canvas.create_polygon(flip_r, fill=body, outline=outline, smooth=True)

        # Eyes - centered on upper body/head area
        eye_y = cy - s * 0.2
        for offset in [-s * 0.12, s * 0.12]:
            self.canvas.create_oval(cx + offset - 3, eye_y - 3, cx + offset + 3, eye_y + 3, fill="white", outline="#2F2F2F")
            self.canvas.create_oval(cx + offset - 1, eye_y - 1, cx + offset + 1, eye_y + 1, fill="#2F2F2F", outline="")

        # Orange beak - centered below eyes
        beak_y = cy - s * 0.05
        beak_pts = [cx, beak_y - s * 0.08, cx - 5, beak_y + s * 0.05, cx + 5, beak_y + s * 0.05]
        self.canvas.create_polygon(beak_pts, fill=accent, outline=darken_color(accent))

        # Rosy cheeks - symmetrical
        cheek_y = cy - s * 0.08
        self.canvas.create_oval(cx - s * 0.24, cheek_y - s * 0.05, cx - s * 0.1, cheek_y + s * 0.05, fill=cheek_color, outline="")
        self.canvas.create_oval(cx + s * 0.1, cheek_y - s * 0.05, cx + s * 0.24, cheek_y + s * 0.05, fill=cheek_color, outline="")

        # Orange feet - centered at bottom
        feet_y = cy + s * 0.38
        self.canvas.create_oval(cx - s * 0.22, feet_y, cx - s * 0.04, feet_y + s * 0.15, fill=accent, outline=darken_color(accent))
        self.canvas.create_oval(cx + s * 0.04, feet_y, cx + s * 0.22, feet_y + s * 0.15, fill=accent, outline=darken_color(accent))

    def _draw_leafkit(self) -> None:
        """Draw Leafkit - Grass kitten with leaf ears and vine tail (cute and aligned)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        stripes = self.data["secondary"]
        flower = self.data["accent"]
        outline = darken_color(body)

        # Vine tail with leaf (behind) - properly attached to body
        tail_start_x = cx + s * 0.32
        tail_start_y = cy + s * 0.15
        self.canvas.create_line(tail_start_x, tail_start_y, cx + s * 0.55, cy, cx + s * 0.72, cy + s * 0.08, fill=stripes, width=3, smooth=True)
        # Leaf at end - properly shaped
        leaf_pts = [cx + s * 0.68, cy + s * 0.03, cx + s * 0.88, cy - s * 0.1, cx + s * 0.78, cy + s * 0.18]
        self.canvas.create_polygon(leaf_pts, fill=body, outline=stripes)

        # Cat body curled - centered
        self.canvas.create_oval(cx - s * 0.42, cy - s * 0.08, cx + s * 0.38, cy + s * 0.45, fill=body, outline=outline, width=1)

        # Stripes on body
        self.canvas.create_arc(cx - s * 0.28, cy + s * 0.02, cx + s * 0.18, cy + s * 0.28, start=0, extent=180, style=tk.ARC, outline=stripes, width=2)

        # Head - centered
        head_cy = cy - s * 0.28
        self.canvas.create_oval(cx - s * 0.32, head_cy - s * 0.25, cx + s * 0.32, head_cy + s * 0.25, fill=body, outline=outline, width=1)

        # Leaf-shaped ears - properly shaped and positioned
        ear_base_y = head_cy - s * 0.12

        leaf_ear_l = [cx - s * 0.22, ear_base_y, cx - s * 0.4, ear_base_y - s * 0.35, cx - s * 0.15, ear_base_y - s * 0.28, cx - s * 0.05, ear_base_y]
        self.canvas.create_polygon(leaf_ear_l, fill=body, outline=stripes, smooth=True)

        leaf_ear_r = [cx + s * 0.05, ear_base_y, cx + s * 0.15, ear_base_y - s * 0.28, cx + s * 0.4, ear_base_y - s * 0.35, cx + s * 0.22, ear_base_y]
        self.canvas.create_polygon(leaf_ear_r, fill=body, outline=stripes, smooth=True)

        # Flower bud on head - centered between ears
        flower_y = head_cy - s * 0.48
        self.canvas.create_oval(cx - s * 0.08, flower_y - s * 0.08, cx + s * 0.08, flower_y + s * 0.08, fill=flower, outline=darken_color(flower))

        # Cat eyes (with slit pupils) - centered
        eye_y = head_cy
        for offset in [-s * 0.12, s * 0.12]:
            self.canvas.create_oval(cx + offset - 4, eye_y - 4, cx + offset + 4, eye_y + 4, fill=stripes, outline="#2F2F2F")
            self.canvas.create_oval(cx + offset - 1, eye_y - 3, cx + offset + 1, eye_y + 3, fill="#2F2F2F", outline="")

        # Pink nose - centered
        nose_y = head_cy + s * 0.12
        nose_pts = [cx, nose_y - s * 0.05, cx - 3, nose_y + s * 0.03, cx + 3, nose_y + s * 0.03]
        self.canvas.create_polygon(nose_pts, fill="#FFB6C1", outline="")

        # Front paws - centered at bottom
        paw_y = cy + s * 0.32
        self.canvas.create_oval(cx - s * 0.28, paw_y, cx - s * 0.08, paw_y + s * 0.15, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.08, paw_y, cx + s * 0.28, paw_y + s * 0.15, fill=body, outline=outline)

    def _draw_sparkrat(self) -> None:
        """Draw Sparkrat - Electric mouse standing on hind legs (properly proportioned)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        light = self.data["secondary"]
        cheeks = self.data["accent"]
        outline = darken_color(body)

        # Zigzag tail (behind) - properly shaped lightning bolt
        tail_pts = [
            cx + s * 0.28, cy + s * 0.15,
            cx + s * 0.45, cy + s * 0.05,
            cx + s * 0.4, cy + s * 0.25,
            cx + s * 0.6, cy + s * 0.1,
            cx + s * 0.52, cy + s * 0.35,
            cx + s * 0.75, cy + s * 0.2,
        ]
        self.canvas.create_line(tail_pts, fill=body, width=4)

        # Chubby body (standing upright) - centered
        self.canvas.create_oval(cx - s * 0.38, cy - s * 0.18, cx + s * 0.38, cy + s * 0.48, fill=body, outline=outline, width=1)

        # Belly - centered
        self.canvas.create_oval(cx - s * 0.24, cy - s * 0.05, cx + s * 0.24, cy + s * 0.32, fill=light, outline="")

        # Head - centered
        head_cy = cy - s * 0.28
        self.canvas.create_oval(cx - s * 0.32, head_cy - s * 0.25, cx + s * 0.32, head_cy + s * 0.25, fill=body, outline=outline, width=1)

        # Round ears with black inside - symmetrically positioned
        ear_y = head_cy - s * 0.15

        # Left ear
        self.canvas.create_oval(cx - s * 0.42, ear_y - s * 0.2, cx - s * 0.15, ear_y + s * 0.1, fill=body, outline=outline)
        self.canvas.create_oval(cx - s * 0.36, ear_y - s * 0.14, cx - s * 0.21, ear_y + s * 0.04, fill="#2F2F2F", outline="")

        # Right ear
        self.canvas.create_oval(cx + s * 0.15, ear_y - s * 0.2, cx + s * 0.42, ear_y + s * 0.1, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.21, ear_y - s * 0.14, cx + s * 0.36, ear_y + s * 0.04, fill="#2F2F2F", outline="")

        # Cheek marks - symmetrically positioned
        cheek_y = head_cy + s * 0.05
        for side in [-1, 1]:
            cheek_x = cx + side * s * 0.26
            self.canvas.create_oval(cheek_x - 5, cheek_y - 4, cheek_x + 5, cheek_y + 4, fill=cheeks, outline="")

        # Eyes - centered
        eye_y = head_cy - s * 0.02
        for offset in [-s * 0.12, s * 0.12]:
            self.canvas.create_oval(cx + offset - 3, eye_y - 3, cx + offset + 3, eye_y + 3, fill="#2F2F2F", outline="")
            self.canvas.create_oval(cx + offset - 1, eye_y - 2, cx + offset + 1, eye_y, fill="white", outline="")

        # Nose - centered
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 2, nose_y - 2, cx + 2, nose_y + 2, fill="#2F2F2F", outline="")

        # Little arms/paws raised - symmetrical
        arm_y = cy - s * 0.02
        self.canvas.create_oval(cx - s * 0.32, arm_y, cx - s * 0.18, arm_y + s * 0.15, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.18, arm_y, cx + s * 0.32, arm_y + s * 0.15, fill=body, outline=outline)

        # Feet - centered at bottom
        feet_y = cy + s * 0.35
        self.canvas.create_oval(cx - s * 0.26, feet_y, cx - s * 0.06, feet_y + s * 0.15, fill=body, outline=outline)
        self.canvas.create_oval(cx + s * 0.06, feet_y, cx + s * 0.26, feet_y + s * 0.15, fill=body, outline=outline)

    def _draw_drakeling(self) -> None:
        """Draw Drakeling - Baby dragon with tiny wings (wings at shoulders, horns on head)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        scales = self.data["secondary"]
        wings = self.data["accent"]
        outline = darken_color(body)
        horn_color = "#E4C9B4"  # Soft tan horns

        # Curled tail with arrow tip (behind) - properly attached
        tail_pts = [cx + s * 0.32, cy + s * 0.25, cx + s * 0.55, cy + s * 0.4, cx + s * 0.72, cy + s * 0.25, cx + s * 0.58, cy + s * 0.15]
        self.canvas.create_polygon(tail_pts, fill=body, outline=scales, smooth=True)
        # Arrow tip
        arrow_pts = [cx + s * 0.68, cy + s * 0.2, cx + s * 0.88, cy + s * 0.15, cx + s * 0.72, cy + s * 0.32]
        self.canvas.create_polygon(arrow_pts, fill=scales, outline="")

        # Tiny bat-like wings (behind body) - attached at shoulder level
        wing_y = cy - s * 0.12
        wing_l = [cx - s * 0.28, wing_y, cx - s * 0.58, wing_y - s * 0.28, cx - s * 0.48, wing_y, cx - s * 0.4, wing_y - s * 0.15, cx - s * 0.32, wing_y + s * 0.12]
        self.canvas.create_polygon(wing_l, fill=wings, outline=scales)

        wing_r = [cx + s * 0.28, wing_y, cx + s * 0.58, wing_y - s * 0.28, cx + s * 0.48, wing_y, cx + s * 0.4, wing_y - s * 0.15, cx + s * 0.32, wing_y + s * 0.12]
        self.canvas.create_polygon(wing_r, fill=wings, outline=scales)

        # Dragon body sitting - centered
        self.canvas.create_oval(cx - s * 0.38, cy - s * 0.12, cx + s * 0.38, cy + s * 0.48, fill=body, outline=scales, width=1)

        # Belly scales - centered
        self.canvas.create_oval(cx - s * 0.2, cy + s * 0.0, cx + s * 0.2, cy + s * 0.32, fill=lighten_color(body, 0.3), outline="")

        # Head - centered
        head_cy = cy - s * 0.28
        self.canvas.create_oval(cx - s * 0.3, head_cy - s * 0.22, cx + s * 0.3, head_cy + s * 0.22, fill=body, outline=scales, width=1)

        # Small horns on top of head - symmetrical
        horn_base_y = head_cy - s * 0.15
        horn_tip_y = head_cy - s * 0.48

        horn_l = [cx - s * 0.18, horn_base_y, cx - s * 0.28, horn_tip_y, cx - s * 0.08, horn_base_y + s * 0.05]
        self.canvas.create_polygon(horn_l, fill=horn_color, outline=darken_color(horn_color))

        horn_r = [cx + s * 0.08, horn_base_y + s * 0.05, cx + s * 0.28, horn_tip_y, cx + s * 0.18, horn_base_y]
        self.canvas.create_polygon(horn_r, fill=horn_color, outline=darken_color(horn_color))

        # Eyes (golden with slit pupils) - centered
        eye_y = head_cy
        for offset in [-s * 0.1, s * 0.1]:
            self.canvas.create_oval(cx + offset - 4, eye_y - 4, cx + offset + 4, eye_y + 4, fill="#FFD700", outline="#2F2F2F")
            self.canvas.create_oval(cx + offset - 1, eye_y - 3, cx + offset + 1, eye_y + 3, fill="#2F2F2F", outline="")

        # Snout/nose - centered
        nose_y = head_cy + s * 0.12
        self.canvas.create_oval(cx - 3, nose_y - 2, cx + 3, nose_y + 3, fill=scales, outline="")
        # Nostrils
        self.canvas.create_oval(cx - 4, nose_y, cx - 2, nose_y + 2, fill="#2F2F2F", outline="")
        self.canvas.create_oval(cx + 2, nose_y, cx + 4, nose_y + 2, fill="#2F2F2F", outline="")

        # Front claws - centered at bottom
        claw_y = cy + s * 0.32
        self.canvas.create_oval(cx - s * 0.26, claw_y, cx - s * 0.06, claw_y + s * 0.15, fill=body, outline=scales)
        self.canvas.create_oval(cx + s * 0.06, claw_y, cx + s * 0.26, claw_y + s * 0.15, fill=body, outline=scales)

    def _draw_shimi(self) -> None:
        """Draw Shimi - Ghost cat with fading wispy bottom (ethereal and floaty)."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        body = self.data["primary"]
        glow = self.data["secondary"]
        white = self.data["accent"]

        # Ghostly aura (outer glow) - centered
        self.canvas.create_oval(cx - s * 0.55, cy - s * 0.65, cx + s * 0.55, cy + s * 0.5, fill=lighten_color(body, 0.6), outline="")

        # Wispy fading tail (to the side and fading)
        for i in range(3):
            alpha_fade = lighten_color(body, i * 0.2)
            self.canvas.create_oval(
                cx + s * 0.32 + i * 7, cy + s * 0.05 - i * 3,
                cx + s * 0.5 + i * 7, cy + s * 0.25 - i * 3,
                fill=alpha_fade, outline=""
            )

        # Cat silhouette body (fades at bottom - no legs) - centered
        self.canvas.create_oval(cx - s * 0.38, cy - s * 0.4, cx + s * 0.38, cy + s * 0.2, fill=body, outline="")

        # Wispy bottom (fading triangle instead of legs) - properly shaped for ghostly effect
        wisps = [cx - s * 0.32, cy + s * 0.1, cx, cy + s * 0.5, cx + s * 0.32, cy + s * 0.1]
        self.canvas.create_polygon(wisps, fill=body, outline="", smooth=True)

        # Pointed cat ears - centered
        ear_base_y = cy - s * 0.32
        ear_tip_y = cy - s * 0.7

        ear_l = [cx - s * 0.28, ear_base_y, cx - s * 0.42, ear_tip_y, cx - s * 0.1, ear_base_y]
        self.canvas.create_polygon(ear_l, fill=glow, outline=body)

        ear_r = [cx + s * 0.1, ear_base_y, cx + s * 0.42, ear_tip_y, cx + s * 0.28, ear_base_y]
        self.canvas.create_polygon(ear_r, fill=glow, outline=body)

        # Glowing white/blue eyes - centered and properly sized
        eye_y = cy - s * 0.15
        for offset in [-s * 0.15, s * 0.15]:
            # Glow effect
            self.canvas.create_oval(cx + offset - 6, eye_y - 5, cx + offset + 6, eye_y + 5, fill=white, outline="")
            # Eye core
            self.canvas.create_oval(cx + offset - 3, eye_y - 3, cx + offset + 3, eye_y + 3, fill="#87CEEB", outline="")

        # No nose or mouth - ethereal/mysterious


class CreatureSelectionScreen:
    """
    Selection screen for choosing a creature type.

    Displays a 5x2 grid of creatures with animated previews.
    """

    WINDOW_WIDTH = 680
    WINDOW_HEIGHT = 420
    CELL_SIZE = 120
    PREVIEW_SIZE = 35

    def __init__(
        self,
        on_select: Callable[[str], None],
        on_cancel: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Initialize selection screen.

        Args:
            on_select: Callback when a creature is selected.
            on_cancel: Callback when selection is cancelled.
        """
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.selected_creature: Optional[str] = None
        self.previews: list[tuple[tk.Canvas, CreaturePreview]] = []
        self.animation_phase = 0.0

        self._create_window()
        self._start_animation()

    def _create_window(self) -> None:
        """Create the selection window."""
        self.root = tk.Tk()
        self.root.title("Choose Your Floob!")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#2E2E4E")

        # Center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.WINDOW_WIDTH) // 2
        y = (screen_height - self.WINDOW_HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")

        # Title
        title_frame = tk.Frame(self.root, bg="#2E2E4E")
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame,
            text="Choose Your Floob!",
            font=("Arial", 24, "bold"),
            fg="#FFD700",
            bg="#2E2E4E"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Click on a creature to select it",
            font=("Arial", 12),
            fg="#AAAAAA",
            bg="#2E2E4E"
        )
        subtitle_label.pack()

        # Grid container
        grid_frame = tk.Frame(self.root, bg="#2E2E4E")
        grid_frame.pack(pady=10)

        # Create creature grid (5x2 for 10 creatures)
        creature_list = list(CREATURES.keys())
        for idx, creature_type in enumerate(creature_list):
            row = idx // 5
            col = idx % 5

            cell_frame = tk.Frame(
                grid_frame,
                width=self.CELL_SIZE,
                height=self.CELL_SIZE + 25,
                bg="#3E3E5E",
                highlightbackground="#5E5E7E",
                highlightthickness=2
            )
            cell_frame.grid(row=row, column=col, padx=5, pady=5)
            cell_frame.grid_propagate(False)

            # Canvas for creature preview
            canvas = tk.Canvas(
                cell_frame,
                width=self.CELL_SIZE - 10,
                height=self.CELL_SIZE - 10,
                bg="#3E3E5E",
                highlightthickness=0
            )
            canvas.pack(pady=5)

            # Create preview
            preview = CreaturePreview(
                canvas,
                creature_type,
                center_x=(self.CELL_SIZE - 10) // 2,
                center_y=(self.CELL_SIZE - 10) // 2 - 10,
                size=self.PREVIEW_SIZE
            )
            self.previews.append((canvas, preview))

            # Creature name label
            data = CREATURES[creature_type]
            name_label = tk.Label(
                cell_frame,
                text=data["name"],
                font=("Arial", 10, "bold"),
                fg="#FFFFFF",
                bg="#3E3E5E"
            )
            name_label.pack()

            # Description label
            desc_label = tk.Label(
                cell_frame,
                text=data["description"],
                font=("Arial", 8),
                fg="#AAAAAA",
                bg="#3E3E5E"
            )
            desc_label.pack()

            # Bind click events
            for widget in [cell_frame, canvas, name_label, desc_label]:
                widget.bind("<Button-1>", lambda e, ct=creature_type: self._on_creature_click(ct))
                widget.bind("<Enter>", lambda e, cf=cell_frame: self._on_hover_enter(cf))
                widget.bind("<Leave>", lambda e, cf=cell_frame: self._on_hover_leave(cf))

        # Button frame
        button_frame = tk.Frame(self.root, bg="#2E2E4E")
        button_frame.pack(pady=15)

        if self.on_cancel:
            cancel_btn = tk.Button(
                button_frame,
                text="Cancel",
                font=("Arial", 12),
                width=12,
                command=self._handle_cancel
            )
            cancel_btn.pack(side=tk.LEFT, padx=10)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._handle_cancel)

    def _on_hover_enter(self, cell_frame: tk.Frame) -> None:
        """Handle mouse entering a cell."""
        cell_frame.configure(highlightbackground="#FFD700", highlightthickness=3)

    def _on_hover_leave(self, cell_frame: tk.Frame) -> None:
        """Handle mouse leaving a cell."""
        cell_frame.configure(highlightbackground="#5E5E7E", highlightthickness=2)

    def _on_creature_click(self, creature_type: str) -> None:
        """Handle creature selection."""
        self.selected_creature = creature_type
        self.root.quit()
        self.root.destroy()
        self.on_select(creature_type)

    def _handle_cancel(self) -> None:
        """Handle cancel/close."""
        self.root.quit()
        self.root.destroy()
        if self.on_cancel:
            self.on_cancel()

    def _start_animation(self) -> None:
        """Start the preview animation loop."""
        self._animate()

    def _animate(self) -> None:
        """Animate all creature previews."""
        self.animation_phase += 0.1

        for idx, (canvas, preview) in enumerate(self.previews):
            canvas.delete("all")
            # Offset bounce phase for each creature
            bounce = math.sin(self.animation_phase + idx * 0.3) * 3
            preview.draw(bounce)

        try:
            self.root.after(50, self._animate)
        except tk.TclError:
            # Window was closed
            pass

    def run(self) -> Optional[str]:
        """
        Run the selection screen.

        Returns:
            Selected creature type, or None if cancelled.
        """
        self.root.mainloop()
        return self.selected_creature


def show_selection_screen(
    on_select: Callable[[str], None],
    on_cancel: Optional[Callable[[], None]] = None
) -> None:
    """
    Show the creature selection screen.

    Args:
        on_select: Callback when a creature is selected.
        on_cancel: Callback when selection is cancelled.
    """
    screen = CreatureSelectionScreen(on_select, on_cancel)
    screen.run()


class CreatureSelectionDialog:
    """
    Modal dialog version of creature selection for use within existing app.

    Unlike CreatureSelectionScreen which creates its own root window,
    this creates a Toplevel dialog that can be shown from an existing app.
    """

    WINDOW_WIDTH = 680
    WINDOW_HEIGHT = 420
    CELL_SIZE = 120
    PREVIEW_SIZE = 35

    def __init__(
        self,
        parent: tk.Tk,
        on_select: Callable[[str], None],
        on_cancel: Optional[Callable[[], None]] = None
    ) -> None:
        """
        Initialize selection dialog.

        Args:
            parent: Parent Tkinter window.
            on_select: Callback when a creature is selected.
            on_cancel: Callback when selection is cancelled.
        """
        self.parent = parent
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.selected_creature: Optional[str] = None
        self.previews: list[tuple[tk.Canvas, CreaturePreview]] = []
        self.animation_phase = 0.0
        self._animation_id: Optional[str] = None

        self._create_dialog()
        self._start_animation()

    def _create_dialog(self) -> None:
        """Create the selection dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Choose Your Floob!")
        self.dialog.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#2E2E4E")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Make dialog appear on top
        self.dialog.attributes("-topmost", True)

        # Center dialog on screen
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - self.WINDOW_WIDTH) // 2
        y = (screen_height - self.WINDOW_HEIGHT) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Title
        title_frame = tk.Frame(self.dialog, bg="#2E2E4E")
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame,
            text="Choose Your Floob!",
            font=("Arial", 24, "bold"),
            fg="#FFD700",
            bg="#2E2E4E"
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Click on a creature to select it (your stats will be kept)",
            font=("Arial", 12),
            fg="#AAAAAA",
            bg="#2E2E4E"
        )
        subtitle_label.pack()

        # Grid container
        grid_frame = tk.Frame(self.dialog, bg="#2E2E4E")
        grid_frame.pack(pady=10)

        # Create creature grid (5x2 for 10 creatures)
        creature_list = list(CREATURES.keys())
        for idx, creature_type in enumerate(creature_list):
            row = idx // 5
            col = idx % 5

            cell_frame = tk.Frame(
                grid_frame,
                width=self.CELL_SIZE,
                height=self.CELL_SIZE + 25,
                bg="#3E3E5E",
                highlightbackground="#5E5E7E",
                highlightthickness=2
            )
            cell_frame.grid(row=row, column=col, padx=5, pady=5)
            cell_frame.grid_propagate(False)

            # Canvas for creature preview
            canvas = tk.Canvas(
                cell_frame,
                width=self.CELL_SIZE - 10,
                height=self.CELL_SIZE - 10,
                bg="#3E3E5E",
                highlightthickness=0
            )
            canvas.pack(pady=5)

            # Create preview
            preview = CreaturePreview(
                canvas,
                creature_type,
                center_x=(self.CELL_SIZE - 10) // 2,
                center_y=(self.CELL_SIZE - 10) // 2 - 10,
                size=self.PREVIEW_SIZE
            )
            self.previews.append((canvas, preview))

            # Creature name label
            data = CREATURES[creature_type]
            name_label = tk.Label(
                cell_frame,
                text=data["name"],
                font=("Arial", 10, "bold"),
                fg="#FFFFFF",
                bg="#3E3E5E"
            )
            name_label.pack()

            # Description label
            desc_label = tk.Label(
                cell_frame,
                text=data["description"],
                font=("Arial", 8),
                fg="#AAAAAA",
                bg="#3E3E5E"
            )
            desc_label.pack()

            # Bind click events
            for widget in [cell_frame, canvas, name_label, desc_label]:
                widget.bind("<Button-1>", lambda e, ct=creature_type: self._on_creature_click(ct))
                widget.bind("<Enter>", lambda e, cf=cell_frame: self._on_hover_enter(cf))
                widget.bind("<Leave>", lambda e, cf=cell_frame: self._on_hover_leave(cf))

        # Button frame
        button_frame = tk.Frame(self.dialog, bg="#2E2E4E")
        button_frame.pack(pady=15)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 12),
            width=12,
            command=self._handle_cancel
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._handle_cancel)

    def _on_hover_enter(self, cell_frame: tk.Frame) -> None:
        """Handle mouse entering a cell."""
        cell_frame.configure(highlightbackground="#FFD700", highlightthickness=3)

    def _on_hover_leave(self, cell_frame: tk.Frame) -> None:
        """Handle mouse leaving a cell."""
        cell_frame.configure(highlightbackground="#5E5E7E", highlightthickness=2)

    def _on_creature_click(self, creature_type: str) -> None:
        """Handle creature selection."""
        self.selected_creature = creature_type
        self._stop_animation()
        self.dialog.grab_release()
        self.dialog.destroy()
        self.on_select(creature_type)

    def _handle_cancel(self) -> None:
        """Handle cancel/close."""
        self._stop_animation()
        self.dialog.grab_release()
        self.dialog.destroy()
        if self.on_cancel:
            self.on_cancel()

    def _start_animation(self) -> None:
        """Start the preview animation loop."""
        self._animate()

    def _stop_animation(self) -> None:
        """Stop the animation loop."""
        if self._animation_id is not None:
            try:
                self.dialog.after_cancel(self._animation_id)
            except tk.TclError:
                pass
            self._animation_id = None

    def _animate(self) -> None:
        """Animate all creature previews."""
        self.animation_phase += 0.1

        for idx, (canvas, preview) in enumerate(self.previews):
            canvas.delete("all")
            # Offset bounce phase for each creature
            bounce = math.sin(self.animation_phase + idx * 0.3) * 3
            preview.draw(bounce)

        try:
            self._animation_id = self.dialog.after(50, self._animate)
        except tk.TclError:
            # Window was closed
            pass


def show_selection_dialog(
    parent: tk.Tk,
    on_select: Callable[[str], None],
    on_cancel: Optional[Callable[[], None]] = None
) -> None:
    """
    Show the creature selection dialog as a modal within an existing app.

    Args:
        parent: Parent Tkinter window.
        on_select: Callback when a creature is selected.
        on_cancel: Callback when selection is cancelled.
    """
    CreatureSelectionDialog(parent, on_select, on_cancel)
