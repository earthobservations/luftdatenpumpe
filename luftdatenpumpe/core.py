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
from pprint import pformat

from .geo import geohash_encode, resolve_location, improve_location, format_address
from .mqtt import MQTTAdapter
from .util import exception_traceback


log = logging.getLogger(__name__)


class LuftdatenPumpe:

    # luftdaten.info API URI
    uri = 'https://api.luftdaten.info/static/v1/data.json'

    def __init__(self, filter=None, reverse_geocode=False, mqtt_uri=None, progressbar=False, dry_run=False):
        self.mqtt_uri = mqtt_uri
        self.reverse_geocode = reverse_geocode
        self.dry_run = dry_run
        self.progressbar = progressbar
        self.filter = filter

        # Cache responses from the luftdaten.info API for five minutes.
        # TODO: Make backend configurable.
        requests_cache.install_cache('api.luftdaten.info', backend='redis', expire_after=300)

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
            station_id = item['location']['id']
            sensor_id = item['sensor']['id']
            sensor_type = item['sensor']['sensor_type']['name']

            # If there is a filter defined, evaluate it
            # For specific location|sensor ids, skip further processing
            if self.filter:
                if 'stations' in self.filter:
                    if station_id not in self.filter['stations']:
                        continue
                if 'sensors' in self.filter:
                    if sensor_id not in self.filter['sensors']:
                        continue

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
                    reading.station.position[key] = float(value)
                else:
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

            yield reading

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
            message = Munch()

            # Station info
            for key, value in reading.station.items():
                if isinstance(value, dict):
                    message.update(value)
                else:
                    message[key] = value

            message['location_id'] = message['station_id']
            del message['station_id']

            # Measurement fields
            message.update(reading.data)

            # Publish to MQTT bus.
            if self.dry_run:
                log.info('Dry-run. Would publish record:\n{}'.format(pformat(message)))
            else:
                self.publish_mqtt(message)

    def get_stations(self):
        stations = {}
        field_candidates = ['station_id', 'name', 'position', 'location']
        for reading in self.request():

            # Location ID for the reading
            station_id = reading.station.station_id

            # Sensor information from the reading
            sensor_info = {
                'sensor_id': reading.station.sensor_id,
                'sensor_type': reading.station.sensor_type,
            }

            # Acquire additional sensors from reading.
            # This continues with the next loop iteration as
            # location information has already been transferred.
            if station_id in stations:
                station = stations[station_id]
                sensor_id = reading.station.sensor_id
                if sensor_id not in station['sensors']:
                    station['sensors'].update({sensor_id: sensor_info})
                continue

            # Acquire station information from reading
            station = Munch()
            for field in field_candidates:
                if field in reading.station:
                    station[field] = reading.station[field]

            # Acquire first sensor from reading
            sensor_id = reading.station.sensor_id
            station['sensors'] = {sensor_id: sensor_info}

            # Collect location if not empty
            if station:
                stations[station_id] = station

        results = []
        for key in sorted(stations.keys()):
            station = stations[key]
            results.append(station)

        return results

    def get_stations_grafana(self):
        stations = self.get_stations()
        entries = []
        for station in stations:
            if 'name' in station:
                station_name = station.name
            else:
                station_name = u'Station #{}, {}'.format(station.station_id, station.position.country)
            entry = {'value': station.station_id, 'text': station_name}
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
