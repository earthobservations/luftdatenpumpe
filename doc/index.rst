.. Luftdatenpumpe documentation master file, created by
   sphinx-quickstart on Sat Dec 17 19:31:12 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##############
Luftdatenpumpe
##############

.. toctree::
   :maxdepth: 2
   :caption: Contents:


*****
About
*****

Acquire and process live and historical air quality data without efforts.

Description
===========

Filter by station-id, sensor-id and sensor-type, apply reverse geocoding,
store into time-series_ and RDBMS_ databases (InfluxDB_ and PostGIS_),
publish to MQTT_, output as JSON, or visualize in `Grafana`_.
Data sources: `Sensor.Community`_ (`luftdaten.info`_), `IRCELINE`_, and
`OpenAQ`_.

The :doc:`Luftdatenpumpe README <README>` has more details about features,
screenshots, and basic usage information.

Example
=======

Visualization of `particulate matter pollution on New Year's Eve 2018`_,
as seen through measurement data of the LDI network. More information at
`Animation of fine dust pollution on New Year's Eve 2018 across Europe`_.

.. figure:: https://ptrace.hiveeyes.org/2019-02-03_particulates-on-new-year-s-eve.gif
    :target: https://ptrace.hiveeyes.org/2019-02-03_particulates-on-new-year-s-eve.mp4
    :alt: Fine dust pollution on New Year's Eve 2018.
    :align: left

    Particulate matter pollution on New Year's Eve 2018 in Europe/Germany.

|clearfix|


********
Handbook
********

.. toctree::
   :maxdepth: 1

   Introduction <README>
   setup/index
   usage
   gallery
   postgis
   mqtt


***********
Development
***********

.. toctree::
   :maxdepth: 1

   CONTRIBUTORS
   CHANGES
   backlog

   models/ldi/README
   models/irceline/README


********
Research
********

.. toctree::
   :maxdepth: 1

   research/open-data
   research/other-projects
   research/tech-radar


.. _Animation of fine dust pollution on New Year's Eve 2018 across Europe: https://community.hiveeyes.org/t/animation-der-feinstaubbelastung-an-silvester-2018-mit-grafanimate/1472
.. _Grafana: https://github.com/grafana/grafana
.. _grafanimate: https://github.com/panodata/grafanimate
.. _InfluxDB: https://github.com/influxdata/influxdb
.. _IRCELINE: https://www.irceline.be/en/documentation/open-data
.. _luftdaten.info: https://web.archive.org/web/20220604103954/https://luftdaten.info/
.. _MQTT: https://mqtt.org/
.. _OpenAQ: https://openaq.org/
.. _particulate matter pollution on New Year's Eve 2018: https://github.com/panodata/grafanimate#fine-dust-pollution-on-new-years-eve
.. _PostGIS: https://postgis.net/
.. _RDBMS: https://en.wikipedia.org/wiki/Relational_database_management_system
.. _sensor.community: https://sensor.community/en/
.. _time-series: https://en.wikipedia.org/wiki/Time_series_database

.. |clearfix| raw:: html

    <div style="clear: both;"></div>
