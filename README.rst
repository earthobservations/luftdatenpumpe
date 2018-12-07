##############
Luftdatenpumpe
##############


*****
About
*****

Features:
- Request data from live API of luftdaten.info
- Enrich location data with geospatial information from OSM/Nominatim
- Display list of stations and readings
- Export list of stations to RDBMS database
- Forward readings to MQTT


****
Demo
****
- https://luftdaten.hiveeyes.org/grafana/d/bEe6HJamk/feinstaub-verlauf-berlin
- https://luftdaten.hiveeyes.org/grafana/d/000000004/feinstaub-karte-deutschland
- https://weather.hiveeyes.org/grafana/d/yDbjQ7Piz/stationslistengalerie


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
- `Support for InfluxDB and MQTT as backend <https://github.com/opendata-stuttgart/sensors-software/issues/33#issuecomment-272711445>`_.
- https://getkotori.org/docs/applications/luftdaten.info/
- https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199


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

> The append-only file is an alternative, fully-durable strategy for Redis. It became available in version 1.1.
> You can turn on the AOF in your Redis configuration file (e.g. `/etc/redis/redis.conf`)::
>
>   appendonly yes


Python module
=============
::

    # Not published yet, please install from repository
    pip install luftdatenpumpe


********
Synopsis
********

List stations
=============
::

    luftdatenpumpe stations --stations=28,297 --reverse-geocode



MQTT forwarding
===============
::

    luftdatenpumpe forward --stations=28,1071 --mqtt-uri mqtt://mqtt.example.org/luftdaten.info

With authentication::

    luftdatenpumpe forward --stations=28,1071 --mqtt-uri mqtt://username:password@mqtt.example.org/luftdaten.info


License
=======

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
