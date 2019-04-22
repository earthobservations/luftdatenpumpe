##########################
Luftdaten-Viewer Databases
##########################


*******
PostGIS
*******


Create and provision PostGIS database
=====================================
Create database::

    su - postgres
    createdb weatherbase

Enable PostGIS extension::

    psql weatherbase
    CREATE EXTENSION postgis;

Create users::

    CREATE ROLE luftdatenpumpe WITH LOGIN;
    CREATE ROLE grafana WITH LOGIN PASSWORD 'readonly';

Pre-flight checks::

    psql -U luftdatenpumpe -h localhost -d weatherbase

Run ``luftdatenpumpe`` for the first time to manifest database schema::

    luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

Create database view and grant permissions to "grafana" user::

    luftdatenpumpe database --target=postgresql://luftdatenpumpe@localhost/weatherbase --create-view --grant-user=grafana

.. note::

    These steps will have to be performed **in order** as the last ``--create-view``
    step will only work after data in the tables has been materialized.


Sanity checks
=============
Let's have a look if everything worked.


Database schema
---------------
As visible by an administrator.
::

    $ psql -U luftdatenpumpe -h localhost -d weatherbase

    weatherbase=> \dtv ldi_*

                   List of relations
     Schema |     Name     | Type  |     Owner
    --------+--------------+-------+----------------
     public | ldi_network  | view  | luftdatenpumpe
     public | ldi_osmdata  | table | luftdatenpumpe
     public | ldi_sensors  | table | luftdatenpumpe
     public | ldi_stations | table | luftdatenpumpe
    (4 rows)

Data
----
- Query the database view ``ldi_network`` here.
- Use read-only account pretending to be Grafana.
::

    psql --username=grafana --host=localhost --dbname=weatherbase --command='select count(*) from ldi_network;'

     count
    -------
      1391


********
InfluxDB
********

Create and provision InfluxDB database
======================================
::

    luftdatenpumpe readings --station=28,1071 --target=influxdb://luftdatenpumpe@localhost/luftdaten_info

Sanity checks
=============
Let's have a look if everything worked.

Database schema
---------------
::

    $ influx -host localhost -username luftdatenpumpe -database luftdaten_info -execute 'SHOW FIELD KEYS; SHOW TAG KEYS;'

    fieldKey    fieldType
    --------    ---------
    P1          float
    P2          float
    humidity    float
    temperature float

    tagKey
    ------
    geohash
    sensor_id
    station_id

Database content
----------------
::

    $ influx -host localhost -username luftdatenpumpe -database luftdaten_info -execute 'SHOW TAG VALUES WITH KEY = station_id;'

    key        value
    ---        -----
    station_id 1071
    station_id 28

::

    $ influx -host localhost -username luftdatenpumpe -database luftdaten_info -execute 'SELECT COUNT(*) FROM ldi_readings;'

    time count_P1 count_P2 count_humidity count_temperature
    ---- -------- -------- -------------- -----------------
    0    4        4        4              4
