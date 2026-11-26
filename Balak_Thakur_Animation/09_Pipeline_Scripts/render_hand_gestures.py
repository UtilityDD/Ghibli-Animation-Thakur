"""
Category C — 10 hand gestures taken from the full-body hand sheet.

Each pose is the whole seated figure from THAKUR_HAND_GESTURE_SHEET_V001.png.
The figure is scaled as one piece so the head, shawl, and lap stay in line,
then placed on the same foot line as the master seated plate.
"""
import math

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

from render_pilot_animations_1_to_3 import (
    BASE_DIR, ease_in_out_cubic, alpha_composite_layer,
)
from render_pilot_animations_3_to_5 import interpolate_flow_rgba
from expand_gesture_library_part1_AB import save_animation_package
from test_fix_single_animation import deform_unified_character_mesh
from calibrate_registered_gestures import LAYERS_DIR


GESTURES = [
    ("01_namaskar", "THAKUR_HANDS_NAMASKAR_V001", "Traditional Namaskar Anjali Mudra",
     lambda f, tf, ph, u: dict(pitch=2.2 * u, yaw=0.0, roll=0.0)),
    ("02_folded_hands", "THAKUR_HANDS_FOLDING_V001", "Folding Hands Gently Across the Lap",
     lambda f, tf, ph, u: dict(pitch=1.2 * u, yaw=0.0, roll=0.4 * math.sin(ph) * u)),
    ("05_waving", "THAKUR_HANDS_WAVING_V001", "Friendly Child Waving Gesture",
     lambda f, tf, ph, u: dict(pitch=-0.8 * u, yaw=1.2 * u, roll=1.4 * u)),
    ("04_pointing", "THAKUR_HANDS_POINTING_V001", "Pointing Gently",
     lambda f, tf, ph, u: dict(pitch=-1.0 * u, yaw=1.6 * u, roll=1.2 * u)),
    ("06_open_palm", "THAKUR_HANDS_EXPLAINING_V001", "Explaining with Open Palms",
     lambda f, tf, ph, u: dict(pitch=0.6 * math.sin(ph) * u, yaw=0.8 * math.sin(ph) * u, roll=0.8 * u)),
    ("03_blessing", "THAKUR_HANDS_RAISING_BLESSING_V001", "Raising One Hand in Blessing",
     lambda f, tf, ph, u: dict(pitch=0.8 * u, yaw=0.0, roll=0.4 * math.sin(ph) * u)),
    ("08_resting_hands", "THAKUR_HANDS_RESTING_V001", "Resting Hands on the Lap",
     lambda f, tf, ph, u: dict(pitch=0.4 * math.sin(ph), yaw=0.0, roll=0.3 * math.sin(ph))),
    ("06_open_palm", "THAKUR_HANDS_EXPRESSING_SURPRISE_V001", "Surprise with Open Hands",
     lambda f, tf, ph, u: dict(pitch=-1.6 * u, yaw=0.0, roll=0.5 * math.sin(ph) * u)),
    ("07_holding_object", "THAKUR_HANDS_PLEADING_V001", "Offering with Both Hands",
     lambda f, tf, ph, u: dict(pitch=1.6 * u, yaw=0.0, roll=-0.8 * u)),
    ("01_namaskar", "THAKUR_HANDS_GREETING_V001", "Namaskar Greeting with a Small Bow",
     lambda f, tf, ph, u: dict(pitch=3.2 * u, yaw=0.0, roll=0.0)),
]


def env_hold(f, total=60, ramp=14):
    if f < ramp:
        return ease_in_out_cubic(f / float(ramp))
    if f < total - ramp:
        return 1.0
    return 1.0 - ease_in_out_cubic((f - (total - ramp)) / float(ramp))


