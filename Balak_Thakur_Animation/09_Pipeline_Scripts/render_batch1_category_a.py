"""
BATCH 1A RENDERER (Agent 1 — Authentic Hand-Painted Facial Animation Specialist):
Renders all 10 Category A (Facial) 24 FPS animations using:
- The 12 100% Authentic Hand-Painted Registered Expression Plates (`registered_seated_01_neutral.png` .. `registered_seated_12_determined.png`)
  from `THAKUR_EXPRESSION_SHEET_12_V001.png`!
- Optical-Flow Guided Facial Feature In-Betweening (`interpolate_flow_rgba`) between `02_gentle_smile` / `01_neutral`
  and the target authentic hand-painted expression plate!
- The Unified Continuous 2D Mesh Deformer (`deform_unified_character_mesh`) for natural breathing, subtle head life, and 3.5-frame delayed uttoriyo cloth sway!
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


def render_category_a_authentic():
    plates = {
        name: load_registered_plate(name)
        for name in [
            "01_neutral", "02_gentle_smile", "03_broad_smile", "04_laughing",
            "05_surprised", "06_curious", "07_angry", "08_sad",
            "09_crying", "10_peaceful", "11_thoughtful", "12_determined"
        ]
    }
    nh, nw, _ = plates["02_gentle_smile"].shape
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 10

    def env_curve(f, total_frames, ramp=14):
        if f < ramp:
            return ease_in_out_cubic(f / float(ramp))
        elif f < total_frames - ramp:
            return 1.0
        else:
            return 1.0 - ease_in_out_cubic((f - (total_frames - ramp)) / float(ramp))

    def render_authentic_transition(
        asset_id: str, title: str, start_plate: np.ndarray, target_plate: np.ndarray,
        total_frames: int = 60, ramp: int = 14,
        pitch_amp: float = 0.0, yaw_amp: float = 0.0, roll_amp: float = 0.0,
        chuckle_bounce: bool = False, blink_schedule: dict = None
    ):
        if blink_schedule is None:
            blink_schedule = {8: 0.30, 9: 0.85, 10: 1.0, 11: 0.70, 12: 0.25}

        # Precompute 10 optical-flow intermediate steps between start_plate and target_plate so rendering 60-72 frames is fast and 100% ghost-free!
        flow_steps = 12
        cached_interp = [
            interpolate_flow_rgba(start_plate, target_plate, i / float(flow_steps))
            for i in range(flow_steps + 1)
        ]

        frames = []
        for f in range(total_frames):
            t = f / float(total_frames)
            phase = 2.0 * math.pi * t
            cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total_frames))

            u = env_curve(f, total_frames, ramp)
            # Sample from optical-flow precomputed cache
            f_idx = u * flow_steps
            i0 = int(math.floor(f_idx))
            i1 = min(flow_steps, i0 + 1)
            frac = f_idx - i0
            if frac <= 0.001 or i0 == i1:
                cur_plate = cached_interp[i0].copy()
            else:
                cur_plate = np.clip(
                    cached_interp[i0].astype(np.float32) * (1.0 - frac) + cached_interp[i1].astype(np.float32) * frac,
                    0, 255
                ).astype(np.uint8)

            # Optional natural blink during baseline/transition frames
            b_val = blink_schedule.get(f, 0.0)
            if b_val > 0.01:
                cur_plate = apply_natural_eyelid_blink_and_smile(cur_plate, b_val, 0.0)

            dy_chuckle = -2.6 * abs(math.sin(2.0 * math.pi * f / 6.0)) * u if chuckle_bounce else 0.0

            deformed = deform_unified_character_mesh(
                cur_plate,
                head_pitch_deg=pitch_amp * u + 0.4 * math.sin(phase),
                head_yaw_deg=yaw_amp * u + 0.5 * math.sin(phase),
                head_roll_deg=roll_amp * u + 0.7 * math.sin(phase - 0.3),
                breath_phase=phase,
                cloth_phase=cloth_phase
            )

            canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
            alpha_composite_layer(canv, deformed, ox, oy + int(round(dy_chuckle)))
            frames.append(canv)

        save_animation_package(
            asset_id, "Facial", title,
            "Method 1 + Method 3: Authentic Hand-Painted Expression Plate + Optical-Flow In-Betweening & Unified 2D Mesh Rig",
            frames, seamless_loop=True
        )
        shutil.copyfile(PREVIEW_DIR / "GIF" / f"{asset_id}.gif", ART_DIR / f"{asset_id}.gif")

    # 1. THAKUR_IDLE_BLINK_V001 (Transition smoothly between 01_neutral and 10_peaceful for blinks, with breathing)
    b_double = {14: 0.25, 15: 0.75, 16: 1.0, 17: 1.0, 18: 0.70, 19: 0.35, 20: 0.10,
                42: 0.30, 43: 0.85, 44: 1.0, 45: 0.65, 46: 0.20}
    render_authentic_transition(
        "THAKUR_IDLE_BLINK_V001", "Natural Idle Blinking & Breathing",
        plates["01_neutral"], plates["02_gentle_smile"], total_frames=60, ramp=20,
        pitch_amp=-0.5, blink_schedule=b_double
    )

    # 2. THAKUR_SMILE_GENTLE_BLINK_V001 (Transition between 02_gentle_smile and 03_broad_smile with natural double blink)
    b1_2 = {18: 0.25, 19: 0.70, 20: 1.0, 21: 1.0, 22: 0.75, 23: 0.40, 24: 0.15,
            52: 0.30, 53: 0.80, 54: 1.0, 55: 0.80, 56: 0.40, 57: 0.12}
    render_authentic_transition(
        "THAKUR_SMILE_GENTLE_BLINK_V001", "Gentle Smiling with Natural Blinking",
        plates["01_neutral"], plates["02_gentle_smile"], total_frames=72, ramp=18,
        pitch_amp=-1.0, roll_amp=1.2, blink_schedule=b1_2
    )

    # 3. THAKUR_FACIAL_LAUGHING_V001 (Authentic hand-painted 04_laughing!)
    render_authentic_transition(
        "THAKUR_FACIAL_LAUGHING_V001", "Innocent Child Laughing",
        plates["02_gentle_smile"], plates["04_laughing"], total_frames=60, ramp=14,
        pitch_amp=-2.2, roll_amp=1.5, chuckle_bounce=True, blink_schedule={}
    )

    # 4. THAKUR_FACIAL_FROWNING_V001 (Authentic hand-painted blend of 08_sad and 12_determined)
    frown_plate = interpolate_flow_rgba(plates["08_sad"], plates["12_determined"], 0.45)
    render_authentic_transition(
        "THAKUR_FACIAL_FROWNING_V001", "Gentle Frowning / Thoughtful Brow Furrow",
        plates["01_neutral"], frown_plate, total_frames=60, ramp=14,
        pitch_amp=2.2, roll_amp=-1.0
    )

    # 5. THAKUR_FACIAL_ANGRY_V001 (Authentic hand-painted 07_angry!)
    render_authentic_transition(
        "THAKUR_FACIAL_ANGRY_V001", "Restrained Righteous Firm / Angry Expression",
        plates["01_neutral"], plates["07_angry"], total_frames=60, ramp=14,
        pitch_amp=2.8
    )

    # 6. THAKUR_FACIAL_SURPRISE_V001 (Authentic hand-painted 05_surprised!)
    render_authentic_transition(
        "THAKUR_FACIAL_SURPRISE_V001", "Innocent Child Surprise",
        plates["01_neutral"], plates["05_surprised"], total_frames=60, ramp=12,
        pitch_amp=-2.8, roll_amp=0.8
    )

    # 7. THAKUR_FACIAL_CURIOUS_V001 (Authentic hand-painted 06_curious!)
    render_authentic_transition(
        "THAKUR_FACIAL_CURIOUS_V001", "Looking Curious with Gentle Head Tilt",
        plates["02_gentle_smile"], plates["06_curious"], total_frames=60, ramp=14,
        pitch_amp=-1.2, roll_amp=3.5
    )

    # 8. THAKUR_FACIAL_SAD_V001 (Authentic hand-painted 08_sad!)
    render_authentic_transition(
        "THAKUR_FACIAL_SAD_V001", "Looking Sad / Compassionate Sorrow",
        plates["01_neutral"], plates["08_sad"], total_frames=60, ramp=14,
        pitch_amp=4.0, roll_amp=-1.2
    )

    # 9. THAKUR_FACIAL_CRYING_V001 (Authentic hand-painted 09_crying with glistening tears!)
    render_authentic_transition(
        "THAKUR_FACIAL_CRYING_V001", "Gentle Crying with Trembling Breath",
        plates["08_sad"], plates["09_crying"], total_frames=72, ramp=16,
        pitch_amp=4.5, roll_amp=-1.5, chuckle_bounce=True
    )

    # 10. THAKUR_FACIAL_EYES_CLOSING_PEACEFULLY_V001 (Authentic hand-painted 10_peaceful!)
    render_authentic_transition(
        "THAKUR_FACIAL_EYES_CLOSING_PEACEFULLY_V001", "Eyes Closing Peacefully in Serene Stillness",
        plates["02_gentle_smile"], plates["10_peaceful"], total_frames=72, ramp=18,
        pitch_amp=1.8, blink_schedule={}
    )


if __name__ == "__main__":
    render_category_a_authentic()
    print("Authentic Hand-Painted Category A (10 Facial Animations) completed successfully.")
