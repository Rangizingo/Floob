"""
Floob 2.0 Base Sprite System.

Provides the BlobSprite class for drawing simple, expressive blob shapes.
These are NOT detailed animals - just soft, rounded blobs that express
personality through animation and simple shapes.

Design Philosophy:
- Simple shapes: circles, ovals, rounded rectangles
- Expression through deformation (squash/stretch)
- Soft gradients and shading
- Subtle outlines for definition
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Import colors from core config
try:
    from core.config import Colors, FORM_COLORS, Sprites as SpritesConfig
except ImportError:
    # Fallback for standalone testing
    class Colors:
        SOFT_PINK = "#FFD6E0"
        SOFT_BLUE = "#A2D2FF"
        SOFT_PURPLE = "#CDB4DB"
        SOFT_CREAM = "#FFF8F0"
        SOFT_GRAY = "#E8E8E8"
        DARK_GRAY = "#C8C8C8"
        BLACK = "#2D2D2D"
        WHITE = "#FFFFFF"

    FORM_COLORS = {}

    class SpritesConfig:
        OUTLINE_WIDTH = 2


def darken_color(hex_color: str, factor: float = 0.85) -> str:
    """
    Darken a hex color by a factor.

    Args:
        hex_color: Color in "#RRGGBB" format.
        factor: Darkening factor (0.0-1.0, lower = darker).

    Returns:
        Darkened hex color string.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """
    Lighten a hex color by a factor.

    Args:
        hex_color: Color in "#RRGGBB" format.
        factor: Lightening factor (0.0-1.0, higher = lighter).

    Returns:
        Lightened hex color string.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def blend_colors(color1: str, color2: str, ratio: float = 0.5) -> str:
    """
    Blend two hex colors together.

    Args:
        color1: First color in "#RRGGBB" format.
        color2: Second color in "#RRGGBB" format.
        ratio: Blend ratio (0.0 = all color1, 1.0 = all color2).

    Returns:
        Blended hex color string.
    """
    c1 = color1.lstrip("#")
    c2 = color2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 * (1 - ratio) + r2 * ratio)
    g = int(g1 * (1 - ratio) + g2 * ratio)
    b = int(b1 * (1 - ratio) + b2 * ratio)
    return f"#{r:02x}{g:02x}{b:02x}"


@dataclass
class BlobColors:
    """
    Color scheme for a blob sprite.

    Attributes:
        primary: Main body color.
        secondary: Secondary/accent color.
        highlight: Lighter highlight color (top of blob).
        shadow: Darker shadow color (bottom of blob).
        outline: Outline color for definition.
    """
    primary: str = "#CDB4DB"  # Default soft purple
    secondary: str = "#E2D4EA"
    highlight: str = "#F0E8F4"
    shadow: str = "#A890B0"
    outline: str = "#A890B0"

    @classmethod
    def from_primary(cls, primary: str) -> BlobColors:
        """
        Create a color scheme from a primary color.

        Automatically generates highlight, shadow, and outline colors.

        Args:
            primary: Primary color in "#RRGGBB" format.

        Returns:
            BlobColors instance with derived colors.
        """
        return cls(
            primary=primary,
            secondary=lighten_color(primary, 0.2),
            highlight=lighten_color(primary, 0.4),
            shadow=darken_color(primary, 0.8),
            outline=darken_color(primary, 0.7),
        )

    @classmethod
    def from_form_id(cls, form_id: str) -> BlobColors:
        """
        Create a color scheme from a form ID.

        Args:
            form_id: Evolution form identifier (e.g., "bloblet", "sparky").

        Returns:
            BlobColors instance with form-specific colors.
        """
        if form_id in FORM_COLORS:
            form = FORM_COLORS[form_id]
            return cls(
                primary=form["primary"],
                secondary=form["secondary"],
                highlight=lighten_color(form["primary"], 0.3),
                shadow=darken_color(form["primary"], 0.8),
                outline=darken_color(form["primary"], 0.7),
            )
        return cls.from_primary(Colors.SOFT_PURPLE)


@dataclass
class AnimationParams:
    """
    Animation parameters for blob deformation.

    Attributes:
        squash: Vertical compression (0.0 = none, 1.0 = max squash).
        stretch: Horizontal stretch (0.0 = none, 1.0 = max stretch).
        rotation: Rotation angle in radians.
        scale: Overall scale multiplier.
        offset_x: Horizontal position offset.
        offset_y: Vertical position offset.
        wobble: Wobble intensity for organic movement.
    """
    squash: float = 0.0
    stretch: float = 0.0
    rotation: float = 0.0
    scale: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    wobble: float = 0.0
    wobble_phase: float = 0.0


class BlobSprite:
    """
    A simple, expressive blob sprite.

    Draws a soft, rounded blob shape that can be deformed for animation.
    The blob uses simple shapes (ovals) with gradient-like shading
    achieved through layered ovals.

    Attributes:
        base_width: Base width of the blob.
        base_height: Base height of the blob.
        colors: Color scheme for the blob.
    """

    def __init__(
        self,
        base_width: float = 60.0,
        base_height: float = 50.0,
        colors: Optional[BlobColors] = None,
    ) -> None:
        """
        Initialize the blob sprite.

        Args:
            base_width: Base width of the blob in pixels.
            base_height: Base height of the blob in pixels.
            colors: Color scheme for the blob.
        """
        self.base_width = base_width
        self.base_height = base_height
        self.colors = colors or BlobColors()
        self._canvas_items: List[int] = []

    def apply_squash_stretch(
        self,
        squash: float = 0.0,
        stretch: float = 0.0,
    ) -> Tuple[float, float]:
        """
        Calculate dimensions with squash/stretch applied.

        Squash compresses vertically and expands horizontally.
        Stretch does the opposite.

        Args:
            squash: Squash amount (0.0-1.0).
            stretch: Stretch amount (0.0-1.0).

        Returns:
            Tuple of (width, height) after deformation.
        """
        # Squash: compress height, expand width (volume preservation)
        squash_factor = 1.0 - squash * 0.4  # Max 40% height reduction
        stretch_factor = 1.0 - stretch * 0.3  # Max 30% height reduction for stretch

        # Combined deformation
        height_factor = squash_factor * (1.0 + stretch * 0.2)
        width_factor = (1.0 / squash_factor) * (1.0 - stretch * 0.1)

        # Apply stretch (opposite direction)
        if stretch > 0:
            height_factor *= (1.0 + stretch * 0.3)
            width_factor *= (1.0 - stretch * 0.15)

        width = self.base_width * width_factor
        height = self.base_height * height_factor

        return width, height

    def draw(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        rotation: float = 0.0,
        animation: Optional[AnimationParams] = None,
    ) -> List[int]:
        """
        Draw the blob sprite on a canvas.

        Args:
            canvas: Tkinter canvas to draw on.
            x: Center X coordinate.
            y: Center Y coordinate.
            scale_x: Horizontal scale multiplier.
            scale_y: Vertical scale multiplier.
            rotation: Rotation angle in radians (limited support).
            animation: Animation parameters for deformation.

        Returns:
            List of canvas item IDs created.
        """
        self._canvas_items.clear()
        animation = animation or AnimationParams()

        # Apply animation parameters
        squash = animation.squash
        stretch = animation.stretch
        total_scale = animation.scale

        # Calculate deformed dimensions
        width, height = self.apply_squash_stretch(squash, stretch)
        width *= scale_x * total_scale
        height *= scale_y * total_scale

        # Apply wobble for organic movement
        if animation.wobble > 0:
            wobble_x = math.sin(animation.wobble_phase * 2) * animation.wobble * 3
            wobble_y = math.cos(animation.wobble_phase * 3) * animation.wobble * 2
            x += wobble_x
            y += wobble_y

        # Apply position offsets
        x += animation.offset_x
        y += animation.offset_y

        # Draw the blob (bottom to top for proper layering)
        items = []

        # Shadow layer (slightly larger, at bottom)
        shadow_y = y + height * 0.05
        shadow_id = canvas.create_oval(
            x - width * 0.48, shadow_y - height * 0.45,
            x + width * 0.48, shadow_y + height * 0.48,
            fill=self.colors.shadow,
            outline="",
        )
        items.append(shadow_id)

        # Main body
        body_id = canvas.create_oval(
            x - width * 0.5, y - height * 0.5,
            x + width * 0.5, y + height * 0.5,
            fill=self.colors.primary,
            outline=self.colors.outline,
            width=SpritesConfig.OUTLINE_WIDTH,
        )
        items.append(body_id)

        # Highlight layer (smaller oval at top)
        highlight_y = y - height * 0.15
        highlight_id = canvas.create_oval(
            x - width * 0.35, highlight_y - height * 0.25,
            x + width * 0.35, highlight_y + height * 0.15,
            fill=self.colors.highlight,
            outline="",
        )
        items.append(highlight_id)

        # Small specular highlight (tiny circle near top)
        spec_x = x - width * 0.15
        spec_y = y - height * 0.25
        spec_size = min(width, height) * 0.08
        spec_id = canvas.create_oval(
            spec_x - spec_size, spec_y - spec_size * 0.7,
            spec_x + spec_size, spec_y + spec_size * 0.7,
            fill=Colors.WHITE,
            outline="",
        )
        items.append(spec_id)

        self._canvas_items = items
        return items

    def draw_egg_shape(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float = 1.0,
        animation: Optional[AnimationParams] = None,
    ) -> List[int]:
        """
        Draw an egg-shaped blob (taller, narrower at top).

        Args:
            canvas: Tkinter canvas to draw on.
            x: Center X coordinate.
            y: Center Y coordinate.
            scale: Overall scale multiplier.
            animation: Animation parameters.

        Returns:
            List of canvas item IDs created.
        """
        self._canvas_items.clear()
        animation = animation or AnimationParams()

        # Egg dimensions (taller than wide)
        width = self.base_width * 0.8 * scale * animation.scale
        height = self.base_height * 1.2 * scale * animation.scale

        # Apply wobble
        if animation.wobble > 0:
            x += math.sin(animation.wobble_phase * 2) * animation.wobble * 2
            # Slight tilt for wobble effect
            tilt = math.sin(animation.wobble_phase * 1.5) * animation.wobble * 0.1

        x += animation.offset_x
        y += animation.offset_y

        items = []

        # Main egg body (use polygon for egg shape)
        # Create egg shape using bezier-like points
        points = []
        num_points = 24
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            # Egg shape: narrower at top
            r_x = width * 0.5
            r_y = height * 0.5
            # Modify radius based on angle to create egg shape
            egg_factor = 1.0 + 0.2 * math.sin(angle)  # Wider at bottom
            px = x + r_x * math.sin(angle) * egg_factor
            py = y + r_y * math.cos(angle)
            points.extend([px, py])

        # Draw egg body
        egg_id = canvas.create_polygon(
            points,
            fill=self.colors.primary,
            outline=self.colors.outline,
            width=SpritesConfig.OUTLINE_WIDTH,
            smooth=True,
        )
        items.append(egg_id)

        # Highlight on egg
        highlight_y = y - height * 0.2
        highlight_id = canvas.create_oval(
            x - width * 0.25, highlight_y - height * 0.15,
            x + width * 0.2, highlight_y + height * 0.1,
            fill=self.colors.highlight,
            outline="",
        )
        items.append(highlight_id)

        # Specular highlight
        spec_x = x - width * 0.1
        spec_y = y - height * 0.3
        spec_size = min(width, height) * 0.06
        spec_id = canvas.create_oval(
            spec_x - spec_size, spec_y - spec_size * 0.8,
            spec_x + spec_size, spec_y + spec_size * 0.8,
            fill=Colors.WHITE,
            outline="",
        )
        items.append(spec_id)

        self._canvas_items = items
        return items

    def clear(self, canvas: tk.Canvas) -> None:
        """
        Clear all canvas items created by this sprite.

        Args:
            canvas: Canvas to clear items from.
        """
        for item_id in self._canvas_items:
            canvas.delete(item_id)
        self._canvas_items.clear()


@dataclass
class NubLimbs:
    """
    Configuration for small nub-like limbs on blobs.

    These are simple bumps/protrusions, not detailed limbs.
    """
    show_arms: bool = False
    show_legs: bool = False
    arm_size: float = 0.15  # Relative to body width
    leg_size: float = 0.12  # Relative to body width


def draw_nub_limbs(
    canvas: tk.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    colors: BlobColors,
    limbs: NubLimbs,
    walk_phase: float = 0.0,
) -> List[int]:
    """
    Draw simple nub limbs on a blob.

    Args:
        canvas: Tkinter canvas to draw on.
        x: Center X of blob.
        y: Center Y of blob.
        width: Blob width.
        height: Blob height.
        colors: Color scheme.
        limbs: Limb configuration.
        walk_phase: Animation phase for walking (0.0-1.0).

    Returns:
        List of canvas item IDs created.
    """
    items = []

    if limbs.show_arms:
        arm_w = width * limbs.arm_size
        arm_h = height * limbs.arm_size * 0.8
        arm_y = y - height * 0.1

        # Left arm
        left_x = x - width * 0.45
        left_id = canvas.create_oval(
            left_x - arm_w, arm_y - arm_h,
            left_x + arm_w * 0.5, arm_y + arm_h,
            fill=colors.primary,
            outline=colors.outline,
        )
        items.append(left_id)

        # Right arm
        right_x = x + width * 0.45
        right_id = canvas.create_oval(
            right_x - arm_w * 0.5, arm_y - arm_h,
            right_x + arm_w, arm_y + arm_h,
            fill=colors.primary,
            outline=colors.outline,
        )
        items.append(right_id)

    if limbs.show_legs:
        leg_w = width * limbs.leg_size
        leg_h = height * limbs.leg_size * 1.2
        leg_y = y + height * 0.4

        # Animate legs with walk phase
        left_offset = math.sin(walk_phase * math.pi * 2) * 3
        right_offset = -left_offset

        # Left leg
        left_x = x - width * 0.25
        left_id = canvas.create_oval(
            left_x - leg_w, leg_y - leg_h * 0.3 + left_offset,
            left_x + leg_w, leg_y + leg_h + left_offset,
            fill=colors.primary,
            outline=colors.outline,
        )
        items.append(left_id)

        # Right leg
        right_x = x + width * 0.25
        right_id = canvas.create_oval(
            right_x - leg_w, leg_y - leg_h * 0.3 + right_offset,
            right_x + leg_w, leg_y + leg_h + right_offset,
            fill=colors.primary,
            outline=colors.outline,
        )
        items.append(right_id)

    return items


class EggSprite:
    """
    Special sprite for egg stage - oval with cracks and inner glow.

    The egg is simpler than the blob:
    - Taller oval shape (egg proportions)
    - Optional crack lines that progress as hatching approaches
    - Inner glow that pulses
    - Wobble animation for anticipation
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        body_color: str = "#FFF8F0",
        accent_color: str = "#FFE8D0",
        size: float = 45.0,
    ) -> None:
        """
        Initialize the egg sprite.

        Args:
            canvas: Tkinter canvas to draw on.
            body_color: Main egg color.
            accent_color: Accent/highlight color.
            size: Base size of the egg.
        """
        self.canvas = canvas
        self.body_color = body_color
        self.accent_color = accent_color
        self.size = size
        self.items: List[int] = []

    def draw(
        self,
        x: float,
        y: float,
        crack_progress: float = 0.0,
        glow: float = 0.0,
        wobble: float = 0.0,
        wobble_phase: float = 0.0,
        scale: float = 1.0,
    ) -> List[int]:
        """
        Draw egg with optional cracks and inner glow.

        Args:
            x: Center X coordinate.
            y: Center Y coordinate.
            crack_progress: Crack visibility (0.0 = none, 1.0 = full cracks).
            glow: Inner glow intensity (0.0 = none, 1.0 = bright).
            wobble: Wobble intensity for animation.
            wobble_phase: Current phase of wobble animation.
            scale: Size scale multiplier.

        Returns:
            List of canvas item IDs created.
        """
        self.clear()

        # Apply wobble
        if wobble > 0:
            x += math.sin(wobble_phase * 2) * wobble * 2
            # Slight rotation effect via skew
            skew = math.sin(wobble_phase * 1.5) * wobble * 0.05
        else:
            skew = 0

        # Egg dimensions (taller than wide)
        width = self.size * 0.8 * scale
        height = self.size * 1.2 * scale

        # Inner glow (draw first, behind everything)
        if glow > 0:
            glow_pulse = 1.0 + math.sin(wobble_phase * 3) * 0.1
            glow_size = max(width, height) * 0.6 * glow_pulse
            glow_color = lighten_color(self.body_color, 0.4 * glow)
            glow_id = self.canvas.create_oval(
                x - glow_size, y - glow_size,
                x + glow_size, y + glow_size,
                fill=glow_color,
                outline="",
            )
            self.items.append(glow_id)

        # Create egg shape using polygon for proper egg curve
        points = self._create_egg_points(x, y, width, height, skew)

        # Main egg body
        egg_id = self.canvas.create_polygon(
            points,
            fill=self.body_color,
            outline=darken_color(self.body_color, 0.85),
            width=2,
            smooth=True,
        )
        self.items.append(egg_id)

        # Highlight at top
        hl_width = width * 0.4
        hl_height = height * 0.25
        hl_y = y - height * 0.25
        highlight_id = self.canvas.create_oval(
            x - hl_width, hl_y - hl_height,
            x + hl_width, hl_y + hl_height * 0.5,
            fill=lighten_color(self.body_color, 0.3),
            outline="",
        )
        self.items.append(highlight_id)

        # Specular highlight (small white dot)
        spec_x = x - width * 0.2
        spec_y = y - height * 0.3
        spec_size = min(width, height) * 0.08
        spec_id = self.canvas.create_oval(
            spec_x - spec_size, spec_y - spec_size * 0.7,
            spec_x + spec_size, spec_y + spec_size * 0.7,
            fill=Colors.WHITE,
            outline="",
        )
        self.items.append(spec_id)

        # Draw cracks based on progress
        if crack_progress > 0:
            self._draw_cracks(x, y, width, height, crack_progress)

        return self.items

    def _create_egg_points(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        skew: float = 0,
    ) -> List[float]:
        """
        Create egg-shaped polygon points.

        Args:
            x: Center X.
            y: Center Y.
            width: Egg width.
            height: Egg height.
            skew: Rotation skew for wobble effect.

        Returns:
            List of x, y coordinate pairs.
        """
        points = []
        num_points = 24

        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            # Egg shape: narrower at top, wider at bottom
            egg_factor = 1.0 + 0.2 * math.sin(angle)  # Wider at bottom
            px = x + (width * 0.5) * math.sin(angle + skew) * egg_factor
            py = y + (height * 0.5) * math.cos(angle)
            points.extend([px, py])

        return points

    def _draw_cracks(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        progress: float,
    ) -> None:
        """
        Draw crack lines on the egg based on progress.

        Args:
            x: Center X.
            y: Center Y.
            width: Egg width.
            height: Egg height.
            progress: Crack progress (0.0-1.0).
        """
        crack_color = darken_color(self.body_color, 0.7)

        # Main crack (appears first)
        if progress > 0.1:
            crack1_points = [
                x - width * 0.2, y - height * 0.1,
                x - width * 0.1, y,
                x - width * 0.2, y + height * 0.15,
                x - width * 0.05, y + height * 0.25,
            ]
            crack1_id = self.canvas.create_line(
                crack1_points,
                fill=crack_color,
                width=1,
            )
            self.items.append(crack1_id)

        # Secondary crack (appears at 40%)
        if progress > 0.4:
            crack2_points = [
                x + width * 0.15, y - height * 0.2,
                x + width * 0.05, y - height * 0.05,
                x + width * 0.15, y + height * 0.1,
            ]
            crack2_id = self.canvas.create_line(
                crack2_points,
                fill=crack_color,
                width=1,
            )
            self.items.append(crack2_id)

        # Branching cracks (appear at 70%)
        if progress > 0.7:
            crack3_points = [
                x - width * 0.1, y,
                x, y + height * 0.05,
                x + width * 0.05, y - height * 0.05,
            ]
            crack3_id = self.canvas.create_line(
                crack3_points,
                fill=crack_color,
                width=1,
            )
            self.items.append(crack3_id)

        # Full crack pattern (appears at 90%)
        if progress > 0.9:
            crack4_points = [
                x, y + height * 0.1,
                x + width * 0.1, y + height * 0.2,
                x, y + height * 0.35,
            ]
            crack4_id = self.canvas.create_line(
                crack4_points,
                fill=crack_color,
                width=1,
            )
            self.items.append(crack4_id)

    def clear(self) -> None:
        """Clear all canvas items created by this sprite."""
        for item_id in self.items:
            self.canvas.delete(item_id)
        self.items.clear()
