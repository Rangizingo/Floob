"""
Particle Effects System for Floob 2.0.

Provides a lightweight particle system for visual effects:
- Hearts floating up
- Sparkles scattering
- ZZZs for sleeping
- Sweat drops falling
- Music notes bouncing
- Stars bursting
- Confetti falling with rotation
- Food crumbs falling

Features object pooling for performance optimization.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, Any
import math
import random
import tkinter as tk


class ParticleType(Enum):
    """Types of particles available in the system."""
    HEART = auto()           # Float up slowly, slight wobble, fade out
    SPARKLE = auto()         # Random scatter from center, shrink and fade
    ZZZ = auto()             # Float up diagonally, fade
    SWEAT = auto()           # Fall down with gravity, small
    MUSIC_NOTE = auto()      # Bounce up, rotate
    STAR = auto()            # Burst pattern outward
    CONFETTI = auto()        # Fall with rotation and drift
    CRUMB = auto()           # Fall quickly with gravity
    DUST = auto()            # Puff outward, fade quickly


@dataclass
class ParticleConfig:
    """
    Configuration for a particle type.

    Defines the visual appearance and behavior of a particle type.
    """
    # Visual
    symbol: str              # Unicode symbol or text to draw
    color: str               # Hex color
    font_size: int = 12      # Font size for text particles
    min_size: float = 1.0    # Minimum scale
    max_size: float = 1.0    # Maximum scale

    # Physics
    gravity: float = 0.0     # Downward acceleration (positive = down)
    drag: float = 0.0        # Velocity damping (0-1)

    # Velocity ranges
    vx_min: float = -20.0
    vx_max: float = 20.0
    vy_min: float = -30.0
    vy_max: float = -10.0

    # Lifetime
    lifetime_min: float = 0.5
    lifetime_max: float = 1.5

    # Behavior
    wobble: float = 0.0      # Horizontal oscillation amplitude
    wobble_speed: float = 5.0
    rotate: bool = False     # Whether particle rotates
    rotate_speed: float = 0.0
    shrink: bool = True      # Whether particle shrinks over lifetime
    fade: bool = True        # Whether particle fades over lifetime


# ============================================================================
# PARTICLE CONFIGURATIONS
# ============================================================================

PARTICLE_CONFIGS: dict[ParticleType, ParticleConfig] = {
    ParticleType.HEART: ParticleConfig(
        symbol="\u2665",  # Solid heart
        color="#FFADAD",  # Soft pink
        font_size=14,
        gravity=-5.0,     # Float upward
        vx_min=-10.0,
        vx_max=10.0,
        vy_min=-40.0,
        vy_max=-20.0,
        lifetime_min=1.0,
        lifetime_max=2.0,
        wobble=8.0,
        wobble_speed=4.0,
        shrink=False,
        fade=True,
    ),

    ParticleType.SPARKLE: ParticleConfig(
        symbol="\u2734",  # Eight-pointed star
        color="#FFF3B0",  # Soft yellow
        font_size=10,
        gravity=0.0,
        drag=0.02,
        vx_min=-60.0,
        vx_max=60.0,
        vy_min=-60.0,
        vy_max=60.0,
        lifetime_min=0.3,
        lifetime_max=0.8,
        shrink=True,
        fade=True,
    ),

    ParticleType.ZZZ: ParticleConfig(
        symbol="Z",
        color="#CDB4DB",  # Soft purple
        font_size=12,
        gravity=-8.0,     # Float up
        vx_min=5.0,       # Drift right and up
        vx_max=15.0,
        vy_min=-25.0,
        vy_max=-15.0,
        lifetime_min=1.5,
        lifetime_max=2.5,
        wobble=3.0,
        wobble_speed=2.0,
        shrink=False,
        fade=True,
    ),

    ParticleType.SWEAT: ParticleConfig(
        symbol="\u25cf",  # Filled circle (will be drawn as drop)
        color="#BDE0FE",  # Soft blue
        font_size=8,
        gravity=80.0,     # Fall down
        vx_min=-5.0,
        vx_max=5.0,
        vy_min=0.0,
        vy_max=10.0,
        lifetime_min=0.5,
        lifetime_max=1.0,
        shrink=False,
        fade=True,
    ),

    ParticleType.MUSIC_NOTE: ParticleConfig(
        symbol="\u266A",  # Eighth note
        color="#B5E48C",  # Soft green
        font_size=14,
        gravity=-30.0,    # Bounce up
        vx_min=-20.0,
        vx_max=20.0,
        vy_min=-50.0,
        vy_max=-30.0,
        lifetime_min=0.8,
        lifetime_max=1.5,
        rotate=True,
        rotate_speed=180.0,
        shrink=False,
        fade=True,
    ),

    ParticleType.STAR: ParticleConfig(
        symbol="\u2605",  # Black star
        color="#FFD700",  # Gold
        font_size=12,
        gravity=20.0,
        drag=0.01,
        vx_min=-80.0,
        vx_max=80.0,
        vy_min=-80.0,
        vy_max=20.0,
        lifetime_min=0.5,
        lifetime_max=1.2,
        rotate=True,
        rotate_speed=360.0,
        shrink=True,
        fade=True,
    ),

    ParticleType.CONFETTI: ParticleConfig(
        symbol="\u25a0",  # Square
        color="#FFB5A7",  # Soft coral (will be randomized)
        font_size=8,
        gravity=50.0,
        drag=0.02,
        vx_min=-40.0,
        vx_max=40.0,
        vy_min=-60.0,
        vy_max=-20.0,
        lifetime_min=1.5,
        lifetime_max=3.0,
        wobble=15.0,
        wobble_speed=8.0,
        rotate=True,
        rotate_speed=540.0,
        shrink=False,
        fade=True,
    ),

    ParticleType.CRUMB: ParticleConfig(
        symbol="\u25cf",  # Filled circle
        color="#DEB887",  # Burlywood (food color)
        font_size=6,
        gravity=120.0,    # Fall fast
        vx_min=-30.0,
        vx_max=30.0,
        vy_min=-10.0,
        vy_max=10.0,
        lifetime_min=0.3,
        lifetime_max=0.7,
        shrink=False,
        fade=False,
    ),

    ParticleType.DUST: ParticleConfig(
        symbol="\u25cf",  # Filled circle
        color="#D4D4D4",  # Light gray
        font_size=4,
        gravity=-10.0,    # Slight upward drift
        drag=0.05,
        vx_min=-30.0,
        vx_max=30.0,
        vy_min=-20.0,
        vy_max=10.0,
        lifetime_min=0.2,
        lifetime_max=0.5,
        shrink=True,
        fade=True,
    ),
}


# Confetti color palette
CONFETTI_COLORS = [
    "#FFB5A7",  # Soft coral
    "#FFD6E0",  # Soft pink
    "#A2D2FF",  # Soft blue
    "#B5E48C",  # Soft green
    "#FFF3B0",  # Soft yellow
    "#CDB4DB",  # Soft purple
]


# ============================================================================
# PARTICLE CLASS
# ============================================================================

@dataclass
class Particle:
    """
    A single particle in the particle system.

    Tracks position, velocity, lifetime, and visual properties.
    Particles are pooled and reused for performance.

    Attributes:
        x: Current X position
        y: Current Y position
        vx: X velocity (pixels per second)
        vy: Y velocity (pixels per second)
        lifetime: Total lifetime in seconds
        age: Current age in seconds
        particle_type: Type of particle
        color: Current color (may be randomized)
        size: Current size multiplier
        rotation: Current rotation in degrees
        active: Whether particle is currently in use
    """
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    lifetime: float = 1.0
    age: float = 0.0
    particle_type: ParticleType = ParticleType.SPARKLE
    color: str = "#FFFFFF"
    size: float = 1.0
    rotation: float = 0.0
    active: bool = False

    # Internal tracking
    _wobble_offset: float = 0.0
    _initial_x: float = 0.0

    def reset(
        self,
        x: float,
        y: float,
        particle_type: ParticleType,
        config: Optional[ParticleConfig] = None,
    ) -> None:
        """
        Reset particle for reuse from pool.

        Args:
            x: Starting X position
            y: Starting Y position
            particle_type: Type of particle to become
            config: Particle configuration (uses default if None)
        """
        if config is None:
            config = PARTICLE_CONFIGS.get(particle_type, PARTICLE_CONFIGS[ParticleType.SPARKLE])

        self.x = x
        self.y = y
        self._initial_x = x
        self.particle_type = particle_type
        self.age = 0.0
        self.active = True

        # Randomize within config ranges
        self.vx = random.uniform(config.vx_min, config.vx_max)
        self.vy = random.uniform(config.vy_min, config.vy_max)
        self.lifetime = random.uniform(config.lifetime_min, config.lifetime_max)
        self.size = random.uniform(config.min_size, config.max_size)
        self.rotation = random.uniform(0, 360) if config.rotate else 0.0
        self._wobble_offset = random.uniform(0, math.pi * 2)

        # Color (randomize for confetti)
        if particle_type == ParticleType.CONFETTI:
            self.color = random.choice(CONFETTI_COLORS)
        else:
            self.color = config.color

    def update(self, delta_time: float) -> bool:
        """
        Update particle state.

        Args:
            delta_time: Time elapsed in seconds

        Returns:
            True if particle is still alive, False if expired
        """
        if not self.active:
            return False

        self.age += delta_time

        # Check expiration
        if self.age >= self.lifetime:
            self.active = False
            return False

        config = PARTICLE_CONFIGS.get(self.particle_type)
        if config is None:
            self.active = False
            return False

        # Apply gravity
        self.vy += config.gravity * delta_time

        # Apply drag
        if config.drag > 0:
            self.vx *= (1.0 - config.drag)
            self.vy *= (1.0 - config.drag)

        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time

        # Apply wobble
        if config.wobble > 0:
            wobble_x = math.sin(self.age * config.wobble_speed + self._wobble_offset) * config.wobble
            self.x = self._initial_x + wobble_x + (self.vx * self.age)

        # Apply rotation
        if config.rotate:
            self.rotation += config.rotate_speed * delta_time

        return True

    def get_opacity(self) -> float:
        """Get current opacity based on lifetime."""
        config = PARTICLE_CONFIGS.get(self.particle_type)
        if config is None or not config.fade:
            return 1.0

        # Fade out in last 30% of lifetime
        fade_start = 0.7
        progress = self.age / self.lifetime

        if progress < fade_start:
            return 1.0
        else:
            return 1.0 - ((progress - fade_start) / (1.0 - fade_start))

    def get_scale(self) -> float:
        """Get current scale based on lifetime."""
        config = PARTICLE_CONFIGS.get(self.particle_type)
        if config is None or not config.shrink:
            return self.size

        # Shrink over lifetime
        progress = self.age / self.lifetime
        return self.size * (1.0 - progress * 0.7)


# ============================================================================
# PARTICLE EMITTER
# ============================================================================

@dataclass
class ParticleEmitter:
    """
    Emits particles at a specified rate.

    Can be positioned and configured to continuously emit
    particles of a specific type.

    Attributes:
        x: Emitter X position
        y: Emitter Y position
        particle_type: Type of particles to emit
        rate: Particles per second
        spread_x: Random X offset range
        spread_y: Random Y offset range
        active: Whether emitter is currently emitting
    """
    x: float = 0.0
    y: float = 0.0
    particle_type: ParticleType = ParticleType.SPARKLE
    rate: float = 5.0        # Particles per second
    spread_x: float = 10.0   # Random X offset
    spread_y: float = 10.0   # Random Y offset
    active: bool = True

    _accumulator: float = field(default=0.0, repr=False)

    def update(self, delta_time: float) -> int:
        """
        Update emitter and return number of particles to spawn.

        Args:
            delta_time: Time elapsed in seconds

        Returns:
            Number of particles to spawn this frame
        """
        if not self.active:
            return 0

        self._accumulator += delta_time * self.rate
        count = int(self._accumulator)
        self._accumulator -= count
        return count

    def get_spawn_position(self) -> tuple[float, float]:
        """
        Get a random spawn position within spread range.

        Returns:
            Tuple of (x, y) spawn position
        """
        x = self.x + random.uniform(-self.spread_x, self.spread_x)
        y = self.y + random.uniform(-self.spread_y, self.spread_y)
        return (x, y)


# ============================================================================
# PARTICLE SYSTEM
# ============================================================================

class ParticleSystem:
    """
    Manages all particles with object pooling for performance.

    Handles particle spawning, updating, and rendering.
    Uses object pooling to minimize garbage collection.

    Usage:
        system = ParticleSystem(pool_size=100)

        # Spawn particles
        system.emit(x=100, y=100, particle_type=ParticleType.HEART, count=5)

        # In update loop:
        system.update(delta_time)

        # In draw loop:
        system.draw(canvas)
    """

    def __init__(self, pool_size: int = 200) -> None:
        """
        Initialize particle system with object pool.

        Args:
            pool_size: Maximum number of particles in pool
        """
        self._pool_size = pool_size
        self._particles: list[Particle] = [Particle() for _ in range(pool_size)]
        self._active_count = 0
        self._emitters: list[ParticleEmitter] = []

    @property
    def active_count(self) -> int:
        """Get number of currently active particles."""
        return sum(1 for p in self._particles if p.active)

    def emit(
        self,
        x: float,
        y: float,
        particle_type: ParticleType,
        count: int = 1,
    ) -> int:
        """
        Emit particles at a position.

        Args:
            x: X position to emit from
            y: Y position to emit from
            particle_type: Type of particles to emit
            count: Number of particles to emit

        Returns:
            Number of particles actually emitted (may be less if pool is full)
        """
        emitted = 0
        config = PARTICLE_CONFIGS.get(particle_type)

        for _ in range(count):
            # Find inactive particle in pool
            particle = self._get_inactive_particle()
            if particle is None:
                break

            # Add some spread
            spread = 5.0
            px = x + random.uniform(-spread, spread)
            py = y + random.uniform(-spread, spread)

            particle.reset(px, py, particle_type, config)
            emitted += 1

        return emitted

    def emit_burst(
        self,
        x: float,
        y: float,
        particle_type: ParticleType,
        count: int = 10,
        radius: float = 20.0,
    ) -> int:
        """
        Emit particles in a burst pattern.

        Particles radiate outward from center.

        Args:
            x: Center X position
            y: Center Y position
            particle_type: Type of particles
            count: Number of particles
            radius: Spread radius

        Returns:
            Number of particles emitted
        """
        emitted = 0
        config = PARTICLE_CONFIGS.get(particle_type)

        for i in range(count):
            particle = self._get_inactive_particle()
            if particle is None:
                break

            # Calculate radial position
            angle = (i / count) * math.pi * 2 + random.uniform(-0.2, 0.2)
            dist = random.uniform(0, radius)
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist

            particle.reset(px, py, particle_type, config)

            # Override velocity to radiate outward
            speed = random.uniform(30, 80)
            particle.vx = math.cos(angle) * speed
            particle.vy = math.sin(angle) * speed

            emitted += 1

        return emitted

    def add_emitter(self, emitter: ParticleEmitter) -> None:
        """
        Add a continuous particle emitter.

        Args:
            emitter: Emitter to add
        """
        self._emitters.append(emitter)

    def remove_emitter(self, emitter: ParticleEmitter) -> None:
        """
        Remove a particle emitter.

        Args:
            emitter: Emitter to remove
        """
        if emitter in self._emitters:
            self._emitters.remove(emitter)

    def clear_emitters(self) -> None:
        """Remove all emitters."""
        self._emitters.clear()

    def clear(self) -> None:
        """Deactivate all particles."""
        for particle in self._particles:
            particle.active = False

    def update(self, delta_time: float) -> None:
        """
        Update all particles and emitters.

        Args:
            delta_time: Time elapsed in seconds
        """
        # Update emitters
        for emitter in self._emitters:
            spawn_count = emitter.update(delta_time)
            for _ in range(spawn_count):
                x, y = emitter.get_spawn_position()
                self.emit(x, y, emitter.particle_type, count=1)

        # Update particles
        for particle in self._particles:
            if particle.active:
                particle.update(delta_time)

    def draw(self, canvas: tk.Canvas, offset_x: float = 0, offset_y: float = 0) -> None:
        """
        Draw all active particles to a canvas.

        Args:
            canvas: Tkinter canvas to draw on
            offset_x: X offset for all particles
            offset_y: Y offset for all particles
        """
        for particle in self._particles:
            if not particle.active:
                continue

            config = PARTICLE_CONFIGS.get(particle.particle_type)
            if config is None:
                continue

            x = particle.x + offset_x
            y = particle.y + offset_y

            opacity = particle.get_opacity()
            scale = particle.get_scale()

            # Calculate color with opacity
            color = self._apply_opacity(particle.color, opacity)

            # Calculate font size with scale
            font_size = int(config.font_size * scale)
            if font_size < 4:
                continue

            # Draw based on particle type
            if particle.particle_type == ParticleType.SWEAT:
                # Draw as teardrop
                self._draw_teardrop(canvas, x, y, color, font_size)
            elif particle.particle_type in (ParticleType.CRUMB, ParticleType.DUST):
                # Draw as circle
                r = font_size / 2
                canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    fill=color, outline=""
                )
            else:
                # Draw as text
                canvas.create_text(
                    x, y,
                    text=config.symbol,
                    font=("Segoe UI Emoji", font_size),
                    fill=color,
                    angle=particle.rotation if config.rotate else 0,
                )

    def _get_inactive_particle(self) -> Optional[Particle]:
        """Get an inactive particle from the pool."""
        for particle in self._particles:
            if not particle.active:
                return particle
        return None

    def _apply_opacity(self, hex_color: str, opacity: float) -> str:
        """
        Blend color toward white based on opacity.

        Since Tkinter doesn't support true alpha, we simulate
        fade by blending toward white.

        Args:
            hex_color: Original hex color
            opacity: Opacity from 0 to 1

        Returns:
            Blended hex color
        """
        if opacity >= 1.0:
            return hex_color

        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Blend toward white (255)
        r = int(r + (255 - r) * (1 - opacity))
        g = int(g + (255 - g) * (1 - opacity))
        b = int(b + (255 - b) * (1 - opacity))

        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw_teardrop(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        color: str,
        size: int,
    ) -> None:
        """
        Draw a teardrop shape for sweat particles.

        Args:
            canvas: Canvas to draw on
            x: Center X
            y: Center Y
            color: Fill color
            size: Size in pixels
        """
        # Teardrop points
        points = [
            x, y - size,           # Top point
            x - size * 0.6, y,     # Left curve
            x, y + size * 0.6,     # Bottom
            x + size * 0.6, y,     # Right curve
        ]
        canvas.create_polygon(
            points,
            fill=color,
            outline="",
            smooth=True,
        )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def spawn_hearts(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 3,
) -> None:
    """Spawn heart particles floating up."""
    system.emit(x, y, ParticleType.HEART, count)


def spawn_sparkles(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 8,
) -> None:
    """Spawn sparkle particles in a burst."""
    system.emit_burst(x, y, ParticleType.SPARKLE, count, radius=15)


def spawn_stars(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 6,
) -> None:
    """Spawn star particles bursting outward."""
    system.emit_burst(x, y, ParticleType.STAR, count, radius=20)


def spawn_confetti(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 15,
) -> None:
    """Spawn confetti particles."""
    system.emit_burst(x, y, ParticleType.CONFETTI, count, radius=30)


def spawn_zzz(
    system: ParticleSystem,
    x: float,
    y: float,
) -> None:
    """Spawn a single ZZZ particle."""
    system.emit(x, y, ParticleType.ZZZ, 1)


def spawn_sweat(
    system: ParticleSystem,
    x: float,
    y: float,
) -> None:
    """Spawn a sweat drop."""
    system.emit(x, y, ParticleType.SWEAT, 1)


def spawn_crumbs(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 4,
) -> None:
    """Spawn food crumb particles."""
    system.emit(x, y, ParticleType.CRUMB, count)


def spawn_dust(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 5,
) -> None:
    """Spawn dust puff particles."""
    system.emit_burst(x, y, ParticleType.DUST, count, radius=10)


def spawn_music_notes(
    system: ParticleSystem,
    x: float,
    y: float,
    count: int = 2,
) -> None:
    """Spawn music note particles bouncing upward."""
    system.emit(x, y, ParticleType.MUSIC_NOTE, count)
