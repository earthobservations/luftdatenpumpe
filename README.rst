##############
Luftdatenpumpe
##############


*****
About
*****
1. Luftdatenpumpe_ acquires the current window of measurement readings from the livedata API of `luftdaten.info`_.

2. While iterating the readings, it collects information about all stations and sensors they are originating from.

3. Then, each stations location information gets enhanced by

    - attaching its geospatial position as a Geohash_.
    - attaching a synthetic real-world address resolved using the reverse geocoding service Nominatim_ by OpenStreetMap_.

4. The resulting data can be

    - displayed on STDOUT or STDERR.
    - stored into RDBMS_ databases using the fine dataset_ package.
      Being built on top of SQLAlchemy_, this supports all major RDBMS_ databases.
    - forwarded to MQTT_.

.. _luftdaten.info: http://luftdaten.info/
.. _Luftdatenpumpe: https://github.com/hiveeyes/luftdatenpumpe
.. _Erneuerung der Luftdatenpumpe: https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199
.. _The Hiveeyes Project: https://hiveeyes.org/

.. _OpenStreetMap: https://en.wikipedia.org/wiki/OpenStreetMap
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. _Geohash: https://en.wikipedia.org/wiki/Geohash
.. _dataset: https://dataset.readthedocs.io/
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _RDBMS: https://en.wikipedia.org/wiki/Relational_database_management_system
.. _MQTT: http://mqtt.org/


****
Demo
****

Live Data
==========
- `Feinstaub Verlauf Berlin <https://luftdaten.hiveeyes.org/grafana/d/bEe6HJamk/feinstaub-verlauf-berlin>`_
- `Feinstaub Karte Deutschland <https://luftdaten.hiveeyes.org/grafana/d/000000004/feinstaub-karte-deutschland>`_

List of stations
================
- `LDI Stations #1 » Select by name, country and state <https://weather.hiveeyes.org/grafana/d/yDbjQ7Piz/amo-ldi-stations-1-select-by-name-country-and-state>`_
- `LDI Stations #2 » Cascaded » Stations <https://weather.hiveeyes.org/grafana/d/Oztw1OEmz/amo-ldi-stations-2-cascaded-stations>`_
- `LDI Stations #3 » Cascaded » Measurements <https://weather.hiveeyes.org/grafana/d/lT4lLcEiz/amo-ldi-stations-3-cascaded-measurements>`_
- `LDI Stations #4 » Select by sensor type <https://weather.hiveeyes.org/grafana/d/kMIweoPik/amo-ldi-stations-4-select-by-sensor-type>`_


********
Synopsis
********

Overview
========
::

    # List stations
    luftdatenpumpe stations --station=28,297 --reverse-geocode

    # Write list of stations and metadata to PostgreSQL database
    luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=postgresql:///weatherbase

    # Forward readings to MQTT
    luftdatenpumpe readings --station=28,1071 --target=mqtt://mqtt.example.org/luftdaten.info


Details
=======
::

    $ luftdatenpumpe --help
        Usage:
          luftdatenpumpe stations [options] [--target=<target>]...
          luftdatenpumpe readings [options] [--target=<target>]...
          luftdatenpumpe --version
          luftdatenpumpe (-h | --help)

        Options:
          --station=<stations>          Filter data by given location ids, comma-separated.
          --sensor=<sensors>            Filter data by given sensor ids, comma-separated.
          --reverse-geocode             Compute geographical address using the Nominatim reverse geocoder and add to MQTT message
          --target=<target>             Data output target
          --progress                    Show progress bar
          --version                     Show version information
          --dry-run                     Run data acquisition and postprocessing but skip publishing to MQTT bus
          --debug                       Enable debug messages
          -h --help                     Show this screen

        Station list examples:

          # Display metadata for given stations in JSON format
          luftdatenpumpe stations --station=28,1071 --reverse-geocode

          # Display metadata for given sensors in JSON format
          luftdatenpumpe stations --sensor=657,2130 --reverse-geocode

          # Display list of stations in JSON format, suitable for integrating with Grafana
          luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=json.grafana+stream://sys.stdout

          # Write list of stations and metadata to PostgreSQL database, also display on STDERR
          luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=postgresql:///weatherbase --target=json+stream://sys.stderr

        Data examples:

          # Publish data to topic "luftdaten.info" at MQTT broker "mqtt.example.org"
          luftdatenpumpe readings --station=28,1071 --target=json+stream://sys.stderr --target=mqtt://mqtt.example.org/luftdaten.info

          # MQTT publishing, with authentication
          luftdatenpumpe readings --station=28,1071 --target=mqtt://username:password@mqtt.example.org/luftdaten.info


*****
Setup
*****

Prerequisites
=============
Debian packages::

    apt install postgis redis-server redis-tools


Postgres database
-----------------
Create database::

    createuser --no-createdb --pwprompt hiveeyes
    createdb --owner hiveeyes weatherbase

Create read-only user::

    su - postgres
    psql

    postgres=# \c weatherbase
    weatherbase=# CREATE ROLE readonly WITH LOGIN PASSWORD 'XXX';
    weatherbase=# GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly;
    weatherbase=# GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;


Redis cache
-----------
This program extensively uses a runtime cache based on Redis.
To make this work best, you should enable data durability with your Redis instance.

    The append-only file is an alternative, fully-durable strategy for Redis. It became available in version 1.1.
    You can turn on the AOF in your Redis configuration file (e.g. `/etc/redis/redis.conf`)::

        appendonly yes


Python module
=============
::

    # Not published yet, please install from repository
    pip install luftdatenpumpe



**********
References
**********

Upstream luftdaten.info
=======================
- http://luftdaten.info/
- http://archive.luftdaten.info/
- http://deutschland.maps.luftdaten.info/

Standing on the shoulders of giants
===================================
- https://github.com/vinsci/geohash/
- https://github.com/openstreetmap/Nominatim
- https://github.com/influxdata/influxdb
- https://github.com/grafana/grafana
- https://grafana.com/plugins/grafana-worldmap-panel

Development
===========
- `opendata-stuttgart/sensors-software: Support for InfluxDB and MQTT as backend <https://github.com/opendata-stuttgart/sensors-software/issues/33#issuecomment-272711445>`_.
- https://getkotori.org/docs/applications/luftdaten.info/
- https://community.hiveeyes.org/t/datenmischwerk/702
- https://community.hiveeyes.org/t/environmental-metadata-library/1190
- https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199



*******
License
*******
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program; if not, see:
<http://www.gnu.org/licenses/agpl-3.0.txt>,
or write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
