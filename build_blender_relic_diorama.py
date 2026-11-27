"""
Blender 4.x Python Automated 3D Diorama Scene Builder
사용법: 블렌더(Blender) 실행 -> 상단 [Scripting] 탭 -> [Open]으로 이 파일 열기 -> [Run Script] 실행!
(실제 1:1 미터 스케일: 하부 다크 월넛 원목 함 75cm + 무반사 유리함 45cm = 총높이 1.20m,
 슬림 진홍색 벨벳 단 7.5cm + 하부 상향 Area 조명 + 가시 면류관·장미 + 손바닥이 바닥을 향한 예수님 파손 왼손 & 52도 세워진 파손 합장 손 유물)
"""
import bpy
import bmesh
import math

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def make_plaster_mat(name="Relic_Plaster_SSS"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.88, 0.84, 0.76, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.68
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
    return mat

def make_velvet_mat():
    mat = bpy.data.materials.new("Crimson_Velvet")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.42, 0.03, 0.05, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.88
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.85
    return mat

def make_walnut_mat():
    mat = bpy.data.materials.new("Dark_Walnut_Wood")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.14, 0.08, 0.045, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.42
    return mat

def make_glass_mat():
    mat = bpy.data.materials.new("LowIron_AntiReflective_Glass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.96, 0.99, 0.98, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["IOR"].default_value = 1.50
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.96
    return mat

def add_box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj

def build_left_blessing_hand_relic(plaster_mat):
    # Sculpted palm-down broken left hand relic (Palm facing -Z in Blender? Note Blender is Z-up!)
    # In Blender: X = left-to-right, Y = depth, Z = UP!
    # So PALM FACING FLOOR = -Z! Back of hand = +Z!
    col = bpy.data.collections.new("Relic_Left_Hand_PalmDown")
    bpy.context.scene.collection.children.link(col)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=1.0, location=(0,0,0))
    palm = bpy.context.active_object
    palm.name = "Left_Hand_Palm_Body"
    palm.scale = (0.055, 0.044, 0.018)
    palm.data.materials.append(plaster_mat)

    # Carve concave hollow on underside (-Z) & jagged wrist break (-X)
    bm = bmesh.new()
    bm.from_mesh(palm.data)
    for v in bm.verts:
        if v.co.z < -0.2 and abs(v.co.x) < 0.75 and abs(v.co.y) < 0.75:
            v.co.z += 0.35 * (1.0 - v.co.x*v.co.x)
        if v.co.x < -0.78:
            v.co.x = -0.78 + 0.04 * math.sin(v.co.y * 9.0)
    bm.to_mesh(palm.data)
    bm.free()

    # Add two surviving blessing fingers (index & middle) curving gently downward (-Z) + broken thumb & knuckle stumps
    parts = [palm]
    finger_specs = [
        ("Index_Finger_Relic",  (0.072, -0.016, -0.008), (0, math.radians(108), 0), (0.0085, 0.0085, 0.036)),
        ("Middle_Finger_Relic", (0.075,  0.002, -0.009), (0, math.radians(110), 0), (0.0090, 0.0090, 0.039)),
        ("Broken_Ring_Stump",   (0.050,  0.019, -0.002), (0, math.radians(96),  0), (0.0080, 0.0080, 0.012)),
        ("Broken_Pinky_Stump",  (0.044,  0.033, -0.003), (0, math.radians(95),  0), (0.0072, 0.0072, 0.009)),
        ("Broken_Thumb_Stump",  (-0.002,-0.042, -0.009), (math.radians(38), math.radians(65), 0), (0.011, 0.010, 0.016)),
    ]
    for fname, loc, rot, sc in finger_specs:
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.0, depth=2.0, location=loc, rotation=rot)
        f = bpy.context.active_object
        f.name = fname
        f.scale = sc
        f.data.materials.append(plaster_mat)
        parts.append(f)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = palm
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()

    # Position at Upper-Left (-0.085, 0, 1.13m) pitched -28 deg downward (↘) with PALM FACING STRAIGHT DOWN (-Z)!
    palm.location = (-0.085, 0.0, 1.13)
    palm.rotation_euler = (0.0, math.radians(28.0), 0.0)
    return palm

