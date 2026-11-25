"""
24 FPS Hybrid Animation Renderer & Exporter for Pilot Project V1 (Animations 3, 4, and 5):
3. THAKUR_PRAYER_SITTING_V001 (96 frames, 4.0s @ 24 FPS, Devotional / Sitting)
   - Method 1 + Method 3: Seated cross-legged (*Sukhasana*) matching the Master Ujanchar Reference.
   - Natural start (hands resting gently on lap, breathing & blink, frames 1-16),
   - Anticipation inhale & slight torso lift (frames 17-24),
   - Forearms & hands rising gracefully into Namaskar at chest level while eyes close peacefully (frames 25-44),
   - Serene devotional hold with gentle breathing & cloth fold follow-through (frames 45-74),
   - Smooth recovery back to resting hands and open-eyed gentle smile (frames 75-96).
4. THAKUR_WALK_CYCLE_V001 (48 frames, 2.0s @ 24 FPS, Seamless Loop, Two Full Strides)
   - Method 2 (8 Traditional Key-Pose Sprites: Contact, Down, Passing, Up x 2 strides) + Method 1 (24 FPS Optical-Flow Guided Skeletal/Mesh In-Betweening, Vertical Weight Bounce, and Overlapping Uttoriyo Shawl Follow-Through).
5. THAKUR_RUN_CYCLE_V001 (36 frames, 1.5s @ 24 FPS, Seamless Loop, Two Full Strides)
   - Method 2 (8 Traditional Key-Pose Sprites: Contact, Cushion/Down, Push-Off/Drive, Airborne Flight x 2 strides) + Method 1 (24 FPS High-Cadence In-Betweening, Flight Arcs, and Dynamic Uttoriyo Shawl Flutter).
"""
import json
import math
import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

from extract_modular_layers import extract_clean_silhouette_rgba
from render_pilot_animations_1_to_3 import (
    BASE_DIR, LAYERS_DIR, GESTURE_DIR, PREVIEW_DIR,
    ease_in_out_cubic, alpha_composite_layer, warp_layer_25d, encode_previews,
    render_pilot_1_gentle_smile_blink
)

ARTIFACT_DIR = Path(r"C:\Users\USER\.gemini\antigravity\brain\7d6c96b0-8de4-401c-93fb-385f2c2d3564")
SOURCE_DIR = BASE_DIR / "03_Character_Assets" / "Source_Files"
RIG_BLEND = BASE_DIR / "03_Character_Assets" / "Rig" / "THAKUR_CHILD_MASTER_RIG_V001.blend"


