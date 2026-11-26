"""
Param Bismoy Balak Thakur (পরম বিস্ময় বালক ঠাকুর)
Master Scene Synthesis Pipeline: "শান্ত প্রস্থান" (The Contemplative Departure)

A continuous 12.0-second (288 frames @ 24 FPS) cinematic acting sequence in 1080p:
Act 1: Seated posture shift & peaceful breath in Sukhasana (Frames 001–072)
Act 2: Organic stand-up motion with center-of-gravity transfer (Frames 073–132)
Act 3: Settle & smooth 180° turnaround rotation (Frames 133–204)
Act 4: Gentle barefoot rear walk away into courtyard depth (Frames 205–288)

Features:
- Multiplane Kazuo Oga Ghibli Background integration (BG01_Ancestral_Courtyard_Day)
- Dense Optical-Flow (Farneback) transitional bridging (zero cuts or pops)
- Anatomical ground plane anchoring at FOOT_Y
- Dynamic elliptical contact shadow tracking footprint
- Volumetric crepuscular sunbeams & 45 floating golden dust motes
- Full 4-format broadcast deliverables (1080p MP4, WebM alpha, GIF, PNG frames)
"""
import os
import sys
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
LIB_DIR = BASE_DIR / "04_Gesture_Library"
BG_PATH = BASE_DIR / "01_Backgrounds" / "BG01_Ancestral_Courtyard_Day" / "BG01_Ancestral_Courtyard_Day_master.png"
OUTPUT_DIR = BASE_DIR / "06_Scene_Compositions" / "Activity_Sit_Stand_Walk"
FRAMES_DIR = OUTPUT_DIR / "frames"
PREVIEWS_DIR = BASE_DIR / "05_Animation_Previews"

WIDTH = 1920
HEIGHT = 1080
FPS = 24
TOTAL_FRAMES = 288


def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - math.pow(-2.0 * t + 2.0, 3.0) / 2.0


def ease_out_quad(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) * (1.0 - t)


