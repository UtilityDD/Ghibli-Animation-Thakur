# AGENT ROLES & RESPONSIBILITIES MANIFEST
## Project: Param Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)
### Architecture: Multi-Agent Production Pipeline (Phases 1–8)

This manifest governs how specialized agents (whether Antigravity subagents, Claude Code, Cursor, or autonomous scripts) divide responsibilities across Tier 1 (Intel i5-12400) and Tier 2 (RTX GPU) workstations.

---

### Agent 1 — Character Design Director
- **Authority**: Owns `00_Project_Documentation/Character_Bible.md` and `Master_Identity_Profile.json`.
- **Identity Invariant**: Enforces the 4.6-head standing ratio, 2.85-head Sukhasana ratio, left-side hair parting, Ghibli watercolor warmth, white *uttoriyo* drape, and uncropped 5-toed bare feet.
- **Rule**: Rejects any synthetic caricature, unnatural smirks, or asymmetric eye drift.

### Agent 2 — Gesture & Key-Pose Designer
- **Authority**: Owns 24 FPS timing curves, exposure charts (X-sheets), and motion formulas.
- **Timing Invariant**: 24 FPS standard; 2–4 frame anticipation before movement, 3-frame overlapping cloth follow-through on uttoriyo sleeves, and gentle sinusoidal breathing rhythm.

### Agent 3 — AI & Layer Asset Generator
- **Authority**: Owns `02_Character_Design/` and modular layers in `03_Character_Assets/Layers/`.
- **Registration Invariant**: Replaces heads using full-bust chin-registered plates (`build_authentic_expression_plates.py`). Never cuts rectangular face patches. Builds symmetrical full-bust plates (`registered_seated_look_left.png`) for lateral gazes.

### Agent 4 — Rigging Specialist
- **Authority**: Maintains `03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend` and `test_fix_single_animation.py` deformers.
- **Pivot Invariant**: Pivots cervical spine motion at `px = 321.5, py = 308.0` (suprasternal collar notch) with cubic Hermite falloff along `y = 246..312`.
- **Path Invariant**: Uses strictly relative texture paths (`//../Layers/...`) for seamless portability across Windows, Linux, and macOS.

### Agent 5 — Animation Specialist
- **Authority**: Executes 24 FPS animation rendering in `04_Gesture_Library/` and `05_Animation_Previews/`.
- **Delivery Invariant**: Every animation folder must contain:
  1. `frames/*.png` (24 FPS uncompressed 32-bit RGBA).
  2. `*.blend` (Blender project file).
  3. `*.json` (Metadata and timing documentation).
  4. Lossless previews in `05_Animation_Previews/` (`GIF/`, `MP4/`, `WebM/`).

### Agent 6 — Quality Controller (QC)
- **Authority**: Runs `validate_full_library.py` and produces contact sheets in `07_Production_Tests/`.
- **Rejection Criteria**: Rejects any asset with transparent boundary notches, double-feature ghosting, clipping at head/toes, or non-relative texture paths.

---

## CURRENT PIPELINE STATE & HANDOFF DIRECTIVE
- **Batch 1 (18 Animations: 10 Facial + 8 Head Movements)**: **COMPLETED, FULLY TESTED & APPROVED BY USER**.
- **Next Assignment**: **Batch 2 (Categories C & D)**:
  - Run `calibrate_registered_gestures.py` to prepare clean armless lap bases.
  - Render Category C (10 Hand Mudras).
  - Render Category D (10 Sitting & Devotional Gestures).
  - Generate Batch 2 verification contact board and update review documentation.