def render_one(asset_id, title, start, active, motion_fn, total=96):
    flow_steps = 24
    cached = [interpolate_flow_rgba(start, active, i / float(flow_steps)) for i in range(flow_steps + 1)]
    nh, nw, _ = start.shape
    ox = (768 - nw) // 2
    oy = (768 - nh) // 2 + 10
    frames = []
    for f in range(total):
        phase = 2.0 * math.pi * f / float(total)
        cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total))
        u = 0.0 if asset_id.endswith("RESTING_V001") else env_hold(f, total, 24)
        f_idx = u * flow_steps
        i0 = int(math.floor(f_idx))
        i1 = min(flow_steps, i0 + 1)
        frac = f_idx - i0
        if frac <= 0.001 or i0 == i1:
            cur = cached[i0].copy()
        else:
            cur = np.clip(
                cached[i0].astype(np.float32) * (1.0 - frac) + cached[i1].astype(np.float32) * frac,
                0, 255,
            ).astype(np.uint8)
        move = motion_fn(f, total, phase, u)
        deformed = deform_unified_character_mesh(
            cur,
            head_pitch_deg=move["pitch"],
            head_yaw_deg=move["yaw"],
            head_roll_deg=move["roll"],
            breath_phase=phase,
            cloth_phase=cloth_phase,
        )
        canv = np.zeros((768, 768, 4), dtype=np.uint8)
        alpha_composite_layer(canv, deformed, ox, oy)
        frames.append(canv)
    save_animation_package(
        asset_id, "Hands", title,
        "Method 1: Full-body hand sheet, one figure on the master foot line, one cervical mesh",
        frames, seamless_loop=True,
    )


def _body_span(alpha: np.ndarray):
    """Crown and feet from the center of the body, so a raised hand does not change the scale."""
    h, w = alpha.shape
    col = alpha[:, int(w * 0.35):int(w * 0.65)] > 40
    ys = np.where(col.any(axis=1))[0]
    if len(ys) < 10:
        ys = np.where(alpha > 40)[0]
    return int(ys.min()), int(ys.max())


def _head_center_x(alpha: np.ndarray) -> float:
    """Horizontal center of the head, so a raised arm does not slide the body sideways."""
    h, w = alpha.shape
    band = alpha[:max(8, int(h * 0.22)), :] > 40
    xs = np.where(band)[1]
    if len(xs) < 8:
        xs = np.where(alpha > 40)[1]
    return float(np.median(xs))


def place_full_figure(fig_rgba: np.ndarray, master: np.ndarray, scale: float = None) -> np.ndarray:
    opaque = fig_rgba[:, :, 3] > 40
    ys, xs = np.where(opaque)
    tight = fig_rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    crown, foot = _body_span(tight[:, :, 3])
    body = tight[crown:foot + 1]
    m_alpha = master[:, :, 3]
    m_ys = np.where(m_alpha > 40)[0]
    target_h = int(m_ys.max() - m_ys.min() + 1)
    master_head = m_alpha[int(m_ys.min()):int(m_ys.min()) + max(8, int(target_h * 0.22)), :]
    target_cx = _head_center_x(master_head)
    target_foot = int(m_ys.max())
    bh, bw = body.shape[:2]
    if scale is None:
        scale = target_h / float(bh)
    nw = max(1, int(round(bw * scale)))
    nh = max(1, int(round(bh * scale)))
    head_cx = _head_center_x(body[:, :, 3]) * scale
    resized = np.array(Image.fromarray(body, mode="RGBA").resize((nw, nh), Image.Resampling.LANCZOS))
    canvas = np.zeros_like(master)
    ox = int(round(target_cx - head_cx))
    oy = target_foot - nh + 1
    alpha_composite_layer(canvas, resized, ox, oy)
    return canvas


