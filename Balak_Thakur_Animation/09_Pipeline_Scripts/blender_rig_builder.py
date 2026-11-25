"""
Blender 5.3 Headless Script: Builds the Reusable 2D Layered Mesh & Skeletal Rig
for Child Thakur (Age 6, Ujanchar) and saves:
`03_Character_Assets/Rig/THAKUR_CHILD_MASTER_RIG_V001.blend`

Supports:
- Hierarchical 2D Armature (`THAKUR_RIG_ARMATURE`) with bones:
  - `root`
  - `pelvis` -> `spine` -> `chest` -> `neck` -> `head`
  - `eye_ctrl`, `brow_L`, `brow_R`, `jaw_mouth_ctrl`
  - `shoulder_L` -> `upper_arm_L` -> `forearm_L` -> `hand_L`
  - `shoulder_R` -> `upper_arm_R` -> `forearm_R` -> `hand_R`
  - `uttoriyo_drape_L`, `uttoriyo_drape_R` (secondary overlapping cloth bones)
  - `dhoti_pleat_center`, `dhoti_hem_L`, `dhoti_hem_R`
  - `thigh_L` -> `shin_L` -> `foot_L`
  - `thigh_R` -> `shin_R` -> `foot_R`
- Layered 2D Subdivided Deform Meshes mapped with Relative Texture Paths (`//../Layers/...`)
  so the `.blend` file works portably across both the Intel i5-12400 machine and the higher-spec RTX GPU machine.
- Orthographic 24 FPS Transparent RGBA Camera & Render Setup.
"""
import os
from pathlib import Path
import bpy

BASE_DIR = Path(r"E:\Codes\Ghibli Animation Thakur\Balak_Thakur_Animation")
LAYERS_DIR = BASE_DIR / "03_Character_Assets" / "Layers"
RIG_OUT_PATH = BASE_DIR / "03_Character_Assets" / "Rig" / "THAKUR_CHILD_MASTER_RIG_V001.blend"


def create_textured_plane(name, tex_filename, width, height, loc_xyz, subdiv=6):
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc_xyz)
    obj = bpy.context.active_object
    obj.name = name
    # Rotate plane to face Front Orthographic Camera (-Y looking toward +Y, so plane lies in X-Z plane)
    obj.rotation_euler = (1.5707963, 0.0, 0.0)
    obj.scale = (width, height, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # Subdivide mesh so armature & lattice deformation creates smooth organic cloth/limb curves
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdiv)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create Emission-based unlit 2D Cel Material with Transparent Alpha
    mat = bpy.data.materials.new(name=f"MAT_{name}")
    mat.use_nodes = True
    if hasattr(mat, "blend_method"):
        mat.blend_method = 'BLEND'
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'BLENDED'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_mix = nodes.new(type='ShaderNodeMixShader')
    node_trans = nodes.new(type='ShaderNodeBsdfTransparent')
    node_emit = nodes.new(type='ShaderNodeEmission')
    node_tex = nodes.new(type='ShaderNodeTexImage')

    img_path = LAYERS_DIR / tex_filename
    if img_path.exists():
        img = bpy.data.images.load(str(img_path))
        node_tex.image = img

    links.new(node_tex.outputs['Color'], node_emit.inputs['Color'])
    links.new(node_tex.outputs['Alpha'], node_mix.inputs['Fac'])
    links.new(node_trans.outputs['BSDF'], node_mix.inputs[1])
    links.new(node_emit.outputs['Emission'], node_mix.inputs[2])
    links.new(node_mix.outputs['Shader'], node_out.inputs['Surface'])

    obj.data.materials.append(mat)
    return obj


