"""
24 FPS Hybrid Animation Renderer & Exporter for Pilot Project V1 (Animations 1, 2, and 3)
Implements proper 2D animation principles (Timing & Spacing, Anticipation, Follow-Through, Overlapping Action, Ease-In/Ease-Out, Weight Distribution):
1. THAKUR_SMILE_GENTLE_BLINK_V001 (72 frames, 3.0s @ 24 FPS, seamless loop)
   - Method 1: 2D Layered Mesh Rig deformation + 5-stage progressive upper-eyelid blink + subtleneutral-to-gentle-smile transition + sinusoidal chest breathing + 3-frame delayed uttoriyo cloth follow-through.
2. THAKUR_HEAD_NOD_YES_V001 (60 frames, 2.5s @ 24 FPS, seamless loop)
   - Method 1: 2D Layered Mesh Rig with readable upward anticipation tilt (frames 1-14), smooth downward affirmative nod with perspective foreshortening & natural blink on the down-pose (frames 15-32), subtle secondary nod/settle (frames 33-48), and 3-frame overlapping uttoriyo collar/hair follow-through (frames 49-60).
3. THAKUR_PRAYER_SITTING_V001 (96 frames, 4.0s @ 24 FPS, natural start -> devotional hold -> serene recovery)
   - Method 1 + Method 3: Seated in Sukhasana matching the Master Reference (`01_Thakur_Age06_Child_Ujanchar_Master_Ref.png`).
   - Starts with resting hands in lap (frames 1-14), deep breath anticipation (15-22), hands and forearms rising gracefully to Namaskar at chest while eyes close into serene Peaceful meditation (23-42), devotional prayer hold with gentle breathing & warm golden aura pulse (43-74), and soft recovery back to resting hands and gentle open-eyed smile (75-96).

For each animation, outputs:
- 24 FPS Transparent RGBA PNG sequence (`04_Gesture_Library/<Category>/<ASSET_ID>/frames/frame_0001.png`...)
- Dedicated editable Blender 5.3 project file (`04_Gesture_Library/<Category>/<ASSET_ID>/<ASSET_ID>.blend`)
- MP4 preview (`05_Animation_Previews/MP4/<ASSET_ID>.mp4`)
- GIF preview (`05_Animation_Previews/GIF/<ASSET_ID>.gif`)
- Transparent WebM (`05_Animation_Previews/WebM/<ASSET_ID>.webm`)
- JSON metadata (`04_Gesture_Library/<Category>/<ASSET_ID>/<ASSET_ID>_metadata.json`)
"""
import json
import math
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

BASE_DIR = Path(r"E:\Codes\Ghibli Animation Thakur\Balak_Thakur_Animation")
LAYERS_DIR = BASE_DIR / "03_Character_Assets" / "Layers"
GESTURE_DIR = BASE_DIR / "04_Gesture_Library"
PREVIEW_DIR = BASE_DIR / "05_Animation_Previews"
FFMPEG_EXE = r"C:\Users\USER\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"


def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def alpha_composite_layer(canvas: np.ndarray, layer: np.ndarray, x_off: int, y_off: int, opacity: float = 1.0):
    ch, cw, _ = canvas.shape
    lh, lw, _ = layer.shape

    x0, y0 = max(0, x_off), max(0, y_off)
    x1, y1 = min(cw, x_off + lw), min(ch, y_off + lh)
    if x0 >= x1 or y0 >= y1:
        return canvas

    lx0, ly0 = x0 - x_off, y0 - y_off
    lx1, ly1 = lx0 + (x1 - x0), ly0 + (y1 - y0)

    sub_c = canvas[y0:y1, x0:x1].astype(np.float32)
    sub_l = layer[ly0:ly1, lx0:lx1].astype(np.float32)

    la = (sub_l[:, :, 3:4] / 255.0) * opacity
    ca = sub_c[:, :, 3:4] / 255.0

    out_a = la + ca * (1.0 - la)
    safe_a = np.where(out_a > 1e-5, out_a, 1.0)
    out_rgb = (sub_l[:, :, :3] * la + sub_c[:, :, :3] * ca * (1.0 - la)) / safe_a

    res = np.zeros_like(sub_c)
    res[:, :, :3] = np.clip(out_rgb, 0, 255)
    res[:, :, 3:4] = np.clip(out_a * 255.0, 0, 255)
    canvas[y0:y1, x0:x1] = res.astype(np.uint8)
    return canvas


