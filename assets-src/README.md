# Source 3D assets

Put authoring/source GLBs here. The Blender GitHub Actions workflow processes `.glb` files into `assets/`.

Examples:
- `assets-src/town-center/stage1.glb`
- `assets-src/resources/tree.glb`
- `assets-src/resources/gold-vein.glb`

Do not edit generated files in `assets/` by hand. The first pipeline pass preserves geometry/materials and applies predictable transforms; authored optimization/LOD/material rules can be added to `blender/process_assets.py` as the art pipeline evolves.
