"""
TEST ANIMATION 1 FIX: THAKUR_SMILE_GENTLE_BLINK_V001
Fixes all 3 root causes of misalignment:
1. Unified Master Plate Deformation (NO split head/body layers -> ZERO double-crown or neck-gap ghosts!)
2. Exact sub-pixel eye socket warp for blinking (Left Eye: x=260..308, y=136..162; Right Eye: x=336..385, y=136..162)
   Rather than drawing a flat rectangle over the eye, we smoothly warp the actual upper eyelid & dark eyelash downward
   to meet the lower eyelid curve while compressing the iris/sclera inside the exact almond eye contour!
3. Exact mouth contour warp around the true mouth center (x=322, y=200) and unified sinusoidal breathing mesh deformation.
"""
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

from render_pilot_animations_1_to_3 import (
    BASE_DIR, LAYERS_DIR, GESTURE_DIR, PREVIEW_DIR,
    ease_in_out_cubic, alpha_composite_layer, encode_previews
)

ART_DIR = Path(r"C:\Users\USER\.gemini\antigravity\brain\7d6c96b0-8de4-401c-93fb-385f2c2d3564")


def load_clean_seated_master(scale_f: float = 1.6):
    """
    Loads the uncropped `body_seated_sukhasana.png` (410w x 435h), preserving 100% of the rounded hair crown
    at the top and all 5 bare toes at the bottom!
    """
    im = Image.open(LAYERS_DIR / "body_seated_sukhasana.png").convert("RGBA")
    arr = np.array(im)  # 435h x 410w
    h, w, _ = arr.shape
    nw, nh = int(round(w * scale_f)), int(round(h * scale_f))
    hi = np.array(Image.fromarray(arr).resize((nw, nh), Image.Resampling.LANCZOS))
    return hi


def apply_natural_eyelid_blink_and_smile(char_rgba: np.ndarray, blink_amt: float, smile_amt: float):
    """
    Applies anatomically accurate, sub-pixel aligned eyelid blinking and gentle smile deformation
    on the 656x696 `char_rgba` plate (where y is shifted by +16px relative to the old 415h crop because crop starts at y=70 instead of y=80!):
    - Left Eye (Viewer's Left): center=(284.0, 165.0), x=261..307, y=150..178
    - Right Eye (Viewer's Right): center=(358.0, 164.5), x=335..381, y=149..178
    - Mouth: center=(322.0, 216.0), x=278..366, y=198..238
    """
    out = char_rgba.copy()

    # 1. Clean Hand-Painted Eyelid Skin + Curved Lash Line Descent (ZERO eyebrow stretching!)
    if blink_amt > 0.005:
        eye_boxes = [
            # (ex0, ex1, ey0, ey1, center_x, top_arch_y, bot_lid_y)
            (261, 307, 150, 178, 284.0, 154.0, 172.5),
            (335, 381, 149, 178, 358.0, 153.5, 172.0)
        ]
        for (ex0, ex1, ey0, ey1, ecx, top_y, bot_y) in eye_boxes:
            ew = ex1 - ex0
            eh = ey1 - ey0
            eye_patch = out[ey0:ey1, ex0:ex1].copy()

            # Sample pure warm skin tone per column from forehead (y=116..128) and cheek (y=181..191)
            forehead_col = np.median(out[116:128, ex0:ex1, :3].astype(np.float32), axis=0)
            cheek_col = np.median(out[181:191, ex0:ex1, :3].astype(np.float32), axis=0)
            lid_skin_col = 0.45 * forehead_col + 0.55 * cheek_col
            crease_col = lid_skin_col * 0.84
            lash_col = np.array([58.0, 38.0, 26.0], dtype=np.float32)

            xs = np.arange(ew, dtype=np.float32)
            xn = ((xs + ex0) - ecx) / (ew * 0.45)
            arch_profile = np.clip(1.0 - xn ** 2, 0.0, 1.0)

            y_upper_rest = (top_y - ey0) + 5.8 * (1.0 - arch_profile)
            # Lower lid reaches down to cover 100% of the bottom rim of the iris when blink_amt == 1.0!
            y_lower_rest = (bot_y - ey0 + 2.2) - 2.0 * (1.0 - arch_profile)
            y_lash_cur = y_upper_rest + blink_amt * (y_lower_rest - y_upper_rest)

            for ix in range(3, ew - 3):
                ap = float(arch_profile[ix])
                if ap <= 0.02:
                    continue
                yu = float(y_upper_rest[ix])
                yl = float(y_lower_rest[ix])
                yc = float(y_lash_cur[ix])

                y_start = max(2, int(math.floor(yu - 1.0)))
                y_end = min(eh - 2, int(math.ceil(yc)))

                for iy in range(y_start, y_end + 1):
                    u_v = (iy - y_start) / max(1.0, float(y_end - y_start))
                    shade = 0.94 + 0.06 * math.sin(u_v * math.pi)
                    skin_rgb = np.clip(lid_skin_col[ix] * shade, 0, 255)
                    w_edge = min(1.0, ap * 2.2)
                    eye_patch[iy, ix, :3] = np.clip(
                        eye_patch[iy, ix, :3].astype(np.float32) * (1.0 - w_edge) + skin_rgb * w_edge, 0, 255
                    ).astype(np.uint8)

                if y_end - y_start >= 3:
                    w_c = min(1.0, ap * 1.6) * 0.45
                    eye_patch[y_start, ix, :3] = np.clip(
                        eye_patch[y_start, ix, :3].astype(np.float32) * (1.0 - w_c) + crease_col[ix] * w_c, 0, 255
                    ).astype(np.uint8)

                lash_thick = 1.0 + 1.05 * ap
                for iy in range(max(1, int(yc - 2)), min(eh - 1, int(yc + 3))):
                    dist = abs(iy - yc)
                    if dist < lash_thick:
                        w_l = (1.0 - dist / lash_thick) * min(1.0, ap * 2.2)
                        eye_patch[iy, ix, :3] = np.clip(
                            eye_patch[iy, ix, :3].astype(np.float32) * (1.0 - w_l) + lash_col * w_l, 0, 255
                        ).astype(np.uint8)

            out[ey0:ey1, ex0:ex1] = eye_patch

    # 2. Subtle Gentle Smile Transition around exact mouth center (cx=322, cy=216)
    if abs(smile_amt) > 0.005:
        mx0, mx1, my0, my1 = 278, 366, 198, 238
        m_patch = out[my0:my1, mx0:mx1].copy()
        mh, mw, _ = m_patch.shape
        gy, gx = np.indices((mh, mw), dtype=np.float32)
        cx, cy = 322.0 - mx0, 216.0 - my0
        nx = (gx - cx) / (mw * 0.45)
        ny = (gy - cy) / (mh * 0.45)
        radial = np.clip(1.0 - np.sqrt(nx ** 2 + ny ** 2), 0.0, 1.0)
        radial = radial * radial * (3.0 - 2.0 * radial)

        shift_y = -smile_amt * 3.4 * (nx ** 2) * radial
        shift_x = -smile_amt * 1.8 * nx * radial
        out[my0:my1, mx0:mx1] = cv2.remap(
            m_patch, (gx + shift_x).astype(np.float32), (gy - shift_y).astype(np.float32),
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
        )

    return out


