"""
THAKUR_SITTING_DOWN_V001 and THAKUR_STANDING_UP_V001 only.

The standing drawing and the seated drawing are never optical-flowed
or crossfaded. Sitting down eases the standing plate toward the floor,
then cuts to the seated plate. Standing up is that clip reversed.
"""
import math

import numpy as np
from PIL import Image

from render_pilot_animations_1_to_3 import (
    LAYERS_DIR, GESTURE_DIR, PREVIEW_DIR, ease_in_out_cubic, alpha_composite_layer,
)
from expand_gesture_library_part1_AB import save_animation_package
from render_emotional_category_f import plate_for, load_expression, load_gesture
from render_locomotion import place_pose, fit_height, shift_y, FOOT_Y, CANVAS

TOTAL = 72
HALF = 36
SETTLE_PX = 18.0
BREATH_PX = 2.0
METHOD = "Method 1: Sleeveless dhoti, standing settle then seated plate, no blended bodies"

SIT_ID = "THAKUR_SITTING_DOWN_V001"
STAND_ID = "THAKUR_STANDING_UP_V001"


def load_standing() -> np.ndarray:
    """Sleeveless dhoti front view on a 768 canvas, feet on the shared foot line."""
    plate = np.array(Image.open(LAYERS_DIR / "body_standing_dhoti_sari_front.png").convert("RGBA"))
    placed = place_pose(plate, fit_height([plate], 540.0))
    if placed.shape != (CANVAS, CANVAS, 4):
        raise RuntimeError(f"standing plate is {placed.shape}, expected {(CANVAS, CANVAS, 4)}")
    foot = _foot_row(placed)
    if foot != FOOT_Y:
        raise RuntimeError(f"standing feet land on row {foot}, expected foot line {FOOT_Y}")
    if foot + int(SETTLE_PX) >= CANVAS:
        raise RuntimeError("18 px settle would push the standing feet out of the frame")
    return placed


def load_seated() -> np.ndarray:
    """Gentle smile on the resting-hands sheet, centered on the 768 canvas."""
    expressions = {"02_gentle_smile": load_expression("02_gentle_smile")}
    gestures = {"08_resting_hands": load_gesture("08_resting_hands")}
    plate = plate_for(expressions, gestures, "02_gentle_smile", "08_resting_hands")
    nh, nw, _ = plate.shape
    canvas = np.zeros((CANVAS, CANVAS, 4), dtype=np.uint8)
    ox = (CANVAS - nw) // 2
    oy = (CANVAS - nh) // 2 + 10
    alpha_composite_layer(canvas, plate, ox, oy)
    if _foot_row(canvas) + int(BREATH_PX) >= CANVAS:
        raise RuntimeError("seated breath would push the feet out of the frame")
    return canvas


def _foot_row(img: np.ndarray) -> int:
    ys = np.where(img[:, :, 3] > 40)[0]
    if len(ys) == 0:
        raise RuntimeError("plate has no opaque pixels")
    return int(ys.max())


def _sitting_down(standing: np.ndarray, seated: np.ndarray) -> list:
    frames = []
    for f in range(TOTAL):
        if f < HALF:
            u = ease_in_out_cubic(f / float(HALF - 1))
            frames.append(shift_y(standing, SETTLE_PX * u))
        else:
            breath = BREATH_PX * math.sin(2.0 * math.pi * (f - HALF) / float(HALF))
            frames.append(shift_y(seated, breath))
    return frames


def _assert_unblended(frames: list, standing: np.ndarray, seated: np.ndarray):
    """Frames 0-35 are only the standing plate. Frames 36-71 are only the seated plate."""
    for f in range(HALF):
        u = ease_in_out_cubic(f / float(HALF - 1))
        dy = int(round(SETTLE_PX * u))
        expect = shift_y(standing, dy)
        if frames[f] is not expect and not np.array_equal(frames[f], expect):
            raise RuntimeError(f"sitting frame {f} is not the standing plate")
        if _foot_row(frames[f]) != FOOT_Y + dy:
            raise RuntimeError(f"sitting frame {f} feet leave the foot line")
    for f in range(HALF, TOTAL):
        breath = BREATH_PX * math.sin(2.0 * math.pi * (f - HALF) / float(HALF))
        expect = shift_y(seated, breath)
        if frames[f] is not expect and not np.array_equal(frames[f], expect):
            raise RuntimeError(f"sitting frame {f} is not the seated plate")
    # The cut is two drawings, not a dissolve.
    jump = np.abs(frames[HALF - 1].astype(np.int16) - frames[HALF].astype(np.int16)).mean()
    if jump < 8.0:
        raise RuntimeError("standing and seated plates look crossfaded at the cut")


def _clear_frames(asset_id: str):
    frames_dir = GESTURE_DIR / "Sitting" / asset_id / "frames"
    if not frames_dir.exists():
        return
    for path in frames_dir.glob("*.png"):
        path.unlink()


def render_sit_stand():
    standing = load_standing()
    seated = load_seated()
    sitting = _sitting_down(standing, seated)
    # Standing up is the reverse: seated plate, then the standing plate rises to the foot line.
    standing_up = list(reversed(sitting))
    _assert_unblended(sitting, standing, seated)
    if len(sitting) != TOTAL or len(standing_up) != TOTAL:
        raise RuntimeError("expected 72 frames in each clip")
    if _foot_row(standing_up[-1]) != FOOT_Y:
        raise RuntimeError("standing up does not finish on the foot line")

    jobs = (
        (SIT_ID, "Sitting Down from Standing into Cross-Legged Sukhasana", sitting),
        (STAND_ID, "Standing Up from Cross-Legged Sukhasana to Standing Pose", standing_up),
    )
    for asset_id, title, frames in jobs:
        _clear_frames(asset_id)
        save_animation_package(asset_id, "Sitting", title, METHOD, frames, seamless_loop=False)
        gif = PREVIEW_DIR / "GIF" / f"{asset_id}.gif"
        if not gif.is_file():
            raise RuntimeError(f"missing preview gif: {gif}")
        print(f"GIF exists: {gif}")


if __name__ == "__main__":
    render_sit_stand()
