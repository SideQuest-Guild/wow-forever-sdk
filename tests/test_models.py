"""Models must keep every field Battle.net sends.

Decoding skips undeclared fields, so a field Blizzard adds would vanish silently. This test decodes every recorded
fixture and names the path of any field a model drops. ``make audit-models`` runs the same check on every live
document.
"""

import re
from typing import Any

import msgspec
import pytest

from tests.conftest import FIXTURES, load_fixture
from wow import models

ROUTES: dict[str, Any] = {
    "dynamic/realm/index": models.RealmIndex,
    "dynamic/realm/{id}": models.Realm,
    "dynamic/region/index": models.RegionIndex,
    "dynamic/region/{id}": models.RegionInfo,
    "dynamic/search/realm": models.SearchPage[models.RealmSearchData],
    "dynamic/ruleset/index": models.RulesetIndex,
    "dynamic/ruleset/{id}": models.Ruleset,
    "profile/guild/{id}": models.Guild,
    "profile/guild/{id}/roster": models.GuildRoster,
    "profile/user/wow": models.AccountProfile,
    "profile/wow/character/{id}": models.CharacterProfile,
    "profile/wow/character/{id}/achievements": models.CharacterAchievements,
    "profile/wow/character/{id}/achievements/statistics": models.CharacterAchievementStatistics,
    "profile/wow/character/{id}/character-media": models.CharacterMedia,
    "profile/wow/character/{id}/collections": models.CharacterCollections,
    "profile/wow/character/{id}/collections/mounts": models.CharacterMounts,
    "profile/wow/character/{id}/collections/pets": models.CharacterPets,
    "profile/wow/character/{id}/collections/toys": models.CharacterToys,
    "profile/wow/character/{id}/collections/transmogs": models.CharacterTransmogs,
    "profile/wow/character/{id}/equipment": models.CharacterEquipment,
    "profile/wow/character/{id}/professions": models.CharacterProfessions,
    "profile/wow/character/{id}/pvp-summary": models.CharacterPvpSummary,
    "profile/wow/character/{id}/quests": models.CharacterQuests,
    "profile/wow/character/{id}/quests/completed": models.CharacterCompletedQuests,
    "profile/wow/character/{id}/reputations": models.CharacterReputations,
    "profile/wow/character/{id}/specializations": models.CharacterSpecializations,
    "profile/wow/character/{id}/statistics": models.CharacterStatistics,
    "profile/wow/character/{id}/status": models.CharacterStatus,
    "static/achievement-category/index": models.AchievementCategoryIndex,
    "static/achievement-category/{id}": models.AchievementCategory,
    "static/achievement/index": models.AchievementIndex,
    "static/achievement/{id}": models.Achievement,
    "static/creature-family/index": models.CreatureFamilyIndex,
    "static/creature-family/{id}": models.CreatureFamily,
    "static/creature-type/index": models.CreatureTypeIndex,
    "static/creature-type/{id}": models.CreatureType,
    "static/item-class/index": models.ItemClassIndex,
    "static/item-class/{id}": models.ItemClass,
    "static/item-set/index": models.ItemSetIndex,
    "static/item-set/{id}": models.ItemSet,
    "static/item/{id}": models.Item,
    "static/media/achievement/{id}": models.Media,
    "static/media/item/{id}": models.Media,
    "static/media/playable-class/{id}": models.Media,
    "static/media/playable-specialization/{id}": models.Media,
    "static/media/profession/{id}": models.Media,
    "static/media/recipe/{id}": models.Media,
    "static/mount/index": models.MountIndex,
    "static/mount/{id}": models.Mount,
    "static/pet/index": models.PetIndex,
    "static/pet/{id}": models.Pet,
    "static/playable-class/index": models.PlayableClassIndex,
    "static/playable-class/{id}": models.PlayableClass,
    "static/playable-race/index": models.PlayableRaceIndex,
    "static/playable-race/{id}": models.PlayableRace,
    "static/playable-specialization/index": models.PlayableSpecializationIndex,
    "static/playable-specialization/{id}": models.PlayableSpecialization,
    "static/power-type/index": models.PowerTypeIndex,
    "static/power-type/{id}": models.PowerType,
    "static/profession/index": models.ProfessionIndex,
    "static/profession/{id}": models.Profession,
    "static/profession/{id}/skill-tier/{id}": models.ProfessionSkillTier,
    "static/quest/area/index": models.QuestAreaIndex,
    "static/quest/area/{id}": models.QuestArea,
    "static/quest/category/index": models.QuestCategoryIndex,
    "static/quest/category/{id}": models.QuestCategory,
    "static/quest/type/index": models.QuestTypeIndex,
    "static/quest/type/{id}": models.QuestType,
    "static/quest/{id}": models.Quest,
    "static/recipe/{id}": models.Recipe,
    "static/reputation-faction/index": models.ReputationFactionIndex,
    "static/reputation-faction/{id}": models.ReputationFaction,
    "static/reputation-tiers/index": models.ReputationTierSetIndex,
    "static/reputation-tiers/{id}": models.ReputationTierSet,
    "static/search/item": models.SearchPage[models.ItemSearchData],
    "static/search/mount": models.SearchPage[models.MountSearchData],
    "static/talent-tree/index": models.TalentTreeIndex,
    "static/talent-tree/{id}/playable-specialization/{id}": models.TalentTree,
    "static/talent/index": models.TalentIndex,
    "static/talent/{id}": models.Talent,
    "static/title/index": models.TitleIndex,
    "static/title/{id}": models.Title,
    "static/toy/index": models.ToyIndex,
    "static/toy/{id}": models.Toy,
}
"""The model for each route, as ``{namespace kind}/{path}`` with ids replaced by ``{id}``."""

