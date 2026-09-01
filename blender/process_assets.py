import bpy
from pathlib import Path
import math
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets-src'
OUT = ROOT / 'assets'

COLORS = {
    'wall': (0.64, 0.48, 0.28, 1.0),
    'stone': (0.43, 0.40, 0.33, 1.0),
    'roof': (0.38, 0.20, 0.08, 1.0),
    'wood': (0.24, 0.10, 0.045, 1.0),
    'accent': (0.12, 0.35, 0.72, 1.0),
    'gold': (0.86, 0.58, 0.08, 1.0),
    'leaf': (0.08, 0.38, 0.055, 1.0),
    'trunk': (0.28, 0.12, 0.035, 1.0),
    'ore': (0.95, 0.62, 0.05, 1.0),
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def mat(name, color, metallic=0.0, roughness=0.82):
    m = bpy.data.materials.new(name=name)
    m.diffuse_color = color
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.22
    return m


def assign(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)


def add_box(name, loc, size, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if bevel > 0:
        mod = obj.modifiers.new('EdgeBevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        mod.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            pass
    return obj


def add_cylinder(name, loc, radius, depth, material, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material)
    return obj


def add_cone(name, loc, radius1, radius2, depth, material, vertices=16):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material)
    return obj


def build_initial_town_center(materials):
    clear_scene()
    wall = materials['wall']
    stone = materials['stone']
    roof = materials['roof']
    wood = materials['wood']
    accent = materials['accent']
    gold = materials['gold']

    add_box('Foundation', (0, 0.30, 0), (12.0, 0.60, 12.0), stone, 0.10)
    add_box('Floor', (0, 0.66, 0), (10.8, 0.18, 10.8), wall, 0.03)

    for x in (-4.6, 4.6):
        for z in (-4.1, 4.1):
            add_box('TimberPost', (x, 3.0, z), (0.65, 5.8, 0.65), wood, 0.05)
    add_box('RearWall', (0, 3.2, 4.35), (9.6, 5.0, 0.55), wall, 0.05)
    add_box('LeftWall', (-4.35, 3.0, 0), (0.45, 4.7, 7.8), wall, 0.04)
    add_box('RightWall', (4.35, 3.0, 0), (0.45, 4.7, 7.8), wall, 0.04)

    for side in (-1, 1):
        roof_panel = add_box('ThatchRoof', (0, 6.0, side * 1.95), (10.8, 0.28, 5.1), roof, 0.03)
        roof_panel.rotation_euler.x = math.radians(side * -31)
    add_box('RidgeBeam', (0, 7.45, 0), (11.1, 0.38, 0.42), wood, 0.03)

    for x in (-1.0, 1.0):
        add_box('BellTowerPost', (x, 8.5, 0), (0.30, 2.0, 0.30), wood, 0.02)
    for z in (-0.9, 0.9):
        add_box('BellTowerBeam', (0, 8.0, z), (2.35, 0.28, 0.28), wood, 0.02)
    add_cone('BellRoof', (0, 9.85, 0), 1.55, 0.15, 1.65, roof, 4)
    add_cylinder('Bell', (0, 8.35, 0), 0.48, 0.70, gold, 16)

    for i in range(10):
        a = i * math.tau / 10
        add_cylinder('FirepitStone', (math.cos(a) * 1.0, 0.95, math.sin(a) * 1.0), 0.28, 0.45, stone, 8)
    add_cylinder('Firepit', (0, 1.13, 0), 0.67, 0.08, wood, 12)

    add_box('FactionBanner', (0, 4.8, -4.62), (1.05, 1.85, 0.08), accent, 0.02)
    add_box('FactionBannerTrim', (0, 5.72, -4.67), (1.16, 0.10, 0.10), gold, 0.01)
    add_cylinder('FactionMedallion', (0, 4.85, -4.70), 0.18, 0.08, gold, 12)
    add_cylinder('FlagPole', (0, 9.65, 0), 0.06, 2.8, wood, 8)
    add_box('FactionFlag', (0.42, 10.55, 0), (0.80, 0.42, 0.06), accent, 0.01)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def export_glb(dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(dst),
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT',
        export_image_format='AUTO',
        export_texcoords=False,
        export_normals=True,
        # Godot's built-in glTF importer does not decode Draco in this CI setup.
        export_draco_mesh_compression_enable=False,
    )
    if not dst.exists() or dst.stat().st_size == 0:
        raise RuntimeError(f'Invalid GLB export: {dst}')
    print(f'Exported {dst} ({dst.stat().st_size} bytes)')


def process_resource(src_path, materials, kind):
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(src_path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f'No mesh in {src_path}')
    for obj in meshes:
        if kind == 'tree':
            obj.scale *= 0.10
            if obj.data.materials:
                for slot in obj.data.materials:
                    if slot and slot.diffuse_color:
                        name = slot.name.lower()
                        if 'leaf' in name or 'green' in name:
                            slot.diffuse_color = COLORS['leaf']
                        else:
                            slot.diffuse_color = COLORS['trunk']
        else:
            obj.scale *= 0.12
            if obj.data.materials:
                for slot in obj.data.materials:
                    slot.diffuse_color = COLORS['ore']
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    materials = {k: mat(k, c, 0.65 if k == 'gold' else 0.0, 0.50 if k == 'gold' else 0.82) for k, c in COLORS.items()}
    town_src = SRC / 'town-center' / 'stage1.glb'
    if town_src.exists():
        build_initial_town_center(materials)
        export_glb(OUT / 'town-center' / 'stage1.glb')
    for kind in ('tree', 'gold-vein'):
        src = SRC / 'resources' / f'{kind}.glb'
        if src.exists():
            process_resource(src, materials, kind)
            export_glb(OUT / 'resources' / f'{kind}.glb')
    print('Successfully processed requested 3D assets without Draco compression.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
