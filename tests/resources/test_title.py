from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_title(client: Client) -> None:
    index = client.titles.index()

    assert index.titles[0].id == 30
    assert index.titles[0].name == "Champion"


def test_get_reads_title_details(client: Client) -> None:
    title = client.titles.get(30)

    assert title.name == "Champion"
    assert title.gender_name.male == "Champion {name}"
    assert title.gender_name.female == "Champion {name}"
