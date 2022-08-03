# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017-2019 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
from munch import munchify

from luftdatenpumpe.target.rdbms import RDBMSStorage
from luftdatenpumpe.util import sanitize_dbsymbol


def stations_from_rdbms(dsuri, prefix):
    """
    Re-make station information from PostgreSQL database.

    Example::

        {
            "station_id": 28,
            "name": "Ulmer Stra\u00dfe, Wangen, Stuttgart, Baden-W\u00fcrttemberg, DE",
            "position": {
                "latitude": 48.778,
                "longitude": 9.236,
                "altitude": 223.7,
                "country": "DE",
                "geohash": "u0wt6pv2qqhz"
            },
            "location": {
                "place_id": "10504194",
                "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
                "osm_type": "way",
                "osm_id": "115374184",
                "lat": "48.777845",
                "lon": "9.23582396156841",
                "display_name": "Kulturhaus ARENA, 241, Ulmer Stra\u00dfe, Wangen, Stuttgart, Regierungsbezirk Stuttgart, Baden-W\u00fcrttemberg, 70327, Deutschland",
                "boundingbox": [
                    "48.7775199",
                    "48.778185",
                    "9.2353783",
                    "9.236272"
                ],
                "address": {
                    "country_code": "DE",
                    "country": "Deutschland",
                    "state": "Baden-W\u00fcrttemberg",
                    "state_district": "Regierungsbezirk Stuttgart",
                    "county": "Stuttgart",
                    "postcode": "70327",
                    "city": "Stuttgart",
                    "city_district": "Wangen",
                    "suburb": "Wangen",
                    "road": "Ulmer Stra\u00dfe",
                    "house_number": "241",
                    "neighbourhood": "Wangen"
                },
                "address_more": {
                    "building": "Kulturhaus ARENA"
                }
            },
            "sensors": [
                {
                    "sensor_id": 658,
                    "sensor_type": "SDS011"
                },
                {
                    "sensor_id": 657,
                    "sensor_type": "DHT22"
                }
            ]
        }
    """

    for station in fetch_from_rdbms(dsuri, prefix):
        entry = {
            "station_id": station.station_id,
            "name": station.name,
            "position": {
                "latitude": station.latitude,
                "longitude": station.longitude,
                "altitude": station.altitude,
                "country": station.country,
                "geohash": station.geohash,
            },
        }
        yield munchify(entry)


def stations_from_rdbms_flex(dsuri, prefix):
    return fetch_from_rdbms(dsuri, prefix)


def fetch_from_rdbms(dsuri, prefix):
    # Sanitize table name.
    prefix = sanitize_dbsymbol(prefix)

    sql = f"""
        SELECT *
        FROM {prefix}_network
        ORDER BY
          {prefix}_network.station_id
    """

    storage = RDBMSStorage(dsuri)
    for station in storage.db.query(sql):
        yield munchify(station)
