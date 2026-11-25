"""
Master Automated Quality Control (QC) Validator & Central Manifest Compiler for the Complete 56-Gesture Library
Scans all 8 category directories under `04_Gesture_Library/`:
- Facial, Head, Hands, Sitting, Devotional, Walking, Running, Emotional
Verifies every single animation for:
1. Character Consistency (Palette lock against Master_Identity_Profile.json)
2. Animation Quality (24 FPS active motion, zero flicker/jumps)
3. Export Quality (32-bit RGBA PNG sequence, .blend project file, MP4, GIF, Transparent WebM, JSON metadata)
4. Generates `07_Production_Tests/Full_Library_56_Animations_QC_Report.json` and visual overview board `07_Production_Tests/Full_Library_56_Animations_Overview_Board.png`.
5. Updates `08_Final_Approved_Assets/asset_manifest.json` with all 56 approved animations.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

from validate_pilot_v1 import (
    BASE_DIR, DOC_DIR, GESTURE_DIR, PREVIEW_DIR, TEST_DIR, APPROVED_DIR,
    load_master_profile, validate_animation_asset
)


def main():
    profile = load_master_profile()
    categories = ["Facial", "Head", "Hands", "Sitting", "Devotional", "Walking", "Running", "Emotional"]

    all_qc_reports = {}
    all_manifest_entries = []
    thumbnails = []

    for cat in categories:
        cat_dir = GESTURE_DIR / cat
        if not cat_dir.exists():
            continue
        for anim_dir in sorted(cat_dir.iterdir()):
            if not anim_dir.is_dir():
                continue
            frames_dir = anim_dir / "frames"
            if not frames_dir.exists():
                continue
            asset_id = anim_dir.name
            pngs = sorted(frames_dir.glob(f"{asset_id}_*.png"))
            if not pngs:
                continue

            rep, samples = validate_animation_asset(asset_id, cat, len(pngs), profile)
            all_qc_reports[asset_id] = rep

            # Pick middle frame (50%) for visual overview board
            mid_rgba = samples[len(samples) // 2]
            thumbnails.append((asset_id, cat, len(pngs), rep["status"], mid_rgba))

            meta_file = anim_dir / f"{asset_id}_metadata.json"
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as mf:
                    meta_data = json.load(mf)
                meta_data["qc_status"] = rep["status"]
                meta_data["approval_status"] = "APPROVED_V1" if rep["status"] == "PASS" else "NEEDS_REVIEW"
                meta_data["editable_blend_file"] = f"04_Gesture_Library/{cat}/{asset_id}/{asset_id}.blend"
                with open(meta_file, "w", encoding="utf-8") as mf:
                    json.dump(meta_data, mf, indent=2)
                all_manifest_entries.append(meta_data)

    # Save Full_Library_56_Animations_QC_Report.json
    total_count = len(all_qc_reports)
    pass_count = sum(1 for r in all_qc_reports.values() if r["status"] == "PASS")
    summary_payload = {
        "total_animations_validated": total_count,
        "total_passed": pass_count,
        "total_failed": total_count - pass_count,
        "target_fps": 24,
        "reports": all_qc_reports
    }
    with open(TEST_DIR / "Full_Library_56_Animations_QC_Report.json", "w", encoding="utf-8") as qf:
        json.dump(summary_payload, qf, indent=2)

    # Update Central Asset Manifest (08_Final_Approved_Assets/asset_manifest.json)
    manifest_path = APPROVED_DIR / "asset_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as mf:
        manifest = json.load(mf)
    manifest["total_approved_animations"] = pass_count
    manifest["animations"] = all_manifest_entries
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    # Build Visual Master Overview Contact Board (8 columns x 7 rows = 56 cells)
    cols = 8
    rows = (len(thumbnails) + cols - 1) // cols
    cell_w, cell_h = 220, 245
    board_w = 40 + cols * cell_w
    board_h = 90 + rows * cell_h + 20
    board = Image.new("RGB", (board_w, board_h), (24, 22, 20))
    draw = ImageDraw.Draw(board)

    draw.text((30, 18), f"PRAM BISMOY BALAK THAKUR — COMPLETE 24 FPS REUSABLE GESTURE LIBRARY ({total_count} ANIMATIONS | {pass_count}/{total_count} QC PASS)", fill=(255, 220, 140))
    draw.text((30, 44), "Categories A-F: Facial (10) | Head (8) | Hands (10) | Sitting & Devotional (10) | Full-Body Locomotion (10) | Emotional Storytelling (8)", fill=(205, 195, 180))

    for idx, (asset_id, cat, fcount, status, rgba_arr) in enumerate(thumbnails):
        r = idx // cols
        c = idx % cols
        x0 = 20 + c * cell_w
        y0 = 80 + r * cell_h

        # Checkerboard thumbnail box (204 x 190)
        tw, th = 204, 190
        chk = np.zeros((th, tw, 3), dtype=np.uint8)
        for cy in range(0, th, 16):
            for cx in range(0, tw, 16):
                c_val = (242, 236, 224) if ((cy // 16 + cx // 16) % 2 == 0) else (222, 214, 200)
                chk[cy:cy + 16, cx:cx + 16] = c_val

        thumb_pil = Image.fromarray(rgba_arr, mode="RGBA").resize((tw, th), Image.Resampling.LANCZOS)
        chk_pil = Image.fromarray(chk, mode="RGB").convert("RGBA")
        comp = Image.alpha_composite(chk_pil, thumb_pil).convert("RGB")
        board.paste(comp, (x0, y0))
        draw.rectangle([x0, y0, x0 + tw, y0 + th], outline=(160, 140, 110), width=1)

        short_name = asset_id.replace("THAKUR_", "").replace("_V001", "")
        draw.text((x0 + 2, y0 + th + 4), f"{idx + 1}. {short_name[:24]}", fill=(245, 225, 175))
        draw.text((x0 + 2, y0 + th + 22), f"[{cat}] {fcount}f @ 24fps | {status}", fill=(0, 235, 160))

    board_path = TEST_DIR / "Full_Library_56_Animations_Overview_Board.png"
    board.save(board_path)
    print(f"Validated {total_count} animations ({pass_count} PASS). Master board saved to {board_path}")


if __name__ == "__main__":
    main()
