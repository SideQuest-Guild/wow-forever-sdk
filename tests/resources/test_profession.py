from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_profession(client: Client) -> None:
    index = client.professions.index()

    assert len(index.professions) == 13
    assert index.professions[0].name == "Tailoring"


def test_get_reads_profession_details(client: Client) -> None:
    tailoring = client.professions.get(197)

    assert tailoring.name == "Tailoring"
    assert tailoring.type.type == "PRIMARY"
    assert tailoring.type.name == "Primary"
    assert tailoring.media.id == 197
    assert len(tailoring.skill_tiers) == 1
    assert tailoring.skill_tiers[0].name == "Tailoring"
