# 🤖 AGENT WORKFLOW & HANDOFF GUIDE (AGENTS.md)
## Project: Param Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)
### High-Fidelity 2D Cutout & Hand-Painted Animation Library (Childhood Age 6, Ujanchar)

> [!IMPORTANT]
> **READ THIS FIRST BEFORE TAKING ANY ACTION IN THIS WORKSPACE.**
> This repository is a multi-agent, multi-workstation production environment. Follow these standards strictly to prevent asset corruption, visual regressions, or broken cross-platform paths.

---

## 🎯 1. Master Character Identity & Non-Negotiables

* **Character**: Param Bismoy Balak Thakur as a 6-year-old child in Ujanchar.
* **Visual Style**: Studio Ghibli hand-painted aesthetic — warm, luminous, innocent, divine, nostalgic.
* **Proportion Formula**:
  * Standing: **4.6 Heads** tall (`THAKUR_BODY_PROPORTION_SHEET_V001.png`).
  * Seated (Sukhasana): **2.85 Heads** tall (`body_seated_sukhasana.png`).
* **Attire**:
  * Pristine white cotton *uttoriyo* (chadar) draped naturally across both shoulders.
  * Knee-to-mid-calf white *dhoti*.
  * Bare feet with soft rosy soles (5 clear toes per foot, uncropped).
* **Hair**: Soft parted black hair with side sweep (parted on Thakur's left / viewer's right).

---

## 🚦 2. Current Production Status (Where We Are Right Now)

| Phase | Milestone | Status | Deliverables / Notes |
| :--- | :--- | :---: | :--- |
| **Phase 1** | System & Toolchain Architecture | ✅ **DONE** | Documentation in `00_Project_Documentation/`. |
| **Phase 2** | Character Bible & Model Sheets | ✅ **DONE** | Turnaround, Expressions, Gestures, Proportions in `02_Character_Design/`. |
| **Phase 3** | Modular Layers & Master 2D Rig | ✅ **DONE** | Master rig (`THAKUR_CHILD_MASTER_RIG_V001.blend`) & 60+ RGBA layers. |
| **Phase 4** | Pilot Benchmark Animations | ✅ **DONE** | 5 foundational animations validated. |
| **Phase 5** | **Batch 1 (Categories A & B)** | ✅ **APPROVED** | **18 Animations Verified & Approved by User**: 10 Facial + 8 Head Movements with seamless neck alignment and authentic hand-painted plates. |
| **Phase 6** | **Batch 2 (Categories C & D)** | 🟡 **NEXT TASK** | **10 Hand Gestures** (Category C) + **10 Sitting & Devotional Gestures** (Category D). |
| **Phase 7** | **Batch 3 (Categories E & F)** | ⏳ **PENDING** | Full-Body Locomotion (Walk/Run cycles) + Emotional Storytelling. |
| **Phase 8** | ComfyUI AI Upscaling & 4K Masters | ⏳ **OPTIONAL** | Tier 2 GPU neural upscaling workflows in `09_Pipeline_Scripts/comfyui_workflows/`. |

---

## 🚫 3. Critical Technical Invariants (THE "NEVER DO" LIST)

1. **NEVER use procedural iris stretching or rectangular eye patches**:
   * All facial animations MUST use the 100% authentic hand-painted heads from `THAKUR_EXPRESSION_SHEET_12_V001.png` registered into `registered_seated_*.png`.
   * For lateral gazes (e.g. looking left), NEVER cut a rectangular patch. Use the full-bust mirrored plate (`registered_seated_look_left.png`).
2. **NEVER pivot the head at the chin tip (`py = 251.0`)**:
   * The cervical spine pivot is ALWAYS anchored at the suprasternal collar notch: `px = 321.5, py = 308.0`.
   * The cervical weight transitions continuously along `y = 246..312` with cubic Hermite falloff so the neck column bends organically without kinks.
3. **NEVER use absolute file paths in Blender or configurations**:
   * All textures inside `.blend` files MUST be linked via relative paths: `//../Layers/<texture_name>.png`.
   * This guarantees cross-machine compatibility between Windows, Linux, and macOS.
4. **NEVER commit OS artifacts or temporary files**:
   * `.gitignore` covers `Thumbs.db`, `.DS_Store`, `__pycache__`, `*.blend1`, `*.tmp`. Keep the git status clean before committing.
5. **ALWAYS export complete 4-format deliverables**:
   * Each animation in `04_Gesture_Library/` MUST include:
     1. `frames/*.png` (24 FPS uncompressed 32-bit transparent RGBA).
     2. `*.blend` (Blender project file).
     3. `*.json` (Timing and motion metadata).
     4. Previews in `05_Animation_Previews/` (`GIF/`, `MP4/`, `WebM/`).

---

## 🛠 4. Core Pipeline Tooling & Commands

All scripts reside in `Balak_Thakur_Animation/09_Pipeline_Scripts/` and run using standard Python 3.10+:

```bash
# Required Python environment:
pip install pillow numpy opencv-python scipy

# 1. Rebuild chin-registered authentic expression plates:
python Balak_Thakur_Animation/09_Pipeline_Scripts/build_authentic_expression_plates.py

# 2. Render Batch 1 Category A (10 Facial Animations):
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_batch1_category_a.py

# 3. Render Batch 1 Category B (8 Head Movements):
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_batch1_category_b.py

# 4. Calibrate gesture arm layers for Batch 2:
python Balak_Thakur_Animation/09_Pipeline_Scripts/calibrate_registered_gestures.py

# 5. Run automated 8-point QC validation across the entire library:
python Balak_Thakur_Animation/09_Pipeline_Scripts/validate_full_library.py
```

---

## 📋 5. Next Agent Assignment: Batch 2 Rollout (Categories C & D)

When resuming or continuing the project, the next task is **Batch 2**:
* **Category C (10 Hand Gestures)**:
  `THAKUR_HAND_PRANAM_V001`, `THAKUR_HAND_BLESSING_V001`, `THAKUR_HAND_OPEN_PALMS_V001`, `THAKUR_HAND_POINTING_V001`, `THAKUR_HAND_WAVING_V001`, `THAKUR_HAND_HOLDING_FLOWER_V001`, `THAKUR_HAND_RESTING_ON_KNEES_V001`, `THAKUR_HAND_TOUCHING_CHEST_V001`, `THAKUR_HAND_EXTENDING_FORWARD_V001`, `THAKUR_HAND_FOLDED_LAP_V001`.
* **Category D (10 Sitting & Devotional Gestures)**:
  `THAKUR_SITTING_CROSS_LEGGED_V001`, `THAKUR_SITTING_NATURALLY_V001`, `THAKUR_SITTING_CHANGING_POSITION_V001`, `THAKUR_SITTING_LOOKING_THOUGHTFULLY_V001`, `THAKUR_SITTING_AND_SMILING_V001`, `THAKUR_SITTING_AND_LAUGHING_V001`, `THAKUR_SITTING_LISTENING_ATTENTIVELY_V001`, `THAKUR_DEVOTIONAL_MEDITATING_V001`, `THAKUR_DEVOTIONAL_BOWING_V001`, `THAKUR_PRAYER_SITTING_V001`.

Use `Balak_Thakur_Animation/09_Pipeline_Scripts/calibrate_registered_gestures.py` which builds the clean armless lap base (`build_clean_armless_lap_base`) to avoid ghost limbs when compositing active gesture arms over the resting dhoti!
