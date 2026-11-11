"""Resource namespaces, such as the class behind ``client.items``, for type annotations and reference."""

from wow._async.resources.account import AsyncAccount
from wow._async.resources.achievement import AsyncAchievementCategories, AsyncAchievements
from wow._async.resources.auction import AsyncAuctions
from wow._async.resources.character import AsyncCharacters
from wow._async.resources.creature import AsyncCreatureFamilies, AsyncCreatureTypes
from wow._async.resources.guild import AsyncGuilds
from wow._async.resources.guild_crest import AsyncGuildCrests
from wow._async.resources.item import AsyncItemClasses, AsyncItems, AsyncItemSets
from wow._async.resources.mount import AsyncMounts
from wow._async.resources.pet import AsyncPets
from wow._async.resources.playable_class import AsyncPlayableClasses
from wow._async.resources.playable_race import AsyncPlayableRaces
from wow._async.resources.playable_specialization import AsyncPlayableSpecializations
from wow._async.resources.power_type import AsyncPowerTypes
from wow._async.resources.profession import AsyncProfessions
from wow._async.resources.quest import AsyncQuestAreas, AsyncQuestCategories, AsyncQuests, AsyncQuestTypes
from wow._async.resources.realm import AsyncRealms
from wow._async.resources.recipe import AsyncRecipes
from wow._async.resources.region import AsyncRegions
from wow._async.resources.reputation import AsyncReputationFactions, AsyncReputationTiers
from wow._async.resources.ruleset import AsyncRulesets
from wow._async.resources.talent import AsyncTalents, AsyncTalentTrees
from wow._async.resources.title import AsyncTitles
from wow._async.resources.toy import AsyncToys
from wow._sync.resources.account import Account
from wow._sync.resources.achievement import AchievementCategories, Achievements
from wow._sync.resources.auction import Auctions
from wow._sync.resources.character import Characters
from wow._sync.resources.creature import CreatureFamilies, CreatureTypes
from wow._sync.resources.guild import Guilds
from wow._sync.resources.guild_crest import GuildCrests
from wow._sync.resources.item import ItemClasses, Items, ItemSets
from wow._sync.resources.mount import Mounts
from wow._sync.resources.pet import Pets
from wow._sync.resources.playable_class import PlayableClasses
from wow._sync.resources.playable_race import PlayableRaces
from wow._sync.resources.playable_specialization import PlayableSpecializations
from wow._sync.resources.power_type import PowerTypes
from wow._sync.resources.profession import Professions
from wow._sync.resources.quest import QuestAreas, QuestCategories, Quests, QuestTypes
from wow._sync.resources.realm import Realms
from wow._sync.resources.recipe import Recipes
from wow._sync.resources.region import Regions
from wow._sync.resources.reputation import ReputationFactions, ReputationTiers
from wow._sync.resources.ruleset import Rulesets
from wow._sync.resources.talent import Talents, TalentTrees
from wow._sync.resources.title import Titles
from wow._sync.resources.toy import Toys

__all__ = [
    "Account",
    "AchievementCategories",
    "Achievements",
    "AsyncAccount",
    "AsyncAchievementCategories",
    "AsyncAchievements",
    "AsyncAuctions",
    "AsyncCharacters",
    "AsyncCreatureFamilies",
    "AsyncCreatureTypes",
    "AsyncGuildCrests",
    "AsyncGuilds",
    "AsyncItemClasses",
    "AsyncItemSets",
    "AsyncItems",
    "AsyncMounts",
    "AsyncPets",
    "AsyncPlayableClasses",
    "AsyncPlayableRaces",
    "AsyncPlayableSpecializations",
    "AsyncPowerTypes",
    "AsyncProfessions",
    "AsyncQuestAreas",
    "AsyncQuestCategories",
    "AsyncQuestTypes",
    "AsyncQuests",
    "AsyncRealms",
    "AsyncRecipes",
    "AsyncRegions",
    "AsyncReputationFactions",
    "AsyncReputationTiers",
    "AsyncRulesets",
    "AsyncTalentTrees",
    "AsyncTalents",
    "AsyncTitles",
    "AsyncToys",
    "Auctions",
    "Characters",
    "CreatureFamilies",
    "CreatureTypes",
    "GuildCrests",
    "Guilds",
    "ItemClasses",
    "ItemSets",
    "Items",
    "Mounts",
    "Pets",
    "PlayableClasses",
    "PlayableRaces",
    "PlayableSpecializations",
    "PowerTypes",
    "Professions",
    "QuestAreas",
    "QuestCategories",
    "QuestTypes",
    "Quests",
    "Realms",
    "Recipes",
    "Regions",
    "ReputationFactions",
    "ReputationTiers",
    "Rulesets",
    "TalentTrees",
    "Talents",
    "Titles",
    "Toys",
]
