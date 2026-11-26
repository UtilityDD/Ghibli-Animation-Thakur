"""
Category F — Emotional storytelling (8 clips, 72 frames @ 24 FPS).

Each clip is one continuous seated figure from the full-body hand sheet.
The painted expression is placed on that figure as one face oval, aligned
to the eye line. The shawl, hands, lap, and feet stay the sheet figure.
Two expressions are never averaged together. Face and hands share one
optical-flow transition.
"""
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from render_pilot_animations_1_to_3 import (
    BASE_DIR, LAYERS_DIR, ease_in_out_cubic, alpha_composite_layer,
)
from render_pilot_animations_3_to_5 import interpolate_flow_rgba
from expand_gesture_library_part1_AB import save_animation_package
from test_fix_single_animation import (
    apply_natural_eyelid_blink_and_smile, deform_unified_character_mesh,
)


EXPRESSIONS = [
    "01_neutral", "02_gentle_smile", "03_broad_smile", "04_laughing",
    "05_surprised", "06_curious", "07_angry", "08_sad",
    "09_crying", "10_peaceful", "11_thoughtful", "12_determined",
]

# Face plate, hand gesture, and how the head settles while the gesture is held.
# pitch > 0 bows the head; pitch < 0 lifts it. Angles stay small so the
# cervical falloff does not kink the neck.
CLIPS = [
    {
        "asset_id": "THAKUR_EMOTIONAL_BECOMING_ANGRY_V001",
        "title": "Becoming Firmly Angry",
        "start_face": "02_gentle_smile",
        "end_face": "07_angry",
        "end_gesture": "02_folded_hands",
        "pitch": 1.6,
        "roll": 0.0,
        "yaw": 0.0,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_BECOMING_HAPPY_V001",
        "title": "Becoming Radiantly Happy",
        "start_face": "01_neutral",
        "end_face": "03_broad_smile",
        "end_gesture": "06_open_palm",
        "pitch": -1.2,
        "roll": 0.8,
        "yaw": 0.0,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_EXPRESSING_WONDER_V001",
        "title": "Expressing Childlike Wonder",
        "start_face": "02_gentle_smile",
        "end_face": "06_curious",
        "end_gesture": "07_holding_object",
        "pitch": -2.4,
        "roll": 0.6,
        "yaw": 0.4,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_LAUGHING_NATURALLY_V001",
        "title": "Laughing Naturally",
        "start_face": "03_broad_smile",
        "end_face": "04_laughing",
        "end_gesture": "08_resting_hands",
        "pitch": -0.6,
        "roll": 0.4,
        "yaw": 0.0,
        "blink": False,
        "chuckle": True,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_BECOMING_EMOTIONAL_V001",
        "title": "Becoming Moved with Compassion",
        "start_face": "10_peaceful",
        "end_face": "09_crying",
        "end_gesture": "01_namaskar",
        "pitch": 2.4,
        "roll": -0.4,
        "yaw": 0.0,
        "blink": False,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_SHOWING_CONCERN_V001",
        "title": "Showing Concern",
        "start_face": "02_gentle_smile",
        "end_face": "08_sad",
        "end_gesture": "06_open_palm",
        "pitch": 1.8,
        "roll": -1.0,
        "yaw": 0.6,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_COMFORTING_SOMEONE_V001",
        "title": "Comforting Someone",
        "start_face": "08_sad",
        "end_face": "02_gentle_smile",
        "end_gesture": "03_blessing",
        "pitch": 0.8,
        "roll": 0.6,
        "yaw": 0.0,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_EMOTIONAL_EXPRESSING_DETERMINATION_V001",
        "title": "Expressing Quiet Determination",
        "start_face": "11_thoughtful",
        "end_face": "12_determined",
        "end_gesture": "02_folded_hands",
        "pitch": 0.6,
        "roll": 0.0,
        "yaw": 0.0,
        "blink": True,
    },
]


def load_expression(name: str) -> np.ndarray:
    return np.array(Image.open(LAYERS_DIR / f"registered_seated_{name}.png").convert("RGBA"))


def load_gesture(name: str) -> np.ndarray:
    return np.array(Image.open(LAYERS_DIR / f"registered_gesture_{name}.png").convert("RGBA"))


def _eye_point(rgba: np.ndarray):
    """Eye line inside the head. Both plates share this canvas, so the shift stays small."""
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    band = gray[140:195, 270:370]
    scores = []
    for row in band:
        dark = row[row < 115]
        scores.append(float(dark.mean()) if len(dark) > 5 else 255.0)
    eye_y = 140 + int(np.argmin(scores))
    row = gray[eye_y, 250:400]
    xs = np.where(row < 115)[0]
    eye_x = 250.0 + float(np.median(xs)) if len(xs) else 318.0
    return eye_x, float(eye_y)


def _skin_mask(rgb: np.ndarray) -> np.ndarray:
    red = rgb[:, :, 0].astype(np.int16)
    green = rgb[:, :, 1].astype(np.int16)
    blue = rgb[:, :, 2].astype(np.int16)
    gray = (red + green + blue) // 3
    return (red - blue > 35) & (gray > 85) & (gray < 225)


