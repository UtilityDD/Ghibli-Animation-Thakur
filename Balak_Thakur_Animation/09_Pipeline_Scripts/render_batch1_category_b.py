"""
BATCH 1B RENDERER (Agent 2 — Authentic Hand-Painted Head Movement Specialist):
Renders all 8 Category B (Head Movements) 24 FPS animations using ONLY the 100% Authentic Hand-Painted
Registered Expression Plates (`registered_seated_02_gentle_smile.png`, `06_curious.png`, `11_thoughtful.png`, `10_peaceful.png`)
and the Unified Continuous 2D Mesh Deformer (`deform_unified_character_mesh`) with natural eyelid blinking!
ZERO procedural iris stretching or synthetic mouth drawing -> 100% pure hand-painted eyes and expressions!
"""
import math
import shutil
from pathlib import Path
import numpy as np
from PIL import Image

from render_pilot_animations_1_to_3 import (
    BASE_DIR, LAYERS_DIR, GESTURE_DIR, PREVIEW_DIR,
    ease_in_out_cubic, alpha_composite_layer
)
from render_pilot_animations_3_to_5 import interpolate_flow_rgba
from expand_gesture_library_part1_AB import save_animation_package
from test_fix_single_animation import (
    ART_DIR, apply_natural_eyelid_blink_and_smile, deform_unified_character_mesh
)


def load_registered_plate(ename: str) -> np.ndarray:
    return np.array(Image.open(LAYERS_DIR / f"registered_seated_{ename}.png").convert("RGBA"))


