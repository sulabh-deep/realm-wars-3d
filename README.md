# Realm Wars 3D

Browser-based 3D RTS prototype. Asset-first architecture with external GLB models loaded by Three.js.

## Current asset pipeline

- `assets/town-center/stage1.glb` — player Town Center Stage 1
- Three.js `GLTFLoader` loads assets at runtime rather than embedding binary GLBs into HTML.
- Future stages and unit/building assets should follow the same external-asset convention.
