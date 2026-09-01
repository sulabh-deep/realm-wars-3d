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

const dracoExtension = document.getRoot().listExtensionsUsed().find(
  (extension) => extension.extensionName === 'KHR_draco_mesh_compression'
);

if (dracoExtension) {
  // Reading the source with a registered decoder materializes the Draco geometry
  // into normal accessors. Disposing the extension removes the KHR_draco wrapper
  // before the document is written back out as a standard GLB.
  dracoExtension.dispose();
  console.log(`Decoded Draco geometry in ${input}`);
} else {
  console.log(`No Draco compression found in ${input}; copying through glTF Transform.`);
}

await io.write(output, document);
console.log(`Wrote ${output}`);
