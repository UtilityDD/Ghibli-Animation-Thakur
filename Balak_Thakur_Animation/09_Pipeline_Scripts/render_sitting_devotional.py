"""
Sitting and devotional clips on the full-body hand sheet.

Each clip is one continuous seated figure. The painted expression is
recolored to that figure's skin. Kneeling, sitting down, and standing up
stay on the standing turnaround and are not rebuilt here.
"""
import math

import numpy as np

from render_pilot_animations_1_to_3 import (
    BASE_DIR, ease_in_out_cubic, alpha_composite_layer,
)
from render_pilot_animations_3_to_5 import interpolate_flow_rgba
from expand_gesture_library_part1_AB import save_animation_package
from test_fix_single_animation import (
    apply_natural_eyelid_blink_and_smile, deform_unified_character_mesh,
)
from render_emotional_category_f import (
    EXPRESSIONS, load_expression, load_gesture, plate_for, stamp_one_face, snap_disputed_parts,
)


CLIPS = [
    {
        "asset_id": "THAKUR_SITTING_CROSS_LEGGED_V001",
        "category": "Sitting",
        "title": "Sitting Cross-Legged (Sukhasana Idle)",
        "start_face": "02_gentle_smile",
        "end_face": "02_gentle_smile",
        "start_gesture": "08_resting_hands",
        "end_gesture": "08_resting_hands",
        "total": 72,
        "still": True,
        "pitch": 0.45,
        "yaw": 0.0,
        "roll": 0.4,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_SITTING_NATURALLY_V001",
        "category": "Sitting",
        "title": "Sitting Naturally with Folded Hands",
        "start_face": "02_gentle_smile",
        "end_face": "02_gentle_smile",
        "start_gesture": "08_resting_hands",
        "end_gesture": "02_folded_hands",
        "total": 72,
        "pitch": 0.6,
        "yaw": 0.4,
        "roll": 0.5,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_SITTING_AND_SMILING_V001",
        "category": "Sitting",
        "title": "Sitting Cross-Legged and Smiling Warmly",
        "start_face": "02_gentle_smile",
        "end_face": "03_broad_smile",
        "start_gesture": "08_resting_hands",
        "end_gesture": "08_resting_hands",
        "total": 60,
        "pitch": -1.0,
        "yaw": 0.4,
        "roll": 0.7,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_SITTING_AND_LAUGHING_V001",
        "category": "Sitting",
        "title": "Sitting Cross-Legged and Laughing Joyfully",
        "start_face": "03_broad_smile",
        "end_face": "04_laughing",
        "start_gesture": "08_resting_hands",
        "end_gesture": "08_resting_hands",
        "total": 60,
        "pitch": -0.6,
        "yaw": 0.3,
        "roll": 0.5,
        "blink": False,
        "chuckle": True,
    },
    {
        "asset_id": "THAKUR_SITTING_LISTENING_ATTENTIVELY_V001",
        "category": "Sitting",
        "title": "Sitting and Listening Attentively",
        "start_face": "02_gentle_smile",
        "end_face": "06_curious",
        "start_gesture": "02_folded_hands",
        "end_gesture": "02_folded_hands",
        "total": 60,
        "pitch": -0.8,
        "yaw": 1.4,
        "roll": 2.4,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_SITTING_LOOKING_THOUGHTFULLY_V001",
        "category": "Sitting",
        "title": "Sitting and Looking Thoughtfully",
        "start_face": "02_gentle_smile",
        "end_face": "11_thoughtful",
        "start_gesture": "02_folded_hands",
        "end_gesture": "02_folded_hands",
        "total": 60,
        "pitch": -1.0,
        "yaw": 2.2,
        "roll": -1.2,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_SITTING_CHANGING_POSITION_V001",
        "category": "Sitting",
        "title": "Changing Sitting Posture and Shifting Weight",
        "start_face": "02_gentle_smile",
        "end_face": "02_gentle_smile",
        "start_gesture": "08_resting_hands",
        "end_gesture": "02_folded_hands",
        "total": 72,
        "pitch": 0.8,
        "yaw": 0.6,
        "roll": 1.2,
        "blink": True,
    },
    {
        "asset_id": "THAKUR_PRAYER_SITTING_V001",
        "category": "Sitting",
        "title": "Sitting Cross-Legged and Praying",
        "start_face": "02_gentle_smile",
        "end_face": "10_peaceful",
        "start_gesture": "08_resting_hands",
        "end_gesture": "01_namaskar",
        "total": 96,
        "ramp": 22,
        "pitch": 3.2,
        "yaw": 0.0,
        "roll": 0.0,
        "blink": False,
    },
    {
        "asset_id": "THAKUR_DEVOTIONAL_MEDITATING_V001",
        "category": "Devotional",
        "title": "Deep Serene Meditation in Sukhasana",
        "start_face": "02_gentle_smile",
        "end_face": "10_peaceful",
        "start_gesture": "08_resting_hands",
        "end_gesture": "08_resting_hands",
        "total": 72,
        "pitch": 1.4,
        "yaw": 0.0,
        "roll": 0.3,
        "blink": False,
    },
    {
        "asset_id": "THAKUR_DEVOTIONAL_BOWING_V001",
        "category": "Devotional",
        "title": "Reverent Devotional Bowing",
        "start_face": "02_gentle_smile",
        "end_face": "10_peaceful",
        "start_gesture": "08_resting_hands",
        "end_gesture": "01_namaskar",
        "total": 72,
        "pitch": 5.0,
        "yaw": 0.0,
        "roll": 0.0,
        "blink": False,
    },
]


