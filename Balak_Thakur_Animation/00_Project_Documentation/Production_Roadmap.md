# MODULAR AGENT WORKFLOW & PRODUCTION ROADMAP
## Project: Param Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)

---

## 1. MODULAR 6-AGENT PRODUCTION SYSTEM

To ensure strict consistency and prevent unauthorized modifications to the Master Character Design, the pipeline is organized into **6 specialized agent roles** coordinated by the **Main Orchestrator**:

| Agent ID | Role Title | Core Responsibility | Current Status |
| :--- | :--- | :--- | :---: |
| **Orchestrator** | **Main Production Director** | Tracks progress, enforces Quality Gates 1–4, updates `asset_manifest.json`, and coordinates batch reviews. | **ACTIVE** |
| **Agent 1** | **Character Design Director** | Maintains `Character_Bible.md` and `Master_Identity_Profile.json`. Ensures 100% fidelity to the canonical master image. | **ACTIVE** |
| **Agent 2** | **Gesture & Key-Pose Designer** | Plans 24 FPS timing charts, anticipation/follow-through breakdowns, and exposure sheets (X-sheets). | **ACTIVE** |
| **Agent 3** | **AI & Layer Asset Generator** | Generates authentic hand-painted model sheets and modular 32-bit RGBA layers (`03_Character_Assets/Layers/`). | **ACTIVE** |
| **Agent 4** | **Rigging Specialist** | Maintains `THAKUR_CHILD_MASTER_RIG_V001.blend` and `Rig_Control_Documentation.md`. Ensures relative paths and seamless cervical pivots. | **ACTIVE** |
| **Agent 5** | **Animation Specialist** | Renders 24 FPS animation packages across Categories A–F (RGBA PNG sequences, `.blend`, MP4, GIF, WebM). | **ACTIVE** |
| **Agent 6** | **Quality Controller (QC)** | Runs automated 8-point QC validation (`validate_full_library.py`) checking 24 FPS consistency, alpha transparency, and anatomy. | **ACTIVE** |

> **Golden Rule:** Only **Agent 1 (Character Design Director)** with explicit **User Sign-Off** at Quality Gates may update the Master Character Design. Agents 2–6 consume the locked identity profile as read-only truth.

---

## 2. PRODUCTION STATUS & PHASED ROADMAP

### ✅ Phase 1: Toolchain Architecture & Setup (COMPLETED)
- Verified Blender 5.3 LTS, Python 3.10+, and image processing toolchain.
- Formulated multi-machine architecture (Tier 1 Intel CPU Eevee/Workbench + Tier 2 NVIDIA RTX CUDA).

### ✅ Phase 2: Master Character Identity Lock & Model Sheets (COMPLETED)
- **Turnaround Sheet** (`THAKUR_TURNAROUND_SHEET_V001.png`): Front, 3/4 Front, Left Profile, Right Profile, Rear orthographics with anatomically corrected profile hands & feet.
- **Expression Sheet** (`THAKUR_EXPRESSION_SHEET_12_V001.png`): 12 authentic hand-painted expressions.
- **Hand Gesture Sheet** (`THAKUR_HAND_GESTURE_SHEET_V001.png`): 8 mudras and childhood hand gestures.
- **Body Proportion Sheet** (`THAKUR_BODY_PROPORTION_SHEET_V001.png`): 4.6-head standing grid & 2.85-head Sukhasana grid.

### ✅ Phase 3: Modular Layer Extraction & Master 2D Rig (COMPLETED)
- Extracted uncropped master seated plate (`body_seated_sukhasana.png`, 410x435) with full rounded hair crown dome and all 5 bare toes.
- Built `THAKUR_CHILD_MASTER_RIG_V001.blend` with 100% relative texture links (`//../Layers/...`).
- Extracted and calibrated 60+ modular 32-bit RGBA cutout layers.

### ✅ Phase 4: Pilot Benchmark Animations (COMPLETED)
- Validated 5 foundational animations with automated 8-point QC checks.

