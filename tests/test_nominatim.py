# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging

from luftdatenpumpe.geo import format_address, improve_location, resolve_location

log = logging.getLogger(__name__)


def test_resolve_location_latlon():
    """
    Test reverse geocoding with latitude/longitude.
    """
    location = resolve_location(latitude=48.778, longitude=9.236)
    assert location.address.city == "Stuttgart"
    assert location.address_more.building == "Kulturhaus ARENA"


def test_resolve_location_geohash():
    """
    Test reverse geocoding with geohash.
    """
    location = resolve_location(geohash="u0wt6pv2qqhz")
    assert location.address.state == "Baden-Württemberg"


def test_improve_location():
    """
    Test reverse geocoding with heuristic improvements.
    """
    location = resolve_location(latitude=48.778, longitude=9.236)
    improve_location(location)
    assert location.address.city == "Stuttgart"
    assert location.address_more.building == "Kulturhaus ARENA"


def test_format_address():
    """
    Test address formatting with heuristic improvements.
    """
    location = resolve_location(latitude=48.778, longitude=9.236)
    improve_location(location)
    name = format_address(location)

    assert name == "Ulmer Straße, Wangen, Stuttgart, Baden-Württemberg, DE"


def test_city_missing():
    """
    Test heuristic OSM improvements re. ``city`` attribute.
    """

    location = resolve_location(latitude=48.578, longitude=9.18)
    improve_location(location)
    assert location.address.city == "Gniebel"

    location = resolve_location(latitude=48.8, longitude=9.002)
    improve_location(location)
    assert location.address.city == "Leonberg"

    location = resolve_location(latitude=24.074, longitude=120.34)
    improve_location(location)
    assert location.address.city == "南投縣"


def test_stadtstaat():
    """
    Test heuristic OSM improvements re. ``city`` attribute for Stadtstaaten.
    """

    location = resolve_location(latitude=53.112, longitude=8.896)
    improve_location(location)
    assert location.address.suburb == "Horn-Lehe"
    assert location.address.city_district == "Bremen-Ost"
    assert location.address.city == "Bremen"
    assert location.address.state == "Bremen"
    name = format_address(location)
    assert name == "Flemingstraße, Horn-Lehe, Bremen-Ost, Bremen, DE"

    location = resolve_location(latitude=52.544, longitude=13.374)
    improve_location(location)
    assert location.address.suburb == "Gesundbrunnen"
    assert location.address.city_district == "Mitte"
    assert location.address.city == "Berlin"
    assert location.address.state == "Berlin"
    name = format_address(location)
    assert name == "Gerichtstraße, Gesundbrunnen, Mitte, Berlin, DE"

    location = resolve_location(latitude=53.448, longitude=10.228)
    improve_location(location)
    assert location.address.suburb == "Curslack"
    assert location.address.city_district == "Curslack"
    assert location.address.city == "Hamburg"
    assert location.address.state == "Hamburg"
    name = format_address(location)
    assert name == "Curslacker Deich, Curslack, Hamburg, DE"


def test_stadtteil():
    """
    Test heuristic OSM improvements re. `suburb` vs. `residential` attribute.
    """

    location = resolve_location(latitude=48.482, longitude=9.203)
    improve_location(location)
    assert location.address.suburb == "Ringelbach"
    assert location.address.city == "Reutlingen"
    assert location.address.state == "Baden-Württemberg"

    name = format_address(location)

    # Test is flaky in DE vs. US (2022-08-03).
    # https://github.com/earthobservations/luftdatenpumpe/runs/7650240048
    assert name in [
        "Albrechtstraße, Ringelbach, Reutlingen, Baden-Württemberg, DE",
        "Paul-Pfizer-Straße, Ringelbach, Reutlingen, Baden-Württemberg, DE",
    ]


def test_residential_village():
    """
    This address has to use information from `residential` and `village` fields.
    """

    location = resolve_location(latitude=48.058, longitude=12.57)
    improve_location(location)
    # log.info(location)

    name = format_address(location)
    assert name == "Trostberger Straße, Lengloh, Traunstein, Bayern, DE"


