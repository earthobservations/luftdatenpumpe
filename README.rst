.. image:: https://img.shields.io/badge/Python-2.7,%203.6-green.svg
    :target: https://pypi.org/project/luftdatenpumpe/

.. image:: https://img.shields.io/pypi/v/luftdatenpumpe.svg
    :target: https://pypi.org/project/luftdatenpumpe/

.. image:: https://img.shields.io/github/tag/hiveeyes/luftdatenpumpe.svg
    :target: https://github.com/hiveeyes/luftdatenpumpe

.. image:: https://assets.okfn.org/images/ok_buttons/od_80x15_red_green.png
    :target: https://github.com/hiveeyes/luftdatenpumpe

.. image:: https://assets.okfn.org/images/ok_buttons/oc_80x15_blue.png
    :target: https://github.com/hiveeyes/luftdatenpumpe

.. image:: https://assets.okfn.org/images/ok_buttons/os_80x15_orange_grey.png
    :target: https://github.com/hiveeyes/luftdatenpumpe

|

##############
Luftdatenpumpe
##############

Process live and historical data from `luftdaten.info`_. Filter by station-id, sensor-id
and sensor-type, apply reverse geocoding, store into timeseries and RDBMS_ databases
(InfluxDB_ and PostGIS_), publish to MQTT_ or just output as JSON.

For running advanced GIS queries against the created PostGIS_ database,
please follow up at the `GIS documentation <doc-postgis_>`_.

.. figure:: https://cdn.jsdelivr.net/gh/hiveeyes/luftdatenpumpe@master/doc/logo.svg
    :target: https://github.com/hiveeyes/luftdatenpumpe
    :height: 200px
    :width: 200px


*****
About
*****
1. Luftdatenpumpe_ acquires the measurement readings either from the livedata API
   of `luftdaten.info`_ or from its archived CSV files published to `archive.luftdaten.info`.
   To minimize impact on the upstream servers, all data gets reasonably cached.

2. While iterating the readings, it optionally filters on station-id, sensor-id or sensor-type
   and restrains information processing to the corresponding stations and sensors.

3. Then, each station's location information gets enhanced by

    - attaching its geospatial position as a Geohash_.
    - attaching a synthetic real-world address resolved using the reverse geocoding service Nominatim_ by OpenStreetMap_.

4. Information about stations can be

    - displayed on STDOUT or STDERR in JSON format.
    - filtered and transformed interactively through jq_, the swiss army knife of JSON manipulation.
    - stored into RDBMS_ databases like PostgreSQL_ using the fine dataset_ package.
      Being built on top of SQLAlchemy_, this supports all major databases.

5. Measurement readings can be

    - displayed on STDOUT or STDERR in JSON format, which allows for piping into jq_ again.
    - forwarded to MQTT_.
    - stored to InfluxDB_ and then
    - displayed in Grafana_.


***********
Screenshots
***********
Display luftdaten.info (LDI) measurements on Grafana Worldmap Panel.


Worldmap and address
====================
Map and station info display. Filter by different synthesized address components and sensor type.

.. image:: https://community.hiveeyes.org/uploads/default/original/2X/f/f455d3afcd20bfa316fefbe69e43ca2fe159e62d.png
    :target: https://weather.hiveeyes.org/grafana/d/9d9rnePmk/amo-ldi-stations-5-map-by-sensor-type


Map overlay
===========
Display verbose name from OSM address and station id on overlay.

.. image:: https://community.hiveeyes.org/uploads/default/original/2X/4/48eeda1a1d418eaf698b241a65080666abcf2497.png
    :target: https://weather.hiveeyes.org/grafana/d/9d9rnePmk/amo-ldi-stations-5-map-by-sensor-type


*********
Live data
*********

Canonical dashboards
====================
- `Feinstaub Verlauf <https://weather.hiveeyes.org/grafana/d/ioUrPwQiz/luftdaten-info-verlauf>`_
- `Feinstaub Karte <https://weather.hiveeyes.org/grafana/d/AOerEQQmk/luftdaten-info-karte>`_