def paint_expression_onto_body(body: np.ndarray, expression: np.ndarray) -> np.ndarray:
    """Painted face on the sheet figure, recolored to that figure's skin."""
    body_x, body_y = _eye_point(body)
    expr_x, expr_y = _eye_point(expression)
    dx = int(round(body_x - expr_x))
    dy = int(round(body_y - expr_y))
    height, width = body.shape[:2]
    shifted = np.zeros_like(expression)
    src_x0, dst_x0 = max(0, -dx), max(0, dx)
    src_y0, dst_y0 = max(0, -dy), max(0, dy)
    src_x1, dst_x1 = width - max(0, dx), width - max(0, -dx)
    src_y1, dst_y1 = height - max(0, dy), height - max(0, -dy)
    shifted[dst_y0:dst_y1, dst_x0:dst_x1] = expression[src_y0:src_y1, src_x0:src_x1]

    yy, xx = np.mgrid[0:height, 0:width]
    center_y = body_y + 22.0
    norm = ((xx - body_x) / 62.0) ** 2 + ((yy - center_y) / 78.0) ** 2
    on_body = body[:, :, 3] > 40
    oval = (norm <= 1.0) & on_body
    # Eyes, mouth, and tears stay. The dark jaw line of the expression plate does not.
    inner = (norm <= 0.72 ** 2) & on_body
    expr_rgb = shifted[:, :, :3]
    body_rgb = body[:, :, :3]
    expr_skin = oval & _skin_mask(expr_rgb)
    body_skin = oval & _skin_mask(body_rgb)
    if int(expr_skin.sum()) > 50 and int(body_skin.sum()) > 50:
        expr_med = np.median(expr_rgb[expr_skin], axis=0).astype(np.float32)
        body_med = np.median(body_rgb[body_skin], axis=0).astype(np.float32)
        corrected = expr_rgb.astype(np.float32).copy()
        corrected[expr_skin] = np.clip(
            body_med + (expr_rgb[expr_skin].astype(np.float32) - expr_med) * 0.4,
            0, 255,
        )
    else:
        corrected = expr_rgb.astype(np.float32)
    use = inner | (oval & _skin_mask(corrected.astype(np.uint8)))
    soft = cv2.GaussianBlur(use.astype(np.uint8) * 255, (0, 0), 2.6).astype(np.float32) / 255.0
    painted = body.copy()
    for channel in range(3):
        painted[:, :, channel] = np.clip(
            body[:, :, channel] * (1.0 - soft) + corrected[:, :, channel] * soft,
            0, 255,
        ).astype(np.uint8)
    return painted


def snap_disputed_parts(start: np.ndarray, active: np.ndarray, blended: np.ndarray, u: float) -> np.ndarray:
    """Keep one pair of hands. Pixels that differ between the two poses are not averaged."""
    if u <= 0.001:
        return start.copy()
    if u >= 0.999:
        return active.copy()
    diff = np.abs(start[:, :, :3].astype(np.int16) - active[:, :, :3].astype(np.int16)).sum(axis=2)
    alpha_diff = np.abs(start[:, :, 3].astype(np.int16) - active[:, :, 3].astype(np.int16))
    dispute = (diff > 90) | (alpha_diff > 40)
    winner = active if u >= 0.5 else start
    out = blended.copy()
    out[dispute] = winner[dispute]
    return out


def stamp_one_face(body: np.ndarray, source: np.ndarray) -> np.ndarray:
    """Replace the blended face with one painted face, so two eyes cannot show at once."""
    eye_x, eye_y = _eye_point(source)
    height, width = body.shape[:2]
    yy, xx = np.mgrid[0:height, 0:width]
    norm = ((xx - eye_x) / 66.0) ** 2 + ((yy - (eye_y + 18.0)) / 82.0) ** 2
    oval = (norm <= 1.0) & (source[:, :, 3] > 40)
    soft = cv2.GaussianBlur(oval.astype(np.uint8) * 255, (0, 0), 1.4).astype(np.float32) / 255.0
    soft = np.where((norm <= 0.82 ** 2) & oval, 1.0, soft)
    painted = body.copy()
    for channel in range(3):
        painted[:, :, channel] = np.clip(
            body[:, :, channel] * (1.0 - soft) + source[:, :, channel] * soft,
            0, 255,
        ).astype(np.uint8)
    return painted


def plate_for(expressions: dict, gestures: dict, face: str, gesture: str) -> np.ndarray:
    """Full-body hand-sheet figure, with the painted expression on the face."""
    return paint_expression_onto_body(gestures[gesture], expressions[face])


def env_hold(f: int, total: int = 72, ramp: int = 16) -> float:
    if f < ramp:
        return ease_in_out_cubic(f / float(ramp))
    if f < total - ramp:
        return 1.0
    return 1.0 - ease_in_out_cubic((f - (total - ramp)) / float(ramp))


