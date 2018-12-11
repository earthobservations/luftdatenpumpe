# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
import dataset
from copy import deepcopy
from collections import OrderedDict

log = logging.getLogger(__name__)


class RDBMSStorage:

    def __init__(self, uri, empty_tables=False):

        # TODO: Make datasource URI configurable.
        #self.db = dataset.connect('sqlite:///:memory:')
        #self.db = dataset.connect('postgres:///weatherbase_dev')
        #self.db = dataset.connect('postgres:///weatherbase')
        self.db = dataset.connect(uri)

        # Optionally, empty all tables
        if empty_tables:
            for tablename in self.db.tables:
                if tablename.startswith('ldi_'):
                    self.db.query('DELETE FROM {}'.format(tablename))

        # Create tables.
        self.db.create_table('ldi_stations', primary_id='id')
        self.db.create_table('ldi_osmdata', primary_id='station_id')
        self.db.create_table('ldi_sensors', primary_id='sensor_id')

        # Assign table handles.
        self.stationtable = self.db['ldi_stations']
        self.sensorstable = self.db['ldi_sensors']
        self.osmtable = self.db['ldi_osmdata']

    def emit(self, stations):
        return self.store_stations(stations)

    def store_stations(self, stations):

        for station in stations:

            # Debugging
            #log.info(station)

            # Station table
            stationdata = OrderedDict()
            stationdata['id'] = station.station_id
            for key, value in station.items():
                if key.startswith('name'):
                    stationdata[key] = value
            stationdata.update(station.position)
            self.stationtable.upsert(stationdata, ['id'])

            # Sensors table
            for sensor in station['sensors']:
                sensordata = {}
                sensordata['station_id'] = station['station_id']
                sensordata.update(sensor)
                self.sensorstable.upsert(sensordata, ['sensor_id'])

            # OSM table
            osmdata = {}
            osmdata['station_id'] = station['station_id']
            location = deepcopy(station['location'])
            for key, value in location['address'].items():
                #key = 'address_' + key
                location[key] = value
            del location['address']

            if 'address_more' in location:
                osmdata['address_more'] = json.dumps(location['address_more'])
                del location['address_more']

            # TODO: Also store bounding box
            del location['boundingbox']

            osmdata.update(location)
            self.osmtable.upsert(osmdata, ['station_id'])

    def dump_tables(self):
        for table in [self.stationtable, self.sensorstable, self.osmtable]:
            print('### Table name:', table.name)
            for record in table.all():
                print(self.json_markdown_dumps(record))
                print()

    def demo_query(self):

        #print(dir(self.stationtable.table))

        # https://dataset.readthedocs.io/en/latest/quickstart.html#running-custom-sql-queries
        expression = 'SELECT * FROM ldi_stations, ldi_osmdata WHERE ldi_stations.id = ldi_osmdata.station_id'
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
