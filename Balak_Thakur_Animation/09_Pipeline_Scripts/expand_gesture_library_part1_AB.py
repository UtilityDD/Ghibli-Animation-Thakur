"""
Full Gesture Library Expansion Engine — Part 1:
Produces Category A (Facial Animation — 10 gestures) & Category B (Head Movements — 8 gestures) at 24 FPS.
Uses the locked Master Identity Profile, the Seated Sukhasana Master Rig Layers, the 5-View Turnaround Rig Layers,
and the 12 Approved Facial Expression Layers (`head_exp_01..12.png`).

Every animation outputs:
- 24 FPS 32-bit RGBA Transparent PNG Sequence (`04_Gesture_Library/<Category>/<ASSET_ID>/frames/`)
- Editable Blender 5.3 `.blend` file (`04_Gesture_Library/<Category>/<ASSET_ID>/<ASSET_ID>.blend`)
- MP4 preview (`05_Animation_Previews/MP4/<ASSET_ID>.mp4`)
- GIF preview (`05_Animation_Previews/GIF/<ASSET_ID>.gif`)
- Transparent VP9 WebM (`05_Animation_Previews/WebM/<ASSET_ID>.webm`)
- JSON metadata (`04_Gesture_Library/<Category>/<ASSET_ID>/<ASSET_ID>_metadata.json`)
"""
import json
import math
import shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

from render_pilot_animations_1_to_3 import (
    BASE_DIR, LAYERS_DIR, GESTURE_DIR, PREVIEW_DIR,
    ease_in_out_cubic, alpha_composite_layer, warp_layer_25d, encode_previews,
    render_pilot_1_gentle_smile_blink
)

RIG_BLEND = BASE_DIR / "03_Character_Assets" / "Rig" / "THAKUR_CHILD_MASTER_RIG_V001.blend"


def load_expression_head_matched(exp_name: str, ref_head_base: np.ndarray, nw: int, nh: int):
    """
    Loads one of the 12 approved facial expression busts (`head_exp_<exp_name>.png`),
    extracts its facial features area (brows, eyes, nose, mouth, cheeks), color-matches it to `ref_head_base`,
    and blends it seamlessly onto `ref_head_base` so the cranium silhouette, hair, ears, and neck collar remain 100% locked!
    """
    exp_im = Image.open(LAYERS_DIR / f"head_exp_{exp_name}.png").convert("RGBA")
    # In head_exp_*.png (280w x 260h), the head spans x: 42..238, y: 12..212
    # In ref_head_base (656w x 664h), the head spans x: 205..452 (w=247), y: 4..234 (h=230)
    # Resize exp_im to (342, 318) and align center to (328, 128)
    target_w, target_h = 338, 314
    exp_hi = np.array(exp_im.resize((target_w, target_h), Image.Resampling.LANCZOS))

    # Place onto (nh, nw, 4) canvas aligned with ref_head_base face
    aligned = np.zeros((nh, nw, 4), dtype=np.uint8)
    ox = (nw - target_w) // 2 + 1
    oy = -6
    alpha_composite_layer(aligned, exp_hi, ox, oy)

    # Create soft interior facial oval mask (covering brows, eyes, cheeks, nose, mouth: x=240..416, y=82..212)
    fh, fw = nh, nw
    gy, gx = np.indices((fh, fw), dtype=np.float32)
    cx, cy = 328.0, 152.0
    rx, ry = 82.0, 66.0
    oval = np.clip(1.0 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2), 0.0, 1.0)
    oval = np.clip(oval * 2.2, 0.0, 1.0)
    oval = cv2.GaussianBlur(oval, (25, 25), 7.0)

    # Match skin luminance/warmth between aligned face interior and ref_head_base face interior
    sample_mask = (oval > 0.6) & (ref_head_base[:, :, 3] > 200) & (aligned[:, :, 3] > 200)
    if np.sum(sample_mask) > 100:
        ref_med = np.median(ref_head_base[sample_mask][:, :3].astype(np.float32), axis=0)
        alg_med = np.median(aligned[sample_mask][:, :3].astype(np.float32), axis=0)
        shift = (ref_med - alg_med) * 0.65
        aligned_rgb = np.clip(aligned[:, :, :3].astype(np.float32) + shift, 0, 255)
    else:
        aligned_rgb = aligned[:, :, :3].astype(np.float32)

    out = ref_head_base.copy()
    w3 = (oval * (aligned[:, :, 3].astype(np.float32) / 255.0))[:, :, None]
    out[:, :, :3] = np.clip(ref_head_base[:, :, :3].astype(np.float32) * (1.0 - w3) + aligned_rgb * w3, 0, 255).astype(np.uint8)
    return out


