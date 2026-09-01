import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets-src'
OUT = ROOT / 'assets'

TARGET_RATIOS = {
    'town-center': 0.18,
    'tree': 0.10,
    'gold-vein': 0.12,
}

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
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.curves):
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
    bsdf.inputs['Specular IOR Level'].default_value = 0.25
    return m


def materials():
    return {k: make_material(k, c, 0.65 if k == 'gold' else 0.0, 0.48 if k == 'gold' else 0.82) for k, c in COLORS.items()}


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


def assign_all(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.material_index = 0


def add_slots(obj, mats):
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)


def classify_tree(obj, mats):
    add_slots(obj, [mats['trunk'], mats['leaf']])
    if not obj.data.vertices:
        return
    zs = [v.co.z for v in obj.data.vertices]
    lo, hi = min(zs), max(zs)
    split = lo + (hi - lo) * 0.38
    for p in obj.data.polygons:
        z = sum(obj.data.vertices[i].co.z for i in p.vertices) / len(p.vertices)
        p.material_index = 0 if z < split else 1


def classify_gold(obj, mats):
    add_slots(obj, [mats['stone'], mats['ore']])
    # Give upward-facing/high-center facets the gold material. This works even
    # when the source GLB is a single mesh with no authored material slots.
    zs = [v.co.z for v in obj.data.vertices]
    lo, hi = min(zs), max(zs)
    split = lo + (hi - lo) * 0.52
    for p in obj.data.polygons:
        center_z = sum(obj.data.vertices[i].co.z for i in p.vertices) / len(p.vertices)
        p.material_index = 1 if (p.normal.z > 0.05 and center_z > split) else 0


def classify_town_center(obj, mats):
    # The supplied asset has no useful authored colors. Assign a stylized
    # material palette from polygon position/orientation so the exported GLB
    # carries real materials and does not depend on Three.js overrides.
    add_slots(obj, [mats['sandstone'], mats['stone'], mats['roof'], mats['wood'], mats['turquoise'], mats['purple'], mats['gold']])
    if not obj.data.vertices:
        return
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    zlo, zhi = min(zs), max(zs)
    height = max(zhi - zlo, 1e-6)

    for p in obj.data.polygons:
        verts = [obj.data.vertices[i].co for i in p.vertices]
        c = sum(verts, Vector()) / len(verts)
        nz = p.normal.z
        relz = (c.z - zlo) / height

        # Roof/upper timber structure: sloped surfaces near the top.
        if relz > 0.58 and abs(nz) < 0.82:
            p.material_index = 2
        # Turquoise domes/roof caps: upward-facing surfaces at the upper band.
        elif relz > 0.58 and nz > 0.55:
            p.material_index = 4
        # Lower structural elements.
        elif relz < 0.16:
            p.material_index = 1
        elif abs(nz) < 0.22 and relz > 0.30:
            p.material_index = 3
        else:
            p.material_index = 0


def classify_object(obj, category, mats):
    name = obj.name.lower()
    if category == 'town-center':
        classify_town_center(obj, mats)
    elif category == 'tree':
        classify_tree(obj, mats)
    elif category == 'gold-vein':
        classify_gold(obj, mats)
    else:
        assign_all(obj, mats['stone'])

    # Preserve the authored palette on export.
    for slot in obj.material_slots:
        if slot.material:
            slot.material.use_nodes = True


def process(src_path: Path, mats):
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(src_path))

    category = src_path.stem.lower()
    if src_path.parent.name.lower() == 'town-center':
        category = 'town-center'
    ratio = TARGET_RATIOS.get(category, 0.20)

    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f'No mesh objects found in {src_path}')

    for obj in meshes:
        apply_transforms(obj)
        optimize_mesh(obj, ratio)
        classify_object(obj, category, mats)
        obj.hide_render = False
        obj.hide_viewport = False
        obj.visible_camera = True

    rel = src_path.relative_to(SRC)
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.gltf(
        filepath=str(dst),
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_texcoords=True,
        export_normals=True,
    )
    print(f'Processed {src_path} -> {dst} (category={category}, decimate ratio={ratio})')


if not SRC.exists():
    raise RuntimeError(f'Missing source directory: {SRC}')

sources = sorted(SRC.rglob('*.glb'))
if not sources:
    raise RuntimeError(f'No GLB files found under {SRC}')

mats = materials()
for src in sources:
    process(src, mats)
