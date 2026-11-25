# REUSABLE 2D CHARACTER RIG CONTROL DOCUMENTATION
## Project: Pram Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)
### Master Rig File: `03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend` (Blender 5.3+)

---

## 1. RIG ARCHITECTURE OVERVIEW

The Child Thakur Master Rig is a **hybrid 2D Cut-Out Subdivided Mesh + Skeletal Armature Rig** built in **Blender 5.3** and backed by modular `32-bit RGBA` component layers in `03_Character_Assets/Layers/`.

It is designed for **100% portable multi-machine operation** (using relative texture paths `//../Layers/...`) across both your **Intel i5-12400 (iGPU)** workstation and your higher-spec **RTX GPU** workstation.

### Scene Collections inside `THAKUR_CHILD_MASTER_RIG_V001.blend`
1. **`01_Standing_Locomotion_Rig`**: Articulated standing layers (`Standing_Head`, `Standing_Torso_Uttoriyo`, `Standing_Arm_L`, `Standing_Arm_R`, `Standing_Dhoti`, `Standing_Leg_L`, `Standing_Leg_R`).
2. **`02_Seated_Devotional_Rig`**: Articulated *Sukhasana* seated layers matching the primary Ujanchar reference (`Seated_Legs_Sukhasana`, `Seated_Torso_Resting`, `Seated_Torso_Namaskar`, `Seated_Head_Smile`).
3. **`03_Facial_Expression_Swaps`**: All 12 approved facial expression layers (`Exp_01_neutral` through `Exp_12_determined`) plus the 5-stage progressive upper-eyelid blink layers (`rig_head_smile_blink_00..04.png`).

---

## 2. ARMATURE BONE HIERARCHY (`THAKUR_RIG_ARMATURE`)

| Bone Name | Parent Bone | Function & Recommended Transform Channels |
| :--- | :--- | :--- |
| `root` | *(None)* | Master world-space placement & ground contact reference (`Z = 0.0`). |
| `pelvis` | `root` | Center of gravity (`Z = 1.55`). Controls vertical bounce in walk/run cycles and seated weight shift. |
| `spine` | `pelvis` | Lower torso flex and subtle forward/back lean during prayer or walking. |
| `chest` | `spine` | Upper torso & breathing expansion (`Scale X/Z: 1.000 -> 1.014` on 72-frame breathing loop). |
| `neck` | `chest` | Neck base pivot (`Z = 2.85`). Leads head nods and turns by 1–2 frames. |
| `head` | `neck` | Primary head rotation (`Rot X` for nodding yes, `Rot Z` for shaking no, `Rot Y` for curious tilt). |
| `eye_ctrl` | `head` | 2.5D gaze direction offset and subtle facial parallax during head turns. |
| `eyelid_blink_ctrl` | `head` | Drives the 5-stage progressive upper-eyelid blink sequence (`00_open` → `01_quarter` → `02_half` → `03_three_quarter` → `04_closed`). |
| `brow_L` / `brow_R` | `head` | Subtle vertical brow raise (`+Z`) or furrow (`-Z`) for emotional nuance. |
| `mouth_smile_ctrl` | `head` | Blends smoothly between `01_neutral`, `02_gentle_smile`, and active expression states. |
| `shoulder_L` / `R` | `chest` | Clavicle shrug and breathing secondary motion. |
| `upper_arm_L` / `R` | `shoulder_L/R` | Main arm swing in walk/run cycles and arm raise in *Namaskar* / waving. |
| `forearm_L` / `R` | `upper_arm_L/R` | Elbow flexion (`Rot Y/X`). |
| `hand_L` / `R` | `forearm_L/R` | Wrist rotation and swap controller for the 8 hand gestures (`01_namaskar` .. `08_resting_hands`). |
| `uttoriyo_drape_L/R` | `shoulder_L/R` | **Overlapping Cloth Follow-Through:** Delay rotation by **3 frames** behind `chest`/`upper_arm` motion to create organic cloth sway. |
| `dhoti_pleat_center` | `pelvis` | Central *koncha* pleat swing between the legs during walking and running. |
| `thigh_L` / `R` | `pelvis` | Upper leg stride angle. |
| `shin_L` / `R` | `thigh_L/R` | Knee bend on passing and down poses. |
| `foot_L` / `R` | `shin_L/R` | Barefoot ankle roll (heel contact → flat → toe push-off). |

---

## 3. ANIMATION TIMING & DEFORMATION RULES (24 FPS)

1. **Blinking (Natural Child Blink):**
   - Closing phase: **3 frames** (`open` → `quarter` → `three_quarter` → `closed`).
   - Closed hold: **2 frames** (`closed`).
   - Opening phase (ease-out): **4 frames** (`closed` → `three_quarter` → `half` → `quarter` → `open`).
2. **Breathing & Cloth Follow-Through:**
   - Every idle, smiling, nodding, or praying animation includes a subtle **24 FPS sinusoidal chest breath** (`1.2%` vertical/horizontal chest expansion) with the white *uttoriyo* shawl edges lagging by **3 frames** (`0.125s`).
3. **Zero Gaps Guarantee:**
   - Subdivided mesh planes overlap at joint pivots with soft alpha feathering (`4px` Gaussian falloff) so bending elbows, knees, or the neck never exposes cut-out seams.
