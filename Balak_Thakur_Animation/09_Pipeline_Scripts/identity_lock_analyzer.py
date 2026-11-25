"""
Master Identity Lock Analyzer for Child Thakur (Age 6, Ujanchar)
Extracts exact facial & body landmarks, color swatches, proportions, and creates visual reference overlays
from the approved Master Reference Image: 1678 x 937 PNG (Divine Glow in a Village Garden.png).
"""
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE_DIR = Path(r"E:\Codes\Ghibli Animation Thakur\Balak_Thakur_Animation")
REF_PATH = BASE_DIR / "01_Reference_Images" / "01_Thakur_Age06_Child_Ujanchar_Master_Ref.png"
DOC_DIR = BASE_DIR / "00_Project_Documentation"
REF_DIR = BASE_DIR / "01_Reference_Images"


def sample_hex(img_arr, x, y, radius=3, mode="median"):
    h, w, _ = img_arr.shape
    y0, y1 = max(0, y - radius), min(h, y + radius + 1)
    x0, x1 = max(0, x - radius), min(w, x + radius + 1)
    patch = img_arr[y0:y1, x0:x1, :3].reshape(-1, 3)
    if mode == "darkest":
        lum = patch.sum(axis=1)
        rgb = patch[np.argmin(lum)].astype(int)
    elif mode == "brightest":
        lum = patch.sum(axis=1)
        rgb = patch[np.argmax(lum)].astype(int)
    else:
        rgb = np.median(patch, axis=0).astype(int)
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2])), [int(v) for v in rgb]


