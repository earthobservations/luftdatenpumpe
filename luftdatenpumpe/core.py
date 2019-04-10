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
from munch import Munch, munchify
from tablib import Dataset
from requests_cache import CachedSession
from luftdatenpumpe.geo import geohash_encode, resolve_location, improve_location, format_address
from luftdatenpumpe.target import RDBMSStorage
from luftdatenpumpe.util import exception_traceback, find_files

from . import __appname__ as APP_NAME
from . import __version__ as APP_VERSION

log = logging.getLogger(__name__)


class LuftdatenPumpe:

    # Live data API URI for luftdaten.info
    uri = 'https://api.luftdaten.info/static/v1/data.json'

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

        if self.source.startswith('postgresql://'):
            return self.make_stations()

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

    def make_stations(self):
        """
        Re-make station information from PostgreSQL database.

        Example::

            {
                "station_id": 28,
                "name": "Ulmer Stra\u00dfe, Wangen, Stuttgart, Baden-W\u00fcrttemberg, DE",
                "position": {
                    "latitude": 48.778,
                    "longitude": 9.236,
                    "altitude": 223.7,
                    "country": "DE",
                    "geohash": "u0wt6pv2qqhz"
                },
                "location": {
                    "place_id": "10504194",
                    "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
                    "osm_type": "way",
                    "osm_id": "115374184",
                    "lat": "48.777845",
                    "lon": "9.23582396156841",
                    "display_name": "Kulturhaus ARENA, 241, Ulmer Stra\u00dfe, Wangen, Stuttgart, Regierungsbezirk Stuttgart, Baden-W\u00fcrttemberg, 70327, Deutschland",
                    "boundingbox": [
                        "48.7775199",
                        "48.778185",
                        "9.2353783",
                        "9.236272"
                    ],
                    "address": {
                        "country_code": "DE",
                        "country": "Deutschland",
                        "state": "Baden-W\u00fcrttemberg",
                        "state_district": "Regierungsbezirk Stuttgart",
                        "county": "Stuttgart",
                        "postcode": "70327",
                        "city": "Stuttgart",
                        "city_district": "Wangen",
                        "suburb": "Wangen",
                        "road": "Ulmer Stra\u00dfe",
                        "house_number": "241",
                        "neighbourhood": "Wangen"
                    },
                    "address_more": {
                        "building": "Kulturhaus ARENA"
                    }
                },
                "sensors": [
                    {
                        "sensor_id": 658,
                        "sensor_type": "SDS011"
                    },
                    {
                        "sensor_id": 657,
                        "sensor_type": "DHT22"
                    }
                ]
            }
        """

        entries = []

        sql = """
            SELECT *
            FROM ldi_stations, ldi_osmdata
            WHERE
              ldi_stations.station_id = ldi_osmdata.station_id
            ORDER BY
              ldi_stations.station_id
        """

        storage = RDBMSStorage(self.source)
        for station in storage.db.query(sql):
            station = munchify(station)
            entry = {
                "station_id": station.station_id,
                "name": station.name,
                "position": {
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "altitude": station.altitude,
                    "country": station.country,
                    "geohash": station.geohash
                }
            }
            entries.append(munchify(entry))

        return entries

    def request_live_data(self):

        log.info('Requesting Live API at {}'.format(self.uri))
        payload = self.session.get(self.uri).content.decode('utf-8')
        data = json.loads(payload)
        #pprint(data)

        timestamp = self.convert_timestamp(data[0]['timestamp'])
        log.info('Timestamp of first record: {}'.format(timestamp))

        iterator = self.apply_filter(data)
        if self.progressbar:
            iterator = tqdm(list(iterator))

        for item in iterator:
            try:

                reading = self.make_reading(item)
                if reading is None:
                    continue
                yield reading

            except Exception as ex:
                log.warning('Could not make reading from {}.\n{}'.format(item, exception_traceback()))

    def apply_filter(self, data):

        for item in data:

            #log.info('item: %s', item)

            # Decode JSON item
            country_code = item['location']['country'].upper()
            station_id = item['location']['id']
            sensor_id = item['sensor']['id']

            # If there is a filter defined, evaluate it.
            # Skip further processing for specific country codes, station ids or sensor ids.
            # TODO: Improve evaluating conditions.
            if self.filter:
                skip = False
                if 'country' in self.filter:
                    if country_code not in self.filter['country']:
                        skip = True
                if 'station' in self.filter:
                    if station_id not in self.filter['station']:
                        skip = True
                if 'sensor' in self.filter:
                    if sensor_id not in self.filter['sensor']:
                        skip = True

                if skip:
                    continue

            yield item

    def make_reading(self, item):

        #log.info('item: %s', item)

        # Decode JSON item
        station_id = item['location']['id']
        sensor_id = item['sensor']['id']
        sensor_type = item['sensor']['sensor_type']['name']

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
        if ('latitude' not in station.position or 'longitude' not in station.position) or \
            (station.position.latitude is None or station.position.longitude is None):
            # TODO: Just emit this message once per X.
            log.warning('Incomplete station position, skipping geospatial enrichment. Station: {}'.format(station))
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
                    country_code=station.position.country,
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
                log.error(u'Problem with reverse geocoder for station {}: {}\n{}'.format(station, ex, exception_traceback()))

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

        # Optionally append suffix appropriately.
        suffix = '.csv'
        if not path.endswith(suffix):
            path += '/**/*' + suffix

        log.info('Building list of CSV files from {}'.format(path))
        data = list(find_files(path))
        log.info('Processing {} files'.format(len(data)))

        # Optionally add progressbar indicator.
        iterator = data
        if self.progressbar:
            iterator = tqdm(list(data))

        # Process all files.
        for csvpath in iterator:
            readings = self.import_csv(csvpath)
            if readings is None:
                continue

            # Optionally, return first reading only.
            # This is a shortcut-option for churning through the whole data set quickly.
            # This can be used to get whole regional coverage of the data while lacking many details.
            if self.quick_mode:
                readings = list(readings)
                if readings:
                    yield readings[0]
                    continue

            # Process all readings per CSV file.
            for reading in readings:
                if reading is None:
                    continue
                yield reading

    @staticmethod
    def sensor_matches(path, sensors):
        for sensor in sensors:
            if sensor in path:
                return True
        return False

    def import_csv(self, csvpath):

        # Skip files not matching filter pattern (by sensor id).
        if not self.import_archive_filename_accepted(csvpath):
            return

        # When progressbar is enabled, log this to the DEBUG level.
        logger = log.info
        if self.progressbar:
            logger = log.debug
        logger('Reading CSV file {}'.format(csvpath))

        if self.sensor_matches(csvpath, ['ppd42ns', 'sds011', 'pms3003', 'pms5003', 'pms7003', 'hpm']):
            """
            PPD42NS
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2
            27;PPD42NS;18;;;2015-10-01T19:41:50.266431+00:00;0.62;0;0;0.62;0;0

            SDS011
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;durP1;ratioP1;P2;durP2;ratioP2
            92;SDS011;42;48.800;9.003;2016-07-14T13:02:46.949036+00:00;7.71;;;5.03;;

            PMS3003
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;P2;P0
            409;PMS3003;193;14.382;121.047;2017-12-31T00:00:21;48.00;39.00;

            PMS5003
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;P2;P0
            11390;PMS5003;5751;52.015;5.432;2018-04-20T00:00:25;45.25;31.50;22.50

            PMS7003
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;P2;P0
            5920;PMS7003;2986;51.213;6.808;2017-12-27T00:01:57;5.00;4.00;1.00

            HPM
            sensor_id;sensor_type;location;lat;lon;timestamp;P1;P2
            7096;HPM;3590;50.853;4.342;2017-11-25T00:04:50;22;21
            """
            fieldnames = ['P0', 'P1', 'P2']

        elif self.sensor_matches(csvpath, ['dht22', 'htu21d']):
            """
            DHT22
            sensor_id;sensor_type;location;lat;lon;timestamp;temperature;humidity
            48;DHT22;19;48.722;9.209;2016-08-13T00:00:26.053188+00:00;;

            HTU21D
            sensor_id;sensor_type;location;lat;lon;timestamp;temperature;humidity
            2875;HTU21D;1445;52.600;13.327;2017-11-26T00:00:38;2.80;99.90
            """
            fieldnames = ['temperature', 'humidity']

        elif self.sensor_matches(csvpath, ['bmp180', 'bmp280', 'bme280']):
            """
            BMP180
            sensor_id;sensor_type;location;lat;lon;timestamp;pressure;altitude;pressure_sealevel;temperature
            1464;BMP180;725;48.410;9.934;2017-04-11T00:00:45;96011;;;11.30

            BMP280
            sensor_id;sensor_type;location;lat;lon;timestamp;pressure;altitude;pressure_sealevel;temperature
            2184;BMP280;1098;48.939;8.961;2017-11-26T00:00:35;;;;2.60

            BME280
            sensor_id;sensor_type;location;lat;lon;timestamp;pressure;altitude;pressure_sealevel;temperature;humidity
            1093;BME280;535;48.746;9.211;2017-03-31T00:00:47;96913.02;;;12.75;63.35
            """
            fieldnames = ['temperature', 'humidity', 'pressure', 'altitude', 'pressure_sealevel']

        elif self.sensor_matches(csvpath, ['ds18b20']):
            """
            DS18B20
            sensor_id;sensor_type;location;lat;lon;timestamp;temperature
            19319;DS18B20;9794;43.851;125.304;2019-01-02T00:04:02;-14.94
            """
            fieldnames = ['temperature']

        else:
            log.warning('Skip import of {}. Unknown sensor type'.format(csvpath))
            return

        return self.csv_reader(csvpath, fieldnames)

    def csv_reader(self, csvpath, fieldnames):

        payload = None
        if self.quick_mode:
            try:
                payload = open(csvpath).read(256)
                payload = '\n'.join(payload.split('\n')[:2])
            except:
                pass
        else:
            payload = open(csvpath).read()

        if payload is None:
            log.error('Could not read CSV file %s', csvpath)
            return

        # Read CSV file into tablib's Dataset and cast to dictionary representation.
        imported_data = Dataset().load(payload, format='csv', delimiter=';')
        records = imported_data.dict

        # Iterate all CSV records.
        for record in records:

            item = self.make_item(record)
            try:
                reading = self.make_reading(item)
                if reading is None:
                    continue

                if not self.csvdata_to_reading(record, reading, fieldnames):
                    continue

                yield reading

            except Exception as ex:
                log.warning('Could not make reading from {}.\n{}'.format(item, exception_traceback()))

    def csvdata_to_reading(self, record, reading, fieldnames):

        # Indicator whether we found any data.
        has_data = False

        # Read all the CSV record fields.
        for fieldname in fieldnames:

            # Skip missing keys.
            if fieldname not in record:
                continue

            # Sanitize value.
            value = record[fieldname].strip()

            # Skip empty or non-numeric values.
            if not value or value.lower() == 'nan':
                continue

            # Actually use this reading, casting to float.
            reading.data[fieldname] = float(value)

            # Signal positive dataness.
            has_data = True

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

            if 'sensor-type' in self.filter:
                # Decode sensor type from filename, e.g. ``2017-01-13_dht22_sensor_318.csv``.
                m = re.match('.+_(\w+)_sensor_\d+\.csv$', csvpath)
                if m:
                    sensor_type = m.group(1)
                    if sensor_type not in self.filter['sensor-type']:
                        return False

        return True
