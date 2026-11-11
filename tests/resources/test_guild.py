from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_get_reads_a_guild_by_slug(client: Client, battlenet: respx.MockRouter) -> None:
    guild = client.guilds.get("SideQuest")

    assert (guild.id, guild.name, guild.slug) == (228203, "SideQuest", "sidequest")
    assert guild.faction.type == "ALLIANCE"
    assert guild.ruleset.name == "Normal"
    assert guild.member_count == 26
    assert battlenet["api"].calls.last.request.url.params["namespace"] == "profile-forever-us"


def test_roster_lists_members_by_rank(client: Client) -> None:
    roster = client.guilds.roster("sidequest")

    assert roster.guild.id == 228203
    guild_master = next(member for member in roster.members if member.rank == 0)
    assert guild_master.character.slug == "legs-behindhead"
    assert (guild_master.character.name, guild_master.character.surname) == ("Legs", "Behindhead")
    assert guild_master.character.playable_class.id == 2
    assert guild_master.character.faction.type == "ALLIANCE"
    assert len(roster.members) == 26
