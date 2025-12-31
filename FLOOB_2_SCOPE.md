# Floob 2.0 - Project Scope & Development Checklist

## Overview

### Project Vision
Transform Floob from a complex animal-shaped creature app into a **Tamagotchi-inspired** virtual pet with:
- **Simple, expressive blob sprites** (not detailed animals)
- **Rich, fluid animation system** with 20+ unique animations
- **Evolution system** where pets grow and change based on care style

### Design Philosophy
- **Less is more**: Simple shapes, maximum expression
- **Movement over detail**: Personality through animation, not complexity
- **Meaningful progression**: Evolution rewards engagement

### Success Criteria
- [ ] Pet feels alive through animation alone
- [ ] Users can identify pet's mood without UI indicators
- [ ] Evolution creates attachment and replay value
- [ ] Runs smoothly at 30+ FPS

---

## Architecture

### Core Systems

```
┌─────────────────────────────────────────────────────────────┐
│                      FLOOB 2.0 ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   PET CORE  │───▶│  ANIMATION  │───▶│  RENDERER   │      │
│  │             │    │   ENGINE    │    │             │      │
│  │ - Stats     │    │             │    │ - Canvas    │      │
│  │ - Evolution │    │ - States    │    │ - Sprites   │      │
│  │ - Care Log  │    │ - Keyframes │    │ - Effects   │      │
│  └─────────────┘    │ - Tweening  │    └─────────────┘      │
│         │           └─────────────┘           │              │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ PERSISTENCE │    │   EVENTS    │    │     UI      │      │
│  │             │    │             │    │             │      │
│  │ - JSON Save │    │ - Input     │    │ - Menu      │      │
│  │ - Evolution │    │ - Triggers  │    │ - Overlay   │      │
│  │   History   │    │ - Callbacks │    │ - Dialogs   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### File Structure (Target)

```
Floob/
├── main.py                 # Entry point
├── config.py               # Constants, colors, timing
│
├── core/
│   ├── __init__.py
│   ├── pet.py              # Pet class (stats, state)
│   ├── evolution.py        # Evolution system
│   └── care_tracker.py     # Tracks care patterns for evolution
│
├── animation/
│   ├── __init__.py
│   ├── engine.py           # Animation engine (tweening, keyframes)
│   ├── states.py           # Animation state definitions
│   ├── sequences.py        # Complex animation sequences
│   └── particles.py        # Particle effects system
│
├── graphics/
│   ├── __init__.py
│   ├── renderer.py         # Main renderer
│   ├── sprites.py          # Simple blob sprite drawing
│   ├── expressions.py      # Eye/mouth expressions
│   └── effects.py          # Visual effects (sparkles, etc.)
│
├── ui/
│   ├── __init__.py
│   ├── window.py           # Transparent overlay window
│   ├── menu.py             # Right-click context menu
│   └── dialogs.py          # Evolution, stats dialogs
│
├── persistence/
│   ├── __init__.py
│   └── save_manager.py     # JSON save/load
│
└── data/
    └── pet_state.json      # Saved pet data