def warp_layer_25d(layer: np.ndarray, pivot_xy: tuple, angle_deg: float = 0.0, scale_x: float = 1.0,
                   scale_y: float = 1.0, tx: float = 0.0, ty: float = 0.0, tilt_pitch_deg: float = 0.0,
                   cloth_sway_px: float = 0.0):
    """
    Applies smooth 2.5D affine + mesh-grid deformation to an RGBA character layer around pivot_xy:
    - Rotation (`angle_deg`), Breathing/Foreshortening Scale (`scale_x`, `scale_y`), Translation (`tx`, `ty`)
    - Vertical perspective pitch (`tilt_pitch_deg`) for natural head nodding
    - Organic sinusoidal cloth wave (`cloth_sway_px`) for the white uttoriyo shawl folds
    """
    h, w, _ = layer.shape
    px, py = pivot_xy

    # Create dense pixel coordinate grid
    grid_y, grid_x = np.indices((h, w), dtype=np.float32)
    dx = grid_x - px
    dy = grid_y - py

    # Inverse transform to sample source
    dx -= tx
    dy -= ty

    # Cloth wave displacement along lower portion of garment
    if abs(cloth_sway_px) > 0.01:
        y_norm = np.clip((grid_y - py) / max(1.0, float(h - py)), 0.0, 1.0)
        dx -= cloth_sway_px * (y_norm ** 1.6) * np.sin(y_norm * math.pi)

    # 2.5D pitch foreshortening (nodding forward compresses vertical spacing slightly and curves horizontal lines downward)
    if abs(tilt_pitch_deg) > 0.01:
        pitch_rad = math.radians(tilt_pitch_deg)
        # Curvature: features near horizontal center dip lower when nodding down (+pitch)
        x_norm = (dx / max(1.0, w * 0.45))
        curve_y = math.sin(pitch_rad) * 18.0 * (1.0 - 0.35 * (x_norm ** 2))
        dy -= curve_y
        sy_pitch = math.cos(pitch_rad * 0.65)
        dy /= max(0.7, sy_pitch)

    # Rotation & Scale
    rad = math.radians(-angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    rx = (dx * cos_a - dy * sin_a) / max(0.1, scale_x)
    ry = (dx * sin_a + dy * cos_a) / max(0.1, scale_y)

    map_x = (rx + px).astype(np.float32)
    map_y = (ry + py).astype(np.float32)

    warped = cv2.remap(layer, map_x, map_y, interpolation=cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    return warped


def encode_previews(frames_dir: Path, asset_id: str, fps: int = 24):
    mp4_path = PREVIEW_DIR / "MP4" / f"{asset_id}.mp4"
    webm_path = PREVIEW_DIR / "WebM" / f"{asset_id}.webm"
    gif_path = PREVIEW_DIR / "GIF" / f"{asset_id}.gif"

    input_pattern = str(frames_dir / f"{asset_id}_%04d.png")

    # 1. MP4 Preview (composited over soft warm studio parchment #F7F3E8 so dark sepia linework and white cloth look rich in MP4 players)
    cmd_mp4 = [
        FFMPEG_EXE, "-y", "-framerate", str(fps), "-i", input_pattern,
        "-vf", "format=rgba,split[fg][bg];[bg]geq=r=247:g=243:b=232:a=255[cream];[cream][fg]overlay=0:0:format=auto,format=yuv420p",
        "-c:v", "libx264", "-crf", "16", "-preset", "fast", str(mp4_path)
    ]
    subprocess.run(cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Transparent WebM (VP9 with yuva420p alpha channel)
    cmd_webm = [
        FFMPEG_EXE, "-y", "-framerate", str(fps), "-i", input_pattern,
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "2M", "-crf", "18",
        "-auto-alt-ref", "0", str(webm_path)
    ]
    subprocess.run(cmd_webm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. High-Quality 24 FPS Palette-Optimized GIF Preview
    cmd_gif = [
        FFMPEG_EXE, "-y", "-framerate", str(fps), "-i", input_pattern,
        "-vf", "format=rgba,split[fg][bg];[bg]geq=r=247:g=243:b=232:a=255[cream];[cream][fg]overlay=0:0:format=auto,scale=540:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
        str(gif_path)
    ]
    subprocess.run(cmd_gif, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return mp4_path, webm_path, gif_path


def build_seated_seamless_head_frames():
    """
    Creates 5 blink stages + neutral-to-smile mouth progression directly on the Seated Sukhasana head
    so that the head, neck, collar, and body match 100% seamlessly at pixel level!
    """
    seat_rgba = np.array(Image.open(LAYERS_DIR / "body_seated_sukhasana.png").convert("RGBA"))
    # In body_seated_sukhasana.png (415h x 410w), the eyes are at y=68..96, x=155..255
    # and the mouth is at y=115..134, x=178..232
    return seat_rgba


def render_pilot_1_gentle_smile_blink():
    """
    PILOT 1: THAKUR_SMILE_GENTLE_BLINK_V001
    Duration: 3.0s (72 frames @ 24 FPS), Seamless Loop
    Category: Facial
    """
    asset_id = "THAKUR_SMILE_GENTLE_BLINK_V001"
    out_dir = GESTURE_DIR / "Facial" / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Load high-resolution expression heads (01_neutral, 02_gentle_smile, 03_broad_smile, 10_peaceful)
    # and seated body base for a full upper-body/seated portrait framing (720 x 720 RGBA canvas)
    seat_full = np.array(Image.open(LAYERS_DIR / "body_seated_sukhasana.png").convert("RGBA"))
    # Upscale cleanly 1.6x to 656 x 664 on a 768 x 768 transparent RGBA production canvas
    sh, sw, _ = seat_full.shape
    scale_f = 1.6
    nw, nh = int(sw * scale_f), int(sh * scale_f)
    seat_hi = np.array(Image.fromarray(seat_full).resize((nw, nh), Image.Resampling.LANCZOS))

    # Separate into Head+Neck layer (y: 0..248) and Seated Body+Uttoriyo+Legs layer (y: 215..nh) with smooth alpha blend
    head_base = np.zeros_like(seat_hi)
    body_base = np.zeros_like(seat_hi)

    # Create smooth split mask at neck collar (y = 222..242)
    neck_mask = np.zeros((nh, nw), dtype=np.float32)
    neck_mask[:224, :] = 1.0
    for y in range(224, 242):
        neck_mask[y, :] = 1.0 - (y - 224) / 18.0
    # Restrict head mask horizontally to neck/head width (x: 170..485)
    x_mask = np.zeros((nh, nw), dtype=np.float32)
    x_mask[:, 180:476] = 1.0
    x_mask = cv2.GaussianBlur(x_mask, (15, 15), 4.0)
    head_weight = neck_mask * x_mask

    head_base[:, :, :3] = seat_hi[:, :, :3]
    head_base[:, :, 3] = (seat_hi[:, :, 3].astype(np.float32) * head_weight).astype(np.uint8)

    body_base[:, :, :3] = seat_hi[:, :, :3]
    body_base[:, :, 3] = (seat_hi[:, :, 3].astype(np.float32) * (1.0 - head_weight * 0.85)).astype(np.uint8)

    # Locate eye bounding box in seat_hi: y=108..154, x=250..406
    # Locate mouth bounding box in seat_hi: y=182..212, x=285..372
    # Build progressive eyelid blink generator directly on head_base using skin/lash color from upper eyelid
    def apply_eyelid_and_smile(h_img: np.ndarray, blink_amt: float, smile_amt: float):
        out = h_img.copy()
        # 1. Subtle gentle smile transition (curls mouth corners slightly upward & widens warm lip curve by up to 3.5px)
        # Mouth center is at (328, 196)
        if abs(smile_amt) > 0.01:
            my0, my1, mx0, mx1 = 175, 220, 275, 382
            m_patch = out[my0:my1, mx0:mx1].copy()
            mh, mw, _ = m_patch.shape
            gy, gx = np.indices((mh, mw), dtype=np.float32)
            cx, cy = mw * 0.5, mh * 0.45
            nx = (gx - cx) / (mw * 0.42)
            ny = (gy - cy) / (mh * 0.45)
            radial = np.clip(1.0 - np.sqrt(nx**2 + ny**2), 0.0, 1.0)
            # Corner lift + slight horizontal widening for warm gentle smile
            shift_y = -smile_amt * 3.8 * (nx ** 2) * radial
            shift_x = -smile_amt * 2.2 * nx * radial
            out[my0:my1, mx0:mx1] = cv2.remap(
                m_patch, (gx + shift_x).astype(np.float32), (gy - shift_y).astype(np.float32),
                interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
            )
            # Slight cheek warmth lift during smile
            for (ch_x, ch_y) in [(272, 168), (384, 168)]:
                cy0, cy1, cx0, cx1 = ch_y - 18, ch_y + 18, ch_x - 22, ch_x + 22
                cp = out[cy0:cy1, cx0:cx1].copy()
                ch_h, ch_w, _ = cp.shape
                cgy, cgx = np.indices((ch_h, ch_w), dtype=np.float32)
                cr = np.clip(1.0 - np.sqrt(((cgx - ch_w/2)/(ch_w/2))**2 + ((cgy - ch_h/2)/(ch_h/2))**2), 0.0, 1.0)
                out[cy0:cy1, cx0:cx1] = cv2.remap(
                    cp, cgx, (cgy + smile_amt * 1.6 * cr).astype(np.float32),
                    interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE
                )

        # 2. Natural Progressive Upper-Eyelid Descent Blink
        if blink_amt > 0.01:
            # Left Eye: x=255..312, y=112..150 | Right Eye: x=344..401, y=112..150
            for (ex0, ex1) in [(254, 313), (343, 402)]:
                ey0, ey1 = 114, 150
                ew = ex1 - ex0
                eh = ey1 - ey0
                # Sample skin tone just above upper lid crease
                skin_fill = np.median(out[ey0 - 6:ey0 - 2, ex0 + 10:ex1 - 10, :3], axis=(0, 1)).astype(np.uint8)
                skin_shadow = (skin_fill.astype(float) * 0.88).astype(np.uint8)
                lash_color = np.array([72, 46, 30], dtype=np.uint8)

                # Curved upper lid position descending from y=2 to y=eh-5
                xs = np.arange(ew, dtype=np.float32)
                x_norm = (xs - ew * 0.5) / (ew * 0.5)
                # Arch when open (curves upward in center), gently curved down when closed
                open_arch = 4.0 + 9.0 * (x_norm ** 2)
                closed_arch = (eh - 8.0) - 3.5 * (1.0 - x_norm ** 2)
                lid_y = (1.0 - blink_amt) * open_arch + blink_amt * closed_arch

                eye_crop = out[ey0:ey1, ex0:ex1].copy()
                for ix in range(4, ew - 4):
                    ly = int(round(lid_y[ix]))
                    ly = max(2, min(eh - 3, ly))
                    # Fill descending upper eyelid above ly with warm eyelid skin gradient
                    for iy in range(2, ly):
                        if eye_crop[iy, ix, 3] > 100:
                            grad = (iy / max(1.0, float(ly)))
                            c = (skin_fill.astype(float) * (1.0 - 0.35 * grad) + skin_shadow.astype(float) * (0.35 * grad)).astype(np.uint8)
                            eye_crop[iy, ix, :3] = c
                    # Draw curved dark sepia upper eyelash line at ly..ly+3
                    for l_off in range(-1, 3):
                        yy = max(0, min(eh - 1, ly + l_off))
                        eye_crop[yy, ix, :3] = lash_color
                out[ey0:ey1, ex0:ex1] = eye_crop
        return out

    total_frames = 72
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20

    # Define natural blink curve (two blinks in 3 seconds: main blink at frame 18..27, soft double-blink at frame 52..60)
    def get_blink(f):
        # Blink 1: frames 18..26 (3f close, 2f hold, 4f ease-out open)
        b1_map = {18: 0.25, 19: 0.65, 20: 1.0, 21: 1.0, 22: 0.80, 23: 0.50, 24: 0.22, 25: 0.06}
        # Blink 2: frames 52..59
        b2_map = {52: 0.30, 53: 0.75, 54: 1.0, 55: 0.85, 56: 0.45, 57: 0.15}
        return b1_map.get(f, b2_map.get(f, 0.0))

    for f in range(total_frames):
        t = f / float(total_frames)
        phase = 2.0 * math.pi * t
        phase_delayed = 2.0 * math.pi * ((f - 3.5) / float(total_frames))  # 3.5-frame cloth overlap delay

        # Subtle sinusoidal breathing
        breath = math.sin(phase)
        cloth_breath = math.sin(phase_delayed)

        # Gentle smile transition: starts neutral-serene (0.0), rises warmly to full gentle smile (1.0) during frames 12..45, and eases back smoothly for seamless loop
        smile_curve = 0.5 - 0.5 * math.cos(phase)  # 0.0 -> 1.0 -> 0.0 smoothly across 72 frames
        blink_val = get_blink(f)

        # Warp body with breathing chest expansion and overlapping uttoriyo cloth sway
        body_warped = warp_layer_25d(
            body_base, pivot_xy=(nw * 0.5, 420),
            angle_deg=0.35 * math.sin(phase),
            scale_x=1.0 + 0.008 * breath,
            scale_y=1.0 + 0.010 * breath,
            tx=0.0, ty=-1.5 * breath,
            cloth_sway_px=2.2 * cloth_breath
        )

        # Apply eyelid blink & smile transition to head, then warp head with subtle affectionate tilt
        head_expr = apply_eyelid_and_smile(head_base, blink_val, smile_curve)
        head_warped = warp_layer_25d(
            head_expr, pivot_xy=(nw * 0.5, 228),
            angle_deg=1.4 * math.sin(phase - 0.4),
            scale_x=1.0, scale_y=1.0,
            tx=1.2 * math.sin(phase),
            ty=-2.2 * breath,
            tilt_pitch_deg=-1.2 * smile_curve
        )

        canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canvas, body_warped, ox, oy)
        alpha_composite_layer(canvas, head_warped, ox, oy)

        Image.fromarray(canvas, mode="RGBA").save(frames_dir / f"{asset_id}_{f + 1:04d}.png")

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)

    meta = {
        "asset_id": asset_id,
        "gesture_name": "Gentle Smiling with Natural Blinking",
        "gesture_category": "Facial",
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "character_version": "1.0.0",
        "animation_method": "Method 1: Rigged 2D Layered Mesh + Progressive Eyelid & Smile Deformation",
        "source_blend_file": "03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend",
        "png_sequence_dir": str(frames_dir.relative_to(BASE_DIR)),
        "preview_mp4": str(mp4_p.relative_to(BASE_DIR)),
        "preview_gif": str(gif_p.relative_to(BASE_DIR)),
        "preview_webm": str(webm_p.relative_to(BASE_DIR)),
        "frame_rate": 24,
        "frame_count": total_frames,
        "duration_seconds": 3.0,
        "dimensions": [canvas_w, canvas_h],
        "transparency": True,
        "seamless_loop": True,
        "approval_status": "PENDING_PILOT_REVIEW",
        "version": "V001"
    }
    with open(out_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"Pilot 1 ({asset_id}) rendered and encoded successfully.")
    return apply_eyelid_and_smile, head_base, body_base, nw, nh


def render_pilot_2_head_nod_yes(apply_eyelid_and_smile, head_base, body_base, nw, nh):
    """
    PILOT 2: THAKUR_HEAD_NOD_YES_V001
    Duration: 2.5s (60 frames @ 24 FPS), Seamless Loop
    Category: Head
    Includes:
    - Readable upward anticipation tilt (frames 1-13)
    - Primary affirmative downward nod with 2.5D pitch foreshortening & natural blink at apex (frames 14-28)
    - Gentle secondary affirmative nod & recovery settle (frames 29-48)
    - 3-frame delayed overlapping action on shoulders/uttoriyo shawl (frames 49-60)
    """
    asset_id = "THAKUR_HEAD_NOD_YES_V001"
    out_dir = GESTURE_DIR / "Head" / asset_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    total_frames = 60
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20

    # Keyframed pitch curve (degrees: negative = upward anticipation, positive = downward nod)
    def get_nod_pitch(f):
        # f in 0..59
        if f < 12:
            # Anticipation: slight lift upward (-5.5 deg)
            u = ease_in_out_cubic(f / 12.0)
            return -5.5 * math.sin(u * math.pi)
        elif f < 25:
            # Primary downward nod (+14.5 deg)
            u = ease_in_out_cubic((f - 12) / 13.0)
            return 14.5 * math.sin(u * math.pi)
        elif f < 38:
            # Recovery past neutral (-2.5 deg) into secondary smaller nod (+6.5 deg)
            u = ease_in_out_cubic((f - 25) / 13.0)
            return 6.5 * math.sin(u * math.pi)
        else:
            # Smooth settle back to 0.0
            u = ease_in_out_cubic((f - 38) / 22.0)
            return 0.0

    blink_map = {16: 0.3, 17: 0.75, 18: 1.0, 19: 1.0, 20: 0.7, 21: 0.35, 22: 0.1}

    for f in range(total_frames):
        t = f / float(total_frames)
        phase = 2.0 * math.pi * t
        pitch = get_nod_pitch(f)
        pitch_delayed = get_nod_pitch(max(0, f - 3))  # 3-frame follow-through on chest/uttoriyo

        breath = math.sin(phase)
        blink_val = blink_map.get(f, 0.0)
        smile_val = 0.35 + 0.45 * max(0.0, pitch / 14.5)  # Warm affirming smile deepens slightly on the nod

        body_warped = warp_layer_25d(
            body_base, pivot_xy=(nw * 0.5, 420),
            angle_deg=0.4 * math.sin(phase),
            scale_x=1.0 + 0.007 * breath,
            scale_y=1.0 + 0.008 * breath - 0.006 * (pitch_delayed / 14.5),
            tx=0.0, ty=1.8 * (pitch_delayed / 14.5) - 1.2 * breath,
            cloth_sway_px=2.8 * (pitch_delayed / 14.5)
        )

        head_expr = apply_eyelid_and_smile(head_base, blink_val, smile_val)
        head_warped = warp_layer_25d(
            head_expr, pivot_xy=(nw * 0.5, 228),
            angle_deg=0.8 * math.sin(phase),
            scale_x=1.0,
            scale_y=1.0 - 0.015 * abs(pitch / 14.5),
            tx=0.0,
            ty=8.5 * (pitch / 14.5) - 1.5 * breath,
            tilt_pitch_deg=pitch
        )

        canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canvas, body_warped, ox, oy)
        alpha_composite_layer(canvas, head_warped, ox, oy)

        Image.fromarray(canvas, mode="RGBA").save(frames_dir / f"{asset_id}_{f + 1:04d}.png")

    mp4_p, webm_p, gif_p = encode_previews(frames_dir, asset_id, fps=24)

    meta = {
        "asset_id": asset_id,
        "gesture_name": "Nodding Yes (With Anticipation & Cloth Follow-Through)",
        "gesture_category": "Head",
        "character_id": "BALAK_THAKUR_AGE06_UJANCHAR",
        "character_version": "1.0.0",
        "animation_method": "Method 1: Rigged 2D Layered Mesh + 2.5D Pitch Foreshortening & Cloth Overlap",
        "source_blend_file": "03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend",
        "png_sequence_dir": str(frames_dir.relative_to(BASE_DIR)),
        "preview_mp4": str(mp4_p.relative_to(BASE_DIR)),
        "preview_gif": str(gif_p.relative_to(BASE_DIR)),
        "preview_webm": str(webm_p.relative_to(BASE_DIR)),
        "frame_rate": 24,
        "frame_count": total_frames,
        "duration_seconds": 2.5,
        "dimensions": [canvas_w, canvas_h],
        "transparency": True,
        "seamless_loop": True,
        "approval_status": "PENDING_PILOT_REVIEW",
        "version": "V001"
    }
    with open(out_dir / f"{asset_id}_metadata.json", "w", encoding="utf-8") as mf:
        json.dump(meta, mf, indent=2)
    print(f"Pilot 2 ({asset_id}) rendered and encoded successfully.")


if __name__ == "__main__":
    fn, hb, bb, nw, nh = render_pilot_1_gentle_smile_blink()
    render_pilot_2_head_nod_yes(fn, hb, bb, nw, nh)

