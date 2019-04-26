# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017-2019 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import sys
import logging
from urllib.parse import urlparse

import redis
from tqdm import tqdm
from requests_cache import CachedSession
from luftdatenpumpe.geo import geohash_encode, resolve_location, improve_location, format_address

from luftdatenpumpe import __appname__ as APP_NAME
from luftdatenpumpe import __version__ as APP_VERSION


log = logging.getLogger(__name__)


class AbstractLuftdatenPumpe:

    network = None
    uri = None

    def __init__(self, source=None, filter=None, reverse_geocode=False, progressbar=False, quick_mode=False, dry_run=False):
        self.source = source
        self.reverse_geocode = reverse_geocode
        self.dry_run = dry_run
        self.progressbar = progressbar
        self.filter = filter

        # Quick mode only imports the first few datasets to speed things up.
        self.quick_mode = quick_mode

        # Cache responses from the luftdaten.info API for five minutes.
        # TODO: Make backend configurable.

        # Configure User-Agent string.
        user_agent = APP_NAME + '/' + APP_VERSION

        # Use hostname of url as cache prefix.
        cache_name = urlparse(self.uri).netloc

        # Configure cached requests session.
        self.session = CachedSession(
            cache_name=cache_name, backend='redis', expire_after=300,
            user_agent=user_agent)

        # Disable request cache by overriding it with a vanilla requests session.
        #import requests; self.session = requests.Session()

        # Gracefully probe Redis for availability if cache is enabled.
        if hasattr(self.session, 'cache'):
            try:
                self.session.cache.responses.get('test')
            except redis.exceptions.ConnectionError as ex:
                log.error('Unable to connect to Redis: %s', ex)
                sys.exit(2)

    def get_readings(self):

        if self.source == 'api':
            data = self.get_readings_from_api()

        elif self.source.startswith('file://'):
            path = self.source.replace('file://', '')
            data = self.get_readings_from_csv(path)

        else:
            raise ValueError('Unknown data source: {}'.format(self.source))

        if data is None:
            raise KeyError('No data selected. Please check connectivity and filter definition.')

        return data

    def get_readings_from_api(self):
        raise NotImplementedError(f'Readings not implemented by sensor network adapter "{self.network}".')

    def get_readings_from_csv(self):
        raise NotImplementedError(f'Readings not implemented by sensor network adapter "{self.network}".')

    def enrich_station(self, station):

        # Sanity checks.
        if ('latitude' not in station.position or 'longitude' not in station.position) or \
           (station.position.latitude is None or station.position.longitude is None):

            # Just emit this message once per station.
            StationGeocodingFailed.emit_warning(station.station_id)
            return

        # Compute geohash.
        station.position.geohash = geohash_encode(station.position.latitude, station.position.longitude)

        # Compute human readable location name.
        if self.reverse_geocode:

            try:

                # Reverse-geocode position.
                station.location = resolve_location(
                    latitude=station.position.latitude,
                    longitude=station.position.longitude,
                    geohash=station.position.geohash,
                    country_code=station.position.get('country'),
                )

                # Improve location information.
                improve_location(station.location)

                # Format address into single label.
                station.name = format_address(station.location)

                # Apply some fixups.
                try:
                    if station.name.lower() == station.position.country.lower():
                        del station['name']
                except:
                    pass

            except Exception:
                log.exception(f'Failed computing humanized name for station {station}')

            if 'name' not in station:
                station.name = f'Station #{station.station_id}'
                try:
                    station.name += ', ' + station.position.country
                except:
                    pass

    def apply_filter(self, data):
        if self.filter:
            return self.filter_rule(data)
        else:
            return data

    def wrap_progress(self, data, stepsize=False):
        # Optionally, add progress reporting.
        if self.progressbar:
            data = list(data)
            total = len(data)
            if stepsize is not False:
                total *= stepsize
            log.info(f'Processing #{total} items')
            data = tqdm(data, unit_scale=stepsize)
        return data


class StationGeocodingFailed:

    stations_with_warnings = {}

    @classmethod
    def emit_warning(cls, station_id):
        if station_id in cls.stations_with_warnings:
            return
        log.warning(f'Incomplete station position, skipping geospatial enrichment for station "{station_id}"')
        cls.stations_with_warnings[station_id] = True
