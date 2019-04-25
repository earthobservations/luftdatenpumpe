# -*- coding: utf-8 -*-
# (c) 2018-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging

from munch import munchify
from influxdb import InfluxDBClient

from luftdatenpumpe.util import sanitize_dbsymbol

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

log = logging.getLogger(__name__)


class InfluxDBStorage:

    capabilities = ['readings']

    def __init__(self, dsn, network=None, dry_run=False):

        self.dry_run = dry_run

        self.network = network or 'default'
        self.measurement = sanitize_dbsymbol(self.network) + '_readings'

        self.buffer = []
        self.is_udp = False

        # TODO: Use timeout value from settings.
        dsn_parts = urlparse(dsn)
        if dsn_parts.scheme.startswith('udp+'):
            self.is_udp = True
            self.db = InfluxDBClient.from_dsn(dsn, udp_port=dsn_parts.port, timeout=5)
        else:
            self.db = InfluxDBClient.from_dsn(dsn, timeout=5)
            self.db.create_database(self.db._database)

    def emit(self, reading):
        """
        Obtain a reading and store into InfluxDB.

        Ingress
        =======
        A reading coming in here looks like::

            {
              "station": {
                "station_id": 11391,
                "position": {
                  "latitude": 50.846,
                  "longitude": 4.414,
                  "altitude": 78.7,
                  "country": "BE",
                  "exact_location": 0,
                  "geohash": "u151k2npmtku"
                }
              },
              "observations": [
                {
                  "meta": {
                    "timestamp": "2019-04-24T18:08:53Z",
                    "sensor_id": 22448,
                    "sensor_type": "DHT22"
                  },
                  "data": {
                    "humidity": 91.8,
                    "temperature": 13.4
                  }
                }
              ]
            }


        Egress
        ======
        The designated output format suitable for feeding into InfluxDB looks like::

            {
              "measurement": "readings",
              "tags": {
                "station_id": 28,
                "sensor_id": 658
              },
              "time": "2018-12-12T02:21:08Z",
              "fields": {
                "P1": 13.35,
                "P2": 8.05
              }
            }

        """

        # Debugging
        if log.getEffectiveLevel() is logging.DEBUG:
            log.debug('Obtained reading for InfluxDB\n%s', json.dumps(reading, indent=2))

        # Build InfluxDB records.
        for observation in reading.observations:

            record = munchify({
                "measurement": self.measurement,
                "tags": {
                    "station_id": reading.station.station_id,
                },
            })

            if 'sensor_id' in observation.meta:
                record.tags.sensor_id = observation.meta.sensor_id

            if 'position' in reading.station and 'geohash' in reading.station.position:
                record.tags.geohash = reading.station.position.geohash

            record.time = observation.meta.timestamp
            record.fields = observation.data

            # Debugging.
            if log.getEffectiveLevel() is logging.DEBUG:
                log.debug('Emitting record to InfluxDB\n%s', json.dumps(record, indent=2))

            # Store into buffer.
            self.buffer.append(record)

        if self.is_udp and len(self.buffer) > 50:
            self.flush()

    def flush(self, final=False):
        # Store into database.
        #print('Writing points:', len(self.buffer))
        self.db.write_points(self.buffer)
        self.buffer = []
