import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets-src'
OUT = ROOT / 'assets'

# Conservative mobile targets. Source GLBs remain untouched; generated GLBs go to assets/.
TARGET_RATIOS = {
    'town-center': 0.18,
    'tree': 0.10,
    'gold-vein': 0.12,
}


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.curves):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


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


def process(src_path: Path):
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
        obj.hide_render = False
        obj.hide_viewport = False

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
    print(f'Processed {src_path} -> {dst} (decimate ratio={ratio})')


if not SRC.exists():
    raise RuntimeError(f'Missing source directory: {SRC}')

sources = sorted(SRC.rglob('*.glb'))
if not sources:
    raise RuntimeError(f'No GLB files found under {SRC}')

for src in sources:
    process(src)