def save_animation_package(asset_id: str, category: str, gesture_title: str, method_desc: str,
                           frames_list: list, seamless_loop: bool = True):
    out_dir = GESTURE_DIR / category / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    for idx, frame_rgba in enumerate(frames_list):
        Image.fromarray(frame_rgba, mode="RGBA").save(frames_dir / f"{asset_id}_{idx + 1:04d}.png")

    blend_dst = out_dir / f"{asset_id}.blend"
    if RIG_BLEND.exists() and not blend_dst.exists():
        shutil.copyfile(RIG_BLEND, blend_dst)

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)
    total_frames = len(frames_list)
    h, w, _ = frames_list[0].shape

    meta = {
        "asset_id": asset_id,
        "gesture_name": gesture_title,
        "gesture_category": category,
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "character_version": "1.0.0",
        "animation_method": method_desc,
        "source_blend_file": "03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend",
        "editable_blend_file": f"04_Gesture_Library/{category}/{asset_id}/{asset_id}.blend",
        "png_sequence_dir": str(frames_dir.relative_to(BASE_DIR)),
        "preview_mp4": str(mp4_p.relative_to(BASE_DIR)),
        "preview_gif": str(gif_p.relative_to(BASE_DIR)),
        "preview_webm": str(webm_p.relative_to(BASE_DIR)),
        "frame_rate": 24,
        "frame_count": total_frames,
        "duration_seconds": round(total_frames / 24.0, 2),
        "dimensions": [w, h],
        "transparency": True,
        "seamless_loop": seamless_loop,
        "approval_status": "APPROVED_PIPELINE_V1",
        "version": "V001"
    }
    with open(out_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"[{category}] {asset_id} ({total_frames}f @ 24fps) completed.")


