# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017-2019 Richard Pobering <richard@hiveeyes.org>
# (c) 2019 Matthias Mehldau <wetter@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging
from copy import deepcopy
from datetime import datetime, timedelta
from operator import itemgetter

from rfc3339 import rfc3339
from munch import munchify, Munch
from urllib.parse import urljoin
from collections import OrderedDict

from luftdatenpumpe.source.common import AbstractLuftdatenPumpe
from luftdatenpumpe.util import slugify, grouper, chunks

log = logging.getLogger(__name__)


class IrcelinePumpe(AbstractLuftdatenPumpe):
    """
    Ingest air quality measurements from the
    Belgian Interregional Environment Agency (IRCEL - CELINE).

    - http://www.irceline.be/en
    - http://deus.irceline.be/
    - https://en.vmm.be/
    - https://project-corona.eu/

    - http://geo.irceline.be/sos/static/doc/api-doc/

    - https://wiki.52north.org/SensorWeb/SensorObservationService
    - https://wiki.52north.org/SensorWeb/SensorObservationServiceIV
    - https://wiki.52north.org/SensorWeb/SensorWebClientRESTInterfaceV0
    - https://github.com/52North/SOS

    """

    # Sensor network identifier.
    network = 'irceline'

    # IRCELINE SOS REST API URI
    uri = 'http://geo.irceline.be/sos/api/v1/'

    timeout = 60

    def get_index(self):
        return self.send_request()

    def send_request(self, endpoint=None, params=None):
        url = urljoin(self.uri, endpoint)
        log.info(f'Requesting IRCELINE live API at {url}')
        params = params or {}
        return self.session.get(url, params=params, timeout=self.timeout).json()

    def get_stations(self):
        """
        http://geo.irceline.be/sos/api/v1/stations/?service=1&expand=true&locale=en
        """

        data = self.send_request('stations', params={'expanded': 'true'})
        #import sys, json; print(json.dumps(data, indent=2)); sys.exit(0)

        # Apply data filter.
        data = self.apply_filter(data)

        stations = []
        for upstream_station in self.wrap_progress(data):
            upstream_station = munchify(upstream_station)
            station_info = munchify({
                'station_id': upstream_station.properties.id,
                'station_label': upstream_station.properties.label,
                'position': {
                    'country': 'BE',
                    'latitude': upstream_station.geometry.coordinates[1],
                    'longitude': upstream_station.geometry.coordinates[0],
                    'altitude': None,
                }
            })
            self.enrich_station(station_info)

            station_info.sensors = self.timeseries_to_sensors(upstream_station.properties.timeseries)
            #print(station_info)

            stations.append(station_info)

        # List of stations sorted by station identifier.
        stations = sorted(stations, key=itemgetter('station_id'))

        return stations

    def filter_rule(self, data):

        if self.filter and 'country' in self.filter:
            raise NotImplementedError("Filtering by country not supported for IRCELINE/SOS, it's Belgium at all.")

        for item in data:

            #log.info('item: %s', item)

            # Decode JSON item
            #country_code = item['location']['country'].upper()
            station_id = item['properties']['id']
            sensor_ids = map(int, item['properties']['timeseries'].keys())

            # If there is a filter defined, evaluate it.
            # Skip further processing for specific country codes, station ids or sensor ids.
            # TODO: Improve evaluating conditions.
            skip = False
            #if 'country' in self.filter:
            #    if country_code not in self.filter['country']:
            #        skip = True
            if 'station' in self.filter:
                if station_id not in self.filter['station']:
                    skip = True
            if 'sensor' in self.filter:
                skip = True
                for sensor_id in sensor_ids:
                    if sensor_id in self.filter['sensor']:
                        skip = False
                        break

            if skip:
                continue

            yield item

    def timeseries_to_sensors(self, measurements):
        """

        Ingress
        ======
        ::

          "timeseries": {
              "7149": {
                "service": {
                  "id": "1",
                  "label": "IRCEL - CELINE: timeseries-api (SOS 2.0)"
                },
                "offering": {
                  "id": "7149",
                  "label": "7149 - GRIMM - procedure"
                },
                "feature": {
                  "id": "1219",
                  "label": "45R510 - Châtelineau"
                },
                "procedure": {
                  "id": "7149",
                  "label": "7149 - GRIMM - procedure"
                },
                "phenomenon": {
                  "id": "6001",
                  "label": "Particulate Matter < 2.5 µm"
                },
                "category": {
                  "id": "6001",
                  "label": "Particulate Matter < 2.5 µm"
                }
              }
          }


        Egress
        ======
        ::

            "sensors": [
                {
                    "sensor_id": 24685,
                    "sensor_type": "SDS011"
                },
                {
                    "sensor_id": 24686,
                    "sensor_type": "DHT22"
                }
            ]

        """

        # Flatten nested data a bit.
        sensors = []

        # Stable
        property_names = ['service', 'category', 'phenomenon']

        # Unstable / Legacy
        property_names_legacy = ['offering', 'feature', 'procedure']

        # TODO: Which ones to use? Use all for now.
        property_names += property_names_legacy

        for sensor_id, timeseries in measurements.items():
            sensor = OrderedDict()
            sensor['sensor_id'] = int(sensor_id)
            for property_name in property_names:
                sensor[f'sensor_{property_name}_id'] = int(timeseries[property_name]['id'])
                sensor[f'sensor_{property_name}_label'] = timeseries[property_name]['label']
            sensor['sensor_type'] = 'unknown'

            sensor['sensor_label'] = sensor['sensor_phenomenon_label']
            sensor['sensor_fieldname'] = self.slugify_fieldname(sensor['sensor_label'])

            sensors.append(sensor)

        return sensors

    def get_phenomena(self):
        """
        http://geo.irceline.be/sos/api/v1/phenomena/?service=1&locale=en

        {
            "id": "5",
            "label": "Particulate Matter < 10 \u00b5m"
        },
        {
            "id": "6001",
            "label": "Particulate Matter < 2.5 \u00b5m"
        },
        {
            "id": "6002",
            "label": "Particulate Matter < 1 \u00b5m"
        },
        """
        return self.send_request('phenomena')

    def get_timeseries_single(self):
        """
        http://geo.irceline.be/sos/api/v1/timeseries/?service=1&phenomenon=6001&expanded=true&force_latest_values=true&status_intervals=true&rendering_hints=true&locale=en
        """

    def get_readings_from_api(self):
        """
        Should yield list of dictionaries like::

          {
            "station": {
              "station_id": 1071,
              "position": {
                "latitude": 52.544,
                "longitude": 13.374,
                "altitude": 38.7,
                "country": "DE",
                "exact_location": 0,
                "geohash": "u33dbm6duz90"
              }
            },
            "observations": [
              {
                "meta": {
                  "timestamp": "2019-04-25T04:36:26Z",
                  "sensor_id": 2130,
                  "sensor_type": "DHT22"
                },
                "data": {
                  "humidity": 82.3,
                  "temperature": 17.8
                }
              }
            ]
          }

        """
        timeseries_id_list = []

        # Map stations and timeseries to their sensors.
        station_map = {}
        timeseries_sensor_map = {}
        for station in self.get_stations():
            station_id = station.station_id
            station_map[station_id] = station

            for sensor in station.sensors:
                timeseries_id = sensor['sensor_id']
                timeseries_id_list.append(timeseries_id)
                timeseries_sensor_map[timeseries_id] = sensor

        # Fetch timeseries for all stations.
        # Attention: While this is just a single call for the client,
        # this operation might be expensive at the backend.
        # TODO: We might move to chunked transfer in the future.
        #print('timeseries_id_list:', timeseries_id_list)

        # Debugging
        #timeseries = self.get_timeseries(timeseries_ids=[6895, 6931], timespan=self.filter.get('timespan'))

        # Fails
        #timeseries = self.get_timeseries(timeseries_ids=[1180, 6895], timespan=self.filter.get('timespan'))

        # For real
        timeseries = self.get_timeseries(timeseries_ids=timeseries_id_list, timespan=self.filter.get('timespan'))

        # Map timeseries to readings.
        timeseries_readings_map = {}
        for tsid, item in timeseries.items():
            print(tsid, item)
            timeseries_id = int(tsid)
            fieldname = timeseries_sensor_map[timeseries_id]['sensor_fieldname']
            data = self.reading_data_from_timeseries(fieldname, item['values'])
            data = list(data)
            # TODO: Emit warning here if station has no data whatsoever?
            if not data:
                continue
            timeseries_readings_map[timeseries_id] = data

        # Make readings for all stations, grouping by timestamp.
        items = []
        for station_id in sorted(station_map.keys()):
            station = station_map[station_id]
            all_data = []
            for sensor in station.sensors:

                timeseries_id = sensor['sensor_id']
                if timeseries_id not in timeseries_readings_map:
                    log.warning(f'Station "{station_id}" has no data for timeseries "{timeseries_id}"')
                    continue

                all_data += timeseries_readings_map[timeseries_id]

            item_station = deepcopy(station)
            del item_station['sensors']

            # Group by timestamp.
            timestamp_data_map = {}
            for data_item in all_data:
                timestamp = data_item['timestamp']
                #del data_item['timestamp']
                timestamp_data_map.setdefault(timestamp, {})
                timestamp_data_map[timestamp].update(data_item)

            # Build list of observations.
            observations = []
            for data in sorted(timestamp_data_map.values(), key=itemgetter('timestamp')):
                timestamp = data['timestamp']
                del data['timestamp']
                observation = munchify(dict(meta={'timestamp': timestamp}, data=data))
                observations.append(observation)

            # List of all readings by timestamp, ascending.
            item = Munch({
                'station': item_station,
                'observations': observations,
            })
            items.append(item)

        return items

    def get_timeseries(self, timeseries_ids=None, timespan=None):
        """
        - http://geo.irceline.be/sos/static/doc/api-doc/#timeseries-example-post-data
        - https://wiki.52north.org/SensorWeb/SensorWebClientRESTInterfaceV0#Timeseries_Data
        - https://en.wikipedia.org/wiki/ISO_8601#Time_intervals

        Valid "timespan" values are:
        - 2019-04-20T01:00:00+02:00/2019-04-22T01:00:00+02:00
        - 2019-04-20T01:00:00Z/PT0h
        - PT6h/2013-08-16TZ
        - P0Y0M3D/2013-01-31TZ

        Examples
        - Three hours worth of data from designated starting point for a specific timeseries::

            http POST 'http://geo.irceline.be/sos/api/v1/timeseries/getData' timeseries:='[6643]' timespan='2019-04-21T22:00:00+02:00/PT3h'

        - Get readings from two timeseries at specific time::

            http POST 'http://geo.irceline.be/sos/api/v1/timeseries/getData' timeseries:='[6643,6693]' timespan='2019-04-20T01:00:00Z/PT0h'

        """

        url = urljoin(self.uri, 'timeseries/getData')

        if timespan is None:
            timespan = f'{self.this_hour()}/PT0h'

        log.info(f'Requesting IRCELINE live API at {url} with timespan "{timespan}" and #{len(timeseries_ids)} timeseries')

        groupsize = 10
        identifiers_grouped = chunks(timeseries_ids, groupsize)
        identifiers_grouped = self.wrap_progress(identifiers_grouped, stepsize=groupsize)

        results = {}
        for identifiers in identifiers_grouped:
            log.debug(f'Requesting SOS timeseries {identifiers}')
            parameters = {'timespan': timespan, 'timeseries': identifiers}
            response = self.session.post(url, json=parameters, timeout=self.timeout)
            if response.headers['Content-Type'].startswith('application/json'):
                data = response.json()
                #print(data)
                results.update(data)
            else:
                log.error(f'Decoding response from IRCELINE failed\n{response.text}')

        return results

    def reading_data_from_timeseries(self, name, values):
        """
        Ingress
        =======
        ::

            values = [{'timestamp': 1556064000000, 'value': 172.0}, {'timestamp': 1556067600000, 'value': 162.0}]

        From::

            {
              "values": [
                {
                  "timestamp": 1556056800000,
                  "value": 36.1
                },
                {
                  "timestamp": 1556060400000,
                  "value": 34.6
                },
                {
                  "timestamp": 1556064000000,
                  "value": 33.1
                },
                {
                  "timestamp": 1556067600000,
                  "value": 32.6
                }
              ]
            }

        Egress
        ======
        ::

            {
              "time": "2019-04-24T00:52:32Z",
              "P1": 4.5,
              "P2": 3.5
            }

        """
        for observation in values:

            value = observation['value']

            # Skip empty or non-numeric values.
            # TODO: Emit warning here?
            if value is None or str(value).lower() == 'nan':
                continue

            entry = {
                'timestamp': self.convert_timestamp(observation['timestamp']),
                name: value,
            }
            yield entry

    @staticmethod
    def convert_timestamp(timestamp):
        datetime_object = datetime.fromtimestamp(timestamp / 1000)
        return rfc3339(datetime_object)

    @staticmethod
    def this_hour():
        now = datetime.now()
        now_aligned_to_hour = now - timedelta(minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        return rfc3339(now_aligned_to_hour)

    @staticmethod
    def slugify_fieldname(fieldname):
        return slugify(fieldname)
