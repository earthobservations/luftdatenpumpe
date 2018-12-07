# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging

from luftdatenpumpe.geo import resolve_location, improve_location, format_address

log = logging.getLogger(__name__)


def test_resolve_location():
    """
    Test reverse geocoding.
    """
    location = resolve_location(latitude=48.778, longitude=9.236)
    assert location.address.city == 'Stuttgart'
    assert location.address_more.building == 'Kulturhaus ARENA'

    # Test reverse geocoding by geohash.
    location = resolve_location(geohash="u0wt6pv2qqhz")
    assert location.address.state == 'Baden-Württemberg'


def test_format_address():
    """
    Test address formatting.
    """
    location = resolve_location(latitude=48.778, longitude=9.236)
    name = format_address(location)

    assert name == 'Ulmer Straße, Wangen, Stuttgart, Baden-Württemberg, DE'


def test_improved_city_alias():
    """
    Test heuristic OSM improvements re. ``city`` attribute.
    """

    location = resolve_location(latitude=48.578, longitude=9.18)
    improve_location(location)
    assert location.address.city == 'Pliezhausen'

    location = resolve_location(latitude=48.8, longitude=9.002)
    improve_location(location)
    assert location.address.city == 'Leonberg'


def test_improved_stadtstaat():
    """
    Test heuristic OSM improvements re. ``city`` attribute for Stadtstaaten.
    """

    location = resolve_location(latitude=53.112, longitude=8.896)
    improve_location(location)
    assert location.address.suburb == 'Horn-Lehe'
    assert location.address.city == 'Stadtbezirk Bremen-Ost'
    assert location.address.state == 'Bremen'
    name = format_address(location)
    assert name == 'Flemingstraße, Horn-Lehe, Stadtbezirk Bremen-Ost, Bremen, DE'

    location = resolve_location(latitude=52.544, longitude=13.374)
    improve_location(location)
    assert location.address.suburb == 'Gesundbrunnen'
    assert location.address.city == 'Berlin'
    assert location.address.state == 'Berlin'
    name = format_address(location)
    assert name == 'Gerichtstraße, Gesundbrunnen, Berlin, DE'


def test_improved_stadtteil():
    """
    Test heuristic OSM improvements re. `suburb` vs. `residential` attribute.
    """

    location = resolve_location(latitude=48.482, longitude=9.204)
    improve_location(location)
    assert location.address.suburb == 'Ringelbach'
    assert location.address.city == 'Reutlingen'
    assert location.address.state == 'Baden-Württemberg'

    name = format_address(location)
    assert name == 'Paul-Pfizer-Straße, Ringelbach, Reutlingen, Baden-Württemberg, DE'


def test_improved_residential_village():
    """
    This address has to use information from `residential` and `village` fields.
    """

    location = resolve_location(latitude=48.058, longitude=12.57)
    improve_location(location)
    #log.info(location)

    name = format_address(location)
    assert name == 'Trostberger Straße, Lengloh, Tacherting, Traunstein, Bayern, DE'


def test_improved_something():
    location = resolve_location(latitude=52.181, longitude=7.630)
    improve_location(location)
    #log.info(location)

    name = format_address(location)
    assert name == 'Holunderbusch, Saerbeck, Steinfurt, Nordrhein-Westfalen, DE'


def test_improved_road():
    """
    These addresses originally lack the `road` attribute.
    """

    # From `pedestrian` attribute
    location = resolve_location(latitude=48.774, longitude=9.174)
    improve_location(location)
    assert location.address.road == 'Königstraße'
    name = format_address(location)
    assert name == 'Königstraße, Stuttgart-Mitte, Stuttgart, Baden-Württemberg, DE'

    # From `cycleway` attribute
    location = resolve_location(latitude=48.194, longitude=11.548)
    improve_location(location)
    assert location.address.road == 'Lerchenauer Straße'
    name = format_address(location)
    assert name == 'Lerchenauer Straße, Hasenbergl-Lerchenau Ost, München, Bayern, DE'

    # From `path` attribute
    location = resolve_location(latitude=49.2, longitude=9.242)
    improve_location(location)
    assert location.address.road == 'Reutlinger Straße'
    name = format_address(location)
    assert name == 'Reutlinger Straße, Neckarsulm, Baden-Württemberg, DE'

    # From `footway` attribute
    location = resolve_location(latitude=48.702, longitude=9.126)
    improve_location(location)
    assert location.address.road == 'Hans-Holbein-Straße'
    name = format_address(location)
    assert name == 'Hans-Holbein-Straße, Leinfelden, Leinfelden-Echterdingen, Esslingen, Baden-Württemberg, DE'