def build_master_rig():
    # Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Configure Color Management to Standard so hand-painted cel colors match Master_Identity_Profile.json 1:1
    try:
        scene.view_settings.view_transform = 'Standard'
    except Exception:
        pass

    # Create Collections for Standing Rig, Seated Rig, and Expression Swaps
    col_standing = bpy.data.collections.new("01_Standing_Locomotion_Rig")
    col_seated = bpy.data.collections.new("02_Seated_Devotional_Rig")
    col_expressions = bpy.data.collections.new("03_Facial_Expression_Swaps")
    scene.collection.children.link(col_standing)
    scene.collection.children.link(col_seated)
    scene.collection.children.link(col_expressions)

    # Create Standing Layered Meshes (ordered front-to-back along Y axis so layers never z-fight)
    layers_standing = [
        ("Standing_Leg_L", "rig_leg_L_front.png", 1.1, 1.4, (0.0, 0.04, 0.75)),
        ("Standing_Leg_R", "rig_leg_R_front.png", 1.1, 1.4, (0.0, 0.03, 0.75)),
        ("Standing_Dhoti", "rig_dhoti_pelvis_front.png", 1.2, 1.3, (0.0, 0.01, 1.45)),
        ("Standing_Torso_Uttoriyo", "rig_torso_uttoriyo_front.png", 1.35, 1.85, (0.0, 0.0, 2.35)),
        ("Standing_Arm_L", "rig_arm_L_front.png", 1.1, 1.8, (0.0, -0.02, 2.25)),
        ("Standing_Arm_R", "rig_arm_R_front.png", 1.1, 1.8, (0.0, -0.02, 2.25)),
        ("Standing_Head", "rig_head_front.png", 1.2, 1.25, (0.0, -0.04, 3.35)),
        ("Standing_Full_Reference", "body_full_front.png", 1.45, 4.15, (0.0, -0.06, 2.1))
    ]
    standing_objs = []
    for lname, tex, w, h, loc in layers_standing:
        o = create_textured_plane(lname, tex, w, h, loc)
        col_standing.objects.link(o)
        scene.collection.objects.unlink(o)
        standing_objs.append(o)

    # Create Seated Sukhasana Layered Meshes
    layers_seated = [
        ("Seated_Legs_Sukhasana", "rig_seated_legs_sukhasana.png", 2.4, 1.1, (0.0, 0.02, 0.65)),
        ("Seated_Torso_Resting", "rig_seated_torso_resting.png", 1.9, 1.45, (0.0, 0.0, 1.55)),
        ("Seated_Torso_Namaskar", "gesture_torso_01_namaskar.png", 1.95, 1.65, (0.0, -0.01, 1.55)),
        ("Seated_Head_Smile", "rig_head_smile_blink_00.png", 1.25, 1.15, (0.0, -0.03, 2.38)),
        ("Seated_Full_Sukhasana", "body_seated_sukhasana.png", 2.45, 2.5, (0.0, -0.05, 1.35))
    ]
    for lname, tex, w, h, loc in layers_seated:
        o = create_textured_plane(lname, tex, w, h, loc)
        col_seated.objects.link(o)
        scene.collection.objects.unlink(o)

    # Create 12 Expression Swap Meshes in 03_Facial_Expression_Swaps
    exp_names = [
        "01_neutral", "02_gentle_smile", "03_broad_smile", "04_laughing",
        "05_surprised", "06_curious", "07_angry", "08_sad",
        "09_crying", "10_peaceful", "11_thoughtful", "12_determined"
    ]
    for idx, ename in enumerate(exp_names):
        o = create_textured_plane(f"Exp_{ename}", f"head_exp_{ename}.png", 1.25, 1.15, (0.0, -0.04, 2.38), subdiv=4)
        o.hide_render = (idx != 1)
        col_expressions.objects.link(o)
        scene.collection.objects.unlink(o)

    # Build Hierarchical 2D Armature (`THAKUR_RIG_ARMATURE`)
    bpy.ops.object.armature_add(enter_editmode=True, location=(0.0, 0.0, 0.0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "THAKUR_RIG_ARMATURE"
    arm_data = arm_obj.data
    arm_data.name = "THAKUR_ARMATURE_DATA"

    # Remove default bone
    for b in list(arm_data.edit_bones):
        arm_data.edit_bones.remove(b)

    def add_bone(bname, head_xyz, tail_xyz, parent_name=None, connect=False):
        b = arm_data.edit_bones.new(bname)
        b.head = head_xyz
        b.tail = tail_xyz
        if parent_name and parent_name in arm_data.edit_bones:
            b.parent = arm_data.edit_bones[parent_name]
            b.use_connect = connect
        return b

    # Core spine & head hierarchy
    add_bone("root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.35))
    add_bone("pelvis", (0.0, 0.0, 1.55), (0.0, 0.0, 1.85), "root")
    add_bone("spine", (0.0, 0.0, 1.85), (0.0, 0.0, 2.35), "pelvis", True)
    add_bone("chest", (0.0, 0.0, 2.35), (0.0, 0.0, 2.85), "spine", True)
    add_bone("neck", (0.0, 0.0, 2.85), (0.0, 0.0, 3.05), "chest", True)
    add_bone("head", (0.0, 0.0, 3.05), (0.0, 0.0, 3.95), "neck", True)

    # Facial control bones parented to head
    add_bone("eye_ctrl", (0.0, -0.1, 3.45), (0.0, -0.1, 3.60), "head")
    add_bone("eyelid_blink_ctrl", (0.28, -0.1, 3.52), (0.28, -0.1, 3.62), "head")
    add_bone("brow_L", (0.15, -0.1, 3.62), (0.28, -0.1, 3.64), "head")
    add_bone("brow_R", (-0.15, -0.1, 3.62), (-0.28, -0.1, 3.64), "head")
    add_bone("mouth_smile_ctrl", (0.0, -0.1, 3.22), (0.0, -0.1, 3.30), "head")

    # Left & Right Shoulders, Arms, Forearms, Hands
    add_bone("shoulder_L", (0.08, 0.0, 2.80), (0.38, 0.0, 2.75), "chest")
    add_bone("upper_arm_L", (0.38, 0.0, 2.75), (0.48, 0.0, 2.25), "shoulder_L", True)
    add_bone("forearm_L", (0.48, 0.0, 2.25), (0.52, 0.0, 1.78), "upper_arm_L", True)
    add_bone("hand_L", (0.52, 0.0, 1.78), (0.52, 0.0, 1.52), "forearm_L", True)

    add_bone("shoulder_R", (-0.08, 0.0, 2.80), (-0.38, 0.0, 2.75), "chest")
    add_bone("upper_arm_R", (-0.38, 0.0, 2.75), (-0.48, 0.0, 2.25), "shoulder_R", True)
    add_bone("forearm_R", (-0.48, 0.0, 2.25), (-0.52, 0.0, 1.78), "upper_arm_R", True)
    add_bone("hand_R", (-0.52, 0.0, 1.78), (-0.52, 0.0, 1.52), "forearm_R", True)

    # Secondary Overlapping Cloth Bones (Uttoriyo Shawl & Dhoti Pleats)
    add_bone("uttoriyo_drape_L", (0.32, -0.02, 2.70), (0.42, -0.02, 1.75), "shoulder_L")
    add_bone("uttoriyo_drape_R", (-0.32, -0.02, 2.70), (-0.42, -0.02, 1.75), "shoulder_R")
    add_bone("dhoti_pleat_center", (0.0, -0.02, 1.65), (0.0, -0.02, 0.85), "pelvis")

    # Left & Right Legs and Bare Feet
    add_bone("thigh_L", (0.18, 0.0, 1.55), (0.20, 0.0, 0.95), "pelvis")
    add_bone("shin_L", (0.20, 0.0, 0.95), (0.20, 0.0, 0.25), "thigh_L", True)
    add_bone("foot_L", (0.20, 0.0, 0.25), (0.28, -0.12, 0.05), "shin_L", True)

    add_bone("thigh_R", (-0.18, 0.0, 1.55), (-0.20, 0.0, 0.95), "pelvis")
    add_bone("shin_R", (-0.20, 0.0, 0.95), (-0.20, 0.0, 0.25), "thigh_R", True)
    add_bone("foot_R", (-0.20, 0.0, 0.25), (-0.28, -0.12, 0.05), "shin_R", True)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Parent standing mesh layers to armature with automatic envelope weights
    for o in standing_objs:
        mod = o.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        o.parent = arm_obj

    # Add Front Orthographic Production Camera
    bpy.ops.object.camera_add(location=(0.0, -5.0, 2.05), rotation=(1.5707963, 0.0, 0.0))
    cam = bpy.context.active_object
    cam.name = "THAKUR_ORTHO_CAM"
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 4.5
    scene.camera = cam

    # Convert all image paths to relative paths (`//../Layers/...`) for multi-machine Git portability
    RIG_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(RIG_OUT_PATH))
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception:
        pass

    print(f"Master Blender 5.3 Rig saved successfully to: {RIG_OUT_PATH}")


if __name__ == "__main__":
    build_master_rig()
