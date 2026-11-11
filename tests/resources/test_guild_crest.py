from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_every_emblem_border_and_color(client: Client) -> None:
    index = client.guild_crests.index()

    assert len(index.emblems) == 196
    assert index.emblems[0].id == 0
    assert index.emblems[0].media.id == 0

    assert len(index.borders) == 6
    assert index.borders[0].id == 0
    assert index.borders[0].media.id == 0

    assert len(index.colors.emblems) == 17
    assert index.colors.emblems[0].id == 0
    assert index.colors.emblems[0].rgba is not None
    assert index.colors.emblems[0].rgba.r == 103
    assert index.colors.emblems[0].rgba.g == 0
    assert index.colors.emblems[0].rgba.b == 33
    assert index.colors.emblems[0].rgba.a == 1.0

    assert len(index.colors.borders) == 17
    assert len(index.colors.backgrounds) == 51


def test_border_media_reads_the_border_image(client: Client) -> None:
    media = client.guild_crests.border_media(0)

    assert media.id == 0
    assert media.assets[0].key == "image"
    assert "/guild/tabards/border_" in media.assets[0].value


def test_emblem_media_reads_the_emblem_image(client: Client) -> None:
    media = client.guild_crests.emblem_media(0)

    assert media.id == 0
    assert media.assets[0].key == "image"
    assert "/guild/tabards/emblem_" in media.assets[0].value
