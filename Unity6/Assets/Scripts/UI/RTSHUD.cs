using UnityEngine;

namespace RealmWars3D
{
    public sealed class RTSHUD : MonoBehaviour
    {
        private Economy economy;
        private GUIStyle header;
        private GUIStyle button;

        public void Initialize(Economy source) => economy = source;

        private void OnGUI()
        {
            if (economy == null) return;
            header ??= new GUIStyle(GUI.skin.label) { fontSize = 15, normal = { textColor = Color.white } };
            button ??= new GUIStyle(GUI.skin.button) { fontSize = 13 };

            GUI.Box(new Rect(0f, 0f, Screen.width, 48f), GUIContent.none);
            GUI.Label(new Rect(14f, 12f, Screen.width - 28f, 28f),
                $"WOOD {economy.Wood}    FOOD {economy.Food}    GOLD {economy.Gold}    POP {economy.Population}/{economy.PopulationCap}", header);

            float h = 58f;
            float y = Screen.height - h - 10f;
            float x = 10f;
            float w = Mathf.Min(190f, (Screen.width - 50f) / 4f);
            DrawTrainButton(ref x, y, w, h, "Villager · 50F", new ResourceCost { food = 50 }, "villager");
            DrawTrainButton(ref x, y, w, h, "Militia · 60F 20G", new ResourceCost { food = 60, gold = 20 }, "militia");
            DrawTrainButton(ref x, y, w, h, "Archer · 30W 40G", new ResourceCost { wood = 30, gold = 40 }, "archer");
            DrawTrainButton(ref x, y, w, h, "Knight · 80F 70G", new ResourceCost { food = 80, gold = 70 }, "knight");
        }

        private void DrawTrainButton(ref float x, float y, float w, float h, string label, ResourceCost cost, string type)
        {
            bool enabled = economy.Population < economy.PopulationCap && economy.CanAfford(cost);
            GUI.enabled = enabled;
            if (GUI.Button(new Rect(x, y, w, h), label, button))
                Train(type, cost);
            GUI.enabled = true;
            x += w + 10f;
        }

        private void Train(string type, ResourceCost cost)
        {
            if (!economy.Spend(cost)) return;
            economy.GetType();
            var townCenter = Object.FindFirstObjectByType<TownCenter>();
            if (townCenter == null) return;
            var position = townCenter.transform.position + new Vector3(6f, 0.8f, 5f);
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = UnitDefinitions.All[type].Name;
            go.transform.position = position;
            go.transform.localScale = Vector3.one * 1.2f;
            var renderer = go.GetComponent<Renderer>();
            var material = new Material(Shader.Find("Standard"));
            material.color = type == "archer" ? Color.green : type == "militia" ? Color.red : type == "knight" ? new Color(0.86f, 0.62f, 0.12f) : Color.blue;
            renderer.sharedMaterial = material;
            var unit = go.AddComponent<Unit>();
            var def = UnitDefinitions.All[type];
            unit.Initialize(type, 0, def.Hp, def.Damage, def.Range);
            typeof(Economy).GetProperty(nameof(Economy.Population))?.SetValue(economy, economy.Population + 1);
        }
    }
}
