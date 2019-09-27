# -*- coding: utf-8 -*-
# (c) 2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2019 Richard Pobering <richard@hiveeyes.org>
# (c) 2019 Matthias Mehldau <wetter@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging
from copy import deepcopy
from datetime import datetime, timedelta
from operator import itemgetter

from requests import HTTPError
from rfc3339 import rfc3339
from munch import munchify, Munch
from tablib import Dataset
from urllib.parse import urljoin
from collections import OrderedDict

from luftdatenpumpe.source.common import AbstractLuftdatenPumpe
from luftdatenpumpe.util import slugify, grouper, chunks

log = logging.getLogger(__name__)


class EEAAirQualityPumpe(AbstractLuftdatenPumpe):
    """
    Ingest air quality measurements from the
    European Environment Agency (EEA).

    - http://discomap.eea.europa.eu/map/fme/AirQualityExport.htm
    - http://ftp.eea.europa.eu/www/aqereporting-3/AQeReporting_products_2018_v1.pdf
    - http://dd.eionet.europa.eu/vocabulary/aq/pollutant

    """

    # Sensor network identifier.
    network = 'eea'

    # Download service REST API URI
    uri = 'https://ereporting.blob.core.windows.net/downloadservice/'

    timeout = 60

    def get_index(self):
        return self.send_request()

    def send_request(self, endpoint=None, params=None):
        url = urljoin(self.uri, endpoint)
        log.info(f'Requesting EEA at {url}')
        params = params or {}

        response = self.session.get(url, params=params, timeout=self.timeout)
        if response.status_code != 200:
            try:
                reason = response.json()
            except:
                reason = 'unknown'
            message = f'Request failed: {reason}'
            log.error(message)
            response.raise_for_status()

        return response.text

    def get_stations(self):
        """
        https://ereporting.blob.core.windows.net/downloadservice/metadata.csv
        """

        payload = self.send_request('metadata.csv')

        # Read CSV file into tablib's Dataset and cast to dictionary representation.
        try:
            data = Dataset().load(payload, format='csv', delimiter=',')
        except Exception:
            log.exception(f'Error reading or decoding station CSV')
            return

        # Apply data filter.
        data = self.apply_filter(data)

        df_grouped = data.df.groupby(['Countrycode', 'AirQualityNetwork', 'AirQualityStation'], as_index=False)

        stations = []
        for name, group in self.wrap_progress(df_grouped):
            first_sensor = group.head(1)
            data = first_sensor.to_dict(orient='records')[0]
            station_info = munchify({
                'station_id': data.pop('AirQualityStation'),
                'station_label': data.pop('Namespace'),
                'network': data.pop('AirQualityNetwork'),
                'nat_code': data.pop('AirQualityStationNatCode'),
                'eoi_code': data.pop('AirQualityStationEoICode'),
                'position': {
                    'country': data.pop('Countrycode'),
                    'latitude': data.pop('Latitude'),
                    'longitude': data.pop('Longitude'),
                    'altitude': data.pop('Altitude'),
                    'area': data.pop('AirQualityStationArea'),
                    'projection': data.pop('Projection'),
                    'building_distance': data.pop('BuildingDistance'),
                    'kerb_distance': data.pop('KerbDistance'),
                }
            })

            # Transfer all other stuff.
            #for key, value in data.items():
            #    station_info[key] = value

            #print('station_info:', station_info)
            #continue

            self.enrich_station(station_info)

            # FIXME: Add sensors.
            #station_info.sensors = self.timeseries_to_sensors(upstream_station.properties.timeseries)

            #print(station_info)
            stations.append(station_info)

        # List of stations sorted by station identifier.
        stations = sorted(stations, key=itemgetter('station_id'))

        return stations

    def filter_rule(self, data):
        print('FILTER:', self.filter)
        df_filtered = data.df
        if self.filter and 'country' in self.filter:
            df_filtered = df_filtered[df_filtered['Countrycode'].isin(self.filter.country)]

        data.df = df_filtered
        return data
