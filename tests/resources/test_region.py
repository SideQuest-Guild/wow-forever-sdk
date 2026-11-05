from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_index_lists_the_host_region(client: Client) -> None:
    index = client.regions.index()

    assert len(index.regions) == 1
    assert index.regions[0].href.endswith("/data/wow/region/91?namespace=dynamic-forever-us")


def test_get_reads_region_details(client: Client) -> None:
    region = client.regions.get(91)

    assert region.id == 91
    assert region.name == "CAMWOW North America"
    assert region.tag == "US"
    assert region.patch_string == "1.60.1"
