using System;
using System.Collections.Generic;
using UnityEngine;

namespace RealmWars3D
{
    [Serializable]
    public struct ResourceCost
    {
        public int wood;
        public int food;
        public int gold;
    }

    public sealed class Economy : MonoBehaviour
    {
        public int Wood { get; private set; } = 250;
        public int Food { get; private set; } = 250;
        public int Gold { get; private set; } = 150;
        public int Population { get; private set; } = 3;
        public int PopulationCap { get; private set; } = 50;

        public bool CanAfford(ResourceCost cost)
            => Wood >= cost.wood && Food >= cost.food && Gold >= cost.gold;

        public bool Spend(ResourceCost cost)
        {
            if (!CanAfford(cost)) return false;
            Wood -= cost.wood;
            Food -= cost.food;
            Gold -= cost.gold;
            return true;
        }

        public bool TryAddPopulation(ResourceCost cost)
        {
            if (Population >= PopulationCap || !Spend(cost)) return false;
            Population++;
            return true;
        }

        public bool TryConsumePopulationSlot()
        {
            if (Population >= PopulationCap) return false;
            Population++;
            return true;
        }

        public void Add(ResourceKind kind, int amount)
        {
            switch (kind)
            {
                case ResourceKind.Wood: Wood += amount; break;
                case ResourceKind.Food: Food += amount; break;
                case ResourceKind.Gold: Gold += amount; break;
            }
        }
    }

    public enum ResourceKind { Wood, Food, Gold }

    public static class UnitDefinitions
    {
        public readonly struct Definition
        {
            public readonly string Name;
            public readonly float Hp;
            public readonly float Damage;
            public readonly float Range;
            public readonly float Speed;
            public readonly ResourceCost Cost;

            public Definition(string name, float hp, float damage, float range, float speed, ResourceCost cost)
            {
                Name = name; Hp = hp; Damage = damage; Range = range; Speed = speed; Cost = cost;
            }
        }

        public static readonly IReadOnlyDictionary<string, Definition> All = new Dictionary<string, Definition>
        {
            ["villager"] = new("Villager", 40f, 3f, 0f, 4f, new ResourceCost { food = 50 }),
            ["militia"] = new("Militia", 60f, 8f, 0f, 4.5f, new ResourceCost { food = 60, gold = 20 }),
            ["archer"] = new("Archer", 45f, 6f, 8f, 4.7f, new ResourceCost { wood = 30, gold = 40 }),
            ["knight"] = new("Knight", 120f, 14f, 0f, 5.2f, new ResourceCost { food = 80, gold = 70 })
        };
    }
}
