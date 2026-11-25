"""
Full Gesture Library Expansion Engine — Part 2:
Produces Category C (Hand and Upper-Body Gestures — 10 items) & Category D (Sitting and Devotional Gestures — 10 items) at 24 FPS.
Uses the locked Master Identity Profile, the Seated Sukhasana Master Rig Layers, the 8 Approved Hand Gesture Layers (`gesture_torso_01..08.png`),
and the 12 Approved Facial Expression Layers (`head_exp_01..12.png`).
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
from expand_gesture_library_part1_AB import (
    load_expression_head_matched, save_animation_package
)


def build_matched_gesture_body(gesture_layer_name: str, body_base: np.ndarray, nw: int, nh: int):
    """
    Loads one of the 8 approved hand/arm gesture torso layers (`gesture_torso_01..08.png`),
    aligns its shoulders and collar seamlessly over `body_base` (preserving the Sukhasana crossed legs and bare right foot),
    and returns a clean (nh x nw x 4) RGBA body state for articulated transition and arm/hand motion!
    """
    g_raw = np.array(Image.open(LAYERS_DIR / f"gesture_torso_{gesture_layer_name}.png").convert("RGBA"))
    gw, gh = 456, 396
    g_hi = np.array(Image.fromarray(g_raw).resize((gw, gh), Image.Resampling.LANCZOS))

    mh, mw, _ = g_hi.shape
    gy, gx = np.indices((mh, mw), dtype=np.float32)
    top_fade = np.clip((gy - 42.0) / 16.0, 0.0, 1.0)
    bot_fade = np.clip((mh - 16.0 - gy) / 40.0, 0.0, 1.0)
    g_hi[:, :, 3] = (g_hi[:, :, 3].astype(np.float32) * top_fade * bot_fade).astype(np.uint8)

    g_full = np.zeros((nh, nw, 4), dtype=np.uint8)
    alpha_composite_layer(g_full, g_hi, 100, 194)

    state = body_base.copy()
    # Clear old resting outer sleeves in torso zone y=195..465 so only the active gesture arms appear
    torso_clear = np.ones((nh, nw), dtype=np.float32)
    torso_clear[195:465, :] = 0.0
    torso_clear = cv2.GaussianBlur(torso_clear, (21, 21), 6.0)
    state[:, :, 3] = (state[:, :, 3].astype(np.float32) * torso_clear).astype(np.uint8)

    # Also cover old resting hands on the lap (x=245..412, y=485..575) with clean white dhoti lap cloth
    lap_patch = state[485:578, 245:412].copy()
    lh, lw, _ = lap_patch.shape
    lgy, lgx = np.indices((lh, lw), dtype=np.float32)
    hand_lap_mask = np.clip(1.0 - np.sqrt(((lgx - lw * 0.5) / (lw * 0.44))**2 + ((lgy - lh * 0.35) / (lh * 0.38))**2), 0.0, 1.0)
    hand_lap_mask = cv2.GaussianBlur(hand_lap_mask, (15, 15), 5.0)[:, :, None]
    clean_cloth = np.zeros((lh, lw, 3), dtype=np.float32)
    clean_cloth[:, :] = np.array([242, 231, 213], dtype=np.float32)
    lap_patch[:, :, :3] = (lap_patch[:, :, :3].astype(np.float32) * (1.0 - hand_lap_mask * 0.90) + clean_cloth * (hand_lap_mask * 0.90)).astype(np.uint8)
    state[485:578, 245:412] = lap_patch

    alpha_composite_layer(state, g_full, 0, 0)
    return state


def render_hand_or_sitting_gesture(
    asset_id: str, category: str, title: str,
    body_base: np.ndarray, active_body: np.ndarray,
    head_start: np.ndarray, head_active: np.ndarray,
    apply_eyelid_and_smile, nw: int, nh: int,
    total_frames: int = 60,
    arm_osc_x: float = 0.0, arm_osc_y: float = 0.0, arm_osc_hz: float = 2.0,
    head_pitch_active: float = 0.0, head_roll_active: float = 0.0,
    eye_close_active: float = 0.0, start_already_in_pose: bool = False
):
    canvas_w, canvas_h = 768, 768
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 20
    frames = []
    b_map = {12: 0.3, 13: 0.85, 14: 1.0, 15: 0.65, 16: 0.2,
             46: 0.3, 47: 0.85, 48: 1.0, 49: 0.65, 50: 0.2}

    for f in range(total_frames):
        t = f / float(total_frames)
        phase = 2.0 * math.pi * t
        breath = math.sin(phase)
        cloth_breath = math.sin(phase - 0.4)

        if start_already_in_pose:
            u = 1.0
            active_wave = math.sin(phase * arm_osc_hz)
        else:
            if f < 14:
                u = ease_in_out_cubic(f / 14.0)
            elif f < total_frames - 14:
                u = 1.0
            else:
                u = 1.0 - ease_in_out_cubic((f - (total_frames - 14)) / 14.0)
            active_wave = math.sin(2.0 * math.pi * (f - 14) / 16.0) * u if (14 <= f < total_frames - 14) else 0.0

        # Warp base resting body and active gesture body
        rest_w = warp_layer_25d(
            body_base, (nw * 0.5, 430),
            angle_deg=0.3 * math.sin(phase),
            scale_x=1.0 + 0.008 * breath, scale_y=1.0 + 0.009 * breath,
            tx=0.0, ty=-14.0 * u - 1.2 * breath,
            cloth_sway_px=2.0 * cloth_breath
        )
        act_w = warp_layer_25d(
            active_body, (nw * 0.5, 430),
            angle_deg=0.3 * math.sin(phase) + 0.4 * active_wave,
            scale_x=1.0 + 0.008 * breath, scale_y=1.0 + 0.009 * breath,
            tx=arm_osc_x * active_wave,
            ty=26.0 * (1.0 - u) - 1.2 * breath + arm_osc_y * active_wave,
            cloth_sway_px=2.5 * cloth_breath + 0.6 * arm_osc_x * active_wave
        )

        if u <= 0.001:
            body_cur = rest_w
        elif u >= 0.999:
            body_cur = act_w
            body_cur[490:, :] = body_base[490:, :]
        else:
            body_cur = np.zeros_like(body_base)
            body_cur[490:, :] = body_base[490:, :]
            body_cur[:490, :] = np.clip(
                rest_w[:490, :].astype(np.float32) * (1.0 - u) + act_w[:490, :].astype(np.float32) * u,
                0, 255
            ).astype(np.uint8)

        blink_val = max(b_map.get(f, 0.0), eye_close_active * u)
        h_s = apply_eyelid_and_smile(head_start, blink_val, 0.25)
        h_a = apply_eyelid_and_smile(head_active, blink_val, 0.55)
        h_blend = np.clip(h_s.astype(np.float32) * (1.0 - u) + h_a.astype(np.float32) * u, 0, 255).astype(np.uint8)

        head_w = warp_layer_25d(
            h_blend, (nw * 0.5, 228),
            angle_deg=head_roll_active * u + 0.8 * math.sin(phase),
            scale_x=1.0, scale_y=1.0 - 0.008 * abs(head_pitch_active * u / 8.0),
            tx=0.25 * head_roll_active * u,
            ty=3.5 * (head_pitch_active * u / 6.0) - 1.5 * breath,
            tilt_pitch_deg=head_pitch_active * u
        )

        canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
        alpha_composite_layer(canv, body_cur, ox, oy)
        alpha_composite_layer(canv, head_w, ox, oy)
        frames.append(canv)

    save_animation_package(
        asset_id, category, title,
        "Method 1 + Method 3: Rigged 2D Layered Mesh + Articulated Hand/Torso Gesture & Cloth Overlap",
        frames, seamless_loop=True
    )


def build_category_c_and_d():
    fn, hb, bb, nw, nh = render_pilot_1_gentle_smile_blink()

    # Load matched expression heads
    h_smile = hb
    h_broad = load_expression_head_matched("03_broad_smile", hb, nw, nh)
    h_laugh = load_expression_head_matched("04_laughing", hb, nw, nh)
    h_surp = load_expression_head_matched("05_surprised", hb, nw, nh)
    h_curious = load_expression_head_matched("06_curious", hb, nw, nh)
    h_sad = load_expression_head_matched("08_sad", hb, nw, nh)
    h_peace = load_expression_head_matched("10_peaceful", hb, nw, nh)
    h_thought = load_expression_head_matched("11_thoughtful", hb, nw, nh)

    # Pre-build the 8 matched gesture bodies
    g_namaskar = build_matched_gesture_body("01_namaskar", bb, nw, nh)
    g_folded = build_matched_gesture_body("02_folded_hands", bb, nw, nh)
    g_blessing = build_matched_gesture_body("03_blessing", bb, nw, nh)
    g_pointing = build_matched_gesture_body("04_pointing", bb, nw, nh)
    g_waving = build_matched_gesture_body("05_waving", bb, nw, nh)
    g_open_palm = build_matched_gesture_body("06_open_palm", bb, nw, nh)
    g_holding = build_matched_gesture_body("07_holding_object", bb, nw, nh)
    g_resting = bb  # 08_resting_hands matches Master Seated Sukhasana directly

    # =========================================================================
    # CATEGORY C — Hand and upper-body gestures (10 items)
    # =========================================================================
    # 1. Namaskar
    render_hand_or_sitting_gesture("THAKUR_HANDS_NAMASKAR_V001", "Hands", "Traditional Namaskar Gesture",
                                   bb, g_namaskar, h_smile, h_smile, fn, nw, nh, total_frames=60, head_pitch_active=3.5)
    # 2. Folding hands
    render_hand_or_sitting_gesture("THAKUR_HANDS_FOLDING_V001", "Hands", "Folding Hands Gently Across Lap",
                                   bb, g_folded, h_smile, h_smile, fn, nw, nh, total_frames=60, head_pitch_active=1.5)
    # 3. Waving
    render_hand_or_sitting_gesture("THAKUR_HANDS_WAVING_V001", "Hands", "Friendly Child Waving Gesture",
                                   bb, g_waving, h_smile, h_broad, fn, nw, nh, total_frames=60,
                                   arm_osc_x=4.5, arm_osc_y=-2.0, head_roll_active=3.0)
    # 4. Pointing
    render_hand_or_sitting_gesture("THAKUR_HANDS_POINTING_V001", "Hands", "Pointing Gently Towards Nature",
                                   bb, g_pointing, h_smile, h_curious, fn, nw, nh, total_frames=60,
                                   arm_osc_x=2.5, arm_osc_y=-2.0, head_roll_active=3.5, head_pitch_active=-2.0)
    # 5. Explaining (Open palms moving gently as if explaining spiritual wisdom)
    render_hand_or_sitting_gesture("THAKUR_HANDS_EXPLAINING_V001", "Hands", "Explaining Gently with Open Palms",
                                   bb, g_open_palm, h_smile, h_thought, fn, nw, nh, total_frames=60,
                                   arm_osc_x=3.5, arm_osc_y=-3.0, head_roll_active=2.5)
    # 6. Raising a hand (Blessing / Abhaya raised right hand)
    render_hand_or_sitting_gesture("THAKUR_HANDS_RAISING_BLESSING_V001", "Hands", "Raising Right Hand in Serene Blessing",
                                   bb, g_blessing, h_smile, h_smile, fn, nw, nh, total_frames=60,
                                   arm_osc_y=-2.0, head_pitch_active=1.5)
    # 7. Resting hands
    render_hand_or_sitting_gesture("THAKUR_HANDS_RESTING_V001", "Hands", "Resting Hands Calmly on Lap",
                                   bb, g_resting, h_smile, h_smile, fn, nw, nh, total_frames=60,
                                   start_already_in_pose=True, arm_osc_y=-1.0)
    # 8. Expressing surprise (Open palms + surprised facial expression)
    render_hand_or_sitting_gesture("THAKUR_HANDS_EXPRESSING_SURPRISE_V001", "Hands", "Expressing Innocent Surprise with Hands",
                                   bb, g_open_palm, h_smile, h_surp, fn, nw, nh, total_frames=60,
                                   arm_osc_y=-3.5, head_pitch_active=-3.5)
    # 9. Pleading (Cupped/open hands offered forward with compassionate pleading expression)
    render_hand_or_sitting_gesture("THAKUR_HANDS_PLEADING_V001", "Hands", "Compassionate Child Pleading Gesture",
                                   bb, g_holding, h_smile, h_sad, fn, nw, nh, total_frames=60,
                                   arm_osc_y=-2.5, head_pitch_active=3.5, head_roll_active=-2.5)
    # 10. Greeting (Warm Namaskar bow with joyful greeting smile)
    render_hand_or_sitting_gesture("THAKUR_HANDS_GREETING_V001", "Hands", "Warm Bengali Namaskar Greeting",
                                   bb, g_namaskar, h_smile, h_broad, fn, nw, nh, total_frames=60,
                                   head_pitch_active=6.5)

    # =========================================================================
    # CATEGORY D — Sitting and devotional gestures (10 items)
    # (Note: Pilot 3 THAKUR_PRAYER_SITTING_V001 is #5 Praying)
    # =========================================================================
    # 1. Sitting cross-legged (Serene Sukhasana baseline matching Master Reference)
    render_hand_or_sitting_gesture("THAKUR_SITTING_CROSS_LEGGED_V001", "Sitting", "Sitting Cross-Legged (Sukhasana Idle)",
                                   bb, bb, h_smile, h_smile, fn, nw, nh, total_frames=72,
                                   start_already_in_pose=True, arm_osc_y=-1.2)
    # 2. Sitting naturally (Folded hands relaxed posture with gentle breathing)
    render_hand_or_sitting_gesture("THAKUR_SITTING_NATURALLY_V001", "Sitting", "Sitting Naturally with Folded Hands",
                                   bb, g_folded, h_smile, h_smile, fn, nw, nh, total_frames=72,
                                   start_already_in_pose=True, arm_osc_y=-1.2, head_roll_active=1.5)
    # 3. Sitting and smiling
    render_hand_or_sitting_gesture("THAKUR_SITTING_AND_SMILING_V001", "Sitting", "Sitting Cross-Legged and Smiling Warmly",
                                   bb, bb, h_smile, h_broad, fn, nw, nh, total_frames=60,
                                   start_already_in_pose=True, head_roll_active=2.0)
    # 4. Sitting and laughing
    render_hand_or_sitting_gesture("THAKUR_SITTING_AND_LAUGHING_V001", "Sitting", "Sitting Cross-Legged and Laughing Joyfully",
                                   bb, bb, h_smile, h_laugh, fn, nw, nh, total_frames=60,
                                   start_already_in_pose=True, arm_osc_y=-3.5, arm_osc_hz=4.0, head_pitch_active=-2.5)
    # 6. Meditating (Also registered in Devotional)
    render_hand_or_sitting_gesture("THAKUR_DEVOTIONAL_MEDITATING_V001", "Devotional", "Deep Serene Meditation in Sukhasana",
                                   bb, bb, h_peace, h_peace, fn, nw, nh, total_frames=72,
                                   start_already_in_pose=True, eye_close_active=1.0, head_pitch_active=2.0)
    # 7. Bowing (Devotional bow with Namaskar hands)
    render_hand_or_sitting_gesture("THAKUR_DEVOTIONAL_BOWING_V001", "Devotional", "Reverent Devotional Bowing",
                                   bb, g_namaskar, h_smile, h_peace, fn, nw, nh, total_frames=72,
                                   eye_close_active=0.9, head_pitch_active=12.5)
    # 8. Listening attentively
    render_hand_or_sitting_gesture("THAKUR_SITTING_LISTENING_ATTENTIVELY_V001", "Sitting", "Sitting and Listening Attentively",
                                   bb, g_folded, h_smile, h_curious, fn, nw, nh, total_frames=60,
                                   start_already_in_pose=True, head_roll_active=5.5, head_pitch_active=-1.5)
    # 9. Changing sitting position (Shifting weight gently from resting hands to folded hands with torso settle)
    render_hand_or_sitting_gesture("THAKUR_SITTING_CHANGING_POSITION_V001", "Sitting", "Changing Sitting Posture & Shifting Weight",
                                   bb, g_folded, h_smile, h_smile, fn, nw, nh, total_frames=72,
                                   arm_osc_x=3.0, arm_osc_y=-2.5, head_roll_active=3.0, head_pitch_active=2.5)
    # 10. Looking thoughtfully
    render_hand_or_sitting_gesture("THAKUR_SITTING_LOOKING_THOUGHTFULLY_V001", "Sitting", "Sitting and Looking Thoughtfully",
                                   bb, bb, h_smile, h_thought, fn, nw, nh, total_frames=60,
                                   start_already_in_pose=True, head_roll_active=-3.0, head_pitch_active=-3.0)


if __name__ == "__main__":
    build_category_c_and_d()
    print("Category C (Hands - 10 animations) and Category D (Sitting/Devotional - 10 animations) complete!")
