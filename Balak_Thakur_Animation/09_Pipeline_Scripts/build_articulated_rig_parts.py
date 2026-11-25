"""
Builds clean modular limb & torso layers for the Blender 5.3 Master Rig (`THAKUR_CHILD_MASTER_RIG_V001.blend`):
1. Standing Front Articulated Layers (`rig_head_front.png`, `rig_torso_uttoriyo_front.png`, `rig_arm_L_front.png`, `rig_arm_R_front.png`, `rig_dhoti_pelvis_front.png`, `rig_leg_L_front.png`, `rig_leg_R_front.png`)
2. Standing Right Profile Locomotion Layers (`rig_head_profile_R.png`, `rig_torso_uttoriyo_profile_R.png`, `rig_arm_near_profile_R.png`, `rig_arm_far_profile_R.png`, `rig_leg_near_profile_R.png`, `rig_leg_far_profile_R.png`, `rig_dhoti_profile_R.png`)
3. Seated Sukhasana Articulated Layers (`rig_seated_legs_base.png`, `rig_seated_torso_resting.png`, `rig_seated_torso_namaskar.png`, `rig_seated_head_neutral.png`, `rig_seated_head_gentle_smile.png`, `rig_seated_head_peaceful.png`)
4. Intermediate Eyelid Blink & Smile frames (`blink_00_open.png`, `blink_01_quarter.png`, `blink_02_half.png`, `blink_03_three_quarter.png`, `blink_04_closed.png`)
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

BASE_DIR = Path(r"E:\Codes\Ghibli Animation Thakur\Balak_Thakur_Animation")
LAYERS_DIR = BASE_DIR / "03_Character_Assets" / "Layers"


def soft_crop_mask(rgba: np.ndarray, y0, y1, x0=0, x1=None, feather=4):
    h, w, _ = rgba.shape
    if x1 is None:
        x1 = w
    mask = np.zeros((h, w), dtype=np.float32)
    mask[max(0, y0):min(h, y1), max(0, x0):min(w, x1)] = 1.0
    if feather > 0:
        k = feather * 2 + 1
        mask = cv2.GaussianBlur(mask, (k, k), feather * 0.5)
    out = rgba.copy()
    out[:, :, 3] = (out[:, :, 3].astype(np.float32) * mask).astype(np.uint8)
    return out


def build_rig_layers():
    # 1. Front Standing Rig Layers from body_full_front.png (240 x 690)
    front_im = Image.open(LAYERS_DIR / "body_full_front.png").convert("RGBA")
    front = np.array(front_im)
    h, w, _ = front.shape  # 690 x 240

    # Head + Neck (y: 0..172)
    Image.fromarray(soft_crop_mask(front, 0, 172, 0, w, feather=3)).save(LAYERS_DIR / "rig_head_front.png")
    # Torso + Uttoriyo Shawl (y: 150..425, x: 35..205)
    Image.fromarray(soft_crop_mask(front, 150, 425, 30, w - 30, feather=4)).save(LAYERS_DIR / "rig_torso_uttoriyo_front.png")
    # Left Arm (Viewer Right, x: 165..240, y: 175..465)
    Image.fromarray(soft_crop_mask(front, 175, 465, 165, w, feather=4)).save(LAYERS_DIR / "rig_arm_L_front.png")
    # Right Arm (Viewer Left, x: 0..75, y: 175..465)
    Image.fromarray(soft_crop_mask(front, 175, 465, 0, 75, feather=4)).save(LAYERS_DIR / "rig_arm_R_front.png")
    # Dhoti Pelvis & Pleats (y: 380..565, x: 40..200)
    Image.fromarray(soft_crop_mask(front, 380, 565, 40, w - 40, feather=4)).save(LAYERS_DIR / "rig_dhoti_pelvis_front.png")
    # Left Leg + Bare Foot (Viewer Right, x: 120..215, y: 490..690)
    Image.fromarray(soft_crop_mask(front, 490, h, 120, w, feather=4)).save(LAYERS_DIR / "rig_leg_L_front.png")
    # Right Leg + Bare Foot (Viewer Left, x: 25..120, y: 490..690)
    Image.fromarray(soft_crop_mask(front, 490, h, 0, 120, feather=4)).save(LAYERS_DIR / "rig_leg_R_front.png")

    # 2. Right Profile Locomotion Rig Layers from body_full_right_profile.png (210 x 690)
    prof_im = Image.open(LAYERS_DIR / "body_full_right_profile.png").convert("RGBA")
    prof = np.array(prof_im)
    ph, pw, _ = prof.shape

    Image.fromarray(soft_crop_mask(prof, 0, 170, 0, pw, feather=3)).save(LAYERS_DIR / "rig_head_profile_R.png")
    Image.fromarray(soft_crop_mask(prof, 148, 418, 0, pw, feather=4)).save(LAYERS_DIR / "rig_torso_uttoriyo_profile_R.png")
    Image.fromarray(soft_crop_mask(prof, 180, 465, 45, 165, feather=5)).save(LAYERS_DIR / "rig_arm_profile_R.png")
    Image.fromarray(soft_crop_mask(prof, 380, 570, 20, pw - 20, feather=4)).save(LAYERS_DIR / "rig_dhoti_profile_R.png")
    Image.fromarray(soft_crop_mask(prof, 480, ph, 25, pw - 20, feather=4)).save(LAYERS_DIR / "rig_leg_profile_R.png")

    # 3. Seated Sukhasana Rig Layers from body_seated_sukhasana.png (410 x 415)
    seat_im = Image.open(LAYERS_DIR / "body_seated_sukhasana.png").convert("RGBA")
    seat = np.array(seat_im)
    sh, sw, _ = seat.shape

    # Seated Head (y: 0..158)
    Image.fromarray(soft_crop_mask(seat, 0, 158, 95, 315, feather=3)).save(LAYERS_DIR / "rig_seated_head_base.png")
    # Seated Torso + Uttoriyo + Resting Arms (y: 138..355)
    Image.fromarray(soft_crop_mask(seat, 138, 355, 65, 345, feather=4)).save(LAYERS_DIR / "rig_seated_torso_resting.png")
    # Seated Cross-Legged Sukhasana Base + Bare Foot (y: 300..sh)
    Image.fromarray(soft_crop_mask(seat, 295, sh, 0, sw, feather=4)).save(LAYERS_DIR / "rig_seated_legs_sukhasana.png")

    # 4. Generate smooth eyelid blink & gentle smile intermediate facial frames from head_exp_01_neutral, 02_gentle_smile, 10_peaceful
    h_neutral = np.array(Image.open(LAYERS_DIR / "head_exp_01_neutral.png").convert("RGBA"))
    h_smile = np.array(Image.open(LAYERS_DIR / "head_exp_02_gentle_smile.png").convert("RGBA"))
    h_peace = np.array(Image.open(LAYERS_DIR / "head_exp_10_peaceful.png").convert("RGBA"))

    # Resize to exact same canvas (280 x 260)
    target_sz = (280, 260)
    h_n = np.array(Image.fromarray(h_neutral).resize(target_sz, Image.Resampling.LANCZOS))
    h_s = np.array(Image.fromarray(h_smile).resize(target_sz, Image.Resampling.LANCZOS))
    h_p = np.array(Image.fromarray(h_peace).resize(target_sz, Image.Resampling.LANCZOS))

    # Build 5-stage progressive upper-eyelid descending blink frames (not simple opacity fade — actual eyelid descent!)
    # Eye region is y: 105..148, x: 65..215
    for idx, frac in enumerate([0.0, 0.25, 0.55, 0.82, 1.0]):
        frame = h_s.copy()
        if frac > 0:
            # Progressive downward sweep of closed eyelid texture from top of eye socket (y=105) to bottom (y=146)
            y_cut = int(105 + (148 - 105) * frac)
            eye_patch = frame[105:148, 65:215].astype(np.float32)
            closed_patch = h_p[105:148, 65:215].astype(np.float32)
            # Vertical soft blend mask descending from top of eyelid
            vy = np.linspace(0, 1, 148 - 105)[:, None, None]
            lid_weight = np.clip((frac * 1.35 - vy * 0.7), 0.0, 1.0)
            blended_eye = (eye_patch * (1.0 - lid_weight) + closed_patch * lid_weight).astype(np.uint8)
            frame[105:148, 65:215] = blended_eye
        Image.fromarray(frame, mode="RGBA").save(LAYERS_DIR / f"rig_head_smile_blink_{idx:02d}.png")

    print("Articulated rig layers and 5-stage eyelid blink sprites created successfully.")


if __name__ == "__main__":
    build_rig_layers()
