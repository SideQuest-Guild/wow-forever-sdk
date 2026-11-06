from typing import TYPE_CHECKING

import pytest

from wow import NotFoundError

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_get_reads_the_summary_with_an_app_token(client: Client, battlenet: respx.MockRouter) -> None:
    evoke = client.characters.get("evoke-saint")

    assert (evoke.id, evoke.name, evoke.surname) == (8651436, "Evoke", "Saint")
    assert evoke.name_search == "Evoke Saint"
    assert evoke.character_class.name == "Hunter"
    assert evoke.race.name == "Troll"
    assert evoke.faction.type == "HORDE"
    assert evoke.level == 21
    assert evoke.ruleset.name == "Normal"
    assert evoke.guild is not None
    assert evoke.guild.slug == "fuzion"
    assert evoke.hunter_pets is not None
    assert evoke.equipment.href.endswith("/profile/wow/character/evoke-saint/equipment?namespace=profile-forever-us")
    request = battlenet["api"].calls.last.request
    assert request.url.params["namespace"] == "profile-forever-us"
    assert request.headers["Authorization"] == "Bearer app-token"


def test_a_slug_in_any_case_reads_the_same_character(client: Client) -> None:
    assert client.characters.get("Evoke-Saint").id == client.characters.get("evoke-saint").id


def test_only_hunters_link_to_pets(client: Client) -> None:
    assert client.characters.get("terrorskull-gloomstep").hunter_pets is None


def test_the_slug_stays_one_path_segment(client: Client, battlenet: respx.MockRouter) -> None:
    with pytest.raises(NotFoundError):
        client.characters.equipment("evoke-saint/../../guild/sidequest")

    request = battlenet["api"].calls.last.request
    assert request.url.raw_path.startswith(
        b"/profile/wow/character/evoke-saint%2F..%2F..%2Fguild%2Fsidequest/equipment?"
    )


def test_status_reports_whether_the_character_exists(client: Client) -> None:
    status = client.characters.status("evoke-saint")

    assert (status.id, status.is_valid) == (8651436, True)


def test_media_lists_rendered_images(client: Client) -> None:
    media = client.characters.media("terrorskull-gloomstep")

    assert [asset.key for asset in media.assets] == ["main-raw", "main-sd-raw", "avatar", "avatar-sd"]
    assert media.character.slug == "terrorskull-gloomstep"


def test_media_is_not_found_until_battlenet_renders_it(client: Client) -> None:
    with pytest.raises(NotFoundError):
        client.characters.media("vaelun-skyrend")


def test_equipment_reads_tooltips_slots_and_enchantments(client: Client) -> None:
    equipment = client.characters.equipment("evoke-saint")

    chest = next(item for item in equipment.equipped_items if item.slot.type == "CHEST")
    assert chest.name == "Tribal Vest"
    assert chest.quantity == 1
    assert chest.enchantments[0].display_string == "Enchanted: Stamina +1 and Armor +8"
    assert chest.enchantments[0].source_item is not None
    assert chest.enchantments[0].source_item.name == "Light Armor Kit"
    assert chest.enchantments[0].enchantment_slot.type == "PERMANENT"
    ammo = equipment.equipped_items[-1]
    assert (ammo.slot.type, ammo.name, ammo.quantity) == ("AMMO", "Sharp Arrow", None)


def test_a_temporary_imbue_has_no_slot_type(client: Client) -> None:
    equipment = client.characters.equipment("daribow-thaumaturge")

    staff = next(item for item in equipment.equipped_items if item.slot.type == "MAIN_HAND")
    imbue = staff.enchantments[0]
    assert imbue.source_item is not None
    assert (imbue.display_string, imbue.source_item.name) == ("Lesser Flame", "Scroll of Imbue Lesser Flame")
    assert (imbue.enchantment_slot.id, imbue.enchantment_slot.type) == (8, None)


def test_a_spell_imbue_has_no_source_item(client: Client) -> None:
    equipment = client.characters.equipment("vaelun-skyrend")

    weapon = next(item for item in equipment.equipped_items if item.slot.type == "MAIN_HAND")
    imbue = weapon.enchantments[0]
    assert (imbue.display_string, imbue.source_item) == ("Rockbiter 2", None)


def test_equipment_reads_transmogs(client: Client) -> None:
    equipment = client.characters.equipment("monnick-mortis")

    chest = next(item for item in equipment.equipped_items if item.slot.type == "CHEST")
    assert chest.transmog is not None
    assert (chest.transmog.item.name, chest.transmog.item_modified_appearance_id) == (
        "Shen'dorei Skyseer's Robe",
        307678,
    )
    assert chest.transmog.second_item is None
    shoulders = next(item for item in equipment.equipped_items if item.slot.type == "SHOULDER")
    assert shoulders.transmog is not None
    assert shoulders.transmog.second_item is not None
    assert shoulders.transmog.second_item.name == "Shen'dorei Skyseer's Pauldrons"


def test_equipment_reads_which_set_pieces_and_bonuses_are_active(client: Client) -> None:
    rotmender = client.characters.equipment("sliding-door").equipped_item_sets[0]

    assert rotmender.display_string == "Rotmender's Raiment (4/5)"
    assert [piece.is_equipped for piece in rotmender.items] == [True, True, True, False, True]
    assert [(effect.required_count, effect.is_active) for effect in rotmender.effects] == [
        (2, True),
        (3, True),
        (4, True),
        (5, False),
    ]