def build_praying_hands_relic(plaster_mat, velvet_top_z):
    parts = []
    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=18, radius=1.0, location=(0, side*0.012, 0))
        h = bpy.context.active_object
        h.scale = (0.034, 0.013, 0.092)
        h.data.materials.append(plaster_mat)
        parts.append(h)
        # Crossed thumbs on upper (+X) bridge!
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16, radius=0.009, depth=0.068,
            location=(0.028, side*0.004, -0.005),
            rotation=(math.radians(side*28), math.radians(-12), 0)
        )
        th = bpy.context.active_object
        th.data.materials.append(plaster_mat)
        parts.append(th)

    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    pray = bpy.context.active_object
    pray.name = "Relic_Praying_Hands_CrossedThumbs"
    bpy.ops.object.shade_smooth()

    # Place on lower-right (+0.098, 0, velvet_top_z + 0.062) tilted 52 deg upward toward upper-left blessing palm!
    pray.location = (0.098, 0.0, velvet_top_z + 0.062)
    pray.rotation_euler = (0.0, math.radians(-38.0), 0.0)
    return pray

def build_diorama():
    clear_scene()
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.world.color = (0.02, 0.018, 0.016)

    m_plaster = make_plaster_mat()
    m_velvet = make_velvet_mat()
    m_walnut = make_walnut_mat()
    m_glass = make_glass_mat()

    # 1. 75cm Dark Walnut Cabinet Stand (Total height with 45cm glass = 1.20m)
    add_box("Walnut_Cabinet_Stand", (0, 0, 0.375), (0.50, 0.42, 0.75), m_walnut)
    # 2. 7.5cm Halved Crimson Velvet Altar Platform
    velvet_h = 0.075
    add_box("Crimson_Velvet_Base", (0, 0, 0.75 + velvet_h/2), (0.43, 0.35, velvet_h), m_velvet)
    velvet_top = 0.75 + velvet_h

    # 3. Crown of Thorns (Left) & Roses (Right)
    m_thorn = bpy.data.materials.new("Dark_Thorns")
    m_thorn.use_nodes = True
    m_thorn.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.09, 0.05, 0.03, 1.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.078, minor_radius=0.008, location=(-0.095, 0.0, velvet_top + 0.016))
    bpy.context.active_object.data.materials.append(m_thorn)

    # 4. Two Broken Relics in Baptismal Blessing Pose!
    build_left_blessing_hand_relic(m_plaster)
    build_praying_hands_relic(m_plaster, velvet_top)

    # 5. Low-Iron Glass Box Walls (50 x 42 x 45 cm -> Top at 1.20m)
    gh = 0.45
    gz = 0.75 + gh/2
    add_box("Glass_Front", (0, -0.20, gz), (0.48, 0.004, gh), m_glass)
    add_box("Glass_Back",  (0,  0.20, gz), (0.48, 0.004, gh), m_glass)
    add_box("Glass_Left",  (-0.24, 0, gz), (0.004, 0.40, gh), m_glass)
    add_box("Glass_Right", ( 0.24, 0, gz), (0.004, 0.40, gh), m_glass)
    add_box("Glass_Top",   (0, 0, 1.20),   (0.48, 0.40, 0.006), m_glass)

    # 6. Warm 3000K Bottom-Up Uplight + Overhead Museum Key Light + Camera
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 0.78))
    up_light = bpy.context.active_object
    up_light.name = "Warm_Bottom_Uplight"
    up_light.rotation_euler = (math.radians(180), 0, 0)
    up_light.data.energy = 18.0
    up_light.data.color = (1.0, 0.72, 0.42)
    up_light.data.size = 0.42

    bpy.ops.object.light_add(type='SPOT', location=(-0.08, -0.35, 1.65))
    key_light = bpy.context.active_object
    key_light.name = "Museum_3000K_KeySpot"
    key_light.rotation_euler = (math.radians(32), 0, math.radians(-10))
    key_light.data.energy = 65.0
    key_light.data.color = (1.0, 0.90, 0.78)

    bpy.ops.object.camera_add(location=(0.0, -1.35, 1.05), rotation=(math.radians(88), 0, 0))
    bpy.context.scene.camera = bpy.context.active_object

if __name__ == "__main__":
    build_diorama()
