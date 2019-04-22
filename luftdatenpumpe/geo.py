# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import re
import time
import logging
import geohash2
from copy import deepcopy
from munch import Munch
from dogpile.cache import make_region
from dogpile.cache.util import kwarg_function_key_generator, to_list
from geopy.geocoders import Nominatim

from luftdatenpumpe.util import invalidate_dogpile_cache
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


def resolve_location(latitude=None, longitude=None, geohash=None, country_code=None, improve=True):

    # If only geohash is given, convert back to lat/lon.
    if latitude is None and longitude is None and geohash is not None:
        latitude, longitude = geohash_decode(geohash)

    # Run reverse geocoder.
    location = reverse_geocode(latitude, longitude, country_code)

    # Backward compatibility re. already cached objects from ``reverse_geocode``.
    if hasattr(location, 'raw'):
        location = location.raw

    if location is None or 'error' in location:
        raise ValueError('Reverse geocoding failed for lat={}, lon={}'.format(latitude, longitude))

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
def reverse_geocode(latitude, longitude, country_code):
    """
    Cache responses of the Nominatim reverse geocoding service.

    Uses a local version of Nomatim to get rid of
    the "one request per second" fair-use policy.

    https://wiki.openstreetmap.org/wiki/Nominatim/Installation

    This is a Python implementation for subsequently requesting::

        time http https://nominatim.hiveeyes.org/reverse lat==52.246 lon==20.898 format==json
        time http https://nominatim.openstreetmaps.org/reverse lat==52.246 lon==20.898 format==json

    """

    location = None
    if country_code == 'DE':
        location = reverse_geocode_main(latitude, longitude)

    if location is None or 'error' in location:
        location = reverse_geocode_fallback(latitude, longitude)

    if location is None or 'error' in location:
        # Must raise an exception here to let the result not be cached.
        raise ValueError('Reverse geocoding failed for lat={}, lon={}'.format(latitude, longitude))

    return location


def reverse_geocode_main(latitude, longitude):

    log.debug('Reverse geocoding I: {}'.format(locals()))

    location = None
    try:
        geolocator = Nominatim(domain='nominatim.hiveeyes.org', user_agent=nominatim_user_agent, timeout=1.25)
        position = (latitude, longitude)
        location = geolocator.reverse(position).raw

        # Sanity checks
        if location['address'] == {'country': 'Deutschland', 'country_code': 'de', 'continent': 'Europe'}:
            return None

    except Exception as ex:
        name = ex.__class__.__name__
        log.warning('Reverse geocoding I failed: {}: {}. lat={}, lon={}'.format(name, ex, latitude, longitude))

    return location


def reverse_geocode_fallback(latitude, longitude):

    log.debug('Reverse geocoding II: {}'.format(locals()))

    location = None
    try:
        # 2018-03-24
        # Nominatim expects the User-Agent as HTTP header otherwise it returns a HTTP-403.
        # This has been fixed in geopy-1.12.0.
        # https://operations.osmfoundation.org/policies/nominatim/
        # https://github.com/geopy/geopy/issues/185
        geolocator = Nominatim(user_agent=nominatim_user_agent, timeout=3.0)

        # FIXME: When using "HTTP_PROXY" from environment, use scheme='http'
        # export HTTP_PROXY=http://weather.hiveeyes.org:8912/
        # See also https://github.com/geopy/geopy/issues/263
        #geolocator = Nominatim(user_agent=nominatim_user_agent, scheme='http')

        position = (latitude, longitude)
        location = geolocator.reverse(position).raw

    except Exception as ex:
        name = ex.__class__.__name__
        log.error('Reverse geocoding II failed: {}: {}. lat={}, lon={}'.format(name, ex, latitude, longitude))

    finally:
        # Obey to fair use policy (an absolute maximum of 1 request per second).
        # https://operations.osmfoundation.org/policies/nominatim/
        time.sleep(1)

    return location


