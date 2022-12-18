.. highlight:: bash

##########################
Luftdaten-Viewer Databases
##########################


************
Introduction
************

This section of the documentation outlines how to provision the PostGIS and
InfluxDB databases. It will assume all services are properly installed and
configured on your system, and otherwise will give you instructions how to
start the corresponding services in sandbox mode.

Prerequisites
=============

When running in sandbox mode, those commands will start the services required
to follow this tutorial. It is InfluxDB, PostGIS, and Redis::

    make influxdb-start
    make postgis-start
    make redis-start

When running in production mode, you may need to configure your services to
provide convenient authentication. On this matter, please have a look at
:ref:`postgresql-authentication`.


*******
PostGIS
*******

Create and provision PostGIS database
=====================================

Connect to PostGIS::

    psql postgres://postgres@localhost:5432

When aiming to connect to PostGIS on a classic Linux host, where PostGIS is
installed as a system service, those commands might work better::

    su - postgres
    psql

Create database::

    CREATE DATABASE weatherbase;
    \connect weatherbase;

Enable PostGIS extension::

    CREATE EXTENSION postgis;

Optionally drop users first::

    DROP ROLE IF EXISTS luftdatenpumpe;
    DROP ROLE IF EXISTS grafana;

Create users::

    CREATE ROLE luftdatenpumpe WITH LOGIN;
    CREATE ROLE grafana WITH LOGIN PASSWORD 'readonly';
    \q


Import data
===========

Pre-flight checks::

    psql postgres://luftdatenpumpe@localhost:5432/weatherbase

Run ``luftdatenpumpe`` for the first time to manifest the database schema.

.. tabs::

    .. tab:: LDI

        ::

            luftdatenpumpe stations \
                --network=ldi --station="49,1033" --reverse-geocode \
                --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

    .. tab:: IRCELINE

        ::

            luftdatenpumpe stations \
                --network=irceline --station="1030,1751" --reverse-geocode \
                --target=postgresql://luftdatenpumpe@localhost/weatherbase --progress

Create database view and grant permissions to "grafana" user.

.. tabs::

    .. tab:: LDI

        ::

            luftdatenpumpe database --network=ldi \
                --target=postgresql://luftdatenpumpe@localhost/weatherbase \
                --create-view --grant-user=grafana

    .. tab:: IRCELINE

        ::

            luftdatenpumpe database --network=irceline \
                --target=postgresql://luftdatenpumpe@localhost/weatherbase \
                --create-view --grant-user=grafana

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

    psql -U luftdatenpumpe -h localhost -d weatherbase --command '\dtv ldi_*'

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

    psql \
        --username=grafana --host=localhost \
        --dbname=weatherbase --command='SELECT COUNT(*) FROM ldi_network;'

::

     count
    -------
      1391


********
InfluxDB
********

Create and provision InfluxDB database
======================================
::

    luftdatenpumpe readings --network=ldi --station="49,1033" \
        --target=influxdb://luftdatenpumpe@localhost/luftdaten_info


Sanity checks
=============
Let's have a look if everything worked.

Database schema
---------------
::

    influx \
        -host localhost -username luftdatenpumpe \
        -database luftdaten_info \
        -execute 'SHOW FIELD KEYS; SHOW TAG KEYS;'

::

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

    influx \
        -host localhost -username luftdatenpumpe \
        -database luftdaten_info \
        -execute 'SHOW TAG VALUES WITH KEY = station_id;'

::

    key        value
    ---        -----
    station_id 1071
    station_id 28

::

    influx \
        -host localhost -username luftdatenpumpe \
        -database luftdaten_info \
        -execute 'SELECT COUNT(*) FROM ldi_readings;'

::

    time count_P1 count_P2 count_humidity count_temperature
    ---- -------- -------- -------------- -----------------
    0    4        4        4              4

