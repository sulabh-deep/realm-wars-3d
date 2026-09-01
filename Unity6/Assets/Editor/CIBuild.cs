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
            EnsureMainSceneInBuildSettings();
            string location = Path.Combine("build", "WebGL");
            Directory.CreateDirectory(location);

            var options = new BuildPlayerOptions
            {
                scenes = new[] { MainScene },
                locationPathName = location,
                target = BuildTarget.WebGL,
                options = BuildOptions.CleanBuildCache
            };

            Debug.Log($"Realm Wars CI: building WebGL -> {location}");
            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException($"Realm Wars CI WebGL build failed: {report.summary.result}");

            Debug.Log($"Realm Wars CI: WebGL succeeded, size={report.summary.totalSize} bytes, time={report.summary.totalTime}");
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
    }
}
#endif
