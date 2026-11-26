"""
Walk, run, and standing clips from the painted locomotion plates.

The shawl is pulled toward the white of the seated sheet. Every pose
shares one foot line and stays inside the frame. The eye is not repainted.
"""
import math

import cv2
import numpy as np
from PIL import Image

from render_pilot_animations_1_to_3 import (
    BASE_DIR, LAYERS_DIR, ease_in_out_cubic, alpha_composite_layer,
)
from render_pilot_animations_3_to_5 import interpolate_flow_rgba
from expand_gesture_library_part1_AB import save_animation_package

CLOTH = np.array([248.0, 242.0, 228.0], dtype=np.float32)
CANVAS = 768
FOOT_Y = 690


def whiten_cloth(rgba: np.ndarray) -> np.ndarray:
    """Move the cream shawl toward the seated white. Skin, hair, and lines stay."""
    out = rgba.copy()
    rgb = out[:, :, :3].astype(np.float32)
    alpha = out[:, :, 3]
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = (red + green + blue) / 3.0
    skin = (red - blue > 55) & (gray > 70) & (gray < 220)
    cloth = (alpha > 40) & ~skin & (gray > 145)
    if int(cloth.sum()) < 50:
        return out
    med = np.median(rgb[cloth], axis=0)
    rgb[cloth] = np.clip(rgb[cloth] + (CLOTH - med) * 0.8, 0, 255)
    out[:, :, :3] = rgb.astype(np.uint8)
    return out


def _tight(rgba: np.ndarray) -> np.ndarray:
    ys, xs = np.where(rgba[:, :, 3] > 40)
    return rgba[int(ys.min()):int(ys.max()) + 1, int(xs.min()):int(xs.max()) + 1]


def _body_height(alpha: np.ndarray) -> int:
    height, width = alpha.shape
    col = alpha[:, int(width * 0.35):int(width * 0.65)] > 40
    ys = np.where(col.any(axis=1))[0]
    if len(ys) < 8:
        ys = np.where(alpha > 40)[0]
    return int(ys.max() - ys.min() + 1)


def _head_x(alpha: np.ndarray) -> float:
    height = alpha.shape[0]
    band = alpha[:max(8, int(height * 0.22)), :] > 40
    xs = np.where(band)[1]
    if len(xs) < 8:
        xs = np.where(alpha > 40)[1]
    return float(np.median(xs))


def place_pose(rgba: np.ndarray, target_h: float) -> np.ndarray:
    tight = _tight(rgba)
    scale = target_h / float(_body_height(tight[:, :, 3]))
    nw = max(1, int(round(tight.shape[1] * scale)))
    nh = max(1, int(round(tight.shape[0] * scale)))
    resized = np.array(Image.fromarray(tight, mode="RGBA").resize((nw, nh), Image.Resampling.LANCZOS))
    ox = int(round(CANVAS / 2.0 - _head_x(resized[:, :, 3])))
    oy = FOOT_Y - nh + 1
    canvas = np.zeros((CANVAS, CANVAS, 4), dtype=np.uint8)
    alpha_composite_layer(canvas, resized, ox, oy)
    return canvas


def fit_height(plates: list, desired: float = 520.0) -> float:
    """One height that keeps the widest pose inside the frame."""
    height = desired
    for _ in range(6):
        widest = 1.0
        for plate in plates:
            tight = _tight(plate)
            scale = height / float(_body_height(tight[:, :, 3]))
            widest = max(widest, tight.shape[1] * scale)
        if widest < CANVAS - 80:
            return height
        height *= (CANVAS - 80) / widest
    return height


def shift_y(img: np.ndarray, dy: float) -> np.ndarray:
    dy = int(round(dy))
    if dy == 0:
        return img
    out = np.zeros_like(img)
    if dy > 0:
        out[dy:] = img[:-dy]
    else:
        out[:dy] = img[-dy:]
    return out


