.. luftdatenpumpe-readme:

##############
Luftdatenpumpe
##############

.. container:: align-center

    .. figure:: https://cdn.jsdelivr.net/gh/earthobservations/luftdatenpumpe@main/doc/logo.svg
        :target: https://github.com/earthobservations/luftdatenpumpe
        :alt: Luftdatenpumpe logo
        :height: 200px
        :width: 200px

    |

    *Acquire and process live and historical air quality data without efforts.*

    .. image:: https://assets.okfn.org/images/ok_buttons/oc_80x15_blue.png
        :target: https://okfn.org/opendata/

    .. image:: https://assets.okfn.org/images/ok_buttons/od_80x15_red_green.png
        :target: https://okfn.org/opendata/

    .. image:: https://assets.okfn.org/images/ok_buttons/ok_80x15_red_green.png
        :target: https://okfn.org/opendata/

    .. image:: https://assets.okfn.org/images/ok_buttons/os_80x15_orange_grey.png
        :target: https://okfn.org/opendata/

|

- **Status**

  .. image:: https://github.com/earthobservations/luftdatenpumpe/workflows/Tests/badge.svg
      :target: https://github.com/earthobservations/luftdatenpumpe/actions?workflow=Tests
      :alt: CI outcome

  .. image:: https://readthedocs.org/projects/luftdatenpumpe/badge/
      :target: https://luftdatenpumpe.readthedocs.io/
      :alt: Documentation build status

  .. image:: https://codecov.io/gh/earthobservations/luftdatenpumpe/branch/main/graph/badge.svg
      :target: https://codecov.io/gh/earthobservations/luftdatenpumpe
      :alt: Test suite code coverage

  .. image:: https://img.shields.io/pypi/v/luftdatenpumpe.svg
      :target: https://pypi.org/project/luftdatenpumpe/
      :alt: Package version on PyPI

  .. image:: https://img.shields.io/pypi/l/luftdatenpumpe.svg
      :target: https://github.com/earthobservations/luftdatenpumpe/blob/main/LICENSE
      :alt: Project license

  .. image:: https://img.shields.io/pypi/status/luftdatenpumpe.svg
      :target: https://pypi.org/project/luftdatenpumpe/
      :alt: Project status (alpha, beta, stable)

- **Usage**

  .. image:: https://pepy.tech/badge/luftdatenpumpe/month
      :target: https://pepy.tech/project/luftdatenpumpe/
      :alt: PyPI downloads per month

- **Compatibility**

  .. image:: https://img.shields.io/badge/Grafana-5.x%20--%208.x-blue.svg
      :target: https://github.com/grafana/grafana
      :alt: Supported Grafana versions

  .. image:: https://img.shields.io/badge/InfluxDB-1.x-blue.svg
      :target: https://github.com/influxdata/influxdb
      :alt: Supported InfluxDB versions

  .. image:: https://img.shields.io/badge/Mosquitto-1.x%2C%202.x-blue.svg
      :target: https://github.com/eclipse/mosquitto
      :alt: Supported Mosquitto versions

  .. image:: https://img.shields.io/badge/PostgreSQL-13%2C%2014%2C%2015-blue.svg
      :target: https://www.postgresql.org/
      :alt: Supported PostgreSQL versions

  .. image:: https://img.shields.io/badge/PostGIS-3.x-blue.svg
      :target: https://postgis.net/
      :alt: Supported PostGIS versions

  .. image:: https://img.shields.io/pypi/pyversions/luftdatenpumpe.svg
      :target: https://pypi.org/project/luftdatenpumpe/
      :alt: Supported Python versions

|

*****
About
*****

Acquire and process live and historical air quality data without efforts.

Filter by station-id, sensor-id and sensor-type, apply reverse geocoding,
store into time-series_ and RDBMS_ databases (InfluxDB_ and PostGIS_),
publish to MQTT_, output as JSON, or visualize in `Grafana`_.

Data sources: `Sensor.Community`_ (`luftdaten.info`_), `IRCELINE`_, and
`OpenAQ`_.


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
     follow up reading the `Luftdatenpumpe PostGIS tutorial`_.

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
you might just want to run ``luftdatenpumpe --help`` on your command line,
or visit the `Luftdatenpumpe usage`_ documentation section.



***********
Screenshots
***********

Luftdaten-Viewer displays stations and measurements from luftdaten.info (LDI) in Grafana.


Map display and filtering
=========================
- Filter by different synthesized address components and sensor type.
- Display measurements from filtered stations on `Panodata Map Panel`_.
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

If you are running Python 3 already, you can installing the program using
``pip``. We recommend to use a `Python virtualenv`_.

::

    pip install luftdatenpumpe --upgrade

At this point, you should be able to conduct simple tests like
``luftdatenpumpe stations`` as seen in the synopsis section above.
At least, you should verify the installation succeeded by running::

    luftdatenpumpe --version

