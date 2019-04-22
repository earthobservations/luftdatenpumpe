# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
from copy import deepcopy
from collections import OrderedDict

import dataset
from munch import munchify
from geoalchemy2 import Geometry    # Pulls in PostGIS capabilities into SQLAlchemy
from sqlalchemy_utils import drop_database

log = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class RDBMSStorage:

    capabilities = ['stations']

    artefacts = munchify([
        {'name': 'ldi_stations', 'type': 'table', 'primary_id': 'station_id'},
        {'name': 'ldi_osmdata', 'type': 'table', 'primary_id': 'station_id'},
        {'name': 'ldi_sensors', 'type': 'table', 'primary_id': 'sensor_id'},
        {'name': 'ldi_network', 'type': 'view'},
    ])

    def __init__(self, uri, dry_run=False):

        self.dry_run = dry_run

        # Connect to database.
        self.db = dataset.connect(uri)

        # Ping database.
        self.ping_database()

        # Check for PostGIS extension.
        self.ensure_postgis()

        # Deploy the database schema.
        self.ensure_schema()

        self.tame_library_loggers()

        # Assign table handles.
        self.stationtable = self.db['ldi_stations']
        self.sensorstable = self.db['ldi_sensors']
        self.osmtable = self.db['ldi_osmdata']

    def emit(self, station):
        return self.store_station(station)

    def flush(self, final=False):
        pass

    def ping_database(self):
        failure = None
        try:
            self.db.query('SELECT TRUE;')

        except Exception as ex:
            failure = f'Database operation failed. Reason: {ex}'
            log.exception(failure, exc_info=False)

        if failure:
            raise DatabaseError(failure)

    def ensure_postgis(self):

        # TODO: Add PostGIS extension. However, this requires superuser permissions.
        # self.db.query('CREATE EXTENSION IF NOT EXISTS postgis')

        failure = None
        try:
            result = self.db.query('SELECT PostGIS_Full_Version();')
            postgis_full_version = list(result)[0]['postgis_full_version']
            log.info(f'PostGIS version: {postgis_full_version}')

        except Exception as ex:

            message = 'Database operation failed'
            if 'function postgis_full_version() does not exist' in str(ex):
                message = 'PostGIS extension not installed'

            failure = f'{message}. Reason: {ex}'
            log.exception(failure, exc_info=False)

        if failure:
            raise DatabaseError(failure)

    def ensure_schema(self):

        # Create tables.
        for tableinfo in self.tableinfos:
            self.db.create_table(tableinfo.name, primary_id=tableinfo.primary_id)

        # FIXME: Funny enough, this workaround helps after upgrading to PostgreSQL 11.
        repr(self.db._tables)

        # Enforce "ldi_osmdata.osm_id" and "ldi_osmdata.osm_place_id" to be of "bigint" type.
        # Otherwise: ``psycopg2.DataError: integer out of range`` with 'osm_id': 2678458514
        ldi_osmdata = self.db.get_table('ldi_osmdata')
        ldi_osmdata.create_column('osm_id', self.db.types.bigint)
        ldi_osmdata.create_column('osm_place_id', self.db.types.bigint)

        # Manually add "geopoint" field to the table because the "dataset"
        # package does not implement appropriate heuristics for that.
        self.db.query('ALTER TABLE ldi_stations ADD COLUMN IF NOT EXISTS "geopoint" geography(Point)')

    @property
    def tableinfos(self):
        for artefact in self.artefacts:
            if artefact.type == 'table':
                yield artefact

    @property
    def viewinfos(self):
        for artefact in self.artefacts:
            if artefact.type == 'view':
                yield artefact

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

    def create_views(self):

        # Inquire fields from osmdata table.
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

    def grant_read_privileges(self, user):
        sql = """
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {user};
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO {user};
        """.format(user=user)
        self.db.query(sql)

    def drop_tables(self):
        log.info('Dropping views and tables in database %s', self.db)

        for viewinfo in self.viewinfos:
            self.db.query('DROP VIEW IF EXISTS {}'.format(viewinfo.name))

        for tableinfo in self.tableinfos:
            table = self.db.get_table(tableinfo.name)
            table.drop()

    def drop_database(self):
        drop_database(self.db.engine.url)

    def drop_data(self):
        """
        Prune data from all tables.
        """
        for tablename in self.db.tables:
            if tablename.startswith('ldi_'):
                log.info('Deleting data from table {}'.format(tablename))
                self.db.query('DELETE FROM {}'.format(tablename))

    def get_all_view_names(self):
        from sqlalchemy import inspect
        inspector = inspect(self.db.engine)
        return inspector.get_view_names()

    def get_database_name(self):
        raise NotImplementedError('Defunct.')

        # https://stackoverflow.com/questions/53554458/sqlalchemy-get-database-name-from-engine/53558430#53558430
        from sqlalchemy import inspect
        inspector = inspect(self.db.engine)
        print(inspector)
        print(dir(inspector))
        print('url:', self.db.engine.url)
        #name = inspector.default_schema_name
        name = inspector.name
        return name

    def get_all_table_names(self):
        raise NotImplementedError('Defunct.')

        for table in self.db._tables.values():
            log.info('Dropping table %s', table.name)
            try:
                table.drop()
            except:
                log.warning('Skipped dropping table/view "%s"', table.name)

    @staticmethod
    def tame_library_loggers():
        logger = logging.getLogger('alembic.runtime.migration')
        logger.disabled = True