def sheet_character_mask(rgb: np.ndarray) -> np.ndarray:
    """Opaque where the painted child is, including white cloth close to the paper."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # The shawl outline is lighter than the hair line. Close those gaps before
    # the paper-colored flood, or the white cloth is read as empty background.
    barrier = (gray < 175).astype(np.uint8)
    barrier = cv2.dilate(barrier, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    flooded = (barrier == 0).astype(np.uint8)
    height, width = flooded.shape
    pad = np.zeros((height + 2, width + 2), np.uint8)
    seeds = [
        (0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1),
        (width // 2, 0), (width // 2, height - 1), (0, height // 2), (width - 1, height // 2),
    ]
    for x, y in seeds:
        if flooded[y, x] == 1:
            cv2.floodFill(flooded, pad, (x, y), 2)
    character = binary_fill_holes(flooded != 2).astype(np.uint8) * 255
    return cv2.erode(character, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))


def extract_sheet_figures(sheet: np.ndarray) -> list:
    """Each painted figure, whole, including arms that cross the column guides."""
    mask = sheet_character_mask(sheet)
    count, labels, stats, centers = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8))
    found = []
    for idx in range(1, count):
        x, y, w, h, area = [int(v) for v in stats[idx]]
        if area < 20000:
            continue
        found.append((int(centers[idx][1]), int(centers[idx][0]), x, y, w, h, idx))
    # Split the two rows first. A one-pixel difference in height must not swap a pose across the row.
    found.sort(key=lambda item: (0 if item[0] < 380 else 1, item[1]))
    if len(found) != 8:
        raise RuntimeError(f"expected 8 figures on the hand sheet, found {len(found)}")
    height, width = mask.shape
    figures = []
    for _, _, x, y, w, h, idx in found:
        x0, y0 = max(0, x - 2), max(0, y - 2)
        x1, y1 = min(width, x + w + 2), min(height, y + h + 2)
        alpha = np.where(labels[y0:y1, x0:x1] == idx, 255, 0).astype(np.uint8)
        figures.append(np.dstack([sheet[y0:y1, x0:x1], alpha]))
    return figures


def shared_fit_scale(figures: list, master: np.ndarray) -> float:
    """One scale for every pose, tall enough to match the master and narrow enough to keep the arms."""
    m_ys = np.where(master[:, :, 3] > 40)[0]
    target_h = int(m_ys.max() - m_ys.min() + 1)
    side_room = master.shape[1] - 36
    scale = target_h / 300.0
    for fig in figures:
        opaque = fig[:, :, 3] > 40
        ys, xs = np.where(opaque)
        tight = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        crown, foot = _body_span(tight[:, :, 3])
        body_h = max(1, foot - crown + 1)
        body_w = tight.shape[1]
        scale = min(scale, target_h / float(body_h), side_room / float(body_w))
    return scale


def build_sheet_plates(master: np.ndarray) -> dict:
    sheet = np.array(Image.open(
        BASE_DIR / "02_Character_Design" / "Hand_Gestures" / "THAKUR_HAND_GESTURE_SHEET_V001.png"
    ).convert("RGB"))
    names = [
        "01_namaskar", "02_folded_hands", "03_blessing", "04_pointing",
        "05_waving", "06_open_palm", "07_holding_object", "08_resting_hands",
    ]
    figures = extract_sheet_figures(sheet)
    scale = shared_fit_scale(figures, master)
    plates = {}
    for name, fig in zip(names, figures):
        Image.fromarray(fig, mode="RGBA").save(LAYERS_DIR / f"gesture_torso_{name}.png")
        plate = place_full_figure(fig, master, scale)
        Image.fromarray(plate, mode="RGBA").save(LAYERS_DIR / f"registered_gesture_{name}.png")
        plates[name] = plate
    return plates


def main():
    master = np.array(Image.open(LAYERS_DIR / "registered_seated_02_gentle_smile.png").convert("RGBA"))
    plates = build_sheet_plates(master)
    thumb_w, thumb_h = 220, 250
    board = Image.new("RGB", (4 * thumb_w + 16, 2 * thumb_h + 16), (236, 230, 218))
    for i, name in enumerate(plates):
        r, c = divmod(i, 4)
        im = Image.fromarray(plates[name], mode="RGBA")
        im.thumbnail((thumb_w - 8, thumb_h - 8), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", im.size, (236, 230, 218, 255))
        bg.alpha_composite(im)
        board.paste(bg.convert("RGB"), (8 + c * thumb_w, 8 + r * thumb_h))
    board_path = BASE_DIR / "07_Production_Tests" / "Hand_Gesture_Sheet_Plates.png"
    board.save(board_path)
    print(f"Plates written. Contact sheet: {board_path}")
    resting = plates["08_resting_hands"]
    for gname, asset_id, title, motion in GESTURES:
        print(f"Rendering {asset_id}")
        active = resting if gname == "08_resting_hands" else plates[gname]
        render_one(asset_id, title, resting, active, motion)
        print(f"Finished {asset_id}")


if __name__ == "__main__":
    import sys
    if "--plates" in sys.argv:
        master = np.array(Image.open(LAYERS_DIR / "registered_seated_02_gentle_smile.png").convert("RGBA"))
        build_sheet_plates(master)
        print("plates only")
    else:
        main()
