#########################
``luftdatenpumpe --help``
#########################

::

    $ luftdatenpumpe --help

    Usage:
      luftdatenpumpe networks [--network=<network>]
      luftdatenpumpe stations --network=<network> [options] [--target=<target>]...
      luftdatenpumpe readings --network=<network> [options] [--target=<target>]... [--timespan=<timespan>]
      luftdatenpumpe database --network=<network> [--target=<target>]... [--create-views] [--grant-user=<username>] [--drop-data] [--drop-tables] [--drop-database]
      luftdatenpumpe grafana --network=<network> --kind=<kind> --name=<name> [--variables=<variables>] [--fields=<fields>]
      luftdatenpumpe --version
      luftdatenpumpe (-h | --help)

    Options:
      --network=<network>           Which sensor network/database to use.
                                    Inquire available networks by running "luftdatenpumpe networks".
      --source=<source>             Data source, either "api" or "file://" [default: api].
      --country=<countries>         Filter data by given country codes, comma-separated.
      --station=<stations>          Filter data by given location ids, comma-separated.
      --sensor=<sensors>            Filter data by given sensor ids, comma-separated.
      --sensor-type=<sensor-types>  Filter data by given sensor types, comma-separated.
      --timespan=<timespan>         Filter readings by time range, only for SOS API (e.g. IRCELINE).
      --reverse-geocode             Compute geographical address using the Nominatim reverse geocoder
      --target=<target>             Data output target
      --target-fieldmap=<fieldmap>  Fieldname mapping for "json+flex" target
      --disable-nominatim-cache     Disable Nominatim reverse geocoder cache
      --progress                    Show progress bar
      --version                     Show version information
      --dry-run                     Skip publishing to MQTT bus
      --debug                       Enable debug messages
      -h --help                     Show this screen


    Network list:

      # Display list of supported sensor networks
      luftdatenpumpe networks

    Acquire stations (LDI):

      # Display metadata for given countries in JSON format
      luftdatenpumpe stations --network=ldi --country=BE,NL,LU

      # Display metadata for given stations in JSON format, with reverse geocoding
      luftdatenpumpe stations --network=ldi --station=49,1033 --reverse-geocode

    Acquire readings (LDI):

      # Display measurement readings for specific station identifiers.
      luftdatenpumpe readings --network=ldi --station=49,1033 --reverse-geocode

      # Display measurement readings for specific sensor identifiers.
      luftdatenpumpe readings --network=ldi --sensor=417

    Acquire stations and readings (IRCELINE):

      luftdatenpumpe stations --network=irceline
      luftdatenpumpe readings --network=irceline --station=1030,1751 --reverse-geocode

    Acquire stations and readings (OpenAQ):

      luftdatenpumpe stations --network=openaq
      luftdatenpumpe readings --network=openaq --country=IN,PK

    Heads up!

      From now on, let's pretend we always want to operate on data coming from the
      sensor network "luftdaten.info", which is identified by "--network=ldi". To
      make this more convenient, we use an environment variable to signal this
      to subsequent invocations of "luftdatenpumpe" by running::

        export LDP_NETWORK=ldi

    Getting started:

      # Display metadata for given stations in JSON format, with reverse geocoding
      luftdatenpumpe stations --station=49,1033 --reverse-geocode --target=json+stream://sys.stderr


    Convert stations into format suitable for Grafana:

      # Display list of stations in JSON format made of value/text items, suitable for use as a Grafana JSON data source
      luftdatenpumpe stations --station=49,1033 --reverse-geocode --target=json.grafana.vt+stream://sys.stdout

      # Display list of stations in JSON format made of key/name items, suitable for use as a mapping in Panodata Map Panel
      luftdatenpumpe stations --station=49,1033 --reverse-geocode --target=json.grafana.kn+stream://sys.stdout


    Write stations into / read stations from RDBMS database:

      # Store list of stations and metadata into RDBMS database (PostgreSQL)
      luftdatenpumpe stations --station=49,1033 --reverse-geocode --target=postgresql://luftdatenpumpe@localhost/weatherbase

      # Read station information from RDBMS database (PostgreSQL) and format for Panodata Map Panel
      luftdatenpumpe stations --source=postgresql://luftdatenpumpe@localhost/weatherbase --target=json.grafana.kn+stream://sys.stdout


    Live data examples (InfluxDB):

      # Store into InfluxDB running on "localhost"
      luftdatenpumpe readings --station=49,1033 --target=influxdb://localhost/luftdaten_info

      # Store into InfluxDB, with UDP
      luftdatenpumpe readings --station=49,1033 --target=udp+influxdb://localhost:4445/luftdaten_info

      # Store into InfluxDB, with authentication
      luftdatenpumpe readings --station=49,1033 --target=influxdb://luftdatenpumpe@localhost/luftdaten_info


    LDI CSV archive data examples (InfluxDB):

      # Mirror archive of luftdaten.info, limiting to 2015 only
      wget --mirror --continue --no-host-directories --directory-prefix=/var/spool/archive.luftdaten.info --accept-regex='2015' http://archive.luftdaten.info/

      # Ingest station information from CSV archive files, store into PostgreSQL
      luftdatenpumpe stations --network=ldi --source=file:///var/spool/archive.luftdaten.info --target=postgresql://luftdatenpumpe@localhost/weatherbase --reverse-geocode --progress

      # Ingest readings from CSV archive files, store into InfluxDB
      luftdatenpumpe readings --network=ldi --source=file:///var/spool/archive.luftdaten.info --target=influxdb://luftdatenpumpe@localhost/luftdaten_info --progress

      # Ingest most early readings
      luftdatenpumpe readings --network=ldi --source=file:///var/spool/archive.luftdaten.info/2015-10-*

      # Ingest most early PMS sensors
      luftdatenpumpe readings --network=ldi --source=file:///var/spool/archive.luftdaten.info/2017-1*/*pms*.csv


    Live data examples (MQTT):

      # Publish data to topic "luftdaten.info" at MQTT broker running on "localhost"
      luftdatenpumpe readings --station=49,1033 --target=mqtt://localhost/luftdaten.info

      # MQTT publishing, with authentication
      luftdatenpumpe readings --station=49,1033 --target=mqtt://username:password@localhost/luftdaten.info


    Combined examples:

      # Write stations to STDERR and PostgreSQL
      luftdatenpumpe stations --station=49,1033 --target=json+stream://sys.stderr --target=postgresql://luftdatenpumpe@localhost/weatherbase

      # Write readings to STDERR, MQTT, and InfluxDB
      luftdatenpumpe readings --station=49,1033 --target=json+stream://sys.stderr --target=mqtt://localhost/luftdaten.info --target=influxdb://luftdatenpumpe@localhost/luftdaten_info

