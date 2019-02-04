# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
import dataset
from copy import deepcopy
from collections import OrderedDict
from geoalchemy2 import Geometry    # Pulls in PostGIS capabilities into SQLAlchemy

log = logging.getLogger(__name__)


class RDBMSStorage:

    capabilities = ['stations']

    def __init__(self, uri, empty_tables=False, dry_run=False):

        self.dry_run = dry_run

        # Connect to database.
        self.db = dataset.connect(uri)

        # Add PostGIS extension.
        self.db.query('CREATE EXTENSION IF NOT EXISTS postgis')

        # Optionally, empty all tables.
        if empty_tables:
            for tablename in self.db.tables:
                if tablename.startswith('ldi_'):
                    self.db.query('DELETE FROM {}'.format(tablename))

        # Create tables.
        self.db.create_table('ldi_stations', primary_id='station_id')
        self.db.create_table('ldi_osmdata', primary_id='station_id')
        self.db.create_table('ldi_sensors', primary_id='sensor_id')

        # Assign table handles.
        self.stationtable = self.db['ldi_stations']
        self.sensorstable = self.db['ldi_sensors']
        self.osmtable = self.db['ldi_osmdata']

        # Add "geopoint" field to table.
        self.db.query('ALTER TABLE ldi_stations ADD COLUMN IF NOT EXISTS "geopoint" geography(Point)')

    def emit(self, station):
        return self.store_station(station)

    def flush(self, final=False):
        pass

    def store_station(self, station):

        # Make up geoposition on the fly
        # In mapping frameworks spatial coordinates are often in order of latitude and longitude.
        # In spatial databases spatial coordinates are in x = longitude, and y = latitude.
        # -- https://postgis.net/2013/08/18/tip_lon_lat/
        # Example: Stuttgart == POINT(9.17721 48.77928)
        if station.position and station.position.latitude and station.position.longitude:
            station.position.geopoint = 'POINT({} {})'.format(station.position.longitude, station.position.latitude)

        # Debugging
        #log.info('station: %s', station)

        # Station table
        stationdata = OrderedDict()
        stationdata['station_id'] = station.station_id
        for key, value in station.items():
            if key.startswith('name'):
                stationdata[key] = value
        stationdata.update(station.position)
        self.stationtable.upsert(stationdata, ['station_id'])

        # Sensors table
        for sensor in station['sensors']:
            sensordata = OrderedDict()
            sensordata['station_id'] = station.station_id
            sensordata.update(sensor)
            self.sensorstable.upsert(sensordata, ['sensor_id'])

        # OSM table
        if 'location' in station:
            osmdata = OrderedDict()
            osmdata['station_id'] = station.station_id
            location = deepcopy(station.location)
            for key, value in location.address.items():
                #key = 'address_' + key
                location[key] = value
            del location['address']

            if 'address_more' in location:
                osmdata['address_more'] = json.dumps(location.address_more)
                del location['address_more']

            # TODO: Also store bounding box
            del location['boundingbox']

            osmdata.update(location)

            # Prefix designated column name with 'osm_'.
            osmdata_real = OrderedDict()
            for key, value in osmdata.items():
                if key not in ['station_id']:
                    if not key.startswith('osm_'):
                        key = 'osm_' + key
                osmdata_real[key] = value

            self.osmtable.upsert(osmdata_real, ['station_id'])

    def dump_tables(self):
        for table in [self.stationtable, self.sensorstable, self.osmtable]:
            print('### Table name:', table.name)
            for record in table.all():
                print(self.json_markdown_dumps(record))
                print()

    def demo_query(self):

        #print(dir(self.stationtable.table))

        # https://dataset.readthedocs.io/en/latest/quickstart.html#running-custom-sql-queries
        expression = 'SELECT * FROM ldi_stations, ldi_osmdata WHERE ldi_stations.station_id = ldi_osmdata.station_id'
        print('### Expression:', expression)
        result = self.db.query(expression)
        for record in result:
            print(self.json_markdown_dumps(record))

    @staticmethod
    def json_markdown_dumps(thing):
        tpl = "```\n{}\n```"
        content = json.dumps(thing, indent=4)
        return tpl.format(content)

    @classmethod
    def get_dialects(cls):
        results = []
        try:
            from sqlalchemy.dialects import __all__ as sql_dialects
            results = list(sql_dialects)
        except:
            pass
        #log.info('SQLAlchemy dialects: %s', results)
        return results

    def create_view(self):

        # Inquire osmdata fields.
        osmdata = self.db.query("""
            SELECT concat(TABLE_NAME, '.', COLUMN_NAME) AS name
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='ldi_osmdata' AND COLUMN_NAME NOT IN ('station_id')
            ORDER BY ORDINAL_POSITION
        """)
        osmdata_columns = []
        for record in osmdata:
            osmdata_columns.append(record['name'])

        # Create unified view.
        osmdata_columns_expression = ', '.join(osmdata_columns)
        view = """
        DROP VIEW IF EXISTS ldi_network;
        CREATE VIEW ldi_network AS
            SELECT
              ldi_stations.station_id,
              ldi_stations.name, ldi_stations.country, 
              ldi_stations.longitude, ldi_stations.latitude, ldi_stations.altitude, 
              ldi_stations.geohash, ldi_stations.geopoint,
              ldi_sensors.sensor_id, ldi_sensors.sensor_type,
              concat(ldi_osmdata.osm_state, ' » ', ldi_osmdata.osm_city) AS state_and_city,
              concat(ldi_stations.name, ' (#', CAST(ldi_stations.station_id AS text), ')') AS name_and_id,
              concat(ldi_osmdata.osm_country, ' (', ldi_osmdata.osm_country_code, ')') AS country_and_countrycode,
              concat(concat_ws(', ', ldi_osmdata.osm_state, ldi_osmdata.osm_country), ' (', ldi_osmdata.osm_country_code, ')') AS state_and_country,
              concat(concat_ws(', ', ldi_osmdata.osm_city, ldi_osmdata.osm_state, ldi_osmdata.osm_country), ' (', ldi_osmdata.osm_country_code, ')') AS city_and_state_and_country,
              {}
            FROM
              ldi_stations, ldi_osmdata, ldi_sensors
            WHERE
              ldi_stations.station_id = ldi_osmdata.station_id AND
              ldi_stations.station_id = ldi_sensors.station_id
            ORDER BY
              osm_country_code, state_and_city, name_and_id, sensor_type
        """.format(osmdata_columns_expression)
        self.db.query(view)