def test_statistics_read_the_stats_sheet(client: Client) -> None:
    stats = client.characters.statistics("evoke-saint")

    assert stats.health == 542
    assert stats.power_type.name == "Mana"
    assert (stats.agility.base, stats.agility.effective) == (51, 75)
    assert stats.melee_crit.value == pytest.approx(3.7075)
    assert stats.speed.rating_normalized == 0
    assert stats.defense is not None
    assert stats.defense.effective == 88
    assert stats.ranged_attack_power == 172


def test_a_sheet_written_before_the_update_reads_without_the_new_stats(client: Client) -> None:
    stats = client.characters.statistics("daribow-thaumaturge")

    assert (stats.defense, stats.melee_hit, stats.movement_speed) == (None, None, None)
    assert stats.speed.value is None


def test_specializations_read_learned_talents(client: Client) -> None:
    groups = client.characters.specializations("evoke-saint").specialization_groups

    assert groups[0].is_active
    beast_mastery = groups[0].specializations[0]
    assert (beast_mastery.specialization_name, beast_mastery.spent_points) == ("Beast Mastery", 12)
    talent = beast_mastery.talents[0]
    assert (talent.talent.name, talent.talent_rank) == ("Deadly Aspects", 5)
    assert talent.spell_tooltip.spell.id == 19552


def test_professions_read_skill_and_known_recipes(client: Client) -> None:
    professions = client.characters.professions("evoke-saint")

    leatherworking = professions.primaries[0]
    assert leatherworking.profession.name == "Leatherworking"
    tier = leatherworking.tiers[0]
    assert (tier.skill_points, tier.max_skill_points, len(tier.known_recipes)) == (52, 150, 23)
    assert [secondary.profession.name for secondary in professions.secondaries] == ["Cooking", "Fishing", "First Aid"]


def test_reputations_read_standing(client: Client) -> None:
    everlook = client.characters.reputations("evoke-saint").reputations[0]

    assert everlook.faction.name == "Everlook"
    assert (everlook.standing.name, everlook.standing.value, everlook.standing.max) == ("Neutral", 1865, 3000)


def test_pvp_summary_reads_kills_and_rank(client: Client) -> None:
    pvp = client.characters.pvp_summary("evoke-saint")

    assert (pvp.honorable_kills, pvp.pvp_rank) == (0, 0)
    assert pvp.pvp_map_statistics == ()


def test_pvp_summary_reads_each_battleground_record(client: Client) -> None:
    warsong = client.characters.pvp_summary("drakaus-warrior").pvp_map_statistics[0]

    assert warsong.world_map.name == "Warsong Gulch"
    assert (warsong.match_statistics.played, warsong.match_statistics.won) == (1, 1)


def test_achievements_read_progress_and_recent_events(client: Client) -> None:
    achievements = client.characters.achievements("evoke-saint")

    assert achievements.total_quantity == 1
    durotar = next(entry for entry in achievements.achievements if entry.completed_timestamp is not None)
    assert durotar.achievement.name == "Explore Durotar"
    assert len(durotar.criteria.child_criteria) == 11
    assert achievements.recent_events[0].achievement.id == 728
    assert achievements.category_progress[0].category.name == "Adventure"


def test_achievement_statistics_read_nested_categories(client: Client) -> None:
    character = client.characters.achievement_statistics("evoke-saint").categories[0]

    assert character.name == "Character"
    consumables = character.sub_categories[0]
    assert consumables.name == "Consumables"
    assert (consumables.statistics[0].name, consumables.statistics[0].quantity) == ("Health potions consumed", 12)


def test_quests_read_the_log_and_completed_quests(client: Client) -> None:
    quests = client.characters.quests("evoke-saint")
    completed = client.characters.completed_quests("evoke-saint")

    assert len(quests.in_progress) == 14
    assert quests.completed.href.endswith("/evoke-saint/quests/completed?namespace=profile-forever-us")
    assert (len(completed.quests), completed.quests[0].name) == (166, "Chen's Empty Keg")


def test_collections_read_mounts_pets_toys_and_appearances(client: Client) -> None:
    slug = "terrorskull-gloomstep"

    links = client.characters.collections(slug)
    mounts = client.characters.mounts(slug)
    pets = client.characters.pets(slug)
    toys = client.characters.toys(slug)
    transmogs = client.characters.transmogs(slug)

    assert links.mounts.href.endswith(f"/{slug}/collections/mounts?namespace=profile-forever-us")
    assert [mount.mount.name for mount in mounts.mounts] == [
        "Cerulean Prideclaw",
        "Veteran Adventurer's Loyal Companion",
    ]
    assert (pets.pets[0].species.name, pets.pets[0].quality.type) == ("Zergling", "UNCOMMON")
    assert [toy.toy.id for toy in toys.toys] == [1761, 1792]
    assert (transmogs.slots[0].slot.type, len(transmogs.slots[0].appearances)) == ("HEAD", 4)


def test_collections_mark_favorites(client: Client) -> None:
    assert all(mount.is_favorite for mount in client.characters.mounts("vaelun-skyrend").mounts)
    assert client.characters.toys("vaelun-skyrend").toys[0].is_favorite
    assert not client.characters.mounts("terrorskull-gloomstep").mounts[0].is_favorite
    pets = client.characters.pets("aille-mistgaze").pets
    assert [pet.species.name for pet in pets if pet.is_favorite] == ["Mini Diablo"]


def test_an_empty_collection_reads_as_empty(client: Client) -> None:
    assert client.characters.mounts("evoke-saint").mounts == ()