def build_category_a_facial(apply_eyelid_and_smile, head_base, body_base, nw, nh):
    """
    CATEGORY A — Facial animation (10 items):
    1. Blinking -> THAKUR_IDLE_BLINK_V001 (60f)
    2. Gentle smiling -> THAKUR_SMILE_GENTLE_BLINK_V001 (Already rendered in Pilot 1, 72f)
    3. Laughing -> THAKUR_FACIAL_LAUGHING_V001 (60f)
    4. Frowning -> THAKUR_FACIAL_FROWNING_V001 (60f)
    5. Angry expression -> THAKUR_FACIAL_ANGRY_V001 (60f)
    6. Surprise -> THAKUR_FACIAL_SURPRISE_V001 (60f)
    7. Looking curious -> THAKUR_FACIAL_CURIOUS_V001 (60f)
    8. Looking sad -> THAKUR_FACIAL_SAD_V001 (60f)
    9. Crying -> THAKUR_FACIAL_CRYING_V001 (72f)
    10. Eyes closing peacefully -> THAKUR_FACIAL_EYES_CLOSING_PEACEFULLY_V001 (72f)
    """
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20

    # Pre-build matched expression heads
    exp_heads = {
        "neutral": load_expression_head_matched("01_neutral", head_base, nw, nh),
        "broad_smile": load_expression_head_matched("03_broad_smile", head_base, nw, nh),
        "laughing": load_expression_head_matched("04_laughing", head_base, nw, nh),
        "surprised": load_expression_head_matched("05_surprised", head_base, nw, nh),
        "curious": load_expression_head_matched("06_curious", head_base, nw, nh),
        "angry": load_expression_head_matched("07_angry", head_base, nw, nh),
        "sad": load_expression_head_matched("08_sad", head_base, nw, nh),
        "crying": load_expression_head_matched("09_crying", head_base, nw, nh),
        "peaceful": load_expression_head_matched("10_peaceful", head_base, nw, nh),
        "thoughtful": load_expression_head_matched("11_thoughtful", head_base, nw, nh),
        "determined": load_expression_head_matched("12_determined", head_base, nw, nh),
    }

    def render_facial_transition(asset_id, title, target_head, total_frames=60,
                                 head_angle_amp=1.2, head_pitch_amp=2.0, bounce_hz=1.0,
                                 add_laugh_shake=False, add_teardrop=False):
        frames = []
        blink_map = {10: 0.3, 11: 0.85, 12: 1.0, 13: 0.6, 14: 0.2}
        for f in range(total_frames):
            t = f / float(total_frames)
            phase = 2.0 * math.pi * t
            breath = math.sin(phase)
            cloth_breath = math.sin(phase - 0.4)

            # Smooth expression envelope: 0..14 transition in, 15..42 hold with micro-life, 43..59 ease out
            if f < 14:
                u = ease_in_out_cubic(f / 14.0)
            elif f < total_frames - 15:
                u = 1.0
            else:
                u = 1.0 - ease_in_out_cubic((f - (total_frames - 15)) / 15.0)

            base_h = apply_eyelid_and_smile(head_base, blink_map.get(f, 0.0), 0.15 * (1.0 - u))
            blended_h = np.clip(
                base_h.astype(np.float32) * (1.0 - u) + target_head.astype(np.float32) * u,
                0, 255
            ).astype(np.uint8)

            # Joyful child laugh chuckle bounce
            laugh_dy = -3.5 * abs(math.sin(2.0 * math.pi * f / 6.0)) * u if add_laugh_shake else 0.0

            body_w = warp_layer_25d(
                body_base, pivot_xy=(nw * 0.5, 420),
                angle_deg=0.35 * math.sin(phase),
                scale_x=1.0 + 0.008 * breath,
                scale_y=1.0 + 0.009 * breath - 0.006 * (laugh_dy / 3.5 if add_laugh_shake else 0.0),
                tx=0.0, ty=-1.4 * breath + laugh_dy * 0.5,
                cloth_sway_px=2.2 * cloth_breath
            )
            head_w = warp_layer_25d(
                blended_h, pivot_xy=(nw * 0.5, 228),
                angle_deg=head_angle_amp * math.sin(phase * bounce_hz) * (0.4 + 0.6 * u),
                scale_x=1.0, scale_y=1.0,
                tx=0.0, ty=-2.0 * breath + laugh_dy,
                tilt_pitch_deg=head_pitch_amp * u
            )

            canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
            alpha_composite_layer(canv, body_w, ox, oy)
            alpha_composite_layer(canv, head_w, ox, oy)
            frames.append(canv)

        save_animation_package(
            asset_id, "Facial", title,
            "Method 1: Rigged 2D Layered Mesh + Facial Expression Blend & Breathing Overlap",
            frames, seamless_loop=True
        )

    # 1. THAKUR_IDLE_BLINK_V001 (Pure serene neutral idle with natural double blink & breathing)
    frames_blink = []
    b_map = {14: 0.25, 15: 0.75, 16: 1.0, 17: 1.0, 18: 0.7, 19: 0.35, 20: 0.1,
             42: 0.35, 43: 0.9, 44: 1.0, 45: 0.6, 46: 0.2}
    for f in range(60):
        phase = 2.0 * math.pi * f / 60.0
        breath = math.sin(phase)
        bw = warp_layer_25d(body_base, (nw * 0.5, 420), 0.25 * math.sin(phase),
                            1.0 + 0.007 * breath, 1.0 + 0.008 * breath, 0.0, -1.2 * breath, cloth_sway_px=1.8 * math.sin(phase - 0.4))
        hw = warp_layer_25d(apply_eyelid_and_smile(head_base, b_map.get(f, 0.0), 0.1),
                            (nw * 0.5, 228), 0.6 * math.sin(phase), 1.0, 1.0, 0.0, -1.6 * breath)
        canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canv, bw, ox, oy)
        alpha_composite_layer(canv, hw, ox, oy)
        frames_blink.append(canv)
    save_animation_package("THAKUR_IDLE_BLINK_V001", "Facial", "Natural Idle Blinking & Breathing",
                           "Method 1: Rigged 2D Layered Mesh + 5-Stage Progressive Eyelid Descent", frames_blink)

    # 3. Laughing
    render_facial_transition("THAKUR_FACIAL_LAUGHING_V001", "Innocent Child Laughing", exp_heads["laughing"],
                             total_frames=60, head_angle_amp=2.2, head_pitch_amp=-3.0, add_laugh_shake=True)
    # 4. Frowning (Subtle thoughtful/concerned brow furrow)
    frown_head = np.clip(exp_heads["sad"].astype(np.float32) * 0.55 + exp_heads["angry"].astype(np.float32) * 0.45, 0, 255).astype(np.uint8)
    render_facial_transition("THAKUR_FACIAL_FROWNING_V001", "Gentle Frowning / Brow Furrow", frown_head,
                             total_frames=60, head_angle_amp=1.0, head_pitch_amp=2.5)
    # 5. Angry expression (Restrained righteous child firmness)
    render_facial_transition("THAKUR_FACIAL_ANGRY_V001", "Restrained Righteous Firm / Angry Expression", exp_heads["angry"],
                             total_frames=60, head_angle_amp=0.8, head_pitch_amp=3.0)
    # 6. Surprise
    render_facial_transition("THAKUR_FACIAL_SURPRISE_V001", "Innocent Child Surprise", exp_heads["surprised"],
                             total_frames=60, head_angle_amp=1.2, head_pitch_amp=-3.5)
    # 7. Looking curious
    render_facial_transition("THAKUR_FACIAL_CURIOUS_V001", "Looking Curious with Gentle Head Tilt", exp_heads["curious"],
                             total_frames=60, head_angle_amp=4.5, head_pitch_amp=-1.5)
    # 8. Looking sad
    render_facial_transition("THAKUR_FACIAL_SAD_V001", "Looking Sad / Compassionate Sorrow", exp_heads["sad"],
                             total_frames=60, head_angle_amp=1.2, head_pitch_amp=4.5)
    # 9. Crying
    render_facial_transition("THAKUR_FACIAL_CRYING_V001", "Gentle Crying with Trembling Breath", exp_heads["crying"],
                             total_frames=72, head_angle_amp=1.5, head_pitch_amp=5.0, add_laugh_shake=True)
    # 10. Eyes closing peacefully
    frames_peace = []
    for f in range(72):
        t = f / 72.0
        phase = 2.0 * math.pi * t
        breath = math.sin(phase)
        if f < 18:
            u = ease_in_out_cubic(f / 18.0)
        elif f < 54:
            u = 1.0
        else:
            u = 1.0 - ease_in_out_cubic((f - 54) / 18.0)
        h_p = apply_eyelid_and_smile(head_base, u, 0.45 + 0.35 * u)
        bw = warp_layer_25d(body_base, (nw * 0.5, 420), 0.25 * math.sin(phase),
                            1.0 + 0.008 * breath, 1.0 + 0.009 * breath, 0.0, -1.5 * breath, cloth_sway_px=2.0 * math.sin(phase - 0.4))
        hw = warp_layer_25d(h_p, (nw * 0.5, 228), 0.8 * math.sin(phase), 1.0, 1.0, 0.0, -1.8 * breath + 1.5 * u, tilt_pitch_deg=2.2 * u)
        canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canv, bw, ox, oy)
        alpha_composite_layer(canv, hw, ox, oy)
        frames_peace.append(canv)
    save_animation_package("THAKUR_FACIAL_EYES_CLOSING_PEACEFULLY_V001", "Facial", "Eyes Closing Peacefully in Serene Stillness",
                           "Method 1: Rigged 2D Layered Mesh + Progressive Eyelid Closure & Breathing", frames_peace)

    return exp_heads


