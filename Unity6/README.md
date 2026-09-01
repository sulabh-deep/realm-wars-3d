# Realm Wars 3D — Unity 6

This directory is the Unity 6 migration of the browser/Three.js RTS prototype.

## Current playable slice

- Orthographic RTS camera with mouse rotation/zoom and touch pinch zoom
- Player and enemy Town Centers
- Starter villagers
- Randomized trees and gold resource nodes
- Unit selection with a selection ring
- Right-click unit movement commands
- Resource HUD
- Unit training buttons for Villager, Militia, Archer and Knight
- Mobile-oriented 60 FPS target

## Open

Open the `Unity6` directory as a Unity 6.0 project (`6000.0.65f1` or a compatible Unity 6 editor).

The main scene is `Assets/Scenes/Main.unity`.

## Source asset sync

The repository already contains authored/generated GLB assets under `../assets` and `../assets-src`. The editor script `Assets/Editor/RealmWarsAssetSetup.cs` mirrors usable assets into `Assets/Models` when the project opens, and exposes `Realm Wars > Sync Source 3D Assets` for manual re-sync.

The current bootstrap uses lightweight procedural visuals so the gameplay slice can run independently of model import; the next migration step is replacing those visuals with the imported Town Center/resource prefabs and then moving combat/pathfinding into dedicated systems.

## Controls

- Desktop: left click select, right click move, middle-drag rotate, wheel zoom
- Mobile: tap select, pinch zoom
