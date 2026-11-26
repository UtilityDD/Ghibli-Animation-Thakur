"""
Param Bismoy Balak Thakur (পরম বিস্ময় বালক ঠাকুর)
Reusable Cinematic Episode Intro Generator (Ghibli Aesthetic, 24 FPS)

Creates a grand, atmospheric episodic pre-roll title sequence for any episode:
1. Base Art: High-detail watercolor title plate (intro.jpeg / animated title GIF)
2. Character Integration: Balak Thakur in serene Sukhasana with subtle golden aura
3. Atmospheric VFX: Floating golden sunbeam bokeh motes, crepuscular rays, cinematic vignette
4. Dynamic Episode Plate: Reusable for any episode number, Bengali title, and English title
5. Cinema Scope: 2.39:1 letterbox bars with organic ease-in
6. Full 4-Format Deliverables: PNG frames (24 FPS), MP4 (H.264), WebM (transparent), GIF, and JSON metadata.
"""
import os
import sys
import json
import math
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
INTRO_IMG_PATH = BASE_DIR.parent / "intro.jpeg"
INTRO_GIF_PATH = BASE_DIR.parent / "THAKUR_EPISODE_TITLE_CINEMA_4K_V001.gif"
MEDITATING_FRAMES_DIR = BASE_DIR / "04_Gesture_Library" / "Devotional" / "THAKUR_DEVOTIONAL_MEDITATING_V001" / "frames"
SMILE_FRAMES_DIR = BASE_DIR / "04_Gesture_Library" / "Facial" / "THAKUR_SMILE_GENTLE_BLINK_V001" / "frames"
OUTPUT_ROOT_DIR = BASE_DIR / "06_Scene_Compositions" / "Episode_Intros"

# Font configurations
FONT_BENGALI_PATH = "C:/Windows/Fonts/vrindab.ttf"
FONT_BENGALI_REG_PATH = "C:/Windows/Fonts/vrinda.ttf"
FONT_ENG_PATH = "C:/Windows/Fonts/georgiab.ttf"
FONT_ENG_REG_PATH = "C:/Windows/Fonts/georgia.ttf"


def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - math.pow(-2.0 * t + 2.0, 3.0) / 2.0


def ease_out_quad(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) * (1.0 - t)


class GoldenBokehParticle:
    """Organic floating golden dust mote drifting in sacred temple sunlight."""
    def __init__(self, rng: np.random.RandomState, w: int, h: int):
        self.x0 = rng.uniform(w * 0.05, w * 0.95)
        self.y0 = rng.uniform(h * 0.1, h * 0.9)
        self.radius = rng.uniform(2.5, 7.5)
        self.speed_y = rng.uniform(0.6, 1.8)
        self.wave_freq = rng.uniform(0.03, 0.08)
        self.wave_amp = rng.uniform(8.0, 24.0)
        self.alpha_peak = rng.uniform(110, 220)
        self.phase = rng.uniform(0, 2 * math.pi)

    def get_pos_and_alpha(self, frame_idx: int, total_frames: int, h: int) -> Tuple[float, float, float, float]:
        t = frame_idx
        cur_y = (self.y0 - self.speed_y * t) % h
        cur_x = self.x0 + math.sin(self.wave_freq * t + self.phase) * self.wave_amp
        
        # Breathing brightness pulse
        pulse = 0.75 + 0.25 * math.sin(0.1 * t + self.phase)
        alpha = self.alpha_peak * pulse
        return cur_x, cur_y, self.radius, alpha


