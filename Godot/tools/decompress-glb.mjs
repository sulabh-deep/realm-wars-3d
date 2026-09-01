import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';

const input = process.argv[2];
const output = process.argv[3];
if (!input || !output) {
  console.error('Usage: node decompress-glb.mjs <input.glb> <output.glb>');
  process.exit(2);
}

const decoder = await draco3d.createDecoderModule();
const io = new NodeIO()
  .registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'draco3d.decoder': decoder });

const document = await io.read(input);
for (const extension of document.getRoot().listExtensionsUsed()) {
  if (extension.extensionName === 'KHR_draco_mesh_compression') {
    extension.dispose();
  }
}
await io.write(output, document);
console.log(`Decompressed ${input} -> ${output}`);
