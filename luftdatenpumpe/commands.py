# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import sys
import logging
from docopt import docopt
from luftdatenpumpe import __appname__, __version__
from luftdatenpumpe.geo import disable_nominatim_cache
from luftdatenpumpe.util import normalize_options, setup_logging, read_list
from luftdatenpumpe.core import LuftdatenPumpe
from luftdatenpumpe.engine import LuftdatenEngine

log = logging.getLogger(__name__)


def run():
    """
    Usage:
      luftdatenpumpe stations [options] [--target=<target>]...
      luftdatenpumpe readings [options] [--target=<target>]...
      luftdatenpumpe --version
      luftdatenpumpe (-h | --help)

    Options:
      --station=<stations>          Filter data by given location ids, comma-separated.
      --sensor=<sensors>            Filter data by given sensor ids, comma-separated.
      --reverse-geocode             Compute geographical address using the Nominatim reverse geocoder
      --target=<target>             Data output target
      --progress                    Show progress bar
      --version                     Show version information
      --dry-run                     Skip publishing to MQTT bus
      --disable-nominatim-cache     Disable Nominatim reverse geocoder cache
      --debug                       Enable debug messages
      -h --help                     Show this screen

    Station list examples:

      # Display metadata for given stations in JSON format
      luftdatenpumpe stations --station=28,1071 --reverse-geocode

      # Display metadata for given sensors in JSON format
      luftdatenpumpe stations --sensor=657,2130 --reverse-geocode

      # Display list of stations in JSON format, suitable for integrating with Grafana
      luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=json.grafana+stream://sys.stdout

      # Write list of stations and metadata to PostgreSQL database, also display on STDERR
      luftdatenpumpe stations --station=28,1071 --reverse-geocode --target=postgresql:///weatherbase --target=json+stream://sys.stderr

    Data examples (InfluxDB):

      # Store into InfluxDB running on "localhost"
      luftdatenpumpe readings --station=28,1071 --target=influxdb://localhost:8086/luftdaten_info

      # Store into InfluxDB, with UDP
      luftdatenpumpe readings --station=28,1071 --target=udp+influxdb://localhost:4445/luftdaten_info

      # Store into InfluxDB, with authentication
      luftdatenpumpe readings --station=28,1071 --target=influxdb://username:password@localhost:8086/luftdaten_info

    Data examples (MQTT):

      # Publish data to topic "luftdaten.info" at MQTT broker running on "localhost"
      luftdatenpumpe readings --station=28,1071 --target=mqtt://localhost/luftdaten.info

      # MQTT publishing, with authentication
      luftdatenpumpe readings --station=28,1071 --target=mqtt://username:password@localhost/luftdaten.info

    Combined examples:

      # Write stations to STDERR and PostgreSQL
      luftdatenpumpe readings --station=28,1071 \
        --target=json+stream://sys.stderr \
        --target=postgresql:///weatherbase

      # Write readings to STDERR, MQTT and InfluxDB
      luftdatenpumpe readings --station=28,1071 \
        --target=json+stream://sys.stderr \
        --target=mqtt://localhost/luftdaten.info \
        --target=influxdb://localhost:8086/luftdaten_info

    """

    # Parse command line arguments
    options = normalize_options(docopt(run.__doc__, version=__appname__ + ' ' + __version__))

    # Setup logging
    debug = options.get('debug')
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    setup_logging(log_level)

    #log.info('Options: {}'.format(json.dumps(options, indent=4)))

    # Optionally, decode filters by station id and/or sensor id
    filter = {}
    for filter_name in ['station', 'sensor']:
        if options[filter_name]:
            filter[filter_name] = list(map(int, read_list(options[filter_name])))
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
        log.info('Acquiring list of stations for {}'.format(datasource_humanized))
        data = pump.get_stations()
        log.info('Acquired #{} stations'.format(len(data)))

    elif options['readings']:
        kind = 'readings'
        log.info('Will publish readings to {}'.format(options['target']))
        data = pump.get_readings()
        log.info('Acquired readings')

    # Sanity checks.
    if data is None:
        log.error('No data to process')
        sys.exit(2)

    # Create and run output processing engine.
    engine = LuftdatenEngine(kind, options['target'], options.get('dry-run', False))
    engine.process(data)