def flow_cycle(poses: list, total: int, bounce: list) -> list:
    frames = []
    per = total // len(poses)
    for f in range(total):
        idx = (f // per) % len(poses)
        nxt = (idx + 1) % len(poses)
        local = ease_in_out_cubic((f % per) / float(per))
        cur = interpolate_flow_rgba(poses[idx], poses[nxt], local)
        su = ease_in_out_cubic(local)
        ty = bounce[idx] * (1.0 - su) + bounce[nxt] * su
        frames.append(shift_y(cur, ty))
    return frames


def load_prepared(names: list, height: float) -> list:
    plates = [whiten_cloth(np.array(Image.open(LAYERS_DIR / name).convert("RGBA"))) for name in names]
    height = fit_height(plates, height)
    return [place_pose(plate, height) for plate in plates]


def load_sari_front(height: float = 540.0) -> np.ndarray:
    """Standing front in the sleeveless dhoti, the same cloth covering part of the chest."""
    plate = np.array(Image.open(LAYERS_DIR / "body_standing_dhoti_sari_front.png").convert("RGBA"))
    return place_pose(plate, fit_height([plate], height))


def render_locomotion(plates_only: bool = False):
    walk = load_prepared([f"walk_keypose_{i:02d}.png" for i in range(1, 9)], 520)
    run = load_prepared([f"run_keypose_{i:02d}.png" for i in range(1, 9)], 500)
    standing_names = [
        "body_full_front.png",
        "body_full_three_quarter_front.png",
        "body_full_right_profile.png",
        "body_full_rear.png",
        "body_full_left_profile.png",
    ]
    standing = load_prepared(standing_names, 540)
    front, three_q, right, rear, left = standing

    board = Image.new("RGB", (5 * 150, 3 * 160), (28, 24, 22))
    thumbs = standing + [walk[0], walk[2], walk[4], run[0], run[2]]
    for i, plate in enumerate(thumbs):
        r, c = divmod(i, 5)
        rgb = np.full(plate.shape[:2] + (3,), 236, np.uint8)
        af = plate[:, :, 3].astype(np.float32) / 255.0
        for ch in range(3):
            rgb[:, :, ch] = (plate[:, :, ch] * af + rgb[:, :, ch] * (1.0 - af)).astype(np.uint8)
        im = Image.fromarray(rgb).resize((140, 150))
        board.paste(im, (8 + c * 150, 8 + r * 160))
    board_path = BASE_DIR / "07_Production_Tests" / "Locomotion_Plate_Check.png"
    board.save(board_path)
    print(f"Plate check written to {board_path}")
    if plates_only:
        return

    method = "Method 1: Painted locomotion plates, white shawl, one foot line"
    sari_method = "Method 1: Sleeveless dhoti worn like a sari, cloth across the chest, bare arms"
    sari_front = load_sari_front(540)
    walk_bounce = [0.0, 8.0, -2.0, -6.0, 0.0, 8.0, -2.0, -6.0]
    run_bounce = [0.0, 6.0, -10.0, -4.0, 0.0, 6.0, -10.0, -4.0]

    standing_jobs = [
        ("THAKUR_STANDING_IDLE_V001", "Walking", "Standing Idle with Natural Breathing",
         sari_method,
         [shift_y(sari_front, -2.2 * math.sin(2.0 * math.pi * f / 72.0)) for f in range(72)]),
        ("THAKUR_MOVING_FORWARD_BACKWARD_V001", "Walking", "Moving Forward and Backward",
         sari_method, _forward_back(sari_front)),
    ]
    if plates_only:
        return
    import sys
    if "--standing" in sys.argv:
        jobs = standing_jobs
    else:
        jobs = standing_jobs + [
        ("THAKUR_WALK_CYCLE_V001", "Walking", "Natural Child Walk Cycle", method,
         flow_cycle(walk, 48, walk_bounce)),
        ("THAKUR_WALK_SLOW_CYCLE_V001", "Walking", "Walking Slowly", method,
         flow_cycle(walk, 72, [v * 0.7 for v in walk_bounce])),
        ("THAKUR_RUN_CYCLE_V001", "Running", "Natural Child Run Cycle", method,
         flow_cycle(run, 32, run_bounce)),
        ("THAKUR_TURN_AROUND_V001", "Walking", "Turning Around", method,
         _turn(standing + [front])),
        ("THAKUR_JUMP_V001", "Running", "Joyful Child Jump", method,
         _jump(right, run)),
        ]
    for asset_id, category, title, job_method, frames in jobs:
        print(f"Rendering {asset_id}")
        save_animation_package(asset_id, category, title, job_method, frames, seamless_loop=True)
        print(f"Finished {asset_id}")


def _turn(views: list, frames_per: int = 24) -> list:
    frames = []
    segments = len(views) - 1
    for f in range(frames_per * segments):
        seg = min(segments - 1, f // frames_per)
        local = (f % frames_per) / float(frames_per)
        frames.append(interpolate_flow_rgba(views[seg], views[seg + 1], local))
    return frames


def _forward_back(front: np.ndarray) -> list:
    frames = []
    for f in range(60):
        phase = 2.0 * math.pi * f / 60.0
        depth = 0.5 - 0.5 * math.cos(phase)
        scale = 1.0 + 0.06 * depth
        resized = cv2.resize(front, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        canvas = np.zeros_like(front)
        oy = FOOT_Y - int(np.where(resized[:, :, 3] > 40)[0].max())
        ox = (CANVAS - resized.shape[1]) // 2
        alpha_composite_layer(canvas, resized, ox, oy + int(round(-5.0 * abs(math.sin(2.0 * math.pi * f / 15.0)))))
        frames.append(canvas)
    return frames


def _jump(stand: np.ndarray, run: list, total: int = 72) -> list:
    keys = [stand, run[1], run[2], run[3], run[1], stand]
    bounds = [int(round(v * total / 48.0)) for v in (0, 10, 16, 25, 35, 48)]
    bounds[-1] = total
    heights = [0.0, 18.0, -16.0, -56.0, 16.0, 0.0]
    frames = []
    for f in range(total):
        seg = 0
        for i in range(len(bounds) - 1):
            if bounds[i] <= f < bounds[i + 1]:
                seg = i
                break
        span = bounds[seg + 1] - bounds[seg]
        local = (f - bounds[seg]) / float(span)
        su = ease_in_out_cubic(local)
        cur = interpolate_flow_rgba(keys[seg], keys[seg + 1], local)
        ty = heights[seg] * (1.0 - su) + heights[seg + 1] * su
        frames.append(shift_y(cur, ty))
    return frames


def _prepared(names: list, height: float) -> list:
    plates = [np.array(Image.open(LAYERS_DIR / name).convert("RGBA")) for name in names]
    height = fit_height(plates, height)
    return [place_pose(plate, height) for plate in plates]


def render_sari_cycles():
    """Walk, run, turn, and jump in the same sleeveless dhoti."""
    turn = _prepared([
        "body_standing_dhoti_sari_front.png",
        "body_standing_dhoti_sari_three_quarter.png",
        "body_standing_dhoti_sari_right.png",
        "body_standing_dhoti_sari_rear.png",
        "body_standing_dhoti_sari_left.png",
    ], 520)
    walk = _prepared([f"walk_sari_{i:02d}.png" for i in range(1, 9)], 500)
    run = _prepared(["run_sari_01.png", "run_sari_03.png", "run_sari_05.png", "run_sari_07.png"], 470)
    method = "Method 1: Sleeveless dhoti worn like a sari, cloth across the chest, bare arms"
    front, _three_q, right, _rear, _left = turn
    jobs = [
        ("THAKUR_WALK_CYCLE_V001", "Walking", "Natural Child Walk Cycle",
         flow_cycle(walk, 96, [0.0, 8.0, -2.0, -6.0, 0.0, 8.0, -2.0, -6.0])),
        ("THAKUR_WALK_SLOW_CYCLE_V001", "Walking", "Walking Slowly",
         flow_cycle(walk, 144, [0.0, 5.6, -1.4, -4.2, 0.0, 5.6, -1.4, -4.2])),
        ("THAKUR_RUN_CYCLE_V001", "Running", "Natural Child Run Cycle",
         flow_cycle(run, 64, [0.0, -8.0, 4.0, -6.0])),
        ("THAKUR_TURN_AROUND_V001", "Walking", "Turning Around",
         _turn(turn + [front], frames_per=24)),
        ("THAKUR_JUMP_V001", "Running", "Joyful Child Jump",
         _jump(right, run, total=72)),
    ]
    for asset_id, category, title, frames in jobs:
        print(f"Rendering {asset_id}")
        save_animation_package(asset_id, category, title, method, frames, seamless_loop=True)
        print(f"Finished {asset_id}")


if __name__ == "__main__":
    import sys
    if "--cycles" in sys.argv:
        render_sari_cycles()
    else:
        render_locomotion(plates_only="--plates" in sys.argv)
