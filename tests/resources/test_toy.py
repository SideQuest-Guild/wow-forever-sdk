from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_toy(client: Client) -> None:
    index = client.toys.index()

    assert index.toys[0].id == 1692
    assert index.toys[0].name == "Centaur Banner Deployment Device"


def test_get_reads_toy_details(client: Client) -> None:
    toy = client.toys.get(1692)

    assert toy.item.name == "Centaur Banner Deployment Device"
    assert toy.media.id == 269900
    assert toy.source.type == "OTHER"
    assert toy.source.name == "Other"
    assert toy.should_exclude_if_uncollected is True
