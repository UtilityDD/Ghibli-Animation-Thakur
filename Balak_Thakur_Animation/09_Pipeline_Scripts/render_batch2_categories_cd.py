"""
BATCH 2 RENDERER (Categories C & D — 20 Animations):
Produces:
- Category C (10 Hand and Upper-Body Gestures)
- Category D (10 Sitting and Devotional Gestures)
Using:
1. Zero-Double-Arm Inpainted Lap Base & Registered Gesture Plates (`registered_gesture_01..08.png`).
2. 100% Authentic Hand-Painted Expression Plates (`registered_seated_01..12.png`).
3. Continuous 2D Anatomical Cervical Mesh Deformer (`deform_unified_character_mesh`).
4. Full 24 FPS export: PNG sequence, .blend, .json metadata, MP4, GIF, WebM previews.
"""
import math
import shutil
from pathlib import Path
import numpy as np
import cv2
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
from calibrate_registered_gestures import (
    build_clean_armless_lap_base, build_registered_gesture_master_plate
)


def load_plate(pname: str) -> np.ndarray:
    path = LAYERS_DIR / f"{pname}.png"
    return np.array(Image.open(path).convert("RGBA"))


def render_batch_2():
    # Load Authentic Registered Plates
    p_resting = load_plate("registered_gesture_08_resting_hands")
    p_namaskar = load_plate("registered_gesture_01_namaskar")
    p_folded = load_plate("registered_gesture_02_folded_hands")
    p_blessing = load_plate("registered_gesture_03_blessing")
    p_pointing = load_plate("registered_gesture_04_pointing")
    p_waving = load_plate("registered_gesture_05_waving")
    p_open_palm = load_plate("registered_gesture_06_open_palm")
    p_holding = load_plate("registered_gesture_07_holding_object")

    # Load Authentic Hand-Painted Expression Plates
    p_neutral = load_plate("registered_seated_01_neutral")
    p_smile = load_plate("registered_seated_02_gentle_smile")
    p_broad = load_plate("registered_seated_03_broad_smile")
    p_laugh = load_plate("registered_seated_04_laughing")
    p_surp = load_plate("registered_seated_05_surprised")
    p_curious = load_plate("registered_seated_06_curious")
    p_sad = load_plate("registered_seated_08_sad")
    p_peace = load_plate("registered_seated_10_peaceful")
    p_thought = load_plate("registered_seated_11_thoughtful")

    nh, nw, _ = p_resting.shape
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 10
    b_single = {14: 0.25, 15: 0.80, 16: 1.0, 17: 0.80, 18: 0.35, 19: 0.10}

    def env_hold(f, tf=60, ramp=14):
        if f < ramp:
            return ease_in_out_cubic(f / float(ramp))
        elif f < tf - ramp:
            return 1.0
        else:
            return 1.0 - ease_in_out_cubic((f - (tf - ramp)) / float(ramp))

    def build_gesture_anim(
        asset_id: str,
        category: str,
        title: str,
        plate_start: np.ndarray,
        plate_active: np.ndarray,
        motion_fn,
        total_frames: int = 60,
        flow_steps: int = 10
    ):
        cached_interp = [
            interpolate_flow_rgba(plate_start, plate_active, i / float(flow_steps))
            for i in range(flow_steps + 1)
        ]

        frames = []
        for f in range(total_frames):
            t = f / float(total_frames)
            phase = 2.0 * math.pi * t
            cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total_frames))

            m_kw = motion_fn(f, total_frames, phase)
            u = max(0.0, min(1.0, m_kw.get("u", env_hold(f, total_frames, 14))))

            f_idx = u * flow_steps
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
            asset_id, category, title,
            "Method 1: Zero-Double-Arm Registered Gesture Plate + Unified Continuous 2D Rig",
            frames, seamless_loop=True
        )
        shutil.copyfile(PREVIEW_DIR / "GIF" / f"{asset_id}.gif", ART_DIR / f"{asset_id}.gif")
        print(f"[{category}] {asset_id} ({total_frames}f @ 24fps) completed.")

    # =========================================================================
    # CATEGORY C: Hand Gestures (10 Animations)
    # =========================================================================

    # 1. THAKUR_HANDS_NAMASKAR_V001
    build_gesture_anim(
        "THAKUR_HANDS_NAMASKAR_V001", "Hands", "Traditional Namaskar Anjali Mudra",
        p_resting, p_namaskar,
        lambda f, tf, ph: dict(u=env_hold(f, tf, 15), pitch=2.5 * env_hold(f, tf, 15), yaw=0.0, roll=0.0),
        total_frames=60
    )

    # 2. THAKUR_HANDS_FOLDING_V001
    build_gesture_anim(
        "THAKUR_HANDS_FOLDING_V001", "Hands", "Folding Hands Gently Across Lap",
        p_resting, p_folded,
        lambda f, tf, ph: dict(u=env_hold(f, tf, 14), pitch=1.5 * env_hold(f, tf, 14), yaw=0.0, roll=0.5 * math.sin(ph)),
        total_frames=60
    )

    # 3. THAKUR_HANDS_WAVING_V001
    build_gesture_anim(
        "THAKUR_HANDS_WAVING_V001", "Hands", "Friendly Child Waving Gesture",
        p_resting, p_waving,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 14),
            pitch=-1.0 * env_hold(f, tf, 14),
            yaw=2.0 * env_hold(f, tf, 14),
            roll=2.5 * env_hold(f, tf, 14) + 1.2 * math.sin(ph * 2.0) * env_hold(f, tf, 14)
        ),
        total_frames=60
    )

    # 4. THAKUR_HANDS_POINTING_V001
    build_gesture_anim(
        "THAKUR_HANDS_POINTING_V001", "Hands", "Pointing Gently Towards Nature with Wonder",
        p_resting, p_pointing,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 14),
            pitch=-1.5 * env_hold(f, tf, 14),
            yaw=3.0 * env_hold(f, tf, 14),
            roll=2.5 * env_hold(f, tf, 14)
        ),
        total_frames=60
    )

    # 5. THAKUR_HANDS_EXPLAINING_V001
    build_gesture_anim(
        "THAKUR_HANDS_EXPLAINING_V001", "Hands", "Explaining Gently with Open Palms",
        p_resting, p_open_palm,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 14),
            pitch=1.0 * math.sin(ph * 1.5) * env_hold(f, tf, 14),
            yaw=1.5 * math.sin(ph) * env_hold(f, tf, 14),
            roll=1.8 * env_hold(f, tf, 14)
        ),
        total_frames=60
    )

    # 6. THAKUR_HANDS_RAISING_BLESSING_V001
    build_gesture_anim(
        "THAKUR_HANDS_RAISING_BLESSING_V001", "Hands", "Raising Right Hand in Serene Abhaya Blessing",
        p_resting, p_blessing,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 15),
            pitch=1.2 * env_hold(f, tf, 15),
            yaw=0.0,
            roll=0.6 * math.sin(ph)
        ),
        total_frames=60
    )

    # 7. THAKUR_HANDS_RESTING_V001
    build_gesture_anim(
        "THAKUR_HANDS_RESTING_V001", "Hands", "Resting Hands Calmly on Lap",
        p_resting, p_resting,
        lambda f, tf, ph: dict(u=0.0, pitch=0.5 * math.sin(ph), yaw=0.0, roll=0.4 * math.sin(ph)),
        total_frames=60
    )

    # 8. THAKUR_HANDS_EXPRESSING_SURPRISE_V001
    build_gesture_anim(
        "THAKUR_HANDS_EXPRESSING_SURPRISE_V001", "Hands", "Expressing Innocent Surprise with Open Hands",
        p_resting, p_open_palm,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 12),
            pitch=-3.0 * env_hold(f, tf, 12),
            yaw=0.0,
            roll=0.8 * math.sin(ph)
        ),
        total_frames=60
    )

    # 9. THAKUR_HANDS_PLEADING_V001
    build_gesture_anim(
        "THAKUR_HANDS_PLEADING_V001", "Hands", "Compassionate Child Pleading Offering",
        p_resting, p_holding,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 14),
            pitch=2.5 * env_hold(f, tf, 14),
            yaw=0.0,
            roll=-1.8 * env_hold(f, tf, 14)
        ),
        total_frames=60
    )

    # 10. THAKUR_HANDS_GREETING_V001
    build_gesture_anim(
        "THAKUR_HANDS_GREETING_V001", "Hands", "Warm Bengali Namaskar Greeting with Joyful Bow",
        p_resting, p_namaskar,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 16),
            pitch=5.5 * env_hold(f, tf, 16),
            yaw=0.0,
            roll=0.0
        ),
        total_frames=60
    )

    # =========================================================================
    # CATEGORY D: Sitting & Devotional Gestures (10 Animations)
    # =========================================================================

    # 1. THAKUR_SITTING_CROSS_LEGGED_V001
    build_gesture_anim(
        "THAKUR_SITTING_CROSS_LEGGED_V001", "Sitting", "Sitting Cross-Legged (Sukhasana Idle Baseline)",
        p_resting, p_resting,
        lambda f, tf, ph: dict(u=0.0, pitch=0.4 * math.sin(ph), yaw=0.0, roll=0.5 * math.sin(ph)),
        total_frames=72
    )

    # 2. THAKUR_SITTING_NATURALLY_V001
    build_gesture_anim(
        "THAKUR_SITTING_NATURALLY_V001", "Sitting", "Sitting Naturally with Folded Hands Posture",
        p_resting, p_folded,
        lambda f, tf, ph: dict(
            u=1.0,
            pitch=0.6 * math.sin(ph),
            yaw=0.8 * math.sin(ph * 0.7),
            roll=1.2 * math.sin(ph)
        ),
        total_frames=72
    )

    # 3. THAKUR_SITTING_AND_SMILING_V001
    build_gesture_anim(
        "THAKUR_SITTING_AND_SMILING_V001", "Sitting", "Sitting Cross-Legged and Smiling Warmly",
        p_smile, p_broad,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 18),
            pitch=-1.0 * env_hold(f, tf, 18),
            yaw=1.5 * math.sin(ph),
            roll=1.8 * env_hold(f, tf, 18)
        ),
        total_frames=60
    )

    # 4. THAKUR_SITTING_AND_LAUGHING_V001
    build_gesture_anim(
        "THAKUR_SITTING_AND_LAUGHING_V001", "Sitting", "Sitting Cross-Legged and Laughing Joyfully",
        p_smile, p_laugh,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 14),
            pitch=-2.0 * env_hold(f, tf, 14) + 1.2 * math.sin(ph * 3.0) * env_hold(f, tf, 14),
            yaw=1.0 * math.sin(ph),
            roll=1.5 * math.sin(ph * 2.0) * env_hold(f, tf, 14)
        ),
        total_frames=60
    )

    # 5. THAKUR_PRAYER_SITTING_V001
    build_gesture_anim(
        "THAKUR_PRAYER_SITTING_V001", "Sitting", "Complete Seated Prayer Cycle (Pranam & Devotion)",
        p_resting, p_namaskar,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 20),
            pitch=4.5 * env_hold(f, tf, 20),
            yaw=0.0,
            roll=0.0
        ),
        total_frames=72
    )

    # 6. THAKUR_DEVOTIONAL_MEDITATING_V001
    build_gesture_anim(
        "THAKUR_DEVOTIONAL_MEDITATING_V001", "Devotional", "Deep Serene Meditation in Sukhasana",
        p_resting, p_peace,
        lambda f, tf, ph: dict(
            u=1.0,
            pitch=1.8,
            yaw=0.0,
            roll=0.3 * math.sin(ph)
        ),
        total_frames=72
    )

    # 7. THAKUR_DEVOTIONAL_BOWING_V001
    build_gesture_anim(
        "THAKUR_DEVOTIONAL_BOWING_V001", "Devotional", "Reverent Devotional Pranama Bowing",
        p_resting, p_namaskar,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 18),
            pitch=11.5 * env_hold(f, tf, 18),
            yaw=0.0,
            roll=0.0
        ),
        total_frames=72
    )

    # 8. THAKUR_SITTING_LISTENING_ATTENTIVELY_V001
    build_gesture_anim(
        "THAKUR_SITTING_LISTENING_ATTENTIVELY_V001", "Sitting", "Sitting and Listening Attentively with Head Tilt",
        p_folded, p_curious,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 16),
            pitch=-1.2 * env_hold(f, tf, 16),
            yaw=2.0 * env_hold(f, tf, 16),
            roll=4.5 * env_hold(f, tf, 16)
        ),
        total_frames=60
    )

    # 9. THAKUR_SITTING_CHANGING_POSITION_V001
    build_gesture_anim(
        "THAKUR_SITTING_CHANGING_POSITION_V001", "Sitting", "Changing Sitting Posture & Weight Shift",
        p_resting, p_folded,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 18),
            pitch=1.8 * math.sin(ph),
            yaw=2.5 * math.sin(ph),
            roll=2.5 * math.sin(ph)
        ),
        total_frames=72
    )

    # 10. THAKUR_SITTING_LOOKING_THOUGHTFULLY_V001
    build_gesture_anim(
        "THAKUR_SITTING_LOOKING_THOUGHTFULLY_V001", "Sitting", "Sitting and Looking Thoughtfully Across the Garden",
        p_folded, p_thought,
        lambda f, tf, ph: dict(
            u=env_hold(f, tf, 16),
            pitch=-1.5 * env_hold(f, tf, 16),
            yaw=4.5 * env_hold(f, tf, 16),
            roll=-2.2 * env_hold(f, tf, 16)
        ),
        total_frames=60
    )


if __name__ == "__main__":
    render_batch_2()
    print("Batch 2: Category C (10 Hand Gestures) & Category D (10 Sitting & Devotional Gestures) completed successfully!")
