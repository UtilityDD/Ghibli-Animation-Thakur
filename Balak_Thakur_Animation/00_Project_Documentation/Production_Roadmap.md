# MODULAR AGENT WORKFLOW & PRODUCTION ROADMAP
## Project: Pram Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)

---

## 1. MODULAR 6-AGENT PRODUCTION SYSTEM (PHASE NINE)

To ensure strict consistency and prevent unauthorized modifications to the Master Character Design, the pipeline is organized into **6 specialized agent roles** coordinated by the **Main Orchestrator**:

| Agent ID | Role Title | Core Responsibility | Write Permissions |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | **Main Production Director** | Tracks progress, enforces Quality Gates 1–4, updates `asset_manifest.json`, and requests user approval at milestones. | `00_Project_Documentation/`, `08_Final_Approved_Assets/` |
| **Agent 1** | **Character Design Director** | Maintains `Character_Bible.md` and `Master_Identity_Profile.json`. Reviews all turnaround, expression, and proportion sheets for identity lock. | `00_Project_Documentation/`, `02_Character_Design/` |
| **Agent 2** | **Gesture & Key-Pose Designer** | Plans 24 FPS timing charts, anticipation/follow-through breakdowns, and keyframe exposure sheets (X-sheets) for every gesture. | `04_Gesture_Library/*/*.json` |
| **Agent 3** | **AI & Layer Asset Generator** | Generates turnaround/expression sheets and clean-plates modular RGBA layers (`03_Character_Assets/Layers/`) locked to the Master Color Palette. | `02_Character_Design/`, `03_Character_Assets/Layers/` |
| **Agent 4** | **Rigging Specialist** | Builds and maintains `THAKUR_CHILD_MASTER_RIG_V001.blend` (bones, UV deform meshes, eye/mouth swap controllers, cloth overlap bones). | `03_Character_Assets/Rig/` |
| **Agent 5** | **Animation Specialist** | Animates 24 FPS actions in Blender 5.3 using Method 1 (2D Rig), Method 2 (Frame-by-Frame / Key-Pose deformation), and Method 3 (AI key-pose assist). | `04_Gesture_Library/`, `05_Animation_Previews/` |
| **Agent 6** | **Quality Controller (QC)** | Runs `qc_validator.py` + visual side-by-side audits against `01_Thakur_Age06_Child_Ujanchar_Master_Ref.png`. Rejects any asset that fails identity or export specs. | `07_Production_Tests/`, QC Reports |

> **Golden Rule:** Only **Agent 1 (Character Design Director)** with explicit **User Sign-Off** at Quality Gate 1 may update the Master Character Design. Agents 2–6 consume the locked identity profile as read-only truth.

---

## 2. PHASED PRODUCTION ROADMAP & QUALITY GATES

- **Phase 1: System Inspection & Toolchain Architecture** — **COMPLETED**
- **Phase 2: Master Character Identity Lock & Character Bible Sheets** — **IN PROGRESS (Quality Gate 1)**
  - `A. Turnaround Sheet` (Front, 3/4 Front, Left Profile, Right Profile, Rear, Neutral Standing)
  - `B. Facial Expression Sheet` (12 core expressions)
  - `C. Hand & Arm Gesture Sheet` (8 devotional & natural child gestures)
  - `D. Body Proportion Sheet` (4.6-head standing grid & 2.85-head seated grid)
  - **🔒 QUALITY GATE 1:** User review and approval of the Character Bible sheets.
- **Phase 3: Modular Layer Slicing & Blender 5.3 Master Rig (`THAKUR_CHILD_MASTER_RIG_V001.blend`)**
  - Slice and clean-plate approved RGBA layers for head, eyes (open/half/closed), eyebrows, 12 mouths, hair, torso, *uttoriyo* folds, arms, 8 hand pairs, *dhoti*, legs, and bare feet.
  - Build and test the 2D skeletal & mesh-deform rig in Blender 5.3.
- **Phase 4: Pilot V1 — 5 Foundational Animations (24 FPS)**
  1. `THAKUR_SMILE_GENTLE_BLINK_V001` (3.0s, 72 frames, seamless loop)
  2. `THAKUR_HEAD_NOD_YES_V001` (2.5s, 60 frames, anticipation & recovery)
  3. `THAKUR_PRAYER_SITTING_V001` (4.0s, 96 frames, seated *Sukhasana* start → *Namaskar* rise → serene hold → recovery)
  4. `THAKUR_WALK_CYCLE_V001` (2.0s, 48 frames, seamless loop, two full strides at 24 FPS)
  5. `THAKUR_RUN_CYCLE_V001` (1.5s, 36 frames, seamless loop, joyful child run with cloth follow-through)
  - **🔒 QUALITY GATE 2:** User review and approval of Pilot V1 (PNG sequences, `.blend` files, MP4, GIF, transparent WebM, JSON metadata, QC reports).
- **Phase 5: Full 40-Gesture Library Expansion (Categories A–F)**
  - Expand across all remaining facial, head, hand, sitting/devotional, full-body, and emotional storytelling animations.
