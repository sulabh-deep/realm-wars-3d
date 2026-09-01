using System.Collections.Generic;
using UnityEngine;

namespace RealmWars3D
{
    public sealed class RealmWarsBootstrap : MonoBehaviour
    {
        private static readonly Color GroundColor = new(0.47f, 0.64f, 0.35f);
        private readonly List<Transform> selection = new();

        private Economy economy;
        private RTSCameraController rtsCamera;

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;

            BuildLighting();
            BuildGround();
            BuildCamera();
            BuildGameState();
        }

        private void BuildLighting()
        {
            var hemi = new GameObject("Hemisphere Light").AddComponent<Light>();
            hemi.type = LightType.Directional;
            hemi.intensity = 0.65f;
            hemi.color = new Color(0.87f, 0.94f, 1f);
            hemi.transform.rotation = Quaternion.Euler(50f, -35f, 0f);

            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.0f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(48f, -30f, 0f);
        }

        private void BuildGround()
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(11f, 1f, 11f);
            var renderer = ground.GetComponent<MeshRenderer>();
            renderer.sharedMaterial = MakeMaterial(GroundColor);
        }

        private void BuildCamera()
        {
            var cameraObject = new GameObject("RTS Camera");
            var camera = cameraObject.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 18f;
            camera.nearClipPlane = 0.1f;
            camera.farClipPlane = 500f;
            cameraObject.tag = "MainCamera";

            rtsCamera = cameraObject.AddComponent<RTSCameraController>();
            rtsCamera.Initialize(camera);
        }

        private void BuildGameState()
        {
            var stateObject = new GameObject("Game State");
            economy = stateObject.AddComponent<Economy>();

            CreateTownCenter("Player Town Center", Vector3.zero, 0);
            CreateTownCenter("Enemy Town Center", new Vector3(32f, 0f, -24f), 1);

            for (int i = 0; i < 12; i++)
            {
                float x = Random.Range(-50f, 50f);
                float z = Random.Range(-40f, 40f);
                CreateResource("Tree", new Vector3(x, 0f, z), PrimitiveType.Capsule, new Color(0.14f, 0.40f, 0.10f), 2.5f);
            }

            for (int i = 0; i < 4; i++)
            {
                float x = Random.Range(-45f, 45f);
                float z = Random.Range(-35f, 35f);
                CreateResource("Gold Vein", new Vector3(x, 0f, z), PrimitiveType.Sphere, new Color(0.90f, 0.63f, 0.10f), 1.1f);
            }

            for (int i = 0; i < 3; i++)
                CreateUnit("Villager", new Vector3(-3f + i * 2f, 0.7f, 4f), 0, Color.blue);
        }

        private void CreateTownCenter(string name, Vector3 position, int owner)
        {
            var root = new GameObject(name);
            root.transform.position = position;
            var building = root.AddComponent<TownCenter>();
            building.Initialize(owner == 0, 1000f);

            CreateCube(root.transform, "Foundation", new Vector3(12f, 0.6f, 12f), new Vector3(0f, 0.3f, 0f), new Color(0.46f, 0.42f, 0.34f));
            CreateCube(root.transform, "Hall", new Vector3(9f, 4.4f, 7f), new Vector3(0f, 2.6f, 0.4f), owner == 0 ? new Color(0.64f, 0.50f, 0.31f) : new Color(0.55f, 0.27f, 0.24f));
            CreateCube(root.transform, "Left Wing", new Vector3(2.2f, 3.5f, 6f), new Vector3(-4f, 2.0f, 0.7f), new Color(0.50f, 0.39f, 0.25f));
            CreateCube(root.transform, "Right Wing", new Vector3(2.2f, 3.5f, 6f), new Vector3(4f, 2.0f, 0.7f), new Color(0.50f, 0.39f, 0.25f));
            CreateCube(root.transform, "Roof", new Vector3(11f, 0.35f, 9f), new Vector3(0f, 5.1f, 0.4f), owner == 0 ? new Color(0.35f, 0.19f, 0.08f) : new Color(0.32f, 0.08f, 0.08f));
            CreateCube(root.transform, "Banner", new Vector3(1.2f, 2.0f, 0.12f), new Vector3(0f, 4.3f, -3.65f), owner == 0 ? new Color(0.10f, 0.28f, 0.72f) : new Color(0.72f, 0.10f, 0.10f));
            CreateCylinder(root.transform, "Tower", 0.7f, 3.2f, new Vector3(0f, 6.7f, 0f), owner == 0 ? new Color(0.55f, 0.38f, 0.20f) : new Color(0.45f, 0.20f, 0.18f));
        }

        private void CreateUnit(string unitName, Vector3 position, int owner, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = unitName;
            go.transform.position = position;
            go.transform.localScale = Vector3.one * 1.2f;
            go.GetComponent<Renderer>().sharedMaterial = MakeMaterial(color);
            var unit = go.AddComponent<Unit>();
            unit.Initialize(unitName.ToLowerInvariant(), owner, 40f, 3f, 3.0f);
        }

        private void CreateResource(string name, Vector3 position, PrimitiveType primitive, Color color, float scale)
        {
            var go = GameObject.CreatePrimitive(primitive);
            go.name = name;
            go.transform.position = position + Vector3.up * (primitive == PrimitiveType.Sphere ? scale : scale * 0.7f);
            go.transform.localScale = new Vector3(scale, scale * 1.6f, scale);
            go.GetComponent<Renderer>().sharedMaterial = MakeMaterial(color);
        }

        private static void CreateCube(Transform parent, string name, Vector3 size, Vector3 localPosition, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPosition;
            go.transform.localScale = size;
            go.GetComponent<Renderer>().sharedMaterial = MakeMaterial(color);
        }

        private static void CreateCylinder(Transform parent, string name, float radius, float height, Vector3 localPosition, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPosition;
            go.transform.localScale = new Vector3(radius * 2f, height * 0.5f, radius * 2f);
            go.GetComponent<Renderer>().sharedMaterial = MakeMaterial(color);
        }

        private static Material MakeMaterial(Color color)
        {
            var material = new Material(Shader.Find("Standard"));
            material.color = color;
            material.enableInstancing = true;
            return material;
        }
    }
}