At `install Luftdatenpumpe`_, you will find more detailed installation instructions
about how to install and configure auxiliary services, and eventually resolve some
prerequisites.


****************
Luftdaten-Viewer
****************

About
=====
Using Luftdatenpumpe, you can build user-friendly interactive GIS systems
on top of PostGIS, InfluxDB and Grafana. This setup is called "Luftdaten-Viewer",
and some example scenarios can be inspected at `Luftdatenpumpe gallery`_.

Instructions
============
These installation instructions outline how to setup the whole system to build
similar interactive data visualization compositions of map-, graph- and other
panel-widgets like outlined in the "Testimonials" section.

- `Luftdaten-Viewer Applications`_
- `Luftdaten-Viewer Databases`_
- `Luftdaten-Viewer Grafana`_


**************
Other projects
**************

Sensor.Community public data aggregator
=======================================

Visualize recent sensor data on a world map for Sensor.Community and for different
other official networks, like EEA, Luchtmeetnet, Atmo AURA/Sud/Occitanie, and
Umweltbundesamt.

- https://github.com/pjgueno/SCPublicData
- https://forum.sensor.community/t/scraping-pm-data-help-needed/1448


*******************
Project information
*******************

Contributions
=============

Any kind of contribution, feedback, or patch, is much welcome. `Create an
issue`_ or submit a patch if you think we should include a new feature, or to
report or fix a bug.

Resources
=========

- `Source code`_
- `Documentation`_
- `Community Forum`_
- `Python Package Index (PyPI)`_

License
=======

The project is licensed under the terms of the GNU AGPL license, see `LICENSE`_.

Content attributions
====================

The copyright of particular images and pictograms are held by their respective
owners, unless otherwise noted.

- `Water Pump Free Icon <https://www.onlinewebfonts.com/icon/97990>`_ from
  `Icon Fonts <https://www.onlinewebfonts.com/icon/>`_ is licensed by CC BY 3.0.


.. _Community Forum: https://community.panodata.org/t/luftdatenpumpe/21
.. _Create an issue: https://github.com/earthobservations/luftdatenpumpe/issues/new
.. _dataset: https://dataset.readthedocs.io/
.. _Documentation: https://luftdatenpumpe.readthedocs.io/
.. _Erneuerung der Luftdatenpumpe: https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199
.. _Geohash: https://en.wikipedia.org/wiki/Geohash
.. _Grafana: https://github.com/grafana/grafana
.. _InfluxDB: https://github.com/influxdata/influxdb
.. _IRCELINE: https://www.irceline.be/en/documentation/open-data
.. _jq: https://stedolan.github.io/jq/
.. _LICENSE: https://github.com/earthobservations/luftdatenpumpe/blob/main/LICENSE
.. _luftdaten.info: https://web.archive.org/web/20220604103954/https://luftdaten.info/
.. _Luftdatenpumpe: https://github.com/earthobservations/luftdatenpumpe
.. _MQTT: https://mqtt.org/
.. _Nominatim: https://wiki.openstreetmap.org/wiki/Nominatim
.. _OpenAQ: https://openaq.org/
.. _OpenStreetMap: https://en.wikipedia.org/wiki/OpenStreetMap
.. _Panodata Map Panel: https://community.panodata.org/t/panodata-map-panel-for-grafana/121
.. _PostgreSQL: https://www.postgresql.org/
.. _PostGIS: https://postgis.net/
.. _Python Package Index (PyPI): https://pypi.org/project/luftdatenpumpe/
.. _RDBMS: https://en.wikipedia.org/wiki/Relational_database_management_system
.. _Sensor.Community: https://sensor.community/en/
.. _Source code: https://github.com/earthobservations/luftdatenpumpe
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _The Hiveeyes Project: https://hiveeyes.org/
.. _time-series: https://en.wikipedia.org/wiki/Time_series_database

.. _install Luftdatenpumpe: https://luftdatenpumpe.readthedocs.io/setup/luftdatenpumpe.html
.. _Luftdaten-Viewer Applications: https://luftdatenpumpe.readthedocs.io/setup/ldview-applications.html
.. _Luftdaten-Viewer Cron Job: https://luftdatenpumpe.readthedocs.io/setup/ldview-cronjob.html
.. _Luftdaten-Viewer Databases: https://luftdatenpumpe.readthedocs.io/setup/ldview-databases.html
.. _Luftdaten-Viewer Grafana: https://luftdatenpumpe.readthedocs.io/setup/ldview-grafana-base.html
.. _Luftdatenpumpe gallery: https://luftdatenpumpe.readthedocs.io/gallery.html
.. _Luftdatenpumpe PostGIS tutorial: https://luftdatenpumpe.readthedocs.io/postgis.html
.. _Luftdatenpumpe usage: https://luftdatenpumpe.readthedocs.io/usage.html
.. _Python virtualenv: https://luftdatenpumpe.readthedocs.io/setup/virtualenv.html
