# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import os
import time
import logging
import appdirs
import Geohash
from beaker.cache import CacheManager
from geopy.geocoders import Nominatim

from . import __appname__ as APP_NAME
from . import __version__ as APP_VERSION


log = logging.getLogger(__name__)


# Configure cache for responses from Nominatim
nominatim_cache_path = os.path.join(appdirs.user_cache_dir(appname='luftdaten.info', appauthor=False), 'nominatim')
nominatim_cache_options = {
    'type': 'file',
    'data_dir': os.path.join(nominatim_cache_path, 'data'),
    'lock_dir': os.path.join(nominatim_cache_path, 'lock'),
}
nominatim_cache = CacheManager(**nominatim_cache_options)


# Configure Nominatim client
nominatim_user_agent = APP_NAME + '/' + APP_VERSION


# Cache responses from Nominatim for 3 months
@nominatim_cache.cache(expire=60 * 60 * 24 * 30 * 3)
def reverse_geocode(latitude=None, longitude=None, geohash=None):
    """
    # Done: Use memoization! Maybe cache into MongoDB as well using Beaker.
    # TODO: Or use a local version of Nomatim: https://wiki.openstreetmap.org/wiki/Nominatim/Installation
    """

    log.info('Decoding from Nominatim: {}'.format(locals()))

    if geohash is not None:
        latitude, longitude = geohash_decode(geohash)

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
        #geolocator = Nominatim(user_agent=APP_NAME + '/' + APP_VERSION, scheme='http')

        position_string = '{}, {}'.format(float(latitude), float(longitude))
        location = geolocator.reverse(position_string)

    except Exception as ex:
        name = ex.__class__.__name__
        log.error('Reverse geocoding failed: {}: {}. lat={}, lon={}, hash={}'.format(name, ex, latitude, longitude, geohash))
        raise

    finally:
        # Obey to fair use policy (an absolute maximum of 1 request per second).
        # https://operations.osmfoundation.org/policies/nominatim/
        time.sleep(1)

    #log.debug(u'Reverse geocoder result: {}'.format(pformat(location.raw)))

    # Be agnostic against city vs. village
    # TODO: Handle Rgbg
    address = location.raw['address']
    if 'city' not in address:
        if 'village' in address:
            address['city'] = address['village']
        elif 'town' in address:
            address['city'] = address['town']
        elif 'county' in address:
            address['city'] = address['county']
        elif 'suburb' in address:
            address['city'] = address['suburb']
        elif 'city_district' in address:
            address['city'] = address['city_district']

        # Stadtstaat FTW!
        elif 'state' in address:
            address['city'] = address['state']

    # Add more convenience for handling Stadtstaaten
    if 'city' in address and 'state' in address and address['city'] == address['state']:
        if 'suburb' in address:
            address['city'] = address['suburb']
        elif 'city_district' in address:
            address['city'] = address['city_district']

    # Stadtteil FTW
    if 'suburb' not in address and 'residential' in address:
        address['suburb'] = address['residential']

    """
    Get this sorted: https://wiki.openstreetmap.org/wiki/Key:place !!!
    Get urban vs. rural sorted out

    1. country
    2. state
    3. "Überregional": "q-region"
        - county, state_district, state
    4. "Regional": "q-hood"
        - neighbourhood vs. quarter vs. residential vs. suburb vs. city_district vs. city vs. allotments

    How to handle "building", "public_building", "residential", "pedestrian", "kindergarten", "clothes"?
    """

    # Be agnostic against road vs. path
    if 'road' not in address:
        road_choices = ['path', 'pedestrian', 'cycleway', 'footway']
        for field in road_choices:
            if field in address:
                address['road'] = address[field]

    # Uppercase country code
    address['country_code'] = address['country_code'].upper()

    # Build display location from components
    # TODO: Modify suburb with things like "Fhain" => "Friedrichshain"
    address_fields = ['road', 'suburb', 'city', 'state', 'country_code']
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
    geohash = geohash[:8]
    return geohash


def geohash_decode(geohash):
    return Geohash.decode(geohash)
