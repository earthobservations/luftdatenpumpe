.. image:: https://github.com/earthobservations/luftdatenpumpe/workflows/Tests/badge.svg
    :target: https://github.com/earthobservations/luftdatenpumpe/actions?workflow=Tests
    :alt: CI outcome

.. image:: https://codecov.io/gh/earthobservations/luftdatenpumpe/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/earthobservations/luftdatenpumpe
    :alt: Test suite code coverage

.. image:: https://pepy.tech/badge/luftdatenpumpe/month
    :target: https://pypi.org/project/luftdatenpumpe/
    :alt: PyPI downloads per month

.. image:: https://img.shields.io/pypi/v/luftdatenpumpe.svg
    :target: https://pypi.org/project/luftdatenpumpe/
    :alt: Package version on PyPI

.. image:: https://img.shields.io/pypi/status/luftdatenpumpe.svg
    :target: https://pypi.org/project/luftdatenpumpe/
    :alt: Project status (alpha, beta, stable)

.. image:: https://img.shields.io/pypi/pyversions/luftdatenpumpe.svg
    :target: https://pypi.org/project/luftdatenpumpe/
    :alt: Support Python versions

.. image:: https://img.shields.io/pypi/l/luftdatenpumpe.svg
    :target: https://github.com/earthobservations/luftdatenpumpe/blob/main/LICENSE
    :alt: Project license

|

##############
Luftdatenpumpe
##############

.. image:: https://assets.okfn.org/images/ok_buttons/od_80x15_red_green.png
    :target: https://okfn.org/opendata/

.. image:: https://assets.okfn.org/images/ok_buttons/oc_80x15_blue.png
    :target: https://okfn.org/opendata/

.. image:: https://assets.okfn.org/images/ok_buttons/os_80x15_orange_grey.png
    :target: https://okfn.org/opendata/


*****
About
*****

Process live and historical data from `luftdaten.info`_, irceline_ and OpenAQ_.
Filter by station-id, sensor-id and sensor-type, apply reverse geocoding,
store into TSDB_ and RDBMS_ databases (InfluxDB_ and PostGIS_),
publish to MQTT_ or just output as JSON.

.. figure:: https://cdn.jsdelivr.net/gh/earthobservations/luftdatenpumpe@main/doc/logo.svg
    :target: https://github.com/earthobservations/luftdatenpumpe
    :height: 200px
    :width: 200px


********
Features
********

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
   - queried using advanced geospatial features when running PostGIS_, please
     follow up reading the `Luftdatenpumpe PostGIS tutorial <doc-postgis_>`_.

5. Measurement readings can be

   - displayed on STDOUT or STDERR in JSON format, which allows for piping into jq_ again.
   - forwarded to MQTT_.
   - stored to InfluxDB_ and then
   - displayed in Grafana_.


********
Synopsis
********
::

    # List networks
    luftdatenpumpe networks

    # List LDI stations
    luftdatenpumpe stations --network=ldi --station=49,1033 --reverse-geocode

    # Store list of LDI stations and metadata into RDBMS database (PostgreSQL), also display on STDERR
    luftdatenpumpe stations --network=ldi --station=49,1033 --reverse-geocode --target=postgresql://luftdatenpumpe@localhost/weatherbase

    # Store LDI readings into InfluxDB
    luftdatenpumpe readings --network=ldi --station=49,1033 --target=influxdb://luftdatenpumpe@localhost/luftdaten_info

    # Forward LDI readings to MQTT
    luftdatenpumpe readings --network=ldi --station=49,1033 --target=mqtt://mqtt.example.org/luftdaten.info


For a full overview about all program options including meaningful examples,
you might just want to run ``luftdatenpumpe --help`` on your command line
or visit `luftdatenpumpe --help`_.



***********
Screenshots
***********

Luftdaten-Viewer displays stations and measurements from luftdaten.info (LDI) in Grafana.


Map display and filtering
=========================
- Filter by different synthesized address components and sensor type.
- Display measurements from filtered stations on Grafana Worldmap Panel.
- Display filtered list of stations with corresponding information in tabular form.
- Measurement values are held against configured thresholds so points are colored appropriately.