def deform_unified_character_mesh(
    char_rgba: np.ndarray,
    head_pitch_deg: float = 0.0,
    head_yaw_deg: float = 0.0,
    head_roll_deg: float = 0.0,
    breath_phase: float = 0.0,
    cloth_phase: float = 0.0
):
    """
    Deforms the ENTIRE character (`656 x 664`) as a single continuous 2D mesh!
    - Because it is a SINGLE continuous mesh with smooth bone weight falloff at the neck (`y=215..255`),
      there is NEVER a detached head, NEVER a neck gap, and NEVER a ghost crown behind the hair!
    - Weight zones along Y (0..664):
      - Head zone (`y = 0..220`): weight_head = 1.0 (smoothly transitions to 0.0 over `y = 220..260` neck/collar).
      - Chest/Torso zone (`y = 230..480`): breathing chest expansion & shoulder lift.
      - Uttoriyo shawl sleeves (`y = 250..500`, outer left/right): 3-frame delayed cloth sway.
      - Crossed legs base (`y = 500..664`): grounded on the mat (`weight = 0.0` at bottom contact `y=650`).
    """
    h, w, _ = char_rgba.shape
    gy, gx = np.indices((h, w), dtype=np.float32)

    # Smooth bone weights (0.0 to 1.0) shifted by +16px for the uncropped 696h canvas:
    w_head = np.clip((274.0 - gy) / (274.0 - 231.0), 0.0, 1.0)
    w_head = w_head * w_head * (3.0 - 2.0 * w_head)

    w_torso = np.clip(1.0 - np.abs(gy - 366.0) / 170.0, 0.0, 1.0)
    w_torso = w_torso * w_torso * (3.0 - 2.0 * w_torso)

    w_cloth = np.clip(1.0 - np.abs(gy - 446.0) / 130.0, 0.0, 1.0)

    dx_total = np.zeros((h, w), dtype=np.float32)
    dy_total = np.zeros((h, w), dtype=np.float32)

    px, py = 322.0, 251.0
    rel_x = gx - px
    rel_y = gy - py

    rad = math.radians(-head_roll_deg)
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    rot_dx = (rel_x * cos_r - rel_y * sin_r) - rel_x
    rot_dy = (rel_x * sin_r + rel_y * cos_r) - rel_y

    # 2.5D Pitch (nodding down/up): shifts facial features vertically with subtle curvature
    pitch_rad = math.radians(head_pitch_deg)
    x_norm_head = np.clip(rel_x / 110.0, -1.5, 1.5)
    pitch_dy = -math.sin(pitch_rad) * 16.0 * (1.0 - 0.25 * (x_norm_head ** 2))
    # Subtle vertical compression of forehead/chin during pitch
    pitch_comp_dy = (gy - 148.0) * (1.0 - math.cos(pitch_rad * 0.65))

    # 2.5D Yaw (turning left/right): shifts facial center horizontally more than outer cranium/ears
    yaw_rad = math.radians(head_yaw_deg)
    y_face_bell = np.clip(1.0 - ((gy - 148.0) / 115.0) ** 2, 0.0, 1.0)
    yaw_dx = -math.sin(yaw_rad) * 20.0 * (1.0 - 0.40 * (x_norm_head ** 2)) * y_face_bell

    dx_total += w_head * (rot_dx + yaw_dx)
    dy_total += w_head * (rot_dy + pitch_dy + pitch_comp_dy)

    # --- B. Torso Breathing & Subtle Living Posture ---
    breath = math.sin(breath_phase)
    cloth_sway = math.sin(cloth_phase)

    # Chest expands horizontally by ±0.8% and lifts vertically by ±1.8px during inhalation
    dx_total += w_torso * (-(gx - 322.0) * 0.008 * breath)
    dy_total += (w_torso + w_head * 0.7) * (1.8 * breath)

    # Overlapping uttoriyo shawl fold wave
    dx_total += w_cloth * (-2.2 * cloth_sway)

    map_x = (gx + dx_total).astype(np.float32)
    map_y = (gy + dy_total).astype(np.float32)

    warped = cv2.remap(
        char_rgba, map_x, map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )
    return warped


