"""
Floob 2.0 Main Renderer.

The BlobRenderer class combines all graphics systems to render
complete pet sprites with expressions, effects, and animations.

This is the main interface for drawing pets - it handles:
- Getting current form appearance from evolution stage
- Applying animation transforms (squash, stretch, position)
- Drawing expressions based on state
- Rendering particle effects
- Drawing UI elements (thought bubbles, stat icons)
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any

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
    get_expression_for_mood,
)
from graphics.evolution_sprites import (
    EvolutionSpriteRenderer,
    EvolutionStage,
    FormAppearance,
    FORM_APPEARANCES,
    get_stage_scale,
)
from graphics.effects import (
    draw_glow,
    draw_pulsing_glow,
    draw_shadow,
    draw_thought_bubble,
    draw_stat_icon,
    draw_hearts,
    draw_zzz,
    draw_sparkles,
    draw_sweat_drops,
    draw_music_notes,
    draw_food_crumbs,
    draw_level_up_burst,
    StatType,
    EffectState,
)

# Import config
try:
    from core.config import Colors, Sprites as SpritesConfig
except ImportError:
    class Colors:
        SOFT_PINK = "#FFD6E0"
        SOFT_BLUE = "#A2D2FF"
        SOFT_PURPLE = "#CDB4DB"
        SOFT_YELLOW = "#FFF3B0"
        SOFT_GRAY = "#E8E8E8"
        WHITE = "#FFFFFF"

    class SpritesConfig:
        SHADOW_OPACITY = 0.2
        SHADOW_OFFSET_Y = 0.1
        SHADOW_SCALE_X = 0.8


class RenderState(Enum):
    """Current rendering state/mode."""
    IDLE = auto()
    WALKING = auto()
    EATING = auto()
    PLAYING = auto()
    SLEEPING = auto()
    HAPPY = auto()
    SAD = auto()
    HUNGRY = auto()
    TIRED = auto()
    TRICK = auto()
    LEVEL_UP = auto()
    EVOLVING = auto()


@dataclass
class PetRenderState:
    """
    Complete state needed to render a pet.

    This consolidates all the information needed to draw the pet
    in its current state, including form, animation, and effects.
    """
    # Identity
    form_id: str = "bloblet"
    name: str = "Floob"

    # Position
    x: float = 75.0
    y: float = 75.0

    # Animation state
    render_state: RenderState = RenderState.IDLE
    animation_phase: float = 0.0
    squash: float = 0.0
    stretch: float = 0.0
    rotation: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    direction: int = 1  # 1 = right, -1 = left

    # Expression
    eye_emotion: EyeEmotion = EyeEmotion.NORMAL
    eye_openness: float = 1.0
    look_direction: Tuple[float, float] = (0.0, 0.0)
    mouth_emotion: MouthEmotion = MouthEmotion.NEUTRAL
    mouth_openness: float = 0.0
    show_blush: bool = False
    show_sweat: bool = False

    # Stats (for indicators)
    hunger: float = 80.0
    happiness: float = 80.0
    energy: float = 80.0

    # Mood
    mood: str = "content"  # ecstatic, happy, content, neutral, sad, miserable
    is_hungry: bool = False
    is_tired: bool = False

    # Thought bubble
    thought_text: Optional[str] = None
    thought_icon: Optional[str] = None
    thought_opacity: float = 1.0

    # Special effects
    show_hearts: bool = False
    show_zzz: bool = False
    show_sparkles: bool = False
    show_music: bool = False
    level_up_progress: float = 0.0  # 0.0 = not leveling, 1.0 = complete


class BlobRenderer:
    """
    Main renderer for blob pet sprites.

    Combines all graphics subsystems to render complete pets
    with animations, expressions, and effects.

    Usage:
        renderer = BlobRenderer()
        state = PetRenderState(form_id="bouncy", x=100, y=100)
        renderer.render(canvas, state)
    """

    def __init__(self) -> None:
        """Initialize the blob renderer."""
        self.evolution_renderer = EvolutionSpriteRenderer()
        self._canvas_items: List[int] = []
        self._effect_items: List[int] = []

        # Animation helpers
        self._bounce_phase: float = 0.0
        self._blink_timer: float = 0.0
        self._is_blinking: bool = False

    def render(
        self,
        canvas: tk.Canvas,
        state: PetRenderState,
    ) -> None:
        """
        Render the complete pet sprite.

        Args:
            canvas: Tkinter canvas to draw on.
            state: Current pet render state.
        """
        self.clear(canvas)

        items = []

        # 1. Draw shadow
        shadow_items = self._draw_shadow(canvas, state)
        items.extend(shadow_items)

        # 2. Draw special background effects
        bg_effect_items = self._draw_background_effects(canvas, state)
        items.extend(bg_effect_items)

        # 3. Draw main pet sprite
        pet_items = self._draw_pet(canvas, state)
        items.extend(pet_items)

        # 4. Draw foreground effects (particles, etc.)
        fg_effect_items = self._draw_foreground_effects(canvas, state)
        items.extend(fg_effect_items)

        # 5. Draw thought bubble if present
        if state.thought_text:
            bubble_items = self._draw_thought_bubble(canvas, state)
            items.extend(bubble_items)

        self._canvas_items = items

    def render_with_animation(
        self,
        canvas: tk.Canvas,
        pet: Any,  # Pet object with stats and state
        animation_state: Dict[str, Any],
    ) -> None:
        """
        Render pet using animation state dictionary.

        This is a convenience method that builds PetRenderState
        from a pet object and animation state dict.

        Args:
            canvas: Tkinter canvas to draw on.
            pet: Pet object with stats, form_id, mood, etc.
            animation_state: Animation state from animation engine.
        """
        # Build render state from pet and animation
        state = self._build_render_state(pet, animation_state)
        self.render(canvas, state)

    def _build_render_state(
        self,
        pet: Any,
        animation_state: Dict[str, Any],
    ) -> PetRenderState:
        """
        Build PetRenderState from pet object and animation state.

        Args:
            pet: Pet object.
            animation_state: Animation state dictionary.

        Returns:
            PetRenderState for rendering.
        """
        # Get form ID from pet (handle both old and new pet formats)
        form_id = getattr(pet, "form_id", None)
        if form_id is None:
            # Fall back to creature_type or default
            form_id = getattr(pet, "creature_type", "bloblet")

        # Get mood
        mood = "content"
        if hasattr(pet, "get_mood"):
            mood_enum = pet.get_mood()
            mood = mood_enum.name.lower() if hasattr(mood_enum, "name") else str(mood_enum).lower()

        # Get stats
        stats = getattr(pet, "stats", None)
        hunger = getattr(stats, "hunger", 80.0) if stats else 80.0
        happiness = getattr(stats, "happiness", 80.0) if stats else 80.0
        energy = getattr(stats, "energy", 80.0) if stats else 80.0

        # Determine render state from pet state
        pet_state = getattr(pet, "state", None)
        render_state = RenderState.IDLE
        if pet_state:
            state_name = pet_state.name if hasattr(pet_state, "name") else str(pet_state)
            render_state = self._pet_state_to_render_state(state_name)

        # Get expression based on mood and state
        eye_params, mouth_params = get_expression_for_mood(
            mood,
            is_hungry=hunger < 30,
            is_tired=energy < 30,
        )

        # Override expressions for specific states
        if render_state == RenderState.SLEEPING:
            eye_params.emotion = EyeEmotion.BLINK
            eye_params.openness = 0.0
            mouth_params.emotion = MouthEmotion.NEUTRAL

        elif render_state == RenderState.EATING:
            mouth_params.emotion = MouthEmotion.EATING
            mouth_params.openness = animation_state.get("phase", 0.0)

        elif render_state == RenderState.HAPPY:
            eye_params.emotion = EyeEmotion.HAPPY
            mouth_params.emotion = MouthEmotion.HAPPY

        elif render_state == RenderState.PLAYING:
            eye_params.emotion = EyeEmotion.SPARKLE
            mouth_params.emotion = MouthEmotion.HAPPY

        # Get animation parameters
        bounce = animation_state.get("bounce", 0.0)
        phase = animation_state.get("phase", 0.0)

        # Calculate squash/stretch from state
        squash = 0.0
        stretch = 0.0
        if render_state == RenderState.WALKING:
            # Walking bounce creates squash/stretch
            walk_phase = animation_state.get("phase", 0.0)
            squash = abs(math.sin(walk_phase * math.pi * 2)) * 0.15
        elif render_state == RenderState.HAPPY:
            # Happy bouncing
            squash = abs(math.sin(phase * 3)) * 0.1

        # Get thought bubble
        thought = getattr(pet, "thought_bubble", None)
        thought_text = None
        thought_icon = None
        thought_opacity = 1.0
        if thought:
            thought_text = getattr(thought, "text", None)
            thought_icon = getattr(thought, "icon", None)
            if hasattr(thought, "get_opacity"):
                thought_opacity = thought.get_opacity()

        return PetRenderState(
            form_id=form_id,
            name=getattr(pet, "name", "Floob"),
            x=animation_state.get("new_x", 75),
            y=animation_state.get("new_y", 75),
            render_state=render_state,
            animation_phase=phase,
            squash=squash,
            stretch=stretch,
            offset_y=-bounce,
            direction=animation_state.get("direction", 1),
            eye_emotion=eye_params.emotion,
            eye_openness=eye_params.openness,
            mouth_emotion=mouth_params.emotion,
            mouth_openness=mouth_params.openness,
            show_blush=(mood == "ecstatic" or mood == "happy"),
            show_sweat=(hunger < 30 or energy < 30),
            hunger=hunger,
            happiness=happiness,
            energy=energy,
            mood=mood,
            is_hungry=hunger < 30,
            is_tired=energy < 30,
            thought_text=thought_text,
            thought_icon=thought_icon,
            thought_opacity=thought_opacity,
            show_hearts=(render_state == RenderState.HAPPY),
            show_zzz=(render_state == RenderState.SLEEPING),
            show_sparkles=(render_state == RenderState.PLAYING or render_state == RenderState.TRICK),
        )

    def _pet_state_to_render_state(self, state_name: str) -> RenderState:
        """Convert pet state name to render state."""
        state_map = {
            "IDLE": RenderState.IDLE,
            "WALKING": RenderState.WALKING,
            "EATING": RenderState.EATING,
            "PLAYING": RenderState.PLAYING,
            "SLEEPING": RenderState.SLEEPING,
            "HAPPY": RenderState.HAPPY,
            "TRICK": RenderState.TRICK,
        }
        return state_map.get(state_name.upper(), RenderState.IDLE)

    def _draw_shadow(
        self,
        canvas: tk.Canvas,
        state: PetRenderState,
    ) -> List[int]:
        """Draw the shadow beneath the pet."""
        appearance = self.evolution_renderer.get_form_appearance(state.form_id)

        # Shadow size based on form scale
        shadow_width = 40 * appearance.scale
        shadow_height = shadow_width * 0.3

        # Shadow position (below pet, slightly compressed when bouncing)
        shadow_y = state.y + 50 * appearance.scale - state.offset_y * 0.5
        shadow_x = state.x + state.offset_x

        # Shadow shrinks when pet is higher (bouncing)
        bounce_factor = 1.0 - abs(state.offset_y) / 50 * 0.3

        return draw_shadow(
            canvas, shadow_x, shadow_y,
            shadow_width * bounce_factor * SpritesConfig.SHADOW_SCALE_X,
            shadow_height,
            SpritesConfig.SHADOW_OPACITY,
        )

    def _draw_background_effects(
        self,
        canvas: tk.Canvas,
        state: PetRenderState,
    ) -> List[int]:
        """Draw effects that appear behind the pet."""
        items = []
        appearance = self.evolution_renderer.get_form_appearance(state.form_id)

        x = state.x + state.offset_x
        y = state.y + state.offset_y

        # Level up glow
        if state.level_up_progress > 0:
            radius = 30 + state.level_up_progress * 50
            items.extend(draw_level_up_burst(
                canvas, x, y, radius, state.animation_phase,
                Colors.SOFT_YELLOW
            ))

        return items

    def _draw_pet(
        self,
        canvas: tk.Canvas,
        state: PetRenderState,
    ) -> List[int]:
        """Draw the main pet sprite."""
        # Build animation params
        animation = AnimationParams(
            squash=state.squash,
            stretch=state.stretch,
            rotation=state.rotation,
            offset_x=state.offset_x,
            offset_y=state.offset_y,
            wobble_phase=state.animation_phase,
        )

        # Build expression params
        eye_params = EyeParams(
            emotion=state.eye_emotion,
            openness=state.eye_openness,
            direction=state.look_direction,
        )

        mouth_params = MouthParams(
            emotion=state.mouth_emotion,
            openness=state.mouth_openness,
        )

        return self.evolution_renderer.draw_form(
            canvas,
            state.x, state.y,
            state.form_id,
            animation=animation,
            eye_params=eye_params,
            mouth_params=mouth_params,
            show_blush=state.show_blush,
            show_sweat=state.show_sweat,
            phase=state.animation_phase,
        )

    def _draw_foreground_effects(
        self,
        canvas: tk.Canvas,
        state: PetRenderState,
    ) -> List[int]:
        """Draw effects that appear in front of the pet."""
        items = []

        x = state.x + state.offset_x
        y = state.y + state.offset_y

        # Hearts (happy state)
        if state.show_hearts:
            items.extend(draw_hearts(canvas, x, y - 40, 3, 50.0, state.animation_phase))

        # ZZZ (sleeping)
        if state.show_zzz:
            items.extend(draw_zzz(canvas, x + 35, y - 30, state.animation_phase))

        # Sparkles (playing/trick)
        if state.show_sparkles:
            items.extend(draw_sparkles(canvas, x, y, 5, 55.0, state.animation_phase))

        # Music notes (playing)
        if state.show_music:
            items.extend(draw_music_notes(canvas, x, y - 30, 3, state.animation_phase))

        # Sweat drops (hungry/tired)
        if state.show_sweat and (state.is_hungry or state.is_tired):
            items.extend(draw_sweat_drops(canvas, x + 25, y - 25, 2, state.animation_phase))

        # Food crumbs (eating)
        if state.render_state == RenderState.EATING:
            items.extend(draw_food_crumbs(canvas, x, y + 20, 4, state.animation_phase))

        return items

    def _draw_thought_bubble(
        self,
        canvas: tk.Canvas,
        state: PetRenderState,
    ) -> List[int]:
        """Draw the thought bubble."""
        bubble_x = state.x + state.offset_x + 25
        bubble_y = state.y + state.offset_y - 60

        return draw_thought_bubble(
            canvas,
            bubble_x, bubble_y,
            state.thought_text,
            state.thought_icon,
            width=80.0,
            height=36.0,
            opacity=state.thought_opacity,
        )

    def clear(self, canvas: tk.Canvas) -> None:
        """Clear all rendered items from canvas."""
        for item_id in self._canvas_items:
            canvas.delete(item_id)
        self._canvas_items.clear()

        for item_id in self._effect_items:
            canvas.delete(item_id)
        self._effect_items.clear()

    def update_idle_animation(self, delta_time: float) -> Dict[str, float]:
        """
        Update idle animation state.

        Returns animation values for breathing and blinking.

        Args:
            delta_time: Time elapsed since last update.

        Returns:
            Dictionary with animation values.
        """
        # Breathing bounce
        self._bounce_phase += delta_time * 2.5
        bounce = math.sin(self._bounce_phase) * 2

        # Blinking
        self._blink_timer += delta_time
        blink = False

        if not self._is_blinking:
            # Random blink interval (2-5 seconds)
            if self._blink_timer > 2.0 + (self._bounce_phase % 3.0):
                self._is_blinking = True
                self._blink_timer = 0
        else:
            # Blink duration (0.15 seconds)
            if self._blink_timer > 0.15:
                self._is_blinking = False
                self._blink_timer = 0

        return {
            "bounce": bounce,
            "blink": self._is_blinking,
            "phase": self._bounce_phase,
        }


def create_simple_render_state(
    form_id: str = "bloblet",
    x: float = 75.0,
    y: float = 75.0,
    mood: str = "content",
    state: str = "idle",
    phase: float = 0.0,
) -> PetRenderState:
    """
    Create a simple render state for testing/preview.

    Args:
        form_id: Evolution form identifier.
        x: X position.
        y: Y position.
        mood: Mood string.
        state: State string (idle, walking, eating, etc.).
        phase: Animation phase.

    Returns:
        PetRenderState ready for rendering.
    """
    # Get expression for mood
    eye_params, mouth_params = get_expression_for_mood(mood)

    # Convert state string to enum
    state_map = {
        "idle": RenderState.IDLE,
        "walking": RenderState.WALKING,
        "eating": RenderState.EATING,
        "playing": RenderState.PLAYING,
        "sleeping": RenderState.SLEEPING,
        "happy": RenderState.HAPPY,
        "trick": RenderState.TRICK,
    }
    render_state = state_map.get(state.lower(), RenderState.IDLE)

    # Adjust for state
    if render_state == RenderState.SLEEPING:
        eye_params.emotion = EyeEmotion.BLINK
        eye_params.openness = 0.0

    return PetRenderState(
        form_id=form_id,
        x=x,
        y=y,
        render_state=render_state,
        animation_phase=phase,
        eye_emotion=eye_params.emotion,
        eye_openness=eye_params.openness,
        mouth_emotion=mouth_params.emotion,
        mood=mood,
        show_hearts=(render_state == RenderState.HAPPY),
        show_zzz=(render_state == RenderState.SLEEPING),
        show_sparkles=(render_state == RenderState.PLAYING),
    )