.. image:: https://community.hiveeyes.org/uploads/default/original/2X/f/f455d3afcd20bfa316fefbe69e43ca2fe159e62d.png
    :target: https://weather.hiveeyes.org/grafana/d/9d9rnePmk/amo-ldi-stations-5-map-by-sensor-type


Map popup labels
================
- Humanized label computed from synthesized OpenStreetMap address.
- Numeric station identifier.
- Measurement value, unit and field name.

.. image:: https://community.hiveeyes.org/uploads/default/original/2X/4/48eeda1a1d418eaf698b241a65080666abcf2497.png
    :target: https://weather.hiveeyes.org/grafana/d/9d9rnePmk/amo-ldi-stations-5-map-by-sensor-type


************
Installation
************

If you are running Python 3 already, installing the program should be as easy as::

    pip install luftdatenpumpe

At this point, you should be able to conduct simple tests like
``luftdatenpumpe stations`` as seen in the synopsis section above.
At least, you should verify the installation succeeded by running::

    luftdatenpumpe --version

However, you might have to resolve some prerequisites so you want to follow
the detailed installation instructions at `install Luftdatenpumpe`_.


****************
Luftdaten-Viewer
****************

About
=====
Using Luftdatenpumpe, you can build user-friendly interactive GIS systems
on top of PostGIS, InfluxDB and Grafana. We are calling this "Luftdaten-Viewer".

Without further ado, you might enjoy reading about existing "Luftdaten-Viewer"
installations at `Testimonials for Luftdatenpumpe`_.

Instructions
============
These installation instructions outline how to setup the whole system to build
similar interactive data visualization compositions of map-, graph- and other
panel-widgets like outlined in the "Testimonials" section.

- `Luftdaten-Viewer Applications`_
- `Luftdaten-Viewer Databases`_
- `Luftdaten-Viewer Grafana`_


*******
License
*******

This project is licensed under the terms of the GNU AGPL license.


********************
Content attributions
********************

The copyright of particular images and pictograms are held by their respective owners, unless otherwise noted.

Icons and pictograms
====================
- `Water Pump Free Icon <https://www.onlinewebfonts.com/icon/97990>`_ from
  `Icon Fonts <http://www.onlinewebfonts.com/icon>`_ is licensed by CC BY 3.0.



.. _doc-virtualenv: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/virtualenv.rst
.. _doc-postgis: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/postgis.rst


.. _luftdaten.info: https://luftdaten.info/
.. _irceline: http://www.irceline.be/en/documentation/open-data
.. _OpenAQ: https://openaq.org/

.. _Luftdatenpumpe: https://github.com/earthobservations/luftdatenpumpe

.. _Testimonials for Luftdatenpumpe: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/testimonials.rst
.. _luftdatenpumpe --help: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/usage.rst
.. _install Luftdatenpumpe: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/setup/luftdatenpumpe.rst
.. _Luftdaten-Viewer Applications: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/setup/ldview-applications.rst
.. _Luftdaten-Viewer Databases: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/setup/ldview-databases.rst
.. _Luftdaten-Viewer Grafana: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/setup/ldview-grafana.rst
.. _Luftdaten-Viewer Cron Job: https://github.com/earthobservations/luftdatenpumpe/blob/main/doc/setup/ldview-cronjob.rst

.. _Erneuerung der Luftdatenpumpe: https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199

.. _The Hiveeyes Project: https://hiveeyes.org/

.. _OpenStreetMap: https://en.wikipedia.org/wiki/OpenStreetMap
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. _Geohash: https://en.wikipedia.org/wiki/Geohash
.. _dataset: https://dataset.readthedocs.io/
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _TSDB: https://en.wikipedia.org/wiki/Time_series_database
.. _RDBMS: https://en.wikipedia.org/wiki/Relational_database_management_system
.. _MQTT: http://mqtt.org/

.. _PostgreSQL: https://www.postgresql.org/
.. _PostGIS: https://postgis.net/
.. _InfluxDB: https://github.com/influxdata/influxdb
.. _Grafana: https://github.com/grafana/grafana

.. _jq: https://stedolan.github.io/jq/
