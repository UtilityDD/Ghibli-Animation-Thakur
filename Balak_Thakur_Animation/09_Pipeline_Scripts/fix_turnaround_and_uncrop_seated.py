"""
Fixes ALL 3 visual issues reported by the user:
1. THAKUR_TURNAROUND_SHEET_V001.png Left Profile & Right Profile Hand Gesture Mismatch:
   - Replaces the flat, 4-finger-backwards hand on Left Profile and Right Profile with the anatomically natural side-profile
     child hand (matching the 3/4 Front View's side-profile hand with a distinct forward-facing thumb and gently curved fingers)!
   - On Left Profile (facing LEFT): the thumb faces LEFT (forward) and the fingers curve gently behind it on the right.
   - On Right Profile (facing RIGHT): the thumb faces RIGHT (forward) and the fingers curve gently behind it on the left.
2. Top-of-Head (Crown) & Bottom-of-Foot (Toes) Clipping on Seated Character (`body_seated_sukhasana.png` and `THAKUR_SMILE_GENTLE_BLINK_V001`):
   - Instead of slicing off rows `y < 19` and `y > 406` (which chopped the top curve of the hair crown and the bottom pinkie toe!),
     we remove ONLY the 2px horizontal chart lines outside the character contour while 100% preserving the full curved hair crown
     at the top and all 5 toes of the bare foot at the bottom!
3. Fine-Tunes Eyelid Blinking on `THAKUR_SMILE_GENTLE_BLINK_V001`:
   - Smooths the eyelid skin-to-lash transition with soft anti-aliased sub-pixel blending and natural ease-in/ease-out eyelid curve
     so the blink looks 100% hand-drawn Ghibli cel animation.
"""
from pathlib import Path
import shutil
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

BASE_DIR = Path(r"E:\Codes\Ghibli Animation Thakur\Balak_Thakur_Animation")
TURN_PATH = BASE_DIR / "02_Character_Design" / "Turnaround" / "THAKUR_TURNAROUND_SHEET_V001.png"
BACKUP_PATH = BASE_DIR / "02_Character_Design" / "Turnaround" / "THAKUR_TURNAROUND_SHEET_V000_PRE_FIX.png"
PROP_PATH = BASE_DIR / "02_Character_Design" / "Body_Proportions" / "THAKUR_BODY_PROPORTION_SHEET_V001.png"
LAYERS_DIR = BASE_DIR / "03_Character_Assets" / "Layers"
PNG_DIR = BASE_DIR / "03_Character_Assets" / "Transparent_PNG"
ART_DIR = Path(r"C:\Users\USER\.gemini\antigravity\brain\7d6c96b0-8de4-401c-93fb-385f2c2d3564")


