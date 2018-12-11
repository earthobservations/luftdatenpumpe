######################
Luftdatenpumpe backlog
######################


******
Prio 1
******
- [x] Download cache for data feed (5 minutes)
- [x] Write metadata directly to Postgres
- [o] Redesign commandline interface
- [o] Create CHANGES.rst, update documentation and repository (tags)
- [o] Add tooling for packaging
- [o] Publish to PyPI


******
Prio 2
******
- [o] Write measurement data directly to InfluxDB
- [o] Refactor for handling multiple data sources and targets
- [o] Get English (or configurable) country labels from Nominatim
- [o] Handle multiple languages with Nominatim. Use English as default.
- [o] Make a sensor type chooser in Grafana. How would that actually select multiple(!) stations by id through Grafana?
- [o] Run some metric about total count of measuremnts per feed action
- [o] Export to tabular format: http://docs.python-tablib.org/
- [o] Output data in tabular, markdown or rst formats
- [o] Publish to MQTT with separate topics
- [/] Store stations / data **while** processing
- [o] Store "boundingbox" attribute to RDBMS database


******
Prio 3
******
- [o] OSM: Why are some roads or towns empty?
      weatherbase=# select * from ldi_osmdata where road is null limit 7;
- [o] Add remark after "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright" like
      "remark": "The address information has been modified by luftdatenpumpe 0.4.0"
- [o] OSM: English labels for e.g. Hercegovine, BA
- [o] Database view
      https://www.postgresql.org/docs/9.2/sql-createview.html
      on top of
      https://community.hiveeyes.org/t/erneuerung-der-luftdatenpumpe/1199/25


******
Prio 4
******
- [o] Write metadata directly to PostGIS
  https://dataset.readthedocs.io/en/latest/
- [o] Add support for JSON and GIS data to "dataset" module
- [o] OSM: Italia only has 3-letter state names like CAL, CAM, LOM, etc.
- [o] Add PostgREST
- [o] Import historical data from http://archive.luftdaten.info/
- [o] Grafana: Link to https://www.madavi.de/sensor/graph.php somehow?
- [o] After importing historical data, make a video from the expanding map
