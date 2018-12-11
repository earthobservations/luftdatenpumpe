########################
Luftdatenpumpe changelog
########################


in progress
===========
- Refactoring, Python2/3 compatibility, Add setup.py
- Add "sensor_type" information to station list
- Use Redis-based caching through dogpile.cache, ditch Beaker
- Refactor data munging
- Always cache full response from Nominatim
- Cache responses from the luftdaten.info API for five minutes
- Add basic RDBMS adapter for storing station list and associated
  information to Postgres and other SQL databases supported by SQLAlchemy
- Streamline station data schema
- Make "sensors" data substructure an array


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