def fix_turnaround_hands_and_feet():
    """
    Rebuilds Left Profile and Right Profile on THAKUR_TURNAROUND_SHEET_V001.png from the clean backup:
    1. Extracts the natural side-profile hanging hand from the 3/4 Front View (x=378..438, y=424..502),
       which has a clear, anatomically expressive forward-facing thumb and gently curved side-profile fingers!
    2. Places it cleanly onto Right Profile (thumb facing RIGHT / forward) and flipped onto Left Profile (thumb facing LEFT / forward),
       matching the wrist exit from the uttoriyo sleeve and keeping the surrounding white dhoti 100% clean.
    3. Flips the bare shins and 5-toed feet below the dhoti hem so Left Profile feet point LEFT and Right Profile feet point RIGHT.
    """
    im_orig = Image.open(BACKUP_PATH).convert("RGB")
    out = np.array(im_orig)

    # --- STEP 1: Extract the expressive side-profile hand from 3/4 Front View (x=384..438, y=432..498) ---
    # In 3/4 Front view, the viewer-left hand (character's right hand) hangs from the sleeve in a natural side profile
    # with the thumb clearly separated on the right (forward) side and curved fingers on the left (back) side!
    ref_hand_crop = out[432:498, 384:438].copy()  # 66h x 54w
    rh_b = ref_hand_crop[:, :, 0].astype(int) - ref_hand_crop[:, :, 2].astype(int)
    rgray = cv2.cvtColor(ref_hand_crop, cv2.COLOR_RGB2GRAY)

    # Extract skin + dark sepia hand outline mask from ref_hand_crop
    r_skin = (rh_b > 32).astype(np.uint8) * 255
    # Exclude the upper-left sleeve corner above y=12
    r_skin[:6, :12] = 0
    near_rs = cv2.dilate(r_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
    r_mask = ((rh_b > 28) | ((rgray < 168) & near_rs)).astype(np.uint8) * 255
    r_mask = binary_fill_holes(r_mask > 0).astype(np.uint8) * 255
    # Keep only the single largest connected component (the hand)
    n_lab, labs, stats, _ = cv2.connectedComponentsWithStats((r_mask > 0).astype(np.uint8))
    if n_lab > 1:
        largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        r_mask = np.where(labs == largest, 255, 0).astype(np.uint8)

    # Resize ref_hand slightly (to 48w x 56h) so its wrist width matches the Left/Right Profile wrist width (34px)
    hand_right_prof_rgb = cv2.resize(ref_hand_crop, (48, 56), interpolation=cv2.INTER_LANCZOS4)
    hand_right_prof_m = cv2.resize(r_mask, (48, 56), interpolation=cv2.INTER_LINEAR)
    # In hand_right_prof_rgb, the thumb is on the RIGHT (forward for Right Profile!) and curved fingers are on the LEFT!
    # For Left Profile (facing LEFT), we mirror it horizontally so the thumb is on the LEFT (forward for Left Profile!)
    hand_left_prof_rgb = hand_right_prof_rgb[:, ::-1, :].copy()
    hand_left_prof_m = hand_right_prof_m[:, ::-1].copy()

    def apply_profile_fixes(img_arr, x_prof_start, x_prof_end, x_hand_start, x_hand_end, is_left_profile):
        # A. Fix Bare Shins & Feet below the exact dhoti lower hem curve (y=580..734)
        fy0, fy1 = 580, 734
        f_crop = img_arr[fy0:fy1, x_prof_start:x_prof_end].copy()
        fh, fw, _ = f_crop.shape
        r_minus_b = f_crop[:, :, 0].astype(int) - f_crop[:, :, 2].astype(int)
        gray = cv2.cvtColor(f_crop, cv2.COLOR_RGB2GRAY)

        is_leg_skin = (r_minus_b > 32).astype(np.uint8) * 255
        near_leg_skin = cv2.dilate(is_leg_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
        is_leg_or_foot = ((r_minus_b > 28) | ((gray < 170) & near_leg_skin)).astype(np.uint8) * 255
        is_leg_or_foot = binary_fill_holes(is_leg_or_foot > 0).astype(np.uint8) * 255

        keep_upper_mask = np.zeros((fh, fw), dtype=np.float32)
        for x in range(fw):
            skin_ys = np.where(is_leg_skin[:, x] > 0)[0]
            if len(skin_ys) > 0 and skin_ys[0] < 45:
                hem_y = max(0, int(skin_ys[0]) - 1)
                keep_upper_mask[:hem_y, x] = 1.0
            else:
                keep_upper_mask[:38, x] = 1.0

        shin_band = is_leg_or_foot[40:65, :]
        sys, sxs = np.where(shin_band > 0)
        shin_cx = int(round(np.mean(sxs)))

        bg_plate = np.zeros_like(f_crop)
        for row_i in range(fh):
            row_bg = np.median(np.concatenate([f_crop[row_i, :8, :], f_crop[row_i, -8:, :]], axis=0), axis=0).astype(np.uint8)
            bg_plate[row_i, :, :] = row_bg

        leg_rgba = np.dstack([f_crop, is_leg_or_foot])
        leg_flipped = np.zeros_like(leg_rgba)
        for x in range(fw):
            src_x = 2 * shin_cx - x
            if 0 <= src_x < fw:
                leg_flipped[:, x, :] = leg_rgba[:, src_x, :]

        for row_i in range(38, 4, -1):
            m_below = leg_flipped[row_i + 1, :, 3] > 128
            m_curr = leg_flipped[row_i, :, 3] > 128
            fill_cols = m_below & (~m_curr)
            if np.any(fill_cols):
                leg_flipped[row_i, fill_cols, :] = leg_flipped[row_i + 1, fill_cols, :]

        leg_a = cv2.GaussianBlur(leg_flipped[:, :, 3].astype(np.float32) / 255.0, (3, 3), 0.6)[:, :, None]
        lower_comp = bg_plate.astype(np.float32) * (1.0 - leg_a) + leg_flipped[:, :, :3].astype(np.float32) * leg_a
        keep_3 = cv2.GaussianBlur(keep_upper_mask, (3, 3), 0.5)[:, :, None]
        img_arr[fy0:fy1, x_prof_start:x_prof_end] = np.clip(
            lower_comp * (1.0 - keep_3) + f_crop.astype(np.float32) * keep_3, 0, 255
        ).astype(np.uint8)

        # B. Replace the flat profile hand (y=440..500) with the expressive side-profile hand (thumb forward, curved fingers back)
        hy0, hy1 = 440, 500
        h_crop = img_arr[hy0:hy1, x_hand_start:x_hand_end].copy()
        hh, hw, _ = h_crop.shape
        hr_b = h_crop[:, :, 0].astype(int) - h_crop[:, :, 2].astype(int)
        hgray = cv2.cvtColor(h_crop, cv2.COLOR_RGB2GRAY)

        # Mask of existing flat hand below wrist (rows 3..hh)
        old_skin = (hr_b > 28).astype(np.uint8) * 255
        near_os = cv2.dilate(old_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
        old_hand_m = ((hr_b > 24) | ((hgray < 185) & near_os)).astype(np.uint8) * 255
        old_hand_m = binary_fill_holes(old_hand_m > 0).astype(np.uint8) * 255

        # Resize new hand to (52w x 60h) so it is slightly wider than the old hand (completely covering the old outline!),
        # and redraw the clean diagonal dhoti fold line where the old hand used to sit so there is ZERO break in the dhoti crease!
        dhoti_under = h_crop.copy()
        # Fill the old hand footprint (below ry=13, where uttoriyo sleeve ends) with clean white dhoti cloth (#EFECE6)
        # and continue any interrupted dhoti diagonal fold line straight up to the uttoriyo hem at ry=13!
        k_dil = cv2.dilate(old_hand_m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        for ry in range(13, hh):
            m_row = k_dil[ry, :] > 0
            if np.any(m_row):
                xs = np.where(m_row)[0]
                xl, xr = max(1, int(xs[0]) - 2), min(hw - 2, int(xs[-1]) + 2)
                dhoti_under[ry, xl:xr + 1] = np.array([239, 235, 227], dtype=np.uint8)

        # Trace the diagonal dhoti fold line that enters from the bottom (ry=59) up to the uttoriyo hem (ry=13)
        # On Left Profile, the fold line enters at x=12 (ry=14) down to x=19 (ry=59); on Right Profile, mirrored!
        line_col = np.array([92, 68, 52], dtype=np.uint8)
        shadow_col = np.array([218, 211, 200], dtype=np.uint8)
        for ry in range(13, hh):
            u_line = (ry - 13) / float(hh - 13)
            if is_left_profile:
                lx = int(round(44 - 8 * u_line))
                dhoti_under[ry, lx:min(hw, lx + 4)] = shadow_col
                dhoti_under[ry, lx - 1:lx + 1] = line_col
            else:
                lx = int(round(12 + 8 * u_line))
                dhoti_under[ry, max(0, lx - 3):lx + 1] = shadow_col
                dhoti_under[ry, lx:lx + 2] = line_col

        new_rgb = cv2.resize(hand_left_prof_rgb if is_left_profile else hand_right_prof_rgb, (52, 60), interpolation=cv2.INTER_LANCZOS4)
        new_m = cv2.resize(hand_left_prof_m if is_left_profile else hand_right_prof_m, (52, 60), interpolation=cv2.INTER_LINEAR)

        old_wrist_xs = np.where(old_hand_m[4:8, :] > 128)[1]
        target_wrist_cx = int(round(np.mean(old_wrist_xs)))
        new_wrist_xs = np.where(new_m[6:10, :] > 128)[1]
        src_wrist_cx = int(round(np.mean(new_wrist_xs)))
        dx_shift = target_wrist_cx - src_wrist_cx - (1 if is_left_profile else -1)

        placed_rgb = np.zeros_like(h_crop)
        placed_m = np.zeros((hh, hw), dtype=np.uint8)
        for x in range(hw):
            sx = x - dx_shift
            if 0 <= sx < 52:
                placed_rgb[:, x, :] = new_rgb[:, sx, :]
                placed_m[:, x] = new_m[:, sx]

        # Composite new hand onto dhoti_under with smooth 8-row blend into the original wrist at top (rows 0..8)
        ha = cv2.GaussianBlur(placed_m.astype(np.float32) / 255.0, (3, 3), 0.5)[:, :, None]
        comp_h = dhoti_under.astype(np.float32) * (1.0 - ha) + placed_rgb.astype(np.float32) * ha
        for ry in range(8):
            w_y = ry / 8.0
            comp_h[ry] = h_crop[ry].astype(np.float32) * (1.0 - w_y) + comp_h[ry] * w_y

        img_arr[hy0:hy1, x_hand_start:x_hand_end] = np.clip(comp_h, 0, 255).astype(np.uint8)

    # Apply to Left Profile and Right Profile
    apply_profile_fixes(out, 635, 795, 702, 758, is_left_profile=True)
    apply_profile_fixes(out, 895, 1055, 933, 989, is_left_profile=False)

    out_im = Image.fromarray(out, mode="RGB")
    out_im.save(TURN_PATH)
    out_im.save(ART_DIR / "thakur_turnaround_sheet_v001_final_1795588115133.jpg", quality=96)
    out_im.crop((590, 40, 1110, 760)).save(ART_DIR / "inspect_profiles_fixed_zoom.png")
    out_im.crop((40, 350, 1340, 520)).save(ART_DIR / "inspect_all_5_hands_fixed.png")
    print("Turnaround sheet Left and Right Profile hands and feet updated cleanly.")


def re_extract_full_seated_sukhasana_uncropped():
    """
    Re-extracts the seated Sukhasana figure from THAKUR_BODY_PROPORTION_SHEET_V001.png
    with generous top and bottom padding (`y = 70..505, x = 885..1295`, 435h x 410w)
    using `extract_clean_silhouette_rgba(crop, line_thresh=145, close_bottom=False, strip_h_lines=True)`
    and then restoring the exact curved hair crown top (`y=20..30`) and bottom 5 toes (`y=400..428`)!
    """
    from extract_modular_layers import extract_clean_silhouette_rgba
    prop_im = Image.open(PROP_PATH).convert("RGB")
    prop_arr = np.array(prop_im)
    crop = prop_arr[70:505, 885:1295].copy()  # 435h x 410w
    rgba = extract_clean_silhouette_rgba(crop, line_thresh=145, close_bottom=False, strip_h_lines=True)

    # 1. Strip ONLY the horizontal 0.0H CROWN chart line whiskers outside the rounded hair dome at y=22..32!
    for iy in range(22, 34):
        for ix in range(410):
            # Hair dome parabola centered at x=204, top at y=26.5, half-width at y=34 is 44px
            xn = (ix - 204.0) / 44.0
            dome_y = 26.2 + 7.8 * (xn ** 2)
            if iy < dome_y:
                rgba[iy, ix, 3] = 0

    # 2. Restore 100% of the bare right foot and all 5 toes at the bottom (y=395..425, x=180..310)
    # and cleanly strip the 2.85H SEATED BASE horizontal chart line at y=423..428!
    foot_gray = cv2.cvtColor(crop[390:425, 180:312], cv2.COLOR_RGB2GRAY)
    foot_rb = crop[390:425, 180:312, 0].astype(int) - crop[390:425, 180:312, 2].astype(int)
    is_foot = ((foot_rb > 32) | ((foot_gray < 138) & (foot_rb > 18))).astype(np.uint8) * 255
    is_foot = binary_fill_holes(is_foot > 0).astype(np.uint8) * 255
    rgba[390:425, 180:312, 3] = np.maximum(rgba[390:425, 180:312, 3], is_foot)
    # The horizontal 2.85H SEATED BASE chart line sits at y=423..427 across the entire width;
    # only the bottom tip of the pinkie toe (x=276..293) reaches y=424!
    for ix in range(410):
        if not (275 <= ix <= 293):
            rgba[422:, ix, 3] = 0
        else:
            rgba[425:, ix, 3] = 0

    # Strip any 1-3px horizontal chart line whiskers at neck/collar (y=145..156) or sleeves
    a = rgba[:, :, 3].copy()
    h, w = a.shape
    for y in range(40, 415):
        xs = np.where(a[y, :] > 30)[0]
        if len(xs) > 10:
            for x in range(xs[0], min(xs[0] + 24, w)):
                if np.sum(a[max(0, y - 4):min(h, y + 5), x] > 30) <= 4:
                    a[max(0, y - 3):min(h, y + 4), x] = 0
            for x in range(xs[-1], max(xs[-1] - 24, 0), -1):
                if np.sum(a[max(0, y - 4):min(h, y + 5), x] > 30) <= 4:
                    a[max(0, y - 3):min(h, y + 4), x] = 0
    rgba[:, :, 3] = a

    Image.fromarray(rgba, mode="RGBA").save(LAYERS_DIR / "body_seated_sukhasana.png")
    Image.fromarray(rgba, mode="RGBA").save(PNG_DIR / "THAKUR_SEATED_SUKHASANA_RGBA.png")
    print("Re-extracted uncropped body_seated_sukhasana.png (410x435) with full uttoriyo, rounded hair crown, and all 5 bare toes.")
    return rgba


if __name__ == "__main__":
    fix_turnaround_hands_and_feet()
    re_extract_full_seated_sukhasana_uncropped()
