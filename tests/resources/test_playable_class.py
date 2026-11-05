from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_the_nine_forever_classes(client: Client) -> None:
    index = client.playable_classes.index()

    assert len(index.classes) == 9
    assert index.classes[0].name == "Warrior"


def test_get_reads_class_details(client: Client) -> None:
    warrior = client.playable_classes.get(1)

    assert warrior.name == "Warrior"
    assert warrior.gender_name.female == "Warrior"
    assert warrior.power_type.name == "Rage"
    assert [spec.name for spec in warrior.specializations] == ["Arms", "Fury", "Protection"]


def test_media_points_at_the_forever_render_path(client: Client) -> None:
    media = client.playable_classes.media(1)

    assert media.assets[0].key == "icon"
    assert "/forever-us/" in media.assets[0].value
