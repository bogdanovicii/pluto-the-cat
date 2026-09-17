using UnityEngine;

namespace PlutoTheCat
{
    /// <summary>
    /// Shared by every cat-set projectile: harmless and charmed enemies are passed straight through instead of
    /// being hit, so they take no damage, no knockback and no on-impact effect. OnSkipped lets one owner observe
    /// the pass-through (the Spray Bottle uses it for Bath Time); it never makes the projectile collide.
    /// </summary>
    public sealed class CatTargetFilter : MonoBehaviour
    {
        /// <summary>Set per spawned projectile, not on the prefab.</summary>
        public System.Action<AIActor> OnSkipped;

        private SpeculativeRigidbody body;

        private void Start()
        {
            body = GetComponent<SpeculativeRigidbody>();
            if (body != null) body.OnPreRigidbodyCollision += Filter;
        }

        private void Filter(SpeculativeRigidbody myBody, PixelCollider myCollider,
            SpeculativeRigidbody other, PixelCollider otherCollider)
        {
            AIActor enemy = other != null ? other.aiActor : null;
            if (enemy == null || CatItemKit.ValidEnemy(enemy)) return;
            PhysicsEngine.SkipCollision = true;
            if (OnSkipped != null) OnSkipped(enemy);
        }

        private void OnDestroy()
        {
            if (body != null) body.OnPreRigidbodyCollision -= Filter;
            body = null;
            OnSkipped = null;
        }
    }
}
