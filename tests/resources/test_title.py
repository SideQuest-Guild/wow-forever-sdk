from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_title(client: Client) -> None:
    index = client.titles.index()

    assert index.titles[0].id == 17
    assert index.titles[0].name == "Commander"


def test_get_reads_title_details(client: Client) -> None:
    title = client.titles.get(17)

    assert title.name == "Commander"
    assert title.gender_name.male == "Commander {name}"
    assert title.gender_name.female == "Commander {name}"
