using UnityEngine;
using UnityEngine.InputSystem;

namespace RealmWars3D
{
    public sealed class Unit : MonoBehaviour
    {
        public string UnitType { get; private set; }
        public int Owner { get; private set; }
        public float MaxHp { get; private set; }
        public float Hp { get; private set; }
        public float Damage { get; private set; }
        public float MoveSpeed { get; private set; }
        public float AttackRange { get; private set; }

        private Vector3 destination;
        private bool moving;
        private GameObject selectionMarker;

        public void Initialize(string unitType, int owner, float hp, float damage, float range)
        {
            UnitType = unitType;
            Owner = owner;
            MaxHp = hp;
            Hp = hp;
            Damage = damage;
            AttackRange = range;
            MoveSpeed = 4f;
            destination = transform.position;
        }

        private void Update()
        {
            if (!moving) return;

            Vector3 next = Vector3.MoveTowards(transform.position, destination, MoveSpeed * Time.deltaTime);
            transform.position = next;
            Vector3 flat = destination - transform.position;
            flat.y = 0f;
            if (flat.sqrMagnitude < 0.01f)
                moving = false;
            else
                transform.rotation = Quaternion.LookRotation(flat.normalized, Vector3.up);
        }

        public void SetDestination(Vector3 worldPosition)
        {
            destination = new Vector3(worldPosition.x, transform.position.y, worldPosition.z);
            moving = true;
        }

        public void SetSelected(bool selected)
        {
            if (selected)
            {
                if (selectionMarker != null) return;
                selectionMarker = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                selectionMarker.name = "Selection Ring";
                selectionMarker.transform.SetParent(transform, false);
                selectionMarker.transform.localPosition = new Vector3(0f, -0.58f, 0f);
                selectionMarker.transform.localScale = new Vector3(1.25f, 0.02f, 1.25f);
                var renderer = selectionMarker.GetComponent<Renderer>();
                renderer.sharedMaterial = CreateMarkerMaterial();
                Object.Destroy(selectionMarker.GetComponent<Collider>());
            }
            else if (selectionMarker != null)
            {
                Object.Destroy(selectionMarker);
                selectionMarker = null;
            }
        }

        private static Material CreateMarkerMaterial()
        {
            var material = new Material(Shader.Find("Standard"));
            material.color = new Color(1f, 0.92f, 0.18f);
            material.SetFloat("_Glossiness", 0.15f);
            return material;
        }

        public void TakeDamage(float amount)
        {
            Hp = Mathf.Max(0f, Hp - Mathf.Max(0f, amount));
            if (Hp <= 0f)
                Destroy(gameObject);
        }
    }
}