```

---

## Development Phases

---

## Phase 1: Foundation & Data Models
*Establish core data structures and configuration*

### 1.1 Configuration Module
- [ ] **1.1.1** Create `config.py` with global constants
- [ ] **1.1.2** Define pastel color palette (10 base colors + variants)
- [ ] **1.1.3** Define timing constants (decay rates, animation speeds)
- [ ] **1.1.4** Define evolution thresholds and XP values

**Acceptance Criteria:**
- All magic numbers moved to config
- Colors are soft pastels
- Easy to tune gameplay balance

### 1.2 Pet Core Data Model
- [ ] **1.2.1** Refactor `PetStats` dataclass (hunger, happiness, energy)
- [ ] **1.2.2** Add `experience` and `level` fields
- [ ] **1.2.3** Add `evolution_stage` enum (EGG, BABY, CHILD, TEEN, ADULT)
- [ ] **1.2.4** Add `care_style` tracking (balanced, spoiled, neglected, playful, pampered)
- [ ] **1.2.5** Add `birth_time` and `evolution_history` list
- [ ] **1.2.6** Add `form_id` to track which evolution path was taken

**Acceptance Criteria:**
- Pet can track all data needed for evolution
- Care patterns are logged for evolution calculation
- Backwards compatible with existing saves (migration)

### 1.3 Evolution System Data Model
- [ ] **1.3.1** Create `evolution.py` with `EvolutionStage` enum
- [ ] **1.3.2** Define `EvolutionForm` dataclass (id, name, stage, requirements)
- [ ] **1.3.3** Create evolution tree structure (dict mapping form_id → possible_evolutions)
- [ ] **1.3.4** Define 15 evolution forms across 5 stages:
  - EGG (1 form)
  - BABY (1 form)
  - CHILD (3 forms based on early care)
  - TEEN (5 forms based on care style)
  - ADULT (5 forms - final evolutions)
- [ ] **1.3.5** Create `check_evolution()` function

**Acceptance Criteria:**
- Clear evolution paths defined
- Each form has distinct visual identity planned
- Evolution requirements are balanced

### 1.4 Care Tracker
- [ ] **1.4.1** Create `care_tracker.py`
- [ ] **1.4.2** Track feeding frequency and amounts
- [ ] **1.4.3** Track play sessions
- [ ] **1.4.4** Track sleep patterns
- [ ] **1.4.5** Track neglect periods (stats below threshold)
- [ ] **1.4.6** Calculate `care_style` from patterns

**Acceptance Criteria:**
- Accurately categorizes care patterns
- Updates in real-time
- Persists between sessions

---

## Phase 2: Animation Engine
*Build the animation system that brings pets to life*

### 2.1 Animation Engine Core
- [x] **2.1.1** Create `animation/engine.py` with `AnimationEngine` class
- [x] **2.1.2** Implement keyframe system (time -> value)
- [x] **2.1.3** Implement tweening functions:
  - Linear
  - Ease-in (slow start)
  - Ease-out (slow end)
  - Ease-in-out (slow start and end)
  - Bounce (overshoot and settle)
  - Elastic (spring effect)
- [x] **2.1.4** Implement animation blending (smooth transitions)
- [x] **2.1.5** Create animation queue for chaining

**Acceptance Criteria:**
- [x] Animations are smooth (no jitter)
- [x] Can blend between any two states
- [x] Supports complex easing curves

### 2.2 Animation State Definitions
- [x] **2.2.1** Create `animation/states.py`
- [x] **2.2.2** Define `AnimationProperty` enum:
  - POSITION_X, POSITION_Y (+ OFFSET_X, OFFSET_Y aliases)
  - SCALE_X, SCALE_Y
  - ROTATION
  - EYE_OPENNESS (0-1)
  - MOUTH_OPENNESS (0-1)
  - MOUTH_CURVE (-1 to 1, sad to happy)
  - BODY_SQUASH (vertical compression) / SQUASH
  - BODY_STRETCH (horizontal stretch) / STRETCH
  - LIMB_PHASE (0-1 for walk cycle)
  - GLOW_INTENSITY, BLUSH/BLUSH_OPACITY
- [x] **2.2.3** Define base animation parameters for each state

**Acceptance Criteria:**
- [x] All animatable properties defined
- [x] Properties can be combined

### 2.3 Idle Animations (5 variations)
- [x] **2.3.1** Implement **Breathing** (gentle scale pulse)
- [x] **2.3.2** Implement **Blinking** (random timing, quick close/open)
- [x] **2.3.3** Implement **Looking Around** (eye movement, head tilt)
- [x] **2.3.4** Implement **Fidgeting** (small position shifts)
- [x] **2.3.5** Implement **Yawning** (mouth open, eyes squint, stretch)

**Acceptance Criteria:**
- [x] Idle never looks static
- [x] Random variation in timing
- [x] Can interrupt cleanly

### 2.4 Reaction Animations (8 types)
- [x] **2.4.1** Implement **Click Reaction** (jump, then happy wiggle)
- [x] **2.4.2** Implement **Double-Click Trick** (spin with sparkles)
- [x] **2.4.3** Implement **Drag Squish** (squash in movement direction)
- [x] **2.4.4** Implement **Feed Reaction** (excited, chomp sequence)
- [x] **2.4.5** Implement **Play Reaction** (bounce, zoom around)
- [x] **2.4.6** Implement **Sleep Transition** (slow droop, curl up)
- [x] **2.4.7** Implement **Wake Transition** (stretch, shake off)
- [x] **2.4.8** Implement **Level Up** (glow, shake, burst of light)

**Acceptance Criteria:**
- [x] Each reaction feels distinct
- [x] Clear feedback for user action
- [x] Smooth transitions in/out

### 2.5 Complex Animation Sequences
- [x] **2.5.1** Create `animation/sequences.py`
- [x] **2.5.2** Implement **Eating Sequence** (10 keyframes):
  1. Notice food -> excited eyes
  2. Lean forward
  3. Open mouth wide
  4. Chomp (3x with squash)
  5. Swallow (throat bulge)
  6. Satisfied expression
  7. Happy wiggle
  8. Return to normal
- [x] **2.5.3** Implement **Playing Sequence** (13 keyframes):
  1. See toy -> alert
  2. Crouch (anticipation)
  3. Pounce forward
  4. Tumble/roll
  5. Grab toy
  6. Shake toy left/right
  7. Toss toy
  8. Chase toy
  9. Catch toy
  10. Victory wiggle
  11. Tired pant
  12. Rest pose
- [x] **2.5.4** Implement **Tantrum Sequence** (when neglected)
- [x] **2.5.5** Implement **Evolution Sequence** (dramatic transformation)
- [x] **2.5.6** Implement **Celebration Sequence** (achievements)
- [x] **2.5.7** Implement **Sleeping Sequence** (gentle idle float)
- [x] **2.5.8** Implement **Bounce Sequence** (simple happy bounce)
- [x] **2.5.9** Implement **Blink Sequence** (quick eye blink)
- [x] **2.5.10** Implement **Yawn Sequence** (tired yawn)

**Acceptance Criteria:**
- [x] Sequences tell a mini-story
- [x] Each frame is distinct
- [x] Sequences can be interrupted gracefully

### 2.6 Particle Effects System
- [x] **2.6.1** Create `animation/particles.py`
- [x] **2.6.2** Implement particle spawner (position, velocity, lifetime)
- [x] **2.6.3** Implement particle types:
  - Hearts (floating up)
  - Sparkles (random scatter)
  - ZZZs (floating up, fading)
  - Sweat drops (falling)
  - Music notes (bouncing)
  - Stars (burst pattern)
  - Confetti (falling, rotating)
  - Food crumbs (falling)
  - Dust (puff outward)
- [x] **2.6.4** Implement particle pooling (performance)

**Acceptance Criteria:**
- [x] Particles enhance without overwhelming
- [x] No performance impact (object pooling)
- [x] Can spawn multiple types simultaneously

---

## Phase 3: Simple Sprite Graphics
*Replace complex animals with expressive blobs*

### 3.1 Base Sprite System
- [x] **3.1.1** Create `graphics/sprites.py`
- [x] **3.1.2** Define base blob shape (rounded rectangle/oval)
- [x] **3.1.3** Implement squash/stretch deformation
- [x] **3.1.4** Implement color with gradient/shading
- [x] **3.1.5** Add subtle outline for definition

**Acceptance Criteria:**
- Blob looks soft and appealing
- Deforms smoothly for animation
- Works at different sizes

### 3.2 Expression System
- [x] **3.2.1** Create `graphics/expressions.py`
- [x] **3.2.2** Implement **Eye System**:
  - Basic dot eyes
  - Blink (line)
  - Happy (curved ^)
  - Sad (curved v)
  - Surprised (large)
  - Sleepy (half-closed)
  - Sparkle (star highlight)
- [x] **3.2.3** Implement **Mouth System**:
  - Neutral (small line)
  - Happy (curve up)
  - Sad (curve down)
  - Open (various sizes)
  - Eating (chomp)
  - Yawn (wide)
- [x] **3.2.4** Implement **Blush Marks** (toggle on/off)
- [x] **3.2.5** Implement **Sweat Drop** (when hungry/tired)

**Acceptance Criteria:**
- Can express full range of emotions
- Eye/mouth combinations work together
- Expressions change smoothly

### 3.3 Evolution Stage Appearances
- [x] **3.3.1** Design **EGG Stage**:
  - Oval shape with crack lines
  - Wobble animation
  - Glow from inside
- [x] **3.3.2** Design **BABY Stage**:
  - Tiny blob (60% of adult size)
  - Huge eyes relative to body
  - Stubby nub limbs
  - Extra wobbly movement
- [x] **3.3.3** Design **CHILD Stage** (3 variants):
  - Balanced: Rounded, symmetric
  - Playful: Slightly stretched, energetic
  - Sleepy: Droopy, soft
- [x] **3.3.4** Design **TEEN Stage** (5 variants):
  - Based on care style
  - Distinct silhouettes
  - Emerging accessories
- [x] **3.3.5** Design **ADULT Stage** (5 variants):
  - Full personality expression
  - Unique accessories/markings
  - Distinct particle effects

**Acceptance Criteria:**
- Clear visual progression through stages
- Each variant is recognizable
- Evolution feels rewarding

### 3.4 Visual Effects
- [x] **3.4.1** Create `graphics/effects.py`
- [x] **3.4.2** Implement glow effect (for egg, level up)
- [x] **3.4.3** Implement shadow (slight oval underneath)
- [x] **3.4.4** Implement thought bubble
- [x] **3.4.5** Implement stat indicators (hunger/happy/energy icons)

**Acceptance Criteria:**
- Effects enhance without cluttering
- Consistent pastel aesthetic

---

## Phase 4: Evolution System Implementation
*Make pets grow and change*

### 4.1 Evolution Mechanics
- [ ] **4.1.1** Implement XP gain from interactions:
  - Feeding: +5 XP
  - Playing: +10 XP
  - Clicking: +1 XP
  - Time alive: +1 XP per minute
- [ ] **4.1.2** Implement level thresholds:
  - Baby → Child: Level 5
  - Child → Teen: Level 15
  - Teen → Adult: Level 30
- [ ] **4.1.3** Implement care style calculation
- [ ] **4.1.4** Implement evolution trigger check
- [ ] **4.1.5** Implement evolution selection (which form based on care)

**Acceptance Criteria:**
- Evolution feels achievable but not instant
- Care style affects outcome
- Clear progression feeling

### 4.2 Evolution Event
- [ ] **4.2.1** Detect evolution ready state
- [ ] **4.2.2** Show pre-evolution signs (glowing, excited)
- [ ] **4.2.3** Trigger evolution animation sequence
- [ ] **4.2.4** Transform sprite to new form
- [ ] **4.2.5** Show celebration effects
- [ ] **4.2.6** Display "Evolved into [Form Name]!" message
- [ ] **4.2.7** Save new form to persistence

**Acceptance Criteria:**
- Evolution is a memorable moment
- Player understands what happened
- New form is clearly different

### 4.3 Special Evolutions
- [ ] **4.3.1** Implement **Golden Form** (perfect care 7 days)
- [ ] **4.3.2** Implement **Ghost Form** (revive from neglect)
- [ ] **4.3.3** Implement **Rainbow Form** (special date trigger)
- [ ] **4.3.4** Implement evolution hints in UI

**Acceptance Criteria:**
- Special forms feel rare and special
- Hints don't give away secrets
- Adds replay value

---

## Phase 5: UI & Integration
*Bring everything together*

### 5.1 Updated Menu System
- [ ] **5.1.1** Redesign right-click menu:
  - Feed
  - Play
  - Sleep/Wake
  - Stats (with evolution progress)
  - Evolution History
  - Settings (auto-care toggle)
  - Quit
- [ ] **5.1.2** Add evolution progress bar to stats
- [ ] **5.1.3** Add care style indicator

**Acceptance Criteria:**
- Menu is clean and usable
- Evolution progress is visible
- All features accessible

### 5.2 Stats & Evolution Dialog
- [ ] **5.2.1** Create stats dialog with:
  - Current stats (bars)
  - Level and XP progress
  - Current form name and stage
  - Care style breakdown
  - Time until next evolution check
- [ ] **5.2.2** Create evolution history dialog:
  - Timeline of forms
  - Unlock dates
  - Total forms discovered

**Acceptance Criteria:**
- Information is clear and readable
- Progress feels tangible

### 5.3 Persistence Updates
- [ ] **5.3.1** Update save format for evolution data
- [ ] **5.3.2** Add migration from old save format
- [ ] **5.3.3** Save evolution history
- [ ] **5.3.4** Save care tracking data

**Acceptance Criteria:**
- Old saves still work
- No data loss on update
- Evolution progress persists

### 5.4 Integration & Polish
- [ ] **5.4.1** Connect all systems in main.py
- [ ] **5.4.2** Add startup animation (egg hatch for new pets)
- [ ] **5.4.3** Add ambient behaviors (random idle variations)
- [ ] **5.4.4** Performance optimization pass
- [ ] **5.4.5** Bug fix pass

**Acceptance Criteria:**
- App runs smoothly
- No crashes or freezes
- Feels polished and complete

---

## Phase 6: Testing & Polish
*Ensure quality*

### 6.1 Testing
- [ ] **6.1.1** Test all animation states and transitions
- [ ] **6.1.2** Test evolution paths (all 15 forms reachable)
- [ ] **6.1.3** Test save/load with evolution data
- [ ] **6.1.4** Test migration from old saves
- [ ] **6.1.5** Test performance over extended runtime

### 6.2 Polish
- [ ] **6.2.1** Tune animation timing
- [ ] **6.2.2** Balance XP and evolution rates
- [ ] **6.2.3** Adjust color palette if needed
- [ ] **6.2.4** Add sound effects (optional future)

---

## Evolution Tree Reference

```
                              ┌─────────┐
                              │   EGG   │
                              │ (Blob)  │
                              └────┬────┘
                                   │
                              ┌────▼────┐
                              │  BABY   │
                              │(Bloblet)│
                              └────┬────┘
                 ┌─────────────────┼─────────────────┐
                 ▼                 ▼                 ▼
          ┌──────────┐      ┌──────────┐      ┌──────────┐
          │  CHILD   │      │  CHILD   │      │  CHILD   │
          │(Bouncy)  │      │(Balanced)│      │ (Sleepy) │
          │ playful  │      │  normal  │      │ pampered │
          └────┬─────┘      └────┬─────┘      └────┬─────┘
       ┌───────┴───┐             │           ┌─────┴─────┐
       ▼           ▼             ▼           ▼           ▼
   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
   │ TEEN  │   │ TEEN  │   │ TEEN  │   │ TEEN  │   │ TEEN  │
   │Sparky │   │Zippy  │   │ Chill │   │Dreamy │   │ Cozy  │
   └───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘   └───┬───┘
       │           │           │           │           │
       ▼           ▼           ▼           ▼           ▼
   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
   │ ADULT │   │ ADULT │   │ ADULT │   │ ADULT │   │ ADULT │
   │Zapper │   │Dasher │   │Loafer │   │Mystic │   │Floofy │
   └───────┘   └───────┘   └───────┘   └───────┘   └───────┘

   SPECIAL FORMS (any stage):
   - Golden (perfect care 7 days)
   - Ghost (revived from neglect)
   - Rainbow (special date)