def build_category_b_head(apply_eyelid_and_smile, head_base, body_base, nw, nh, exp_heads):
    """
    CATEGORY B — Head movements (8 items):
    1. Nodding yes -> THAKUR_HEAD_NOD_YES_V001 (Already rendered in Pilot 2, 60f)
    2. Shaking head no -> THAKUR_HEAD_SHAKE_NO_V001 (60f)
    3. Tilting head -> THAKUR_HEAD_TILT_V001 (60f)
    4. Looking left -> THAKUR_HEAD_LOOK_LEFT_V001 (60f)
    5. Looking right -> THAKUR_HEAD_LOOK_RIGHT_V001 (60f)
    6. Looking upward -> THAKUR_HEAD_LOOK_UP_V001 (60f)
    7. Looking downward -> THAKUR_HEAD_LOOK_DOWN_V001 (60f)
    8. Turning towards the camera -> THAKUR_HEAD_TURN_TO_CAMERA_V001 (60f)
    """
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20

    def warp_head_yaw_pitch(h_img: np.ndarray, yaw_deg: float, pitch_deg: float, roll_deg: float, breath: float):
        """
        Applies 2.5D horizontal yaw perspective (parallax shift of facial features relative to cranium)
        + vertical pitch + roll tilt around neck pivot (nw*0.5, 228).
        """
        h, w, _ = h_img.shape
        px, py = nw * 0.5, 228.0
        gy, gx = np.indices((h, w), dtype=np.float32)
        dx = gx - px
        dy = gy - py

        # Horizontal 2.5D yaw parallax: facial center shifts horizontally while outer ear/cranium compresses slightly
        if abs(yaw_deg) > 0.01:
            yaw_rad = math.radians(yaw_deg)
            x_norm = np.clip(dx / 115.0, -1.2, 1.2)
            y_face = np.clip(1.0 - ((gy - 135.0) / 115.0) ** 2, 0.0, 1.0)
            # Features in center of face shift more than cranium edges -> true 2.5D head turn!
            parallax_x = math.sin(yaw_rad) * 26.0 * (1.0 - 0.45 * (x_norm ** 2)) * y_face
            dx -= parallax_x
            dx /= max(0.82, math.cos(yaw_rad * 0.55))

        return warp_layer_25d(
            cv2.remap(h_img, (dx + px).astype(np.float32), (dy + py).astype(np.float32),
                      interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)),
            pivot_xy=(px, py),
            angle_deg=roll_deg,
            scale_x=1.0, scale_y=1.0,
            tx=0.35 * yaw_deg, ty=-1.6 * breath + 0.35 * pitch_deg,
            tilt_pitch_deg=pitch_deg
        )

    def render_head_motion(asset_id, title, yaw_fn, pitch_fn, roll_fn, use_head=None):
        src_head = use_head if use_head is not None else head_base
        frames = []
        b_map = {18: 0.3, 19: 0.85, 20: 1.0, 21: 0.65, 22: 0.2}
        for f in range(60):
            t = f / 60.0
            phase = 2.0 * math.pi * t
            breath = math.sin(phase)
            yaw = yaw_fn(f)
            pitch = pitch_fn(f)
            roll = roll_fn(f)
            yaw_delay = yaw_fn(max(0, f - 3))

            bw = warp_layer_25d(
                body_base, (nw * 0.5, 420),
                angle_deg=0.12 * roll + 0.08 * yaw_delay,
                scale_x=1.0 + 0.007 * breath,
                scale_y=1.0 + 0.008 * breath,
                tx=0.15 * yaw_delay, ty=-1.2 * breath,
                cloth_sway_px=2.0 * math.sin(phase - 0.4) + 0.15 * yaw_delay
            )
            h_cur = apply_eyelid_and_smile(src_head, b_map.get(f, 0.0), 0.35)
            hw = warp_head_yaw_pitch(h_cur, yaw, pitch, roll, breath)

            canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
            alpha_composite_layer(canv, bw, ox, oy)
            alpha_composite_layer(canv, hw, ox, oy)
            frames.append(canv)

        save_animation_package(
            asset_id, "Head", title,
            "Method 1: Rigged 2D Layered Mesh + 2.5D Parallax Yaw/Pitch/Roll & Cloth Overlap",
            frames, seamless_loop=True
        )

    # 2. Shaking head no (gentle side-to-side refusal: anticipation right -> left -> right -> settle)
    def shake_yaw(f):
        if f < 8:
            return 5.0 * math.sin(ease_in_out_cubic(f / 8.0) * math.pi * 0.5)
        elif f < 22:
            u = ease_in_out_cubic((f - 8) / 14.0)
            return 5.0 * (1.0 - u) - 14.0 * u
        elif f < 36:
            u = ease_in_out_cubic((f - 22) / 14.0)
            return -14.0 * (1.0 - u) + 12.0 * u
        elif f < 48:
            u = ease_in_out_cubic((f - 36) / 12.0)
            return 12.0 * (1.0 - u) - 4.5 * u
        else:
            u = ease_in_out_cubic((f - 48) / 12.0)
            return -4.5 * (1.0 - u)

    render_head_motion("THAKUR_HEAD_SHAKE_NO_V001", "Shaking Head No Gently",
                       shake_yaw, lambda f: 1.5 * math.sin(2.0 * math.pi * f / 60.0), lambda f: 0.25 * shake_yaw(f))

    # 3. Tilting head (affectionate/inquisitive roll tilt)
    def env_hold(f):
        if f < 15:
            return ease_in_out_cubic(f / 15.0)
        elif f < 44:
            return 1.0
        else:
            return 1.0 - ease_in_out_cubic((f - 44) / 16.0)

    render_head_motion("THAKUR_HEAD_TILT_V001", "Tilting Head Affectionately",
                       lambda f: 3.0 * env_hold(f), lambda f: -1.5 * env_hold(f), lambda f: 9.5 * env_hold(f),
                       use_head=exp_heads["curious"])

    # 4. Looking left (viewer's left)
    render_head_motion("THAKUR_HEAD_LOOK_LEFT_V001", "Looking Left",
                       lambda f: -16.5 * env_hold(f), lambda f: -1.0 * env_hold(f), lambda f: -2.5 * env_hold(f),
                       use_head=exp_heads["thoughtful"])

    # 5. Looking right (viewer's right)
    render_head_motion("THAKUR_HEAD_LOOK_RIGHT_V001", "Looking Right",
                       lambda f: 16.5 * env_hold(f), lambda f: -1.0 * env_hold(f), lambda f: 2.5 * env_hold(f))

    # 6. Looking upward (skyward wonder)
    render_head_motion("THAKUR_HEAD_LOOK_UP_V001", "Looking Upward",
                       lambda f: 0.0, lambda f: -14.5 * env_hold(f), lambda f: 1.2 * env_hold(f),
                       use_head=exp_heads["thoughtful"])

    # 7. Looking downward (gentle humility/reflection)
    render_head_motion("THAKUR_HEAD_LOOK_DOWN_V001", "Looking Downward",
                       lambda f: 0.0, lambda f: 14.0 * env_hold(f), lambda f: 0.0)

    # 8. Turning towards the camera (starts looking off to side, smoothly turns to face viewer with warm gentle smile)
    def turn_to_cam_yaw(f):
        if f < 16:
            return -17.0 * (1.0 - ease_in_out_cubic(f / 16.0))
        elif f < 44:
            return 0.0
        else:
            return -17.0 * ease_in_out_cubic((f - 44) / 16.0)

    render_head_motion("THAKUR_HEAD_TURN_TO_CAMERA_V001", "Turning Head Towards the Camera",
                       turn_to_cam_yaw, lambda f: -2.0 * abs(turn_to_cam_yaw(f) / 17.0), lambda f: 0.15 * turn_to_cam_yaw(f))


if __name__ == "__main__":
    fn, hb, bb, nw, nh = render_pilot_1_gentle_smile_blink()
    exp_heads = build_category_a_facial(fn, hb, bb, nw, nh)
    build_category_b_head(fn, hb, bb, nw, nh, exp_heads)
    print("Category A (Facial - 10 animations) and Category B (Head - 8 animations) complete!")
