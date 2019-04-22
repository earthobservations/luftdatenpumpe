#####################
luftdatenpumpe --help
#####################

::

    $ luftdatenpumpe --help

    Usage:
      luftdatenpumpe stations [options] [--target=<target>]...
      luftdatenpumpe readings [options] [--target=<target>]...
      luftdatenpumpe database [--target=<target>]... [--create-views] [--grant-user=<username>] [--drop-data] [--drop-tables] [--drop-database]
      luftdatenpumpe grafana --kind=<kind> --name=<name> [--variables=<variables>]
      luftdatenpumpe --version
      luftdatenpumpe (-h | --help)

    Options:
      --source=<source>             Data source, either "api" or "file://" [default: api].
      --country=<countries>         Filter data by given country codes, comma-separated.
      --station=<stations>          Filter data by given location ids, comma-separated.
      --sensor=<sensors>            Filter data by given sensor ids, comma-separated.
      --sensor-type=<sensor-types>  Filter data by given sensor types, comma-separated.
      --reverse-geocode             Compute geographical address using the Nominatim reverse geocoder
      --target=<target>             Data output target
      --disable-nominatim-cache     Disable Nominatim reverse geocoder cache
      --progress                    Show progress bar
      --version                     Show version information
      --dry-run                     Skip publishing to MQTT bus
      --debug                       Enable debug messages
      -h --help                     Show this screen


    Station list examples:

      # Display metadata for given countries in JSON format
      luftdatenpumpe stations --country=BE,NL,LU

      # Display metadata for given stations in JSON format, with reverse geocoding
      luftdatenpumpe stations --station=28,1071 --reverse-geocode

      # Display metadata for given sensors in JSON format, with reverse geocoding
      luftdatenpumpe stations --sensor=657,2130 --reverse-geocode

      # Display list of stations in JSON format made of value/text items, suitable for use as a Grafana JSON data source
      luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=json.grafana.vt+stream://sys.stdout

      # Display list of stations in JSON format made of key/name items, suitable for use as a mapping in Grafana Worldmap Panel
      luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=json.grafana.kn+stream://sys.stdout

      # Store list of stations and metadata into RDBMS database (PostgreSQL), also display on STDERR
      luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=postgresql://luftdatenpumpe@localhost/weatherbase --target=json+stream://sys.stderr

      # Read station information from RDBMS database (PostgreSQL) and format for Grafana Worldmap Panel
      luftdatenpumpe stations --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.grafana.kn+stream://sys.stdout


    Live data examples (InfluxDB):

      # Store into InfluxDB running on "localhost"
      luftdatenpumpe readings --station=28,1071 --target=influxdb://localhost:8086/luftdaten_info

      # Store into InfluxDB, with UDP
      luftdatenpumpe readings --station=28,1071 --target=udp+influxdb://localhost:4445/luftdaten_info

      # Store into InfluxDB, with authentication
      luftdatenpumpe readings --station=28,1071 --target=influxdb://username:password@localhost:8086/luftdaten_info


    Archive data examples (InfluxDB):

      # Mirror archive of luftdaten.info
      wget --mirror --continue --no-host-directories --directory-prefix=/var/spool/archive.luftdaten.info http://archive.luftdaten.info/

      # Ingest station information from CSV archive files, store into PostgreSQL
      luftdatenpumpe stations --source=file:///var/spool/archive.luftdaten.info --target=postgresql://luftdatenpumpe@localhost/weatherbase --reverse-geocode --progress

      # Ingest readings from CSV archive files, store into InfluxDB
      luftdatenpumpe readings --source=file:///var/spool/archive.luftdaten.info --station=483 --sensor=988 --target=influxdb://localhost:8086/luftdaten_info --progress

      # Ingest most early readings
      luftdatenpumpe readings --source=file:///var/spool/archive.luftdaten.info/2015-10-*

      # Ingest most early PMS sensors
      luftdatenpumpe readings --source=file:///var/spool/archive.luftdaten.info/2017-1*/*pms*.csv


    Live data examples (MQTT):

      # Publish data to topic "luftdaten.info" at MQTT broker running on "localhost"
      luftdatenpumpe readings --station=28,1071 --target=mqtt://localhost/luftdaten.info

      # MQTT publishing, with authentication
      luftdatenpumpe readings --station=28,1071 --target=mqtt://username:password@localhost/luftdaten.info


    Combined examples:

      # Write stations to STDERR and PostgreSQL
      luftdatenpumpe stations --station=28,1071 --target=json+stream://sys.stderr --target=postgresql://luftdatenpumpe@localhost/weatherbase

      # Write readings to STDERR, MQTT and InfluxDB
      luftdatenpumpe readings --station=28,1071 --target=json+stream://sys.stderr --target=mqtt://localhost/luftdaten.info --target=influxdb://localhost:8086/luftdaten_info
