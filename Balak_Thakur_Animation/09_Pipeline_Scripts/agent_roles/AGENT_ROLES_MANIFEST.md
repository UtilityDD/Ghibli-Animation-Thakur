# AGENT ROLES & RESPONSIBILITIES MANIFEST (PHASE NINE)
## Project: Pram Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)

This folder defines the modular agent responsibilities for our production pipeline. These instructions can be loaded by Antigravity subagents (`invoke_subagent` / `run_workflow`) or Claude Code / Cursor skills on either the Tier 1 (Intel i5-12400) or Tier 2 (RTX GPU) workstation.

---

### Agent 1 — Character Design Director
- **Identity Lock Authority:** Owns `00_Project_Documentation/Character_Bible.md` and `Master_Identity_Profile.json`.
- **Rule:** Never allow facial structure, hair parting (always Child Thakur's left / viewer's right), 4.6-head standing ratio, 2.85-head seated ratio, or white cotton *uttoriyo* + knee-to-mid-calf *dhoti* attire to drift.

### Agent 2 — Gesture & Key-Pose Designer
- **Timing Authority:** Designs 24 FPS exposure sheets (X-sheets), defining anticipation frames, primary key poses, extremes, breakdown passing poses, and 2–4 frame overlapping cloth follow-through before animation rendering begins.

### Agent 3 — AI & Layer Asset Generator
- **Asset Authority:** Produces turnaround views, facial expression sheets, hand gesture sheets, and slices clean RGBA component layers into `03_Character_Assets/Layers/` (`head_base.png`, `eyes_open.png`, `eyes_half.png`, `eyes_closed.png`, `brows.png`, `mouth_*`, `torso_uttoriyo.png`, `arm_upper_*`, `forearm_*`, `hand_*`, `dhoti_*`, `leg_*`, `foot_*`).

### Agent 4 — Rigging Specialist
- **Rig Authority:** Maintains `03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend` and `00_Project_Documentation/Rig_Control_Documentation.md`. Ensures every bone pivot, UV mesh deform weight, and facial expression switch works cleanly in Blender 5.3 without visible gaps between body parts.

### Agent 5 — Animation Specialist
- **Motion Authority:** Executes the hybrid animation system at 24 FPS:
  - **Method 1 (Rigged 2D Character):** Blinking, breathing, smiling, nodding, waving, praying, sitting gestures.
  - **Method 2 (Frame-by-Frame / Multi-Pose Deformation):** Walking cycle, running cycle, jumping, turning, complex cloth motion.
  - **Method 3 (AI-Assisted Key Poses):** Alternative angles and complex gesture exploration cleaned into rig-compatible layers.

### Agent 6 — Quality Controller (QC)
- **Verification Authority:** Runs `09_Pipeline_Scripts/qc_validator.py` on every generated sheet and animation sequence, checking character consistency, 5-finger / 5-toe anatomy, 24 FPS smoothness, RGBA alpha transparency, and JSON metadata completeness.
