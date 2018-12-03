# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging

import requests
from tqdm import tqdm
from munch import Munch
from pprint import pformat
from collections import OrderedDict

from .geo import geohash_encode, resolve_location, format_address
from .mqtt import MQTTAdapter
from .util import exception_traceback


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
            reading = Munch(
                meta=Munch(),
                data=Munch(),
            )

            # Insert timestamp in appropriate format
            reading.meta.time = self.convert_timestamp(item['timestamp'])

            # Insert baseline metadata information
            reading.meta.location_id = location_id
            reading.meta.sensor_id = sensor_id
            reading.meta.sensor_type = sensor_type

            # Collect location info
            del item['location']['id']
            reading.meta.update(item['location'])
            for key, value in reading.meta.items():
                if key in ['latitude', 'longitude', 'altitude']:
                    try:
                        reading.meta[key] = float(value)
                    except:
                        reading.meta[key] = None

            # Collect sensor values
            for sensor in item['sensordatavalues']:
                name = sensor['value_type']
                value = float(sensor['value'])
                reading.data[name] = value

            # Insert geo data
            if self.geohash:

                # Compute geohash
                reading.meta['geohash'] = geohash_encode(item['location']['latitude'], item['location']['longitude'])

            #print('reading:', reading)

            # Human readable location name
            if self.reverse_geocode:
                try:

                    # Reverse-geocode position
                    location = resolve_location(
                        latitude=reading.meta['latitude'],
                        longitude=reading.meta['longitude'],
                        geohash=reading.meta.geohash
                    )

                    # Format address into single label.
                    location_name = format_address(location)

                    reading.meta.location_info = location
                    reading.meta.location_name = location_name

                except Exception as ex:
                    reading['location_name'] = u'Location-ID: {}'.format(location_id)
                    log.error(u'Problem with reverse geocoder: {}\n{}'.format(ex, exception_traceback()))

            log.debug('Reading:', json.dumps(reading))

            # Debugging
            #break

            yield reading

    def forward_to_mqtt(self):
        """
        Will publish these kind of messages to the MQTT bus:
        {
            "time": "2018-12-03T01:49:00Z",
            "location_id": 9564,
            "sensor_id": 18870,
            "sensor_type": "DHT22",
            "geohash": "u3qcs53rp",
            "altitude": 85.0,
            "temperature": 2.8,
            "humidity": 90.5
        }
        """
        for reading in self.request():

            # Build MQTT message.

            # Metadata fields
            metadata_fields = ['time', 'location_id', 'sensor_id', 'sensor_type', 'geohash', 'altitude']
            message = OrderedDict()
            for fieldname in metadata_fields:
                message[fieldname] = reading.meta[fieldname]

            # Measurement fields
            message.update(reading.data)

            # Publish to MQTT bus.
            if self.dry_run:
                log.info('Dry-run. Would publish record:\n{}'.format(pformat(message)))
            else:
                self.publish_mqtt(message)

    def get_stations(self):
        locations = {}
        field_candidates = ['location_id', 'location_name', 'location_info', 'geohash', 'latitude', 'longitude', 'altitude']
        for reading in self.request():

            # Location ID for the reading
            location_id = reading.meta.location_id

            # Sensor information from the reading
            sensor_info = {
                'sensor_id': reading.meta.sensor_id,
                'sensor_type': reading.meta.sensor_type,
            }

            # Acquire additional sensors from reading.
            # This continues with the next loop iteration as location
            # information has already been transferred.
            if location_id in locations:
                location = locations[location_id]
                sensor_id = reading.meta.sensor_id
                if sensor_id not in location['sensors']:
                    location['sensors'].update({sensor_id: sensor_info})
                continue

            # Acquire location information from reading
            location = {}
            for field in field_candidates:
                if field in reading.meta:
                    location[field] = reading.meta[field]

            # Acquire first sensor from reading
            sensor_id = reading.meta.sensor_id
            location['sensors'] = {sensor_id: sensor_info}

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
        mqtt_message = json.dumps(measurement)
        self.mqtt.publish(mqtt_message)
