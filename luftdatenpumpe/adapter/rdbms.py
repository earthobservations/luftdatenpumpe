# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
import dataset
from copy import deepcopy

log = logging.getLogger(__name__)


class RDBMSStorage:

    def __init__(self):

        # TODO: Make datasource URI configurable.
        #self.db = dataset.connect('sqlite:///:memory:')
        self.db = dataset.connect('postgres:///weatherbase_dev')
        #self.db = dataset.connect('postgres:///weatherbase')

        # Create tables.
        self.db.create_table('ldi_stations', primary_id='location_id')
        self.db.create_table('ldi_osmdata', primary_id='location_id')
        self.db.create_table('ldi_sensors', primary_id='location_id')

        # Assign table handles.
        self.stationtable = self.db['ldi_stations']
        self.osmtable = self.db['ldi_osmdata']
        self.sensorstable = self.db['ldi_sensors']

    def store_stations(self, stations):

        for _, station in stations.items():

            # Debugging
            #log.info(station)

            # Station table
            stationdata = deepcopy(station)
            del stationdata['location_info']
            del stationdata['sensors']
            self.stationtable.upsert(stationdata, ['location_id'])

            # Sensors table
            for _, sensor in station['sensors'].items():
                sensordata = {}
                sensordata['location_id'] = station['location_id']
                sensordata.update(sensor)
                self.sensorstable.upsert(sensordata, ['location_id'])

            # OSM table
            osmdata = {}
            osmdata['location_id'] = station['location_id']
            location_info = deepcopy(station['location_info'])
            for key, value in location_info['address'].items():
                key = 'address_' + key
                location_info[key] = value
            del location_info['address']
            del location_info['boundingbox']
            osmdata.update(location_info)
            self.osmtable.upsert(osmdata, ['location_id'])

    def dump_tables(self):
        for table in [self.stationtable, self.sensorstable, self.osmtable]:
            print('### Table name:', table.name)
            for record in table.all():
                print(self.json_markdown_dumps(record))
                print()

    def demo_query(self):

        #print(dir(self.stationtable.table))

        # https://dataset.readthedocs.io/en/latest/quickstart.html#running-custom-sql-queries
        expression = 'SELECT * FROM ldi_stations, ldi_osmdata WHERE ldi_stations.location_id = ldi_osmdata.location_id'
        print('### Expression:', expression)
        result = self.db.query(expression)
        for record in result:
            print(self.json_markdown_dumps(record))

    @staticmethod
    def json_markdown_dumps(thing):
        tpl = "```\n{}\n```"
        content = json.dumps(thing, indent=4)
        return tpl.format(content)
