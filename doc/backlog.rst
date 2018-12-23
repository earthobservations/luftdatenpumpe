######################
Luftdatenpumpe backlog
######################


******
Prio 1
******
- [x] Download cache for data feed (5 minutes)
- [x] Write metadata directly to Postgres
- [x] Redesign commandline interface
- [x] Create CHANGES.rst, update documentation and repository (tags)
- [x] Add tooling for packaging
- [x] Publish to PyPI
- [x] Write measurement data directly to InfluxDB
- [x] Store stations / data **while** processing
- [x] Make a sensor type chooser in Grafana. How would that actually select
      multiple(!) stations by id through Grafana?
- [x] Store Geohash into InfluxDB database again. Check for sensor_id.
- [x] Probe Redis when starting
- [o] Add link to Demo #5
- [o] Add Grafana assets


******
Prio 2
******
- [o] Refactor for handling multiple data sources and targets
- [o] Run some metric about total count of measuremnts per feed action
- [o] Export to tabular format: http://docs.python-tablib.org/
- [o] Output data in tabular, markdown or rst formats
- [o] Publish to MQTT with separate topics
- [o] Store "boundingbox" attribute to RDBMS database
- [o] Dry-run for RDBMS storage
- [o] Filter by sensor type on command line
- Grafana Worldmap Panel
    - [o] Handle multiple languages with Nominatim. Use English as default.
    - [o] Get English (or configurable) country labels from Nominatim
    - [o] JSON endpoint: Add formatter ``jq '[ .[] | {key: .station_id | tostring, name: .name} ]'``
    - [o] JSON endpoint: Map by geohash only
    - [o] Link to Nominatim place_id, see https://nominatim.hiveeyes.org/details.php?place_id=8110875


******
Prio 3
******
- [o] OSM: Why are some roads or towns empty?
      luftdaten_meta=# select * from ldi_osmdata where road is null limit 7;
- [o] Add remark after "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright" like
      "remark": "The address information has been modified by luftdatenpumpe 0.4.0"
- [o] OSM: English labels for e.g. Hercegovine, BA
- [o] Database view
      https://www.postgresql.org/docs/9.2/sql-createview.html
      on top of
      https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199/25
- [o] Integrate https://github.com/openaq/openaq-fetch somehow


******
Prio 4
******
- [o] Write metadata directly to PostGIS
  https://dataset.readthedocs.io/en/latest/
- [o] Add support for JSON and GIS data to "dataset" module
- [o] OSM: Italia only has 3-letter state names like CAL, CAM, LOM, etc.
- [o] Add PostgREST
- [o] Import historical data from http://archive.luftdaten.info/
- [o] Grafana: Link to https://www.madavi.de/sensor/graph.php and/or
      http://deutschland.maps.luftdaten.info/#13/50.9350/13.3913 somehow?
- [o] After importing historical data, make a video from the expanding map
- [o] Update

    - https://github.com/opendata-stuttgart/sensors-software/issues/33
    - https://twitter.com/SchindlerTimo/status/1064634624192774150

- [o] Provide jq examples


*********************
What others are doing
*********************

OpenAQ
======
- https://openaq.org/
- https://github.com/openaq
- https://github.com/dolugen/openaq-browser
- https://docs.openaq.org/
- https://dolugen.github.io/openaq-browser/

European Environment Agency
===========================
- https://www.eea.europa.eu/themes/air/air-quality-index

OpenSense
=========
- https://www.opensense.network/
- https://github.com/opensense-network
- https://twitter.com/sallapf/status/1070334518106750977

openHAB weather bindings
========================
- https://www.openhab.org/addons/bindings/weather1/
- https://community.openhab.org/t/weather-widget/45437
- https://community.openhab.org/t/solved-json-path-weather-warnings-dwd-deutscher-wetterdienst/46295

Weather API
===========
- https://darksky.net/
