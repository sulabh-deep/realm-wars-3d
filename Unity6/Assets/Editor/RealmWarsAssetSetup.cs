#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEngine;

namespace RealmWars3D.Editor
{
    [InitializeOnLoad]
    internal static class RealmWarsAssetSetup
    {
        static RealmWarsAssetSetup() => EditorApplication.delayCall += SyncSourceAssets;

        [MenuItem("Realm Wars/Sync Source 3D Assets")]
        public static void SyncSourceAssets()
        {
            string projectRoot = Directory.GetParent(Application.dataPath)?.FullName ?? string.Empty;
            string repoRoot = Directory.GetParent(projectRoot)?.FullName ?? string.Empty;
            string sourceRoot = Path.Combine(repoRoot, "assets");
            string destinationRoot = Path.Combine(Application.dataPath, "Resources", "Models");
            if (!Directory.Exists(sourceRoot))
            {
                Debug.LogWarning($"Realm Wars asset sync skipped. Source folder not found: {sourceRoot}");
                return;
            }

            CopyTree(Path.Combine(sourceRoot, "town-center"), Path.Combine(destinationRoot, "TownCenter"));
            CopyTree(Path.Combine(sourceRoot, "resources"), Path.Combine(destinationRoot, "Resources"));
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log("Realm Wars: GLB assets synchronized into Assets/Resources/Models.");
        }

        private static void CopyTree(string source, string destination)
        {
            if (!Directory.Exists(source)) return;
            Directory.CreateDirectory(destination);
            foreach (string file in Directory.GetFiles(source, "*", SearchOption.TopDirectoryOnly))
            {
                string extension = Path.GetExtension(file).ToLowerInvariant();
                if (extension != ".glb" && extension != ".gltf" && extension != ".bin" && extension != ".png" && extension != ".jpg" && extension != ".jpeg") continue;
                string target = Path.Combine(destination, Path.GetFileName(file));
                if (!File.Exists(target) || File.GetLastWriteTimeUtc(file) > File.GetLastWriteTimeUtc(target))
                    File.Copy(file, target, true);
            }
        }
    }
}
#endif
