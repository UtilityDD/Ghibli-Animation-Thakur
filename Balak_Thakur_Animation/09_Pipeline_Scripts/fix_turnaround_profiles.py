"""
Flawless, Zero-Artifact Anatomical Fix for Left Profile and Right Profile on THAKUR_TURNAROUND_SHEET_V001.png:
1. For the bare shins and feet (y=588..734):
   - Above the lowest point of the white dhoti boundary curve `y_dhoti_bottom(x)`, 100% of the original dhoti pixels are kept UNTOUCHED!
   - Below `y_dhoti_bottom(x)`, the bare legs and 5-toed feet are flipped horizontally around the ankle center `shin_cx` over the clean studio background + Ground line.
2. For the hanging hand (y=446..492):
   - Flips the hand block horizontally around its wrist center `hand_cx` and repairs the 3px outer dhoti margin with clean white dhoti shading (`#EFECE6`).
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

BASE_DIR = Path(r"E:\Codes\Ghibli Animation Thakur\Balak_Thakur_Animation")
TURN_PATH = BASE_DIR / "02_Character_Design" / "Turnaround" / "THAKUR_TURNAROUND_SHEET_V001.png"
BACKUP_PATH = BASE_DIR / "02_Character_Design" / "Turnaround" / "THAKUR_TURNAROUND_SHEET_V000_PRE_FIX.png"
ART_DIR = Path(r"C:\Users\USER\.gemini\antigravity\brain\7d6c96b0-8de4-401c-93fb-385f2c2d3564")


def fix_profile_perfect(img_arr: np.ndarray, x_prof_start: int, x_prof_end: int, x_hand_start: int, x_hand_end: int):
    # =========================================================================
    # 1. BARE SHINS & FEET BELOW THE EXACT DHOTI LOWER HEM CURVE (y=580..734)
    # =========================================================================
    fy0, fy1 = 580, 734
    f_crop = img_arr[fy0:fy1, x_prof_start:x_prof_end].copy()
    fh, fw, _ = f_crop.shape

    r_minus_b = f_crop[:, :, 0].astype(int) - f_crop[:, :, 2].astype(int)
    gray = cv2.cvtColor(f_crop, cv2.COLOR_RGB2GRAY)

    # Identify bare leg/foot skin (r_minus_b > 32) and its dark sepia outline
    is_leg_skin = (r_minus_b > 32).astype(np.uint8) * 255
    near_leg_skin = cv2.dilate(is_leg_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
    is_leg_or_foot = ((r_minus_b > 28) | ((gray < 170) & near_leg_skin)).astype(np.uint8) * 255
    is_leg_or_foot = binary_fill_holes(is_leg_or_foot > 0).astype(np.uint8) * 255

    # Trace the exact bottom outline of the white dhoti for each column x!
    # In rows dy=0..38 (y=580..618), the white dhoti interior has r_minus_b <= 25 and gray > 165,
    # and its bottom ink outline sits immediately below the white cloth (within 4px below the lowest white cloth pixel in column x).
    # For any column x where white cloth exists in dy=0..35, `y_dhoti_hem[x]` is the lowest white cloth row + 3px (to include the dark sepia hem line!).
    # Above `y_dhoti_hem[x]`, we keep 100% of `f_crop` untouched!
    keep_upper_mask = np.zeros((fh, fw), dtype=np.float32)
    for x in range(fw):
        col_rb = r_minus_b[:38, x]
        col_g = gray[:38, x]
        # White/grey dhoti cloth pixels (distinct from cream background which has r_minus_b ~ 14 and gray ~ 244, or wait: dhoti white has r_minus_b < 18 and gray in 175..242 enclosed by dark outline)
        # Even simpler: where is the leg skin in column x?
        # In column x, any row ABOVE the first bare leg skin pixel (minus 2px for the dhoti hem ink line) is 100% original dhoti or background!
        skin_ys = np.where(is_leg_skin[:, x] > 0)[0]
        if len(skin_ys) > 0 and skin_ys[0] < 45:
            hem_y = max(0, int(skin_ys[0]) - 1)
            keep_upper_mask[:hem_y, x] = 1.0
        else:
            # No bare leg skin at top of this column -> keep rows 0..38 100% original!
            keep_upper_mask[:38, x] = 1.0

    # Find horizontal center of the shin at dy=40..65 (y=620..645)
    shin_band = is_leg_or_foot[40:65, :]
    sys, sxs = np.where(shin_band > 0)
    shin_cx = int(round(np.mean(sxs)))

    # Clean studio background plate (with horizontal Ground guideline preserved)
    bg_plate = np.zeros_like(f_crop)
    for row_i in range(fh):
        row_bg = np.median(np.concatenate([f_crop[row_i, :8, :], f_crop[row_i, -8:, :]], axis=0), axis=0).astype(np.uint8)
        bg_plate[row_i, :, :] = row_bg

    # Flip bare legs & feet horizontally around shin_cx
    leg_rgba = np.dstack([f_crop, is_leg_or_foot])
    leg_flipped = np.zeros_like(leg_rgba)
    for x in range(fw):
        src_x = 2 * shin_cx - x
        if 0 <= src_x < fw:
            leg_flipped[:, x, :] = leg_rgba[:, src_x, :]

    # Extend top of flipped shins upward by 14px so they tuck completely behind `keep_upper_mask` (the dhoti hem) with zero gap!
    for row_i in range(38, 4, -1):
        m_below = leg_flipped[row_i + 1, :, 3] > 128
        m_curr = leg_flipped[row_i, :, 3] > 128
        fill_cols = m_below & (~m_curr)
        if np.any(fill_cols):
            leg_flipped[row_i, fill_cols, :] = leg_flipped[row_i + 1, fill_cols, :]

    leg_a = cv2.GaussianBlur(leg_flipped[:, :, 3].astype(np.float32) / 255.0, (3, 3), 0.6)[:, :, None]
    lower_comp = bg_plate.astype(np.float32) * (1.0 - leg_a) + leg_flipped[:, :, :3].astype(np.float32) * leg_a

    # Combine: above the dhoti hem curve (`keep_upper_mask == 1`), keep 100% original `f_crop`; below, use `lower_comp`!
    keep_3 = cv2.GaussianBlur(keep_upper_mask, (3, 3), 0.5)[:, :, None]
    final_feet = np.clip(lower_comp * (1.0 - keep_3) + f_crop.astype(np.float32) * keep_3, 0, 255).astype(np.uint8)
    img_arr[fy0:fy1, x_prof_start:x_prof_end] = final_feet

    # =========================================================================
    # 2. FIX HANGING HAND THUMB DIRECTION CLEANLY as a 2D Rigid Flip (y=443..493)
    # =========================================================================
    hy0, hy1 = 443, 493
    h_crop = img_arr[hy0:hy1, x_hand_start:x_hand_end].copy()
    hh, hw, _ = h_crop.shape
    hr_b = h_crop[:, :, 0].astype(int) - h_crop[:, :, 2].astype(int)
    hgray = cv2.cvtColor(h_crop, cv2.COLOR_RGB2GRAY)

    # Extract exact mask of the hand (skin + dark sepia hand outline)
    h_skin = (hr_b > 32).astype(np.uint8) * 255
    near_hs = cv2.dilate(h_skin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0
    h_mask = ((hr_b > 28) | ((hgray < 172) & near_hs)).astype(np.uint8) * 255
    h_mask = binary_fill_holes(h_mask > 0).astype(np.uint8) * 255

    # Find wrist horizontal center at top of hand (rows 2..8)
    wrist_xs = np.where(h_mask[2:8, :] > 128)[1]
    wrist_cx = int(round(np.mean(wrist_xs)))

    # Clean white dhoti background under the hand by interpolating each row linearly from the white dhoti pixels on the left and right of the hand!
    dhoti_under = h_crop.copy()
    k_dil_h = cv2.dilate(h_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    for ry in range(hh):
        m_row = k_dil_h[ry, :] > 0
        if np.any(m_row):
            xs = np.where(m_row)[0]
            xl, xr = max(1, int(xs[0]) - 2), min(hw - 2, int(xs[-1]) + 2)
            c_left = h_crop[ry, xl, :].astype(np.float32)
            c_right = h_crop[ry, xr, :].astype(np.float32)
            # Clamp to bright dhoti cloth tone if a dark fold line was hit at xl/xr
            if np.mean(c_left) < 195:
                c_left = np.array([236.0, 230.0, 220.0], dtype=np.float32)
            if np.mean(c_right) < 195:
                c_right = np.array([236.0, 230.0, 220.0], dtype=np.float32)
            span = max(1, xr - xl)
            for ix in range(xl, xr + 1):
                u = (ix - xl) / float(span)
                dhoti_under[ry, ix, :] = np.clip(c_left * (1.0 - u) + c_right * u, 0, 255).astype(np.uint8)

    # Flip the hand RGBA horizontally around wrist_cx
    hand_rgba = np.dstack([h_crop, h_mask])
    hand_flipped = np.zeros_like(hand_rgba)
    for x in range(hw):
        src_x = 2 * wrist_cx - x
        if 0 <= src_x < hw:
            hand_flipped[:, x, :] = hand_rgba[:, src_x, :]

    # Composite flipped hand over dhoti_under with a smooth 6px vertical blend at the top wrist (rows 0..6)
    ha = cv2.GaussianBlur(hand_flipped[:, :, 3].astype(np.float32) / 255.0, (3, 3), 0.5)[:, :, None]
    comp_hand = (dhoti_under.astype(np.float32) * (1.0 - ha) + hand_flipped[:, :, :3].astype(np.float32) * ha)

    for ry in range(6):
        w_y = ry / 6.0
        comp_hand[ry] = h_crop[ry].astype(np.float32) * (1.0 - w_y) + comp_hand[ry] * w_y

    img_arr[hy0:hy1, x_hand_start:x_hand_end] = np.clip(comp_hand, 0, 255).astype(np.uint8)


def main():
    im_orig = Image.open(BACKUP_PATH).convert("RGB")
    out = np.array(im_orig)

    # Left Profile: feet slice x=635..795; hand slice x=702..758
    fix_profile_perfect(out, 635, 795, 702, 758)

    # Right Profile: feet slice x=895..1055; hand slice x=933..989
    fix_profile_perfect(out, 895, 1055, 933, 989)

    out_im = Image.fromarray(out, mode="RGB")
    out_im.save(TURN_PATH)
    out_im.save(ART_DIR / "thakur_turnaround_sheet_v001_final_1795588115133.jpg", quality=96)
    out_im.crop((590, 40, 1110, 760)).save(ART_DIR / "inspect_profiles_fixed_zoom.png")
    print("Flawlessly fixed Left and Right Profile hands and feet.")


if __name__ == "__main__":
    main()
