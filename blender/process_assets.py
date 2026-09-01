import bpy
from pathlib import Path

ROOT = Path(bpy.path.abspath('//')).parent
SRC = ROOT / 'assets-src'
OUT = ROOT / 'assets'

# Conservative first-pass optimization. Materials are preserved when present;
# source meshes are normalized and exported as external GLBs.

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

def process(src_path: Path):
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(src_path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for obj in meshes:
        obj.select_set(True)
        # Apply imported object transforms so exported assets have predictable bounds.
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        except RuntimeError:
            pass
        # Keep normals and materials intact. A later art pass can add authored LODs.
        obj.select_set(False)
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
    )
    print(f'Processed {src_path} -> {dst}')

if SRC.exists():
    for src in SRC.rglob('*.glb'):
        process(src)
else:
    print('No assets-src directory yet; nothing to process.')
