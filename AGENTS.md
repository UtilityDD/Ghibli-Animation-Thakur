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
| **Phase 6** | **Batch 2 (Categories C & D)** | ✅ **APPROVED** | **20 Animations Verified**: 10 Hand Gestures (Category C) + 10 Sitting & Devotional Gestures (Category D) with zero-double-arm inpainting. |
| **Phase 7** | **Batch 3 (Categories E & F)** | ✅ **APPROVED** | **18 Animations Verified**: Full-Body Locomotion (Cat E: 5 Walk + 2 Run) + Emotional Storytelling (Cat F: 8 Gestures) + Kneeling/Sit/Stand. |
| **Phase 8** | **Complete 56-Animation Master Library** | ✅ **100% COMPLETE** | **All 56 Animations Passed 8-Point QC**: 24 FPS RGBA frames, .blend, .json, GIF/MP4/WebM previews, and HTML galleries. |
| **Phase 9** | **Season 1 Episode 1 Pre-Production** | 🟡 **NEXT TASK** | Secondary Character Model Sheets (Mata Charushila Devi, Sanatan Master) + Kazuo Oga Ghibli Backgrounds (BG01, BG02). |
| **Phase 10** | ComfyUI AI Upscaling & 4K Masters | ⏳ **OPTIONAL** | Tier 2 GPU neural upscaling workflows in `09_Pipeline_Scripts/comfyui_workflows/`. |

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

# 4. Calibrate gesture arm layers & render Batch 2 (Categories C & D):
python Balak_Thakur_Animation/09_Pipeline_Scripts/calibrate_registered_gestures.py
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_batch2_categories_cd.py

# 5. Render Batch 3 (Categories E & F - Locomotion & Emotional):
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_locomotion.py
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_emotional_category_f.py

# 6. Run automated 8-point QC validation across the entire 56-animation library:
python Balak_Thakur_Animation/09_Pipeline_Scripts/validate_full_library.py
```

---

## 📋 5. Next Agent Assignment: Season 1 Episode 1 Asset Pre-Production

The full 56-animation character gesture library for Param Bismoy Balak Thakur is **100% COMPLETE and APPROVED**.
When resuming or continuing the project on another machine, the next production task is **Season 1 Episode 1 Asset Pre-Production**:
* **Secondary Character Model Sheets**:
  1. **Mata Charushila Devi** (Thakur's mother, Age ~28):
     - Height: 6.2 Heads tall.
     - Attire: Traditional Bengali white taant sari with narrow red border (laal-paar taant), modest ghomta (veil) draped over head, soft loving maternal eyes.
     - Deliverable: Turnaround sheet (5 views) + Expression sheet (12 expressions) in `02_Character_Design/Secondary_Characters/Charushila_Devi/`.
  2. **Sanatan Hazra Mastermoshai** (Village pathshala schoolmaster, Age ~45):
     - Height: 6.0 Heads tall.
     - Attire: Traditional beige/white khadi kurta and dhoti, round wire-rim spectacles, wooden cane/slate, gentle scholarly demeanor.
     - Deliverable: Model sheet in `02_Character_Design/Secondary_Characters/Sanatan_Master/`.
* **Ghibli Background Environments (Per `Background_Art_Bible.md`)**:
  1. `BG01_Ancestral_Courtyard_Day`: Mud plinth, hand-plastered cow dung courtyard, tulsi mancha, banana fronds, warm morning sunlight.
  2. `BG02_Kali_Puja_Night`: Earthen oil diyas, brass bell, marigold garlands, sacred midnight spiritual atmosphere.