def improve_location(location):
    """
    Heuristically compensate for anomalies from upstream OSM.

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

    if location is None:
        return

    address = location.address

    # Uppercase `country_code` attribute.
    if 'country_code' in address:
        address.country_code = address.country_code.upper()


    # Patch `country` field.
    if 'country_code' in address:

        # R.D. => Dominican Republic
        # Example: Guayacanes, Costámbar, Puerto Plata, DO (#109)
        if address.country_code == 'DO':
            address.country = 'Dominican Republic'

        # RP => Republic of Poland
        # Example: Polarna, Krzyki, Osiedle Krzyki-Partynice, Wrocław, dolnośląskie, PL (#1463)
        if address.country_code == 'PL':
            address.country = 'Poland'


    # Improve `city` attribute.

    # Stadtstaat handling. For all known Stadtstaaten,
    # - if `city` is missing, use `state` attribute.
    # - if `state` is missing, use `city` attribute.
    # https://de.wikipedia.org/wiki/Stadtstaat#Souver%C3%A4ne_Stadtstaaten
    stadtstaaten = [

        # Germany
        'Berlin', 'Bremen', 'Hamburg',

        # Austria
        'Wien',
    ]
    city_or_state = address.get('city', address.get('state'))
    if city_or_state in stadtstaaten:
        address.state = address.city = city_or_state

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

    # Patch `city` field.
    if 'city' in address and address.city == 'Rgbg':
        address.city = 'Regensburg'

    if 'city' not in address:
        address.city = 'unknown'


    # Improve Stadtteil.
    # Use `residential` or `neighbourhood` for missing `suburb` attribute.
    if 'suburb' not in address and 'residential' in address:
        address.suburb = address.residential
    if 'suburb' not in address and 'neighbourhood' in address:
        address.suburb = address.neighbourhood

    # Be agnostic against road vs. path
    if 'road' not in address:
        road_choices = ['path', 'pedestrian', 'cycleway', 'footway', 'neighbourhood', 'house_number']
        for fieldname in road_choices:
            if fieldname in address:
                address.road = address[fieldname]
                break

    if 'road' not in address:
        address.road = 'unknown'


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

    # Clean up `county`, 'city_district` and `suburb` fields.
    blacklist = [
        # county
        'Landkreis', 'Kreis', 'Verwaltungsgemeinschaft',

        # city_district
        'Stadtbezirk',

        # suburb: prefixes
        'Bezirksteil', 'Bezirk', 'KG',

        # suburb: values
        'Fhain',
    ]
    blacklist_fields = ['county', 'city_district', 'suburb']
    for fieldname in blacklist_fields:
        if fieldname in address:
            for black in blacklist:
                if black in address[fieldname]:
                    address[fieldname] = address[fieldname].replace(black, '').strip()

    # Build display location from components.
    address_components = ['road', 'suburb', 'city_district', 'city', 'county', 'state', 'country_code']
    address_parts = []
    starts_with_number = re.compile('^\d+')
    for field_choices in address_components:
        field_choices = to_list(field_choices)
        for fieldname in field_choices:
            if fieldname in address:
                component = address[fieldname]

                if not component or component == 'unknown':
                    continue

                if address_parts and component == address_parts[-1]:
                    continue

                if starts_with_number.match(component):
                    continue

                address_parts.append(component)
                break

    location_label = ', '.join(address_parts)
    return location_label


def geohash_encode(latitude, longitude):
    """
    Compute Geohash from coordinates.

    -- https://en.wikipedia.org/wiki/Geohash
    """
    geohash = geohash2.encode(float(latitude), float(longitude))

    # Eight characters should be fine?
    #geohash = geohash[:8]

    return geohash


def geohash_decode(geohash):
    """
    Compute coordinates from Geohash.

    -- https://en.wikipedia.org/wiki/Geohash
    """
    return geohash2.decode(geohash)


def disable_nominatim_cache():
    log.info('Disabling Nominatim cache')
    # Invalidate the Nominatim cache; this applies only for this session, it will _not_ _purge_ all data at once.
    invalidate_dogpile_cache(nominatim_cache)
