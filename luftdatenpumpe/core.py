# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging

import requests
from tqdm import tqdm
from pprint import pformat

from .geo import geohash_encode, reverse_geocode
from .mqtt import MQTTAdapter
from .util import exception_traceback

from . import __appname__ as APP_NAME
from . import __version__ as APP_VERSION


log = logging.getLogger(__name__)


class LuftdatenPumpe:

    # luftdaten.info API URI
    uri = 'https://api.luftdaten.info/static/v1/data.json'

    def __init__(self, filter=None, geohash=False, reverse_geocode=False, mqtt_uri=None, progressbar=False, dry_run=False):
        self.mqtt_uri = mqtt_uri
        self.geohash = geohash
        self.reverse_geocode = reverse_geocode
        self.dry_run = dry_run
        self.progressbar = progressbar
        self.filter = filter
        if mqtt_uri:
            self.mqtt = MQTTAdapter(mqtt_uri)

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

            #log.info('item: %s', item)

            # Decode JSON item
            timestamp = item['timestamp']
            location_id = item['location']['id']
            sensor_id = item['sensor']['id']
            sensor_type = item['sensor']['sensor_type']['name']

            # If there is a filter defined, evaluate it
            # For specific location|sensor ids, skip further processing
            if self.filter:
                if 'locations' in self.filter:
                    if location_id not in self.filter['locations']:
                        continue
                if 'sensors' in self.filter:
                    if sensor_id not in self.filter['sensors']:
                        continue

            # Build reading
            reading = {}

            # Collect sensor values
            for sensor in item['sensordatavalues']:
                name = sensor['value_type']
                value = float(sensor['value'])
                reading[name] = value

            # Insert timestamp in appropriate format
            reading['time'] = self.convert_timestamp(timestamp)

            # Insert sensor address information
            sensor_address = {
                'location_id': location_id,
                'sensor_id':   sensor_id,
                'sensor_type': sensor_type,
            }
            reading.update(sensor_address)

            # Insert geo data
            if self.geohash:

                # Compute geohash
                reading['geohash'] = geohash_encode(item['location']['latitude'], item['location']['longitude'])

            try:
                altitude = item['location']['altitude']
                reading['altitude'] = float(altitude)
            except:
                log.error('Problem reading altitude value')

            # Human readable location name
            if self.reverse_geocode:
                try:
                    if 'geohash' in reading:
                        location_name = reverse_geocode(geohash=reading['geohash'])
                    else:
                        location_name = reverse_geocode(
                            latitude=item['location']['latitude'],
                            longitude=item['location']['longitude'])

                    # 2018-12-02: Workaround re. charset encoding of cached items wrt. Python3 compatibility
                    if type(location_name) is bytes:
                        location_name = location_name.decode('utf-8')

                    reading['location_name'] = location_name

                except Exception as ex:
                    reading['location_name'] = u'Location-ID: {}'.format(location_id)
                    log.error(u'Problem with reverse geocoder: {}\n{}'.format(ex, exception_traceback()))

            #reading['__item__'] = item
            log.debug('Reading: %s', reading)

            yield reading

            # Debugging
            #break

    def request_and_publish(self):
        for reading in self.request():
            # Publish to MQTT bus
            if self.dry_run:
                log.info('Dry-run. Would publish record:\n{}'.format(pformat(reading)))
            else:
                self.publish_mqtt(reading)

    def get_stations(self):
        locations = {}
        field_candidates = ['location_id', 'location_name', 'geohash', 'altitude']
        for reading in self.request():

            #print('ITEM: %s', reading)

            # Location ID for the reading
            location_id = reading['location_id']

            # Acquire additional sensors from reading
            if location_id in locations:
                location = locations[location_id]
                sensor_id = reading['sensor_id']
                if sensor_id not in location['sensors']:
                    location['sensors'].append(sensor_id)
                continue


            # Acquire location information from reading
            location = {}
            for field in field_candidates:
                if field in reading:
                    location[field] = reading[field]

            # Acquire first sensor from reading
            sensor_id = reading['sensor_id']
            location['sensors'] = [sensor_id]

            # Collect location if not empty
            if location:
                locations[location_id] = location

        return locations

    def get_stations_grafana(self):
        stations = self.get_stations()
        entries = []
        for location_id, location in stations.items():
            #print(location_id, location)
            if 'location_name' in location:
                location_name = location['location_name']
            else:
                location_name = u'Location: {}'.format(location_id)
            entry = {'value': location_id, 'text': location_name}
            entries.append(entry)
        return entries

    @staticmethod
    def convert_timestamp(timestamp):
        # mungle timestamp to be formally in ISO 8601/UTC
        if ' ' in timestamp:
            timestamp = timestamp.replace(' ', 'T')
        if '+' not in timestamp:
            timestamp += 'Z'
        return timestamp

    def publish_mqtt(self, measurement):
        # FIXME: Don't only use ``sort_keys``. Also honor the field names of the actual readings by
        # putting them first. This is:
        # - "P1" and "P2" for "sensor_type": "SDS011"
        # - "temperature" and "humidity" for "sensor_type": "DHT22"
        # - "temperature", "humidity", "pressure" and "pressure_at_sealevel" for "sensor_type": "BME280"
        mqtt_message = json.dumps(measurement, sort_keys=True)
        self.mqtt.publish(mqtt_message)
