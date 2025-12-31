"""
Floob 2.0 Evolution Stage Appearances.

Defines distinct visual appearances for each evolution stage and form.
Each stage has unique characteristics:

EGG Stage:
- Oval shape with crack lines
- Gentle wobble animation
- Inner glow effect

BABY Stage (Bloblet):
- Tiny blob (60% size)
- HUGE eyes (40% of face)
- Extra wobbly movement

CHILD Stage (3 variants):
- Bouncy: Slightly taller, energetic pastel
- Balanced: Round symmetric, neutral pastel
- Sleepy: Droopy/melted look, calm pastel

TEEN Stage (5 variants):
- Sparky: Angular edges, zigzag antenna
- Zippy: Streamlined teardrop, speed lines
- Chill: Round relaxed, half-lidded eyes
- Dreamy: Cloud-like fluffy edges
- Cozy: Soft chunky shape, rosy cheeks

ADULT Stage (5 variants):
- Zapper: Sharp features, lightning marks
- Dasher: Sleek aerodynamic, motion blur
- Loafer: Big relaxed blob, content smile
- Mystic: Ethereal glow, floating particles
- Floofy: Extra fluffy edges, hearts
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

from graphics.sprites import (
    BlobSprite,
    BlobColors,
    AnimationParams,
    NubLimbs,
    draw_nub_limbs,
    darken_color,
    lighten_color,
)
from graphics.expressions import (
    ExpressionRenderer,
    EyeParams,
    MouthParams,
    EyeEmotion,
    MouthEmotion,
)

# Import config colors
try:
    from core.config import Colors, FORM_COLORS, Sprites as SpritesConfig
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
        SOFT_MINT = "#B8E0D2"
        SOFT_LAVENDER = "#D8B4E2"
        LIGHT_YELLOW = "#FFF9D6"
        WHITE = "#FFFFFF"

    FORM_COLORS = {
        "egg": {"primary": "#FFF8F0", "secondary": "#FFF9D6", "accent": "#FFB5A7"},
        "bloblet": {"primary": "#FFD6E0", "secondary": "#FFE8ED", "accent": "#FFF8F0"},
    }

    class SpritesConfig:
        EGG_SCALE = 0.7
        BABY_SCALE = 0.6
        CHILD_SCALE = 0.8
        TEEN_SCALE = 0.9
        ADULT_SCALE = 1.0
        BABY_EYE_MULTIPLIER = 1.5


class EvolutionStage(Enum):
    """Evolution stages."""
    EGG = auto()
    BABY = auto()
    CHILD = auto()
    TEEN = auto()
    ADULT = auto()


@dataclass
class FormAppearance:
    """
    Visual appearance configuration for an evolution form.

    Attributes:
        form_id: Unique identifier for this form.
        stage: Evolution stage.
        colors: Color scheme.
        scale: Size scale relative to base.
        eye_size_mult: Eye size multiplier.
        wobble_intensity: How wobbly the movement is.
        has_antenna: Whether to show antenna/protrusion.
        has_glow: Whether to show glow effect.
        expression_tendencies: Default expression emotions.
        special_features: List of special visual features.
    """
    form_id: str
    stage: EvolutionStage
    colors: BlobColors = field(default_factory=BlobColors)
    scale: float = 1.0
    eye_size_mult: float = 1.0
    wobble_intensity: float = 0.0
    has_antenna: bool = False
    has_glow: bool = False
    has_limbs: bool = False
    limb_config: NubLimbs = field(default_factory=NubLimbs)
    expression_tendencies: Dict[str, float] = field(default_factory=dict)
    special_features: List[str] = field(default_factory=list)


# Define all form appearances
FORM_APPEARANCES: Dict[str, FormAppearance] = {}


def _init_form_appearances() -> None:
    """Initialize all form appearance configurations."""
    global FORM_APPEARANCES

    # EGG Stage
    FORM_APPEARANCES["egg"] = FormAppearance(
        form_id="egg",
        stage=EvolutionStage.EGG,
        colors=BlobColors.from_form_id("egg") if "egg" in FORM_COLORS else BlobColors.from_primary(Colors.SOFT_CREAM),
        scale=SpritesConfig.EGG_SCALE,
        wobble_intensity=0.3,
        has_glow=True,
        special_features=["crack_lines", "inner_glow", "wobble"],
    )

    # BABY Stage (Bloblet)
    FORM_APPEARANCES["bloblet"] = FormAppearance(
        form_id="bloblet",
        stage=EvolutionStage.BABY,
        colors=BlobColors.from_form_id("bloblet") if "bloblet" in FORM_COLORS else BlobColors.from_primary(Colors.SOFT_PINK),
        scale=SpritesConfig.BABY_SCALE,
        eye_size_mult=SpritesConfig.BABY_EYE_MULTIPLIER,
        wobble_intensity=0.5,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=False, show_legs=True, leg_size=0.1),
        special_features=["huge_eyes", "extra_wobbly"],
    )

    # CHILD Stage (3 variants)
    FORM_APPEARANCES["bouncy"] = FormAppearance(
        form_id="bouncy",
        stage=EvolutionStage.CHILD,
        colors=BlobColors.from_primary(Colors.SOFT_YELLOW),
        scale=SpritesConfig.CHILD_SCALE,
        eye_size_mult=1.2,
        wobble_intensity=0.3,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True),
        expression_tendencies={"happy": 0.7, "energetic": 0.8},
        special_features=["taller_shape", "bounce_lines"],
    )

    FORM_APPEARANCES["balanced"] = FormAppearance(
        form_id="balanced",
        stage=EvolutionStage.CHILD,
        colors=BlobColors.from_primary(Colors.SOFT_BLUE),
        scale=SpritesConfig.CHILD_SCALE,
        eye_size_mult=1.1,
        wobble_intensity=0.2,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True),
        expression_tendencies={"content": 0.6, "calm": 0.7},
        special_features=["round_symmetric"],
    )

    FORM_APPEARANCES["sleepy"] = FormAppearance(
        form_id="sleepy",
        stage=EvolutionStage.CHILD,
        colors=BlobColors.from_primary(Colors.SOFT_LAVENDER),
        scale=SpritesConfig.CHILD_SCALE * 0.95,
        eye_size_mult=1.0,
        wobble_intensity=0.15,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, arm_size=0.12),
        expression_tendencies={"sleepy": 0.5, "relaxed": 0.7},
        special_features=["droopy_shape", "melted_look"],
    )

    # TEEN Stage (5 variants)
    FORM_APPEARANCES["sparky"] = FormAppearance(
        form_id="sparky",
        stage=EvolutionStage.TEEN,
        colors=BlobColors.from_primary(Colors.SOFT_YELLOW),
        scale=SpritesConfig.TEEN_SCALE,
        eye_size_mult=1.1,
        wobble_intensity=0.4,
        has_antenna=True,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True),
        expression_tendencies={"alert": 0.7, "excited": 0.6},
        special_features=["angular_edges", "zigzag_antenna", "spark_particles"],
    )

    FORM_APPEARANCES["zippy"] = FormAppearance(
        form_id="zippy",
        stage=EvolutionStage.TEEN,
        colors=BlobColors.from_primary(Colors.SOFT_ORANGE),
        scale=SpritesConfig.TEEN_SCALE,
        eye_size_mult=1.0,
        wobble_intensity=0.2,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, leg_size=0.15),
        expression_tendencies={"focused": 0.7, "determined": 0.6},
        special_features=["teardrop_shape", "speed_lines", "streamlined"],
    )

    FORM_APPEARANCES["chill"] = FormAppearance(
        form_id="chill",
        stage=EvolutionStage.TEEN,
        colors=BlobColors.from_primary(Colors.SOFT_BLUE),
        scale=SpritesConfig.TEEN_SCALE,
        eye_size_mult=1.0,
        wobble_intensity=0.1,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, arm_size=0.18),
        expression_tendencies={"relaxed": 0.8, "chill": 0.9},
        special_features=["round_relaxed", "half_lidded_default"],
    )

    FORM_APPEARANCES["dreamy"] = FormAppearance(
        form_id="dreamy",
        stage=EvolutionStage.TEEN,
        colors=BlobColors.from_primary(Colors.SOFT_PURPLE),
        scale=SpritesConfig.TEEN_SCALE,
        eye_size_mult=1.2,
        wobble_intensity=0.25,
        has_glow=True,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=False),
        expression_tendencies={"dreamy": 0.8, "wonder": 0.7},
        special_features=["cloud_edges", "star_particles", "fluffy"],
    )

    FORM_APPEARANCES["cozy"] = FormAppearance(
        form_id="cozy",
        stage=EvolutionStage.TEEN,
        colors=BlobColors.from_primary(Colors.SOFT_PINK),
        scale=SpritesConfig.TEEN_SCALE * 1.05,
        eye_size_mult=1.1,
        wobble_intensity=0.15,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, arm_size=0.2),
        expression_tendencies={"content": 0.8, "warm": 0.7},
        special_features=["chunky_soft", "rosy_cheeks", "warm_glow"],
    )

    # ADULT Stage (5 variants)
    FORM_APPEARANCES["zapper"] = FormAppearance(
        form_id="zapper",
        stage=EvolutionStage.ADULT,
        colors=BlobColors.from_primary(Colors.SOFT_YELLOW),
        scale=SpritesConfig.ADULT_SCALE,
        eye_size_mult=1.0,
        wobble_intensity=0.3,
        has_antenna=True,
        has_glow=True,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True),
        expression_tendencies={"alert": 0.8, "energetic": 0.7},
        special_features=["sharp_features", "lightning_marks", "electric_glow", "spark_burst"],
    )

    FORM_APPEARANCES["dasher"] = FormAppearance(
        form_id="dasher",
        stage=EvolutionStage.ADULT,
        colors=BlobColors.from_primary(Colors.SOFT_GREEN),
        scale=SpritesConfig.ADULT_SCALE,
        eye_size_mult=0.95,
        wobble_intensity=0.1,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, leg_size=0.18),
        expression_tendencies={"focused": 0.8, "determined": 0.7},
        special_features=["aerodynamic", "motion_blur", "speed_aura", "sleek"],
    )

    FORM_APPEARANCES["loafer"] = FormAppearance(
        form_id="loafer",
        stage=EvolutionStage.ADULT,
        colors=BlobColors.from_primary(Colors.SOFT_BLUE),
        scale=SpritesConfig.ADULT_SCALE * 1.1,
        eye_size_mult=1.0,
        wobble_intensity=0.05,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, arm_size=0.2, leg_size=0.15),
        expression_tendencies={"content": 0.9, "relaxed": 0.85},
        special_features=["big_relaxed", "content_smile", "soft_round"],
    )

    FORM_APPEARANCES["mystic"] = FormAppearance(
        form_id="mystic",
        stage=EvolutionStage.ADULT,
        colors=BlobColors.from_primary(Colors.SOFT_PURPLE),
        scale=SpritesConfig.ADULT_SCALE,
        eye_size_mult=1.15,
        wobble_intensity=0.2,
        has_glow=True,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=False),
        expression_tendencies={"wise": 0.7, "mystical": 0.8},
        special_features=["ethereal_glow", "floating_particles", "aura", "sparkle_eyes"],
    )

    FORM_APPEARANCES["floofy"] = FormAppearance(
        form_id="floofy",
        stage=EvolutionStage.ADULT,
        colors=BlobColors.from_primary(Colors.SOFT_PINK),
        scale=SpritesConfig.ADULT_SCALE * 1.05,
        eye_size_mult=1.2,
        wobble_intensity=0.15,
        has_limbs=True,
        limb_config=NubLimbs(show_arms=True, show_legs=True, arm_size=0.22, leg_size=0.18),
        expression_tendencies={"happy": 0.8, "loving": 0.75},
        special_features=["fluffy_edges", "heart_particles", "blush_default", "soft_fur"],
    )


# Initialize on module load
_init_form_appearances()


class EvolutionSpriteRenderer:
    """
    Renders evolution-specific sprite variations.

    Handles drawing the unique visual features for each form,
    including special effects, shapes, and decorations.
    """

    def __init__(self) -> None:
        """Initialize the evolution sprite renderer."""
        self.blob_sprite = BlobSprite()
        self.expression_renderer = ExpressionRenderer()
        self._canvas_items: List[int] = []

    def get_form_appearance(self, form_id: str) -> FormAppearance:
        """
        Get the appearance configuration for a form.

        Args:
            form_id: Form identifier.

        Returns:
            FormAppearance for the form, or default if not found.
        """
        return FORM_APPEARANCES.get(
            form_id,
            FORM_APPEARANCES.get("bloblet", FormAppearance("unknown", EvolutionStage.BABY))
        )

    def draw_form(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        form_id: str,
        animation: Optional[AnimationParams] = None,
        eye_params: Optional[EyeParams] = None,
        mouth_params: Optional[MouthParams] = None,
        show_blush: bool = False,
        show_sweat: bool = False,
        phase: float = 0.0,
    ) -> List[int]:
        """
        Draw a complete evolution form sprite.

        Args:
            canvas: Tkinter canvas to draw on.
            x: Center X coordinate.
            y: Center Y coordinate.
            form_id: Evolution form identifier.
            animation: Animation parameters.
            eye_params: Eye expression parameters.
            mouth_params: Mouth expression parameters.
            show_blush: Whether to show blush marks.
            show_sweat: Whether to show sweat drop.
            phase: Animation phase for effects.

        Returns:
            List of canvas item IDs created.
        """
        self._canvas_items.clear()
        items = []

        appearance = self.get_form_appearance(form_id)
        animation = animation or AnimationParams()

        # Apply form-specific scale and wobble
        animation.scale *= appearance.scale
        if appearance.wobble_intensity > 0:
            animation.wobble = appearance.wobble_intensity
            animation.wobble_phase = phase

        # Update blob colors
        self.blob_sprite.colors = appearance.colors

        # Draw based on stage
        if appearance.stage == EvolutionStage.EGG:
            items.extend(self._draw_egg(canvas, x, y, appearance, animation, phase))
        else:
            # Draw main body
            items.extend(self._draw_body(canvas, x, y, appearance, animation, phase))

            # Draw limbs if applicable
            if appearance.has_limbs:
                width, height = self.blob_sprite.apply_squash_stretch(
                    animation.squash, animation.stretch
                )
                width *= animation.scale
                height *= animation.scale
                items.extend(draw_nub_limbs(
                    canvas, x + animation.offset_x, y + animation.offset_y,
                    width, height, appearance.colors, appearance.limb_config, phase
                ))

            # Draw special features
            items.extend(self._draw_special_features(
                canvas, x, y, appearance, animation, phase
            ))

            # Draw face
            items.extend(self._draw_face(
                canvas, x, y, appearance, animation,
                eye_params, mouth_params, show_blush, show_sweat
            ))

        self._canvas_items = items
        return items

    def _draw_egg(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        appearance: FormAppearance,
        animation: AnimationParams,
        phase: float,
    ) -> List[int]:
        """Draw the egg stage sprite."""
        items = []

        # Inner glow (behind egg)
        if appearance.has_glow:
            glow_pulse = 1.0 + math.sin(phase * 2) * 0.1
            glow_size = 45 * animation.scale * glow_pulse
            glow_id = canvas.create_oval(
                x - glow_size, y - glow_size * 1.2,
                x + glow_size, y + glow_size * 0.8,
                fill=lighten_color(appearance.colors.primary, 0.3),
                outline="",
            )
            items.append(glow_id)

        # Draw egg body
        egg_items = self.blob_sprite.draw_egg_shape(
            canvas, x, y, animation.scale, animation
        )
        items.extend(egg_items)

        # Crack lines
        if "crack_lines" in appearance.special_features:
            items.extend(self._draw_crack_lines(
                canvas, x, y, animation.scale, phase
            ))

        return items

    def _draw_crack_lines(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
    ) -> List[int]:
        """Draw subtle crack lines on the egg."""
        items = []

        # Small cracks that appear over time
        crack_color = "#D0D0D0"
        base_size = 25 * scale

        # Main crack (zigzag)
        crack1_points = [
            x - base_size * 0.3, y - base_size * 0.2,
            x - base_size * 0.15, y - base_size * 0.1,
            x - base_size * 0.25, y + base_size * 0.1,
            x - base_size * 0.1, y + base_size * 0.2,
        ]
        crack1_id = canvas.create_line(
            crack1_points,
            fill=crack_color,
            width=1,
        )
        items.append(crack1_id)

        # Secondary smaller crack
        crack2_points = [
            x + base_size * 0.2, y - base_size * 0.15,
            x + base_size * 0.1, y,
        ]
        crack2_id = canvas.create_line(
            crack2_points,
            fill=crack_color,
            width=1,
        )
        items.append(crack2_id)

        return items

    def _draw_body(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        appearance: FormAppearance,
        animation: AnimationParams,
        phase: float,
    ) -> List[int]:
        """Draw the main blob body for non-egg stages."""
        items = []

        # Form-specific body modifications
        if "taller_shape" in appearance.special_features:
            self.blob_sprite.base_height = 55
            self.blob_sprite.base_width = 50
        elif "teardrop_shape" in appearance.special_features:
            self.blob_sprite.base_height = 60
            self.blob_sprite.base_width = 45
        elif "droopy_shape" in appearance.special_features:
            self.blob_sprite.base_height = 45
            self.blob_sprite.base_width = 55
        elif "chunky_soft" in appearance.special_features:
            self.blob_sprite.base_height = 50
            self.blob_sprite.base_width = 60
        elif "big_relaxed" in appearance.special_features:
            self.blob_sprite.base_height = 55
            self.blob_sprite.base_width = 65
        elif "aerodynamic" in appearance.special_features:
            self.blob_sprite.base_height = 50
            self.blob_sprite.base_width = 45
        else:
            # Default proportions
            self.blob_sprite.base_height = 50
            self.blob_sprite.base_width = 55

        # Draw glow effect behind body if applicable
        if appearance.has_glow:
            glow_pulse = 1.0 + math.sin(phase * 1.5) * 0.08
            width = self.blob_sprite.base_width * animation.scale * glow_pulse
            height = self.blob_sprite.base_height * animation.scale * glow_pulse
            glow_id = canvas.create_oval(
                x - width * 0.6, y - height * 0.6,
                x + width * 0.6, y + height * 0.6,
                fill=lighten_color(appearance.colors.primary, 0.4),
                outline="",
            )
            items.append(glow_id)

        # Draw main blob
        body_items = self.blob_sprite.draw(
            canvas, x, y,
            scale_x=1.0, scale_y=1.0,
            animation=animation
        )
        items.extend(body_items)

        return items

    def _draw_special_features(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        appearance: FormAppearance,
        animation: AnimationParams,
        phase: float,
    ) -> List[int]:
        """Draw form-specific special features."""
        items = []
        scale = animation.scale

        # Antenna (for sparky, zapper)
        if appearance.has_antenna or "zigzag_antenna" in appearance.special_features:
            items.extend(self._draw_antenna(canvas, x, y, scale, phase, appearance.colors))

        # Speed lines (for zippy, dasher)
        if "speed_lines" in appearance.special_features:
            items.extend(self._draw_speed_lines(canvas, x, y, scale, phase))

        # Cloud edges (for dreamy)
        if "cloud_edges" in appearance.special_features:
            items.extend(self._draw_cloud_puffs(canvas, x, y, scale, phase, appearance.colors))

        # Fluffy edges (for floofy)
        if "fluffy_edges" in appearance.special_features:
            items.extend(self._draw_fluffy_edges(canvas, x, y, scale, phase, appearance.colors))

        # Lightning marks (for zapper)
        if "lightning_marks" in appearance.special_features:
            items.extend(self._draw_lightning_marks(canvas, x, y, scale, appearance.colors))

        # Star particles (for dreamy, mystic)
        if "star_particles" in appearance.special_features:
            items.extend(self._draw_star_particles(canvas, x, y, scale, phase))

        # Floating particles (for mystic)
        if "floating_particles" in appearance.special_features:
            items.extend(self._draw_floating_particles(canvas, x, y, scale, phase, appearance.colors))

        return items

    def _draw_antenna(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
        colors: BlobColors,
    ) -> List[int]:
        """Draw a zigzag antenna on top of the blob."""
        items = []

        # Antenna sway
        sway = math.sin(phase * 3) * 3

        # Zigzag points
        base_y = y - 30 * scale
        points = [
            x + sway * 0.2, base_y,
            x + 5 + sway * 0.5, base_y - 8 * scale,
            x - 3 + sway * 0.7, base_y - 16 * scale,
            x + 4 + sway, base_y - 24 * scale,
        ]

        # Draw antenna line
        line_id = canvas.create_line(
            points,
            fill=colors.outline,
            width=2,
        )
        items.append(line_id)

        # Ball at top
        ball_x = x + 4 + sway
        ball_y = base_y - 24 * scale
        ball_size = 5 * scale
        ball_id = canvas.create_oval(
            ball_x - ball_size, ball_y - ball_size,
            ball_x + ball_size, ball_y + ball_size,
            fill=colors.secondary,
            outline=colors.outline,
        )
        items.append(ball_id)

        return items

    def _draw_speed_lines(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
    ) -> List[int]:
        """Draw speed/motion lines behind the blob."""
        items = []

        line_color = "#E0E0E0"
        for i in range(3):
            offset_y = (i - 1) * 12 * scale
            offset_x = -40 * scale - (phase * 20) % 30
            length = 15 + (i * 5)

            line_id = canvas.create_line(
                x + offset_x, y + offset_y,
                x + offset_x - length * scale, y + offset_y,
                fill=line_color,
                width=2,
                capstyle=tk.ROUND,
            )
            items.append(line_id)

        return items

    def _draw_cloud_puffs(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
        colors: BlobColors,
    ) -> List[int]:
        """Draw fluffy cloud-like puffs around the blob."""
        items = []

        puff_color = lighten_color(colors.primary, 0.3)
        num_puffs = 5
        radius = 35 * scale

        for i in range(num_puffs):
            angle = (i / num_puffs) * 2 * math.pi + phase * 0.5
            puff_x = x + math.cos(angle) * radius
            puff_y = y + math.sin(angle) * radius * 0.7
            puff_size = (8 + math.sin(phase * 2 + i) * 3) * scale

            puff_id = canvas.create_oval(
                puff_x - puff_size, puff_y - puff_size,
                puff_x + puff_size, puff_y + puff_size,
                fill=puff_color,
                outline="",
            )
            items.append(puff_id)

        return items

    def _draw_fluffy_edges(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
        colors: BlobColors,
    ) -> List[int]:
        """Draw fluffy/fuzzy edges around the blob."""
        items = []

        fluff_color = lighten_color(colors.primary, 0.2)
        num_fluffs = 8
        radius = 32 * scale

        for i in range(num_fluffs):
            angle = (i / num_fluffs) * 2 * math.pi
            wobble = math.sin(phase * 3 + i * 0.5) * 2
            fluff_x = x + math.cos(angle) * (radius + wobble)
            fluff_y = y + math.sin(angle) * (radius * 0.8 + wobble)
            fluff_size = (5 + math.sin(phase * 2 + i) * 2) * scale

            fluff_id = canvas.create_oval(
                fluff_x - fluff_size, fluff_y - fluff_size,
                fluff_x + fluff_size, fluff_y + fluff_size,
                fill=fluff_color,
                outline="",
            )
            items.append(fluff_id)

        return items

    def _draw_lightning_marks(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        colors: BlobColors,
    ) -> List[int]:
        """Draw lightning bolt marks on the body."""
        items = []

        mark_color = darken_color(colors.primary, 0.7)

        # Left lightning mark
        left_points = [
            x - 15 * scale, y - 5 * scale,
            x - 10 * scale, y,
            x - 18 * scale, y + 5 * scale,
            x - 12 * scale, y + 10 * scale,
        ]
        left_id = canvas.create_line(
            left_points,
            fill=mark_color,
            width=2,
        )
        items.append(left_id)

        # Right lightning mark
        right_points = [
            x + 15 * scale, y - 5 * scale,
            x + 10 * scale, y,
            x + 18 * scale, y + 5 * scale,
            x + 12 * scale, y + 10 * scale,
        ]
        right_id = canvas.create_line(
            right_points,
            fill=mark_color,
            width=2,
        )
        items.append(right_id)

        return items

    def _draw_star_particles(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
    ) -> List[int]:
        """Draw floating star particles around the blob."""
        items = []

        star_color = Colors.SOFT_YELLOW
        num_stars = 4

        for i in range(num_stars):
            # Orbit around the blob
            angle = (i / num_stars) * 2 * math.pi + phase
            radius = 45 * scale
            star_x = x + math.cos(angle) * radius
            star_y = y + math.sin(angle) * radius * 0.6 - 10 * scale

            # Fade in/out based on phase
            if (phase + i * 0.5) % 2 < 1.5:
                star_id = canvas.create_text(
                    star_x, star_y,
                    text="*",
                    font=("Arial", int(8 * scale)),
                    fill=star_color,
                )
                items.append(star_id)

        return items

    def _draw_floating_particles(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        scale: float,
        phase: float,
        colors: BlobColors,
    ) -> List[int]:
        """Draw ethereal floating particles."""
        items = []

        particle_color = lighten_color(colors.secondary, 0.3)
        num_particles = 6

        for i in range(num_particles):
            # Float upward and fade
            offset_phase = phase + i * 0.4
            float_y = (offset_phase * 15) % 50
            fade = 1.0 - (float_y / 50)

            if fade > 0.2:
                p_x = x + math.sin(offset_phase * 2 + i) * 30 * scale
                p_y = y - 20 * scale - float_y * scale
                p_size = (3 + fade * 2) * scale

                p_id = canvas.create_oval(
                    p_x - p_size, p_y - p_size,
                    p_x + p_size, p_y + p_size,
                    fill=particle_color,
                    outline="",
                )
                items.append(p_id)

        return items

    def _draw_face(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        appearance: FormAppearance,
        animation: AnimationParams,
        eye_params: Optional[EyeParams],
        mouth_params: Optional[MouthParams],
        show_blush: bool,
        show_sweat: bool,
    ) -> List[int]:
        """Draw the face (eyes, mouth, extras)."""
        items = []

        # Calculate face dimensions
        width, height = self.blob_sprite.apply_squash_stretch(
            animation.squash, animation.stretch
        )
        width *= animation.scale
        height *= animation.scale

        face_x = x + animation.offset_x
        face_y = y + animation.offset_y

        # Apply form-specific eye size
        eye_params = eye_params or EyeParams()
        eye_params.size_multiplier *= appearance.eye_size_mult

        # Apply expression tendencies
        if "half_lidded_default" in appearance.special_features:
            if eye_params.emotion == EyeEmotion.NORMAL:
                eye_params.emotion = EyeEmotion.SLEEPY
                eye_params.openness = 0.6

        # Draw eyes
        items.extend(self.expression_renderer.draw_eyes(
            canvas, face_x, face_y, width, height, eye_params
        ))

        # Draw mouth
        mouth_params = mouth_params or MouthParams()
        items.extend(self.expression_renderer.draw_mouth(
            canvas, face_x, face_y, width, height, mouth_params
        ))

        # Draw blush if applicable
        if show_blush or "blush_default" in appearance.special_features or "rosy_cheeks" in appearance.special_features:
            items.extend(self.expression_renderer.draw_blush(
                canvas, face_x, face_y, width, height
            ))

        # Draw sweat drop if applicable
        if show_sweat:
            items.extend(self.expression_renderer.draw_sweat_drop(
                canvas, face_x, face_y, width, height
            ))

        return items

    def clear(self, canvas: tk.Canvas) -> None:
        """Clear all canvas items."""
        for item_id in self._canvas_items:
            canvas.delete(item_id)
        self._canvas_items.clear()


def get_stage_scale(stage: EvolutionStage) -> float:
    """
    Get the scale factor for an evolution stage.

    Args:
        stage: Evolution stage.

    Returns:
        Scale factor (0.0-1.0).
    """
    scales = {
        EvolutionStage.EGG: SpritesConfig.EGG_SCALE,
        EvolutionStage.BABY: SpritesConfig.BABY_SCALE,
        EvolutionStage.CHILD: SpritesConfig.CHILD_SCALE,
        EvolutionStage.TEEN: SpritesConfig.TEEN_SCALE,
        EvolutionStage.ADULT: SpritesConfig.ADULT_SCALE,
    }
    return scales.get(stage, 1.0)
