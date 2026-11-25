# 🌸 Pram Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)
## High-Fidelity 2D Cutout & Hand-Painted Animation Library (Age 6, Ujanchar)

[![Status](https://img.shields.io/badge/Production-Batch%201%20Approved-success.svg)](https://github.com/UtilityDD/Ghibli-Animation-Thakur)
[![Engine](https://img.shields.io/badge/Blender-5.3%20LTS-orange.svg)](https://www.blender.org/)
[![Style](https://img.shields.io/badge/Visual%20Style-Studio%20Ghibli%20Warmth-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)]()

---

## 📖 Project Overview

**Pram Bismoy Balak Thakur** is a high-fidelity, culturally authentic 2D digital animation library capturing the divine childhood of Thakur (Age 6) in the idyllic rural atmosphere of Ujanchar. 

This repository houses the complete production pipeline:
* **Character Bible & Master Identity Profile**: Rigid proportion formulas (4.6H standing, 2.85H seated), anatomical color palettes, and strict QC checklists.
* **Master 2D Deform Rig (`.blend`)**: Non-linear, 100% relative-path Blender 5.3 armature with subdivided Bezier lattice & mesh deformers for cloth flutter and facial lifelines.
* **Modular Layer System (60+ Slices)**: 32-bit transparent RGBA master textures separated by cranium, hair locks, eyes (sclera/pupil/eyelid), brows, mouth phonemes, cloth, arms, torso, and sukhasana lap.
* **56-Gesture Standardized Animation Library**: 6 core production categories rendered at 24 FPS with transparent alpha channels, lossless WebM, MP4, and animated GIFs.
* **Automated Python Pipeline**: Head-registration, zero-ghosting plate builder, automated QC validation, and ComfyUI IP-Adapter/ControlNet workflows.

---

## 🗂 Repository Directory Layout

```
Ghibli-Animation-Thakur/
├── .gitignore
├── README.md                                          <-- Master Documentation & Setup Guide
├── Divine Glow in a Village Garden.png                <-- Foundational Master Art Reference (1678 x 937)
│
└── Balak_Thakur_Animation/
    ├── 00_Project_Documentation/                      <-- Project Standards & Specifications
    │   ├── Master_Identity_Profile.json               <-- Machine-readable JSON specifications
    │   ├── Character_Bible.md                         <-- Complete character background & anatomy
    │   ├── Visual_Style_Guide.md                      <-- Color swatches, line weights & lighting
    │   ├── Toolchain_Research.md                      <-- Multi-machine architecture specifications
    │   ├── Rig_Control_Documentation.md               <-- Armature bones, constraints & drivers
    │   ├── QC_Checklist_Standard.md                   <-- Strict visual acceptance criteria
    │   └── Production_Roadmap.md                      <-- Phased rollout schedule & milestones
    │
    ├── 01_Reference_Images/                           <-- Approved Character References
    │   ├── Master_Character_Reference_HiRes.png       <-- Canonical master painting
    │   ├── Master_Identity_Landmarks_Overlay.png      <-- Facial proportion grid & key points
    │   └── Master_Child_Thakur_Square_Head.png        <-- Registered face reference plate
    │
    ├── 02_Character_Design/                           <-- Model Sheets & Design Guides
    │   ├── Turnaround/
    │   │   └── THAKUR_TURNAROUND_SHEET_V001.png       <-- Front, 3/4, Profile, Back orthographics
    │   ├── Expressions/
    │   │   └── THAKUR_EXPRESSION_SHEET_12_V001.png    <-- 12 Authentic Hand-Painted Expression Heads
    │   ├── Hand_Gestures/
    │   │   └── THAKUR_HAND_GESTURE_SHEET_V001.png     <-- 8 mudras & natural childhood hand gestures
    │   └── Body_Proportions/
    │       └── THAKUR_BODY_PROPORTION_SHEET_V001.png  <-- 4.6 Head Standing / 2.85 Head Sukhasana grid
    │
    ├── 03_Character_Assets/                           <-- Source Rig & Texture Layers
    │   ├── Rig/
    │   │   └── THAKUR_CHILD_MASTER_RIG_V001.blend     <-- Master 2D Blender deform rig
    │   └── Layers/                                    <-- 60+ modular 32-bit RGBA sliced elements
    │       ├── registered_seated_01_neutral.png ... 12_determined.png
    │       ├── body_seated_sukhasana.png              <-- Uncropped master seated plate
    │       ├── cranium_dome.png, hair_bangs.png, eyes, brows, mouth shapes...
    │       └── arms_pranam, arms_lap_resting, arms_blessing...
    │
    ├── 04_Gesture_Library/                            <-- 56 Standardized Production Gestures
    │   ├── Facial/                                    <-- Category A (10 expressions, 24 FPS PNGs)
    │   ├── Head/                                      <-- Category B (8 head movements, 24 FPS PNGs)
    │   ├── Hands/                                     <-- Category C (10 hand mudras & gestures)
    │   ├── Sitting/                                   <-- Category D1 (10 seated posture variations)
    │   ├── Devotional/                                <-- Category D2 (Bowing, Pranam, Dhyana)
    │   ├── Walking/                                   <-- Category E1 (Walk cycle, turns, standing idle)
    │   ├── Running/                                   <-- Category E2 (Run cycle, jump)
    │   └── Emotional/                                 <-- Category F (8 storytelling emotional sequences)
    │
    ├── 05_Animation_Previews/                         <-- Ready-to-preview MP4, GIF & WebM
    ├── 06_Backgrounds/                                <-- Ghibli watercolor environment layers
    ├── 07_Production_Tests/                           <-- Verification Contact Sheets & QC Boards
    ├── 08_Final_Approved_Assets/                      <-- Asset manifest catalog (`asset_manifest.json`)
    └── 09_Pipeline_Scripts/                           <-- Automation Tooling
        ├── comfyui_workflows/                         <-- ComfyUI ControlNet & IP-Adapter graphs
        ├── build_authentic_expression_plates.py       <-- Zero-ghosting chin-registered plates
        ├── calibrate_registered_gestures.py           <-- Sliced limb calibration & inpainting
        ├── render_batch1_category_a.py                <-- Facial animation batch renderer
        ├── render_batch1_category_b.py                <-- Head movement batch renderer
        ├── fix_turnaround_and_uncrop_seated.py        <-- Boundary dome uncropping & turnaround fix
        └── validate_full_library.py                   <-- Automated 8-point automated QC validator
```

---

## 💻 Multi-Machine Workflow Setup

This repository is optimized for dual-workstation development:
1. **Tier 1 (General Development Workstation)**:
   * Intel Core i5-12400 (6C / 12T), 16 GB DDR4, Intel UHD 730 Graphics.
   * Runs Blender 5.3 Workbench/Eevee preview rendering, layer slicing, Python calibration scripts, and frame validation.
2. **Tier 2 (High-Performance GPU Workstation)**:
   * NVIDIA RTX GPU (RTX 2060 / 3060 / 4080+), CUDA acceleration.
   * Runs the portable ComfyUI workflows in `09_Pipeline_Scripts/comfyui_workflows/` for neural temporal inbetweening, ControlNet Ghibli diffusion styling, and 4K upscaling.

### Cloning on a Second Machine
```bash
git clone https://github.com/UtilityDD/Ghibli-Animation-Thakur.git
cd Ghibli-Animation-Thakur
```

### Blender Asset Portability Guarantee
* All `.blend` project files in `03_Character_Assets/Rig/` and `04_Gesture_Library/` use strictly **relative texture paths** (`//../Layers/...`).
* Simply open `THAKUR_CHILD_MASTER_RIG_V001.blend` in Blender 5.3+ on **any operating system** (Windows, Linux, macOS); textures will resolve instantly without broken links.

---

## 🎨 Visual Identity & Strict Quality Criteria

### Foundational Character Master
* **Subject**: Param Bismoy Balak Thakur (Childhood age 6).
* **Setting**: Village garden in Ujanchar, golden morning sunlight filtering through banyan foliage.
* **Attire**: Pure white homespun cotton *uttoriyo* (chadar) draped gracefully over both shoulders; knee-to-mid-calf pristine white *dhoti*; bare feet with natural rosy soles.

### ⚠️ Critical Facial & Eye Quality Benchmark
> [!IMPORTANT]
> **Zero Uncanny Valley Rule**:
> 1. **Pupil & Eye Convergence**: Never allow asymmetric, squinting, or wall-eyed pupils. Eyes must have soft, focused convergence with warm amber-brown Ghibli specular highlights.
> 2. **Expression Authenticity**: The character's smile must remain innocent, peaceful, and child-like—never a synthetic smirk or strained caricature.
> 3. **Hand-Painted Registration**: Always use the hand-painted expression plates from `THAKUR_EXPRESSION_SHEET_12_V001.png` registered smoothly along the jawline curve (`y=251`) rather than artificial warping.

---

## 🚀 Running the Automated Production Scripts

Ensure Python 3.10+ and Pillow (`pip install pillow numpy`) are installed.

### 1. Build Chin-Registered Authentic Expression Plates
```bash
python Balak_Thakur_Animation/09_Pipeline_Scripts/build_authentic_expression_plates.py
```

### 2. Render Facial & Head Animation Batches
```bash
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_batch1_category_a.py
python Balak_Thakur_Animation/09_Pipeline_Scripts/render_batch1_category_b.py
```

### 3. Run 8-Point Quality Control Validation
```bash
python Balak_Thakur_Animation/09_Pipeline_Scripts/validate_full_library.py
```

---

## 📅 Production Roadmap & Delivery Status

- [x] **Phase 1: Project Architecture & Master Identity Documentation** (Complete)
- [x] **Phase 2: Canonical Model Sheets & Turnaround Guides** (Complete)
- [x] **Phase 3: 60+ Modular 32-Bit RGBA Layer Assets & Rig Setup** (Complete)
- [x] **Phase 4: Pilot Benchmark Animations & QC Validation** (Complete)
- [x] **Phase 5: Batch 1 Approved** (10 Facial + 8 Head = 18 Animations Verified)
- [ ] **Phase 6: Batch 2 Rollout** (10 Hand Mudras + 10 Seated & Devotional Gestures)
- [ ] **Phase 7: Batch 3 Rollout** (Locomotion: Walk/Run Cycles + Emotional Storytelling)
- [ ] **Phase 8: ComfyUI Temporal Upscaling & Final 4K Master Deliverables**

---
*Created with devotion for the timeless portrayal of Param Bismoy Balak Thakur.*
