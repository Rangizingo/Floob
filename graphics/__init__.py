"""
Floob 2.0 Graphics Module.

Provides the complete sprite and rendering system for simple,
expressive blob sprites. This replaces the complex animal creatures
with soft, rounded blobs that express personality through animation.

Modules:
    sprites: Base blob sprite system with squash/stretch
    expressions: Eye and mouth expression system
    evolution_sprites: Evolution stage-specific appearances
    effects: Visual effects (glow, shadow, particles)
    renderer: Main renderer combining all systems

Design Philosophy:
- Simple shapes over complex details
- Expression through animation
- Soft pastel color palette
- Smooth deformations

Usage:
    from graphics import BlobRenderer, PetRenderState

    renderer = BlobRenderer()
    state = PetRenderState(form_id="bloblet", x=75, y=75)
    renderer.render(canvas, state)
"""

# Base sprite system
from graphics.sprites import (
    BlobSprite,
    EggSprite,
    BlobColors,
    AnimationParams,
    NubLimbs,
    draw_nub_limbs,
    darken_color,
    lighten_color,
    blend_colors,
)

# Expression system
from graphics.expressions import (
    ExpressionRenderer,
    EyeParams,
    MouthParams,
    EyeEmotion,
    MouthEmotion,
    get_expression_for_mood,
)

# Evolution stage sprites
from graphics.evolution_sprites import (
    EvolutionSpriteRenderer,
    EvolutionStage,
    FormAppearance,
    FORM_APPEARANCES,
    get_stage_scale,
)

# Visual effects
from graphics.effects import (
    draw_glow,
    draw_pulsing_glow,
    draw_shadow,
    draw_thought_bubble,
    draw_stat_icon,
    draw_stat_bar,
    draw_level_up_burst,
    draw_hearts,
    draw_zzz,
    draw_sparkles,
    draw_sweat_drops,
    draw_music_notes,
    draw_food_crumbs,
    StatType,
    EffectState,
    Effects,
)

# Main renderer
from graphics.renderer import (
    BlobRenderer,
    PetRenderState,
    RenderState,
    create_simple_render_state,
)

__all__ = [
    # Sprites
    "BlobSprite",
    "EggSprite",
    "BlobColors",
    "AnimationParams",
    "NubLimbs",
    "draw_nub_limbs",
    "darken_color",
    "lighten_color",
    "blend_colors",
    # Expressions
    "ExpressionRenderer",
    "EyeParams",
    "MouthParams",
    "EyeEmotion",
    "MouthEmotion",
    "get_expression_for_mood",
    # Evolution sprites
    "EvolutionSpriteRenderer",
    "EvolutionStage",
    "FormAppearance",
    "FORM_APPEARANCES",
    "get_stage_scale",
    # Effects
    "draw_glow",
    "draw_pulsing_glow",
    "draw_shadow",
    "draw_thought_bubble",
    "draw_stat_icon",
    "draw_stat_bar",
    "draw_level_up_burst",
    "draw_hearts",
    "draw_zzz",
    "draw_sparkles",
    "draw_sweat_drops",
    "draw_music_notes",
    "draw_food_crumbs",
    "StatType",
    "EffectState",
    "Effects",
    # Renderer
    "BlobRenderer",
    "PetRenderState",
    "RenderState",
    "create_simple_render_state",
]
