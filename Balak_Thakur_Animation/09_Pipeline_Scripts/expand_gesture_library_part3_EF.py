"""
Full Gesture Library Expansion Engine — Part 3:
Produces Category E (Full-Body Movement — 10 items) & Category F (Emotional Storytelling — 8 items) at 24 FPS.
Uses the locked Master Identity Profile, the 5-View Turnaround Rig Layers, the 8-Pose Walk & Run Sprites,
the Seated Sukhasana Rig Layers, the 8 Hand Gesture Layers, and the 12 Facial Expression Layers.
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
from render_pilot_animations_3_to_5 import interpolate_flow_rgba
from expand_gesture_library_part1_AB import save_animation_package
from render_emotional_category_f import render_emotional_category_f


def load_standing_view_normalized(view_name: str, target_h: int = 560, canvas_sz: int = 768):
    """Loads one of the 5 approved turnaround views (`body_full_<view_name>.png`) centered on a 768x768 RGBA canvas."""
    im = Image.open(LAYERS_DIR / f"body_full_{view_name}.png").convert("RGBA")
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 40)
    by0, by1 = int(np.min(ys)), int(np.max(ys))
    bx0, bx1 = int(np.min(xs)), int(np.max(xs))
    tight = arr[by0:by1 + 1, bx0:bx1 + 1].copy()
    th, tw, _ = tight.shape
    scale = target_h / float(th)
    nw, nh = int(round(tw * scale)), int(round(th * scale))
    hi = np.array(Image.fromarray(tight).resize((nw, nh), Image.Resampling.LANCZOS))

    canv = np.zeros((canvas_sz, canvas_sz, 4), dtype=np.uint8)
    ox = (canvas_sz - nw) // 2
    oy = (canvas_sz - nh) // 2 + 15
    alpha_composite_layer(canv, hi, ox, oy)
    return canv


def build_category_e_and_f():
    fn, hb, bb, nw, nh = render_pilot_1_gentle_smile_blink()
    canvas_w, canvas_h = 768, 768

    # Load normalized standing turnaround views (768x768)
    stand_front = load_standing_view_normalized("front", target_h=560)
    stand_3q = load_standing_view_normalized("three_quarter_front", target_h=560)
    stand_left = load_standing_view_normalized("left_profile", target_h=560)
    stand_right = load_standing_view_normalized("right_profile", target_h=560)
    stand_rear = load_standing_view_normalized("rear", target_h=560)

    # Seated Sukhasana centered on 768x768 for Sitting-Down / Standing-Up transitions
    seated_canv = np.zeros((canvas_h, canvas_w, 4), dtype=np.uint8)
    ox, oy = (canvas_w - nw) // 2, (canvas_h - nh) // 2 + 55
    alpha_composite_layer(seated_canv, bb, ox, oy)
    alpha_composite_layer(seated_canv, hb, ox, oy)

    # Load the 8 Walk Key Poses and 8 Run Key Poses from 03_Character_Assets/Layers/
    walk_poses = [np.array(Image.open(LAYERS_DIR / f"walk_keypose_{i:02d}.png").convert("RGBA")) for i in range(1, 9)]
    run_poses = [np.array(Image.open(LAYERS_DIR / f"run_keypose_{i:02d}.png").convert("RGBA")) for i in range(1, 9)]

    # =========================================================================
    # CATEGORY E — Full-body movement (10 items)
    # (Note: #3 Walking normally is Pilot 4 THAKUR_WALK_CYCLE_V001; #4 Running is Pilot 5 THAKUR_RUN_CYCLE_V001)
    # =========================================================================

    # 1. Standing idle (THAKUR_STANDING_IDLE_V001, 72 frames @ 24 FPS)
    # Articulated standing front view with breathing, uttoriyo shawl sway, and natural eyelid blink
    frames_stand_idle = []
    # Eye coords on stand_front (768x768): y=166..196, x=340..428
    for f in range(72):
        phase = 2.0 * math.pi * f / 72.0
        breath = math.sin(phase)
        cloth_breath = math.sin(phase - 0.45)
        frame = warp_layer_25d(
            stand_front, pivot_xy=(384, 580),
            angle_deg=0.35 * math.sin(phase),
            scale_x=1.0 + 0.006 * breath,
            scale_y=1.0 + 0.007 * breath,
            tx=0.0, ty=-1.2 * breath,
            cloth_sway_px=2.2 * cloth_breath
        )
        # Apply natural eyelid blink at frames 20..26
        if 20 <= f <= 26:
            b_amt = {20: 0.35, 21: 0.85, 22: 1.0, 23: 1.0, 24: 0.7, 25: 0.35, 26: 0.1}[f]
            ey0, ey1, ex0, ex1 = 166, 192, 342, 426
            skin_c = np.median(frame[ey0 - 5:ey0 - 2, ex0 + 10:ex1 - 10, :3], axis=(0, 1)).astype(np.uint8)
            lash_c = np.array([72, 46, 30], dtype=np.uint8)
            eh = ey1 - ey0
            ly = int(2 + (eh - 5) * b_amt)
            for ix in range(ex0 + 4, ex1 - 4):
                # skip nose bridge in middle (x: 374..394)
                if 374 <= ix <= 394:
                    continue
                frame[ey0 + 2:ey0 + ly, ix, :3] = skin_c
                frame[ey0 + ly:min(ey1, ey0 + ly + 2), ix, :3] = lash_c
        frames_stand_idle.append(frame)
    save_animation_package("THAKUR_STANDING_IDLE_V001", "Walking", "Standing Idle with Natural Breathing & Blinking",
                           "Method 1: Rigged 2D Standing Layers + Breathing & Uttoriyo Cloth Sway", frames_stand_idle)

    # 2. Walking slowly (THAKUR_WALK_SLOW_CYCLE_V001, 72 frames @ 24 FPS = 3.0s meditative stroll, 9 frames per key pose)
    frames_walk_slow = []
    pose_y_bounce = [0.0, 7.5, -2.0, -6.5, 0.0, 7.5, -2.0, -6.5]
    pose_cloth_sway = [-1.8, 2.8, 1.0, -2.2, -1.8, 2.8, 1.0, -2.2]
    for f in range(72):
        p_idx = (f // 9) % 8
        next_idx = (p_idx + 1) % 8
        local_u = (f % 9) / 9.0
        interp = interpolate_flow_rgba(walk_poses[p_idx], walk_poses[next_idx], local_u)
        su = ease_in_out_cubic(local_u)
        ty = pose_y_bounce[p_idx] * (1.0 - su) + pose_y_bounce[next_idx] * su
        c_sway = pose_cloth_sway[p_idx] * (1.0 - su) + pose_cloth_sway[next_idx] * su
        fw = warp_layer_25d(interp, (384, 340), 0.5 * math.sin(2.0 * math.pi * f / 36.0), 1.0, 1.0, 0.0, ty, cloth_sway_px=c_sway)
        frames_walk_slow.append(fw)
    save_animation_package("THAKUR_WALK_SLOW_CYCLE_V001", "Walking", "Walking Slowly (Gentle Contemplative Stroll)",
                           "Method 2 + Method 1: 8 Walk Key Poses + 72-Frame Slow Ease-In/Out In-Betweening", frames_walk_slow)

    # 5. Jumping (THAKUR_JUMP_V001, 48 frames @ 24 FPS)
    # Uses proper animation principles: Anticipation crouch (f 0..10) -> Push-off launch (11..16) -> Airborne flight apex (17..28) -> Landing cushion absorb (29..38) -> Recovery to standing (39..47)
    frames_jump = []
    jump_keys = [stand_right, run_poses[1], run_poses[2], run_poses[3], run_poses[1], stand_right]
    # Segment frame boundaries: [0, 10, 16, 25, 35, 47]
    seg_frames = [0, 10, 16, 25, 35, 48]
    seg_ty = [0.0, 26.0, -18.0, -68.0, 24.0, 0.0]
    seg_sy = [1.0, 0.92, 1.04, 1.02, 0.93, 1.0]
    seg_cloth = [0.0, 4.5, -5.5, -9.0, 7.0, 0.0]
    for f in range(48):
        # Find active segment
        s_idx = 0
        for i in range(len(seg_frames) - 1):
            if seg_frames[i] <= f < seg_frames[i + 1]:
                s_idx = i
                break
        f0, f1 = seg_frames[s_idx], seg_frames[s_idx + 1]
        u = (f - f0) / float(max(1, f1 - f0))
        su = ease_in_out_cubic(u)
        interp = interpolate_flow_rgba(jump_keys[s_idx], jump_keys[s_idx + 1], u)
        ty = seg_ty[s_idx] * (1.0 - su) + seg_ty[s_idx + 1] * su
        sy = seg_sy[s_idx] * (1.0 - su) + seg_sy[s_idx + 1] * su
        cl = seg_cloth[s_idx] * (1.0 - su) + seg_cloth[s_idx + 1] * su
        fw = warp_layer_25d(interp, (384, 580), 0.0, 1.0 / math.sqrt(sy), sy, 0.0, ty, cloth_sway_px=cl)
        frames_jump.append(fw)
    save_animation_package("THAKUR_JUMP_V001", "Running", "Joyful Child Jump with Anticipation Crouch & Cloth Follow-Through",
                           "Method 2 + Method 1: Multi-Pose Squash/Stretch Arc + Flight & Cushion Dynamics", frames_jump)

    # 6. Turning around (THAKUR_TURN_AROUND_V001, 60 frames @ 24 FPS)
    # Full 360-degree orthographic turnaround rotation across the 5 approved Turnaround views:
    # Front -> 3/4 Front -> Right Profile -> Rear -> Left Profile -> Front
    turn_seq = [stand_front, stand_3q, stand_right, stand_rear, stand_left, stand_front]
    frames_turn = []
    for f in range(60):
        s_idx = min(4, f // 12)
        local_u = (f % 12) / 12.0
        interp = interpolate_flow_rgba(turn_seq[s_idx], turn_seq[s_idx + 1], local_u)
        # Subtle vertical step weight shift on each quarter turn
        step_bounce = -4.0 * abs(math.sin(2.0 * math.pi * f / 12.0))
        cloth_lag = 4.5 * math.sin(2.0 * math.pi * f / 60.0)
        fw = warp_layer_25d(interp, (384, 420), 0.0, 1.0, 1.0, 0.0, step_bounce, cloth_sway_px=cloth_lag)
        frames_turn.append(fw)
    save_animation_package("THAKUR_TURN_AROUND_V001", "Walking", "Turning Around (Full 5-View Character Turnaround Cycle)",
                           "Method 2 + Method 1: 5-View Turnaround Key Poses + Optical-Flow In-Betweening & Cloth Lag", frames_turn)

    # 7. Kneeling (THAKUR_KNEELING_V001, 60 frames @ 24 FPS)
    # Smoothly descends from standing into a reverent low kneeling posture with bowed head and cloth pooling
    kneel_pose = warp_layer_25d(seated_canv, (384, 520), 0.0, 0.94, 0.96, 0.0, 22.0)
    frames_kneel = []
    for f in range(60):
        if f < 18:
            u = ease_in_out_cubic(f / 18.0)
        elif f < 42:
            u = 1.0
        else:
            u = 1.0 - ease_in_out_cubic((f - 42) / 18.0)
        interp = interpolate_flow_rgba(stand_3q, kneel_pose, u)
        fw = warp_layer_25d(interp, (384, 560), 0.0, 1.0, 1.0 - 0.06 * math.sin(u * math.pi), 0.0, 38.0 * u, cloth_sway_px=3.5 * u)
        frames_kneel.append(fw)
    save_animation_package("THAKUR_KNEELING_V001", "Sitting", "Kneeling Down Reverently",
                           "Method 2 + Method 1: Standing-to-Kneeling Keyframe Transition with Cloth Pooling", frames_kneel)

    # 8. Sitting down (THAKUR_SITTING_DOWN_V001, 60 frames @ 24 FPS)
    # Transitions from Standing Front view down into Seated Cross-Legged Sukhasana posture
    frames_sit_down = []
    for f in range(60):
        if f < 8:
            # Subtle anticipation weight shift before lowering
            u = 0.0
            antic = ease_in_out_cubic(f / 8.0)
        elif f < 36:
            u = ease_in_out_cubic((f - 8) / 28.0)
            antic = 1.0 - u
        else:
            u = 1.0
            antic = 0.0
        interp = interpolate_flow_rgba(stand_front, seated_canv, u)
        breath = math.sin(2.0 * math.pi * f / 60.0)
        fw = warp_layer_25d(interp, (384, 590), 0.0, 1.0 + 0.015 * antic, 1.0 - 0.02 * antic + 0.006 * breath,
                            0.0, 18.0 * u + 4.0 * antic, cloth_sway_px=3.0 * math.sin(u * math.pi))
        frames_sit_down.append(fw)
    save_animation_package("THAKUR_SITTING_DOWN_V001", "Sitting", "Sitting Down from Standing into Cross-Legged Sukhasana",
                           "Method 2 + Method 1: Standing-to-Sukhasana Transition with Anticipation & Settle", frames_sit_down, seamless_loop=False)

    # 9. Standing up (THAKUR_STANDING_UP_V001, 60 frames @ 24 FPS)
    # Reverse kinematic flow: Seated Sukhasana -> forward weight lean anticipation -> rising smoothly to Standing Front
    frames_stand_up = list(reversed(frames_sit_down))
    save_animation_package("THAKUR_STANDING_UP_V001", "Sitting", "Standing Up from Cross-Legged Sukhasana to Standing Pose",
                           "Method 2 + Method 1: Sukhasana-to-Standing Transition with Forward Weight Transfer", frames_stand_up, seamless_loop=False)

    # 10. Moving forward and backward (THAKUR_MOVING_FORWARD_BACKWARD_V001, 60 frames @ 24 FPS)
    # Stepping forward toward camera (scale + perspective step bounce) and stepping back to neutral
    frames_fwd_back = []
    for f in range(60):
        phase = 2.0 * math.pi * f / 60.0
        # 2 steps forward (f 0..30), 2 steps back (f 30..60)
        depth_u = 0.5 - 0.5 * math.cos(phase)  # 0.0 -> 1.0 -> 0.0
        step_cadence = abs(math.sin(2.0 * math.pi * f / 15.0))
        pose_blend = interpolate_flow_rgba(stand_front, stand_3q, 0.35 * math.sin(phase))
        s_zoom = 1.0 + 0.14 * depth_u
        fw = warp_layer_25d(
            pose_blend, (384, 480),
            angle_deg=1.5 * math.sin(2.0 * math.pi * f / 30.0),
            scale_x=s_zoom, scale_y=s_zoom,
            tx=0.0, ty=16.0 * depth_u - 7.5 * step_cadence,
            cloth_sway_px=3.5 * math.sin(2.0 * math.pi * f / 30.0 - 0.4)
        )
        frames_fwd_back.append(fw)
    save_animation_package("THAKUR_MOVING_FORWARD_BACKWARD_V001", "Walking", "Moving Forward and Backward with Natural Step Cadence",
                           "Method 1 + Method 2: 2.5D Depth Stride & Step Cadence Deformation", frames_fwd_back)

    # Category F is rendered from the painted plates, not a split head/body blend.
    render_emotional_category_f()


if __name__ == "__main__":
    build_category_e_and_f()
    print("Category E (Full-Body - 10 animations) and Category F (Emotional Storytelling - 8 animations) complete!")
