# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
import requests
import requests_cache
from tqdm import tqdm
from munch import Munch
from luftdatenpumpe.geo import geohash_encode, resolve_location, improve_location, format_address
from luftdatenpumpe.util import exception_traceback


log = logging.getLogger(__name__)


class LuftdatenPumpe:

    # luftdaten.info API URI
    uri = 'https://api.luftdaten.info/static/v1/data.json'

    def __init__(self, filter=None, reverse_geocode=False, progressbar=False, dry_run=False):
        self.reverse_geocode = reverse_geocode
        self.dry_run = dry_run
        self.progressbar = progressbar
        self.filter = filter

        # Cache responses from the luftdaten.info API for five minutes.
        # TODO: Make backend configurable.
        requests_cache.install_cache('api.luftdaten.info', backend='redis', expire_after=300)

    def request(self):
        payload = requests.get(self.uri).content.decode('utf-8')
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

        # If there is a filter defined, evaluate it
        # For specific location|sensor ids, skip further processing
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

            # Compute geohash
            station.position.geohash = geohash_encode(station.position.latitude, station.position.longitude)

            # Compute human readable location name
            if self.reverse_geocode:

                try:

                    # Reverse-geocode position
                    station.location = resolve_location(
                        latitude=station.position.latitude,
                        longitude=station.position.longitude,
                        geohash=station.position.geohash
                    )

                    # Improve location information
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

    def get_readings(self):
        return list(self.request())

    def get_stations(self):
        stations = {}
        field_candidates = ['station_id', 'name', 'position', 'location']
        for reading in self.request():

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

    @staticmethod
    def convert_timestamp(timestamp):
        # mungle timestamp to be formally in ISO 8601/UTC
        if ' ' in timestamp:
            timestamp = timestamp.replace(' ', 'T')
        if '+' not in timestamp:
            timestamp += 'Z'
        return timestamp