def interpolate_flow_rgba(pose_a: np.ndarray, pose_b: np.ndarray, u: float) -> np.ndarray:
    """Dense Farneback optical flow interpolation between two RGBA character poses."""
    if u <= 0.001:
        return pose_a.copy()
    if u >= 0.999:
        return pose_b.copy()

    ga = cv2.cvtColor(pose_a[:, :, :3], cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(pose_b[:, :, :3], cv2.COLOR_RGB2GRAY)
    aa = pose_a[:, :, 3].astype(np.float32) / 255.0
    ab = pose_b[:, :, 3].astype(np.float32) / 255.0
    fa = (ga.astype(np.float32) * aa).astype(np.uint8)
    fb = (gb.astype(np.float32) * ab).astype(np.uint8)

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

    warp_a = cv2.remap(pose_a, map_a_x, map_a_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    warp_b = cv2.remap(pose_b, map_b_x, map_b_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    blend = (warp_a.astype(np.float32) * (1.0 - u) + warp_b.astype(np.float32) * u).astype(np.uint8)
    return blend


class GoldenBokehParticle:
    def __init__(self, rng: np.random.RandomState, w: int, h: int):
        self.x0 = rng.uniform(w * 0.05, w * 0.95)
        self.y0 = rng.uniform(h * 0.1, h * 0.95)
        self.radius = rng.uniform(3.0, 8.5)
        self.speed_y = rng.uniform(0.5, 1.6)
        self.wave_freq = rng.uniform(0.02, 0.06)
        self.wave_amp = rng.uniform(10.0, 30.0)
        self.alpha_peak = rng.uniform(90, 200)
        self.phase = rng.uniform(0, 2 * math.pi)

    def get_pos(self, frame_idx: int, h: int) -> Tuple[float, float, float, float]:
        t = frame_idx
        cur_y = (self.y0 - self.speed_y * t) % h
        cur_x = self.x0 + math.sin(self.wave_freq * t + self.phase) * self.wave_amp
        pulse = 0.75 + 0.25 * math.sin(0.08 * t + self.phase)
        return cur_x, cur_y, self.radius, self.alpha_peak * pulse


def build_contact_shadow(char_rgba: np.ndarray, base_y: int, center_x: int, scale: float = 1.0) -> Image.Image:
    """Constructs a soft Ghibli ground contact shadow matching character foot footprint."""
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)

    # Detect character width at ground level
    a = char_rgba[:, :, 3]
    ys, xs = np.where(a > 50)
    if len(xs) > 0:
        c_w = (xs.max() - xs.min()) * scale
    else:
        c_w = 200.0 * scale

    rx = int(max(40.0, c_w * 0.42))
    ry = int(max(14.0, rx * 0.28))
    sy = base_y + 4

    # Core dark contact shadow
    s_draw.ellipse(
        [(center_x - int(rx * 0.7), sy - int(ry * 0.6)), (center_x + int(rx * 0.7), sy + int(ry * 0.6))],
        fill=(32, 22, 16, int(115 * scale))
    )
    # Softer ambient diffusion halo
    s_draw.ellipse(
        [(center_x - rx, sy - ry), (center_x + rx, sy + ry)],
        fill=(45, 30, 20, int(75 * scale))
    )

    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    return shadow


def create_crepuscular_rays(w: int, h: int) -> np.ndarray:
    """Volumetric morning sunlight god-rays entering at 34 degrees."""
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    rad = math.radians(34.0)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    proj = xx * sin_a + yy * cos_a

    rays = (
        0.5 + 0.3 * np.sin(proj * 0.012)
        + 0.15 * np.sin(proj * 0.028 + 1.2)
        + 0.1 * np.sin(proj * 0.006 + 2.5)
    )
    rays = np.clip(rays, 0.0, 1.0)
    v_falloff = np.clip((h - yy) / float(h), 0.2, 1.0)
    ray_alpha = (rays * v_falloff * 60.0).astype(np.uint8)

    overlay[:, :, 0] = 255
    overlay[:, :, 1] = 232
    overlay[:, :, 2] = 175
    overlay[:, :, 3] = ray_alpha
    return overlay


def build_continuous_activity_clip():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)

    print("\n=======================================================")
    print("🎬 RENDERING CONTINUOUS CINEMATIC SCENE: 'শান্ত প্রস্থান'")
    print("   Total Frames: 288 (12.0s @ 24 FPS)")
    print("   Resolution: 1920 x 1080 Full HD (2.39:1 Cinema Scope)")
    print("   Output Directory:", OUTPUT_DIR)
    print("=======================================================\n")

    # 1. Load Background Master
    if BG_PATH.exists():
        bg_img = Image.open(BG_PATH).convert("RGBA")
        if bg_img.size != (WIDTH, HEIGHT):
            bg_img = bg_img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    else:
        # Fallback warm plinth
        bg_img = Image.new("RGBA", (WIDTH, HEIGHT), (42, 32, 24, 255))
    bg_arr = np.array(bg_img)

    # 2. Load Raw Source Animation Sequences
    print("Loading source animation frames from gesture library...")

    # Act 1 frames: Sitting Changing Position (take 72 frames)
    act1_paths = sorted((LIB_DIR / "Sitting" / "THAKUR_SITTING_CHANGING_POSITION_V001" / "frames").glob("*.png"))
    act1_frames = [np.array(Image.open(p).convert("RGBA")) for p in act1_paths[:72]]
    print(f"Loaded Act 1 (Sitting shift): {len(act1_frames)} frames")

    # Act 2 frames: Standing Up (72 frames mapped to 60 frames)
    act2_paths = sorted((LIB_DIR / "Sitting" / "THAKUR_STANDING_UP_V001" / "frames").glob("*.png"))
    act2_raw = [np.array(Image.open(p).convert("RGBA")) for p in act2_paths]
    act2_indices = np.linspace(0, len(act2_raw) - 1, 60).astype(int)
    act2_frames = [act2_raw[i] for i in act2_indices]
    print(f"Loaded Act 2 (Stand Up): {len(act2_frames)} frames")

    # Act 3 frames: Settle Idle (18 frames) + Turn Around to rear (54 frames)
    idle_paths = sorted((LIB_DIR / "Walking" / "THAKUR_STANDING_IDLE_V001" / "frames").glob("*.png"))
    act3_idle = [np.array(Image.open(p).convert("RGBA")) for p in idle_paths[:18]]

    turn_paths = sorted((LIB_DIR / "Walking" / "THAKUR_TURN_AROUND_V001" / "frames").glob("*.png"))
    # Frame 1 to 60 covers 0 deg to 180 deg (front to rear)
    turn_raw = [np.array(Image.open(p).convert("RGBA")) for p in turn_paths[:60]]
    turn_indices = np.linspace(0, len(turn_raw) - 1, 54).astype(int)
    act3_turn = [turn_raw[i] for i in turn_indices]
    act3_frames = act3_idle + act3_turn
    print(f"Loaded Act 3 (Settle & Turnaround): {len(act3_frames)} frames")

    # Act 4 frames: Rear Walk Away into Depth (84 frames)
    # Master rear figure is turn_raw[59] (exact rear view)
    rear_plate = turn_raw[-1].copy()
    act4_frames = []
    # Synthesize 3.5 gentle contemplative walking strides from rear
    # Each stride is 24 frames
    stride_len = 24
    for step_f in range(84):
        phase = (step_f % stride_len) / float(stride_len)
        # Vertical pelvic bounce (sine wave 2 peaks per cycle)
        bounce_y = int(round(math.sin(phase * 4.0 * math.pi) * 2.5))
        # Subtle horizontal sway
        sway_x = math.sin(phase * 2.0 * math.pi) * 3.0
        # Subtle shoulder lean
        rot_angle = math.sin(phase * 2.0 * math.pi) * 1.2

        # Apply warp to rear plate
        h_s, w_s, _ = rear_plate.shape
        M = cv2.getRotationMatrix2D((w_s / 2.0, h_s * 0.65), rot_angle, 1.0)
        M[0, 2] += sway_x
        M[1, 2] += bounce_y
        warped_step = cv2.warpAffine(rear_plate, M, (w_s, h_s), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
        act4_frames.append(warped_step)
    print(f"Synthesized Act 4 (Rear Walk Stride): {len(act4_frames)} frames")

    # 3. Assemble Continuous Character Sequence with Flow Bridging
    print("Assembling master sequence with dense optical flow blending...")
    all_char_frames: List[np.ndarray] = []

    # --- Act 1 (Frames 0..71) ---
    all_char_frames.extend(act1_frames)

    # --- Bridge between Act 1 end and Act 2 start (8-frame smooth flow transition) ---
    # Replace last 4 frames of Act 1 and first 4 frames of Act 2 with flow blend
    bridge_len = 8
    p_a = act1_frames[-1]
    p_b = act2_frames[0]
    bridge_frames = [interpolate_flow_rgba(p_a, p_b, (k + 1) / float(bridge_len + 1)) for k in range(bridge_len)]

    # Splice bridge:
    all_char_frames = all_char_frames[:-4] + bridge_frames + act2_frames[4:]

    # --- Act 3 (Frames 132..203) ---
    # Smooth bridge from Act 2 end (standing) to Act 3 idle start
    p_act2_end = all_char_frames[-1]
    p_act3_start = act3_frames[0]
    bridge_2_3 = [interpolate_flow_rgba(p_act2_end, p_act3_start, (k + 1) / 5.0) for k in range(4)]
    all_char_frames.extend(bridge_2_3)
    all_char_frames.extend(act3_frames[4:])

    # --- Act 4 (Frames 204..287) ---
    # Smooth bridge from Act 3 turnaround rear to Act 4 rear walk start
    p_turn_end = all_char_frames[-1]
    p_walk_start = act4_frames[0]
    bridge_3_4 = [interpolate_flow_rgba(p_turn_end, p_walk_start, (k + 1) / 5.0) for k in range(4)]
    all_char_frames.extend(bridge_3_4)
    all_char_frames.extend(act4_frames[4:])

    # Ensure exactly 288 frames
    if len(all_char_frames) < TOTAL_FRAMES:
        all_char_frames.extend([all_char_frames[-1]] * (TOTAL_FRAMES - len(all_char_frames)))
    elif len(all_char_frames) > TOTAL_FRAMES:
        all_char_frames = all_char_frames[:TOTAL_FRAMES]

    print(f"Master character timeline ready: {len(all_char_frames)} continuous frames.")

    # 4. Environmental Setup
    rng = np.random.RandomState(108)
    particles = [GoldenBokehParticle(rng, WIDTH, HEIGHT) for _ in range(45)]
    sunbeams = create_crepuscular_rays(WIDTH, HEIGHT)

    # 5. Render Full Cinematic Composite
    print("\nRendering 288 frames of multiplane cinematic composition...")
    rendered_pil_frames = []

    # Ground placement metrics:
    # Courtyard plinth ground contact line in 1080p canvas:
    # Seated base at y = 870
    # Standing foot at y = 860
    base_standing_ground_y = 860
    base_seated_ground_y = 872
    char_base_x = int(WIDTH * 0.48)

    for f_idx in range(TOTAL_FRAMES):
        # Camera subtle pan & push: 0..288
        cam_t = f_idx / float(TOTAL_FRAMES - 1)
        # Slow cinematic push-in 1.000 -> 1.035
        zoom = 1.0 + 0.035 * cam_t
        zw, zh = int(WIDTH * zoom), int(HEIGHT * zoom)
        bg_zoomed = cv2.resize(bg_arr, (zw, zh), interpolation=cv2.INTER_LINEAR)
        # Subtle camera drift upward as Thakur stands and walks away
        pan_y = int(22.0 * ease_in_out_cubic(cam_t))
        ox = (zw - WIDTH) // 2
        oy = max(0, min(zh - HEIGHT, (zh - HEIGHT) // 2 - pan_y))
        frame_canvas = bg_zoomed[oy:oy + HEIGHT, ox:ox + WIDTH].copy()

        # Fade in from black on frames 0..20
        if f_idx < 20:
            fade_in = ease_out_quad(f_idx / 20.0)
            frame_canvas[:, :, :3] = (frame_canvas[:, :, :3].astype(np.float32) * fade_in).astype(np.uint8)

        # Fade out to black on frames 272..288
        if f_idx > 272:
            fade_out = 1.0 - ease_in_out_cubic((f_idx - 272) / 16.0)
            frame_canvas[:, :, :3] = (frame_canvas[:, :, :3].astype(np.float32) * fade_out).astype(np.uint8)

        # Sunbeam overlay
        beam_pulse = 0.88 + 0.12 * math.sin(0.06 * f_idx)
        b_alpha = (sunbeams[:, :, 3].astype(np.float32) * beam_pulse / 255.0)[:, :, None]
        b_rgb = sunbeams[:, :, :3].astype(np.float32)
        frame_canvas[:, :, :3] = np.clip(
            frame_canvas[:, :, :3].astype(np.float32) * (1.0 - b_alpha * 0.35) + b_rgb * (b_alpha * 0.35),
            0, 255
        ).astype(np.uint8)

        pil_frame = Image.fromarray(frame_canvas, mode="RGBA")

        # --- Character Placement & Perspective Depth Trajectory ---
        c_raw = all_char_frames[f_idx]
        
        # Calculate character scale & ground anchor:
        if f_idx < 72:
            # Act 1: Seated
            c_scale = 0.96
            ground_y = base_seated_ground_y
            cur_x = char_base_x
        elif f_idx < 132:
            # Act 2: Standing Up transition
            stand_t = (f_idx - 72) / 60.0
            c_scale = 0.96 + 0.04 * stand_t
            ground_y = int(base_seated_ground_y * (1.0 - stand_t) + base_standing_ground_y * stand_t)
            cur_x = char_base_x
        elif f_idx < 204:
            # Act 3: Settle & Turnaround
            c_scale = 1.00
            ground_y = base_standing_ground_y
            cur_x = char_base_x
        else:
            # Act 4: Walking Away into Depth
            walk_t = (f_idx - 204) / 84.0
            # Perspective scaling: 1.00 -> 0.86
            c_scale = 1.00 - 0.14 * ease_out_quad(walk_t)
            # Perspective elevation: character walks further back into the courtyard
            ground_y = int(base_standing_ground_y - 72.0 * ease_out_quad(walk_t))
            # Subtle path curvature toward garden grove
            cur_x = int(char_base_x + 36.0 * math.sin(walk_t * math.pi * 0.8))

        # Dynamic Ground Contact Shadow
        shadow_layer = build_contact_shadow(c_raw, ground_y, cur_x, scale=c_scale)
        pil_frame = Image.alpha_composite(pil_frame, shadow_layer)

        # Scale character RGBA
        c_pil = Image.fromarray(c_raw, mode="RGBA")
        cw = int(round(c_pil.width * c_scale))
        ch = int(round(c_pil.height * c_scale))
        c_resized = c_pil.resize((cw, ch), Image.Resampling.LANCZOS)

        # Align character: bottom of sprite at ground_y
        # In sprite coordinates, foot/base is around y = 690..724 of 768
        foot_offset_in_sprite = int(700 * c_scale)
        pos_x = cur_x - cw // 2
        pos_y = ground_y - foot_offset_in_sprite

        # Composite Character onto scene
        pil_frame.alpha_composite(c_resized, (pos_x, pos_y))

        # --- Atmospheric Floating Golden Bokeh Motes ---
        particle_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(particle_layer)
        for p in particles:
            px, py, pr, pa = p.get_pos(f_idx, HEIGHT)
            if pa > 10:
                p_draw.ellipse([(px - pr * 1.6, py - pr * 1.6), (px + pr * 1.6, py + pr * 1.6)], fill=(255, 220, 130, int(pa * 0.35)))
                p_draw.ellipse([(px - pr, py - pr), (px + pr, py + pr)], fill=(255, 248, 200, int(pa)))
        particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(1.2))
        pil_frame = Image.alpha_composite(pil_frame, particle_layer)

        # --- Cinematic 2.39:1 Anamorphic Scope Bars ---
        bar_h = int(HEIGHT * 0.11)
        scope_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(scope_layer)
        s_draw.rectangle([(0, 0), (WIDTH, bar_h)], fill=(10, 8, 6, 255))
        s_draw.rectangle([(0, HEIGHT - bar_h), (WIDTH, HEIGHT)], fill=(10, 8, 6, 255))
        pil_frame = Image.alpha_composite(pil_frame, scope_layer)

        # Save Master PNG Frame
        frame_name = f"ACT_SIT_STAND_WALK_{f_idx+1:04d}.png"
        pil_frame.save(FRAMES_DIR / frame_name, format="PNG")
        rendered_pil_frames.append(pil_frame)

        if (f_idx + 1) % 24 == 0 or (f_idx + 1) == TOTAL_FRAMES:
            print(f"Rendered frame {f_idx+1:03d} / {TOTAL_FRAMES} ({(f_idx+1)/TOTAL_FRAMES*100.0:.0f}%)")

    # 6. Multi-Format Video Exports
    print("\nExporting multi-format video deliverables...")

    # (A) Full HD 1080p MP4 (H.264, yuv420p)
    mp4_path = OUTPUT_DIR / "ACT_SIT_STAND_WALK.mp4"
    cmd_mp4 = [
        "ffmpeg", "-y", "-r", str(FPS),
        "-i", str(FRAMES_DIR / "ACT_SIT_STAND_WALK_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        str(mp4_path)
    ]
    try:
        subprocess.run(cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Generated 1080p MP4: {mp4_path} ({mp4_path.stat().st_size / (1024*1024):.2f} MB)")
    except Exception as e:
        print(f"MP4 export notice: {e}")

    # (B) WebM Export (VP9 with yuva420p)
    webm_path = OUTPUT_DIR / "ACT_SIT_STAND_WALK.webm"
    cmd_webm = [
        "ffmpeg", "-y", "-r", str(FPS),
        "-i", str(FRAMES_DIR / "ACT_SIT_STAND_WALK_%04d.png"),
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "26", "-b:v", "0",
        str(webm_path)
    ]
    try:
        subprocess.run(cmd_webm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Generated WebM: {webm_path} ({webm_path.stat().st_size / (1024*1024):.2f} MB)")
    except Exception as e:
        print(f"WebM export notice: {e}")

    # (C) GIF Preview (scaled to 640x360 at 12 fps for smooth web playback)
    gif_path = OUTPUT_DIR / "ACT_SIT_STAND_WALK.gif"
    gif_frames = [im.resize((640, 360), Image.Resampling.BILINEAR).convert("P", palette=Image.Palette.ADAPTIVE) for im in rendered_pil_frames[::2]]
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=int(1000.0 / (FPS / 2.0)),
        loop=0,
        optimize=True
    )
    print(f"✅ Generated GIF preview: {gif_path} ({gif_path.stat().st_size / (1024*1024):.2f} MB)")

    # (D) Metadata JSON
    meta = {
        "sequence_id": "ACT_SIT_STAND_WALK_V001",
        "title": "শান্ত প্রস্থান (The Contemplative Departure)",
        "character": "Param Bismoy Balak Thakur (Age 6, Ujanchar)",
        "scene": "Ancestral Courtyard Plinth (Morning Komorebi)",
        "resolution": [WIDTH, HEIGHT],
        "fps": FPS,
        "total_frames": TOTAL_FRAMES,
        "duration_seconds": round(TOTAL_FRAMES / float(FPS), 2),
        "acts": {
            "act_1_sitting_posture_shift": {"frames": [1, 72], "seconds": [0.0, 3.0]},
            "act_2_organic_stand_up": {"frames": [73, 132], "seconds": [3.0, 5.5]},
            "act_3_settle_and_turnaround": {"frames": [133, 204], "seconds": [5.5, 8.5]},
            "act_4_gentle_walk_into_depth": {"frames": [205, 288], "seconds": [8.5, 12.0]}
        },
        "technical_features": [
            "Dense Farneback optical flow transitional bridging",
            "Continuous ground-plane contact shadow tracking",
            "Perspective depth scaling (1.00x -> 0.86x)",
            "Volumetric 34-degree crepuscular sunbeam illumination",
            "45 golden bokeh dust particles with sinusoidal drift",
            "2.39:1 Anamorphic cinema scope bars"
        ]
    }
    meta_path = OUTPUT_DIR / "ACT_SIT_STAND_WALK_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved metadata: {meta_path}")

    # (E) Copy GIF to Previews for central gallery access
    preview_gif_copy = PREVIEWS_DIR / "GIF" / "THAKUR_ACTIVITY_SIT_STAND_WALK_V001.gif"
    shutil.copy(gif_path, preview_gif_copy)
    print(f"✅ Copied preview to central GIF gallery: {preview_gif_copy}")

    return OUTPUT_DIR


if __name__ == "__main__":
    build_continuous_activity_clip()