def render_category_b_authentic():
    p_neutral = load_registered_plate("01_neutral")
    p_smile = load_registered_plate("02_gentle_smile")
    p_curious = load_registered_plate("06_curious")
    p_peaceful = load_registered_plate("10_peaceful")
    p_thoughtful = load_registered_plate("11_thoughtful")
    # 100% authentic hand-painted Looking-Left plate (full mirrored bust with seamless cranium & jawline registration):
    p_look_left = np.array(Image.open(LAYERS_DIR / "registered_seated_look_left.png").convert("RGBA"))

    nh, nw, _ = p_smile.shape
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 10
    b_single = {16: 0.25, 17: 0.75, 18: 1.0, 19: 0.85, 20: 0.40, 21: 0.12}

    def env_hold(f, tf=60, ramp=15):
        if f < ramp:
            return ease_in_out_cubic(f / float(ramp))
        elif f < tf - ramp:
            return 1.0
        else:
            return 1.0 - ease_in_out_cubic((f - (tf - ramp)) / float(ramp))

    def build_head_anim(asset_id, title, start_p, active_p, motion_fn, total_frames=60):
        flow_steps = 10
        cached_interp = [
            interpolate_flow_rgba(start_p, active_p, i / float(flow_steps))
            for i in range(flow_steps + 1)
        ]

        frames = []
        for f in range(total_frames):
            t = f / float(total_frames)
            phase = 2.0 * math.pi * t
            cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total_frames))

            m_kw = motion_fn(f, total_frames, phase)
            u = m_kw.get("u", env_hold(f, total_frames, 15))
            f_idx = max(0.0, min(1.0, u)) * flow_steps
            i0 = int(math.floor(f_idx))
            i1 = min(flow_steps, i0 + 1)
            frac = f_idx - i0
            cur_p = cached_interp[i0].copy() if (frac <= 0.001 or i0 == i1) else np.clip(
                cached_interp[i0].astype(np.float32) * (1.0 - frac) + cached_interp[i1].astype(np.float32) * frac,
                0, 255
            ).astype(np.uint8)

            b_val = b_single.get(f, 0.0)
            if b_val > 0.01:
                cur_p = apply_natural_eyelid_blink_and_smile(cur_p, b_val, 0.0)

            deformed = deform_unified_character_mesh(
                cur_p,
                head_pitch_deg=m_kw.get("pitch", 0.0),
                head_yaw_deg=m_kw.get("yaw", 0.0),
                head_roll_deg=m_kw.get("roll", 0.0),
                breath_phase=phase,
                cloth_phase=cloth_phase
            )

            canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
            alpha_composite_layer(canv, deformed, ox, oy)
            frames.append(canv)

        save_animation_package(
            asset_id, "Head", title,
            "Method 1: Authentic Hand-Painted Expression Plate + Unified Continuous 2D Mesh Rig",
            frames, seamless_loop=True
        )
        shutil.copyfile(PREVIEW_DIR / "GIF" / f"{asset_id}.gif", ART_DIR / f"{asset_id}.gif")

    # 1. THAKUR_HEAD_NOD_YES_V001
    def nod_pitch(f):
        if f < 11:
            return -4.5 * math.sin(ease_in_out_cubic(f / 11.0) * math.pi)
        elif f < 25:
            return 12.5 * math.sin(ease_in_out_cubic((f - 11) / 14.0) * math.pi)
        elif f < 38:
            return 5.5 * math.sin(ease_in_out_cubic((f - 25) / 13.0) * math.pi)
        else:
            return 0.0

    build_head_anim(
        "THAKUR_HEAD_NOD_YES_V001", "Nodding Yes with Anticipation & Cloth Follow-Through",
        p_smile, p_smile,
        lambda f, tf, ph: dict(u=0.0, pitch=nod_pitch(f), yaw=0.0, roll=0.6 * math.sin(ph))
    )

    # 2. THAKUR_HEAD_SHAKE_NO_V001
    def shake_yaw(f):
        if f < 8:
            return 4.5 * math.sin(ease_in_out_cubic(f / 8.0) * math.pi * 0.5)
        elif f < 22:
            u = ease_in_out_cubic((f - 8) / 14.0)
            return 4.5 * (1.0 - u) - 12.5 * u
        elif f < 36:
            u = ease_in_out_cubic((f - 22) / 14.0)
            return -12.5 * (1.0 - u) + 10.5 * u
        elif f < 48:
            u = ease_in_out_cubic((f - 36) / 12.0)
            return 10.5 * (1.0 - u) - 3.5 * u
        else:
            u = ease_in_out_cubic((f - 48) / 12.0)
            return -3.5 * (1.0 - u)

    build_head_anim(
        "THAKUR_HEAD_SHAKE_NO_V001", "Shaking Head No Gently",
        p_neutral, p_smile,
        lambda f, tf, ph: dict(u=0.5, pitch=1.0 * abs(shake_yaw(f) / 12.5), yaw=shake_yaw(f), roll=0.22 * shake_yaw(f))
    )

    # 3. THAKUR_HEAD_TILT_V001 (Uses authentic hand-painted 06_curious!)
    build_head_anim(
        "THAKUR_HEAD_TILT_V001", "Tilting Head Affectionately",
        p_smile, p_curious,
        lambda f, tf, ph: dict(u=env_hold(f), pitch=-1.0 * env_hold(f), yaw=2.0 * env_hold(f), roll=5.5 * env_hold(f))
    )

    # 4. THAKUR_HEAD_LOOK_LEFT_V001 (Uses 100% authentic hand-painted registered_seated_look_left!)
    build_head_anim(
        "THAKUR_HEAD_LOOK_LEFT_V001", "Looking Left (Viewer's Left)",
        p_smile, p_look_left,
        lambda f, tf, ph: dict(u=env_hold(f), pitch=-0.8 * env_hold(f), yaw=-6.5 * env_hold(f), roll=-1.2 * env_hold(f))
    )

    # 5. THAKUR_HEAD_LOOK_RIGHT_V001 (Uses authentic hand-painted 11_thoughtful gaze!)
    build_head_anim(
        "THAKUR_HEAD_LOOK_RIGHT_V001", "Looking Right (Viewer's Right)",
        p_smile, p_thoughtful,
        lambda f, tf, ph: dict(u=env_hold(f), pitch=-0.8 * env_hold(f), yaw=6.5 * env_hold(f), roll=1.2 * env_hold(f))
    )

    # 6. THAKUR_HEAD_LOOK_UP_V001
    build_head_anim(
        "THAKUR_HEAD_LOOK_UP_V001", "Looking Upward with Serene Wonder",
        p_smile, p_curious,
        lambda f, tf, ph: dict(u=0.5 * env_hold(f), pitch=-12.0 * env_hold(f), yaw=0.0, roll=0.8 * env_hold(f))
    )

    # 7. THAKUR_HEAD_LOOK_DOWN_V001
    build_head_anim(
        "THAKUR_HEAD_LOOK_DOWN_V001", "Looking Downward Gently",
        p_smile, p_peaceful,
        lambda f, tf, ph: dict(u=0.35 * env_hold(f), pitch=12.0 * env_hold(f), yaw=0.0, roll=0.0)
    )

    # 8. THAKUR_HEAD_TURN_TO_CAMERA_V001
    def turn_cam_u(f):
        return 1.0 - env_hold(f, 60, 16)

    build_head_anim(
        "THAKUR_HEAD_TURN_TO_CAMERA_V001", "Turning Head Towards the Camera with Warm Smile",
        p_smile, p_look_left,
        lambda f, tf, ph: dict(u=turn_cam_u(f), pitch=-1.0 * turn_cam_u(f), yaw=-7.0 * turn_cam_u(f), roll=-1.2 * turn_cam_u(f))
    )


if __name__ == "__main__":
    render_category_b_authentic()
    print("Authentic Hand-Painted Category B (8 Head Animations) completed successfully.")
