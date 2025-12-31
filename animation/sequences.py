"""
Complex Animation Sequences for Floob 2.0.

Defines multi-frame animation sequences that tell mini-stories:
- Eating Sequence (8 keyframes over 2.5 seconds)
- Playing Sequence (12 keyframes over 3 seconds)
- Evolution Sequence (dramatic 4-second transformation)

Sequences are data-driven collections of keyframes that can be
played through the animation engine.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any

from animation.engine import (
    Animation,
    AnimationSet,
    Keyframe,
    EasingType,
)


@dataclass
class SequenceKeyframe:
    """
    A keyframe in an animation sequence with multiple properties.

    Represents a moment in time during a sequence where multiple
    animation properties are defined together for storytelling.

    Attributes:
        time: Time in seconds from sequence start
        description: Human-readable description of this moment
        properties: Dict of property names to values at this keyframe
        easing: Default easing for all properties at this keyframe
        trigger_particles: Particle types to spawn at this keyframe
        trigger_sound: Sound effect to play at this keyframe
    """
    time: float
    description: str = ""
    properties: dict[str, float] = field(default_factory=dict)
    easing: EasingType = EasingType.EASE_IN_OUT
    trigger_particles: list[str] = field(default_factory=list)
    trigger_sound: Optional[str] = None


@dataclass
class AnimationSequence:
    """
    A complete multi-keyframe animation sequence.

    Sequences are composed of SequenceKeyframes that define
    multiple properties at once, making it easy to create
    complex, expressive animations.

    Attributes:
        name: Name of the sequence
        keyframes: List of sequence keyframes in time order
        loop: Whether the sequence loops
        on_complete: Callback when sequence finishes
    """
    name: str
    keyframes: list[SequenceKeyframe] = field(default_factory=list)
    loop: bool = False
    priority: int = 20

    @property
    def duration(self) -> float:
        """Get total sequence duration."""
        if not self.keyframes:
            return 0.0
        return max(kf.time for kf in self.keyframes)

    def to_animation_set(self) -> AnimationSet:
        """
        Convert the sequence to an AnimationSet for the engine.

        Returns:
            AnimationSet containing all property animations
        """
        anim_set = AnimationSet(name=self.name, priority=self.priority)

        # Collect all unique property names
        all_properties: set[str] = set()
        for seq_kf in self.keyframes:
            all_properties.update(seq_kf.properties.keys())

        # Create an Animation for each property
        for prop_name in all_properties:
            keyframe_list: list[Keyframe] = []

            for seq_kf in self.keyframes:
                if prop_name in seq_kf.properties:
                    keyframe_list.append(Keyframe(
                        time=seq_kf.time,
                        value=seq_kf.properties[prop_name],
                        easing=seq_kf.easing,
                    ))

            if keyframe_list:
                anim_set.add_animation(Animation(
                    property_name=prop_name,
                    keyframes=keyframe_list,
                    loop=self.loop,
                ))

        return anim_set

    def get_particle_triggers(self) -> list[tuple[float, list[str]]]:
        """
        Get list of (time, particle_types) for particle spawning.

        Returns:
            List of tuples with time and particle types to spawn
        """
        triggers = []
        for kf in self.keyframes:
            if kf.trigger_particles:
                triggers.append((kf.time, kf.trigger_particles))
        return triggers


# ============================================================================
# EATING SEQUENCE
# ============================================================================

def create_eating_sequence() -> AnimationSequence:
    """
    Create the eating animation sequence.

    8 keyframes over 2.5 seconds:
    1. t=0.0: Notice - eyes widen
    2. t=0.3: Lean forward - position_y -= 5
    3. t=0.5: Mouth open wide
    4. t=0.7: Chomp 1 - squash
    5. t=0.9: Chomp 2 - squash
    6. t=1.1: Chomp 3 - squash
    7. t=1.5: Swallow - stretch vertical briefly
    8. t=2.0: Satisfied - happy eyes, small wiggle
    9. t=2.5: Return to normal

    Returns:
        AnimationSequence for eating
    """
    seq = AnimationSequence(name="eating", priority=25)

    # 1. Notice - eyes widen
    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Notice food - eyes widen",
        properties={
            "eye_openness": 1.3,
            "mouth_openness": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "position_y": 0.0,
            "rotation": 0.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 2. Lean forward
    seq.keyframes.append(SequenceKeyframe(
        time=0.3,
        description="Lean forward with anticipation",
        properties={
            "eye_openness": 1.2,
            "mouth_openness": 0.2,
            "position_y": -5.0,
            "rotation": 3.0,
            "scale_y": 1.02,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 3. Mouth open wide
    seq.keyframes.append(SequenceKeyframe(
        time=0.5,
        description="Mouth opens wide",
        properties={
            "mouth_openness": 1.0,
            "eye_openness": 0.9,
            "position_y": -3.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 4. Chomp 1 - squash
    seq.keyframes.append(SequenceKeyframe(
        time=0.7,
        description="Chomp 1 - bite down",
        properties={
            "mouth_openness": 0.1,
            "scale_y": 0.9,
            "scale_x": 1.1,
            "position_y": 0.0,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["crumb"],
    ))

    # 5. Chomp 2 - open
    seq.keyframes.append(SequenceKeyframe(
        time=0.85,
        description="Chomp 2 - open",
        properties={
            "mouth_openness": 0.7,
            "scale_y": 1.0,
            "scale_x": 1.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 6. Chomp 2 - close
    seq.keyframes.append(SequenceKeyframe(
        time=1.0,
        description="Chomp 2 - bite",
        properties={
            "mouth_openness": 0.1,
            "scale_y": 0.92,
            "scale_x": 1.08,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["crumb"],
    ))

    # 7. Chomp 3 - final bite
    seq.keyframes.append(SequenceKeyframe(
        time=1.2,
        description="Chomp 3 - final bite",
        properties={
            "mouth_openness": 0.0,
            "scale_y": 0.88,
            "scale_x": 1.12,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["crumb"],
    ))

    # 8. Swallow - stretch
    seq.keyframes.append(SequenceKeyframe(
        time=1.5,
        description="Swallow - stretch vertical",
        properties={
            "mouth_openness": 0.0,
            "scale_y": 1.1,
            "scale_x": 0.95,
            "eye_openness": 0.8,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 9. Satisfied
    seq.keyframes.append(SequenceKeyframe(
        time=2.0,
        description="Satisfied - happy expression",
        properties={
            "mouth_openness": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "eye_openness": 0.7,  # Happy squint
            "rotation": 3.0,
            "blush": 0.5,
        },
        easing=EasingType.EASE_IN_OUT,
        trigger_particles=["heart"],
    ))

    # 10. Return to normal
    seq.keyframes.append(SequenceKeyframe(
        time=2.5,
        description="Return to normal",
        properties={
            "mouth_openness": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "eye_openness": 1.0,
            "rotation": 0.0,
            "blush": 0.0,
            "position_y": 0.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    return seq


# ============================================================================
# PLAYING SEQUENCE
# ============================================================================

def create_playing_sequence() -> AnimationSequence:
    """
    Create the playing animation sequence.

    12 keyframes over 3 seconds:
    1. Alert - see toy
    2. Crouch - anticipation
    3. Pounce forward
    4. Tumble/roll
    5. Grab toy
    6. Shake toy
    7. Toss toy
    8. Chase toy
    9. Catch toy
    10. Victory wiggle
    11. Tired pant
    12. Rest pose

    Returns:
        AnimationSequence for playing
    """
    seq = AnimationSequence(name="playing", priority=25)

    # 1. Alert - see toy
    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Alert - see toy",
        properties={
            "eye_openness": 1.3,
            "scale_y": 1.05,
            "scale_x": 0.98,
            "position_x": 0.0,
            "position_y": 0.0,
            "rotation": 0.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 2. Crouch - anticipation
    seq.keyframes.append(SequenceKeyframe(
        time=0.25,
        description="Crouch - anticipation",
        properties={
            "eye_openness": 1.2,
            "scale_y": 0.85,
            "scale_x": 1.1,
            "position_y": 5.0,
            "rotation": -5.0,
        },
        easing=EasingType.EASE_IN,
    ))

    # 3. Pounce forward
    seq.keyframes.append(SequenceKeyframe(
        time=0.45,
        description="Pounce forward",
        properties={
            "scale_y": 1.2,
            "scale_x": 0.85,
            "position_y": -15.0,
            "position_x": 20.0,
            "rotation": 15.0,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["sparkle"],
    ))

    # 4. Land and tumble
    seq.keyframes.append(SequenceKeyframe(
        time=0.7,
        description="Land and tumble",
        properties={
            "scale_y": 0.9,
            "scale_x": 1.1,
            "position_y": 2.0,
            "position_x": 30.0,
            "rotation": 45.0,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["dust"],
    ))

    # 5. Grab toy
    seq.keyframes.append(SequenceKeyframe(
        time=0.95,
        description="Grab toy",
        properties={
            "scale_y": 1.0,
            "scale_x": 1.0,
            "position_y": 0.0,
            "position_x": 25.0,
            "rotation": 0.0,
            "mouth_openness": 0.3,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 6. Shake toy left
    seq.keyframes.append(SequenceKeyframe(
        time=1.15,
        description="Shake toy left",
        properties={
            "rotation": -20.0,
            "position_x": 20.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 7. Shake toy right
    seq.keyframes.append(SequenceKeyframe(
        time=1.35,
        description="Shake toy right",
        properties={
            "rotation": 20.0,
            "position_x": 30.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 8. Toss toy
    seq.keyframes.append(SequenceKeyframe(
        time=1.55,
        description="Toss toy",
        properties={
            "rotation": -10.0,
            "position_x": 15.0,
            "position_y": -5.0,
            "mouth_openness": 0.0,
            "scale_y": 1.1,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["star"],
    ))

    # 9. Chase toy
    seq.keyframes.append(SequenceKeyframe(
        time=1.85,
        description="Chase toy",
        properties={
            "position_x": -15.0,
            "position_y": 0.0,
            "rotation": -15.0,
            "scale_y": 0.95,
            "scale_x": 1.05,
            "limb_phase": 0.5,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 10. Catch toy
    seq.keyframes.append(SequenceKeyframe(
        time=2.15,
        description="Catch toy",
        properties={
            "position_x": -20.0,
            "rotation": 5.0,
            "scale_y": 0.9,
            "scale_x": 1.1,
            "mouth_openness": 0.5,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["sparkle"],
    ))

    # 11. Victory wiggle
    seq.keyframes.append(SequenceKeyframe(
        time=2.45,
        description="Victory wiggle",
        properties={
            "position_x": -10.0,
            "position_y": -8.0,
            "rotation": 10.0,
            "scale_y": 1.05,
            "scale_x": 1.0,
            "mouth_openness": 0.0,
            "eye_openness": 0.8,  # Happy squint
            "blush": 0.5,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["heart"],
    ))

    # 12. Tired pant
    seq.keyframes.append(SequenceKeyframe(
        time=2.75,
        description="Tired pant",
        properties={
            "position_x": 0.0,
            "position_y": 2.0,
            "rotation": 0.0,
            "scale_y": 0.98,
            "eye_openness": 0.9,
            "mouth_openness": 0.3,
            "blush": 0.3,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 13. Rest pose
    seq.keyframes.append(SequenceKeyframe(
        time=3.0,
        description="Rest pose",
        properties={
            "position_x": 0.0,
            "position_y": 0.0,
            "rotation": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "eye_openness": 1.0,
            "mouth_openness": 0.0,
            "blush": 0.0,
            "limb_phase": 0.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    return seq


# ============================================================================
# EVOLUTION SEQUENCE
# ============================================================================

def create_evolution_sequence() -> AnimationSequence:
    """
    Create the evolution animation sequence.

    Dramatic 4-second transformation:
    1. Glow start
    2. Shake intensify
    3. Flash white
    4. Transform
    5. Burst
    6. Reveal
    7. Celebrate

    Returns:
        AnimationSequence for evolution
    """
    seq = AnimationSequence(name="evolution", priority=50)

    # 1. Glow start
    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Glow start - power building",
        properties={
            "glow_intensity": 0.2,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "position_x": 0.0,
            "position_y": 0.0,
            "rotation": 0.0,
            "opacity": 1.0,
        },
        easing=EasingType.EASE_IN,
    ))

    # 2. Shake begins
    seq.keyframes.append(SequenceKeyframe(
        time=0.3,
        description="Shake begins",
        properties={
            "glow_intensity": 0.4,
            "position_x": 3.0,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["sparkle"],
    ))

    # 3. Shake intensifies
    seq.keyframes.append(SequenceKeyframe(
        time=0.5,
        description="Shake intensifies",
        properties={
            "glow_intensity": 0.6,
            "position_x": -4.0,
        },
        easing=EasingType.LINEAR,
    ))

    # 4. More shaking
    seq.keyframes.append(SequenceKeyframe(
        time=0.7,
        description="More shaking",
        properties={
            "glow_intensity": 0.7,
            "position_x": 5.0,
        },
        easing=EasingType.LINEAR,
    ))

    # 5. Peak shake
    seq.keyframes.append(SequenceKeyframe(
        time=0.9,
        description="Peak shake",
        properties={
            "glow_intensity": 0.85,
            "position_x": -6.0,
            "scale_y": 1.05,
        },
        easing=EasingType.LINEAR,
        trigger_particles=["sparkle", "star"],
    ))

    # 6. Flash white - transform begins
    seq.keyframes.append(SequenceKeyframe(
        time=1.1,
        description="Flash white - transform begins",
        properties={
            "glow_intensity": 1.0,
            "position_x": 0.0,
            "scale_y": 1.1,
            "scale_x": 1.1,
            "opacity": 0.8,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["star", "sparkle"],
    ))

    # 7. Compress before burst
    seq.keyframes.append(SequenceKeyframe(
        time=1.5,
        description="Compress before burst",
        properties={
            "glow_intensity": 1.0,
            "scale_y": 0.7,
            "scale_x": 0.7,
            "opacity": 0.5,
        },
        easing=EasingType.EASE_IN,
    ))

    # 8. BURST!
    seq.keyframes.append(SequenceKeyframe(
        time=1.7,
        description="BURST - transformation!",
        properties={
            "glow_intensity": 1.0,
            "scale_y": 1.5,
            "scale_x": 1.5,
            "opacity": 1.0,
            "position_y": -10.0,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["star", "confetti", "sparkle"],
    ))

    # 9. Reveal new form
    seq.keyframes.append(SequenceKeyframe(
        time=2.2,
        description="Reveal new form",
        properties={
            "glow_intensity": 0.6,
            "scale_y": 1.1,
            "scale_x": 1.1,
            "position_y": -5.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 10. Settle
    seq.keyframes.append(SequenceKeyframe(
        time=2.7,
        description="Settle",
        properties={
            "glow_intensity": 0.3,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "position_y": 0.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 11. Celebrate bounce 1
    seq.keyframes.append(SequenceKeyframe(
        time=3.0,
        description="Celebrate bounce 1",
        properties={
            "glow_intensity": 0.2,
            "position_y": -12.0,
            "rotation": 10.0,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["heart", "confetti"],
    ))

    # 12. Celebrate bounce 2
    seq.keyframes.append(SequenceKeyframe(
        time=3.3,
        description="Celebrate bounce 2",
        properties={
            "position_y": 0.0,
            "rotation": -8.0,
        },
        easing=EasingType.BOUNCE,
    ))

    # 13. Final pose
    seq.keyframes.append(SequenceKeyframe(
        time=4.0,
        description="Final pose - new form revealed",
        properties={
            "glow_intensity": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "position_y": 0.0,
            "position_x": 0.0,
            "rotation": 0.0,
            "opacity": 1.0,
            "eye_openness": 1.0,
            "blush": 0.3,
        },
        easing=EasingType.EASE_OUT,
    ))

    return seq


# ============================================================================
# TANTRUM SEQUENCE
# ============================================================================

def create_tantrum_sequence() -> AnimationSequence:
    """
    Create a tantrum animation sequence (when neglected).

    Shows frustration with jumping, shaking, and grumpy expressions.

    Returns:
        AnimationSequence for tantrum
    """
    seq = AnimationSequence(name="tantrum", priority=25)

    # 1. Annoyed start
    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Annoyed",
        properties={
            "eye_openness": 0.6,
            "scale_y": 1.0,
            "position_y": 0.0,
            "rotation": 0.0,
        },
        easing=EasingType.LINEAR,
    ))

    # 2. Stomp 1
    seq.keyframes.append(SequenceKeyframe(
        time=0.2,
        description="Stomp 1",
        properties={
            "position_y": -8.0,
            "scale_y": 1.1,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 3. Land stomp
    seq.keyframes.append(SequenceKeyframe(
        time=0.35,
        description="Land stomp",
        properties={
            "position_y": 2.0,
            "scale_y": 0.85,
            "scale_x": 1.15,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["dust"],
    ))

    # 4. Shake left
    seq.keyframes.append(SequenceKeyframe(
        time=0.5,
        description="Shake left",
        properties={
            "position_y": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "rotation": -15.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 5. Shake right
    seq.keyframes.append(SequenceKeyframe(
        time=0.65,
        description="Shake right",
        properties={
            "rotation": 15.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 6. Shake left again
    seq.keyframes.append(SequenceKeyframe(
        time=0.8,
        description="Shake left again",
        properties={
            "rotation": -12.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 7. Stomp 2
    seq.keyframes.append(SequenceKeyframe(
        time=1.0,
        description="Stomp 2",
        properties={
            "position_y": -10.0,
            "rotation": 0.0,
            "scale_y": 1.15,
        },
        easing=EasingType.EASE_OUT,
    ))

    # 8. Land hard
    seq.keyframes.append(SequenceKeyframe(
        time=1.2,
        description="Land hard",
        properties={
            "position_y": 3.0,
            "scale_y": 0.8,
            "scale_x": 1.2,
        },
        easing=EasingType.EASE_IN,
        trigger_particles=["dust", "sweat"],
    ))

    # 9. Pout
    seq.keyframes.append(SequenceKeyframe(
        time=1.5,
        description="Pout",
        properties={
            "position_y": 0.0,
            "scale_y": 0.95,
            "scale_x": 1.05,
            "eye_openness": 0.5,
            "rotation": 5.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    # 10. Settle
    seq.keyframes.append(SequenceKeyframe(
        time=2.0,
        description="Settle - still grumpy",
        properties={
            "position_y": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "eye_openness": 0.7,
            "rotation": 0.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    return seq


# ============================================================================
# CELEBRATION SEQUENCE
# ============================================================================

def create_celebration_sequence() -> AnimationSequence:
    """
    Create a celebration animation sequence (achievements).

    Happy bouncing with lots of particles.

    Returns:
        AnimationSequence for celebration
    """
    seq = AnimationSequence(name="celebration", priority=25)

    # Generate bounce pattern
    for i in range(6):
        t = i * 0.4

        # Jump up
        seq.keyframes.append(SequenceKeyframe(
            time=t,
            description=f"Bounce {i+1} - crouch",
            properties={
                "position_y": 3.0 if i > 0 else 0.0,
                "scale_y": 0.85,
                "scale_x": 1.1,
                "rotation": -10.0 if i % 2 == 0 else 10.0,
            },
            easing=EasingType.EASE_IN,
        ))

        seq.keyframes.append(SequenceKeyframe(
            time=t + 0.15,
            description=f"Bounce {i+1} - jump",
            properties={
                "position_y": -15.0 + i * 2,  # Decreasing height
                "scale_y": 1.15,
                "scale_x": 0.9,
                "rotation": 10.0 if i % 2 == 0 else -10.0,
            },
            easing=EasingType.EASE_OUT,
            trigger_particles=["sparkle", "star"] if i < 3 else ["sparkle"],
        ))

        seq.keyframes.append(SequenceKeyframe(
            time=t + 0.3,
            description=f"Bounce {i+1} - land",
            properties={
                "position_y": 2.0,
                "scale_y": 0.9,
                "scale_x": 1.08,
                "rotation": 0.0,
            },
            easing=EasingType.EASE_IN,
        ))

    # Final settle
    seq.keyframes.append(SequenceKeyframe(
        time=2.5,
        description="Final settle - happy",
        properties={
            "position_y": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "rotation": 0.0,
            "eye_openness": 0.8,  # Happy squint
            "blush": 0.4,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["heart", "confetti"],
    ))

    return seq


# ============================================================================
# PRE-BUILT SEQUENCE INSTANCES
# ============================================================================

# ============================================================================
# SLEEPING SEQUENCE (Gentle idle floating)
# ============================================================================

def create_sleeping_sequence() -> AnimationSequence:
    """
    Create sleeping idle animation sequence.

    Gentle floating movement with slow breathing and occasional
    subtle shifts. ZZZ particles spawn periodically.

    Returns:
        AnimationSequence for sleeping idle
    """
    seq = AnimationSequence(name="sleeping_idle", priority=10, loop=True)

    # Gentle floating up and down (8 second cycle)
    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Rest position",
        properties={
            "position_y": 5.0,
            "scale_y": 0.92,
            "scale_x": 1.02,
            "eye_openness": 0.0,
            "rotation": 3.0,
        },
        easing=EasingType.EASE_IN_OUT,
        trigger_particles=["zzz"],
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=2.0,
        description="Gentle rise",
        properties={
            "position_y": 3.0,
            "scale_y": 0.95,
            "rotation": 1.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=4.0,
        description="Peak float",
        properties={
            "position_y": 2.0,
            "scale_y": 0.97,
            "rotation": -1.0,
        },
        easing=EasingType.EASE_IN_OUT,
        trigger_particles=["zzz"],
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=6.0,
        description="Settle down",
        properties={
            "position_y": 4.0,
            "scale_y": 0.93,
            "rotation": 2.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=8.0,
        description="Return to rest",
        properties={
            "position_y": 5.0,
            "scale_y": 0.92,
            "scale_x": 1.02,
            "eye_openness": 0.0,
            "rotation": 3.0,
        },
        easing=EasingType.EASE_IN_OUT,
        trigger_particles=["zzz"],
    ))

    return seq


# ============================================================================
# CLICK REACTION SEQUENCE
# ============================================================================

def create_click_reaction_sequence() -> AnimationSequence:
    """
    Create click reaction animation sequence.

    Quick jump with happy wiggle and hearts.

    Returns:
        AnimationSequence for click reaction
    """
    seq = AnimationSequence(name="click_reaction", priority=25)

    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Start - squash before jump",
        properties={
            "position_y": 0.0,
            "scale_y": 0.9,
            "scale_x": 1.1,
            "rotation": 0.0,
            "eye_openness": 1.0,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.12,
        description="Jump up",
        properties={
            "position_y": -15.0,
            "scale_y": 1.15,
            "scale_x": 0.9,
            "rotation": 5.0,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["sparkle"],
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.3,
        description="Peak - happy squint",
        properties={
            "position_y": -12.0,
            "scale_y": 1.1,
            "eye_openness": 0.7,
            "blush": 0.3,
        },
        easing=EasingType.LINEAR,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.5,
        description="Land squash",
        properties={
            "position_y": 0.0,
            "scale_y": 0.85,
            "scale_x": 1.15,
            "rotation": -3.0,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.65,
        description="Wiggle left",
        properties={
            "scale_y": 1.02,
            "scale_x": 0.98,
            "rotation": -8.0,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["heart"],
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.8,
        description="Wiggle right",
        properties={
            "rotation": 8.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.95,
        description="Wiggle center",
        properties={
            "rotation": -4.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=1.1,
        description="Settle",
        properties={
            "position_y": 0.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "rotation": 0.0,
            "eye_openness": 1.0,
            "blush": 0.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    return seq


# ============================================================================
# YAWN SEQUENCE
# ============================================================================

def create_yawn_sequence() -> AnimationSequence:
    """
    Create yawn animation sequence.

    Big yawn with stretch when tired.

    Returns:
        AnimationSequence for yawning
    """
    seq = AnimationSequence(name="yawn", priority=20)

    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Start - normal",
        properties={
            "mouth_openness": 0.0,
            "eye_openness": 1.0,
            "scale_y": 1.0,
            "rotation": 0.0,
        },
        easing=EasingType.LINEAR,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.3,
        description="Mouth starts opening",
        properties={
            "mouth_openness": 0.3,
            "eye_openness": 0.7,
            "scale_y": 1.02,
            "rotation": -2.0,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.6,
        description="Big yawn - peak",
        properties={
            "mouth_openness": 1.0,
            "eye_openness": 0.2,
            "scale_y": 1.1,
            "scale_x": 0.95,
            "rotation": -5.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=1.3,
        description="Hold yawn",
        properties={
            "mouth_openness": 0.9,
            "eye_openness": 0.15,
            "scale_y": 1.08,
        },
        easing=EasingType.LINEAR,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=1.7,
        description="Mouth closing",
        properties={
            "mouth_openness": 0.4,
            "eye_openness": 0.4,
            "scale_y": 1.02,
            "rotation": -2.0,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=2.0,
        description="End - slightly tired",
        properties={
            "mouth_openness": 0.0,
            "eye_openness": 0.8,
            "scale_y": 1.0,
            "scale_x": 1.0,
            "rotation": 0.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    return seq


# ============================================================================
# BOUNCE SEQUENCE (Simple happy bounce)
# ============================================================================

def create_bounce_sequence() -> AnimationSequence:
    """
    Create happy bounce animation sequence.

    Quick, joyful bounce with squash and stretch.

    Returns:
        AnimationSequence for bouncing
    """
    seq = AnimationSequence(name="bounce", priority=20)

    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Squash before jump",
        properties={
            "position_y": 0.0,
            "squash": 0.8,
            "scale_y": 0.85,
            "scale_x": 1.15,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.15,
        description="Launch",
        properties={
            "position_y": -5.0,
            "squash": 1.1,
            "scale_y": 1.1,
            "scale_x": 0.92,
        },
        easing=EasingType.EASE_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.3,
        description="Peak",
        properties={
            "position_y": -15.0,
            "squash": 1.2,
            "scale_y": 1.15,
            "scale_x": 0.88,
        },
        easing=EasingType.EASE_OUT,
        trigger_particles=["sparkle"],
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.45,
        description="Descending",
        properties={
            "position_y": -5.0,
            "squash": 1.1,
            "scale_y": 1.1,
            "scale_x": 0.92,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.55,
        description="Land squash",
        properties={
            "position_y": 0.0,
            "squash": 0.85,
            "scale_y": 0.88,
            "scale_x": 1.12,
        },
        easing=EasingType.BOUNCE,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.75,
        description="Settle",
        properties={
            "position_y": 0.0,
            "squash": 1.0,
            "scale_y": 1.0,
            "scale_x": 1.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    return seq


# ============================================================================
# BREATHING SEQUENCE (Subtle idle)
# ============================================================================

def create_breathing_sequence() -> AnimationSequence:
    """
    Create gentle breathing animation sequence.

    Subtle scale pulse for idle state.

    Returns:
        AnimationSequence for breathing (looping)
    """
    seq = AnimationSequence(name="breathing", priority=5, loop=True)

    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Rest",
        properties={
            "scale_y": 1.0,
            "scale_x": 1.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=1.5,
        description="Inhale",
        properties={
            "scale_y": 1.03,
            "scale_x": 0.99,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=3.0,
        description="Exhale",
        properties={
            "scale_y": 1.0,
            "scale_x": 1.0,
        },
        easing=EasingType.EASE_IN_OUT,
    ))

    return seq


# ============================================================================
# BLINK SEQUENCE
# ============================================================================

def create_blink_sequence() -> AnimationSequence:
    """
    Create quick blink animation sequence.

    Fast close and open of eyes.

    Returns:
        AnimationSequence for blinking
    """
    seq = AnimationSequence(name="blink", priority=15)

    seq.keyframes.append(SequenceKeyframe(
        time=0.0,
        description="Eyes open",
        properties={
            "eye_openness": 1.0,
        },
        easing=EasingType.LINEAR,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.05,
        description="Closing",
        properties={
            "eye_openness": 0.3,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.08,
        description="Closed",
        properties={
            "eye_openness": 0.0,
        },
        easing=EasingType.EASE_IN,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.12,
        description="Opening",
        properties={
            "eye_openness": 0.3,
        },
        easing=EasingType.EASE_OUT,
    ))

    seq.keyframes.append(SequenceKeyframe(
        time=0.18,
        description="Eyes open",
        properties={
            "eye_openness": 1.0,
        },
        easing=EasingType.EASE_OUT,
    ))

    return seq


# ============================================================================
# PRE-BUILT SEQUENCE INSTANCES
# ============================================================================

EATING_SEQUENCE = create_eating_sequence()
PLAYING_SEQUENCE = create_playing_sequence()
EVOLUTION_SEQUENCE = create_evolution_sequence()
TANTRUM_SEQUENCE = create_tantrum_sequence()
CELEBRATION_SEQUENCE = create_celebration_sequence()
SLEEPING_SEQUENCE = create_sleeping_sequence()
CLICK_REACTION_SEQUENCE = create_click_reaction_sequence()
YAWN_SEQUENCE = create_yawn_sequence()
BOUNCE_SEQUENCE = create_bounce_sequence()
BREATHING_SEQUENCE = create_breathing_sequence()
BLINK_SEQUENCE = create_blink_sequence()


def get_sequence(name: str) -> Optional[AnimationSequence]:
    """
    Get a pre-built animation sequence by name.

    Args:
        name: Name of the sequence

    Returns:
        AnimationSequence or None if not found
    """
    sequences = {
        "eating": EATING_SEQUENCE,
        "playing": PLAYING_SEQUENCE,
        "evolution": EVOLUTION_SEQUENCE,
        "tantrum": TANTRUM_SEQUENCE,
        "celebration": CELEBRATION_SEQUENCE,
        "sleeping": SLEEPING_SEQUENCE,
        "sleeping_idle": SLEEPING_SEQUENCE,
        "click": CLICK_REACTION_SEQUENCE,
        "click_reaction": CLICK_REACTION_SEQUENCE,
        "yawn": YAWN_SEQUENCE,
        "bounce": BOUNCE_SEQUENCE,
        "breathing": BREATHING_SEQUENCE,
        "blink": BLINK_SEQUENCE,
    }
    return sequences.get(name.lower())
