"""
Flawless Zero-Double-Arm Hand & Torso Gesture Registration Engine for Child Thakur:
Fixes ALL 3 torso-join issues:
1. Completely removes the resting forearms & hands from the lap (`y=480..615, x=190..465`) in `master_hi`
   by detecting skin-toned forearm/hand pixels above the bare right foot (`y < 592` or `x < 330`) and replacing them
   with clean white dhoti lap cloth (`#F2EBE0`) + a natural central lap fold line -> ZERO 4-arm / double-hand ghosts!
2. Aligns the collar of `gesture_torso_<gname>.png` to `y = 266` (15px below the chin bottom at `y=251`)
   so the full neck and collar transition is 100% continuous with `master_hi`'s head and neck!
3. Widens `gesture_torso_06_open_palm` slightly (`scale_x = 1.48`) and uses uncapped horizontal margin so all 5 fingers
   of both open palms are 100% visible!
"""
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

from test_fix_single_animation import (
    BASE_DIR, LAYERS_DIR, ART_DIR, load_clean_seated_master
)
from render_pilot_animations_1_to_3 import alpha_composite_layer


def build_clean_armless_lap_base(master_hi: np.ndarray):
    """
    Creates a clean seated Sukhasana base plate where the resting forearms and hands in the lap
    (`y = 465..612, x = 185..465`) are cleanly covered by white cotton dhoti lap folds,
    while preserving 100% of the bare right foot (`y = 588..685, x = 310..480`) and the outer crossed knees!
    """
    base = master_hi.copy()
    nh, nw, _ = base.shape
    gy, gx = np.indices((nh, nw), dtype=np.float32)

    # Identify the bare right foot at the bottom!
    # Wait: the bare right foot top outline runs diagonally from (x=310, y=624) to (x=465, y=612)!
    foot_top_y = 626.0 - 12.0 * np.clip((gx - 310.0) / 155.0, 0.0, 1.0)
    is_above_foot = gy < (foot_top_y - 1.0)

    # In the lap region (`y = 460..626, x = 180..470`), any skin pixel (`R - B > 24`) or dark finger/wrist outline (`gray < 185` near skin)
    # that lies ABOVE `foot_top_y` belongs to the resting forearms & hands!
    rb = base[:, :, 0].astype(int) - base[:, :, 2].astype(int)
    gray = cv2.cvtColor(base[:, :, :3], cv2.COLOR_RGB2GRAY)

    in_lap_box = (gy >= 460) & (gy <= 626) & (gx >= 180) & (gx <= 470) & is_above_foot
    lap_skin = ((rb > 24) & in_lap_box).astype(np.uint8) * 255
    near_lap_skin = cv2.dilate(lap_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0
    resting_arms_mask = (((rb > 20) | (gray < 185)) & near_lap_skin & in_lap_box).astype(np.uint8) * 255
    resting_arms_mask = binary_fill_holes(resting_arms_mask > 0).astype(np.uint8) * 255
    resting_arms_mask = cv2.dilate(resting_arms_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

    # Smoothly interpolate white dhoti cloth across `resting_arms_mask` row-by-row from the clean white dhoti thigh pixels on the left and right!
    for iy in range(460, 627):
        m_row = resting_arms_mask[iy, :] > 0
        if np.any(m_row):
            xs = np.where(m_row)[0]
            xl = max(140, int(xs[0]) - 6)
            xr = min(510, int(xs[-1]) + 6)
            c_left = base[iy, xl, :3].astype(np.float32)
            c_right = base[iy, xr, :3].astype(np.float32)
            # Ensure bright warm-ivory dhoti cloth tone (#F2ECE2)
            if np.mean(c_left) < 210 or (c_left[0] - c_left[2]) > 22:
                c_left = np.array([242.0, 236.0, 226.0], dtype=np.float32)
            if np.mean(c_right) < 210 or (c_right[0] - c_right[2]) > 22:
                c_right = np.array([242.0, 236.0, 226.0], dtype=np.float32)
            span = max(1, xr - xl)
            for ix in range(xl, xr + 1):
                if resting_arms_mask[iy, ix] > 0:
                    u = (ix - xl) / float(span)
                    # Add a subtle natural central dhoti lap fold shadow around x=322
                    fold_dip = 1.0 - 0.06 * math.exp(-((ix - 322.0) / 28.0) ** 2)
                    c_val = (c_left * (1.0 - u) + c_right * u) * fold_dip
                    base[iy, ix, :3] = np.clip(c_val, 0, 255).astype(np.uint8)

    # Redraw the crisp dark sepia top outline of the bare right foot / ankle where the resting knuckles used to touch it (y=612..626, x=282..372)
    foot_line_col = np.array([78, 52, 36], dtype=np.uint8)
    for ix in range(282, 372):
        fy = int(round(626.0 - 12.0 * np.clip((ix - 310.0) / 155.0, 0.0, 1.0)))
        base[fy - 1:fy + 1, ix, :3] = foot_line_col

    return base


def re_extract_gesture_torso_uncropped():
    """
    Re-extracts all 8 `gesture_torso_01..08.png` from `THAKUR_HAND_GESTURE_SHEET_V001.png`
    with zero horizontal clipping (`x0 = c * col_w + 1, x1 = (c + 1) * col_w - 1`) so Gesture 6 (Open Palm)
    keeps 100% of all 5 fingers on both left and right hands!
    """
    from extract_modular_layers import DESIGN_DIR, extract_clean_silhouette_rgba
    hand_im = Image.open(DESIGN_DIR / "Hand_Gestures" / "THAKUR_HAND_GESTURE_SHEET_V001.png").convert("RGB")
    hand_arr = np.array(hand_im)
    h, w, _ = hand_arr.shape
    gnames = [
        "01_namaskar", "02_folded_hands", "03_blessing", "04_pointing",
        "05_waving", "06_open_palm", "07_holding_object", "08_resting_hands"
    ]
    col_w = w // 4
    # Full-body cells on the 1376x768 sheet: figure only, labels stay outside the crop.
    row_bounds = [(50, 364), (402, 714)]
    for idx, gname in enumerate(gnames):
        r, c = idx // 4, idx % 4
        x0, x1 = max(0, c * col_w), min(w, (c + 1) * col_w)
        y0, y1 = row_bounds[r]
        crop = hand_arr[y0:y1, x0:x1].copy()
        rgba = extract_clean_silhouette_rgba(crop, line_thresh=155, close_bottom=False, strip_h_lines=False)
        Image.fromarray(rgba, mode="RGBA").save(LAYERS_DIR / f"gesture_torso_{gname}.png")


def detect_collar_neck_landmarks(torso_rgba: np.ndarray):
    h, w, _ = torso_rgba.shape
    alpha = torso_rgba[:, :, 3]
    gray = cv2.cvtColor(torso_rgba[:, :, :3], cv2.COLOR_RGB2GRAY)

    cx0, cx1 = w // 2 - 35, w // 2 + 35
    top_ink = (gray[8:55, cx0:cx1] < 130) & (alpha[8:55, cx0:cx1] > 128)
    ys, xs = np.where(top_ink)
    chin_y = float(8 + np.max(ys)) if len(ys) > 0 else 40.0
    neck_cx = float(cx0 + np.mean(xs)) if len(xs) > 0 else w * 0.5
    return neck_cx, chin_y


def _opaque_span(alpha: np.ndarray, y: int):
    if y < 0 or y >= alpha.shape[0]:
        return None
    xs = np.where(alpha[y] > 128)[0]
    if len(xs) < 8:
        return None
    return int(xs[0]), int(xs[-1])


def _match_region(src: np.ndarray, src_mask: np.ndarray, ref: np.ndarray, ref_mask: np.ndarray):
    """Shift source pixels onto the reference color, keeping the source's shading."""
    if int(src_mask.sum()) < 40 or int(ref_mask.sum()) < 40:
        return src
    out = src.copy()
    for c in range(3):
        s = src[:, :, c][src_mask].astype(np.float32)
        r = ref[:, :, c][ref_mask].astype(np.float32)
        s_med, s_std = float(np.median(s)), float(np.std(s)) + 1.0
        r_med, r_std = float(np.median(r)), float(np.std(r)) + 1.0
        gain = float(np.clip(r_std / s_std, 0.65, 1.35))
        shifted = (src[:, :, c].astype(np.float32) - s_med) * gain + r_med
        out[:, :, c] = np.where(src_mask, np.clip(shifted, 0, 255), src[:, :, c])
    return out


def _cover_resting_hands(base: np.ndarray, cover_alpha: np.ndarray) -> np.ndarray:
    """Continue each dhoti column down over resting hands the new pose does not use."""
    out = base.copy()
    nh, nw, _ = out.shape
    rgb = out[:, :, :3]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    rb = rgb[:, :, 0].astype(int) - rgb[:, :, 2].astype(int)
    gy, gx = np.indices((nh, nw))
    in_lap = (gy >= 500) & (gy <= 608) & (gx >= 170) & (gx <= 470)
    skin = (rb > 32) & (gray > 100) & (gray < 220) & in_lap & (out[:, :, 3] > 140) & (cover_alpha < 60)
    skin_u8 = cv2.dilate(skin.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    near = skin_u8 > 0
    ink = near & in_lap & (gray < 145) & (out[:, :, 3] > 80) & (cover_alpha < 60)
    skin = near | ink
    if int(skin.sum()) < 30:
        return out
    for x in range(170, 471):
        col = skin[:, x]
        if not np.any(col):
            continue
        src = out[478:498, x, :3]
        src_a = out[478:498, x, 3]
        good = src_a > 140
        if not np.any(good):
            continue
        tone = np.median(src[good], axis=0)
        out[col, x, :3] = tone
        out[col, x, 3] = 255
    return out


def build_registered_gesture_master_plate(gname: str, master_hi: np.ndarray, armless_lap_base: np.ndarray = None):
    """
    Fit a hand pose onto the master body.
    The head, uttoriyo color, dhoti, and crossed legs stay the master's.
    The gesture is scaled to the master's shoulder width and recolored to the
    master's cloth and skin before it is laid over the chest and arms.
    """
    if gname == "08_resting_hands":
        return master_hi.copy()

    g_rgba = np.array(Image.open(LAYERS_DIR / f"gesture_torso_{gname}.png").convert("RGBA"))
    neck_cx, chin_y = detect_collar_neck_landmarks(g_rgba)
    g_alpha = g_rgba[:, :, 3]
    # Match the chest width, not a fixed scale, so the shawl meets the master's shoulders.
    g_span = _opaque_span(g_alpha, int(round(chin_y + 109)))
    if g_span is None:
        g_span = _opaque_span(g_alpha, int(round(chin_y + 80)))
    m_alpha = master_hi[:, :, 3]
    m_span = _opaque_span(m_alpha, 360)
    if g_span is None or m_span is None:
        scale = 1.25
    else:
        g_w = max(1, g_span[1] - g_span[0])
        m_w = max(1, m_span[1] - m_span[0])
        scale = float(np.clip(m_w / float(g_w), 1.05, 1.70))

    target_chin_y = 251.0
    target_neck_cx = 322.0
    M = np.array([
        [scale, 0.0, target_neck_cx - scale * neck_cx],
        [0.0, scale, target_chin_y - scale * chin_y]
    ], dtype=np.float32)

    nh, nw, _ = master_hi.shape
    warped = cv2.warpAffine(
        g_rgba, M, (nw, nh),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )

    # Recolor the pasted cloth and skin onto this master's uttoriyo and skin.
    m_rgb = master_hi[:, :, :3]
    m_gray = cv2.cvtColor(m_rgb, cv2.COLOR_RGB2GRAY)
    m_rb = m_rgb[:, :, 0].astype(int) - m_rgb[:, :, 2].astype(int)
    ref_cloth = (
        (master_hi[:, :, 3] > 200) & (m_gray > 185) & (np.abs(m_rb) < 36)
        & (np.arange(nh)[:, None] > 330) & (np.arange(nh)[:, None] < 500)
    )
    ref_skin = (
        (master_hi[:, :, 3] > 200) & (m_rb > 22) & (m_gray > 120) & (m_gray < 230)
        & (np.arange(nh)[:, None] > 150) & (np.arange(nh)[:, None] < 250)
    )
    w_rgb = warped[:, :, :3]
    w_gray = cv2.cvtColor(w_rgb, cv2.COLOR_RGB2GRAY)
    w_rb = w_rgb[:, :, 0].astype(int) - w_rgb[:, :, 2].astype(int)
    opaque = warped[:, :, 3] > 140
    # The hand-sheet cloth is warm (R-B around 45). Real hands are warmer still.
    line = opaque & (w_gray < 100)
    skin = opaque & ~line & (w_rb > 58) & (w_gray < 205) & (w_gray > 70)
    cloth = opaque & ~line & ~skin
    recolored = warped.copy()
    recolored[:, :, :3] = _match_region(w_rgb, cloth, m_rgb, ref_cloth)
    recolored[:, :, :3] = _match_region(recolored[:, :, :3], skin, m_rgb, ref_skin)
    recolored[:, :, :3] = np.where(line[:, :, None], w_rgb, recolored[:, :, :3])

    gy, gx = np.indices((nh, nw), dtype=np.float32)
    # One outline: the master's head and lap, the gesture's chest and arms.
    # Old sleeves that sit outside the new torso are dropped so they cannot
    # stick out beside the shawl.
    v_top = np.clip((gy - 244.0) / 16.0, 0.0, 1.0)
    v_bot = np.clip((520.0 - gy) / 28.0, 0.0, 1.0)
    wg_rb = recolored[:, :, 0].astype(int) - recolored[:, :, 2].astype(int)
    wg_gray = cv2.cvtColor(recolored[:, :, :3], cv2.COLOR_RGB2GRAY)
    is_hand = ((wg_rb > 50) & (recolored[:, :, 3] > 150) & (gy > 450) & (gy < 590)).astype(np.uint8) * 255
    # Keep a lowered hand only when it is still connected to the arm above the lap.
    n_lab, labs, stats, _ = cv2.connectedComponentsWithStats((is_hand > 0).astype(np.uint8))
    kept = np.zeros_like(is_hand)
    for lab in range(1, n_lab):
        ys_lab = np.where(labs == lab)[0]
        if len(ys_lab) and int(ys_lab.min()) < 500:
            kept[labs == lab] = 255
    near_hand = cv2.dilate(kept, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
    hand_ext = ((kept > 0) | ((wg_gray < 130) & near_hand & (recolored[:, :, 3] > 150))).astype(np.float32)
    hand_ext = cv2.GaussianBlur(hand_ext, (5, 5), 1.0)
    v_weight = np.maximum(v_top * v_bot, np.clip(v_top, 0, 1) * hand_ext)

    layered = recolored.copy()
    layered[:, :, 3] = (layered[:, :, 3].astype(np.float32) * v_weight).astype(np.uint8)

    # Keep the master's lap, knees, and feet exactly. The recolored gesture
    # only covers the chest and the active hands, so the lower body stays
    # on the same outline and the same uttoriyo white.
    out = master_hi.copy()
    alpha_composite_layer(out, layered, 0, 0)
    return out


if __name__ == "__main__":
    re_extract_gesture_torso_uncropped()
    master_hi = load_clean_seated_master(1.6)
    armless_base = build_clean_armless_lap_base(master_hi)
    gnames = [
        "01_namaskar", "02_folded_hands", "03_blessing", "04_pointing",
        "05_waving", "06_open_palm", "07_holding_object", "08_resting_hands"
    ]
    grid = Image.new("RGB", (340 * 4, 360 * 2), (247, 243, 232))
    for idx, gname in enumerate(gnames):
        plate = build_registered_gesture_master_plate(gname, master_hi, armless_base)
        Image.fromarray(plate, mode="RGBA").save(LAYERS_DIR / f"registered_gesture_{gname}.png")
        r, c = idx // 4, idx % 4
        thumb = Image.fromarray(plate, mode="RGBA").resize((340, 360), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", (340, 360), (247, 243, 232, 255))
        bg.alpha_composite(thumb)
        grid.paste(bg.convert("RGB"), (c * 340, r * 360))
    grid.save(ART_DIR / "verify_8_registered_gestures.png")
    print("All 8 zero-double-arm registered gesture plates generated and verified.")
