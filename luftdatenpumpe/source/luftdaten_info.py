# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017-2019 Richard Pobering <richard@hiveeyes.org>
# (c) 2019 Matthias Mehldau <wetter@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import re
import json
import logging
from tqdm import tqdm
from munch import Munch
from tablib import Dataset
from operator import itemgetter
from luftdatenpumpe.source.common import AbstractLuftdatenPumpe
from luftdatenpumpe.util import exception_traceback, find_files, is_nan

log = logging.getLogger(__name__)


class LuftdatenPumpe(AbstractLuftdatenPumpe):

    # Live data API URI for luftdaten.info
    uri = 'https://api.luftdaten.info/static/v1/data.json'

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

        # Fetch data from remote API.
        log.info('Requesting luftdaten.info live API at {}'.format(self.uri))
        payload = self.session.get(self.uri).content.decode('utf-8')
        data = json.loads(payload)
        #pprint(data)

        # Mungle timestamp to be formally in ISO 8601 format (UTC).
        timestamp = self.convert_timestamp(data[0]['timestamp'])
        log.info('Timestamp of first record: {}'.format(timestamp))

        # Apply data filter.
        data = self.apply_filter(data)

        # Optionally, add progress reporting.
        if self.progressbar:
            data = list(data)
            log.info('Acquired #{} items from luftdaten.info live API'.format(len(data)))
            data = tqdm(data)

        # Transform live API items to actual readings while optionally
        # applying a number of transformation and enrichment steps.
        for item in data:
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

        # Process all files, optionally add progressbar indicator.
        for csvpath in self.wrap_progress(data):
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
