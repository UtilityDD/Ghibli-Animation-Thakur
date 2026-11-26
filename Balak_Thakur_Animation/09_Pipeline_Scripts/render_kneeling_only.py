"""
Rebuild THAKUR_KNEELING_V001 only.

Frames 0-35 are the sleeveless standing dhoti, shifted down as one sprite.
Frame 36 switches to the approved seated plate. The two bodies are never blended.
"""
import math

import numpy as np

from render_pilot_animations_1_to_3 import (
    PREVIEW_DIR, ease_in_out_cubic, alpha_composite_layer,
)
from render_locomotion import load_sari_front, shift_y
from render_emotional_category_f import load_expression, load_gesture, plate_for
from expand_gesture_library_part1_AB import save_animation_package

CANVAS = 768
TOTAL = 72
STAND_FRAMES = 36
MAX_SETTLE = 18.0
BREATH = 2.0
METHOD = "Method 1: Sleeveless dhoti, standing settle then seated plate, no blended bodies"


def opaque_rows(img: np.ndarray):
    ys = np.where(img[:, :, 3] > 40)[0]
    return int(ys.min()), int(ys.max())


def seated_plate() -> np.ndarray:
    """Approved seated figure: gentle smile on resting hands, same canvas placement as sitting clips."""
    expressions = {"02_gentle_smile": load_expression("02_gentle_smile")}
    gestures = {"08_resting_hands": load_gesture("08_resting_hands")}
    body = plate_for(expressions, gestures, "02_gentle_smile", "08_resting_hands")
    height, width, _ = body.shape
    ox = (CANVAS - width) // 2
    oy = (CANVAS - height) // 2 + 10
    canvas = np.zeros((CANVAS, CANVAS, 4), dtype=np.uint8)
    alpha_composite_layer(canvas, body, ox, oy)
    return canvas


def render_kneeling():
    standing = load_sari_front()
    seated = seated_plate()
    stand_top, stand_bottom = opaque_rows(standing)
    seat_top, seat_bottom = opaque_rows(seated)
    if stand_top < 0 or stand_bottom + int(MAX_SETTLE) >= CANVAS:
        raise RuntimeError(f"Standing feet leave the frame: y {stand_top}..{stand_bottom} plus {MAX_SETTLE}")
    if seat_top - int(BREATH) < 0 or seat_bottom + int(BREATH) >= CANVAS:
        raise RuntimeError(f"Seated breath leaves the frame: y {seat_top}..{seat_bottom}")

    frames = []
    for f in range(TOTAL):
        if f < STAND_FRAMES:
            u = ease_in_out_cubic(f / float(STAND_FRAMES - 1))
            frames.append(shift_y(standing, MAX_SETTLE * u))
        else:
            local = (f - STAND_FRAMES) / float(TOTAL - STAND_FRAMES)
            frames.append(shift_y(seated, BREATH * math.sin(2.0 * math.pi * local)))

    save_animation_package(
        "THAKUR_KNEELING_V001",
        "Sitting",
        "Kneeling Down Reverently",
        METHOD,
        frames,
        seamless_loop=True,
    )
    gif_path = PREVIEW_DIR / "GIF" / "THAKUR_KNEELING_V001.gif"
    print(f"GIF exists: {gif_path.exists()} {gif_path}")


if __name__ == "__main__":
    render_kneeling()
