#######
Gallery
#######

Some example installations, usually running live data feeds through them.


**************
luftdaten.info
**************

About
=====
Acquisition of sensor data from the LDI network.

Adapter
=======
Implemented by `luftdatenpumpe.source.luftdaten_info <https://github.com/earthobservations/luftdatenpumpe/blob/main/luftdatenpumpe/source/luftdaten_info.py>`_

Dashboards
==========
- `LDI Feinstaub Karte Europa <https://weather.hiveeyes.org/grafana/d/AOerEQQmk/luftdaten-info-karte>`_
- `LDI Feinstaub Verlauf <https://weather.hiveeyes.org/grafana/d/ioUrPwQiz/luftdaten-info-verlauf>`_
- `Vergleich LDI Umweltdaten vs. DWD Wetterdaten <https://weather.hiveeyes.org/grafana/d/NP0wTOtmk/weather-hiveeyes-org>`_
- `Vergleich LDI Feuchtigkeitswerte BME280 vs. DHT22 mit DWD-Daten <https://weather.hiveeyes.org/grafana/d/BJo-dOfik/vergleich-bme280-and-dht22-sensoren-mit-dwd>`_
- `LDI Karte und Kompensation <https://weather.hiveeyes.org/grafana/d/FUygU7_mk/wtf-ldi-karte-und-kompensation-dev>`_
- `LDI Feuchtekorrektur PM10 <https://weather.hiveeyes.org/grafana/d/IgmFilaiz/wtf-pm10-feuchtekorrektur-ldi>`_

Screenshots
===========

.. figure:: https://ptrace.hiveeyes.org/2018-12-28_luftdaten-info-coverage.gif
    :target: https://ptrace.hiveeyes.org/2018-12-28_luftdaten-info-coverage.mp4
    :alt: Coverage of LDI network 2015-2018.

    `Coverage of LDI network 2015-2018 <https://github.com/panodata/grafanimate#luftdateninfo-coverage>`_

.. figure:: https://ptrace.hiveeyes.org/2019-02-03_particulates-on-new-year-s-eve.gif
    :target: https://ptrace.hiveeyes.org/2019-02-03_particulates-on-new-year-s-eve.mp4
    :alt: Fine dust pollution on New Year's Eve 2018.

    `Fine dust pollution on New Year's Eve 2018 <https://github.com/panodata/grafanimate#fine-dust-pollution-on-new-years-eve>`_
    |
    `Animation of fine dust pollution on New Year's Eve 2018 across Europe <https://community.hiveeyes.org/t/animation-der-feinstaubbelastung-an-silvester-2018-mit-grafanimate/1472>`_

References
==========
- https://web.archive.org/web/20220604103954/https://luftdaten.info/
- https://sensor.community/
- https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199
- https://community.hiveeyes.org/t/ldi-data-plane-v2/1412

Labs
====
- `LDI Demo #1 » Stations by name, country and state <https://weather.hiveeyes.org/grafana/d/yDbjQ7Piz/amo-ldi-stations-1-select-by-name-country-and-state>`_
- `LDI Demo #2 » Cascaded stations <https://weather.hiveeyes.org/grafana/d/Oztw1OEmz/amo-ldi-stations-2-cascaded-stations>`_
- `LDI Demo #3 » Measurements by cascaded location selector <https://weather.hiveeyes.org/grafana/d/lT4lLcEiz/amo-ldi-stations-3-cascaded-measurements>`_
- `LDI Demo #4 » Find stations by sensor type <https://weather.hiveeyes.org/grafana/d/kMIweoPik/amo-ldi-stations-4-select-by-sensor-type>`_
- `LDI Demo #5 » Map by location and sensor type <https://weather.hiveeyes.org/grafana/d/9d9rnePmk/amo-ldi-stations-5-map-by-sensor-type>`_


*****
DHT22
*****

About
=====

An analysis of the results of DHT22 humidity sensors.

Screenshots
===========

.. figure:: https://community.panodata.org/uploads/default/original/1X/41fd0e21e8f252c9843d73c6267d2436ea9f3391.png
    :target: https://community.panodata.org/t/data-crunching-and-visualization/108
    :alt: Analyzing DHT22 measurement values on the LDI network.

    Analyzing DHT22 measurement values on the LDI network.


********
IRCELINE
********

About
=====
Air quality monitoring for the Flanders Environment Agency in Belgium.

Luftdatenpumpe helped VMM to support their work for the Belgian Interregional
Environment Agency (IRCEL - CELINE) on air quality monitoring within the EU-funded
Corona EU and VAQUUMS projects.

More details about this can be found at `Supporting the Flanders Environment
Agency (VMM) by analyzing and visualizing air quality sensor data with
InfluxDB and Grafana`_.

Adapter
=======
Implemented by `luftdatenpumpe.source.irceline <https://github.com/earthobservations/luftdatenpumpe/blob/main/luftdatenpumpe/source/irceline.py>`_

Dashboards
==========
- `Luftdaten-Viewer » IRCELINE » Map <https://vmm.panodata.net/grafana/d/CM5mTOZWk/luftdaten-viewer-irceline-map>`_
- `Luftdaten-Viewer » IRCELINE » Trend <https://vmm.panodata.net/grafana/d/JzSioOWWz/luftdaten-viewer-irceline-trend>`_

Screenshots
===========

.. figure:: https://community.panodata.org/uploads/default/original/1X/0c6f30f17d9c6c87d6b65f8daf37c6a443bffd91.png
    :target: https://community.panodata.org/t/data-crunching-and-visualization/108
    :alt: Comparing air quality sensors.

    Comparing air quality sensors.

.. figure:: https://community.panodata.org/uploads/default/original/1X/3fc53c44ad36c08b07b2c5352cb8b3d99d997877.png
    :target: https://community.panodata.org/t/data-crunching-and-visualization/108
    :alt: Comparing air quality sensors.

    Comparing air quality sensors.

.. figure:: https://community.panodata.org/uploads/default/original/1X/06814f55316d7e008af208bd20382d440819246c.png
    :target: https://community.panodata.org/t/supporting-the-flanders-environment-agency-vmm-by-analyzing-and-visualizing-air-quality-sensor-data-with-influxdb-and-grafana/17
    :alt: Humidity compensation for air quality sensors.

    Humidity compensation for air quality sensors.


References
==========
- https://www.irceline.be/en
- https://web.archive.org/web/20211129062716/http://deus.irceline.be/
- https://en.vmm.be/
- https://web.archive.org/web/20210112053937/https://project-corona.eu/default.aspx
- https://geo.irceline.be/sos/static/doc/api-doc/


.. _Supporting the Flanders Environment Agency (VMM) by analyzing and visualizing air quality sensor data with InfluxDB and Grafana: https://community.panodata.org/t/supporting-the-flanders-environment-agency-vmm-by-analyzing-and-visualizing-air-quality-sensor-data-with-influxdb-and-grafana/17