Labs
====
- `LDI Demo #1 » Stations by name, country and state <https://weather.hiveeyes.org/grafana/d/yDbjQ7Piz/amo-ldi-stations-1-select-by-name-country-and-state>`_
- `LDI Demo #2 » Cascaded stations <https://weather.hiveeyes.org/grafana/d/Oztw1OEmz/amo-ldi-stations-2-cascaded-stations>`_
- `LDI Demo #3 » Measurements by cascaded location selector <https://weather.hiveeyes.org/grafana/d/lT4lLcEiz/amo-ldi-stations-3-cascaded-measurements>`_
- `LDI Demo #4 » Find stations by sensor type <https://weather.hiveeyes.org/grafana/d/kMIweoPik/amo-ldi-stations-4-select-by-sensor-type>`_
- `LDI Demo #5 » Map by location and sensor type <https://weather.hiveeyes.org/grafana/d/9d9rnePmk/amo-ldi-stations-5-map-by-sensor-type>`_


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

For a **full** overview about all program options including meaningful examples,
you might just want to run ``luftdatenpumpe --help`` on your command line
or visit `luftdatenpumpe --help`_.

Details
=======
::

    Usage:
      luftdatenpumpe stations [options] [--target=<target>]...
      luftdatenpumpe readings [options] [--target=<target>]...
      luftdatenpumpe grafana --kind=<kind> --name=<name> [--variables=<variables>]
      luftdatenpumpe --version
      luftdatenpumpe (-h | --help)

    Options:
      --source=<source>             Data source, either "api" or "file://" [default: api].
      --station=<stations>          Filter data by given location ids, comma-separated.
      --sensor=<sensors>            Filter data by given sensor ids, comma-separated.
      --sensor-type=<sensor-types>  Filter data by given sensor types, comma-separated.
      --reverse-geocode             Compute geographical address using the Nominatim reverse geocoder
      --target=<target>             Data output target
      --create-database-view        Create database view like "ldi_view" spanning all tables.
      --disable-nominatim-cache     Disable Nominatim reverse geocoder cache
      --progress                    Show progress bar
      --version                     Show version information
      --dry-run                     Skip publishing to MQTT bus
      --debug                       Enable debug messages
      -h --help                     Show this screen



*****
Setup
*****


Configure package repository
============================
Hiveeyes is hosting recent releases of InfluxDB and Grafana there.
We are mostly also running exactly these releases on our production servers.

Add Hiveeyes package repository::

    wget -qO - https://packages.hiveeyes.org/hiveeyes/foss/debian/pubkey.txt | apt-key add -

Add Hiveeyes package repository, e.g. by appending this to ``/etc/apt/sources.list``::

    deb https://packages.hiveeyes.org/hiveeyes/foss/debian/ testing main foundation

Reindex package database::

    apt install apt-transport-https
    apt update


Install packages
================
Debian packages::

    apt install postgis redis-server redis-tools influxdb grafana


Configure PostgreSQL
====================
Create user and database::

    su - postgres
    createuser --no-createdb --pwprompt hiveeyes
    createdb --owner hiveeyes weatherbase

Create read-only user::

    psql

    postgres=# \c weatherbase
    weatherbase=# CREATE ROLE readonly WITH LOGIN PASSWORD 'readonly';
    weatherbase=# GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly;
    weatherbase=# GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

.. note::

    This probably has to be performed **after** the database has been created
    and populated. All the tables and sequences have not been materialized
    here after all at this point. So please bear with the current state of the
    documentation and apply some own creativity to the outlined installation
    process. This is really just a rough guide for moderately experienced users.


Configure Redis
===============
This program extensively uses a runtime cache based on Redis.
To make this work best, you should enable data durability with your Redis instance.

    The append-only file is an alternative, fully-durable strategy for Redis. It became available in version 1.1.
    You can turn on the AOF in your Redis configuration file (e.g. `/etc/redis/redis.conf`)::

        appendonly yes