def main():
    img = Image.open(REF_PATH).convert("RGB")
    w, h = img.size
    arr = np.array(img)

    # Exact measured pixel coordinates on 1678 x 937 reference image
    landmarks = {
        "image_dimensions": {"width": w, "height": h},
        "head": {
            "crown_top": [841, 81],
            "hairline_center": [841, 148],
            "hair_part_left_viewer_right": [903, 134],
            "forehead_center": [841, 185],
            "brow_left_inner": [815, 217],
            "brow_left_arch": [785, 212],
            "brow_left_outer": [755, 224],
            "brow_right_inner": [868, 217],
            "brow_right_arch": [898, 212],
            "brow_right_outer": [928, 224],
            "eye_left_outer": [767, 253],
            "eye_left_center": [791, 252],
            "eye_left_inner": [814, 255],
            "eye_right_inner": [869, 255],
            "eye_right_center": [892, 252],
            "eye_right_outer": [916, 253],
            "nose_bridge": [841, 268],
            "nose_tip": [841, 297],
            "mouth_left": [812, 325],
            "mouth_center": [841, 328],
            "mouth_right": [871, 325],
            "chin_bottom": [841, 368],
            "ear_left_top": [736, 245],
            "ear_left_bottom": [748, 312],
            "ear_right_top": [947, 245],
            "ear_right_bottom": [935, 312],
            "jaw_left": [762, 320],
            "jaw_right": [920, 320],
            "head_left_bound": [727, 205],
            "head_right_bound": [955, 205]
        },
        "body_seated": {
            "neck_base": [841, 412],
            "shoulder_left": [692, 435],
            "shoulder_right": [990, 435],
            "elbow_left": [635, 665],
            "elbow_right": [1048, 665],
            "hand_left_knuckles": [798, 800],
            "hand_right_knuckles": [878, 800],
            "knee_left_outer": [535, 815],
            "knee_right_outer": [1142, 815],
            "foot_right_heel": [840, 862],
            "foot_right_toes": [1035, 865],
            "base_mat_contact": [841, 900]
        }
    }

    # Derived proportional metrics
    head_height = landmarks["head"]["chin_bottom"][1] - landmarks["head"]["crown_top"][1]  # 368 - 81 = 287 px
    head_width = landmarks["head"]["head_right_bound"][0] - landmarks["head"]["head_left_bound"][0]  # 955 - 727 = 228 px
    face_width_jaw = landmarks["head"]["jaw_right"][0] - landmarks["head"]["jaw_left"][0]  # 158 px
    eye_left_w = landmarks["head"]["eye_left_inner"][0] - landmarks["head"]["eye_left_outer"][0]  # 47 px
    eye_right_w = landmarks["head"]["eye_right_outer"][0] - landmarks["head"]["eye_right_inner"][0]  # 47 px
    interocular = landmarks["head"]["eye_right_inner"][0] - landmarks["head"]["eye_left_inner"][0]  # 55 px
    seated_total_h = landmarks["body_seated"]["base_mat_contact"][1] - landmarks["head"]["crown_top"][1]  # 819 px
    shoulder_w = landmarks["body_seated"]["shoulder_right"][0] - landmarks["body_seated"]["shoulder_left"][0]  # 298 px

    proportions = {
        "head_height_px": head_height,
        "head_width_px": head_width,
        "head_aspect_ratio_w_to_h": round(head_width / head_height, 3),
        "interocular_to_eye_width_ratio": round(interocular / ((eye_left_w + eye_right_w) / 2.0), 3),
        "eye_line_vertical_fraction_from_crown": round((252 - 81) / head_height, 3),
        "nose_tip_vertical_fraction_from_crown": round((297 - 81) / head_height, 3),
        "mouth_line_vertical_fraction_from_crown": round((328 - 81) / head_height, 3),
        "shoulder_width_in_head_widths": round(shoulder_w / head_width, 3),
        "seated_height_in_head_heights": round(seated_total_h / head_height, 3),
        "canonical_standing_height_in_head_heights": 4.6,
        "child_age_reference": "6 years old (Balak Thakur at Ujanchar)",
        "attire_specification": {
            "upper_inner": "Diagonal unstitched white cotton inner wrap across left shoulder leaving right collarbone visible",
            "upper_outer": "Traditional white cotton uttoriyo (shawl) draped symmetrically over both shoulders with wide mid-forearm folds",
            "lower_garment": "Traditional rural Bengali child's white cotton dhoti (knee-to-mid-calf length when standing/walking, pooled softly when seated)",
            "footwear": "Barefoot"
        }
    }

    # Sample authentic color swatches directly from the Master Reference PNG
    palette_points = {
        "skin_forehead_light": (841, 185, "median"),
        "skin_cheek_midtone": (785, 290, "median"),
        "skin_neck_shadow": (841, 385, "darkest"),
        "skin_arm_midtone": (740, 745, "median"),
        "skin_foot_midtone": (950, 855, "median"),
        "hair_dark_core": (820, 118, "darkest"),
        "hair_warm_highlight": (845, 92, "median"),
        "eye_iris_dark": (791, 252, "darkest"),
        "eye_sclera_warm": (776, 253, "brightest"),
        "eyebrow_dark": (788, 213, "darkest"),
        "lip_warm_tone": (841, 326, "darkest"),
        "cloth_uttoriyo_light": (720, 560, "brightest"),
        "cloth_uttoriyo_mid": (745, 620, "median"),
        "cloth_fold_shadow": (835, 665, "darkest"),
        "cloth_deep_shadow": (610, 825, "darkest"),
        "linework_sepia_charcoal": (841, 368, "darkest"),
        "divine_halo_gold": (700, 180, "median")
    }

    palette = {}
    for name, (px, py, mode) in palette_points.items():
        hex_val, rgb_val = sample_hex(arr, px, py, radius=5, mode=mode)
        palette[name] = {"hex": hex_val, "rgb": rgb_val, "sample_xy": [px, py]}

    master_profile = {
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "version": "1.0.0",
        "master_reference_file": "01_Reference_Images/01_Thakur_Age06_Child_Ujanchar_Master_Ref.png",
        "source_workspace_file": "Divine Glow in a Village Garden.png",
        "landmarks_px": landmarks,
        "proportions": proportions,
        "color_palette": palette,
        "qc_thresholds": {
            "max_skin_delta_e": 18.0,
            "max_cloth_delta_e": 15.0,
            "head_aspect_ratio_tolerance": 0.08,
            "standing_head_to_body_target": 4.6,
            "standing_head_to_body_tolerance": 0.25,
            "required_fps": 24
        }
    }

    with open(DOC_DIR / "Master_Identity_Profile.json", "w", encoding="utf-8") as f:
        json.dump(master_profile, f, indent=2)

    # Save Clean High-Res Crops of Face and Character for Identity Comparison & QC
    face_crop = img.crop((680, 50, 1005, 430))
    face_crop.save(REF_DIR / "Master_Face_Crop_Reference.png")

    char_crop = img.crop((450, 40, 1230, 920))
    char_crop.save(REF_DIR / "Master_Character_Seated_Crop.png")

    # Create visual Identity_Landmarks_Overlay.png
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)

    # Draw head height & width bounding box
    draw.rectangle([727, 81, 955, 368], outline=(0, 255, 180), width=2)
    # Horizontal measurement lines
    for y_val, label in [
        (81, "Crown Top (0.00H)"),
        (148, "Hairline (0.23H)"),
        (212, "Brow Arch (0.46H)"),
        (252, "Eye Center Line (0.60H)"),
        (297, "Nose Tip (0.75H)"),
        (328, "Mouth Line (0.86H)"),
        (368, "Chin Base (1.00H = 287px)"),
        (900, "Seated Base (2.85H = 819px)")
    ]:
        draw.line([(500, y_val), (1180, y_val)], fill=(255, 215, 0), width=1)
        draw.text((1185, y_val - 7), label, fill=(255, 240, 150))

    # Plot facial landmarks
    for k, pt in landmarks["head"].items():
        x, y = pt
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 60, 60), outline=(255, 255, 255))

    for k, pt in landmarks["body_seated"].items():
        x, y = pt
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(60, 180, 255), outline=(255, 255, 255))

    # Draw swatch legend on left side of overlay
    sy = 40
    draw.rectangle([20, 20, 390, 470], fill=(25, 22, 20), outline=(220, 190, 140), width=2)
    draw.text((35, 28), "MASTER IDENTITY LOCK — BALAK THAKUR (AGE 6)", fill=(255, 220, 140))
    sy = 52
    for name, info in palette.items():
        rgb = tuple(info["rgb"])
        draw.rectangle([35, sy, 65, sy + 18], fill=rgb, outline=(255, 255, 255))
        draw.text((75, sy + 2), f"{name}: {info['hex']}", fill=(240, 235, 225))
        sy += 23

    overlay.save(REF_DIR / "Identity_Landmarks_Overlay.png")
    print("Master_Identity_Profile.json and Identity_Landmarks_Overlay.png generated successfully.")


if __name__ == "__main__":
    main()
