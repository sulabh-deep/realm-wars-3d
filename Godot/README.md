# Realm Wars 3D — Godot 4

Godot 4 migration of the original browser RTS prototype.

## First target

Web export only. Android will be added after the Web build and gameplay are stable.

## Run locally

Open `Godot/` in Godot 4.5.x and run `scenes/main.tscn`.

## CI

`.github/workflows/godot-web.yml` builds a playable Web export in headless mode and uploads it as a GitHub Actions artifact.

No Unity activation or engine license secret is required.

The project uses Godot's Compatibility renderer because Godot 4 Web exports target WebAssembly + WebGL 2.0 and the Compatibility renderer is the supported renderer for Web. The default single-threaded export is enabled for broad hosting/browser compatibility.
