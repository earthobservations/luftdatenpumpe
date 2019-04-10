# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import sys
import json
import logging
from docopt import docopt, DocoptExit
from luftdatenpumpe import __appname__, __version__
from luftdatenpumpe.geo import disable_nominatim_cache
from luftdatenpumpe.grafana import get_artefact
from luftdatenpumpe.target import resolve_target_handler
from luftdatenpumpe.util import normalize_options, setup_logging, read_list, read_pairs
from luftdatenpumpe.core import LuftdatenPumpe
from luftdatenpumpe.engine import LuftdatenEngine

log = logging.getLogger(__name__)


def run():
    """
    Usage:
      luftdatenpumpe stations [options] [--target=<target>]...
      luftdatenpumpe readings [options] [--target=<target>]...
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
      --create-database-view        Create database view like "ldi_view" spanning all tables.
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

      # Write list of stations and metadata to RDBMS database (PostgreSQL), also display on STDERR
      luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=postgresql:///weatherbase --target=json+stream://sys.stderr

      # Read station information from RDBMS database (PostgreSQL) and format for Grafana Worldmap Panel
      luftdatenpumpe stations --source=postgresql:///weatherbase --target=json.grafana.kn+stream://sys.stdout


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
      luftdatenpumpe stations --source=file:///var/spool/archive.luftdaten.info --target=postgresql:///weatherbase --reverse-geocode --progress

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
      luftdatenpumpe stations --station=28,1071 --target=json+stream://sys.stderr --target=postgresql:///weatherbase

      # Write readings to STDERR, MQTT and InfluxDB
      luftdatenpumpe readings --station=28,1071 --target=json+stream://sys.stderr --target=mqtt://localhost/luftdaten.info --target=influxdb://localhost:8086/luftdaten_info


    """

    # Parse command line arguments
    options = normalize_options(docopt(run.__doc__, version=__appname__ + ' ' + __version__))

    # Setup logging
    debug = options.get('debug')
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    setup_logging(log_level)

    # Debugging
    #log.info('Options: {}'.format(json.dumps(options, indent=4)))


    # A. Utility targets

    # Create database view and exit.
    if options['create-database-view']:
        log.info('Creating database view')
        for target in options['target']:
            if target.startswith('postgresql:'):
                handler = resolve_target_handler(target)
                handler.create_view()
        sys.exit()

    # Generate Grafana datasource and dashboard JSON and exit.
    elif options['grafana']:
        options.variables = read_pairs(options.variables)
        log.info('Generating Grafana artefact '
                 'kind={}, name={}, variables={}'.format(
                    options.kind, options.name, json.dumps(options.variables)))
        thing = get_artefact(options.kind, options.name, variables=options.variables)
        print(thing)
        sys.exit()


    # B. Data processing targets

    # Optionally apply filters by country code, station id and/or sensor id
    filter = {}

    # Lists of Integers.
    for filter_name in ['station', 'sensor']:
        if options[filter_name]:
            filter[filter_name] = list(map(int, read_list(options[filter_name])))

    # Lists of lower-case Strings.
    for filter_name in ['sensor-type']:
        if options[filter_name]:
            filter[filter_name] = list(map(str.lower, read_list(options[filter_name])))

    # Lists of upper-case Strings.
    for filter_name in ['country']:
        if options[filter_name]:
            filter[filter_name] = list(map(str.upper, read_list(options[filter_name])))

    log.info('Applying filter: {}'.format(filter))

    # Fake data source. Currently always LDI.
    # TODO: Add more data sources.
    datasource = 'ldi'
    datasource_humanized = datasource.upper()

    # Default output target is STDOUT.
    if not options['target']:
        options['target'] = ['json+stream://sys.stdout']

    # Optionally disable Nominatim cache.
    if options['disable-nominatim-cache']:
        # Invalidate the Nominatim cache; this applies only for this session, it will _not_ _purge_ all data at once.
        disable_nominatim_cache()

    # The main workhorse.
    pump = LuftdatenPumpe(
        source=options['source'],
        filter=filter,
        reverse_geocode=options['reverse-geocode'],
        progressbar=options['progress'],
        dry_run=options['dry-run'],
    )

    # Acquire data.
    data = None
    kind = None
    if options['stations']:
        kind = 'stations'
        log.info('Acquiring list of stations from {}. source={}'.format(datasource_humanized, options['source']))
        data = pump.get_stations()
        log.info('Acquired #{} stations'.format(len(data)))

    elif options['readings']:
        kind = 'readings'
        log.info('Acquiring readings from {}. source={}'.format(datasource_humanized, options['source']))
        data = pump.get_readings()

    else:
        raise DocoptExit('Subcommand not implemented')

    # Sanity checks.
    if data is None:
        log.error('No data to process')
        sys.exit(2)

    # Create and run output processing engine.
    log.info('Will publish data to {}'.format(options['target']))
    engine = LuftdatenEngine(kind, options['target'], options.get('dry-run', False))
    engine.process(data)
