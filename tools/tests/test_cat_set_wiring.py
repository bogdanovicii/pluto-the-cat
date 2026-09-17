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

    def test_feather_teaser(self):
        feather = self.requires(
            'FeatherTeaserGun.cs',
            'public class FeatherTeaserGun : GunBehaviour',
            'public const string ID = "pluto:feather_teaser"',
            'NewGun("Feather Teaser", "pluto_feather_teaser")',
            'PickupObject.ItemQuality.B', 'ETGMod.Databases.Items.Add(gun, null, "ANY")',
            'ProjectileModule.ShootStyle.Charged', 'ProjectileModule.ChargeProjectile',
            'PlutoConfig.FeatherChargeSeconds', 'PlutoConfig.FeatherClip',
            'PlutoConfig.FeatherRange', 'PlutoConfig.FeatherDamage',
            'PlutoConfig.FeatherDistractSeconds', 'PlutoConfig.FeatherBossSlowSeconds',
            'PlutoConfig.FeatherReloadSeconds',
            'RoomHandler.ActiveEnemyType.All', 'CatItemKit.ValidEnemy(enemy)',
            'CatItemKit.HitboxOverlaps(enemy,', 'HashSet<AIActor>',
            'outwardHits', 'returnHits', 'returning',
            'activeLure', 'RestoreGunState', 'CurrentGun', 'OnDestroy',
            'Coroutine', 'StopCoroutine(', 'BehaviorOverridesVelocity', 'BehaviorVelocity',
            'previousOverride', 'previousVelocity', 'appliedVelocity',
            'behaviorSpeculator.Interrupt()', 'healthHaver.IsBoss',
            'CatItemKit.Slow(enemy, PlutoConfig.FeatherBossSlowSeconds',
            'PlayerHasActiveSynergy(PlutoSynergies.Playtime)', 'BallOfYarnItem.ApplyTangle(enemy)',
            'pluto_feather_lure_001', 'pluto_feather_lure_002',
            'pluto_feather_teaser_idle', 'pluto_feather_teaser_charge',
            'pluto_feather_teaser_fire', 'pluto_feather_teaser_empty', 'pluto_feather_teaser_return',
        )
        self.assertNotIn('InterruptAndDisable', feather)
        self.assertNotIn('CatItemKit.Stun(', feather)
        # Gate both normal and inventory/forced reloads, and preserve natural clip accounting.
        for api in ('Attack', 'ContinueAttack', 'CeaseAttack', 'FinishReload'):
            self.assertIn('AccessTools.Method(typeof(Gun), "' + api + '"', feather)
        # Keep the permanent Harmony hooks pinned to the verified DLL overloads. A name-only
        # lookup can silently select the wrong method if a future publicized assembly adds one.
        self.assertIn('new[] { typeof(ProjectileData), typeof(GameObject) }', feather)
        self.assertIn('new[] { typeof(bool), typeof(ProjectileData) }', feather)
        self.assertIn('new[] { typeof(bool), typeof(bool), typeof(bool) }', feather)
        self.assertIn('gun.reloadTime = -1f', feather)
        self.assertIn('gun.reloadTime = previousReloadTime', feather)
        self.assertIn('gun.OverrideAnimations = previousAnimations', feather)
        self.assertNotRegex(feather, r'ClipShotsRemaining\s*=\s*[^=]')
        self.assertIn('OnSwitchedAwayFrom', feather)
        self.assertIn('state.enemy.BehaviorVelocity.Equals(state.appliedVelocity)', feather)
        # Natural expiry must clear its handle without asking Unity to stop the coroutine
        # that is currently executing; teardown paths still stop stored handles.
        self.assertIn('RestoreDistraction(state, false)', feather)
        self.assertIn('RestoreDistraction(states[i], true)', feather)
        # Substeps must actually reach the end point before changing legs, even at low frame times.
        self.assertIn('private Vector2 origin, position, direction', feather)
        self.assertIn('position += move', feather)
        self.assertIn('float remaining = (target - position).magnitude', feather)
        self.assertNotIn('delta.magnitude <= MaxStep', feather)
        # Killing an enemy can remove it from the room list synchronously; iterate a snapshot.
        self.assertIn('AIActor[] enemies = active.ToArray()', feather)
        for suffix in ('idle', 'charge', 'fire', 'empty', 'return'):
            self.assertIn('gun.UpdateAnimation("' + suffix + '"', feather)
            self.assertTrue((RES / ('WeaponCollection/pluto_feather_teaser_' + suffix + '_001.png')).exists())
        for frame in ('001', '002'):
            self.assertTrue((RES / ('ProjectileCollection/pluto_feather_lure_' + frame + '.png')).exists())
        config = self.source('PlutoConfig.cs')
        for key, value in [('ChargeSeconds', '0.6f'), ('Clip', '1'), ('Range', '7f'),
                           ('Damage', '7f'), ('DistractSeconds', '1.5f'),
                           ('BossSlowSeconds', '0.5f'), ('ReloadSeconds', '0.4f')]:
            self.assertIn('Feather' + key + ' = ' + value + ';', config)
        # Reuse the same cooldown and effects for both toys; keep the original Yarn timings.
        yarn = self.requires('BallOfYarnItem.cs', 'public static void ApplyTangle(AIActor enemy)',
                             'static readonly Dictionary<AIActor, float> tangledAt',
                             'CatItemKit.Stun(enemy, PlutoConfig.YarnTangleSeconds)',
                             'PlutoConfig.YarnTangleSeconds + PlutoConfig.YarnSlowSeconds',
                             'BallOfYarnItem.ApplyTangle(body.aiActor)')
        self.assertEqual(1, yarn.count('Dictionary<AIActor, float> tangledAt'))
        synergy = self.requires('PlutoSynergies.cs', 'public const string Playtime = "Playtime"',
                                'Register(Playtime, new List<string> { FeatherTeaserGun.ID, BallOfYarnItem.ID });')
        self.assertEqual(1, synergy.count('Register(Playtime,'))
        plugin = self.source('Plugin.cs')
        self.assertLess(plugin.index('Step("feather teaser", FeatherTeaserGun.Add)'),
                        plugin.index('Step("synergies", PlutoSynergies.Init)'))


if __name__ == '__main__':
    unittest.main()
