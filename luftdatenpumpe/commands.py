# -*- coding: utf-8 -*-
# (c) 2017-2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017-2019 Richard Pobering <richard@hiveeyes.org>
# (c) 2019 Matthias Mehldau <wetter@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import sys
import json
import logging
from docopt import docopt, DocoptExit
from luftdatenpumpe import __appname__, __version__
from luftdatenpumpe.grafana import get_artefact
from luftdatenpumpe.source import resolve_source_handler
from luftdatenpumpe.source.rdbms import stations_from_rdbms
from luftdatenpumpe.engine import LuftdatenEngine
from luftdatenpumpe.util import normalize_options, setup_logging, read_pairs, Application

log = logging.getLogger(__name__)

network_list = ['ldi', 'irceline']


def run():
    """
    Usage:
      luftdatenpumpe networks
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
      --disable-nominatim-cache     Disable Nominatim reverse geocoder cache
      --progress                    Show progress bar
      --version                     Show version information
      --dry-run                     Skip publishing to MQTT bus
      --debug                       Enable debug messages
      -h --help                     Show this screen


    Network list example:

      # Display list of supported sensor networks
      luftdatenpumpe networks

    Basic station list examples:

      # Display metadata for given countries in JSON format
      luftdatenpumpe stations --network=ldi --database=ldi --country=BE,NL,LU

      # Display metadata for given stations in JSON format, with reverse geocoding
      luftdatenpumpe stations --network=ldi --station=28,1071 --reverse-geocode


    Heads up!

      From now on, let's pretend we always want to operate on data coming from the
      sensor network "luftdaten.info". which is identified by "--network=ldi". To
      make this more convenient, we use an environment variable to signal this
      to subsequent invocations of "luftdatenpumpe" by running::

        export LDP_NETWORK=ldi

    Further examples:

      # Display metadata for given sensors in JSON format, with reverse geocoding
      luftdatenpumpe stations --sensor=28,1071 --reverse-geocode

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
      luftdatenpumpe readings --station=28,1071 --target=influxdb://luftdatenpumpe@localhost/luftdaten_info

      # Store into InfluxDB, with UDP
      luftdatenpumpe readings --station=28,1071 --target=udp+influxdb://localhost:4445/luftdaten_info

      # Store into InfluxDB, with authentication
      luftdatenpumpe readings --station=28,1071 --target=influxdb://luftdatenpumpe@localhost/luftdaten_info


    LDI CSV archive data examples (InfluxDB):

      # Mirror archive of luftdaten.info, limiting to 2015 only
      wget --mirror --continue --no-host-directories --directory-prefix=/var/spool/archive.luftdaten.info --accept-regex='2015' http://archive.luftdaten.info/

      # Ingest station information from CSV archive files, store into PostgreSQL
      luftdatenpumpe stations --network=ldi --source=file:///var/spool/archive.luftdaten.info --target=postgresql://luftdatenpumpe@localhost/weatherbase --reverse-geocode --progress

      # Ingest readings from CSV archive files, store into InfluxDB
      luftdatenpumpe readings --network=ldi --source=file:///var/spool/archive.luftdaten.info --station=483 --sensor=988 --target=influxdb://luftdatenpumpe@localhost/luftdaten_info --progress

      # Ingest most early readings
      luftdatenpumpe readings --network=ldi --source=file:///var/spool/archive.luftdaten.info/2015-10-*

      # Ingest most early PMS sensors
      luftdatenpumpe readings --network=ldi --source=file:///var/spool/archive.luftdaten.info/2017-1*/*pms*.csv


    Live data examples (MQTT):

      # Publish data to topic "luftdaten.info" at MQTT broker running on "localhost"
      luftdatenpumpe readings --station=28,1071 --target=mqtt://localhost/luftdaten.info

      # MQTT publishing, with authentication
      luftdatenpumpe readings --station=28,1071 --target=mqtt://username:password@localhost/luftdaten.info


    Combined examples:

      # Write stations to STDERR and PostgreSQL
      luftdatenpumpe stations --station=28,1071 --target=json+stream://sys.stderr --target=postgresql://luftdatenpumpe@localhost/weatherbase

      # Write readings to STDERR, MQTT and InfluxDB
      luftdatenpumpe readings --station=28,1071 --target=json+stream://sys.stderr --target=mqtt://localhost/luftdaten.info --target=influxdb://luftdatenpumpe@localhost/luftdaten_info


    """

    # Bootstrap application.
    application = Application(name=__appname__, version=__version__, docopt_recipe=run.__doc__)

    options = application.options

    # 1. Run some sanity checks on ingress parameters.
    if options.networks:
        log.info('List of available networks: %s', network_list)
        sys.exit(0)
    check_options(options)

    # 2. Dispatch to maintenance targets.
    run_maintenance(options)

    # 3. Dispatch to data processing targets.
    run_engine(options)


