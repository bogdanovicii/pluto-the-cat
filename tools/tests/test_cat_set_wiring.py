"""Source-level wiring checks for the Round 2 cat set engine integrations."""
import pathlib
import re
import struct
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
            'PlutoCharmEffect.ExtendOwned(enemy, PlutoConfig.SprayCharmBonusSeconds, PlutoConfig.SprayCharmMaxSeconds)',
            'PlutoConfig.SprayCharmMaxSeconds',
            'PlayerHasActiveSynergy(PlutoSynergies.BathTime)',
            'bool eligibleActor =', '!enemy.IsHarmlessEnemy',
            '!enemy.healthHaver.IsBoss',
            # The mist itself passes through harmless and charmed enemies.
            'AddComponent<CatTargetFilter>()', 'filter.OnSkipped = OnPassedThrough',
            'private void OnPassedThrough(AIActor enemy)',
        )
        self.assertNotIn('gun.InfiniteAmmo', spray)
        self.assertNotIn('PreventStartingOwnerFromDropping', spray)
        # InterruptAndDisable sets BehaviorSpeculator.enabled = false permanently; a 0.5 s flinch must only Interrupt.
        self.assertNotIn('InterruptAndDisable', spray)
        self.assertRegex(spray, r'SetProjectileSpriteRight\("pluto_spray_mist_001",\s*(?:8|9|10),\s*(?:8|9|10)')

        # A real impact wets first, then rolls the flinch. Only valid enemies ever reach it: the shared
        # CatTargetFilter skips the collision for harmless and charmed actors, so they take no damage,
        # no knockback and no water.
        collision = spray.index('private void OnCollision(CollisionData collision)')
        water = spray.index('AddWater(collision.Contact)', collision)
        flinch_filter = spray.index('CatItemKit.ValidEnemy(enemy)', water)
        self.assertLess(water, flinch_filter)
        self.assertNotIn('PlutoCharmEffect.ExtendOwned(', spray[collision:flinch_filter])
        # Bath Time is the one documented exception and rides the pass-through, not an impact.
        skipped = spray.index('private void OnPassedThrough(AIActor enemy)')
        eligible = spray.index('bool eligibleActor =', skipped)
        bath = spray.index('PlutoCharmEffect.ExtendOwned(', eligible)
        self.assertLess(eligible, bath)

        self.requires(
            'CatTargetFilter.cs',
            'public sealed class CatTargetFilter : MonoBehaviour',
            'OnPreRigidbodyCollision += Filter',
            'OnPreRigidbodyCollision -= Filter',
            'CatItemKit.ValidEnemy(enemy)',
            'PhysicsEngine.SkipCollision = true',
            'OnSkipped',
        )

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
            'enemy.m_activeEffects', 'enemy.m_activeEffectData',
            'Mathf.Min(enemy.m_activeEffects.Count, enemy.m_activeEffectData.Count)',
            'PlutoCharmEffect effect = enemy.m_activeEffects[i] as PlutoCharmEffect',
            'effect.effectIdentifier == "pluto_love"',
            'public static bool ExtendOwned(AIActor enemy, float bonus, float max)',
            'effect.duration = CatSetRules.ExtendCapped(effect.duration, bonus, max)',
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
        # A returned lure releases the gun/reload gate but its independently hosted
        # distraction lease keeps running for the full configured duration.
        self.assertIn('Finish(false)', feather)
        self.assertIn('LureFinished(this, cancelDistractions, position)', feather)
        self.assertIn('DetachDistractionsFromLure(lure, lastPosition, cancelDistractions)', feather)
        self.assertIn('lease.targetPosition = lastPosition', feather)
        self.assertIn('lease.source = null', feather)
        distract_method = feather.index('private IEnumerator Distract(DistractionLease lease)')
        lure_class = feather.index('public class FeatherLure : MonoBehaviour')
        self.assertLess(distract_method, lure_class)
        self.assertIn('elapsed < PlutoConfig.FeatherDistractSeconds', feather[distract_method:lure_class])
        # Interrupting once is insufficient: an AI can begin another attack before 1.5 s.
        # The active ownership lease must suppress firing on every frame without disabling AI.
        update_owner = feather.index('private static bool UpdateDistractionOwnership(')
        release_owner = feather.index('private static void ReleaseDistractionOwnership(', update_owner)
        self.assertIn('behaviorSpeculator.Interrupt()', feather[update_owner:release_owner])
        # Co-op/multiple lures share one nesting-safe ownership generation per enemy.
        self.assertIn('Dictionary<AIActor, SharedDistraction> SharedDistractions', feather)
        self.assertIn('List<DistractionLease> leases', feather)
        self.assertIn('state.leases[state.leases.Count - 1]', feather)
        self.assertIn('ReferenceEquals(current, state)', feather)
        self.assertIn('ReferenceEquals(lease.shared, state)', feather)
        self.assertIn('state.enemy.BehaviorOverridesVelocity = state.previousOverride', feather)
        self.assertIn('state.enemy.BehaviorVelocity = state.previousVelocity', feather)
        # Playtime: while the yarn tangle holds the enemy, the feather must hand its velocity back so the
        # enemy visibly stops chasing, and only re-take it if the stun ends first.
        self.assertIn('behaviorSpeculator.IsStunned', feather)
        self.assertIn('private static bool Tangled(AIActor enemy)', feather)
        self.assertIn('private static void SuspendDistraction(SharedDistraction state)', feather)
        self.assertIn('public bool suspended;', feather)
        suspend = feather.index('if (Tangled(state.enemy))', update_owner)
        resume = feather.index('if (state.suspended)', suspend)
        reassert = feather.index('state.enemy.BehaviorVelocity = state.appliedVelocity;', resume)
        self.assertLess(suspend, resume)
        self.assertLess(resume, reassert)
        self.assertIn('EndDistraction(lease, false)', feather)
        self.assertIn('EndDistraction(leases[i], true)', feather)
        # Outbound and return are separate valid hits; each starts its own full lease.
        self.assertNotIn('distractionLeases[i].enemy == enemy && distractionLeases[i].source == source', feather)
        for teardown in ('OnSwitchedAwayFrom', 'OnDropped', 'OnDestroy', 'OnDisable'):
            start = feather.index(teardown)
            self.assertIn('CancelAllDistractions()', feather[start:start + 260])
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

    def test_toilet_paper_roll(self):
        paper = self.requires(
            'ToiletPaperRollItem.cs',
            'public class ToiletPaperRollItem : PlayerItem',
            'public const string ID = "pluto:toilet_paper_roll"',
            'Bogdan and Bianca', 'home defence',
            'PickupObject.ItemQuality.C',
            'ItemBuilder.SetupItem(item,',
            'ItemBuilder.CooldownType.Damage', 'PlutoConfig.TPRechargeDamage',
            'PlutoConfig.TPLength', 'PlutoConfig.TPSeconds', 'PlutoConfig.TPHits',
            'CatSetRules.StreamerAlive(Time.time, born, PlutoConfig.TPSeconds, hits, PlutoConfig.TPHits)',
            'unadjustedAimPoint.XY() - user.CenterPosition',
            'new Vector2(-aim.y, aim.x)',
            'user.CenterPosition + aim',
            'CollisionLayer.BulletBlocker', 'OnPreRigidbodyCollision',
            'private const float SegmentHalfWidth = 3f / 16f',
            'ManualWidth = 6', 'ManualHeight = 6',
            'CatItemKit.IsEnemyBullet(projectile)', 'projectile.collidesWithPlayer',
            'PhysicsEngine.SkipCollision = true',
            'static readonly HashSet<Projectile> ClaimedProjectiles',
            'TryClaimProjectile(projectile)', 'CleanupProjectileClaims()',
            'projectile.HasDiedInAir', 'projectile.DieInAir(',
            'destroyed = projectile == null || projectile.HasDiedInAir',
            'TearNearest(', 'List<Segment>',
            'Coroutine lifetime', 'StopCoroutine(lifetime)',
            'OwnershipValid()', 'owner.CurrentRoom == room', 'DestroyAllSegments()',
            'OnPreDrop', 'OnDestroy', 'Teardown(false)',
            'FinishNormally()', 'PlayerHasActiveSynergy(PlutoSynergies.Shredder)',
            'PlutoConfig.TPConfettiDamage', 'RoomHandler.ActiveEnemyType.All',
            'CatItemKit.ValidEnemy(enemy)', 'enemy.specRigidbody.HitboxPixelCollider',
            'CatSetRules.StreamerStripOverlapsAabb(',
            'PlutoConfig.TPLength, SegmentHalfWidth * 2f',
            'ApplyDamage(', 'CoreDamageTypes.None', 'DamageCategory.Normal',
            'toilet_paper_streamer_001', 'toilet_paper_bits_001', 'toilet_paper_confetti_001',
        )
        # Segment bodies are projectile-only blockers: actors pass through, while each
        # actually destroyed enemy projectile accounts for one hit at most.
        self.assertNotIn('CollisionLayer.EnemyCollider', paper)
        self.assertNotIn('CollisionLayer.PlayerCollider', paper)
        # Alexandria ItemBuilder.SetupItem registers PlayerItems in the normal ANY loot pool.
        self.assertNotIn('PickupObject.ItemQuality.EXCLUDED', paper)
        self.assertNotIn('CatItemKit.HitboxOverlaps(enemy, envelopeMin, envelopeMax)', paper)
        claim = paper.index('TryClaimProjectile(projectile)')
        die = paper.index('projectile.DieInAir(', claim)
        count = paper.index('hits++', die)
        self.assertLess(claim, die)
        self.assertLess(die, count)
        self.assertIn('if (!destroyed)', paper[die:count])
        self.assertIn('finally', paper[die:count])
        self.assertIn('ClaimedProjectiles.Remove(projectile)', paper[die:count])
        # Confetti is only reachable from normal timeout/final-hit completion.
        finish = paper.index('private void FinishNormally()')
        teardown = paper.index('private void Teardown(bool normalCompletion)', finish)
        self.assertIn('Teardown(true)', paper[finish:teardown])
        self.assertIn('if (normalCompletion && shredder)', paper[teardown:])
        self.assertNotIn('BurstConfetti()', paper[:finish])

        config = self.source('PlutoConfig.cs')
        for key, value in [('TPRechargeDamage', '400f'), ('TPLength', '4f'),
                           ('TPSeconds', '5f'), ('TPHits', '12'),
                           ('TPConfettiDamage', '10f')]:
            self.assertIn('public static ' + ('int ' if key == 'TPHits' else 'float ') + key + ' = ' + value + ';', config)

        synergy = self.requires(
            'PlutoSynergies.cs',
            'public const string Shredder = "Shredder"',
            'Register(Shredder, new List<string> { ToiletPaperRollItem.ID, ScratchingPostItem.ID });',
        )
        self.assertEqual(1, synergy.count('Register(Shredder,'))
        plugin = self.source('Plugin.cs')
        self.assertLess(plugin.index('Step("toilet paper roll", ToiletPaperRollItem.Init)'),
                        plugin.index('Step("synergies", PlutoSynergies.Init)'))

        for resource in (
            ROOT / 'PlutoTheCat/Resources/Items/toilet_paper_roll_icon.png',
            ROOT / 'PlutoTheCat/Resources/Effects/cat_set/toilet_paper_streamer_001.png',
            ROOT / 'PlutoTheCat/Resources/Effects/cat_set/toilet_paper_bits_001.png',
            ROOT / 'PlutoTheCat/Resources/Effects/cat_set/toilet_paper_confetti_001.png',
        ):
            self.assertTrue(resource.exists(), str(resource.relative_to(ROOT)))

    def test_cone_of_shame(self):
        cone = self.requires(
            'ConeOfShameItem.cs',
            'public class ConeOfShameItem : PassiveItem',
            'public const string ID = "pluto:cone_of_shame"',
            'PickupObject.ItemQuality.B', 'ItemBuilder.SetupItem(item,',
            'public override void Update()', 'base.Update()',
            'Bogdan and Bianca', "Vet's clinic", 'see its point',
            'PlutoConfig.ConeCooldown', 'PlutoConfig.ConeArcDegrees',
            'PlutoConfig.ConeRadius', 'CatSetRules.ConeReady(',
            'CatSetRules.InCone(delta.x, delta.y, aim.x, aim.y,',
            'ReadOnlyCollection<Projectile> projectiles = StaticReferenceManager.AllProjectiles',
            'CatItemKit.IsEnemyBullet(projectile)', 'projectile.collidesWithPlayer',
            'projectile.HasDiedInAir', 'projectile.DieInAir(',
            'break;', 'lastBlock = Time.time', 'wasReady = false',
            'if (!wasReady && ready)', 'PlutoVFX.BlockSpark',
            'wearer.CenterPosition + new Vector2(0f, 1.1f)',
            'public override void DisableEffect(PlayerController player)',
            'public override DebrisObject Drop(PlayerController player)',
            'public override void OnDestroy()', 'private void Unhook()',
        )
        # ItemBuilder.SetupItem registers ordinary non-EXCLUDED passives in the ANY loot pool.
        self.assertNotIn('PickupObject.ItemQuality.EXCLUDED', cone)
        self.assertNotIn('SilencerInstance.DestroyBulletsInRange', cone)
        # The ready scan runs every frame: it must not copy the whole live projectile list.
        self.assertNotIn('AllProjectiles.ToArray()', cone)
        self.assertNotIn('using System.Linq;', cone)
        self.assertEqual(3, cone.count('Unhook();'))
        # Initial pickup is already ready but must not masquerade as a cooldown transition.
        self.assertIn('wasReady = true', cone)
        pickup = cone.index('public override void Pickup(')
        update = cone.index('public override void Update()', pickup)
        self.assertNotIn('PlutoVFX.Spawn(', cone[pickup:update])
        # Only the first qualifying live hostile shot is consumed in a scan.
        die = cone.index('projectile.DieInAir(')
        block_time = cone.index('lastBlock = Time.time', die)
        stop = cone.index('break;', block_time)
        self.assertLess(die, block_time)
        self.assertLess(block_time, stop)

        config = self.source('PlutoConfig.cs')
        for key, typename, value in (
            ('ConeCooldown', 'float', '3f'), ('ConeArcDegrees', 'float', '70f'),
            ('ConeRadius', 'float', '1.5f'), ('ConeCocoStuffing', 'int', '1')):
            self.assertIn('public static ' + typename + ' ' + key + ' = ' + value + ';', config)

        coco = self.requires(
            'CocoBlueItem.cs', '"cone_"', '"knight_"',
            'PlayerHasActiveSynergy(PlutoSynergies.MatchingCones)',
            '? PlutoConfig.ConeCocoStuffing : 0', 'matchingCones',
            'charges.Grow(PlutoConfig.ConeCocoStuffing)',
            'charges.Clamp(MaxStuffing)',
            'anim.Prefix = clip',
        )
        self.assertNotIn('anim.AnimNames', coco)
        for clip in ('idle', 'move'):
            self.assertIn('prefix + "' + clip + '"', coco)
        for clip in ('pet', 'block', 'ko'):
            self.assertIn('named.name == "' + clip + '"', coco)
        self.assertIn('SetClip(named.anim, prefix + named.name)', coco)
        self.requires('CocoFriends.cs',
                      'CompanionKitRules.CocoHelmetPrefix(matchingCones, knight != null,')

        rules = self.source('CompanionKitRules.cs')
        selector = rules[rules.index('public static string CocoHelmetPrefix('):]
        self.assertIn('if (matchingCones) return "cone_";', selector)
        self.assertIn('return squire ? "knight_" : "";', selector)

        synergy = self.requires(
            'PlutoSynergies.cs', 'public const string MatchingCones = "Matching Cones"',
            'Register(MatchingCones, new List<string> { ConeOfShameItem.ID, CocoBlueItem.ID });',
        )
        self.assertEqual(1, synergy.count('Register(MatchingCones,'))
        plugin = self.source('Plugin.cs')
        self.assertLess(plugin.index('Step("cone of shame", ConeOfShameItem.Init)'),
                        plugin.index('Step("synergies", PlutoSynergies.Init)'))

        self.assertTrue((ROOT / 'PlutoTheCat/Resources/Items/cone_of_shame_icon.png').exists())

    def test_coffee_mug(self):
        mug = self.requires(
            'CoffeeMugItem.cs',
            'public class CoffeeMugItem : PlayerItem',
            'public const string ID = "pluto:coffee_mug"',
            'string name = "Coffee Mug"',
            'ItemBuilder.SetupItem(item, "Off The Table",',
            'Bogdan', 'Bianca', 'looked her in the eye',
            'PickupObject.ItemQuality.C',
            'ItemBuilder.CooldownType.Damage, PlutoConfig.CoffeeRechargeDamage',
            'Plugin.ITEM_ROOT + "/coffee_mug_icon"',
            # 3-tile throw toward aim that stops at the first collision, shattering once.
            'unadjustedAimPoint.XY() - user.CenterPosition',
            'baseData.range = PlutoConfig.CoffeeRange',
            'OnDestruction', 'private bool armed', 'public void Disarm()',
            # Configured player-owned shard ring.
            'int count = PlutoConfig.CoffeeShardCount',
            'CatSetRules.ShardAngle(i, count)',
            'baseData.damage = PlutoConfig.CoffeeShardDamage',
            'shard.Owner = owner',
            'coffee_shard_00', 'coffee_puddle_001',
            # Harmless/charmed enemies are neither hit nor slowed.
            'CatItemKit.ValidEnemy(enemy)', 'AddComponent<CatTargetFilter>()',
            # Puddle slow: hitbox scan, owned slow id, released on exit/end/teardown.
            'RoomHandler.ActiveEnemyType.All',
            'CatItemKit.HitboxOverlaps(enemy, min, max)',
            'remaining = PlutoConfig.CoffeeSlowSeconds',
            'CatItemKit.Slow(enemy,', 'SlowId = "pluto_coffee_slow"',
            'RemoveEffect(SlowId)', 'owner.CurrentRoom != ownerRoom',
            # Espresso on use.
            'PlayerHasActiveSynergy(PlutoSynergies.Espresso)',
            'as CatnipPouchItem',
            'ExtendZoomies(user, PlutoConfig.CoffeeZoomiesBonusSeconds)',
            # Teardown.
            'public override void OnPreDrop(PlayerController user)',
            'public override void OnDestroy()', 'private void Teardown()',
            'Plugin.Log(',
        )
        self.assertNotIn('PickupObject.ItemQuality.EXCLUDED', mug)
        # The slow is a plain speed effect: no goop at all (never damaging/fire), no manual velocity ownership.
        for banned in ('Goop', 'BehaviorOverridesVelocity', 'MovementSpeed', 'CenterPosition, min'):
            self.assertNotIn(banned, mug)
        self.assertEqual(2, mug.count('Teardown();'))
        # The mug shatters exactly once: the armed latch drops before any shard/puddle is spawned.
        latch = mug.index('if (!armed')
        disarm = mug.index('armed = false;', latch)
        shatter = mug.index('.Shatter(', disarm)
        self.assertLess(latch, disarm)
        self.assertLess(disarm, shatter)
        # Released enemies are exactly those previously slowed by this puddle and no longer inside it.
        self.assertIn('slowed', mug[mug.index('RemoveEffect(SlowId)') - 400:mug.index('RemoveEffect(SlowId)')])

        config = self.source('PlutoConfig.cs')
        for key, typename, value in (
            ('CoffeeRechargeDamage', 'float', '300f'), ('CoffeeRange', 'float', '3f'),
            ('CoffeeShardCount', 'int', '10'), ('CoffeeShardDamage', 'float', '5f'),
            ('CoffeeSlowSeconds', 'float', '3f'), ('CoffeeZoomiesBonusSeconds', 'float', '2f')):
            self.assertIn('public static ' + typename + ' ' + key + ' = ' + value + ';', config)

        synergy = self.requires(
            'PlutoSynergies.cs', 'public const string Espresso = "Espresso"',
            'Register(Espresso, new List<string> { CoffeeMugItem.ID, CatnipPouchItem.ID });',
        )
        self.assertEqual(1, synergy.count('Register(Espresso,'))
        plugin = self.source('Plugin.cs')
        self.assertLess(plugin.index('Step("coffee mug", CoffeeMugItem.Init)'),
                        plugin.index('Step("synergies", PlutoSynergies.Init)'))

        for resource in (
            'Items/coffee_mug_icon.png', 'Effects/cat_set/coffee_puddle_001.png',
            'Effects/cat_set/coffee_shard_001.png', 'Effects/cat_set/coffee_shard_002.png',
            'Effects/cat_set/coffee_shard_003.png', 'Effects/cat_set/coffee_shard_004.png',
        ):
            self.assertTrue((ROOT / 'PlutoTheCat/Resources' / resource).exists(), resource)

    def test_coffee_puddle_scans_its_own_room(self):
        mug = self.source('CoffeeMugItem.cs')
        # A mug thrown through a doorway slows enemies in the puddle's room, not the thrower's.
        self.assertIn('room = at.GetAbsoluteRoom();', mug)
        self.assertIn('ownerRoom = user != null ? user.CurrentRoom : null;', mug)
        self.assertIn('owner.CurrentRoom != ownerRoom', mug)
        self.assertNotIn('owner.CurrentRoom != room', mug)

    def test_catnip_zoomies_are_extendable(self):
        tricks = self.requires(
            'CatTricks.cs',
            'public static StatModifier AcquireSpeed(PlayerController p, float amount)',
            'public static void ReleaseSpeed(PlayerController p, StatModifier boost)',
            'PlutoConfig.MaxSpeedBonus - CurrentSpeedBonus(p)',
        )
        timed = tricks[tricks.index('public static IEnumerator TimedSpeed('):tricks.index('public static StatModifier AcquireSpeed(')]
        self.assertIn('AcquireSpeed(p, amount)', timed)
        self.assertIn('ReleaseSpeed(p, boost)', timed)

        catnip = self.requires(
            'CatnipPouchItem.cs',
            'private float zoomiesRemaining',
            'public bool ExtendZoomies(PlayerController user, float bonus)',
            'CatSetRules.ExtendRemaining(zoomiesRemaining, bonus,',
            'CatSetRules.ExtendDuration(m_activeDuration, bonus)',
            'buffed == user',
            'speedMod = CatTricks.AcquireSpeed(user, PlutoConfig.CatnipSpeedBonus)',
            'CatTricks.ReleaseSpeed(buffed, speedMod)', 'speedMod = null',
            'zoomiesRemaining = PlutoConfig.CatnipSeconds',
            'while (user != null && zoomiesRemaining > 0f)',
            'zoomiesRemaining -= dt',
            # Existing Catnip behaviour and numbers are kept.
            'PlutoConfig.CatnipFireRateMultiplier', 'PlutoVFX.Catnip', 'AfterImageTrailController',
            'CatnapSpeed = 0.8f', 'LeafInterval = 0.3f', 'PlutoConfig.CatnapSeconds',
            'PlutoSynergies.NipAndTuck', 'm_activeDuration = PlutoConfig.CatnipSeconds',
        )
        # One owned speed modifier and one loop: no detached TimedSpeed coroutine left running on drop.
        self.assertNotIn('TimedSpeed', catnip)
        self.assertEqual(1, catnip.count('while ('))
        # Inactive or wrong wearer is a no-op: rejection happens before any state is touched.
        extend = catnip[catnip.index('public bool ExtendZoomies('):]
        self.assertLess(extend.index('return false;'), extend.index('CatSetRules.ExtendRemaining('))
        # The catnap only starts after the (possibly extended) zoomies loop ends.
        loop = catnip.index('while (user != null && zoomiesRemaining > 0f)')
        end = catnip.index('EndZoomies();', loop)
        nap = catnip.index('napMod = CatItemKit.Mod(', end)
        self.assertLess(loop, end)
        self.assertLess(end, nap)
        stop = catnip[catnip.index('private void StopAll()'):]
        self.assertIn('EndZoomies();', stop)
        self.assertIn('EndNap();', stop)

        config = self.source('PlutoConfig.cs')
        for key, value in (('CatnipSeconds', '7f'), ('CatnipSpeedBonus', '2f'), ('CatnipFireRateMultiplier', '1.25f')):
            self.assertIn('public static float ' + key + ' = ' + value + ';', config)

    def test_round2_registration(self):
        plugin = self.source('Plugin.cs')
        synergies = self.source('PlutoSynergies.cs')

        # All five pickups: exact ID, fixed quality, normal loot pool, init step before synergies.
        roster = (
            ('SprayBottleGun.cs', 'SprayBottleGun', 'spray_bottle', 'C', 'spray bottle', 'Add'),
            ('FeatherTeaserGun.cs', 'FeatherTeaserGun', 'feather_teaser', 'B', 'feather teaser', 'Add'),
            ('ToiletPaperRollItem.cs', 'ToiletPaperRollItem', 'toilet_paper_roll', 'C', 'toilet paper roll', 'Init'),
            ('ConeOfShameItem.cs', 'ConeOfShameItem', 'cone_of_shame', 'B', 'cone of shame', 'Init'),
            ('CoffeeMugItem.cs', 'CoffeeMugItem', 'coffee_mug', 'C', 'coffee mug', 'Init'),
        )
        synergy_step = plugin.index('Step("synergies", PlutoSynergies.Init)')
        for filename, cls, slug, quality, step, init in roster:
            text = self.source(filename)
            self.assertEqual(1, text.count('public const string ID = "pluto:' + slug + '"'), filename)
            qualities = re.findall(r'\.quality = PickupObject\.ItemQuality\.(\w+);', text)
            self.assertEqual([quality], qualities, filename)
            self.assertNotIn('EXCLUDED', text, filename)
            if filename.endswith('Gun.cs'):
                self.assertEqual(1, text.count('ETGMod.Databases.Items.Add(gun, null, "ANY")'), filename)
            else:
                # Alexandria's SetupItem adds passive/active items to the normal loot pool.
                self.assertEqual(1, text.count('ItemBuilder.SetupItem(item, '), filename)
                self.assertNotIn('Databases.Items.Add', text, filename)
            call = 'Step("' + step + '", ' + cls + '.' + init + ');'
            self.assertEqual(1, plugin.count(call), call)
            self.assertLess(plugin.index(call), synergy_step, call)

        # Five exact synergy pairs, each registered once.
        for const, name, pair in (
            ('BathTime', 'Bath Time', 'SprayBottleGun.ID, WetFoodCanItem.ID'),
            ('Playtime', 'Playtime', 'FeatherTeaserGun.ID, BallOfYarnItem.ID'),
            ('Shredder', 'Shredder', 'ToiletPaperRollItem.ID, ScratchingPostItem.ID'),
            ('MatchingCones', 'Matching Cones', 'ConeOfShameItem.ID, CocoBlueItem.ID'),
            ('Espresso', 'Espresso', 'CoffeeMugItem.ID, CatnipPouchItem.ID'),
        ):
            self.assertIn('public const string ' + const + ' = "' + name + '";', synergies)
            self.assertEqual(1, synergies.count('Register(' + const + ','), const)
            self.assertEqual(1, synergies.count('Register(' + const + ', new List<string> { ' + pair + ' });'), const)

        # Generated resource manifest.
        res = ROOT / 'PlutoTheCat' / 'Resources'
        weapons = RES / 'WeaponCollection'
        for prefix, counts in (('pluto_spray_bottle_', {'idle': 1, 'fire': 2, 'reload': 3}),
                               ('pluto_feather_teaser_', {'idle': 1, 'charge': 1, 'fire': 1, 'empty': 1, 'return': 1})):
            for clip, count in counts.items():
                frames = sorted(weapons.glob(prefix + clip + '_[0-9][0-9][0-9].png'))
                self.assertEqual(count, len(frames), prefix + clip)
                for frame in frames:
                    self.assertTrue(frame.with_suffix('.jtk2d').exists(), frame.name + ' has no .jtk2d')
        for name in ('pluto_spray_mist_001', 'pluto_water_drop_001', 'pluto_water_splash_001',
                     'pluto_feather_lure_001', 'pluto_feather_lure_002', 'pluto_loose_feather_burst_001'):
            self.assertTrue((RES / 'ProjectileCollection' / (name + '.png')).exists(), name)
        self.assertFalse((RES / 'ProjectileCollection' / 'pluto_feather_lure_003.png').exists())
        for name in ('pluto_spray_bottle_idle_001', 'pluto_feather_teaser_idle_001'):
            path = RES / 'Ammonomicon Encounter Icon Collection' / (name + '.png')
            self.assertEqual((24, 32), png_size(path), name)
        for name in ('toilet_paper_roll_icon', 'cone_of_shame_icon', 'coffee_mug_icon'):
            self.assertEqual((16, 16), png_size(res / 'Items' / (name + '.png')), name)
        effects = res / 'Effects' / 'cat_set'
        for name in ('toilet_paper_streamer_001', 'toilet_paper_bits_001', 'toilet_paper_confetti_001',
                     'coffee_puddle_001'):
            self.assertTrue((effects / (name + '.png')).exists(), name)
        shards = [(effects / ('coffee_shard_00%d.png' % i)).read_bytes() for i in range(1, 5)]
        self.assertEqual(4, len(set(shards)), 'mug shards must be four distinct sprites')
        coco = res / 'Companions' / 'coco'
        for clip in ('idle', 'move', 'pet', 'block', 'ko'):
            knight = sorted((coco / ('knight_' + clip)).glob('*.png'))
            cone = sorted((coco / ('cone_' + clip)).glob('*.png'))
            self.assertTrue(knight, 'knight_' + clip)
            self.assertEqual(len(knight), len(cone), 'cone_' + clip)
            self.assertEqual([png_size(p) for p in knight], [png_size(p) for p in cone], 'cone_' + clip)
        for preview in ('cat-set-items-2190', 'spray-bottle-2190', 'feather-teaser-2190', 'coco-cones-2190'):
            self.assertTrue((ROOT / 'docs' / 'art-preview' / (preview + '.png')).exists(), preview)


def png_size(path):
    with open(str(path), 'rb') as handle:
        header = handle.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n', str(path)
    return struct.unpack('>II', header[16:24])


if __name__ == '__main__':
    unittest.main()
