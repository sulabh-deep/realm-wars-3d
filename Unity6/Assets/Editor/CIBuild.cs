#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace RealmWars3D.Editor
{
    public static class CIBuild
    {
        private const string MainScene = "Assets/Scenes/Main.unity";

        public static void BuildWebGL()
        {
            Build(BuildTarget.WebGL, Path.Combine("build", "WebGL"));
        }

        public static void BuildAndroid()
        {
            Build(BuildTarget.Android, Path.Combine("build", "Android", "RealmWars3D.apk"));
        }

        private static void Build(BuildTarget target, string location)
        {
            EnsureOutputDirectory(location);
            EnsureMainSceneInBuildSettings();

            var options = new BuildPlayerOptions
            {
                scenes = new[] { MainScene },
                locationPathName = location,
                target = target,
                options = BuildOptions.CleanBuildCache
            };

            Debug.Log($"Realm Wars CI: building {target} -> {location}");
            BuildReport report = BuildPipeline.BuildPlayer(options);
            BuildSummary summary = report.summary;

            Debug.Log($"Realm Wars CI: result={summary.result}, size={summary.totalSize} bytes, time={summary.totalTime}");
            if (summary.result != BuildResult.Succeeded)
                throw new BuildFailedException($"Realm Wars CI build failed for {target}: {summary.result}");
        }

        private static void EnsureMainSceneInBuildSettings()
        {
            if (!File.Exists(MainScene))
                throw new BuildFailedException($"Main scene not found: {MainScene}");

            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(MainScene, true)
            };
        }

        private static void EnsureOutputDirectory(string outputPath)
        {
            string directory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(directory))
                Directory.CreateDirectory(directory);
        }
    }
}
#endif
