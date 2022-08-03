# -*- coding: utf-8 -*-
# (c) 2018-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
import types
from collections import OrderedDict

log = logging.getLogger(__name__)


def json_formatter(data):
    if isinstance(data, types.GeneratorType):
        data = list(data)
    return json.dumps(data, indent=2)


def curated_station_list(stations):
    seen = {}
    for station in stations:
        if station.station_id in seen:
            continue
        if "name" not in station:
            station.name = "Station #{}, {}".format(station.station_id, station.position.country)
        seen[station.station_id] = True
        yield station


class JsonFlexFormatter:
    def __init__(self, fieldmap):
        self.fieldmap = fieldmap

    def formatter(self, stations):
        entries = []
        for station in curated_station_list(stations):
            entry = OrderedDict()
            for key_left, key_right in self.fieldmap.items():

                # Compute value, optionally applying conversion.
                conversion = None
                if "|" in key_right:
                    key_right, conversion = key_right.split("|")
                value = station[str(key_right)]
                if conversion is not None:
                    converter = eval(conversion)
                    value = converter(value)

                entry[str(key_left)] = value

            entries.append(entry)
        return json_formatter(entries)


def json_grafana_formatter_vt(stations):
    """
    Format list of stations in JSON format made of value/text items,
    suitable for use as a Grafana JSON data source.

    Example::

        luftdatenpumpe stations \
            --source=postgresql://luftdatenpumpe@localhost/weatherbase \
            --target=json.grafana.vt+stream://sys.stdout

    Emits items like::

        {
            "value": 22,
            "text": "Steglen, Haslach, Herrenberg, Vereinbarte  der Stadt Herrenberg, Baden-W\u00fcrttemberg, DE"
        }

    """
    entries = []
    for station in curated_station_list(stations):
        entry = {"value": str(station.station_id), "text": station.name}
        entries.append(entry)
    return json_formatter(entries)


def json_grafana_formatter_kn(stations):
    """
    Format list of stations in JSON format made of key/name items,
    suitable for use as a mapping in Grafana Worldmap Panel.

    Example::

        luftdatenpumpe stations \
            --source=postgresql://luftdatenpumpe@localhost/weatherbase \
            --target=json.grafana.kn+stream://sys.stdout

    Emits items like::

        {
            "key": "22",
            "name": "Steglen, Haslach, Herrenberg, Vereinbarte  der Stadt Herrenberg, Baden-W\u00fcrttemberg, DE"
        }

    """
    entries = []
    for station in curated_station_list(stations):
        entry = {"key": str(station.station_id), "name": station.name}
        entries.append(entry)
    return json_formatter(entries)
