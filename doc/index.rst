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

Process live and historical data from `sensor.community`_ (formerly
`luftdaten.info`_), `IRCELINE`_, and `OpenAQ`_.

Filter by station-id, sensor-id and sensor-type, apply reverse geocoding,
store into TSDB_ and RDBMS_ databases (InfluxDB_ and PostGIS_),
publish to MQTT_ or just output as JSON.

The :doc:`Luftdatenpumpe README <README>` has more details about features,
screenshots, and basic usage information.


********
Handbook
********

.. toctree::
   :maxdepth: 1

   Introduction <README>
   setup/index
   Usage <usage>
   gallery


***********
Development
***********

.. toctree::
   :maxdepth: 1

   CONTRIBUTORS
   CHANGES
   backlog


*******
Details
*******

.. toctree::
   :maxdepth: 1

   postgis
   mqtt
   ldi-schema
   models/ldi/README
   models/irceline/README


********
Research
********

.. toctree::
   :maxdepth: 1

   research/tech-radar
   research/other-projects
   research/open-data


******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _InfluxDB: https://github.com/influxdata/influxdb
.. _IRCELINE: https://www.irceline.be/en/documentation/open-data
.. _luftdaten.info: https://web.archive.org/web/20220604103954/https://luftdaten.info/
.. _MQTT: https://mqtt.org/
.. _OpenAQ: https://openaq.org/
.. _PostGIS: https://postgis.net/
.. _RDBMS: https://en.wikipedia.org/wiki/Relational_database_management_system
.. _sensor.community: https://sensor.community/en/
.. _TSDB: https://en.wikipedia.org/wiki/Time_series_database