def test_something():
    location = resolve_location(latitude=52.181, longitude=7.630)
    improve_location(location)
    # log.info(location)

    name = format_address(location)
    assert name == "Holunderbusch, Saerbeck, Steinfurt, Nordrhein-Westfalen, DE"


def test_road_missing():
    """
    These addresses originally lack the `road` attribute.
    """

    # From `pedestrian` attribute
    location = resolve_location(latitude=48.774, longitude=9.174)
    improve_location(location)
    assert location.address.road == "Königstraße"
    name = format_address(location)
    assert name == "Königstraße, Stuttgart-Mitte, Stuttgart, Baden-Württemberg, DE"

    # From `cycleway` attribute
    location = resolve_location(latitude=48.194, longitude=11.548)
    improve_location(location)
    assert location.address.road == "Lerchenauer Straße"
    name = format_address(location)
    assert name == "Lerchenauer Straße, Hasenbergl-Lerchenau Ost, Feldmoching-Hasenbergl, München, Bayern, DE"

    # From `path` attribute
    location = resolve_location(latitude=49.2, longitude=9.242)
    improve_location(location)
    assert location.address.road == "Reutlinger Straße"
    name = format_address(location)
    assert name == "Reutlinger Straße, Amorbach, Heilbronn, Baden-Württemberg, DE"

    # From `footway` attribute
    location = resolve_location(latitude=48.702, longitude=9.126)
    improve_location(location)
    assert location.address.road == "Hans-Holbein-Straße"
    name = format_address(location)
    assert name == "Hans-Holbein-Straße, Oberaichen, Esslingen, Baden-Württemberg, DE"

    # From `house_number` attribute
    location = resolve_location(latitude=42.734, longitude=23.308)
    improve_location(location)
    assert location.address.road == "\u0431\u043b.402"
    name = format_address(location)
    assert name == "бл.402, ж.к. Надежда 4, Надежда, София, София-град, BG"


def test_road_unknown():
    """
    Road unknown.
    """

    # From `neighbourhood` attribute (ex).
    location = resolve_location(latitude=27.222, longitude=78.01)
    improve_location(location)
    assert location.address.road == "Unknown Road"
    name = format_address(location)
    assert name == "Civil Lines, Agra, Uttar Pradesh, IN"

    # Unknown road.
    location = resolve_location(latitude=49.342, longitude=8.146)
    improve_location(location)
    assert location.address.road == "Unknown Road"
    name = format_address(location)
    assert name == "Neustadt an der Weinstraße, Rheinland-Pfalz, DE"


def test_city_district_vs_suburb():
    """
    Check priority control of `city_district` vs. `suburb`.
    I.e. use `"city_district": "Friedrichshain-Kreuzberg"` over `"suburb": "Fhain"`.
    """

    location = resolve_location(latitude=52.518, longitude=13.442)
    improve_location(location)
    name = format_address(location)
    assert name == "Weidenweg, Friedrichshain, Friedrichshain-Kreuzberg, Berlin, DE"


def test_city_patches():
    """
    Check patched `city` attribute,
    I.e. use `"city": "Regensburg"` over `"city": "Rgbg"`.
    """

    location = resolve_location(latitude=49.006, longitude=12.104)
    improve_location(location)
    assert location.address.city == "Regensburg"
    name = format_address(location)
    assert name == "Regerstraße, Galgenberg, Regensburg, Bayern, DE"


def test_country_patches():
    """
    Fix `"country": "RP"` to `"country": "Poland"`.
    """

    location = resolve_location(latitude=51.72, longitude=19.48)
    improve_location(location)
    assert location.address.country == "Poland"
    name = format_address(location)
    assert name == "Rentowna, Górna, Łódź-Górna, Łódź, województwo łódzkie, PL"

    location = resolve_location(latitude=19.806, longitude=-70.704)
    improve_location(location)
    assert location.address.country == "Dominican Republic"
    name = format_address(location)
    assert name == "Calle Guayacanes, Costámbar, Puerto Plata, DO"


def test_taiwan_poor():
    """
    LDI station #187 does not have good reverse geocoding information.
    """

    location = resolve_location(latitude=24.074, longitude=120.34)
    improve_location(location)
    assert location.address.country_code == "TW"
    assert location.address.country == "臺灣"
    name = format_address(location)
    assert name == "南投縣, 臺灣省, TW"