```

---

## Color Palette Reference

### Base Pastels
| Name | Hex | Usage |
|------|-----|-------|
| Soft Pink | #FFD6E0 | Blush, hearts |
| Soft Blue | #A2D2FF | Water effects, calm |
| Soft Purple | #CDB4DB | Mystic, sleep |
| Soft Green | #B5E48C | Nature, health |
| Soft Yellow | #FFF3B0 | Energy, happy |
| Soft Orange | #FFB5A7 | Warm, food |
| Soft Cream | #FFF8F0 | Highlights |
| Soft Gray | #E8E8E8 | Shadows |

### Evolution Stage Tints
| Stage | Tint |
|-------|------|
| Egg | Warm white glow |
| Baby | Extra soft/desaturated |
| Child | Base colors |
| Teen | Slightly more saturated |
| Adult | Full saturation + unique accents |

---

## Workflow

1. Complete task (e.g., 1.1.1)
2. Test the change works
3. Mark task complete: `[x]`
4. Move to next task
5. Commit after completing each subsection (1.1, 1.2, etc.)
6. Push after completing each phase

---

## Notes

- **Priority**: Animation system is the heart - make it great
- **Simplicity**: Resist adding complexity to sprites
- **Performance**: Keep it light - this runs constantly
- **Charm**: Small details make big differences

---

*Last Updated: December 30, 2025*
*Version: 2.0 Scope Draft*