def run_maintenance(options):

    # A. Maintenance targets
    # Create database view "ldi_network" spanning all "ldi_*" tables.
    if options['database']:

        if not options['target']:
            message = 'No target for database operation given'
            log.error(message)
            raise NotImplementedError(message)

        engine = get_engine(options)
        for target in options['target']:
            if target.startswith('postgresql:'):
                handler = engine.resolve_target_handler(target)

                try:

                    if options['drop-data']:
                        handler.drop_data()

                    if options['drop-tables']:
                        handler.drop_tables()

                    if options['drop-database']:
                        handler.drop_database()

                    if options['create-views']:
                        log.info('Creating database views')
                        handler.create_views()

                    if options['grant-user']:
                        log.info('Granting read privileges to "%s"', options['grant-user'])
                        handler.grant_read_privileges(options['grant-user'])

                except Exception as ex:
                    log.exception('Database operation failed. Reason: %s', ex, exc_info=False)

            else:
                log.warning('Can not run database operation on "%s"', target)

        sys.exit()

    # Generate JSON for Grafana datasource or dashboard and exit.
    elif options['grafana']:
        options.variables = read_pairs(options.variables)
        options.fields = read_pairs(options.fields)
        thing = get_artefact(options.kind, options.name, variables=options.variables, fields=options.fields)
        print(thing)
        sys.exit()


def check_options(options):

    # A. Sanity checks
    if not options.network:
        message = '--network parameter missing'
        log.error(message)
        raise DocoptExit(message)

    # A.2 Resolve data source handler class from network identifier.
    options.network = options.network.lower()

    # A.3 Resolve data domain (stations vs. readings).
    options.domain = None
    for flavor in ['stations', 'readings']:
        if options[flavor]:
            options.domain = flavor
            break


def get_engine(options):

    # Create and run output processing engine.
    log.info(f'Will publish data to {options.target}')
    engine = LuftdatenEngine(
        network=options.network,
        domain=options.domain,
        targets=options.target,
        progressbar=options.progress,
        dry_run=options['dry-run'],
    )

    return engine


def get_data(options):

    pump = resolve_source_handler(options)

    # Acquire data.
    if options.domain == 'stations':
        log.info(f'Acquiring list of stations from network "{options.network}" with source "{options.source}"')

        if options.source.startswith('postgresql://'):
            data = stations_from_rdbms(options.source, options.network)

        else:
            data = pump.get_stations()

        log.info(f'Acquired #{len(data)} stations')

    elif options.domain == 'readings':
        log.info(f'Acquiring readings from network "{options.network}" with source "{options.source}"')
        data = pump.get_readings()

    else:
        raise DocoptExit('Subcommand not implemented')

    # Sanity checks.
    if data is None:
        log.error('No data to process')
        sys.exit(2)

    return data


def run_engine(options):
    data = get_data(options)
    engine = get_engine(options)
    engine.process(data)
