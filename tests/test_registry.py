import pytest

from courtbeat.registry import REGISTRY, get_connector

from courtbeat.connectors.courts.washoe_district import WashoeDistrictConnector
from courtbeat.connectors.courts.clark_district import ClarkDistrictConnector
from courtbeat.connectors.courts.churchill_district import ChurchillDistrictConnector
from courtbeat.connectors.courts.churchill_justice import ChurchillJusticeConnector
from courtbeat.connectors.sheriff.churchill_sheriff import ChurchillSheriffConnector
from courtbeat.connectors.jails.washoe_jail import WashoeJailConnector


def test_registry_contains_expected_keys():
    expected = {
        "washoe_district",
        "clark_district",
        "churchill_district",
        "churchill_justice",
        "churchill_sheriff",
        "washoe_jail",
    }

    assert expected.issubset(REGISTRY.keys())


def test_registry_maps_to_correct_classes():
    assert REGISTRY["washoe_district"] is WashoeDistrictConnector
    assert REGISTRY["clark_district"] is ClarkDistrictConnector
    assert REGISTRY["churchill_district"] is ChurchillDistrictConnector
    assert REGISTRY["churchill_justice"] is ChurchillJusticeConnector
    assert REGISTRY["churchill_sheriff"] is ChurchillSheriffConnector
    assert REGISTRY["washoe_jail"] is WashoeJailConnector


def test_get_connector_instantiates_correct_class():
    conn = get_connector("washoe_district")
    assert isinstance(conn, WashoeDistrictConnector)

    conn = get_connector("clark_district")
    assert isinstance(conn, ClarkDistrictConnector)

    conn = get_connector("churchill_justice")
    assert isinstance(conn, ChurchillJusticeConnector)


def test_get_connector_raises_on_invalid_name():
    with pytest.raises(KeyError):
        get_connector("not_a_real_connector")