def render_ornamental_divider(w: int, h: int, color=(243, 202, 101, 230)) -> Image.Image:
    """Generates an elegant Indian/Bengali classical horizontal rule with diamond finials."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    mid_y = h // 2
    cx = w // 2
    rule_half_w = int(w * 0.42)
    
    # Gradient line out from center
    for x in range(cx - rule_half_w, cx + rule_half_w):
        dist_from_c = abs(x - cx) / float(rule_half_w)
        a = int(color[3] * max(0.0, 1.0 - dist_from_c * dist_from_c))
        draw.line([(x, mid_y), (x, mid_y)], fill=(color[0], color[1], color[2], a), width=2)
    
    # Center diamond
    dia_sz = 6
    dia_pts = [(cx, mid_y - dia_sz), (cx + dia_sz, mid_y), (cx, mid_y + dia_sz), (cx - dia_sz, mid_y)]
    draw.polygon(dia_pts, fill=color)
    
    # Outer side dots
    for dot_offset in [-int(rule_half_w * 0.5), int(rule_half_w * 0.5)]:
        draw.ellipse([(cx + dot_offset - 2, mid_y - 2), (cx + dot_offset + 2, mid_y + 2)], fill=color)
        
    return img


def create_crepuscular_sunbeam_overlay(w: int, h: int, angle_deg: float = 38.0, intensity: float = 0.35) -> np.ndarray:
    """Creates soft volumetric sunlight god-rays angling down from top-left."""
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    # Generate 5-6 soft ray bands
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    proj = xx * sin_a + yy * cos_a
    
    # Ray pattern via multi-frequency sines
    rays = (
        0.5 + 0.3 * np.sin(proj * 0.015)
        + 0.15 * np.sin(proj * 0.035 + 1.2)
        + 0.1 * np.sin(proj * 0.008 + 2.4)
    )
    rays = np.clip(rays, 0.0, 1.0)
    
    # Vertical falloff: strongest in upper mid, fading gently towards bottom
    v_falloff = np.clip((h - yy) / float(h), 0.15, 1.0)
    ray_alpha = (rays * v_falloff * 255.0 * intensity).astype(np.uint8)
    
    # Warm golden sunlight tone: RGB(255, 235, 175)
    overlay[:, :, 0] = 255
    overlay[:, :, 1] = 230
    overlay[:, :, 2] = 165
    overlay[:, :, 3] = ray_alpha
    return overlay


def build_episode_intro_sequence(
    episode_num: int = 1,
    title_bengali: str = "কালীপূজার রাত্রে মহাবির্ভাব",
    title_english: str = "The Divine Advent on Kali Puja Night",
    chapter_ref: str = "শ্রীশ্রী ১০৮ স্বামী স্বরূপানন্দ পরমহংসদেব শৈশব লীলা — উজানচর",
    total_frames: int = 144,  # 6.0 seconds @ 24 FPS
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    enable_letterbox: bool = True
) -> Path:
    """Renders the complete 24 FPS cinematic intro sequence for an episode."""
    ep_slug = f"EPISODE_{episode_num:02d}_INTRO"
    output_dir = OUTPUT_ROOT_DIR / ep_slug
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=======================================================")
    print(f"🎬 RENDERING CINEMATIC INTRO: Episode {episode_num}")
    print(f"   Bengali Title: {title_bengali}")
    print(f"   English Title: {title_english}")
    print(f"   Duration: {total_frames} frames ({total_frames/fps:.1f}s @ {fps} FPS)")
    print(f"   Output: {output_dir}")
    print(f"=======================================================\n")

    # 1. Load Background Master Plate
    if INTRO_IMG_PATH.exists():
        bg_master = Image.open(INTRO_IMG_PATH).convert("RGBA")
        if bg_master.size != (width, height):
            bg_master = bg_master.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # Fallback warm Ghibli parchment gradient
        bg_master = Image.new("RGBA", (width, height), (38, 28, 22, 255))

    bg_arr = np.array(bg_master)

    # 2. Load Meditating/Smiling Balak Thakur character cycle
    char_frames = []
    anim_source_dir = MEDITATING_FRAMES_DIR if MEDITATING_FRAMES_DIR.exists() else SMILE_FRAMES_DIR
    if anim_source_dir.exists():
        png_paths = sorted(anim_source_dir.glob("*.png"))
        for p in png_paths:
            char_frames.append(Image.open(p).convert("RGBA"))
    print(f"Loaded {len(char_frames)} character motion frames for integration.")

    # 3. Setup Fonts
    try:
        font_ep = ImageFont.truetype(FONT_ENG_PATH, 20)
        font_bn = ImageFont.truetype(FONT_BENGALI_PATH, 42)
        font_en = ImageFont.truetype(FONT_ENG_PATH, 22)
        font_ref = ImageFont.truetype(FONT_BENGALI_REG_PATH, 16)
    except Exception as e:
        print(f"Warning loading system fonts: {e}. Falling back to default.")
        font_ep = ImageFont.load_default()
        font_bn = font_ep
        font_en = font_ep
        font_ref = font_ep

    # 4. Initialize 45 Atmospheric Bokeh particles
    rng = np.random.RandomState(42 + episode_num)
    particles = [GoldenBokehParticle(rng, width, height) for _ in range(45)]

    # 5. Precompute sunbeams and ornamental divider
    sunbeam_overlay = create_crepuscular_sunbeam_overlay(width, height, angle_deg=34.0, intensity=0.30)
    divider_img = render_ornamental_divider(w=int(width * 0.65), h=16, color=(245, 205, 105, 235))

    rendered_images = []

    # Sequence Timing milestones (in frames)
    # 0 -> 30: Fade up from black, title emergence, sunbeam activation
    # 30 -> 72: Character settles, subtitle plate slides in with golden bloom
    # 72 -> 120: Golden hold, breathing glow, particle ascension
    # 120 -> 144: Cinematic dissolve to first scene
    
    for f_idx in range(total_frames):
        t = f_idx / float(total_frames - 1)
        
        # Continuous slow Ken Burns push-in: scale 1.000 -> 1.045
        zoom_factor = 1.0 + 0.045 * (f_idx / float(total_frames))
        zw = int(width * zoom_factor)
        zh = int(height * zoom_factor)
        
        # Crop center after zoom
        bg_zoomed = cv2.resize(bg_arr, (zw, zh), interpolation=cv2.INTER_LINEAR)
        ox = (zw - width) // 2
        oy = (zh - height) // 2
        frame_canvas = bg_zoomed[oy:oy + height, ox:ox + width].copy()

        # Fade in from black (Frames 0..28)
        if f_idx < 28:
            fade_in = ease_out_quad(f_idx / 28.0)
            frame_canvas[:, :, :3] = (frame_canvas[:, :, :3].astype(np.float32) * fade_in).astype(np.uint8)

        # Dissolve out to black at the end (Frames 126..144)
        if f_idx > 126:
            fade_out = 1.0 - ease_in_out_cubic((f_idx - 126) / 18.0)
            frame_canvas[:, :, :3] = (frame_canvas[:, :, :3].astype(np.float32) * fade_out).astype(np.uint8)

        # --- Volumetric Crepuscular Sunbeams ---
        beam_pulse = 0.85 + 0.15 * math.sin(0.08 * f_idx)
        beam_alpha = (sunbeam_overlay[:, :, 3].astype(np.float32) * beam_pulse / 255.0)[:, :, None]
        beam_rgb = sunbeam_overlay[:, :, :3].astype(np.float32)
        frame_canvas[:, :, :3] = np.clip(
            frame_canvas[:, :, :3].astype(np.float32) * (1.0 - beam_alpha * 0.4) + beam_rgb * (beam_alpha * 0.4),
            0, 255
        ).astype(np.uint8)

        # Convert to PIL for typography and character layering
        pil_frame = Image.fromarray(frame_canvas, mode="RGBA")

        # --- Character Integration (Balak Thakur in Sacred Golden Rim) ---
        if char_frames:
            char_idx = f_idx % len(char_frames)
            char_img = char_frames[char_idx]
            
            # Place Thakur gracefully on lower right quadrant or centered
            # Scale Thakur to fit harmoniously: seated height ~380 px
            c_scale = 360.0 / float(char_img.height)
            cw = int(char_img.width * c_scale)
            ch = int(char_img.height * c_scale)
            char_resized = char_img.resize((cw, ch), Image.Resampling.LANCZOS)
            
            # Position: Right-balanced, chest above bottom
            char_x = int(width * 0.68 - cw // 2)
            char_y = int(height * 0.88 - ch)
            
            # Sacred Rim Glow behind Thakur
            glow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(glow_layer)
            glow_pulse = 0.8 + 0.2 * math.sin(0.12 * f_idx)
            g_cx = char_x + cw // 2
            g_cy = char_y + int(ch * 0.45)
            g_r = int(140 * glow_pulse)
            g_draw.ellipse(
                [(g_cx - g_r, g_cy - g_r), (g_cx + g_r, g_cy + g_r)],
                fill=(255, 225, 140, int(65 * glow_pulse))
            )
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(38))
            pil_frame = Image.alpha_composite(pil_frame, glow_layer)
            
            # Composite Character
            pil_frame.alpha_composite(char_resized, (char_x, char_y))

        # --- Dynamic Episode Subtitle Plate ---
        # Starts entering at frame 24, fully settled by frame 48
        plate_alpha = 0.0
        if f_idx >= 24:
            plate_alpha = ease_out_quad(min(1.0, (f_idx - 24) / 24.0))

        if plate_alpha > 0.01:
            plate_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            p_draw = ImageDraw.Draw(plate_layer)
            
            # Text layout anchor (Left quadrant or center)
            # Center of text area: x = width * 0.38, y = height * 0.58
            text_cx = int(width * 0.42)
            base_y = int(height * 0.52)
            
            # Subtle slide-up motion on entrance
            y_offset = int((1.0 - plate_alpha) * 18.0)
            cur_y = base_y + y_offset
            
            # 1. "EPISODE 01" Roman Header
            ep_str = f"E P I S O D E   {episode_num:02d}"
            ep_bbox = p_draw.textbbox((0, 0), ep_str, font=font_ep)
            ep_w = ep_bbox[2] - ep_bbox[0]
            ep_x = text_cx - ep_w // 2
            ep_y = cur_y - 75
            
            # Shadow
            p_draw.text((ep_x + 1, ep_y + 1), ep_str, font=font_ep, fill=(20, 12, 8, int(180 * plate_alpha)))
            p_draw.text((ep_x, ep_y), ep_str, font=font_ep, fill=(245, 205, 110, int(240 * plate_alpha)))
            
            # 2. Main Bengali Title with Golden Bloom
            bn_bbox = p_draw.textbbox((0, 0), title_bengali, font=font_bn)
            bn_w = bn_bbox[2] - bn_bbox[0]
            bn_x = text_cx - bn_w // 2
            bn_y = cur_y - 40
            
            # Ambient glow behind Bengali title
            for gx in [-2, 0, 2]:
                for gy in [-2, 0, 2]:
                    p_draw.text((bn_x + gx, bn_y + gy), title_bengali, font=font_bn, fill=(210, 140, 45, int(90 * plate_alpha)))
            p_draw.text((bn_x + 2, bn_y + 2), title_bengali, font=font_bn, fill=(15, 8, 4, int(220 * plate_alpha)))
            p_draw.text((bn_x, bn_y), title_bengali, font=font_bn, fill=(255, 248, 225, int(255 * plate_alpha)))
            
            # 3. Ornamental Divider
            div_w, div_h = divider_img.size
            div_x = text_cx - div_w // 2
            div_y = cur_y + 22
            div_stamp = divider_img.copy()
            div_alpha = (np.array(div_stamp)[:, :, 3].astype(np.float32) * plate_alpha).astype(np.uint8)
            div_stamp.putalpha(Image.fromarray(div_alpha))
            plate_layer.alpha_composite(div_stamp, (div_x, div_y))
            
            # 4. English Subtitle
            en_upper = title_english.upper()
            en_bbox = p_draw.textbbox((0, 0), en_upper, font=font_en)
            en_w = en_bbox[2] - en_bbox[0]
            en_x = text_cx - en_w // 2
            en_y = cur_y + 44
            p_draw.text((en_x + 1, en_y + 1), en_upper, font=font_en, fill=(20, 10, 6, int(180 * plate_alpha)))
            p_draw.text((en_x, en_y), en_upper, font=font_en, fill=(240, 222, 185, int(230 * plate_alpha)))
            
            # 5. Canonical Chapter Reference footer
            ref_bbox = p_draw.textbbox((0, 0), chapter_ref, font=font_ref)
            ref_w = ref_bbox[2] - ref_bbox[0]
            ref_x = text_cx - ref_w // 2
            ref_y = cur_y + 80
            p_draw.text((ref_x + 1, ref_y + 1), chapter_ref, font=font_ref, fill=(15, 8, 4, int(140 * plate_alpha)))
            p_draw.text((ref_x, ref_y), chapter_ref, font=font_ref, fill=(215, 190, 150, int(190 * plate_alpha)))
            
            pil_frame = Image.alpha_composite(pil_frame, plate_layer)

        # --- Floating Golden Bokeh Particles ---
        particle_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        part_draw = ImageDraw.Draw(particle_layer)
        for p in particles:
            px, py, pr, pa = p.get_pos_and_alpha(f_idx, total_frames, height)
            if pa > 5:
                # Soft dual-halo bokeh
                part_draw.ellipse(
                    [(px - pr * 1.8, py - pr * 1.8), (px + pr * 1.8, py + pr * 1.8)],
                    fill=(255, 215, 120, int(pa * 0.35))
                )
                part_draw.ellipse(
                    [(px - pr, py - pr), (px + pr, py + pr)],
                    fill=(255, 245, 190, int(pa))
                )
        particle_layer = particle_layer.filter(ImageFilter.GaussianBlur(1.2))
        pil_frame = Image.alpha_composite(pil_frame, particle_layer)

        # --- Cinematic 2.39:1 Anamorphic Scope Bars ---
        if enable_letterbox:
            # 2.39:1 scope on 16:9 gives ~84 px black bars top and bottom
            bar_h = int(height * 0.11)
            # Smoothly close in at start
            bar_cur_h = min(bar_h, int(bar_h * min(1.0, f_idx / 18.0)))
            if bar_cur_h > 0:
                scope_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                s_draw = ImageDraw.Draw(scope_layer)
                s_draw.rectangle([(0, 0), (width, bar_cur_h)], fill=(12, 9, 7, 255))
                s_draw.rectangle([(0, height - bar_cur_h), (width, height)], fill=(12, 9, 7, 255))
                pil_frame = Image.alpha_composite(pil_frame, scope_layer)

        # Save frame PNG
        frame_name = f"{ep_slug}_{f_idx+1:04d}.png"
        frame_path = frames_dir / frame_name
        pil_frame.save(frame_path, format="PNG")
        rendered_images.append(pil_frame)

        if (f_idx + 1) % 24 == 0 or (f_idx + 1) == total_frames:
            print(f"Rendered frame {f_idx+1:03d} / {total_frames} ({(f_idx+1)/total_frames*100.0:.0f}%)")

    # 6. Export Multi-Format Deliverables
    print("\nExporting multi-format video deliverables...")

    # (A) MP4 Export (H.264, yuv420p)
    mp4_path = output_dir / f"{ep_slug}.mp4"
    ffmpeg_cmd_mp4 = [
        "ffmpeg", "-y", "-r", str(fps),
        "-i", str(frames_dir / f"{ep_slug}_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        str(mp4_path)
    ]
    try:
        subprocess.run(ffmpeg_cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Generated MP4: {mp4_path} ({mp4_path.stat().st_size / (1024*1024):.2f} MB)")
    except Exception as e:
        print(f"MP4 export notice: {e}")

    # (B) WebM Export (VP9 with alpha channel support)
    webm_path = output_dir / f"{ep_slug}.webm"
    ffmpeg_cmd_webm = [
        "ffmpeg", "-y", "-r", str(fps),
        "-i", str(frames_dir / f"{ep_slug}_%04d.png"),
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "24", "-b:v", "0",
        str(webm_path)
    ]
    try:
        subprocess.run(ffmpeg_cmd_webm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Generated WebM: {webm_path} ({webm_path.stat().st_size / (1024*1024):.2f} MB)")
    except Exception as e:
        print(f"WebM export notice: {e}")

    # (C) GIF Preview (subsampled for web preview size)
    gif_path = output_dir / f"{ep_slug}.gif"
    gif_frames = [im.resize((640, 360), Image.Resampling.BILINEAR).convert("P", palette=Image.Palette.ADAPTIVE) for im in rendered_images[::2]]
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=int(1000.0 / (fps / 2.0)),
        loop=0,
        optimize=True
    )
    print(f"✅ Generated GIF preview: {gif_path} ({gif_path.stat().st_size / (1024*1024):.2f} MB)")

    # (D) Metadata JSON
    metadata = {
        "sequence_id": ep_slug,
        "type": "REUSABLE_EPISODE_CINEMATIC_INTRO",
        "episode_number": episode_num,
        "bengali_title": title_bengali,
        "english_title": title_english,
        "canonical_reference": chapter_ref,
        "resolution": [width, height],
        "fps": fps,
        "total_frames": total_frames,
        "duration_seconds": round(total_frames / float(fps), 2),
        "aspect_ratio": "16:9 Cinema Letterbox 2.39:1",
        "cue_points": {
            "fade_in_complete": 28,
            "subtitle_plate_in": 48,
            "golden_particle_peak": 84,
            "scene_dissolve_start": 126
        },
        "character": {
            "name": "Param Bismoy Balak Thakur",
            "age": 6,
            "location": "Ujanchar, Brahmanbaria",
            "aesthetic": "Studio Ghibli Hand-Painted Watercolor"
        }
    }
    meta_path = output_dir / f"{ep_slug}_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated metadata: {meta_path}")

    return output_dir


def main():
    parser = argparse.ArgumentParser(description="Reusable Cinematic Episode Intro Generator")
    parser.add_argument("--episode", type=int, default=1, help="Episode Number (e.g. 1)")
    parser.add_argument("--bengali", type=str, default="কালীপূজার রাত্রে মহাবির্ভাব", help="Bengali Title")
    parser.add_argument("--english", type=str, default="The Divine Advent on Kali Puja Night", help="English Title")
    parser.add_argument("--ref", type=str, default="শ্রীশ্রী ১০৮ স্বামী স্বরূপানন্দ পরমহংসদেব শৈশব লীলা — উজানচর", help="Canonical Chapter Ref")
    parser.add_argument("--frames", type=int, default=144, help="Total frames (default 144 @ 24fps = 6s)")
    parser.add_argument("--all-season1", action="store_true", help="Render all 5 canonical Season 1 intros")
    args = parser.parse_args()

    if args.all_season1:
        episodes = [
            (1, "কালীপূজার রাত্রে মহাবির্ভাব", "The Divine Advent on Kali Puja Night", "অধ্যায় ১: দীপান্বিতা কালীপূজায় শুভ আবির্ভাব"),
            (2, "অষ্টসিদ্ধি ও অলৌকিক যোগলীলা", "The Eight Supernatural Siddhis", "অধ্যায় ২-৩: অনন্ত শক্তির মহাপ্রকাশ ও যোগসিদ্ধি"),
            (3, "সপ্তহস্ত কালনাগ ও তিতাসের মেঘঝড়", "The Seven-Cubit Serpent & The Titas Tempest", "অধ্যায় ৪: কালনাগের শান্ত সমর্পণ ও ঝড় নিবারণ"),
            (4, "লোববাবু ও একু হাজরার পাঠশালা", "The Village Pathshalas of Ujanchar", "অধ্যায় ৫: বাল্যশিক্ষা ও অলৌকিক পাঠোদ্ধার"),
            (5, "সনাতন মাষ্টারের নয়নজল ও সামাদের পিতা", "Tears of Sanatan Master & The Peasant's Faith", "অধ্যায় ৬: পরীক্ষার খাতায় দৈব সত্য ও সামাদের পিতার রোগমুক্তি")
        ]
        for ep_num, bn, en, ch_ref in episodes:
            build_episode_intro_sequence(
                episode_num=ep_num,
                title_bengali=bn,
                title_english=en,
                chapter_ref=ch_ref,
                total_frames=args.frames
            )
    else:
        build_episode_intro_sequence(
            episode_num=args.episode,
            title_bengali=args.bengali,
            title_english=args.english,
            chapter_ref=args.ref,
            total_frames=args.frames
        )


if __name__ == "__main__":
    main()