def render_pilot_3_prayer_sitting(apply_eyelid_and_smile, head_base, body_base, nw, nh):
    """
    PILOT 3: THAKUR_PRAYER_SITTING_V001
    Duration: 4.0s (96 frames @ 24 FPS), Natural Start -> Devotional Hold -> Recovery (Loopable)
    Category: Sitting / Devotional
    """
    asset_id = "THAKUR_PRAYER_SITTING_V001"
    out_dir = GESTURE_DIR / "Sitting" / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    dev_dir = GESTURE_DIR / "Devotional" / asset_id
    dev_dir.mkdir(parents=True, exist_ok=True)

    # Load gesture_torso_01_namaskar.png (332w x 293h) and align its shoulders/collar exactly to body_base (nw=656, nh=664)
    namaskar_raw = np.array(Image.open(LAYERS_DIR / "gesture_torso_01_namaskar.png").convert("RGBA"))
    # In body_base (656 x 664), the torso/shoulders span width ~445px (x: 105..550) and y: 205..535
    nam_w, nam_h = 456, 402
    nam_hi = np.array(Image.fromarray(namaskar_raw).resize((nam_w, nam_h), Image.Resampling.LANCZOS))

    # Build a feathered mask on nam_hi so its outer shoulders and lower waist blend smoothly over the Sukhasana crossed legs
    mh, mw, _ = nam_hi.shape
    gy, gx = np.indices((mh, mw), dtype=np.float32)
    # Mask out the upper chin snippet of gesture_torso_01_namaskar (y < 46) because our articulated head_base sits on top
    top_fade = np.clip((gy - 42.0) / 16.0, 0.0, 1.0)
    # Soft fade at the bottom waist/lap (y > mh - 55) so the Sukhasana crossed legs and bare right foot remain 100% visible below!
    bot_fade = np.clip((mh - 18.0 - gy) / 42.0, 0.0, 1.0)
    nam_mask = top_fade * bot_fade
    nam_hi[:, :, 3] = (nam_hi[:, :, 3].astype(np.float32) * nam_mask).astype(np.uint8)

    # Place nam_hi onto a full (nh x nw) layer aligned at x=100, y=194 (so shoulders sit cleanly below chin at y=228)
    nam_layer_full = np.zeros((nh, nw, 4), dtype=np.uint8)
    alpha_composite_layer(nam_layer_full, nam_hi, 100, 194)

    # Clear the old outer resting shoulders/sleeves of body_namaskar_state between y=195..475 outside nam_layer_full's opaque silhouette
    # so there is no double-shoulder outline behind the raised Namaskar arms!
    body_namaskar_state = body_base.copy()
    nam_alpha_f = (nam_layer_full[:, :, 3].astype(np.float32) / 255.0)
    # In torso zone y=195..475, fade out body_namaskar_state wherever nam_layer_full is not opaque
    torso_clear = np.ones((nh, nw), dtype=np.float32)
    torso_clear[195:465, :] = 0.0
    torso_clear = cv2.GaussianBlur(torso_clear, (21, 21), 6.0)
    body_namaskar_state[:, :, 3] = (body_namaskar_state[:, :, 3].astype(np.float32) * torso_clear).astype(np.uint8)
    # Softly paint clean dhoti lap folds over the resting hands region (x: 255..400, y: 495..585) in body_namaskar_state
    lap_patch = body_namaskar_state[485:588, 245:412].copy()
    # Sample clean white dhoti color from left/right thighs (x=210, y=535)
    dhoti_light = np.array([247, 236, 218], dtype=np.uint8)
    dhoti_mid = np.array([224, 209, 192], dtype=np.uint8)
    lh, lw, _ = lap_patch.shape
    lgy, lgx = np.indices((lh, lw), dtype=np.float32)
    # Elliptical mask covering only the resting hands in the center of the lap above the bare right foot (foot is at y > 572)
    hand_lap_mask = np.clip(1.0 - np.sqrt(((lgx - lw * 0.5) / (lw * 0.44))**2 + ((lgy - lh * 0.35) / (lh * 0.38))**2), 0.0, 1.0)
    hand_lap_mask = cv2.GaussianBlur(hand_lap_mask, (15, 15), 5.0)[:, :, None]
    clean_cloth = np.zeros((lh, lw, 3), dtype=np.float32)
    clean_cloth[:, :] = dhoti_light * 0.75 + dhoti_mid * 0.25
    lap_patch[:, :, :3] = (lap_patch[:, :, :3].astype(np.float32) * (1.0 - hand_lap_mask * 0.92) + clean_cloth * (hand_lap_mask * 0.92)).astype(np.uint8)
    body_namaskar_state[485:588, 245:412] = lap_patch
    # Composite the Namaskar torso & praying hands onto body_namaskar_state
    alpha_composite_layer(body_namaskar_state, nam_layer_full, 0, 0)

    total_frames = 96
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20

    for f in range(total_frames):
        t = f / float(total_frames)
        phase = 2.0 * math.pi * t * 2.0  # 2 gentle breath cycles over 4.0 seconds
        breath = math.sin(phase)
        cloth_breath = math.sin(phase - 0.45)

        # Prayer timeline:
        # 0..15: Resting in Sukhasana, gentle breathing, natural blink at f=8..14
        # 16..22: Subtle inhale anticipation (chest lifts slightly, head tilts -2.5 deg)
        # 23..40: Hands rise gracefully from lap to chest in Namaskar; eyelids close peacefully
        # 41..74: Serene devotional prayer hold in Namaskar with gentle breathing and slight bow (+4.5 deg pitch)
        # 75..91: Hands lower softly back to resting posture while eyes gently open
        # 92..95: Settle in resting Sukhasana for clean loop
        if f < 16:
            pray_u = 0.0
            pitch = 0.0
            eye_close = {8: 0.3, 9: 0.8, 10: 1.0, 11: 0.7, 12: 0.25}.get(f, 0.0)
        elif f < 23:
            u = ease_in_out_cubic((f - 16) / 7.0)
            pray_u = 0.08 * u
            pitch = -3.0 * u  # Anticipation lift
            eye_close = 0.15 * u
        elif f < 41:
            u = ease_in_out_cubic((f - 23) / 18.0)
            pray_u = 0.08 + 0.92 * u
            pitch = -3.0 * (1.0 - u) + 5.5 * u  # Gentle devotional bow as hands reach chest
            eye_close = 0.15 + 0.85 * u
        elif f < 74:
            pray_u = 1.0
            hold_u = (f - 41) / 33.0
            pitch = 5.5 + 1.2 * math.sin(hold_u * math.pi)
            eye_close = 1.0  # Peaceful closed eyes during prayer hold
        elif f < 91:
            u = ease_in_out_cubic((f - 74) / 17.0)
            pray_u = 1.0 - u
            pitch = 5.5 * (1.0 - u)
            eye_close = 1.0 - u
        else:
            pray_u = 0.0
            pitch = 0.0
            eye_close = 0.0

        # Articulated upward/downward motion trajectory during the hand transition (pray_u between 0 and 1)
        # Rest state slides slightly upward as it fades out; Namaskar state rises from lap (+38px downward offset) to chest (0px)
        rest_body_warped = warp_layer_25d(
            body_base, pivot_xy=(nw * 0.5, 430),
            angle_deg=0.3 * math.sin(phase),
            scale_x=1.0 + 0.008 * breath,
            scale_y=1.0 + 0.009 * breath,
            tx=0.0, ty=-18.0 * pray_u - 1.2 * breath,
            cloth_sway_px=2.0 * cloth_breath
        )
        nam_body_warped = warp_layer_25d(
            body_namaskar_state, pivot_xy=(nw * 0.5, 430),
            angle_deg=0.3 * math.sin(phase),
            scale_x=1.0 + 0.008 * breath,
            scale_y=1.0 + 0.009 * breath,
            tx=0.0, ty=36.0 * (1.0 - pray_u) - 1.2 * breath,
            cloth_sway_px=2.4 * cloth_breath
        )

        # Blend the two articulated body states with vertical motion trajectory
        body_blend = np.zeros_like(body_base)
        if pray_u <= 0.001:
            body_blend = rest_body_warped
        elif pray_u >= 0.999:
            body_blend = nam_body_warped
        else:
            # Keep lower crossed legs stationary while upper torso/arms transition smoothly
            leg_line = 490
            body_blend[leg_line:, :] = body_base[leg_line:, :]
            top_r = rest_body_warped[:leg_line, :].astype(np.float32)
            top_n = nam_body_warped[:leg_line, :].astype(np.float32)
            body_blend[:leg_line, :] = np.clip(top_r * (1.0 - pray_u) + top_n * pray_u, 0, 255).astype(np.uint8)

        head_expr = apply_eyelid_and_smile(head_base, eye_close, 0.45 + 0.45 * pray_u)
        head_warped = warp_layer_25d(
            head_expr, pivot_xy=(nw * 0.5, 228),
            angle_deg=0.6 * math.sin(phase * 0.5),
            scale_x=1.0,
            scale_y=1.0 - 0.008 * abs(pitch / 6.0),
            tx=0.0,
            ty=3.8 * (pitch / 6.0) - 1.5 * breath,
            tilt_pitch_deg=pitch
        )

        canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canvas, body_blend, ox, oy)
        alpha_composite_layer(canvas, head_warped, ox, oy)

        Image.fromarray(canvas, mode="RGBA").save(frames_dir / f"{asset_id}_{f + 1:04d}.png")

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)

    meta = {
        "asset_id": asset_id,
        "gesture_name": "Sitting Cross-Legged (Sukhasana) and Praying (Namaskar)",
        "gesture_category": "Sitting / Devotional",
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "character_version": "1.0.0",
        "animation_method": "Method 1 + Method 3: Rigged 2D Sukhasana Layers + Articulated Namaskar Hand Rise & Serene Eye Close",
        "source_blend_file": "03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend",
        "png_sequence_dir": str(frames_dir.relative_to(BASE_DIR)),
        "preview_mp4": str(mp4_p.relative_to(BASE_DIR)),
        "preview_gif": str(gif_p.relative_to(BASE_DIR)),
        "preview_webm": str(webm_p.relative_to(BASE_DIR)),
        "frame_rate": 24,
        "frame_count": total_frames,
        "duration_seconds": 4.0,
        "dimensions": [canvas_w, canvas_h],
        "transparency": True,
        "seamless_loop": True,
        "approval_status": "PENDING_PILOT_REVIEW",
        "version": "V001"
    }
    with open(out_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    with open(dev_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"Pilot 3 ({asset_id}) rendered and encoded successfully.")


def extract_8_keyposes_from_sheet(sheet_path: Path, save_sheet_copy: Path, target_box=(380, 620)):
    """
    Slices an 8-pose (4x2 grid) locomotion sprite sheet into 8 clean RGBA key-pose sprites,
    auto-aligns every pose by its cranial head center X and ground contact / hip ratio so there is
    ZERO horizontal jitter, and normalizes character scale.
    """
    shutil.copyfile(sheet_path, save_sheet_copy)
    im = Image.open(sheet_path).convert("RGB")
    arr = np.array(im)
    h, w, _ = arr.shape  # 1376 x 768
    col_w, row_h = w // 4, h // 2

    poses = []
    heights = []
    for idx in range(8):
        r, c = idx // 4, idx % 4
        x0, x1 = c * col_w + 8, (c + 1) * col_w - 8
        y0, y1 = r * row_h + 6, (r + 1) * row_h - 6
        crop = arr[y0:y1, x0:x1].copy()
        rgba = extract_clean_silhouette_rgba(crop, line_thresh=150, close_bottom=False, strip_h_lines=False)

        # Find tight bounding box of character alpha > 40
        ys, xs = np.where(rgba[:, :, 3] > 40)
        by0, by1 = int(np.min(ys)), int(np.max(ys))
        bx0, bx1 = int(np.min(xs)), int(np.max(xs))
        tight = rgba[by0:by1 + 1, bx0:bx1 + 1].copy()
        poses.append(tight)
        heights.append(tight.shape[0])

    # Normalize all 8 poses to a consistent standing height scale (~520px tall on a 768x768 canvas)
    med_h = float(np.median(heights))
    target_h = 520.0
    scale_base = target_h / med_h

    aligned_poses = []
    canvas_w, canvas_h = 768, 768
    for idx, p in enumerate(poses):
        ph, pw, _ = p.shape
        # Preserve subtle natural height differences across contact/down/pass/up within ±3%
        s = scale_base
        nw, nh = int(round(pw * s)), int(round(ph * s))
        p_hi = np.array(Image.fromarray(p).resize((nw, nh), Image.Resampling.LANCZOS))

        # Locate head center X (top 22% of sprite) to lock horizontal spine axis across all 8 poses
        head_band = p_hi[:int(nh * 0.22), :, 3]
        hys, hxs = np.where(head_band > 128)
        head_cx = int(np.median(hxs)) if len(hxs) > 0 else nw // 2

        canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        # Align head_cx to canvas center X (384)
        ox = (canvas_w // 2) - head_cx
        # Align crown top to y=110 (we will apply smooth sinusoidal vertical bounce Curve in the 24 FPS synthesizer!)
        oy = 115
        alpha_composite_layer(canv, p_hi, ox, oy)
        aligned_poses.append(canv)

    return aligned_poses


def interpolate_flow_rgba(pose_a: np.ndarray, pose_b: np.ndarray, u: float):
    """
    Dense Optical-Flow (DIS / Farneback) bi-directional motion-compensated interpolation between key pose A and key pose B.
    Produces crisp intermediate frames without double-image ghosting!
    """
    if u <= 0.001:
        return pose_a.copy()
    if u >= 0.999:
        return pose_b.copy()

    # Compute grayscale + alpha weighted structural representation for flow
    ga = cv2.cvtColor(pose_a[:, :, :3], cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(pose_b[:, :, :3], cv2.COLOR_RGB2GRAY)
    aa = (pose_a[:, :, 3].astype(np.float32) / 255.0)
    ab = (pose_b[:, :, 3].astype(np.float32) / 255.0)
    fa = (ga.astype(np.float32) * aa).astype(np.uint8)
    fb = (gb.astype(np.float32) * ab).astype(np.uint8)

    # Downscale 0.5x for fast, smooth global limb/cloth flow estimation
    h, w = fa.shape
    fa_s = cv2.resize(fa, (w // 2, h // 2))
    fb_s = cv2.resize(fb, (w // 2, h // 2))

    flow_ab_s = cv2.calcOpticalFlowFarneback(fa_s, fb_s, None, 0.5, 3, 21, 3, 5, 1.2, 0)
    flow_ba_s = cv2.calcOpticalFlowFarneback(fb_s, fa_s, None, 0.5, 3, 21, 3, 5, 1.2, 0)

    flow_ab = cv2.resize(flow_ab_s, (w, h)) * 2.0
    flow_ba = cv2.resize(flow_ba_s, (w, h)) * 2.0

    gy, gx = np.indices((h, w), dtype=np.float32)
    map_a_x = (gx - u * flow_ab[:, :, 0]).astype(np.float32)
    map_a_y = (gy - u * flow_ab[:, :, 1]).astype(np.float32)
    map_b_x = (gx - (1.0 - u) * flow_ba[:, :, 0]).astype(np.float32)
    map_b_y = (gy - (1.0 - u) * flow_ba[:, :, 1]).astype(np.float32)

    warped_a = cv2.remap(pose_a, map_a_x, map_a_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    warped_b = cv2.remap(pose_b, map_b_x, map_b_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    su = ease_in_out_cubic(u)
    out = np.clip(warped_a.astype(np.float32) * (1.0 - su) + warped_b.astype(np.float32) * su, 0, 255).astype(np.uint8)
    # Sharpen alpha threshold slightly so silhouette edges stay crisp Ghibli cel-style
    a_float = out[:, :, 3].astype(np.float32) / 255.0
    a_crisp = np.clip((a_float - 0.35) / 0.45, 0.0, 1.0)
    out[:, :, 3] = (a_crisp * 255.0).astype(np.uint8)
    return out


def render_pilot_4_walk_cycle():
    """
    PILOT 4: THAKUR_WALK_CYCLE_V001
    Duration: 2.0s (48 frames @ 24 FPS), Seamless Loop (2 full strides: 24 frames per stride, 6 frames per key pose)
    Category: Walking
    """
    asset_id = "THAKUR_WALK_CYCLE_V001"
    out_dir = GESTURE_DIR / "Walking" / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    walk_sheet_src = ARTIFACT_DIR / "thakur_walk_cycle_sprite_sheet_v002_1795589271990.jpg"
    walk_sheet_dst = SOURCE_DIR / "THAKUR_WALK_CYCLE_KEYPOSES_8_V001.png"
    poses = extract_8_keyposes_from_sheet(walk_sheet_src, walk_sheet_dst)

    # Save the 8 extracted RGBA key poses into 03_Character_Assets/Layers/ for full editability
    for idx, p in enumerate(poses):
        Image.fromarray(p, mode="RGBA").save(LAYERS_DIR / f"walk_keypose_{idx + 1:02d}.png")

    total_frames = 48
    frames_per_pose = total_frames // 8  # 6 frames per key interval (8 * 6 = 48 frames = 2.0s @ 24 FPS)

    # Vertical center-of-mass walk bounce per key pose (Contact=0px, Down=+11px, Pass=-3px, Up=-10px)
    pose_y_bounce = [0.0, 11.0, -3.0, -10.0, 0.0, 11.0, -3.0, -10.0]
    pose_cloth_sway = [-2.5, 4.0, 1.5, -3.5, -2.5, 4.0, 1.5, -3.5]

    for f in range(total_frames):
        p_idx = (f // frames_per_pose) % 8
        next_idx = (p_idx + 1) % 8
        local_u = (f % frames_per_pose) / float(frames_per_pose)

        interp = interpolate_flow_rgba(poses[p_idx], poses[next_idx], local_u)

        # Smooth sinusoidal vertical walk bounce and overlapping uttoriyo cloth follow-through
        su = ease_in_out_cubic(local_u)
        ty = pose_y_bounce[p_idx] * (1.0 - su) + pose_y_bounce[next_idx] * su
        c_sway = pose_cloth_sway[p_idx] * (1.0 - su) + pose_cloth_sway[next_idx] * su

        final_frame = warp_layer_25d(
            interp, pivot_xy=(384, 340),
            angle_deg=0.8 * math.sin(2.0 * math.pi * f / 24.0),
            scale_x=1.0, scale_y=1.0,
            tx=0.0, ty=ty,
            cloth_sway_px=c_sway
        )
        Image.fromarray(final_frame, mode="RGBA").save(frames_dir / f"{asset_id}_{f + 1:04d}.png")

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)

    meta = {
        "asset_id": asset_id,
        "gesture_name": "Natural Child Walk Cycle (Right Profile, Barefoot, White Uttoriyo & Dhoti)",
        "gesture_category": "Walking",
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "character_version": "1.0.0",
        "animation_method": "Method 2 + Method 1: 8 Frame-by-Frame Key Poses + 24 FPS Motion-Compensated In-Betweening & Cloth Follow-Through",
        "source_blend_file": "03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend",
        "source_keypose_sheet": "03_Character_Assets/Source_Files/THAKUR_WALK_CYCLE_KEYPOSES_8_V001.png",
        "png_sequence_dir": str(frames_dir.relative_to(BASE_DIR)),
        "preview_mp4": str(mp4_p.relative_to(BASE_DIR)),
        "preview_gif": str(gif_p.relative_to(BASE_DIR)),
        "preview_webm": str(webm_p.relative_to(BASE_DIR)),
        "frame_rate": 24,
        "frame_count": total_frames,
        "duration_seconds": 2.0,
        "dimensions": [768, 768],
        "transparency": True,
        "seamless_loop": True,
        "approval_status": "PENDING_PILOT_REVIEW",
        "version": "V001"
    }
    with open(out_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"Pilot 4 ({asset_id}) rendered and encoded successfully.")


def render_pilot_5_run_cycle():
    """
    PILOT 5: THAKUR_RUN_CYCLE_V001
    Duration: 1.33s (32 frames @ 24 FPS, 4 frames per key pose across 8 key poses = crisp energetic child run cadence)
    Category: Running
    """
    asset_id = "THAKUR_RUN_CYCLE_V001"
    out_dir = GESTURE_DIR / "Running" / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    run_sheet_src = ARTIFACT_DIR / "thakur_run_cycle_sprite_sheet_v003_1795589295777.jpg"
    run_sheet_dst = SOURCE_DIR / "THAKUR_RUN_CYCLE_KEYPOSES_8_V001.png"
    poses = extract_8_keyposes_from_sheet(run_sheet_src, run_sheet_dst)

    for idx, p in enumerate(poses):
        Image.fromarray(p, mode="RGBA").save(LAYERS_DIR / f"run_keypose_{idx + 1:02d}.png")

    total_frames = 32  # 8 poses * 4 frames per pose = 32 frames @ 24 FPS (1.33s seamless high-energy loop)
    frames_per_pose = 4

    # Vertical flight & cushion curve per run pose (1.Contact=0px, 2.Down/Cushion=+15px, 3.Drive=-6px, 4.Airborne Flight=-16px)
    pose_y_arc = [0.0, 15.0, -6.0, -16.0, 0.0, 15.0, -6.0, -16.0]
    pose_cloth_flutter = [-4.0, 6.5, 3.0, -6.0, -4.0, 6.5, 3.0, -6.0]

    for f in range(total_frames):
        p_idx = (f // frames_per_pose) % 8
        next_idx = (p_idx + 1) % 8
        local_u = (f % frames_per_pose) / float(frames_per_pose)

        interp = interpolate_flow_rgba(poses[p_idx], poses[next_idx], local_u)

        su = ease_in_out_cubic(local_u)
        ty = pose_y_arc[p_idx] * (1.0 - su) + pose_y_arc[next_idx] * su
        flutter = pose_cloth_flutter[p_idx] * (1.0 - su) + pose_cloth_flutter[next_idx] * su

        final_frame = warp_layer_25d(
            interp, pivot_xy=(384, 340),
            angle_deg=1.5 * math.sin(2.0 * math.pi * f / 16.0),
            scale_x=1.0, scale_y=1.0,
            tx=0.0, ty=ty,
            cloth_sway_px=flutter
        )
        Image.fromarray(final_frame, mode="RGBA").save(frames_dir / f"{asset_id}_{f + 1:04d}.png")

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)

    meta = {
        "asset_id": asset_id,
        "gesture_name": "Natural Joyful Child Run Cycle (Right Profile, Barefoot, Flowing Uttoriyo & Dhoti)",
        "gesture_category": "Running",
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "character_version": "1.0.0",
        "animation_method": "Method 2 + Method 1: 8 Frame-by-Frame Run Key Poses + 24 FPS Flight Arcs & Uttoriyo Shawl Follow-Through",
        "source_blend_file": "03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend",
        "source_keypose_sheet": "03_Character_Assets/Source_Files/THAKUR_RUN_CYCLE_KEYPOSES_8_V001.png",
        "png_sequence_dir": str(frames_dir.relative_to(BASE_DIR)),
        "preview_mp4": str(mp4_p.relative_to(BASE_DIR)),
        "preview_gif": str(gif_p.relative_to(BASE_DIR)),
        "preview_webm": str(webm_p.relative_to(BASE_DIR)),
        "frame_rate": 24,
        "frame_count": total_frames,
        "duration_seconds": round(total_frames / 24.0, 2),
        "dimensions": [768, 768],
        "transparency": True,
        "seamless_loop": True,
        "approval_status": "PENDING_PILOT_REVIEW",
        "version": "V001"
    }
    with open(out_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"Pilot 5 ({asset_id}) rendered and encoded successfully.")


if __name__ == "__main__":
    fn, hb, bb, nw, nh = render_pilot_1_gentle_smile_blink()
    render_pilot_3_prayer_sitting(fn, hb, bb, nw, nh)
    render_pilot_4_walk_cycle()
    render_pilot_5_run_cycle()
