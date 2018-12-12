# -*- coding: utf-8 -*-
# (c) 2018 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import types
import logging

from munch import Munch
from urllib.parse import urlparse

from luftdatenpumpe.target.influxdb import InfluxDBStorage
from luftdatenpumpe.target.stream import StreamTarget
from luftdatenpumpe.target.rdbms import RDBMSStorage
from luftdatenpumpe.target.mqtt import MQTTAdapter

log = logging.getLogger(__name__)


def json_formatter(data):
    if isinstance(data, types.GeneratorType):
        data = list(data)
    return json.dumps(data, indent=4)


def json_grafana_formatter(stations):
    entries = []
    for station in stations:
        if 'name' in station:
            station_name = station.name
        else:
            station_name = u'Station #{}, {}'.format(station.station_id, station.position.country)
        entry = {'value': station.station_id, 'text': station_name}
        entries.append(entry)
    return json_formatter(entries)


def resolve_target_handler(target, dry_run=False):
    handler = None

    url = Munch(urlparse(target)._asdict())
    log.debug('Resolving target: %s', json.dumps(url))

    formatter = lambda x: x
    if '+' in url.scheme:
        format, scheme = url.scheme.split('+')
        url.scheme = scheme
        if format.startswith('json.grafana'):
            formatter = json_grafana_formatter
        elif format.startswith('json'):
            formatter = json_formatter
        formatter.format = format

    #effective_url = urlunparse(url.values())

    if url.scheme == 'stream':

        # FIXME: There might be dragons?
        import sys
        stream = eval(url.netloc)

        handler = StreamTarget(stream, formatter)

    elif url.scheme in RDBMSStorage.get_dialects():
        handler = RDBMSStorage(target, dry_run=dry_run)

    elif url.scheme == 'mqtt':
        handler = MQTTAdapter(target, dry_run=dry_run)

    elif url.scheme == 'influxdb':
        handler = InfluxDBStorage(target, dry_run=dry_run)

    return handler
