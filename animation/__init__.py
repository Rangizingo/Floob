"""
Animation Engine for Floob 2.0.

This module provides a rich, data-driven animation system with:
- Keyframe-based animations with smooth interpolation
- Multiple easing functions for natural motion
- Animation blending and transitions
- Particle effects system
- Complex animation sequences

Modules:
    engine: Core animation engine with keyframes and tweening
    states: Animation property and state definitions
    reactions: Reaction animations for user interactions
    sequences: Complex multi-frame animation sequences
    particles: Particle effects system
"""

from animation.engine import (
    AnimationEngine,
    Keyframe,
    Animation,
    EasingType,
    linear,
    ease_in,
    ease_out,
    ease_in_out,
    bounce,
    elastic,
)
from animation.states import (
    AnimationProperty,
    AnimationState,
    AnimationStateConfig,
    IDLE_ANIMATIONS,
    STATE_CONFIGS,
)
from animation.reactions import (
    ReactionType,
    REACTION_ANIMATIONS,
    get_reaction_animation,
)
from animation.sequences import (
    AnimationSequence,
    SequenceKeyframe,
    EATING_SEQUENCE,
    PLAYING_SEQUENCE,
    EVOLUTION_SEQUENCE,
    TANTRUM_SEQUENCE,
    CELEBRATION_SEQUENCE,
    SLEEPING_SEQUENCE,
    CLICK_REACTION_SEQUENCE,
    YAWN_SEQUENCE,
    BOUNCE_SEQUENCE,
    BREATHING_SEQUENCE,
    BLINK_SEQUENCE,
    get_sequence,
    create_eating_sequence,
    create_playing_sequence,
    create_evolution_sequence,
    create_tantrum_sequence,
    create_celebration_sequence,
    create_sleeping_sequence,
    create_click_reaction_sequence,
    create_yawn_sequence,
    create_bounce_sequence,
    create_breathing_sequence,
    create_blink_sequence,
)
from animation.particles import (
    Particle,
    ParticleType,
    ParticleEmitter,
    ParticleSystem,
    ParticleConfig,
    PARTICLE_CONFIGS,
    spawn_hearts,
    spawn_sparkles,
    spawn_stars,
    spawn_confetti,
    spawn_zzz,
    spawn_sweat,
    spawn_crumbs,
    spawn_dust,
    spawn_music_notes,
)

__all__ = [
    # Engine
    "AnimationEngine",
    "Keyframe",
    "Animation",
    "EasingType",
    "linear",
    "ease_in",
    "ease_out",
    "ease_in_out",
    "bounce",
    "elastic",
    # States
    "AnimationProperty",
    "AnimationState",
    "AnimationStateConfig",
    "IDLE_ANIMATIONS",
    "STATE_CONFIGS",
    # Reactions
    "ReactionType",
    "REACTION_ANIMATIONS",
    "get_reaction_animation",
    # Sequences
    "AnimationSequence",
    "SequenceKeyframe",
    "EATING_SEQUENCE",
    "PLAYING_SEQUENCE",
    "EVOLUTION_SEQUENCE",
    "TANTRUM_SEQUENCE",
    "CELEBRATION_SEQUENCE",
    "SLEEPING_SEQUENCE",
    "CLICK_REACTION_SEQUENCE",
    "YAWN_SEQUENCE",
    "BOUNCE_SEQUENCE",
    "BREATHING_SEQUENCE",
    "BLINK_SEQUENCE",
    "get_sequence",
    "create_eating_sequence",
    "create_playing_sequence",
    "create_evolution_sequence",
    "create_tantrum_sequence",
    "create_celebration_sequence",
    "create_sleeping_sequence",
    "create_click_reaction_sequence",
    "create_yawn_sequence",
    "create_bounce_sequence",
    "create_breathing_sequence",
    "create_blink_sequence",
    # Particles
    "Particle",
    "ParticleType",
    "ParticleEmitter",
    "ParticleSystem",
    "ParticleConfig",
    "PARTICLE_CONFIGS",
    "spawn_hearts",
    "spawn_sparkles",
    "spawn_stars",
    "spawn_confetti",
    "spawn_zzz",
    "spawn_sweat",
    "spawn_crumbs",
    "spawn_dust",
    "spawn_music_notes",
]
