# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017-2019 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging
from munch import munchify
from urllib.parse import urljoin
from collections import OrderedDict
from luftdatenpumpe.source.common import AbstractLuftdatenPumpe


log = logging.getLogger(__name__)


class IrcelinePumpe(AbstractLuftdatenPumpe):
    """
    This is for ingesting air quality measurements from the
    Belgian Interregional Environment Agency (IRCEL - CELINE).

    - http://www.irceline.be/en
    - http://deus.irceline.be/
    - https://en.vmm.be/
    - https://project-corona.eu/

    - http://geo.irceline.be/sos/static/doc/api-doc/

    """

    uri = 'http://geo.irceline.be/sos/api/v1/'

    def get_index(self):
        return self.send_request()

    def send_request(self, endpoint=None, params=None):
        url = urljoin(self.uri, endpoint)
        log.info(f'Requesting IRCELINE live API at {url}')
        params = params or {}
        return self.session.get(url, params=params).json()

    def get_stations(self):
        """
        http://geo.irceline.be/sos/api/v1/stations/?service=1&expand=true&locale=en
        """

        if self.filter:
            raise NotImplementedError('Filtering not supported for IRCELINE/SOS yet')

        data = self.send_request('stations', params={'expanded': 'true'})
        #print(json.dumps(data))
        #sys.exit(0)

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

        return stations

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
        property_names = ['phenomenon', 'procedure', 'feature', 'service']
        for sensor_id, timeseries in measurements.items():
            sensor = OrderedDict()
            sensor['sensor_id'] = int(sensor_id)
            for property_name in property_names:
                sensor[f'sensor_{property_name}_id'] = int(timeseries[property_name]['id'])
                sensor[f'sensor_{property_name}_label'] = timeseries[property_name]['label']
            sensor['sensor_type'] = sensor['sensor_phenomenon_label']
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

    def get_timeseries(self):
        """
        http://geo.irceline.be/sos/api/v1/timeseries/?service=1&phenomenon=6001&expanded=true&force_latest_values=true&status_intervals=true&rendering_hints=true&locale=en
        """

    def get_data(self):
        """
        http://geo.irceline.be/sos/api/v1/timeseries/6001/getData?timespan=2019-04-21T22%3A00%3A00%2B02%3A00%2F2019-04-23T01%3A59%3A59%2B02%3A00
        http POST 'http://geo.irceline.be/sos/api/v1/timeseries/getData' timespan='2019-04-21T22:00:00+02:00/PT1S' timeseries:='[6643,6693]' expanded=true

        :return:
        """
        pass
