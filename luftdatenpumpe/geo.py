# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import time
import logging
import Geohash
from copy import deepcopy
from munch import Munch
from dogpile.cache import make_region
from dogpile.cache.util import kwarg_function_key_generator
from geopy.geocoders import Nominatim

from . import __appname__ as APP_NAME
from . import __version__ as APP_VERSION


log = logging.getLogger(__name__)


# Configure cache for responses from Nominatim
nominatim_cache = make_region(
    function_key_generator=kwarg_function_key_generator) \
    .configure('dogpile.cache.redis')


# Configure Nominatim client
nominatim_user_agent = APP_NAME + '/' + APP_VERSION


# Maybe also add building, public_building
osm_address_fields = \
    [
        'continent',
        'country_code', 'country', 'state', 'state_district', 'county',
        'postcode',
        'post_box',
        'city', 'town', 'village', 'city_district', 'suburb', 'residential',
        'road', 'pedestrian', 'cycleway', 'footway', 'path',
        'house_number',

        'administrative', 'region', 'neighbourhood', 'industrial', 'common',
        'address26', 'address29',
    ]


def resolve_location(latitude=None, longitude=None, geohash=None, improve=True):

    # If only geohash is given, convert back to lat/lon.
    if latitude is None and longitude is None and geohash is not None:
        latitude, longitude = geohash_decode(geohash)

    # Run reverse geocoder.
    location = reverse_geocode(latitude, longitude).raw

    location = rebundle_location(location)

    return location


def rebundle_location(location):

    address = Munch()
    for field in osm_address_fields:
        if field in location['address']:
            address[field] = location['address'][field]
            del location['address'][field]

    address_more = Munch()
    for key, value in location['address'].items():
        address_more[key] = value

    del location['address']

    result = Munch(location)
    result.address = address

    if address_more:
        result.address_more = address_more

    return result


# Cache responses from Nominatim for 3 months
@nominatim_cache.cache_on_arguments(expiration_time=60 * 60 * 24 * 30 * 3)
def reverse_geocode(latitude, longitude):
    """
    Cache responses of the Nominatim reverse geocoding service.

    TODO:
    - Use a local version of Nomatim to get rid of
      the 1 request per second fair use policy.
      https://wiki.openstreetmap.org/wiki/Nominatim/Installation
    """

    log.debug('Decoding from Nominatim: {}'.format(locals()))

    try:
        # 2018-03-24
        # Nominatim expects the User-Agent as HTTP header otherwise it returns a HTTP-403.
        # This has been fixed in geopy-1.12.0.
        # https://operations.osmfoundation.org/policies/nominatim/
        # https://github.com/geopy/geopy/issues/185
        geolocator = Nominatim(user_agent=nominatim_user_agent)

        # FIXME: When using "HTTP_PROXY" from environment, use scheme='http'
        # export HTTP_PROXY=http://weather.hiveeyes.org:8912/
        # See also https://github.com/geopy/geopy/issues/263
        #geolocator = Nominatim(user_agent=nominatim_user_agent, scheme='http')

        position = (latitude, longitude)
        location = geolocator.reverse(position)

    except Exception as ex:
        name = ex.__class__.__name__
        log.error('Reverse geocoding failed: {}: {}. lat={}, lon={}'.format(name, ex, latitude, longitude))
        raise

    finally:
        # Obey to fair use policy (an absolute maximum of 1 request per second).
        # https://operations.osmfoundation.org/policies/nominatim/
        time.sleep(1)

    return location


def improve_location(location):
    """
    Heuristically compensate for anomalies from upstream OSM.

    FIXME:
    - [x] With a Berlin address, there is ``"state": null``?
    - [o] Modify suburb with things like "Fhain" => "Friedrichshain"
    - [o] Handle city==Rgbg

    TODO:
    - Get urban vs. rural sorted out

        1. country
        2. state
        3. "Überregional": "q-region"
            - county, state_district, state
        4. "Regional": "q-hood"
            - neighbourhood vs. quarter vs. residential vs. suburb vs. city_district vs. city vs. allotments

    - How to handle "building", "public_building", "residential", "pedestrian", "kindergarten", "clothes"?
    - Also check OSM place: https://wiki.openstreetmap.org/wiki/Key:place !!!
    """

    address = location.address


    # Improve `city` attribute.
    # If `city` is missing, try a number of alternative attributes.
    city_choices = [

        # Aliases
        'village', 'town', 'county', 'suburb', 'city_district',

        # Stadtstaat
        'state',
    ]
    if 'city' not in address:
        for fieldname in city_choices:
            if fieldname in address:
                address.city = address[fieldname]
                break

    # Improve Stadtstaat.
    # As the name of the city will already be propagated through the `state` attribute,
    # we can stuff more details on the lower level into the `city` attribute.
    if 'city' in address and 'state' in address and address.city == address.state:
        if 'city_district' in address:
            address.city = address.city_district
        elif 'suburb' in address:
            address.city = address.suburb

    # Reverse Stadtstaat improvements.
    # If `state` is missing, use `city` attribute for all known Stadtstaaten.
    # TODO: Add more? Hamburg, Bremen, etc.
    if 'state' not in address and address.city in ['Berlin']:
        address.state = address.city

    # Improve Stadtteil.
    # Use `residential` for missing `suburb` attribute.
    if 'suburb' not in address and 'residential' in address:
        address.suburb = address.residential

    # Be agnostic against road vs. path
    if 'road' not in address:
        road_choices = ['path', 'pedestrian', 'cycleway', 'footway']
        for fieldname in road_choices:
            if fieldname in address:
                address.road = address[fieldname]


def format_address(location):
    """
    The canonical station ``name`` attribute yields a more compact display
    name than that already provided by the upstream OSM ``display_name`` attribute.

    References
    ----------
    - https://github.com/OpenCageData/address-formatting
    - https://opencagedata.com/
    - https://openaddresses.io/
    - http://results.openaddresses.io/
    - https://github.com/DenisCarriere/geocoder-geojson

    """

    location = deepcopy(location)
    address = location.address

    # Uppercase `country_code`.
    address['country_code'] = address['country_code'].upper()

    # Clean up `county` field.
    blacklist = [
        # county
        'Landkreis', 'Kreis', 'Verwaltungsgemeinschaft',

        # suburb
        'Bezirksteil', 'Bezirk',
    ]
    blacklist_fields = ['county', 'suburb']
    for fieldname in blacklist_fields:
        if fieldname in address:
            for black in blacklist:
                if black in address[fieldname]:
                    address[fieldname] = address[fieldname].replace(black, '').strip()

    # Build display location from components.
    address_fields = ['road', 'suburb', 'city', 'county', 'state', 'country_code']
    address_parts = []
    for address_field in address_fields:
        if address_field in address:
            next_field = address[address_field]
            if address_parts and next_field == address_parts[-1]:
                continue
            address_parts.append(next_field)

    location_label = ', '.join(address_parts)
    return location_label


def geohash_encode(latitude, longitude):
    # https://en.wikipedia.org/wiki/Geohash
    # Eight characters should be fine
    geohash = Geohash.encode(float(latitude), float(longitude))
    #geohash = geohash[:8]
    return geohash


def geohash_decode(geohash):
    return Geohash.decode(geohash)
