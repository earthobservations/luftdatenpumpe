# -*- coding: utf-8 -*-
# (c) 2018-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import types
import logging


log = logging.getLogger(__name__)


def json_formatter(data):
    if isinstance(data, types.GeneratorType):
        data = list(data)
    return json.dumps(data, indent=2)


def json_grafana_formatter_base(stations):
    entries = []
    for station in stations:
        if 'name' in station:
            station_name = station.name
        else:
            station_name = u'Station #{}, {}'.format(station.station_id, station.position.country)
        entry = {'value': station.station_id, 'text': station_name}
        entries.append(entry)
    return entries


def json_grafana_formatter_vt(stations):
    """
    Format list of stations in JSON format made of value/text items,
    suitable for use as a Grafana JSON data source.

    Example::

        luftdatenpumpe stations --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.grafana.vt+stream://sys.stdout

    Emits items like::

        {
            "value": 22,
            "text": "Steglen, Haslach, Herrenberg, Vereinbarte  der Stadt Herrenberg, Baden-W\u00fcrttemberg, DE"
        }

    """
    entries = json_grafana_formatter_base(stations)
    return json_formatter(entries)


def json_grafana_formatter_kn(stations):
    """
    Format list of stations in JSON format made of key/name items,
    suitable for use as a mapping in Grafana Worldmap Panel.

    Example::

        luftdatenpumpe stations --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.grafana.kn+stream://sys.stdout

    Emits items like::

        {
            "key": "22",
            "name": "Steglen, Haslach, Herrenberg, Vereinbarte  der Stadt Herrenberg, Baden-W\u00fcrttemberg, DE"
        }

    """
    entries = []
    for station in json_grafana_formatter_base(stations):
        entry = {'key': str(station['value']), 'name': station['text']}
        entries.append(entry)
    return json_formatter(entries)
