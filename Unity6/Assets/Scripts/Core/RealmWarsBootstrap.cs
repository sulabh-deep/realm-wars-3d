using System.Collections.Generic;
using UnityEngine;

namespace RealmWars3D
{
    public sealed class RealmWarsBootstrap : MonoBehaviour
    {
        private static readonly Color GroundColor = new(0.47f, 0.64f, 0.35f);
        private Economy economy;

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            BuildLighting();
            BuildGround();
            BuildCamera();
            BuildGameState();
            var input = new GameObject("RTS Input");
            input.AddComponent<RTSSelectionController>();
            var hud = new GameObject("RTS HUD").AddComponent<RTSHUD>();
            hud.Initialize(economy);
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
            ground.GetComponent<MeshRenderer>().sharedMaterial = MakeMaterial(GroundColor);
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
            cameraObject.AddComponent<RTSCameraController>().Initialize(camera);
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
                CreateResourceModel("Tree", "Models/Resources/tree", new Vector3(x, 0f, z), 1f);
            }

            for (int i = 0; i < 4; i++)
            {
                float x = Random.Range(-45f, 45f);
                float z = Random.Range(-35f, 35f);
                CreateResourceModel("Gold Vein", "Models/Resources/gold-vein", new Vector3(x, 0f, z), 1f);
            }

            for (int i = 0; i < 3; i++)
                CreateUnit("Villager", new Vector3(-3f + i * 2f, 0.7f, 4f), 0, Color.blue);
        }

        private void CreateTownCenter(string name, Vector3 position, int owner)
        {
            var prefab = Resources.Load<GameObject>("Models/TownCenter/stage1");
            if (prefab == null)
            {
                CreateProceduralTownCenter(name, position, owner);
                return;
            }

            var root = Instantiate(prefab, position, Quaternion.identity);
            root.name = name;
            var building = root.GetComponent<TownCenter>() ?? root.AddComponent<TownCenter>();
            building.Initialize(owner == 0, 1000f);
            TintFaction(root, owner == 0 ? new Color(0.10f, 0.28f, 0.72f) : new Color(0.72f, 0.10f, 0.10f));
            AddBuildingCollider(root);
        }

        private static void TintFaction(GameObject root, Color accent)
        {
            foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                var materials = renderer.materials;
                for (int i = 0; i < materials.Length; i++)
                {
                    string materialName = materials[i].name.ToLowerInvariant();
                    if (materialName.Contains("accent") || materialName.Contains("banner") || materialName.Contains("flag"))
                        materials[i].color = accent;
                }
                renderer.materials = materials;
            }
        }

        private static void AddBuildingCollider(GameObject root)
        {
            if (root.GetComponentInChildren<Collider>() != null) return;
            var colliderObject = new GameObject("Building Collider");
            colliderObject.transform.SetParent(root.transform, false);
            var box = colliderObject.AddComponent<BoxCollider>();
            box.center = new Vector3(0f, 3f, 0f);
            box.size = new Vector3(12f, 6f, 12f);
        }

        private void CreateResourceModel(string name, string resourcePath, Vector3 position, float scale)
        {
            var prefab = Resources.Load<GameObject>(resourcePath);
            if (prefab == null)
            {
                CreateResource(name, position, name == "Tree" ? PrimitiveType.Capsule : PrimitiveType.Sphere,
                    name == "Tree" ? new Color(0.14f, 0.40f, 0.10f) : new Color(0.90f, 0.63f, 0.10f),
                    name == "Tree" ? 2.5f : 1.1f);
                return;
            }

            var root = Instantiate(prefab, position, Quaternion.identity);
            root.name = name;
            root.transform.localScale *= scale;
        }

        private void CreateProceduralTownCenter(string name, Vector3 position, int owner)
        {
            var root = new GameObject(name);
            root.transform.position = position;
            var building = root.AddComponent<TownCenter>();
            building.Initialize(owner == 0, 1000f);
            CreateCube(root.transform, "Foundation", new Vector3(12f, 0.6f, 12f), new Vector3(0f, 0.3f, 0f), new Color(0.46f, 0.42f, 0.34f));
            CreateCube(root.transform, "Hall", new Vector3(9f, 4.4f, 7f), new Vector3(0f, 2.6f, 0.4f), owner == 0 ? new Color(0.64f, 0.50f, 0.31f) : new Color(0.55f, 0.27f, 0.24f));
            CreateCube(root.transform, "Roof", new Vector3(11f, 0.35f, 9f), new Vector3(0f, 5.1f, 0.4f), owner == 0 ? new Color(0.35f, 0.19f, 0.08f) : new Color(0.32f, 0.08f, 0.08f));
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

        private static void CreateResource(string name, Vector3 position, PrimitiveType primitive, Color color, float scale)
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

        private static Material MakeMaterial(Color color)
        {
            var shader = Shader.Find("Standard") ?? Shader.Find("Universal Render Pipeline/Lit");
            var material = new Material(shader);
            material.color = color;
            material.enableInstancing = true;
            return material;
        }
    }
}