def save_plate_board(pairs: list, path: Path):
    thumb_w, thumb_h = 220, 234
    label_h = 36
    cols = 4
    rows = 4
    board = Image.new("RGB", (cols * thumb_w + 24, rows * (thumb_h + label_h) + 56), (28, 24, 22))
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 13)
    draw.text((16, 14), "Emotional plates — start, then the held pose", font=font, fill=(255, 220, 150))
    for i, (label, plate) in enumerate(pairs):
        r, c = divmod(i, cols)
        x0 = 12 + c * thumb_w
        y0 = 44 + r * (thumb_h + label_h)
        im = Image.fromarray(plate, mode="RGBA")
        im.thumbnail((thumb_w - 8, thumb_h - 4), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", (thumb_w - 8, thumb_h - 4), (236, 230, 218, 255))
        bg.alpha_composite(im, ((bg.width - im.width) // 2, (bg.height - im.height) // 2))
        board.paste(bg.convert("RGB"), (x0, y0))
        draw.text((x0, y0 + thumb_h - 2), label[:32], font=font, fill=(245, 230, 190))
    path.parent.mkdir(parents=True, exist_ok=True)
    board.save(path)


def render_emotional_category_f(plates_only: bool = False, only: str = None):
    expressions = {name: load_expression(name) for name in EXPRESSIONS}
    gestures = {
        "01_namaskar": load_gesture("01_namaskar"),
        "02_folded_hands": load_gesture("02_folded_hands"),
        "03_blessing": load_gesture("03_blessing"),
        "06_open_palm": load_gesture("06_open_palm"),
        "07_holding_object": load_gesture("07_holding_object"),
        "08_resting_hands": load_gesture("08_resting_hands"),
    }
    nh, nw, _ = gestures["08_resting_hands"].shape
    canvas_w, canvas_h = 768, 768
    ox = (canvas_w - nw) // 2
    oy = (canvas_h - nh) // 2 + 10

    built = []
    for clip in CLIPS:
        start = plate_for(expressions, gestures, clip["start_face"], "08_resting_hands")
        active = plate_for(expressions, gestures, clip["end_face"], clip["end_gesture"])
        if start.shape != active.shape:
            raise RuntimeError(f"{clip['asset_id']} plate shapes differ: {start.shape} vs {active.shape}")
        built.append((clip, start, active))

    board_pairs = []
    for clip, start, active in built:
        short = clip["asset_id"].replace("THAKUR_EMOTIONAL_", "").replace("_V001", "")
        board_pairs.append((f"{short} start", start))
        board_pairs.append((f"{short} hold", active))
    board_path = BASE_DIR / "07_Production_Tests" / "Emotional_F_Plate_Check.png"
    save_plate_board(board_pairs, board_path)
    print(f"Plate check written to {board_path}")
    if plates_only:
        return

    early_blink = {4: 0.25, 5: 0.75, 6: 1.0, 7: 0.55, 8: 0.15}
    flow_steps = 24

    for clip, start, active in built:
        if only and clip["asset_id"] != only:
            continue
        print(f"Rendering {clip['asset_id']}")
        cached = [
            interpolate_flow_rgba(start, active, i / float(flow_steps))
            for i in range(flow_steps + 1)
        ]
        frames = []
        total = 96
        for f in range(total):
            phase = 2.0 * math.pi * f / float(total)
            cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total))
            u = env_hold(f, total, 24)

            f_idx = u * flow_steps
            i0 = int(math.floor(f_idx))
            i1 = min(flow_steps, i0 + 1)
            frac = f_idx - i0
            if frac <= 0.001 or i0 == i1:
                cur = cached[i0].copy()
            else:
                cur = np.clip(
                    cached[i0].astype(np.float32) * (1.0 - frac)
                    + cached[i1].astype(np.float32) * frac,
                    0, 255,
                ).astype(np.uint8)

            cur = snap_disputed_parts(start, active, cur, u)
            cur = stamp_one_face(cur, active if u >= 0.5 else start)

            if clip["blink"]:
                b_val = early_blink.get(f, 0.0)
                if b_val > 0.01 and u < 0.45:
                    cur = apply_natural_eyelid_blink_and_smile(cur, b_val, 0.0)

            deformed = deform_unified_character_mesh(
                cur,
                head_pitch_deg=clip["pitch"] * u,
                head_yaw_deg=clip["yaw"] * u,
                head_roll_deg=clip["roll"] * u,
                breath_phase=phase,
                cloth_phase=cloth_phase,
            )
            chuckle = 0
            if clip.get("chuckle"):
                chuckle = int(round(-2.2 * abs(math.sin(2.0 * math.pi * f / 8.0)) * u))

            canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
            alpha_composite_layer(canv, deformed, ox, oy + chuckle)
            frames.append(canv)

        save_animation_package(
            clip["asset_id"], "Emotional", clip["title"],
            "Method 1: Full-body hand sheet with the painted expression on one face oval",
            frames, seamless_loop=True,
        )


if __name__ == "__main__":
    import sys
    chosen = None
    if "--only" in sys.argv:
        chosen = sys.argv[sys.argv.index("--only") + 1]
    render_emotional_category_f(plates_only="--plates" in sys.argv, only=chosen)