RECORDED = sorted(path.relative_to(FIXTURES).with_suffix("").as_posix() for path in FIXTURES.rglob("*.json"))


def route(name: str) -> str:
    """Turn ``static/item/19019`` into ``static/item/{id}``.

    Every path part with a digit in it is an id or a slug, and so is the part after ``character/`` or ``guild/``: a
    character's or a guild's slug is a name, such as ``evoke-saint``.
    """
    slugged = re.sub(r"(/(?:character|guild)/)[^/]+", r"\1{id}", name)
    return re.sub(r"(?<=/)[^/]*\d[^/]*", "{id}", slugged)


def api_path(name: str) -> tuple[str, str]:
    """Split ``static/item/19019`` into its namespace kind and its route, ``/data/wow/item/19019``.

    Profile documents about one character or account, ``profile/wow/...`` and ``profile/user/...``, live under
    ``/profile/`` instead.
    """
    kind, _, path = name.partition("/")
    return kind, f"/profile/{path}" if path.startswith(("wow/", "user/")) else f"/data/wow/{path}"


def dropped(sent: object, kept: object, path: str = "$") -> list[str]:
    """Paths in ``sent`` that ``kept`` lost or changed."""
    if isinstance(sent, dict) and isinstance(kept, dict):
        return [
            lost
            for key, value in sent.items()
            for lost in (dropped(value, kept[key], f"{path}.{key}") if key in kept else [f"{path}.{key}"])
        ]
    if isinstance(sent, list) and isinstance(kept, (list, tuple)) and len(sent) == len(kept):
        return [
            lost
            for index, pair in enumerate(zip(sent, kept, strict=True))
            for lost in dropped(*pair, f"{path}[{index}]")
        ]
    return [] if sent == kept else [path]


def test_every_route_has_fixtures_and_every_fixture_a_route() -> None:
    assert {route(name) for name in RECORDED} == ROUTES.keys()


@pytest.mark.parametrize("name", RECORDED)
def test_model_keeps_every_recorded_field(name: str) -> None:
    body = load_fixture(name)["body"]

    decoded = msgspec.json.decode(msgspec.json.encode(body), type=ROUTES[route(name)])

    assert dropped(body, msgspec.to_builtins(decoded)) == []


def test_a_new_field_is_reported_by_path() -> None:
    body = load_fixture("static/playable-class/1")["body"]
    body["power_type"]["color"] = "red"

    decoded = msgspec.json.decode(msgspec.json.encode(body), type=models.PlayableClass)

    assert dropped(body, msgspec.to_builtins(decoded)) == ["$.power_type.color"]
