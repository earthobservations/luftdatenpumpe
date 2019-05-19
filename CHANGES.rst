########################
Luftdatenpumpe changelog
########################


in progress
===========

2019-05-19 0.12.0
=================
- Always fetch last 12 hours worth of data to reduce gaps when API is offline.
- Update documentation
- Distinguish between "sensor_type_name" and "sensor_type_id"
- Tune worldmap panel default settings


2019-04-26 0.11.0
=================
- Push architecture towards ingesting of data from multiple sensor networks
- Integrate data from the SOS REST API of the IRCELINE network


2019-04-22 0.10.0
=================
- Improve RDBMS subsystem
- Improve robustness, logging and error handling
- Add resources and documentation for running as cron job
- Allow customizing the Grafana panels from the command line


2019-04-10 0.9.0
================
- Add GIS capabilities through PostGIS
- Set default format for "stream://" targets to "json"
- Fix published messages getting lost when not starting
  the MQTT main loop after connecting to MQTT broker
- Refactor station list filter
- Filter stations by country code


2019-01-22 0.8.2
================
- Add missing sensor DS18B20
- Fix PostgreSQL version in Grafana datasource JSON
- Add station id to "multiple stations" chooser on trend dashboard
- Don't try to enrich incomplete station information


2019-01-19 0.8.1
================
- Make dashboards not editable


2019-01-19 0.8.0
================
- Refactor and improve Grafana datasource- and dashboard JSON files
- Add ``luftdatenpumpe grafana`` subcommand for accessing
  Grafana datasource- and dashboard JSON files
- Improve documentation significantly


2019-01-18 0.7.0
================
- Rename OSM data field "country_name" back to "country"
- Add sanity checks for protecting against unqualified responses
  from Nominatim service with DE-only dataset loaded
- Use country code for routing to different Nominatim services,
  one of them having the DE-only dataset loaded
- Improve RDBMS database schema
- Naming things
- Show cardinality in sensor type chooser


2019-01-18 0.6.0
================
- Fix renaming OSM field "country" to "country_name"


2019-01-18 0.5.0
================
- Add InfluxDB egress handler
- Improve HTTP response caching
- Probe Redis before starting and croak if connection fails
- Add "geohash" field when writing into InfluxDB
- Use nominatim.hiveeyes.org as primary reverse geocoder,
  fall back to nominatim.openstreetmap.org
- Add option to disable the Nominatim cache
- Add configuration and documentation about Grafana Worldmap
- Unlock CSV data acquisition from archive.luftdaten.info
- Add Grafana Graph dashboard
- Add User-Agent for requests to api.luftdaten.info
- Improve globbing when selecting path for CSV import
- Compensate empty values (nan) when importing from CSV
- Add output formatter for Grafana Worldmap Panel JSON file
- Add RDBMS database (PostgreSQL) as station data source
- Add ``--sensor-type`` filter option
- Improve CSV file reading
- Flush each 50 records when talking to InfluxDB with UDP
- Introduce quick mode for importing just the first few records
- Add new option "--create-database-view"
- Rename OSM data field "country" to "country_name"


2018-12-11 0.4.3
================
- Fix setup.py
- Add MANIFEST.in file


2018-12-11 0.4.2
================
- Use "geohash2" package from PyPI for Python3 compatibility
- Fix twine. Just works outside of virtualenv.


2018-12-11 0.4.1
================
- Remove unknown Trove classifiers from setup.py


2018-12-11 0.4.0
================
- Refactoring, Python2/3 compatibility, Add setup.py
- Add "sensor_type" information to station list
- Use Redis-based caching through dogpile.cache, ditch Beaker
- Refactor data munging
- Always cache full response from Nominatim
- Cache responses from the luftdaten.info API for five minutes
- Add basic RDBMS adapter for storing station list and associated
  information to Postgres and other SQL databases supported by SQLAlchemy
- Streamline station data schema
- Add test harness for reverse geocoder subsystem
- Improve robustness and quality of reverse geocoder
- Make "sensors" data substructure an array
- Refactor target machinery and redesign command line interface
- Add release tooling


2018-12-02 0.3.0
================
- Add option "--dry-run"
- Fix filtering by station id
- Fix access to Nominatim reverse geocoder API
- Use "appdirs" module for computing cache location. Report about cache location at startup.
- Improve OSM address formatter: Honor "footway" as another fieldname choice for encoding the "road"
- Improve OSM address formatter: Honor "suburb" field
- Improve filtering by sensor- and/or location-identifiers
- Implement "stations" subcommand to acquire, display and export list of stations
- Prevent duplicate segments in formatted address
- Use station id as label when name is not available


2017-06-06 0.2.0
================
- Add filtering by sensor id. Thanks, Panzki!


2017-04-25 0.1.0
================
- Add commandline interface
- Add caching for Nominatim responses
- Appropriate timestamp mungling
- Improve Documentation


2017-03-31 0.0.0
================
- Basic implementation to request data from live API of luftdaten.info,
  enrich geospatial information and publish to MQTT bus
- Add "sensor_type" field
- Improve OSM address formatter