Install Luftdatenpumpe
======================
::

    apt install build-essential python3-dev libicu-dev

::

    pip install luftdatenpumpe

.. note::

    We recommend to use a Python `virtualenv <doc-virtualenv_>`_ to install and operate this
    software independently from your local system-wide Python installation.

.. note::

    ``luftdatenpumpe`` depends on the PyICU package.
    Sometimes, ``pkg-config`` is not able to find the appropriate ICU installation, like::

        RuntimeError:
        Please set the ICU_VERSION environment variable to the version of
        ICU you have installed.

    So, you might try to do things like::

        $ export PKG_CONFIG_PATH="/usr/local/opt/icu4c/lib/pkgconfig"
        $ pkg-config --modversion icu-i18n
        63.1


*******
Running
*******
At this point, you should try to conduct simple tests
like outlined in the synopsis section above.

After that, you might want to advance into reading about
`integrating Luftdatenpumpe with Grafana`_ in order to learn about
how to build such beautiful and interactive map- and graph-compositions.



**********
References
**********

luftdaten.info
==============
- http://luftdaten.info/
- http://archive.luftdaten.info/
- http://deutschland.maps.luftdaten.info/

Resources
=========
- `opendata-stuttgart/sensors-software: Support for InfluxDB and MQTT as backend <https://github.com/opendata-stuttgart/sensors-software/issues/33#issuecomment-272711445>`_.
- https://getkotori.org/docs/applications/luftdaten.info/
- https://community.hiveeyes.org/t/datenmischwerk/702
- https://community.hiveeyes.org/t/environmental-metadata-library/1190
- https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199
- https://community.hiveeyes.org/t/ldi-dataplane-v2/1412

Technologies
============
Standing on the shoulders of giants.

Databases
---------
- https://github.com/influxdata/influxdb
- https://dataset.readthedocs.io/
- https://www.sqlalchemy.org/
- https://www.postgresql.org/
- https://postgis.net/
- https://github.com/pramsey/pgsql-http
- https://redis.io/

Software and services
---------------------
- https://github.com/grafana/grafana
- https://grafana.com/plugins/grafana-worldmap-panel
- https://en.wikipedia.org/wiki/Geohash
- https://nominatim.org/



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


********************
Content attributions
********************
The copyright of particular images and pictograms are held by their respective owners, unless otherwise noted.

Icons and pictograms
====================
- `Water Pump Free Icon <https://www.onlinewebfonts.com/icon/97990>`_ from
  `Icon Fonts <http://www.onlinewebfonts.com/icon>`_ is licensed by CC BY 3.0.



.. _doc-virtualenv: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/virtualenv.rst
.. _doc-postgis: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/postgis.rst


.. _luftdaten.info: https://luftdaten.info/
.. _Luftdatenpumpe: https://github.com/hiveeyes/luftdatenpumpe
.. _integrating Luftdatenpumpe with Grafana: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/grafana.rst
.. _luftdatenpumpe --help: https://github.com/hiveeyes/luftdatenpumpe/blob/master/doc/running.rst
.. _Erneuerung der Luftdatenpumpe: https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199

.. _The Hiveeyes Project: https://hiveeyes.org/

.. _OpenStreetMap: https://en.wikipedia.org/wiki/OpenStreetMap
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. _Geohash: https://en.wikipedia.org/wiki/Geohash
.. _dataset: https://dataset.readthedocs.io/
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _RDBMS: https://en.wikipedia.org/wiki/Relational_database_management_system
.. _MQTT: http://mqtt.org/

.. _PostgreSQL: https://www.postgresql.org/
.. _PostGIS: https://postgis.net/
.. _InfluxDB: https://github.com/influxdata/influxdb
.. _Grafana: https://github.com/grafana/grafana

.. _jq: https://stedolan.github.io/jq/
