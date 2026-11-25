# TOOLCHAIN RESEARCH & HARDWARE COMPARISON REPORT
## Project: Pram Bismoy Balak Thakur (প্রম বিস্ময় বালক ঠাকুর)

---

## 1. WORKSTATION HARDWARE PROFILES (DUAL-MACHINE REPOSITORY)

This repository is engineered to support collaborative production across two hardware tiers:

| Hardware Component | Current Active Machine (Tier 1) | Secondary High-Spec Machine (Tier 2) |
| :--- | :--- | :--- |
| **CPU** | 12th Gen Intel Core i5-12400 (6C/12T) | AMD Ryzen 7 3700X (8C/16T) or higher |
| **RAM** | 16 GB DDR4 (`15.69 GB` usable) | 24 GB+ DDR4 |
| **GPU** | Intel UHD Graphics 730 (2 GB shared, No CUDA) | NVIDIA RTX 2060 (6 GB VRAM, CUDA/Tensor) or higher |
| **System Drive (`C:`)** | 35.03 GB Free (Protected — 0 GB model storage) | 256 GB NVMe SSD (Protected — keep models off `C:`) |
| **Production Drives (`D:` / `E:`)** | `D:` 110.75 GB Free, `E:` 96.66 GB Free | `D:` 1 TB HDD / Secondary Drive for large checkpoints |

---

## 2. COMPREHENSIVE EVALUATION OF AVAILABLE TOOLS

### A. Character & Image Generation
1. **Antigravity Built-in `image-generator` Subagent**
   - **Status:** Verified & Operational on Tier 1 and Tier 2.
   - **Capabilities:** High-resolution turnaround sheets, expression grids, hand gesture sheets, and key-pose reference generation guided by local reference images.
   - **VRAM / Disk Footprint:** 0 MB local VRAM, 0 MB local disk cache.
   - **Verdict:** **Primary Generator for Phase Two Character Bible & Key Poses.**
2. **Python OpenCV + Pillow + Scikit-Image Automated Color & Landmark Calibrator**
   - **Status:** Verified & Operational (`python 3.11`, `opencv-python 4.13`, `pillow 10.4`, `scikit-image 0.26`).
   - **Capabilities:** Exact histogram/Reinhard color locking to `Master_Identity_Profile.json`, clean alpha extraction, orthographic grid alignment, and side-by-side comparison sheet assembly.
   - **Verdict:** **Mandatory Post-Processing & Identity Lock Layer.**

### B. Traditional & Hybrid 2D Animation Software
1. **Blender 5.3.0 (2D Mesh Cut-Out + Lattice/Armature Deform + Grease Pencil)**
   - **Status:** Verified & Operational (`C:\Program Files\Blender Foundation\Blender 5.3\blender.exe`).
   - **Capabilities:** Full Python API (`bpy`) automation, hierarchical 2D bone rigging, UV texture/mouth/eye swapping, organic cloth mesh deformation, headless 24 FPS RGBA rendering (`PNG`), and hardware-agnostic execution (runs in seconds on Intel iGPU via Eevee/Workbench and scales to CUDA/OptiX on RTX 2060).
   - **License:** GPL (100% free for commercial & devotional production).
   - **Verdict:** **Selected Primary Animation & Rigging Engine.**
2. **OpenToonz / Synfig / Krita**
   - **Status:** Not installed on Tier 1.
   - **Verdict:** Not needed; Blender 5.3 provides superior Python automation and unified 2D/2.5D rigging without installing extra software on `C:`.

### C. AI-Assisted Animation & Video Pipelines (Tier 2 GPU Extension)
1. **ComfyUI + ControlNet (OpenPose / Lineart) + IP-Adapter FaceID/Plus**
   - **Status:** Portable workflow JSON provided in `09_Pipeline_Scripts/comfyui_workflows/` for Tier 2 (RTX 2060 6 GB VRAM).
   - **Hardware Notes:** Requires `--medvram` or FP16 SD1.5 / SDXL-Lightning checkpoints stored on `D:\ComfyUI_Models\` on the RTX 2060 workstation. Not run locally on the Intel UHD 730 machine.
   - **Role in Hybrid Pipeline:** Used on Tier 2 for Method 3 (generating intermediate frame references or exploring complex 3D turns from Blender OpenPose passes), while keeping the Blender 2D rig as the authoritative editable source.

### D. Video & Preview Encoding
1. **FFmpeg 8.1.1 Essentials**
   - **Status:** Verified & Operational.
   - **Capabilities:** Lossless RGBA PNG sequence packaging, H.264 `.mp4` preview generation (`yuv420p`), transparent `.webm` (`libvpx-vp9` with `yuva420p` alpha channel), and high-quality 24 FPS palette-gen `.gif` previews.
   - **Verdict:** **Selected Master Encoder.**
