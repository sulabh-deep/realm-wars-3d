import bpy
from pathlib import Path
from mathutils import Vector
import sys
import traceback
import math

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets-src'
OUT = ROOT / 'assets'
TARGET_RATIOS = {'tree': 0.10, 'gold-vein': 0.12}
COLORS = {
    'sandstone': (0.72, 0.48, 0.20, 1.0),
    'stone': (0.55, 0.48, 0.36, 1.0),
    'roof': (0.24, 0.10, 0.045, 1.0),
    'wood': (0.30, 0.14, 0.055, 1.0),
    'turquoise': (0.035, 0.62, 0.68, 1.0),
    'purple': (0.24, 0.055, 0.38, 1.0),
    'gold': (0.95, 0.58, 0.035, 1.0),
    'leaf': (0.08, 0.38, 0.055, 1.0),
    'trunk': (0.28, 0.12, 0.035, 1.0),
    'ore': (0.86, 0.53, 0.025, 1.0),
    'dark': (0.055, 0.035, 0.025, 1.0),
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.images, bpy.data.curves, bpy.data.materials):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def make_material(name, rgba, metallic=0.0, roughness=0.82):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.25
    return m


def assign_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def add_bevel(obj, amount=0.08, segments=2):
    if obj.type != 'MESH':
        return
    mod = obj.modifiers.new('SoftStylizedEdges', 'BEVEL')
    mod.width = amount
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError:
        pass


