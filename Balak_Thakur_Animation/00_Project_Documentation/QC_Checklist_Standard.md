# PRODUCTION QUALITY CONTROL (QC) CHECKLIST & STANDARD
## Project: Pram Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)

Every character sheet and animation sequence must pass both **Automated QC (`09_Pipeline_Scripts/qc_validator.py`)** and **Manual Director Review** before moving to `08_Final_Approved_Assets/`.

---

## 1. CHARACTER CONSISTENCY CHECKS (NON-NEGOTIABLE)
- [ ] **Face Shape & Proportions:** Soft 6-year-old oval-round face (`W/H ratio = 0.794 ± 0.05`), full cheeks, rounded chin.
- [ ] **Eye Position & Expression:** Large almond eyes at `0.60H` from crown, inter-ocular spacing `~1.17 × eye width`, warm espresso-brown iris (`#4C2E15`), serene and compassionate gaze.
- [ ] **Hair Silhouette & Part:** Neat espresso-brown hair (`#533E2D`) with clean part on Child Thakur's **left side** (viewer's right), rounded ears fully visible.
- [ ] **Clothing Accuracy:** Unstitched white cotton inner diagonal wrap + symmetric white *uttoriyo* shawl (`#FDEBCD` / `#E0C7B2`) over both shoulders + traditional knee-to-mid-calf white *dhoti* (or pooled softly when seated in *Sukhasana*) + **bare feet**.
- [ ] **Body Proportions:** Standing height locked at **`4.60 H ± 0.20 H`**; seated cross-legged height locked at **`2.85 H ± 0.10 H`**.
- [ ] **Skin Tone Lock:** Warm Bengali golden-tan (`#FDC275` sunlit / `#E39856` shadow / `#CC8756` limb midtone) within `ΔE ≤ 18.0` of Master Reference.

---

## 2. ANATOMICAL QUALITY CHECKS
- [ ] **Hands & Fingers:** Every visible hand has natural child proportions and **5 digits** (4 fingers + 1 thumb). No fused, extra, or twisted fingers.
- [ ] **Feet & Toes:** Bare child feet with natural arch and **5 toes**—no footwear or sandals.
- [ ] **Joints & Limbs:** Smooth shoulder, elbow, wrist, knee, and ankle articulation with no paper-cutout gaps or awkward pinching.

---

## 3. ANIMATION QUALITY CHECKS (24 FPS)
- [ ] **Timing & Spacing:** Smooth 24 FPS motion using ease-in/ease-out (no robotic linear interpolation).
- [ ] **Anticipation & Recovery:** Natural preparatory motion before nods, prayers, or steps, with soft settle at completion.
- [ ] **Follow-Through & Overlapping Action:** *Uttoriyo* shawl drapes and *dhoti* pleats lag slightly behind torso/leg motion by 2–4 frames.
- [ ] **Loop Seamlessness:** Idle, walk, and run cycles match first and last frame pose/velocity seamlessly with zero jump.
- [ ] **Zero Flicker / Background Contamination:** No frame-to-frame lighting strobe or leftover background halo fringes on transparent layers.

---

## 4. TECHNICAL EXPORT CHECKS
- [ ] **Frame Rate:** Strictly `24 FPS`.
- [ ] **Transparency:** Clean 32-bit `RGBA` PNG sequences and `yuva420p` WebM with verified alpha channel (`min_alpha == 0`, clean anti-aliased silhouette edges).
- [ ] **Editable Source Preserved:** Corresponding `.blend` project file and modular RGBA layers stored in `03_Character_Assets/` / `04_Gesture_Library/`.
- [ ] **Previews & Metadata:** `.mp4`, `.gif`, `.webm`, and per-animation `.json` metadata + central `asset_manifest.json` entry validated.
