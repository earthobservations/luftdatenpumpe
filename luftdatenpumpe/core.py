# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import re
import sys
import json
import redis
import logging

from tqdm import tqdm
from munch import Munch
from tablib import Dataset
from requests_cache import CachedSession
from luftdatenpumpe.geo import geohash_encode, resolve_location, improve_location, format_address
from luftdatenpumpe.util import exception_traceback, find_files

from . import __appname__ as APP_NAME
from . import __version__ as APP_VERSION

log = logging.getLogger(__name__)


class LuftdatenPumpe:

    # Live data API URI for luftdaten.info
    uri = 'https://api.luftdaten.info/static/v1/data.json'

    def __init__(self, source=None, filter=None, reverse_geocode=False, progressbar=False, dry_run=False):
        self.source = source
        self.reverse_geocode = reverse_geocode
        self.dry_run = dry_run
        self.progressbar = progressbar
        self.filter = filter

        # Cache responses from the luftdaten.info API for five minutes.
        # TODO: Make backend configurable.

        # Configure User-Agent string.
        user_agent = APP_NAME + '/' + APP_VERSION

        # Configure cached requests session.
        self.session = CachedSession(
            cache_name='api.luftdaten.info', backend='redis', expire_after=300,
            user_agent=user_agent)

        # Probe Redis for availability.
        try:
            self.session.cache.responses.get('test')
        except redis.exceptions.ConnectionError as ex:
            log.error('Unable to connect to Redis: %s', ex)
            sys.exit(2)

    def get_readings(self):

        if self.source == 'api':
            data = self.request_live_data()

        elif self.source.startswith('file://'):
            path = self.source.replace('file://', '')
            data = self.import_archive(path)

        else:
            raise ValueError('Unknown data source: {}'.format(self.source))

        if data is None:
            raise KeyError('No data selected. Please check connectivity and filter definition.')

        return data

    def get_stations(self):
        stations = {}
        field_candidates = ['station_id', 'name', 'position', 'location']
        for reading in self.get_readings():

            # Location ID for the reading
            station_id = reading.station.station_id

            # Sensor information from the reading
            sensor_info = Munch({
                'sensor_id': reading.station.sensor_id,
                'sensor_type': reading.station.sensor_type,
            })

            # Acquire additional sensors from reading.
            # This continues with the next loop iteration as
            # location information has already been transferred.
            if station_id in stations:
                station = stations[station_id]
                sensor_id = reading.station.sensor_id
                if not any(map(lambda item: item.sensor_id == sensor_id, station['sensors'])):
                    station['sensors'].append(sensor_info)
                continue

            # New station found: Acquire its information from reading
            station = Munch()
            for field in field_candidates:
                if field in reading.station:
                    station[field] = reading.station[field]

            # Acquire first sensor from reading
            station['sensors'] = [sensor_info]

            # Collect location if not empty
            if station:
                stations[station_id] = station

        results = []
        for key in sorted(stations.keys()):
            station = stations[key]
            results.append(station)

        return results

    def request_live_data(self):

        log.info('Requesting Live API at {}'.format(self.uri))
        payload = self.session.get(self.uri).content.decode('utf-8')
        data = json.loads(payload)
        #pprint(data)

        timestamp = self.convert_timestamp(data[0]['timestamp'])
        log.info('Timestamp of first record: {}'.format(timestamp))

        iterator = data
        if self.progressbar:
            iterator = tqdm(data)

        for item in iterator:
            try:

                reading = self.make_reading(item)
                if reading is None:
                    continue
                yield reading

            except Exception as ex:
                log.warning('Could not make reading from {}.\n{}'.format(item, exception_traceback()))

    def make_reading(self, item):

        #log.info('item: %s', item)

        # Decode JSON item
        station_id = item['location']['id']
        sensor_id = item['sensor']['id']
        sensor_type = item['sensor']['sensor_type']['name']

        # If there is a filter defined, evaluate it.
        # For specific location|sensor ids, skip further processing.
        if self.filter:
            if 'station' in self.filter:
                if station_id not in self.filter['station']:
                    return
            if 'sensor' in self.filter:
                if sensor_id not in self.filter['sensor']:
                    return

        # Build reading
        reading = Munch(
            station=Munch(),
            data=Munch(),
        )

        # Insert timestamp in appropriate format
        reading.data.time = self.convert_timestamp(item['timestamp'])

        # Insert baseline metadata information
        reading.station.station_id = station_id
        reading.station.sensor_id = sensor_id
        reading.station.sensor_type = sensor_type

        # Collect position information
        del item['location']['id']
        reading.station.position = Munch()
        for key, value in item['location'].items():
            if key in ['latitude', 'longitude', 'altitude']:
                try:
                    value = float(value)
                except:
                    value = None
            reading.station.position[key] = value

        # Collect sensor values
        if 'sensordatavalues' in item:
            for sensor in item['sensordatavalues']:
                name = sensor['value_type']
                value = float(sensor['value'])
                reading.data[name] = value

        # Add more detailed location information
        self.enrich_station(reading.station)

        log.debug('Reading: %s', json.dumps(reading))

        # Debugging
        #break

        return reading

    def enrich_station(self, station):

        # Sanity checks.
        if 'latitude' not in station.position or 'longitude' not in station.position:
            # TODO: Reenable this log message, but just emit once.
            #log.warning('Could not enrich station information for {}'.format(station))
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
                    geohash=station.position.geohash
                )

                # Improve location information.
                improve_location(station.location)

                # Format address into single label.
                station.name = format_address(station.location)

                try:
                    if station.name.lower() == station.position.country.lower():
                        del station['name']
                except:
                    pass

            except Exception as ex:
                log.error(u'Problem with reverse geocoder: {}\n{}'.format(ex, exception_traceback()))

            if 'name' not in station:
                station.name = u'Station #{}'.format(station.station_id)
                try:
                    station.name += ', ' + station.position.country
                except:
                    pass

    @staticmethod
    def convert_timestamp(timestamp):
        # Mungle timestamp to be formally in ISO 8601 format (UTC).
        if ' ' in timestamp:
            timestamp = timestamp.replace(' ', 'T')
        if '+' not in timestamp:
            timestamp += 'Z'
        return timestamp

    def import_archive(self, path):
        log.info('Importing CSV files from {}'.format(path))

        data = find_files(path, '.csv')

        iterator = data
        if self.progressbar:
            iterator = tqdm(list(data))

        for csvpath in iterator:
            readings = self.import_csv(csvpath)
            if readings is None:
                continue
            for reading in readings:
                if reading is None:
                    continue
                yield reading

    def import_csv(self, csvpath):

        # Skip files not matching filter pattern (by sensor id).
        if not self.import_archive_filename_accepted(csvpath):
            return

        logger = log.info
        if self.progressbar:
            logger = log.debug
        #logger('Importing {}'.format(csvpath))
        log.info('Importing {}'.format(csvpath))

        if 'ppd42ns' in csvpath or 'sds011' in csvpath:
            """
            PPD42NS
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2
            27;PPD42NS;18;;;2015-10-01T19:41:50.266431+00:00;0.62;0;0;0.62;0;0

            SDS011
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2
            92;SDS011;42;48.800;9.003;2016-07-14T13:02:46.949036+00:00;7.71;;;5.03;;
            """
            fieldnames = ['P1', 'P2']

        elif 'dht22' in csvpath:
            """
            DHT22
            sensor_id;sensor_type;location;lat;lon;timestamp;temperature;humidity
            48;DHT22;19;48.722;9.209;2016-08-13T00:00:26.053188+00:00;;
            """
            fieldnames = ['temperature', 'humidity']

        elif 'bme280' in csvpath:
            """
            BMP180
            sensor_id;sensor_type;location;lat;lon;timestamp;pressure;altitude;pressure_sealevel;temperature
            1464;BMP180;725;48.410;9.934;2017-04-11T00:00:45;96011;;;11.30

            BME280
            sensor_id;sensor_type;location;lat;lon;timestamp;pressure;altitude;pressure_sealevel;temperature;humidity
            1093;BME280;535;48.746;9.211;2017-03-31T00:00:47;96913.02;;;12.75;63.35
            """
            fieldnames = ['temperature', 'humidity', 'pressure', 'altitude', 'pressure_sealevel']

        else:
            log.warning('Skip import of {}. Unknown sensor type'.format(csvpath))
            return

        #print('reading:', reading)
        return self.csv_reader(csvpath, fieldnames)

    def csv_reader(self, csvpath, fieldnames):
        imported_data = Dataset().load(open(csvpath).read(), format='csv', delimiter=';')
        data = imported_data.dict

        for csvitem in data:
            # print(csvitem)

            item = self.make_item(csvitem)
            try:
                reading = self.make_reading(item)
                if reading is None:
                    continue

                if not self.csvdata_to_reading(csvitem, reading, fieldnames):
                    continue

                yield reading

            except Exception as ex:
                log.warning('Could not make reading from {}.\n{}'.format(item, exception_traceback()))

    def csvdata_to_reading(self, csvitem, reading, fieldnames):
        has_data = False
        for fieldname in fieldnames:
            if csvitem[fieldname]:
                has_data = True
                reading.data[fieldname] = float(csvitem[fieldname])
        return has_data

    def make_item(self, csvitem):

        log.debug(csvitem)

        item = {
            'timestamp': csvitem['timestamp'],
            'location': {
                'id': int(csvitem['location']),
            },
            'sensor': {
                'id': int(csvitem['sensor_id']),
                'sensor_type': {
                    'name': csvitem['sensor_type'],
                }
            },
        }

        if csvitem['lat'] and csvitem['lon']:
            item['location'].update(latitude=float(csvitem['lat']), longitude=float(csvitem['lon']))

        return item

    def import_archive_filename_accepted(self, csvpath):
        # If there is a filter defined, evaluate it.
        # For specific location|sensor ids, skip further processing.
        if self.filter:

            if 'sensor' in self.filter:
                # Decode station id from filename, e.g. ``2017-01-13_dht22_sensor_318.csv``.
                m = re.match('.+sensor_(\d+)\.csv$', csvpath)
                if m:
                    sensor_id = int(m.group(1))
                    if sensor_id not in self.filter['sensor']:
                        return False

        return True