def box(name, loc, scale, mat, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_mat(o, mat)
    add_bevel(o, bevel, 2)
    return o


def cylinder(name, loc, radius, depth, mat, vertices=16, bevel=0.04):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    assign_mat(o, mat)
    add_bevel(o, bevel, 2)
    return o


def dome(name, loc, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = (radius, radius * 0.62, radius)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_mat(o, mat)
    return o


def cone_roof(name, loc, radius, depth, mat, vertices=4, rotation=math.pi / 4):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=0.12, depth=depth, location=loc, rotation=(0, 0, rotation))
    o = bpy.context.object
    o.name = name
    assign_mat(o, mat)
    return o


def battlements(center_x, center_z, width, depth, y, mat, spacing=1.15):
    # Front/back crenellations
    count_x = max(3, int(width / spacing))
    for i in range(count_x):
        x = center_x - width / 2 + (i + 0.5) * width / count_x
        if i % 2 == 0:
            box('Crenellation', (x, y, center_z - depth / 2), (0.65, 0.65, 0.65), mat, 0.04)
            box('Crenellation', (x, y, center_z + depth / 2), (0.65, 0.65, 0.65), mat, 0.04)
    count_z = max(3, int(depth / spacing))
    for i in range(count_z):
        z = center_z - depth / 2 + (i + 0.5) * depth / count_z
        if i % 2 == 0:
            box('Crenellation', (center_x - width / 2, y, z), (0.65, 0.65, 0.65), mat, 0.04)
            box('Crenellation', (center_x + width / 2, y, z), (0.65, 0.65, 0.65), mat, 0.04)


def banner(loc, height, width, purple, gold):
    # Hanging banner, slightly tapered by using a thin cube plus gold emblem.
    box('Banner', loc, (width, height, 0.08), purple, 0.02)
    box('BannerTrim', (loc[0], loc[1] + height / 2 - 0.06, loc[2] - 0.05), (width + 0.06, 0.10, 0.10), gold, 0.02)
    cylinder('BannerMedallion', (loc[0], loc[1] + 0.05, loc[2] - 0.055), 0.13, 0.08, gold, 12, 0.01).rotation_euler.x = math.pi / 2


def awning(loc, width, turquoise, gold):
    # Small striped canopy built from alternating slanted strips.
    for i in range(5):
        x = loc[0] - width / 2 + (i + 0.5) * width / 5
        mat = turquoise if i % 2 == 0 else gold
        o = box('AwningStripe', (x, loc[1], loc[2]), (width / 5 + 0.04, 0.10, 1.35), mat, 0.025)
        o.rotation_euler.x = math.radians(-18)


def flagpole(loc, height, wood, gold, turquoise):
    cylinder('FlagPole', (loc[0], loc[1] + height / 2, loc[2]), 0.055, height, wood, 10, 0.01)
    cylinder('PoleFinial', (loc[0], loc[1] + height + 0.15, loc[2]), 0.12, 0.30, gold, 10, 0.01)
    box('Flag', (loc[0] + 0.34, loc[1] + height - 0.15, loc[2]), (0.60, 0.30, 0.05), turquoise, 0.01)


def build_town_center(mats):
    """Build a clean, game-ready stylized Town Center matching the supplied references.
    This deliberately does NOT use the current white source GLB: that file is a fused
    single-material early-settlement mesh and cannot produce the requested castle form.
    """
    clear_scene()
    sand, stone, roof, wood = mats['sandstone'], mats['stone'], mats['roof'], mats['wood']
    teal, purple, gold, dark = mats['turquoise'], mats['purple'], mats['gold'], mats['dark']

    # Footprint / courtyard.
    box('Foundation', (0, 0.35, 0), (18, 0.7, 16), stone, 0.10)
    box('MainFoundation', (0, 0.85, 0), (15.5, 0.35, 13.5), sand, 0.06)

    # Main two-storey hall.
    box('MainHall', (0, 5.0, 0.4), (10.5, 7.8, 7.4), sand, 0.12)
    box('UpperBand', (0, 8.85, 0.4), (11.2, 0.55, 7.9), stone, 0.06)

    # Four large corner towers.
    tower_positions = [(-6.6, -4.5), (-6.6, 5.3), (6.6, -4.5), (6.6, 5.3)]
    for idx, (x, z) in enumerate(tower_positions):
        box(f'Tower{idx+1}', (x, 4.0, z), (3.6, 7.6, 3.6), sand, 0.13)
        box(f'TowerCap{idx+1}', (x, 7.95, z), (4.25, 1.05, 4.25), sand, 0.10)
        battlements(x, z, 3.8, 3.8, 8.65, sand, 1.0)
        dome(f'Dome{idx+1}', (x, 9.55, z), 1.72, teal)
        cylinder(f'DomeBase{idx+1}', (x, 8.95, z), 1.75, 0.35, sand, 16, 0.03)
        flagpole((x, 9.75, z), 1.7, wood, gold, teal)
        # Narrow tower window.
        box(f'TowerWindow{idx+1}', (x, 4.6, z - 1.83), (0.55, 1.6, 0.08), dark, 0.02)

    # Main roof and turquoise dome.
    box('RoofSlab', (0, 9.25, 0.4), (11.7, 0.55, 8.3), roof, 0.08)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=4.05, radius2=0.18, depth=2.25, location=(0, 11.0, 0.4))
    main_roof = bpy.context.object
    main_roof.name = 'MainRoof'
    assign_mat(main_roof, roof)
    dome('MainDome', (0, 11.35, 0.4), 3.35, teal)
    cylinder('MainDomeBase', (0, 10.35, 0.4), 3.45, 0.45, sand, 24, 0.05)
    flagpole((0, 12.75, 0.4), 1.8, wood, gold, teal)

    # Front gatehouse and arched-looking entrance assembled from pillars + curved arch blocks.
    front_z = -4.15
    box('GateLeft', (-2.15, 3.15, front_z), (1.1, 5.0, 1.0), sand, 0.08)
    box('GateRight', (2.15, 3.15, front_z), (1.1, 5.0, 1.0), sand, 0.08)
    # Arch ring made from 7 wedge-like blocks around the top of the doorway.
    for i in range(7):
        a = math.pi - i * math.pi / 6
        x = 2.15 * math.cos(a)
        y = 5.55 + 1.35 * math.sin(a)
        o = box('GateArch', (x, y, front_z - 0.03), (0.78, 0.75, 1.05), sand, 0.05)
        o.rotation_euler.z = a - math.pi / 2
    box('GateDark', (0, 2.7, front_z - 0.08), (3.3, 3.8, 0.10), dark, 0.03)
    for y in [1.05, 1.35, 1.65]:
        box('GateStep', (0, y, front_z - 0.65), (4.3, 0.25, 1.1), stone, 0.04)

    # Side walls / parapets connecting towers.
    for x in [-6.6, 6.6]:
        box('SideWall', (x, 6.7, 0.4), (1.15, 3.2, 10.0), sand, 0.06)
    box('RearWall', (0, 6.7, 5.2), (12.8, 3.2, 1.1), sand, 0.06)
    battlements(0, 0.4, 13.0, 10.0, 8.35, sand, 1.0)

    # Front facade balcony, awnings and banners.
    box('Balcony', (0, 7.25, -4.15), (7.2, 0.35, 1.3), stone, 0.05)
    for x in [-3.0, -1.0, 1.0, 3.0]:
        box('BalconyPost', (x, 7.7, -4.65), (0.15, 0.8, 0.15), wood, 0.01)
    for x in [-3.5, -1.75, 0, 1.75, 3.5]:
        awning((x, 7.45, -4.95), 1.55, teal, gold)
    for x in [-4.2, -2.1, 0, 2.1, 4.2]:
        banner((x, 7.0, -4.0), 1.8, 0.72, purple, gold)

    # Side banners.
    for z in [-1.8, 0.8, 3.4]:
        banner((-5.25, 5.7, z), 1.5, 0.62, purple, gold)
        banner((5.25, 5.7, z), 1.5, 0.62, purple, gold)

    # Small market-like side awnings.
    for side in [-1, 1]:
        for z in [-2.2, 0.1, 2.4]:
            awning((side * 5.25, 6.2, z), 1.35, teal, gold)

    # Decorative gold shields.
    for x in [-2.2, 0, 2.2]:
        cylinder('Shield', (x, 8.9, -4.02), 0.22, 0.08, gold, 16, 0.01).rotation_euler.x = math.pi / 2

    # Ensure origin and bounds are predictable.
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            obj.hide_render = False
            obj.hide_viewport = False
            obj.cast_shadow = True
            obj.select_set(False)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def apply_transforms(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    try:
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except RuntimeError:
        pass
    obj.select_set(False)


def optimize_mesh(obj, ratio):
    if obj.type != 'MESH' or not obj.data.polygons:
        return
    modifier = obj.modifiers.new(name='RealmWarsMobileDecimate', type='DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except RuntimeError:
        pass
    obj.select_set(False)


def add_slots(obj, mats):
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)


def classify_tree(obj, mats):
    add_slots(obj, [mats['trunk'], mats['leaf']])
    zs = [v.co.z for v in obj.data.vertices]
    if not zs:
        return
    lo, hi = min(zs), max(zs)
    split = lo + (hi - lo) * 0.38
    for p in obj.data.polygons:
        z = sum(obj.data.vertices[i].co.z for i in p.vertices) / len(p.vertices)
        p.material_index = 0 if z < split else 1


def classify_gold(obj, mats):
    add_slots(obj, [mats['stone'], mats['ore']])
    zs = [v.co.z for v in obj.data.vertices]
    if not zs:
        return
    lo, hi = min(zs), max(zs)
    split = lo + (hi - lo) * 0.52
    for p in obj.data.polygons:
        z = sum(obj.data.vertices[i].co.z for i in p.vertices) / len(p.vertices)
        p.material_index = 1 if p.normal.z > 0.05 and z > split else 0


def export_scene(dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.export_scene.gltf(
        filepath=str(dst), export_format='GLB', use_selection=False,
        export_apply=True, export_materials='EXPORT', export_image_format='AUTO',
        export_texcoords=True, export_normals=True
    )
    if not dst.exists() or dst.stat().st_size == 0:
        raise RuntimeError(f'GLB export did not produce a valid file: {dst}')


def process_source(src_path, mats):
    category = 'town-center' if src_path.parent.name.lower() == 'town-center' else src_path.stem.lower()
    dst = OUT / src_path.relative_to(SRC)

    if category == 'town-center':
        # Replace the fused white early-settlement mesh with a deliberately authored
        # Stage 1 Town Center. This is the only reliable way to match the supplied
        # castle references while retaining a small, mobile-friendly GLB.
        build_town_center(mats)
        export_scene(dst)
        print(f'Generated authored Town Center -> {dst}')
        return

    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(src_path))
    ratio = TARGET_RATIOS.get(category, 0.20)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f'No mesh objects found in {src_path}')
    for obj in meshes:
        apply_transforms(obj)
        optimize_mesh(obj, ratio)
        if category == 'tree':
            classify_tree(obj, mats)
        elif category == 'gold-vein':
            classify_gold(obj, mats)
        else:
            add_slots(obj, [mats['stone']])
            for p in obj.data.polygons:
                p.material_index = 0
        obj.hide_render = False
        obj.hide_viewport = False
    export_scene(dst)
    print(f'Processed {src_path} -> {dst} ({category}, ratio={ratio})')


def main():
    if not SRC.exists():
        raise RuntimeError(f'Missing source directory: {SRC}')
    sources = sorted(SRC.rglob('*.glb'))
    if not sources:
        raise RuntimeError(f'No GLB files found under {SRC}')
    mats = {k: make_material(k, c, 0.65 if k == 'gold' else 0.0, 0.48 if k == 'gold' else 0.82) for k, c in COLORS.items()}
    for src in sources:
        process_source(src, mats)
    print(f'Successfully processed {len(sources)} GLB asset(s).')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
