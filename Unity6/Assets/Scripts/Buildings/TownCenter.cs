using UnityEngine;

namespace RealmWars3D
{
    public sealed class TownCenter : MonoBehaviour
    {
        public bool IsPlayer { get; private set; }
        public float MaxHp { get; private set; }
        public float Hp { get; private set; }
        public const float Radius = 6f;

        public void Initialize(bool isPlayer, float maxHp)
        {
            IsPlayer = isPlayer;
            MaxHp = Mathf.Max(1f, maxHp);
            Hp = MaxHp;
        }

        public void TakeDamage(float amount)
        {
            Hp = Mathf.Max(0f, Hp - Mathf.Max(0f, amount));
            if (Hp <= 0f)
                gameObject.SetActive(false);
        }
    }
}
