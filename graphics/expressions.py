"""
Floob 2.0 Expression System.

Provides expressive eyes and mouths for blob sprites.
Expressions are simple but convey a wide range of emotions
through basic shapes and minimal detail.

Eye Emotions:
- Normal (dot eyes)
- Blink (horizontal line)
- Happy (curved ^ shape)
- Sad (curved v shape)
- Surprised (large circles)
- Sleepy (half-closed)
- Sparkle (star highlight)

Mouth Emotions:
- Neutral (small line)
- Happy (curve smile)
- Sad (curve frown)
- Open (oval)
- Eating (wide with chomp)
- Yawn (very wide)
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple

# Import colors
try:
    from core.config import Colors
except ImportError:
    class Colors:
        SOFT_PINK = "#FFD6E0"
        SOFT_BLUE = "#A2D2FF"
        BLACK = "#2D2D2D"
        WHITE = "#FFFFFF"


class EyeEmotion(Enum):
    """Eye expression types."""
    NORMAL = auto()
    BLINK = auto()
    HAPPY = auto()
    SAD = auto()
    SURPRISED = auto()
    SLEEPY = auto()
    SPARKLE = auto()
    ANGRY = auto()
    LOVE = auto()  # Heart eyes


class MouthEmotion(Enum):
    """Mouth expression types."""
    NEUTRAL = auto()
    HAPPY = auto()
    SAD = auto()
    OPEN = auto()
    EATING = auto()
    YAWN = auto()
    SMIRK = auto()
    WORRIED = auto()


@dataclass
class EyeParams:
    """
    Parameters for eye rendering.

    Attributes:
        emotion: Current eye emotion.
        openness: How open the eyes are (0.0 = closed, 1.0 = fully open).
        direction: Tuple of (x, y) offset for looking direction.
        size_multiplier: Eye size multiplier (babies have bigger eyes).
        pupil_size: Pupil size relative to eye.
        highlight: Whether to show highlight/sparkle.
    """
    emotion: EyeEmotion = EyeEmotion.NORMAL
    openness: float = 1.0
    direction: Tuple[float, float] = (0.0, 0.0)
    size_multiplier: float = 1.0
    pupil_size: float = 0.5
    highlight: bool = True


@dataclass
class MouthParams:
    """
    Parameters for mouth rendering.

    Attributes:
        emotion: Current mouth emotion.
        openness: How open the mouth is (0.0 = closed, 1.0 = fully open).
        width: Mouth width multiplier.
    """
    emotion: MouthEmotion = MouthEmotion.NEUTRAL
    openness: float = 0.0
    width: float = 1.0


class ExpressionRenderer:
    """
    Renders facial expressions (eyes and mouth) on blob sprites.

    Uses simple shapes to convey emotions without complex details.
    """

    # Default colors
    EYE_COLOR = "#2D2D2D"  # Near black
    EYE_WHITE = "#FFFFFF"
    HIGHLIGHT_COLOR = "#FFFFFF"
    MOUTH_COLOR = "#2D2D2D"
    TONGUE_COLOR = "#FFADAD"  # Soft pink/red
    BLUSH_COLOR = "#FFD6E0"  # Soft pink
    SWEAT_COLOR = "#A2D2FF"  # Soft blue

    def __init__(
        self,
        eye_spacing: float = 0.25,
        eye_height: float = -0.1,
        mouth_height: float = 0.15,
        base_eye_size: float = 8.0,
        base_mouth_width: float = 12.0,
    ) -> None:
        """
        Initialize the expression renderer.

        Args:
            eye_spacing: Eye spacing as ratio of face width.
            eye_height: Eye vertical position as ratio of face height (negative = up).
            mouth_height: Mouth vertical position as ratio of face height.
            base_eye_size: Base eye radius in pixels.
            base_mouth_width: Base mouth width in pixels.
        """
        self.eye_spacing = eye_spacing
        self.eye_height = eye_height
        self.mouth_height = mouth_height
        self.base_eye_size = base_eye_size
        self.base_mouth_width = base_mouth_width
        self._canvas_items: List[int] = []

    def draw_eyes(
        self,
        canvas: tk.Canvas,
        face_x: float,
        face_y: float,
        face_width: float,
        face_height: float,
        params: Optional[EyeParams] = None,
    ) -> List[int]:
        """
        Draw eyes on the blob face.

        Args:
            canvas: Tkinter canvas to draw on.
            face_x: Center X of face.
            face_y: Center Y of face.
            face_width: Width of face.
            face_height: Height of face.
            params: Eye rendering parameters.

        Returns:
            List of canvas item IDs created.
        """
        params = params or EyeParams()
        items = []

        # Calculate eye positions
        eye_y = face_y + face_height * self.eye_height
        eye_offset = face_width * self.eye_spacing
        eye_size = self.base_eye_size * params.size_multiplier

        # Apply look direction
        look_x, look_y = params.direction
        look_x = max(-1.0, min(1.0, look_x)) * eye_size * 0.3
        look_y = max(-1.0, min(1.0, look_y)) * eye_size * 0.2

        # Draw both eyes
        for side in [-1, 1]:  # -1 = left, 1 = right
            eye_x = face_x + side * eye_offset

            if params.emotion == EyeEmotion.BLINK or params.openness <= 0.1:
                # Closed eyes - horizontal line
                items.extend(self._draw_closed_eye(
                    canvas, eye_x, eye_y, eye_size
                ))

            elif params.emotion == EyeEmotion.HAPPY:
                # Happy eyes - upward arc (^ shape)
                items.extend(self._draw_happy_eye(
                    canvas, eye_x, eye_y, eye_size
                ))

            elif params.emotion == EyeEmotion.SAD:
                # Sad eyes - downward arc
                items.extend(self._draw_sad_eye(
                    canvas, eye_x, eye_y, eye_size
                ))

            elif params.emotion == EyeEmotion.SURPRISED:
                # Surprised - large circles
                items.extend(self._draw_surprised_eye(
                    canvas, eye_x, eye_y, eye_size * 1.3,
                    look_x, look_y, params.highlight
                ))

            elif params.emotion == EyeEmotion.SLEEPY:
                # Sleepy - half-closed, droopy
                items.extend(self._draw_sleepy_eye(
                    canvas, eye_x, eye_y, eye_size, params.openness
                ))

            elif params.emotion == EyeEmotion.SPARKLE:
                # Sparkle - star highlight
                items.extend(self._draw_sparkle_eye(
                    canvas, eye_x, eye_y, eye_size,
                    look_x, look_y
                ))

            elif params.emotion == EyeEmotion.ANGRY:
                # Angry - angled brows
                items.extend(self._draw_angry_eye(
                    canvas, eye_x, eye_y, eye_size, side,
                    look_x, look_y
                ))

            elif params.emotion == EyeEmotion.LOVE:
                # Heart eyes
                items.extend(self._draw_heart_eye(
                    canvas, eye_x, eye_y, eye_size
                ))

            else:  # NORMAL
                # Normal dot eyes with optional highlight
                items.extend(self._draw_normal_eye(
                    canvas, eye_x, eye_y, eye_size,
                    look_x, look_y, params.highlight
                ))

        return items

    def _draw_normal_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
        look_x: float,
        look_y: float,
        highlight: bool,
    ) -> List[int]:
        """Draw a normal dot eye."""
        items = []

        # Main eye (dark circle)
        eye_id = canvas.create_oval(
            x - size + look_x, y - size + look_y,
            x + size + look_x, y + size + look_y,
            fill=self.EYE_COLOR,
            outline="",
        )
        items.append(eye_id)

        # Highlight (small white circle)
        if highlight:
            hl_size = size * 0.35
            hl_x = x - size * 0.3 + look_x
            hl_y = y - size * 0.3 + look_y
            hl_id = canvas.create_oval(
                hl_x - hl_size, hl_y - hl_size,
                hl_x + hl_size, hl_y + hl_size,
                fill=self.HIGHLIGHT_COLOR,
                outline="",
            )
            items.append(hl_id)

        return items

    def _draw_closed_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
    ) -> List[int]:
        """Draw a closed eye (horizontal line)."""
        items = []
        line_id = canvas.create_line(
            x - size, y,
            x + size, y,
            fill=self.EYE_COLOR,
            width=2,
            capstyle=tk.ROUND,
        )
        items.append(line_id)
        return items

    def _draw_happy_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
    ) -> List[int]:
        """Draw a happy eye (^ arc)."""
        items = []
        # Draw upward arc
        arc_id = canvas.create_arc(
            x - size, y - size * 0.5,
            x + size, y + size * 1.5,
            start=0, extent=180,
            style=tk.ARC,
            outline=self.EYE_COLOR,
            width=2,
        )
        items.append(arc_id)
        return items

    def _draw_sad_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
    ) -> List[int]:
        """Draw a sad eye (v arc, slightly droopy)."""
        items = []
        # Draw downward arc
        arc_id = canvas.create_arc(
            x - size, y - size * 1.2,
            x + size, y + size * 0.8,
            start=180, extent=180,
            style=tk.ARC,
            outline=self.EYE_COLOR,
            width=2,
        )
        items.append(arc_id)
        return items

    def _draw_surprised_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
        look_x: float,
        look_y: float,
        highlight: bool,
    ) -> List[int]:
        """Draw a surprised eye (large circle with pupil)."""
        items = []

        # White of eye
        white_id = canvas.create_oval(
            x - size + look_x * 0.3, y - size + look_y * 0.3,
            x + size + look_x * 0.3, y + size + look_y * 0.3,
            fill=self.EYE_WHITE,
            outline=self.EYE_COLOR,
            width=1,
        )
        items.append(white_id)

        # Pupil
        pupil_size = size * 0.5
        pupil_id = canvas.create_oval(
            x - pupil_size + look_x, y - pupil_size + look_y,
            x + pupil_size + look_x, y + pupil_size + look_y,
            fill=self.EYE_COLOR,
            outline="",
        )
        items.append(pupil_id)

        # Highlight
        if highlight:
            hl_size = size * 0.25
            hl_x = x - size * 0.3 + look_x * 0.5
            hl_y = y - size * 0.3 + look_y * 0.5
            hl_id = canvas.create_oval(
                hl_x - hl_size, hl_y - hl_size,
                hl_x + hl_size, hl_y + hl_size,
                fill=self.HIGHLIGHT_COLOR,
                outline="",
            )
            items.append(hl_id)

        return items

    def _draw_sleepy_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
        openness: float,
    ) -> List[int]:
        """Draw a sleepy half-closed eye."""
        items = []

        if openness < 0.3:
            # Nearly closed - just a line
            return self._draw_closed_eye(canvas, x, y, size)

        # Half-closed eye with droopy lid
        # Draw the eye
        eye_height = size * openness * 0.8
        eye_id = canvas.create_oval(
            x - size, y - eye_height,
            x + size, y + eye_height,
            fill=self.EYE_COLOR,
            outline="",
        )
        items.append(eye_id)

        # Droopy eyelid (covers top portion)
        lid_y = y - eye_height * 0.5
        lid_id = canvas.create_arc(
            x - size * 1.2, lid_y - size,
            x + size * 1.2, lid_y + size * 0.5,
            start=0, extent=-180,
            style=tk.ARC,
            outline=self.EYE_COLOR,
            width=2,
        )
        items.append(lid_id)

        return items

    def _draw_sparkle_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
        look_x: float,
        look_y: float,
    ) -> List[int]:
        """Draw an eye with sparkle/star highlight."""
        items = []

        # Main eye
        eye_id = canvas.create_oval(
            x - size + look_x, y - size + look_y,
            x + size + look_x, y + size + look_y,
            fill=self.EYE_COLOR,
            outline="",
        )
        items.append(eye_id)

        # Star-shaped highlight
        star_x = x - size * 0.25 + look_x
        star_y = y - size * 0.25 + look_y
        star_size = size * 0.4

        # Draw 4-pointed star
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            r = star_size if i % 2 == 0 else star_size * 0.4
            px = star_x + math.cos(angle) * r
            py = star_y + math.sin(angle) * r
            points.extend([px, py])

        star_id = canvas.create_polygon(
            points,
            fill=self.HIGHLIGHT_COLOR,
            outline="",
        )
        items.append(star_id)

        return items

    def _draw_angry_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
        side: int,
        look_x: float,
        look_y: float,
    ) -> List[int]:
        """Draw an angry eye with angled brow."""
        items = []

        # Main eye
        eye_id = canvas.create_oval(
            x - size + look_x, y - size + look_y,
            x + size + look_x, y + size + look_y,
            fill=self.EYE_COLOR,
            outline="",
        )
        items.append(eye_id)

        # Angry brow (angled line above eye)
        brow_y = y - size * 1.3
        inner_x = x + side * size * 0.3
        outer_x = x - side * size * 1.0
        brow_id = canvas.create_line(
            inner_x, brow_y + size * 0.3,
            outer_x, brow_y - size * 0.2,
            fill=self.EYE_COLOR,
            width=2,
            capstyle=tk.ROUND,
        )
        items.append(brow_id)

        return items

    def _draw_heart_eye(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        size: float,
    ) -> List[int]:
        """Draw a heart-shaped eye (love eyes)."""
        items = []

        # Simple heart using overlapping circles and triangle
        heart_color = "#FF6B8A"  # Pink-red

        # Top circles of heart
        c_size = size * 0.6
        left_id = canvas.create_oval(
            x - size * 0.8, y - size * 0.6,
            x, y + size * 0.2,
            fill=heart_color,
            outline="",
        )
        items.append(left_id)

        right_id = canvas.create_oval(
            x, y - size * 0.6,
            x + size * 0.8, y + size * 0.2,
            fill=heart_color,
            outline="",
        )
        items.append(right_id)

        # Bottom point of heart
        point_id = canvas.create_polygon(
            x - size * 0.7, y - size * 0.1,
            x + size * 0.7, y - size * 0.1,
            x, y + size * 0.8,
            fill=heart_color,
            outline="",
        )
        items.append(point_id)

        return items

    def draw_mouth(
        self,
        canvas: tk.Canvas,
        face_x: float,
        face_y: float,
        face_width: float,
        face_height: float,
        params: Optional[MouthParams] = None,
    ) -> List[int]:
        """
        Draw mouth on the blob face.

        Args:
            canvas: Tkinter canvas to draw on.
            face_x: Center X of face.
            face_y: Center Y of face.
            face_width: Width of face.
            face_height: Height of face.
            params: Mouth rendering parameters.

        Returns:
            List of canvas item IDs created.
        """
        params = params or MouthParams()
        items = []

        mouth_y = face_y + face_height * self.mouth_height
        mouth_width = self.base_mouth_width * params.width

        if params.emotion == MouthEmotion.NEUTRAL:
            items.extend(self._draw_neutral_mouth(canvas, face_x, mouth_y, mouth_width))

        elif params.emotion == MouthEmotion.HAPPY:
            items.extend(self._draw_happy_mouth(canvas, face_x, mouth_y, mouth_width))

        elif params.emotion == MouthEmotion.SAD:
            items.extend(self._draw_sad_mouth(canvas, face_x, mouth_y, mouth_width))

        elif params.emotion == MouthEmotion.OPEN:
            items.extend(self._draw_open_mouth(
                canvas, face_x, mouth_y, mouth_width, params.openness
            ))

        elif params.emotion == MouthEmotion.EATING:
            items.extend(self._draw_eating_mouth(
                canvas, face_x, mouth_y, mouth_width, params.openness
            ))

        elif params.emotion == MouthEmotion.YAWN:
            items.extend(self._draw_yawn_mouth(
                canvas, face_x, mouth_y, mouth_width, params.openness
            ))

        elif params.emotion == MouthEmotion.SMIRK:
            items.extend(self._draw_smirk_mouth(canvas, face_x, mouth_y, mouth_width))

        elif params.emotion == MouthEmotion.WORRIED:
            items.extend(self._draw_worried_mouth(canvas, face_x, mouth_y, mouth_width))

        return items

    def _draw_neutral_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
    ) -> List[int]:
        """Draw a neutral mouth (small horizontal line)."""
        items = []
        line_id = canvas.create_line(
            x - width * 0.3, y,
            x + width * 0.3, y,
            fill=self.MOUTH_COLOR,
            width=2,
            capstyle=tk.ROUND,
        )
        items.append(line_id)
        return items

    def _draw_happy_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
    ) -> List[int]:
        """Draw a happy smile (upward curve)."""
        items = []
        arc_id = canvas.create_arc(
            x - width, y - width * 0.8,
            x + width, y + width * 0.6,
            start=200, extent=140,
            style=tk.ARC,
            outline=self.MOUTH_COLOR,
            width=2,
        )
        items.append(arc_id)
        return items

    def _draw_sad_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
    ) -> List[int]:
        """Draw a sad frown (downward curve)."""
        items = []
        arc_id = canvas.create_arc(
            x - width * 0.8, y,
            x + width * 0.8, y + width,
            start=20, extent=140,
            style=tk.ARC,
            outline=self.MOUTH_COLOR,
            width=2,
        )
        items.append(arc_id)
        return items

    def _draw_open_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
        openness: float,
    ) -> List[int]:
        """Draw an open mouth (oval)."""
        items = []
        open_amt = max(0.3, openness) * width * 0.6
        mouth_id = canvas.create_oval(
            x - width * 0.5, y - open_amt * 0.3,
            x + width * 0.5, y + open_amt,
            fill="#3D3D3D",
            outline=self.MOUTH_COLOR,
            width=1,
        )
        items.append(mouth_id)
        return items

    def _draw_eating_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
        openness: float,
    ) -> List[int]:
        """Draw an eating/chomping mouth."""
        items = []
        # Animate between open and closed
        open_amt = abs(math.sin(openness * math.pi * 4)) * width * 0.5 + 3

        # Mouth opening
        mouth_id = canvas.create_oval(
            x - width * 0.6, y - open_amt * 0.3,
            x + width * 0.6, y + open_amt,
            fill=self.TONGUE_COLOR,
            outline=self.MOUTH_COLOR,
            width=2,
        )
        items.append(mouth_id)

        # Teeth marks when more closed
        if open_amt < width * 0.3:
            for i in range(3):
                tooth_x = x - width * 0.3 + i * width * 0.3
                tooth_id = canvas.create_line(
                    tooth_x, y - open_amt * 0.2,
                    tooth_x, y + open_amt * 0.2,
                    fill=Colors.WHITE,
                    width=2,
                )
                items.append(tooth_id)

        return items

    def _draw_yawn_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
        openness: float,
    ) -> List[int]:
        """Draw a yawning mouth (very wide oval)."""
        items = []
        open_amt = max(0.5, openness) * width * 0.8

        # Wide open mouth
        mouth_id = canvas.create_oval(
            x - width * 0.7, y - open_amt * 0.2,
            x + width * 0.7, y + open_amt,
            fill="#3D3D3D",
            outline=self.MOUTH_COLOR,
            width=2,
        )
        items.append(mouth_id)

        # Tongue at bottom
        tongue_id = canvas.create_oval(
            x - width * 0.3, y + open_amt * 0.3,
            x + width * 0.3, y + open_amt * 0.9,
            fill=self.TONGUE_COLOR,
            outline="",
        )
        items.append(tongue_id)

        return items

    def _draw_smirk_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
    ) -> List[int]:
        """Draw a smirk (asymmetric smile)."""
        items = []
        # Draw curve that goes up more on one side
        points = [
            x - width * 0.5, y + 2,
            x, y - 2,
            x + width * 0.5, y - 5,
        ]
        line_id = canvas.create_line(
            points,
            fill=self.MOUTH_COLOR,
            width=2,
            smooth=True,
            capstyle=tk.ROUND,
        )
        items.append(line_id)
        return items

    def _draw_worried_mouth(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
    ) -> List[int]:
        """Draw a worried wavy mouth."""
        items = []
        # Wavy line
        points = [
            x - width * 0.5, y + 2,
            x - width * 0.25, y - 2,
            x, y + 2,
            x + width * 0.25, y - 2,
            x + width * 0.5, y + 2,
        ]
        line_id = canvas.create_line(
            points,
            fill=self.MOUTH_COLOR,
            width=2,
            smooth=True,
            capstyle=tk.ROUND,
        )
        items.append(line_id)
        return items

    def draw_blush(
        self,
        canvas: tk.Canvas,
        face_x: float,
        face_y: float,
        face_width: float,
        face_height: float,
        intensity: float = 1.0,
    ) -> List[int]:
        """
        Draw blush marks on cheeks.

        Args:
            canvas: Tkinter canvas to draw on.
            face_x: Center X of face.
            face_y: Center Y of face.
            face_width: Width of face.
            face_height: Height of face.
            intensity: Blush intensity (0.0-1.0).

        Returns:
            List of canvas item IDs created.
        """
        items = []

        if intensity <= 0:
            return items

        blush_y = face_y + face_height * 0.05
        blush_offset = face_width * 0.3
        blush_w = face_width * 0.12
        blush_h = blush_w * 0.6

        # Adjust color based on intensity
        color = self.BLUSH_COLOR

        # Left blush
        left_id = canvas.create_oval(
            face_x - blush_offset - blush_w, blush_y - blush_h,
            face_x - blush_offset + blush_w, blush_y + blush_h,
            fill=color,
            outline="",
        )
        items.append(left_id)

        # Right blush
        right_id = canvas.create_oval(
            face_x + blush_offset - blush_w, blush_y - blush_h,
            face_x + blush_offset + blush_w, blush_y + blush_h,
            fill=color,
            outline="",
        )
        items.append(right_id)

        return items

    def draw_sweat_drop(
        self,
        canvas: tk.Canvas,
        face_x: float,
        face_y: float,
        face_width: float,
        face_height: float,
        side: int = 1,
    ) -> List[int]:
        """
        Draw a sweat drop for stress/hunger/tiredness.

        Args:
            canvas: Tkinter canvas to draw on.
            face_x: Center X of face.
            face_y: Center Y of face.
            face_width: Width of face.
            face_height: Height of face.
            side: Which side (-1 = left, 1 = right).

        Returns:
            List of canvas item IDs created.
        """
        items = []

        drop_x = face_x + side * face_width * 0.45
        drop_y = face_y - face_height * 0.2

        # Teardrop shape using polygon
        points = [
            drop_x, drop_y - 10,  # Top point
            drop_x - 5, drop_y,    # Left curve
            drop_x, drop_y + 5,    # Bottom
            drop_x + 5, drop_y,    # Right curve
        ]
        drop_id = canvas.create_polygon(
            points,
            fill=self.SWEAT_COLOR,
            outline=Colors.SOFT_BLUE,
            smooth=True,
        )
        items.append(drop_id)

        return items

    def clear(self, canvas: tk.Canvas) -> None:
        """Clear all canvas items created by this renderer."""
        for item_id in self._canvas_items:
            canvas.delete(item_id)
        self._canvas_items.clear()


def get_expression_for_mood(
    mood: str,
    is_hungry: bool = False,
    is_tired: bool = False,
) -> Tuple[EyeParams, MouthParams]:
    """
    Get expression parameters based on pet mood and status.

    Args:
        mood: Mood string (ecstatic, happy, content, neutral, sad, miserable).
        is_hungry: Whether pet is hungry.
        is_tired: Whether pet is tired.

    Returns:
        Tuple of (EyeParams, MouthParams) for the mood.
    """
    eye_params = EyeParams()
    mouth_params = MouthParams()

    if mood == "ecstatic":
        eye_params.emotion = EyeEmotion.SPARKLE
        mouth_params.emotion = MouthEmotion.HAPPY
        mouth_params.width = 1.3

    elif mood == "happy":
        eye_params.emotion = EyeEmotion.HAPPY
        mouth_params.emotion = MouthEmotion.HAPPY

    elif mood == "content":
        eye_params.emotion = EyeEmotion.NORMAL
        eye_params.highlight = True
        mouth_params.emotion = MouthEmotion.HAPPY
        mouth_params.width = 0.8

    elif mood == "neutral":
        eye_params.emotion = EyeEmotion.NORMAL
        mouth_params.emotion = MouthEmotion.NEUTRAL

    elif mood == "sad":
        eye_params.emotion = EyeEmotion.SAD
        mouth_params.emotion = MouthEmotion.SAD

    elif mood == "miserable":
        eye_params.emotion = EyeEmotion.SAD
        eye_params.openness = 0.7
        mouth_params.emotion = MouthEmotion.SAD
        mouth_params.width = 1.2

    # Override for status effects
    if is_tired:
        eye_params.emotion = EyeEmotion.SLEEPY
        eye_params.openness = 0.5

    if is_hungry:
        mouth_params.emotion = MouthEmotion.WORRIED

    return eye_params, mouth_params
