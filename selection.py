"""
Creature selection screen for the Desktop Virtual Pet.

Displays a grid of 15 creatures for the user to choose from.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import math


# Creature data: (name, description, primary_color, secondary_color)
CREATURES = {
    "sparkit": {
        "name": "Sparkit",
        "description": "Electric mouse",
        "primary": "#FFD700",  # Yellow
        "secondary": "#000000",  # Black tips
        "accent": "#FF69B4",  # Pink cheeks
    },
    "fumewl": {
        "name": "Fumewl",
        "description": "Fire owl",
        "primary": "#FF6B35",  # Orange-red
        "secondary": "#FF4500",  # Flame orange
        "accent": "#FFD700",  # Ember eyes
    },
    "drophin": {
        "name": "Drophin",
        "description": "Water sprite",
        "primary": "#87CEEB",  # Light blue
        "secondary": "#4169E1",  # Royal blue
        "accent": "#00CED1",  # Cyan gem
    },
    "clovekit": {
        "name": "Clovekit",
        "description": "Lucky cat",
        "primary": "#98FB98",  # Mint green
        "secondary": "#228B22",  # Forest green
        "accent": "#FFD700",  # Gold eyes
    },
    "emberpup": {
        "name": "Emberpup",
        "description": "Fire dog",
        "primary": "#FF7F50",  # Coral orange
        "secondary": "#FF4500",  # Red-orange
        "accent": "#2F2F2F",  # Coal nose
    },
    "lunavee": {
        "name": "Lunavee",
        "description": "Moon rabbit",
        "primary": "#B0C4DE",  # Light steel blue
        "secondary": "#E6E6FA",  # Lavender
        "accent": "#FFD700",  # Star gold
    },
    "puffox": {
        "name": "Puffox",
        "description": "Cloud fox",
        "primary": "#FFB6C1",  # Light pink
        "secondary": "#87CEEB",  # Light blue
        "accent": "#DDA0DD",  # Plum swirls
    },
    "gemling": {
        "name": "Gemling",
        "description": "Crystal creature",
        "primary": "#E6E6FA",  # Lavender
        "secondary": "#9370DB",  # Medium purple
        "accent": "#FF69B4",  # Pink gem
    },
    "thornpaw": {
        "name": "Thornpaw",
        "description": "Grass cat",
        "primary": "#90EE90",  # Light green
        "secondary": "#228B22",  # Forest green
        "accent": "#FF69B4",  # Flower pink
    },
    "flickett": {
        "name": "Flickett",
        "description": "Electric bunny",
        "primary": "#FFFF00",  # Bright yellow
        "secondary": "#FFD700",  # Gold
        "accent": "#FF6B6B",  # Spark red
    },
    "soochi": {
        "name": "Soochi",
        "description": "Psychic fox",
        "primary": "#9370DB",  # Medium purple
        "secondary": "#4B0082",  # Indigo
        "accent": "#FF00FF",  # Magenta
    },
    "kibble": {
        "name": "Kibble",
        "description": "Normal type cutie",
        "primary": "#F5DEB3",  # Wheat/cream
        "secondary": "#DEB887",  # Burlywood
        "accent": "#FF69B4",  # Pink nose
    },
    "wispurr": {
        "name": "Wispurr",
        "description": "Ghost cat",
        "primary": "#9370DB",  # Purple
        "secondary": "#E6E6FA",  # Lavender
        "accent": "#FFFFFF",  # White glow
    },
    "tidekit": {
        "name": "Tidekit",
        "description": "Water kitten",
        "primary": "#ADD8E6",  # Light blue
        "secondary": "#4169E1",  # Royal blue
        "accent": "#00CED1",  # Cyan bubbles
    },
    "charrix": {
        "name": "Charrix",
        "description": "Fire fox",
        "primary": "#FF6347",  # Tomato red
        "secondary": "#FF4500",  # Orange-red
        "accent": "#FFD700",  # Ember gold
    },
}


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
        self.data = CREATURES.get(creature_type, CREATURES["kibble"])

    def draw(self, bounce: float = 0) -> None:
        """Draw the creature preview with optional bounce offset."""
        self.bounce_offset = bounce
        method_name = f"_draw_{self.creature_type}"
        draw_method = getattr(self, method_name, self._draw_default)
        draw_method()

    def _draw_default(self) -> None:
        """Default drawing method - simple blob."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Body
        self.canvas.create_oval(
            cx - s, cy - s * 0.9,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Eyes
        eye_y = cy - s * 0.15
        for offset in [-s * 0.35, s * 0.35]:
            self.canvas.create_oval(
                cx + offset - 4, eye_y - 5,
                cx + offset + 4, eye_y + 5,
                fill="white",
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 2,
                cx + offset + 2, eye_y + 2,
                fill="#2F2F2F",
                outline=""
            )

    def _draw_sparkit(self) -> None:
        """Draw Sparkit - Electric mouse."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Body
        self.canvas.create_oval(
            cx - s, cy - s * 0.8,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Ears (round with black tips)
        for side in [-1, 1]:
            ear_x = cx + side * s * 0.7
            ear_y = cy - s * 0.7
            # Outer ear
            self.canvas.create_oval(
                ear_x - s * 0.4, ear_y - s * 0.5,
                ear_x + s * 0.4, ear_y + s * 0.3,
                fill=color,
                outline=darken_color(color)
            )
            # Black tip
            self.canvas.create_oval(
                ear_x - s * 0.25, ear_y - s * 0.5,
                ear_x + s * 0.25, ear_y - s * 0.1,
                fill="#000000",
                outline=""
            )

        # Rosy cheeks
        for side in [-1, 1]:
            self.canvas.create_oval(
                cx + side * s * 0.5 - 5, cy + s * 0.1 - 4,
                cx + side * s * 0.5 + 5, cy + s * 0.1 + 4,
                fill="#FF69B4",
                outline=""
            )

        # Eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 3, eye_y - 3,
                cx + offset + 3, eye_y + 3,
                fill="#2F2F2F",
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 1, eye_y - 2,
                cx + offset + 1, eye_y,
                fill="white",
                outline=""
            )

        # Nose
        self.canvas.create_oval(
            cx - 2, cy + s * 0.2 - 2,
            cx + 2, cy + s * 0.2 + 2,
            fill="#FF6B6B",
            outline=""
        )

        # Lightning bolt tail
        tail_x = cx + s * 0.9
        tail_y = cy
        points = [
            tail_x, tail_y - 3,
            tail_x + 8, tail_y - 8,
            tail_x + 5, tail_y,
            tail_x + 15, tail_y + 5,
            tail_x + 3, tail_y + 2,
            tail_x + 6, tail_y + 8,
            tail_x, tail_y + 3,
        ]
        self.canvas.create_polygon(
            points,
            fill=color,
            outline=darken_color(color)
        )

    def _draw_fumewl(self) -> None:
        """Draw Fumewl - Fire owl."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Body (oval)
        self.canvas.create_oval(
            cx - s * 0.85, cy - s * 0.9,
            cx + s * 0.85, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Ear tufts (flame-like)
        for side in [-1, 1]:
            tuft_x = cx + side * s * 0.5
            tuft_y = cy - s * 0.8
            points = [
                tuft_x - side * 3, tuft_y + 8,
                tuft_x, tuft_y - 8,
                tuft_x + side * 5, tuft_y + 5,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=""
            )

        # Big round eyes
        eye_y = cy - s * 0.15
        for offset in [-s * 0.3, s * 0.3]:
            # Eye white
            self.canvas.create_oval(
                cx + offset - 7, eye_y - 8,
                cx + offset + 7, eye_y + 8,
                fill="white",
                outline="#2F2F2F"
            )
            # Ember iris
            self.canvas.create_oval(
                cx + offset - 4, eye_y - 4,
                cx + offset + 4, eye_y + 4,
                fill="#FF8C00",
                outline=""
            )
            # Pupil
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 2,
                cx + offset + 2, eye_y + 2,
                fill="#2F2F2F",
                outline=""
            )

        # Small beak
        self.canvas.create_polygon(
            cx, cy + s * 0.15,
            cx - 4, cy + s * 0.3,
            cx + 4, cy + s * 0.3,
            fill="#FFD700",
            outline=darken_color("#FFD700")
        )

        # Wing stubs
        for side in [-1, 1]:
            self.canvas.create_arc(
                cx + side * s * 0.5, cy - s * 0.1,
                cx + side * s * 1.1, cy + s * 0.6,
                start=90 if side == 1 else 0,
                extent=90,
                style=tk.CHORD,
                fill=darken_color(color),
                outline=""
            )

    def _draw_drophin(self) -> None:
        """Draw Drophin - Water sprite."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Teardrop body
        points = [
            cx, cy - s,
            cx + s * 0.8, cy + s * 0.3,
            cx + s * 0.5, cy + s,
            cx, cy + s * 0.8,
            cx - s * 0.5, cy + s,
            cx - s * 0.8, cy + s * 0.3,
        ]
        self.canvas.create_polygon(
            points,
            fill=color,
            outline=self.data["secondary"],
            width=2,
            smooth=True
        )

        # Forehead gem
        self.canvas.create_oval(
            cx - 4, cy - s * 0.6 - 4,
            cx + 4, cy - s * 0.6 + 4,
            fill=self.data["accent"],
            outline=darken_color(self.data["accent"])
        )

        # Fin ears
        for side in [-1, 1]:
            self.canvas.create_polygon(
                cx + side * s * 0.4, cy - s * 0.3,
                cx + side * s * 0.7, cy - s * 0.6,
                cx + side * s * 0.8, cy - s * 0.2,
                fill=color,
                outline=self.data["secondary"]
            )

        # Eyes
        eye_y = cy - s * 0.15
        for offset in [-s * 0.25, s * 0.25]:
            self.canvas.create_oval(
                cx + offset - 4, eye_y - 4,
                cx + offset + 4, eye_y + 4,
                fill="white",
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 1,
                cx + offset + 2, eye_y + 3,
                fill="#2F2F2F",
                outline=""
            )

        # Dolphin snout
        self.canvas.create_arc(
            cx - s * 0.3, cy + s * 0.1,
            cx + s * 0.3, cy + s * 0.5,
            start=200, extent=140,
            style=tk.ARC,
            outline="#2F2F2F",
            width=2
        )

    def _draw_clovekit(self) -> None:
        """Draw Clovekit - Lucky cat."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.8,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Cat ears (one up, one flopped)
        # Left ear (up)
        points_left = [
            cx - s * 0.5, cy - s * 0.5,
            cx - s * 0.3, cy - s * 1.1,
            cx - s * 0.1, cy - s * 0.5,
        ]
        self.canvas.create_polygon(points_left, fill=color, outline=darken_color(color))
        # Inner ear
        self.canvas.create_polygon(
            cx - s * 0.45, cy - s * 0.5,
            cx - s * 0.3, cy - s * 0.9,
            cx - s * 0.15, cy - s * 0.5,
            fill="#FFB6C1", outline=""
        )

        # Right ear (flopped)
        points_right = [
            cx + s * 0.1, cy - s * 0.5,
            cx + s * 0.5, cy - s * 0.7,
            cx + s * 0.6, cy - s * 0.3,
        ]
        self.canvas.create_polygon(points_right, fill=color, outline=darken_color(color))

        # Big golden eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 6,
                cx + offset + 5, eye_y + 6,
                fill=self.data["accent"],
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 2,
                cx + offset + 2, eye_y + 2,
                fill="#2F2F2F",
                outline=""
            )

        # Small pink nose
        self.canvas.create_polygon(
            cx, cy + s * 0.15,
            cx - 3, cy + s * 0.25,
            cx + 3, cy + s * 0.25,
            fill="#FFB6C1",
            outline=""
        )

        # Whiskers
        for side in [-1, 1]:
            for dy in [-3, 3]:
                self.canvas.create_line(
                    cx + side * s * 0.2, cy + s * 0.25 + dy,
                    cx + side * s * 0.7, cy + s * 0.2 + dy * 1.5,
                    fill="#333333",
                    width=1
                )

        # Four-leaf clover tail
        tail_x = cx + s
        tail_y = cy + s * 0.2
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            leaf_cx = tail_x + math.cos(rad) * 6
            leaf_cy = tail_y + math.sin(rad) * 6
            self.canvas.create_oval(
                leaf_cx - 4, leaf_cy - 4,
                leaf_cx + 4, leaf_cy + 4,
                fill=self.data["secondary"],
                outline=""
            )

    def _draw_emberpup(self) -> None:
        """Draw Emberpup - Fire dog."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Floppy dog ears with flame tips
        for side in [-1, 1]:
            # Ear base
            self.canvas.create_oval(
                cx + side * s * 0.5, cy - s * 0.7,
                cx + side * s * 1.1, cy + s * 0.1,
                fill=color,
                outline=darken_color(color)
            )
            # Flame tip
            tip_x = cx + side * s * 0.9
            tip_y = cy - s * 0.6
            self.canvas.create_polygon(
                tip_x - 4, tip_y + 5,
                tip_x, tip_y - 8,
                tip_x + 4, tip_y + 5,
                fill=self.data["secondary"],
                outline=""
            )

        # Happy eyes (arcs)
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_arc(
                cx + offset - 5, eye_y - 5,
                cx + offset + 5, eye_y + 5,
                start=0, extent=180,
                style=tk.ARC,
                outline="#2F2F2F",
                width=2
            )

        # Coal black nose
        self.canvas.create_oval(
            cx - 4, cy + s * 0.15 - 3,
            cx + 4, cy + s * 0.15 + 3,
            fill=self.data["accent"],
            outline=""
        )

        # Happy panting mouth
        self.canvas.create_arc(
            cx - 8, cy + s * 0.2,
            cx + 8, cy + s * 0.5,
            start=200, extent=140,
            style=tk.CHORD,
            fill="#FF6B6B",
            outline="#2F2F2F"
        )

        # Flame tail
        tail_x = cx + s * 0.8
        tail_y = cy + s * 0.3
        points = [
            tail_x, tail_y,
            tail_x + 8, tail_y - 15,
            tail_x + 12, tail_y - 5,
            tail_x + 5, tail_y,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.data["secondary"],
            outline=darken_color(self.data["secondary"]),
            smooth=True
        )

    def _draw_lunavee(self) -> None:
        """Draw Lunavee - Moon rabbit."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Silvery blue body
        self.canvas.create_oval(
            cx - s, cy - s * 0.8,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Long upright rabbit ears with star tips
        for side in [-1, 1]:
            ear_x = cx + side * s * 0.3
            # Outer ear
            self.canvas.create_oval(
                ear_x - s * 0.2, cy - s * 1.5,
                ear_x + s * 0.2, cy - s * 0.3,
                fill=color,
                outline=darken_color(color)
            )
            # Inner ear
            self.canvas.create_oval(
                ear_x - s * 0.1, cy - s * 1.3,
                ear_x + s * 0.1, cy - s * 0.4,
                fill=self.data["secondary"],
                outline=""
            )
            # Star tip
            star_y = cy - s * 1.5
            self.canvas.create_text(
                ear_x, star_y - 3,
                text="*",
                font=("Arial", 8, "bold"),
                fill=self.data["accent"]
            )

        # Crescent moon on forehead
        self.canvas.create_arc(
            cx - 6, cy - s * 0.55,
            cx + 6, cy - s * 0.25,
            start=45, extent=180,
            style=tk.ARC,
            outline=self.data["accent"],
            width=2
        )

        # Big sparkly eyes
        eye_y = cy - s * 0.05
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 6,
                cx + offset + 5, eye_y + 6,
                fill="#FFFFFF",
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 3, eye_y - 3,
                cx + offset + 3, eye_y + 3,
                fill="#4169E1",
                outline=""
            )
            # Sparkle
            self.canvas.create_oval(
                cx + offset - 1, eye_y - 4,
                cx + offset + 1, eye_y - 2,
                fill="white",
                outline=""
            )

        # Small smile
        self.canvas.create_arc(
            cx - 5, cy + s * 0.2,
            cx + 5, cy + s * 0.4,
            start=200, extent=140,
            style=tk.ARC,
            outline="#2F2F2F",
            width=1
        )

        # Fluffy cotton tail
        tail_x = cx + s * 0.9
        tail_y = cy + s * 0.4
        self.canvas.create_oval(
            tail_x - 6, tail_y - 6,
            tail_x + 6, tail_y + 6,
            fill=self.data["secondary"],
            outline=""
        )

    def _draw_puffox(self) -> None:
        """Draw Puffox - Cloud fox."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Fluffy cloud-shaped body (multiple overlapping ovals)
        for dx, dy, sz in [(-s*0.3, 0, 0.9), (s*0.3, 0, 0.9), (0, -s*0.2, 0.85), (0, s*0.2, 0.85)]:
            self.canvas.create_oval(
                cx + dx - s * sz, cy + dy - s * sz * 0.8,
                cx + dx + s * sz, cy + dy + s * sz * 0.8,
                fill=color,
                outline=""
            )
        # Main body overlay
        self.canvas.create_oval(
            cx - s * 0.8, cy - s * 0.7,
            cx + s * 0.8, cy + s * 0.8,
            fill=lighten_color(color, 0.3),
            outline=darken_color(color)
        )

        # Pointy fox ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.5,
                cx + side * s * 0.3, cy - s * 1.0,
                cx + side * s * 0.7, cy - s * 0.4,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=darken_color(self.data["secondary"])
            )

        # Swirl patterns on cheeks
        for side in [-1, 1]:
            self.canvas.create_arc(
                cx + side * s * 0.3, cy - s * 0.1,
                cx + side * s * 0.6, cy + s * 0.2,
                start=0, extent=270,
                style=tk.ARC,
                outline=self.data["accent"],
                width=2
            )

        # Dreamy half-closed eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.25, s * 0.25]:
            self.canvas.create_arc(
                cx + offset - 5, eye_y - 3,
                cx + offset + 5, eye_y + 5,
                start=0, extent=180,
                style=tk.CHORD,
                fill="#2F2F2F",
                outline=""
            )
            # Highlight
            self.canvas.create_arc(
                cx + offset - 5, eye_y - 1,
                cx + offset + 5, eye_y + 5,
                start=0, extent=180,
                style=tk.ARC,
                outline="white",
                width=1
            )

        # Big fluffy tail
        tail_x = cx + s
        tail_y = cy
        for i, (dx, dy, tsz) in enumerate([(0, 0, 10), (5, -8, 8), (10, 3, 7)]):
            self.canvas.create_oval(
                tail_x + dx - tsz, tail_y + dy - tsz,
                tail_x + dx + tsz, tail_y + dy + tsz,
                fill=self.data["secondary"] if i % 2 else color,
                outline=""
            )

    def _draw_gemling(self) -> None:
        """Draw Gemling - Crystal creature."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Crystalline body (hexagonal shape)
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 90)
            points.extend([
                cx + math.cos(angle) * s * 0.9,
                cy + math.sin(angle) * s * 0.9
            ])
        self.canvas.create_polygon(
            points,
            fill=color,
            outline=self.data["secondary"],
            width=2
        )

        # Crystal facet highlights
        self.canvas.create_line(
            cx - s * 0.3, cy - s * 0.4,
            cx, cy + s * 0.2,
            fill=lighten_color(color, 0.5),
            width=2
        )
        self.canvas.create_line(
            cx + s * 0.3, cy - s * 0.4,
            cx, cy + s * 0.2,
            fill=lighten_color(color, 0.5),
            width=2
        )

        # Angular crystal ears
        for side in [-1, 1]:
            ear_points = [
                cx + side * s * 0.5, cy - s * 0.6,
                cx + side * s * 0.4, cy - s * 1.1,
                cx + side * s * 0.7, cy - s * 0.8,
            ]
            self.canvas.create_polygon(
                ear_points,
                fill=self.data["secondary"],
                outline=darken_color(self.data["secondary"])
            )

        # Glowing gem in chest
        self.canvas.create_oval(
            cx - 6, cy + s * 0.1,
            cx + 6, cy + s * 0.35,
            fill=self.data["accent"],
            outline=darken_color(self.data["accent"]),
            width=2
        )
        # Gem highlight
        self.canvas.create_oval(
            cx - 2, cy + s * 0.12,
            cx + 1, cy + s * 0.2,
            fill="white",
            outline=""
        )

        # Crystal eyes
        eye_y = cy - s * 0.2
        for offset in [-s * 0.25, s * 0.25]:
            self.canvas.create_polygon(
                cx + offset, eye_y - 5,
                cx + offset - 4, eye_y,
                cx + offset, eye_y + 5,
                cx + offset + 4, eye_y,
                fill=self.data["accent"],
                outline="#2F2F2F"
            )

        # Faceted tail
        tail_x = cx + s * 0.8
        tail_y = cy + s * 0.2
        self.canvas.create_polygon(
            tail_x, tail_y,
            tail_x + 8, tail_y - 8,
            tail_x + 15, tail_y,
            tail_x + 8, tail_y + 8,
            fill=self.data["secondary"],
            outline=darken_color(self.data["secondary"])
        )

    def _draw_thornpaw(self) -> None:
        """Draw Thornpaw - Grass cat."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Petal collar
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            petal_cx = cx + math.cos(rad) * s * 0.65
            petal_cy = cy + s * 0.1 + math.sin(rad) * s * 0.4
            self.canvas.create_oval(
                petal_cx - 5, petal_cy - 4,
                petal_cx + 5, petal_cy + 4,
                fill=self.data["accent"],
                outline=""
            )

        # Body overlay (to cover petal stems)
        self.canvas.create_oval(
            cx - s * 0.7, cy - s * 0.5,
            cx + s * 0.7, cy + s * 0.7,
            fill=color,
            outline=""
        )

        # Leaf-shaped ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.3, cy - s * 0.5,
                cx + side * s * 0.2, cy - s * 1.0,
                cx + side * s * 0.5, cy - s * 0.9,
                cx + side * s * 0.6, cy - s * 0.4,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=darken_color(self.data["secondary"]),
                smooth=True
            )

        # Green cat eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 5,
                cx + offset + 5, eye_y + 5,
                fill=self.data["secondary"],
                outline="#2F2F2F"
            )
            # Vertical pupil
            self.canvas.create_oval(
                cx + offset - 1, eye_y - 4,
                cx + offset + 1, eye_y + 4,
                fill="#2F2F2F",
                outline=""
            )

        # Cat nose
        self.canvas.create_polygon(
            cx, cy + s * 0.1,
            cx - 3, cy + s * 0.2,
            cx + 3, cy + s * 0.2,
            fill="#FFB6C1",
            outline=""
        )

        # Vine tail with flower bud
        tail_x = cx + s * 0.8
        tail_y = cy + s * 0.1
        self.canvas.create_line(
            tail_x, tail_y,
            tail_x + 10, tail_y - 10,
            tail_x + 15, tail_y - 5,
            fill=self.data["secondary"],
            width=3,
            smooth=True
        )
        # Flower bud at end
        self.canvas.create_oval(
            tail_x + 12, tail_y - 10,
            tail_x + 20, tail_y - 2,
            fill=self.data["accent"],
            outline=darken_color(self.data["accent"])
        )

    def _draw_flickett(self) -> None:
        """Draw Flickett - Electric bunny."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Body with static-fuzzy effect (jagged outline simulated)
        self.canvas.create_oval(
            cx - s, cy - s * 0.8,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2,
            dash=(3, 2)
        )

        # Long zigzag-tipped rabbit ears
        for side in [-1, 1]:
            ear_x = cx + side * s * 0.3
            # Main ear
            self.canvas.create_oval(
                ear_x - s * 0.18, cy - s * 1.3,
                ear_x + s * 0.18, cy - s * 0.3,
                fill=color,
                outline=darken_color(color)
            )
            # Zigzag tip
            tip_y = cy - s * 1.3
            points = [
                ear_x - 4, tip_y + 5,
                ear_x - 2, tip_y - 3,
                ear_x + 2, tip_y + 2,
                ear_x + 4, tip_y - 5,
            ]
            self.canvas.create_line(
                points,
                fill=self.data["accent"],
                width=2
            )

        # Spark marks on cheeks
        for side in [-1, 1]:
            spark_x = cx + side * s * 0.5
            spark_y = cy + s * 0.1
            self.canvas.create_text(
                spark_x, spark_y,
                text="*",
                font=("Arial", 10, "bold"),
                fill=self.data["accent"]
            )

        # Energetic wide eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 6,
                cx + offset + 5, eye_y + 6,
                fill="white",
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 3, eye_y - 3,
                cx + offset + 3, eye_y + 3,
                fill="#2F2F2F",
                outline=""
            )
            # Multiple sparkles for energetic look
            self.canvas.create_oval(
                cx + offset - 1, eye_y - 4,
                cx + offset + 1, eye_y - 2,
                fill="white",
                outline=""
            )

        # Excited open smile
        self.canvas.create_arc(
            cx - 6, cy + s * 0.15,
            cx + 6, cy + s * 0.4,
            start=200, extent=140,
            style=tk.CHORD,
            fill="#FF6B6B",
            outline="#2F2F2F"
        )

        # Lightning bolt feet
        for side in [-1, 1]:
            foot_x = cx + side * s * 0.4
            foot_y = cy + s * 0.85
            points = [
                foot_x - 3, foot_y - 3,
                foot_x + 3 * side, foot_y - 8,
                foot_x, foot_y,
                foot_x + 5 * side, foot_y + 5,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=""
            )

    def _draw_soochi(self) -> None:
        """Draw Soochi - Psychic fox."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Purple gradient body (simulated with overlapping ovals)
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=self.data["secondary"],
            outline=darken_color(self.data["secondary"]),
            width=2
        )
        self.canvas.create_oval(
            cx - s * 0.85, cy - s * 0.7,
            cx + s * 0.85, cy + s * 0.85,
            fill=color,
            outline=""
        )

        # Fox ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.5,
                cx + side * s * 0.2, cy - s * 1.1,
                cx + side * s * 0.7, cy - s * 0.5,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=darken_color(self.data["secondary"])
            )

        # Third eye gem on forehead
        self.canvas.create_oval(
            cx - 4, cy - s * 0.5,
            cx + 4, cy - s * 0.3,
            fill=self.data["accent"],
            outline=darken_color(self.data["accent"]),
            width=2
        )

        # Mysterious glowing eyes
        eye_y = cy - s * 0.05
        for offset in [-s * 0.3, s * 0.3]:
            # Glow effect
            self.canvas.create_oval(
                cx + offset - 7, eye_y - 7,
                cx + offset + 7, eye_y + 7,
                fill=self.data["accent"],
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 5,
                cx + offset + 5, eye_y + 5,
                fill="white",
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 2,
                cx + offset + 2, eye_y + 2,
                fill=self.data["accent"],
                outline=""
            )

        # Wispy floating tail tendrils
        tail_base_x = cx + s * 0.7
        tail_base_y = cy + s * 0.2
        for i, (curve, length) in enumerate([(10, 20), (-5, 15), (15, 18)]):
            self.canvas.create_line(
                tail_base_x, tail_base_y,
                tail_base_x + length * 0.5, tail_base_y + curve,
                tail_base_x + length, tail_base_y + curve * 0.3,
                fill=self.data["secondary"] if i % 2 else color,
                width=3 - i * 0.5,
                smooth=True
            )

    def _draw_kibble(self) -> None:
        """Draw Kibble - Normal type cutie."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Cream round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=color,
            outline=self.data["secondary"],
            width=2
        )

        # Belly
        self.canvas.create_oval(
            cx - s * 0.6, cy - s * 0.1,
            cx + s * 0.6, cy + s * 0.7,
            fill=lighten_color(color, 0.4),
            outline=""
        )

        # One floppy ear, one perked ear
        # Left ear (perked)
        points_left = [
            cx - s * 0.5, cy - s * 0.5,
            cx - s * 0.3, cy - s * 1.0,
            cx - s * 0.1, cy - s * 0.5,
        ]
        self.canvas.create_polygon(points_left, fill=color, outline=self.data["secondary"])

        # Right ear (floppy)
        self.canvas.create_oval(
            cx + s * 0.2, cy - s * 0.6,
            cx + s * 0.8, cy + s * 0.1,
            fill=color,
            outline=self.data["secondary"]
        )

        # Simple happy eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 4, eye_y - 4,
                cx + offset + 4, eye_y + 4,
                fill="#2F2F2F",
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 2,
                cx + offset, eye_y,
                fill="white",
                outline=""
            )

        # Heart-shaped pink nose
        self.canvas.create_text(
            cx, cy + s * 0.2,
            text="\u2665",
            font=("Arial", 8),
            fill=self.data["accent"]
        )

        # Tongue out
        self.canvas.create_oval(
            cx - 3, cy + s * 0.35,
            cx + 3, cy + s * 0.5,
            fill="#FF6B6B",
            outline="#2F2F2F"
        )

        # Curly tail
        tail_x = cx + s * 0.8
        tail_y = cy + s * 0.2
        self.canvas.create_arc(
            tail_x - 8, tail_y - 8,
            tail_x + 8, tail_y + 8,
            start=0, extent=270,
            style=tk.ARC,
            outline=self.data["secondary"],
            width=4
        )

    def _draw_wispurr(self) -> None:
        """Draw Wispurr - Ghost cat."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Ghostly aura (outer glow)
        self.canvas.create_oval(
            cx - s * 1.1, cy - s * 1.0,
            cx + s * 1.1, cy + s * 1.1,
            fill=lighten_color(color, 0.7),
            outline=""
        )

        # Semi-transparent purple body (fading at bottom)
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s * 0.5,
            fill=color,
            outline=""
        )
        # Wispy bottom (triangle fade)
        points = [
            cx - s * 0.8, cy + s * 0.3,
            cx, cy + s * 1.2,
            cx + s * 0.8, cy + s * 0.3,
        ]
        self.canvas.create_polygon(
            points,
            fill=color,
            outline="",
            smooth=True
        )

        # Cat ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.5,
                cx + side * s * 0.2, cy - s * 1.0,
                cx + side * s * 0.6, cy - s * 0.5,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=color
            )

        # Glowing white eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            # Glow
            self.canvas.create_oval(
                cx + offset - 6, eye_y - 6,
                cx + offset + 6, eye_y + 6,
                fill=self.data["accent"],
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 4, eye_y - 4,
                cx + offset + 4, eye_y + 4,
                fill="white",
                outline=""
            )

        # Wispy tail that fades
        tail_x = cx + s * 0.6
        tail_y = cy + s * 0.3
        for i in range(3):
            alpha = 1.0 - i * 0.3
            width = 4 - i
            self.canvas.create_line(
                tail_x + i * 5, tail_y,
                tail_x + i * 5 + 10, tail_y - 10 + i * 5,
                fill=lighten_color(color, i * 0.2),
                width=width,
                smooth=True
            )

    def _draw_tidekit(self) -> None:
        """Draw Tidekit - Water kitten."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Light blue round body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=color,
            outline=self.data["secondary"],
            width=2
        )

        # Bubble patterns
        bubble_positions = [(-s * 0.5, -s * 0.3), (s * 0.4, s * 0.2), (-s * 0.3, s * 0.4)]
        for bx, by in bubble_positions:
            self.canvas.create_oval(
                cx + bx - 4, cy + by - 4,
                cx + bx + 4, cy + by + 4,
                fill=lighten_color(color, 0.5),
                outline=self.data["accent"]
            )

        # Fin-shaped ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.4, cy - s * 0.5,
                cx + side * s * 0.2, cy - s * 0.9,
                cx + side * s * 0.5, cy - s * 0.7,
                cx + side * s * 0.7, cy - s * 0.4,
            ]
            self.canvas.create_polygon(
                points,
                fill=self.data["secondary"],
                outline=darken_color(self.data["secondary"]),
                smooth=True
            )

        # Cat eyes
        eye_y = cy - s * 0.1
        for offset in [-s * 0.3, s * 0.3]:
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 5,
                cx + offset + 5, eye_y + 5,
                fill=self.data["secondary"],
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 2, eye_y - 2,
                cx + offset + 2, eye_y + 2,
                fill="#2F2F2F",
                outline=""
            )

        # Cat nose
        self.canvas.create_polygon(
            cx, cy + s * 0.1,
            cx - 3, cy + s * 0.2,
            cx + 3, cy + s * 0.2,
            fill="#FFB6C1",
            outline=""
        )

        # Whiskers
        for side in [-1, 1]:
            for dy in [-2, 2]:
                self.canvas.create_line(
                    cx + side * s * 0.15, cy + s * 0.2 + dy,
                    cx + side * s * 0.6, cy + s * 0.15 + dy * 1.5,
                    fill="#333333",
                    width=1
                )

        # Fish-like tail
        tail_x = cx + s * 0.8
        tail_y = cy + s * 0.2
        points = [
            tail_x, tail_y,
            tail_x + 15, tail_y - 10,
            tail_x + 10, tail_y,
            tail_x + 15, tail_y + 10,
        ]
        self.canvas.create_polygon(
            points,
            fill=self.data["secondary"],
            outline=darken_color(self.data["secondary"])
        )

    def _draw_charrix(self) -> None:
        """Draw Charrix - Fire fox."""
        cx, cy = self.center_x, self.center_y - self.bounce_offset
        s = self.size
        color = self.data["primary"]

        # Orange-red body
        self.canvas.create_oval(
            cx - s, cy - s * 0.85,
            cx + s, cy + s,
            fill=color,
            outline=darken_color(color),
            width=2
        )

        # Large fox ears
        for side in [-1, 1]:
            points = [
                cx + side * s * 0.35, cy - s * 0.55,
                cx + side * s * 0.15, cy - s * 1.2,
                cx + side * s * 0.65, cy - s * 0.55,
            ]
            self.canvas.create_polygon(
                points,
                fill=color,
                outline=darken_color(color)
            )
            # Inner ear
            inner_points = [
                cx + side * s * 0.35, cy - s * 0.55,
                cx + side * s * 0.2, cy - s * 0.95,
                cx + side * s * 0.55, cy - s * 0.55,
            ]
            self.canvas.create_polygon(
                inner_points,
                fill=self.data["secondary"],
                outline=""
            )

        # Ember freckle marks on cheeks
        for side in [-1, 1]:
            for i in range(3):
                fx = cx + side * (s * 0.4 + i * 4)
                fy = cy + s * 0.05 + (i % 2) * 3
                self.canvas.create_oval(
                    fx - 2, fy - 2,
                    fx + 2, fy + 2,
                    fill=self.data["accent"],
                    outline=""
                )

        # Fierce but cute eyes
        eye_y = cy - s * 0.1
        for side_idx, offset in enumerate([-s * 0.3, s * 0.3]):
            self.canvas.create_oval(
                cx + offset - 5, eye_y - 5,
                cx + offset + 5, eye_y + 5,
                fill="white",
                outline="#2F2F2F"
            )
            self.canvas.create_oval(
                cx + offset - 3, eye_y - 2,
                cx + offset + 3, eye_y + 4,
                fill=self.data["accent"],
                outline=""
            )
            self.canvas.create_oval(
                cx + offset - 1, eye_y,
                cx + offset + 1, eye_y + 2,
                fill="#2F2F2F",
                outline=""
            )
            # Determined eyebrows
            side = -1 if side_idx == 0 else 1
            self.canvas.create_line(
                cx + offset - 5, eye_y - 8,
                cx + offset + 5, eye_y - 6 + side * 2,
                fill=darken_color(color),
                width=2
            )

        # Small nose
        self.canvas.create_oval(
            cx - 3, cy + s * 0.15 - 2,
            cx + 3, cy + s * 0.15 + 2,
            fill="#2F2F2F",
            outline=""
        )

        # Multiple small flame tails (3-5)
        tail_base_x = cx + s * 0.7
        tail_base_y = cy + s * 0.15
        for i, (angle, length, width) in enumerate([
            (-30, 18, 4), (0, 22, 5), (30, 18, 4), (-15, 15, 3), (15, 15, 3)
        ]):
            rad = math.radians(angle)
            end_x = tail_base_x + math.cos(rad) * length
            end_y = tail_base_y - math.sin(rad) * length * 0.5
            color_choice = self.data["secondary"] if i % 2 == 0 else self.data["accent"]
            self.canvas.create_line(
                tail_base_x, tail_base_y,
                end_x, end_y,
                fill=color_choice,
                width=width,
                capstyle=tk.ROUND
            )


class CreatureSelectionScreen:
    """
    Selection screen for choosing a creature type.

    Displays a 5x3 grid of creatures with animated previews.
    """

    WINDOW_WIDTH = 680
    WINDOW_HEIGHT = 580
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

        # Create creature grid (5x3)
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
