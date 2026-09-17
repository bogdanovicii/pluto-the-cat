"""Source-level wiring checks for the Round 2 cat set engine integrations."""
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'PlutoTheCat' / 'src'
RES = ROOT / 'PlutoTheCat' / 'Resources' / 'SpriteRoot'


class CatSetWiringTests(unittest.TestCase):
    def source(self, name):
        path = SRC / name
        self.assertTrue(path.exists(), name + ' is not implemented')
        return path.read_text(encoding='utf-8')

    def requires(self, name, *needles):
        text = self.source(name)
        for needle in needles:
            self.assertIn(needle, text, name + ' missing ' + needle)
        return text

    def test_spray_bottle(self):
        spray = self.requires(
            'SprayBottleGun.cs',
            'public class SprayBottleGun : GunBehaviour',
            'public const string ID = "pluto:spray_bottle"',
            'NewGun("Spray Bottle", "pluto_spray_bottle")',
            'Game.Items.Rename("outdated_gun_mods:spray_bottle", ID)',
            'Bogdan and Bianca', 'kitchen counter', 'never worked', 'other people',
            'PickupObject.ItemQuality.C',
            'ProjectileModule.ShootStyle.SemiAutomatic',
            'ETGMod.Databases.Items.Add(gun, null, "ANY")',
            'SetupSprite(null, "pluto_spray_bottle_idle_001"',
            'WeaponLayout.SPRAY_BOTTLE_MUZZLE_X',
            'WeaponLayout.SPRAY_BOTTLE_MUZZLE_Y',
            'pluto_spray_mist_001',
            'PlutoConfig.SprayClip', 'PlutoConfig.SprayCooldown',
            'PlutoConfig.SprayRange', 'PlutoConfig.SprayDamage',
            'PlutoConfig.SprayKnockback', 'PlutoConfig.SprayReloadSeconds',
            'PlutoConfig.SprayFlinchChance', 'PlutoConfig.SprayFlinchSeconds',
            'PlutoConfig.SprayCharmBonusSeconds',
            'TimedAddGoopCircle', 'WaterGoop',
            'PickupObjectDatabase.GetById(10)', 'GetComponent<GoopModifier>()',
            'GetGoopManagerForGoopType(WaterGoop)', 'AddWater(collision.Contact)',
            'impactHandled', 'CatItemKit.HitboxOverlaps(',
            'CatItemKit.ValidEnemy(', 'healthHaver.IsBoss',
            'CatSetRules.RollFlinch(Random.value, PlutoConfig.SprayFlinchChance)',
            'behaviorSpeculator.Interrupt()',
            'CatItemKit.Stun(enemy, PlutoConfig.SprayFlinchSeconds)',
            'PlutoCharmEffect.ExtendOwned(enemy, PlutoConfig.SprayCharmBonusSeconds)',
            'PlayerHasActiveSynergy(PlutoSynergies.BathTime)',
            'bool eligibleActor =', '!enemy.IsHarmlessEnemy',
            '!enemy.healthHaver.IsBoss',
        )
        self.assertNotIn('gun.InfiniteAmmo', spray)
        self.assertNotIn('PreventStartingOwnerFromDropping', spray)
        # InterruptAndDisable sets BehaviorSpeculator.enabled = false permanently; a 0.5 s flinch must only Interrupt.
        self.assertNotIn('InterruptAndDisable', spray)
        self.assertRegex(spray, r'SetProjectileSpriteRight\("pluto_spray_mist_001",\s*(?:8|9|10),\s*(?:8|9|10)')

        collision = spray.index('private void OnCollision(CollisionData collision)')
        water = spray.index('AddWater(collision.Contact)', collision)
        owner = spray.index('PlayerController owner =', water)
        eligible = spray.index('bool eligibleActor =', owner)
        bath = spray.index('PlutoCharmEffect.ExtendOwned(', eligible)
        flinch_filter = spray.index('CatItemKit.ValidEnemy(enemy)', bath)
        self.assertLess(water, owner)
        self.assertLess(owner, eligible)
        self.assertLess(eligible, bath)
        self.assertLess(bath, flinch_filter)

        for resource in (
            'WeaponCollection/pluto_spray_bottle_idle_001.png',
            'WeaponCollection/pluto_spray_bottle_fire_001.png',
            'WeaponCollection/pluto_spray_bottle_fire_002.png',
            'WeaponCollection/pluto_spray_bottle_reload_001.png',
            'WeaponCollection/pluto_spray_bottle_reload_002.png',
            'WeaponCollection/pluto_spray_bottle_reload_003.png',
            'ProjectileCollection/pluto_spray_mist_001.png',
        ):
            self.assertTrue((RES / resource).exists(), resource)

        kit = self.requires(
            'CatItemKit.cs',
            'public static bool ValidEnemy(AIActor enemy)',
            'enemy.healthHaver != null', '!enemy.healthHaver.IsDead',
            '!enemy.IsHarmlessEnemy',
            '!enemy.CanTargetEnemies || enemy.CanTargetPlayers',
            'public static bool HitboxOverlaps(AIActor enemy, Vector2 min, Vector2 max)',
            'HitboxPixelCollider', 'UnitBottomLeft', 'UnitTopRight',
        )
        self.assertRegex(kit, r'eMax\.x\s*>=\s*min\.x\s*&&\s*eMin\.x\s*<=\s*max\.x')
        self.assertRegex(kit, r'eMax\.y\s*>=\s*min\.y\s*&&\s*eMin\.y\s*<=\s*max\.y')

        plugin = self.source('Plugin.cs')
        spray_step = plugin.index('Step("spray bottle", SprayBottleGun.Add)')
        synergy_step = plugin.index('Step("synergies", PlutoSynergies.Init)')
        self.assertLess(spray_step, synergy_step)

    def test_bath_time_extends_owned_charm(self):
        charm = self.requires(
            'PlutoCharmEffect.cs',
            'public static bool ExtendOwned(AIActor enemy, float bonus)',
            'enemy.m_activeEffects', 'enemy.m_activeEffectData',
            'Mathf.Min(enemy.m_activeEffects.Count, enemy.m_activeEffectData.Count)',
            'PlutoCharmEffect effect = enemy.m_activeEffects[i] as PlutoCharmEffect',
            'effect.effectIdentifier == "pluto_love"',
            'effect.duration = CatSetRules.ExtendDuration(effect.duration, bonus)',
            'return true', 'return false',
        )
        start = charm.index('public static bool ExtendOwned(')
        end = charm.index('public override void OnEffectApplied', start)
        self.assertNotIn('ApplyEffect', charm[start:end])

        synergies = self.requires(
            'PlutoSynergies.cs',
            'public const string BathTime = "Bath Time"',
            'Register(BathTime, new List<string> { SprayBottleGun.ID, WetFoodCanItem.ID });',
        )
        self.assertEqual(1, synergies.count('Register(BathTime,'))


if __name__ == '__main__':
    unittest.main()