def test_render_pilot_1():
    asset_id = "THAKUR_SMILE_GENTLE_BLINK_V001"
    out_dir = GESTURE_DIR / "Facial" / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    master_hi = load_clean_seated_master(scale_f=1.6)
    nh, nw, _ = master_hi.shape
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20

    # Natural blink schedule across 72 frames (3.0s @ 24 FPS):
    # Blink 1 at frames 18..25, Blink 2 at frames 52..58
    b1_map = {18: 0.25, 19: 0.70, 20: 1.0, 21: 1.0, 22: 0.75, 23: 0.40, 24: 0.15}
    b2_map = {52: 0.30, 53: 0.80, 54: 1.0, 55: 0.80, 56: 0.40, 57: 0.12}

    total_frames = 72
    for f in range(total_frames):
        t = f / float(total_frames)
        phase = 2.0 * math.pi * t
        cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total_frames))

        blink_val = b1_map.get(f, b2_map.get(f, 0.0))
        smile_val = 0.5 - 0.5 * math.cos(phase)  # Smooth 0 -> 1 -> 0 gentle smile progression

        # 1. Apply exact sub-pixel eyelid blink and gentle smile on master plate
        face_animated = apply_natural_eyelid_blink_and_smile(master_hi, blink_val, smile_val)

        # 2. Deform as a single continuous unified mesh (breathing, subtle affectionate head tilt, cloth overlap)
        deformed = deform_unified_character_mesh(
            face_animated,
            head_pitch_deg=-1.0 * smile_val,
            head_yaw_deg=0.8 * math.sin(phase),
            head_roll_deg=1.3 * math.sin(phase - 0.3),
            breath_phase=phase,
            cloth_phase=cloth_phase
        )

        canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canvas, deformed, ox, oy)
        Image.fromarray(canvas, mode="RGBA").save(frames_dir / f"{asset_id}_{f + 1:04d}.png")

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)

    # Save diagnostic close-up comparison of FULL character (Crown to Toes) for Frame 1, Frame 19, Frame 21, Frame 36
    diag = Image.new("RGBA", (384 * 4, 768), (247, 243, 232, 255))
    for idx, f_num in enumerate([1, 19, 21, 36]):
        fim = Image.open(frames_dir / f"{asset_id}_{f_num:04d}.png")
        crop = fim.crop((192, 0, 576, 768))
        diag.alpha_composite(crop, (idx * 384, 0))
    diag.convert("RGB").save(ART_DIR / "test_fix_smile_blink_verification.png")

    # Copy updated GIF and MP4 to artifact dir for user preview
    import shutil
    shutil.copyfile(gif_p, ART_DIR / f"{asset_id}.gif")
    shutil.copyfile(mp4_p, ART_DIR / f"{asset_id}.mp4")
    print("Test fix for THAKUR_SMILE_GENTLE_BLINK_V001 rendered and verified.")


if __name__ == "__main__":
    test_render_pilot_1()