### ✅ Phase 5: Batch 1 Delivery & Approval (COMPLETED & APPROVED BY USER)
- **Category A (10 Facial Animations)**: Rendered at 24 FPS with 100% authentic hand-painted expression plates (`registered_seated_01_neutral.png` .. `12_determined.png`), zero-ghosting chin registration, and sub-pixel eyelid blinking.
- **Category B (8 Head Movements)**: Rendered at 24 FPS with anatomical cervical spine pivot (`px = 321.5, py = 308.0`), cubic Hermite neck falloff (`y = 246..312`), and full-bust mirrored Look-Left plate (`registered_seated_look_left.png`).
- Formally approved by user in `Batch1_Category_AB_Review.md`.

### ✅ Phase 6: Batch 2 Rollout (COMPLETED & VERIFIED)
- **Category C (10 Hand Gestures)**: Rendered at 24 FPS with zero-double-arm inpainting and dynamic chest matching (`_cover_resting_hands`, `_match_region`, `_opaque_span`).
- **Category D (10 Sitting & Devotional Gestures)**: Cross-legged, naturally, changing position, listening attentively, looking thoughtfully, laughing, smiling, meditating, bowing (extended to 96 frames), prayer.

### ✅ Phase 7: Batch 3 Rollout (COMPLETED & VERIFIED)
- **Category E (Full-Body Locomotion - 7 Animations)**: Walk Cycle (Right Profile, Barefoot), Walk Slow Cycle, Moving Forward & Backward, Standing Idle, Turn Around (5-view cycle), Jump, Run Cycle.
- **Category F (Emotional Storytelling - 8 Animations)**: Becoming Angry, Becoming Emotional, Becoming Happy, Comforting Someone, Expressing Determination, Expressing Wonder, Laughing Naturally, Showing Concern.

### ✅ Master Gesture Library Milestone (COMPLETED)
- **Total Animations**: 56 Animations across 8 Categories.
- **Quality Gates**: All 56 animations passed 8-point automated QC validator (`validate_full_library.py`).
- **Review Assets**: Complete HTML suites (`finalized_library_preview.html`, `natural_motion_preview.html`, `emotional_preview.html`, etc.) and master contact board (`Full_Library_56_Animations_Overview_Board.png`).

### 🟡 Phase 8: Season 1 Episode 1 Asset Pre-Production (CURRENT NEXT STEP)
- **Secondary Characters**:
  1. *Mata Charushila Devi* (Age ~28): 6.2H tall, white taant sari with narrow red border, ghomta, gentle maternal eyes. Model sheet (Turnaround + Expressions).
  2. *Sanatan Hazra Mastermoshai* (Age ~45): 6.0H tall, spectacles, beige khadi kurta & dhoti, pathshala master. Model sheet.
- **Ghibli Background Environments (Per `Background_Art_Bible.md`)**:
  1. `BG01_Ancestral_Courtyard_Day`: Mud plinth, cow dung plaster courtyard, tulsi mancha, banana grove, warm morning sunlight.
  2. `BG02_Kali_Puja_Night`: Earthen oil lamps, brass bell, marigold garlands, sacred midnight atmosphere.

### ⏳ Phase 9: ComfyUI Upscaling & Final 4K Masters (OPTIONAL / TIER 2 GPU)
- Run `09_Pipeline_Scripts/comfyui_workflows/thakur_controlnet_ipadapter_workflow.json` on CUDA machines for temporal inbetweening and 4K upscaling.

---

## 3. MULTI-MACHINE & MULTI-AGENT INVARIANTS

1. **Relative Paths Only**: Always use `//../Layers/...` in Blender. Never hardcode drive letters (`C:`, `E:`).
2. **Authentic Hand-Painted Plates**: Never stretch irises procedurally or paste rectangular eye boxes. Always use registered plates from `THAKUR_EXPRESSION_SHEET_12_V001.png`.
3. **Anatomical Cervical Pivot**: Always pivot head/neck motion at `px = 321.5, py = 308.0` with smooth Hermite falloff.
4. **Git Discipline**: Pull latest before starting work (`git pull origin main`), run QC (`validate_full_library.py`), and commit atomic changes with clear semantic messages.