def env_hold(f, total, ramp):
    if f < ramp:
        return ease_in_out_cubic(f / float(ramp))
    if f < total - ramp:
        return 1.0
    return 1.0 - ease_in_out_cubic((f - (total - ramp)) / float(ramp))


def render_sitting_devotional(plates_only=False, only=None):
    expressions = {name: load_expression(name) for name in EXPRESSIONS}
    gestures = {
        name: load_gesture(name)
        for name in ("08_resting_hands", "02_folded_hands", "01_namaskar")
    }
    nh, nw, _ = gestures["08_resting_hands"].shape
    ox = (768 - nw) // 2
    oy = (768 - nh) // 2 + 10

    built = []
    for clip in CLIPS:
        start = plate_for(expressions, gestures, clip["start_face"], clip["start_gesture"])
        active = plate_for(expressions, gestures, clip["end_face"], clip["end_gesture"])
        built.append((clip, start, active))

    from PIL import Image
    pairs = []
    for clip, start, active in built:
        short = clip["asset_id"].replace("THAKUR_", "").replace("_V001", "")
        pairs.append((short, active))
    thumb_w, thumb_h = 200, 214
    cols = 5
    rows = 2
    board = Image.new("RGB", (cols * thumb_w + 16, rows * thumb_h + 16), (28, 24, 22))
    for i, (label, plate) in enumerate(pairs):
        r, c = divmod(i, cols)
        im = Image.fromarray(plate, mode="RGBA")
        im.thumbnail((thumb_w - 8, thumb_h - 8), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", im.size, (236, 230, 218, 255))
        bg.alpha_composite(im)
        board.paste(bg.convert("RGB"), (8 + c * thumb_w, 8 + r * thumb_h))
    board_path = BASE_DIR / "07_Production_Tests" / "Sitting_Devotional_Plate_Check.png"
    board.save(board_path)
    print(f"Plate check written to {board_path}")
    if plates_only:
        return

    early_blink = {4: 0.25, 5: 0.75, 6: 1.0, 7: 0.55, 8: 0.15}
    flow_steps = 24
    for clip, start, active in built:
        if only and clip["asset_id"] != only:
            continue
        print(f"Rendering {clip['asset_id']}")
        total = clip["total"] + 24
        ramp = max(24, clip.get("ramp", 16))
        cached = [
            interpolate_flow_rgba(start, active, i / float(flow_steps))
            for i in range(flow_steps + 1)
        ]
        frames = []
        for f in range(total):
            phase = 2.0 * math.pi * f / float(total)
            cloth_phase = 2.0 * math.pi * ((f - 3.5) / float(total))
            u = 0.0 if clip.get("still") else env_hold(f, total, ramp)
            f_idx = u * flow_steps
            i0 = int(math.floor(f_idx))
            i1 = min(flow_steps, i0 + 1)
            frac = f_idx - i0
            if frac <= 0.001 or i0 == i1:
                cur = cached[i0].copy()
            else:
                cur = np.clip(
                    cached[i0].astype(np.float32) * (1.0 - frac)
                    + cached[i1].astype(np.float32) * frac,
                    0, 255,
                ).astype(np.uint8)
            if not clip.get("still"):
                cur = snap_disputed_parts(start, active, cur, u)
                cur = stamp_one_face(cur, active if u >= 0.5 else start)
            if clip["blink"]:
                b_val = early_blink.get(f, 0.0)
                if b_val > 0.01 and u < 0.45:
                    cur = apply_natural_eyelid_blink_and_smile(cur, b_val, 0.0)
            breathe = 1.0 if clip.get("still") else u
            deformed = deform_unified_character_mesh(
                cur,
                head_pitch_deg=clip["pitch"] * breathe * (math.sin(phase) if clip.get("still") else 1.0),
                head_yaw_deg=clip["yaw"] * u,
                head_roll_deg=clip["roll"] * (math.sin(phase) if clip.get("still") else u),
                breath_phase=phase,
                cloth_phase=cloth_phase,
            )
            chuckle = 0
            if clip.get("chuckle"):
                chuckle = int(round(-2.2 * abs(math.sin(2.0 * math.pi * f / 8.0)) * u))
            canv = np.zeros((768, 768, 4), dtype=np.uint8)
            alpha_composite_layer(canv, deformed, ox, oy + chuckle)
            frames.append(canv)
        save_animation_package(
            clip["asset_id"], clip["category"], clip["title"],
            "Method 1: Full-body hand sheet with the painted expression on one face oval",
            frames, seamless_loop=True,
        )
        print(f"Finished {clip['asset_id']}")


if __name__ == "__main__":
    import sys
    chosen = None
    if "--only" in sys.argv:
        chosen = sys.argv[sys.argv.index("--only") + 1]
    render_sitting_devotional(plates_only="--plates" in sys.argv, only=chosen)
