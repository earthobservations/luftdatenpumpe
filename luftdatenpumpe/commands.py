# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import sys
import json
import logging

from docopt import docopt

from . import __appname__, __version__
from .util import setup_logging
from .core import LuftdatenPumpe
from .adapter.rdbms import RDBMSStorage

log = logging.getLogger(__name__)


def run():
    """
    Usage:
      luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten.info [--sensors=<sensors>] [--stations=<stations>] [--reverse-geocode] [--progress] [--debug] [--dry-run]
      luftdatenpumpe stations [--sensors=<sensors>] [--stations=<stations>] [--reverse-geocode] [--format=<format>] [--progress] [--debug] [--dry-run]
      luftdatenpumpe --version
      luftdatenpumpe (-h | --help)

    Options:
      --mqtt-uri=<mqtt-uri>         Use specified MQTT broker
      --sensors=<sensors>           Filter data by given sensor ids, comma-separated.
      --stations=<stations>       Filter data by given location ids, comma-separated.
      --reverse-geocode             Compute geographical address using the Nominatim reverse geocoder and add to MQTT message
      --format=<format>             Output format
      --progress                    Show progress bar
      --version                     Show version information
      --dry-run                     Run data acquisition and postprocessing but skip publishing to MQTT bus
      --debug                       Enable debug messages
      -h --help                     Show this screen

    Examples:

      # Publish data to topic "luftdaten.info" at MQTT broker "mqtt.example.org"
      luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten.info

      # Publish fully enriched data for multiple sensor ids
      luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten.info --reverse-geocode --sensors=2115,2116

      # Publish fully enriched data for multiple location ids
      luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten.info --reverse-geocode --stations=1064,1071

      # Publish data suitable for displaying in Grafana Worldmap Panel using Kotori
      luftdatenpumpe forward --mqtt-uri mqtt://mqtt.example.org/luftdaten/testdrive/earth/42/data.json --reverse-geocode --progress

      # Display list of stations in JSON format
      luftdatenpumpe stations --stations=1064,1071 --reverse-geocode

      # Display list of stations in JSON format, suitable for integrating with Grafana
      luftdatenpumpe stations --stations=1064,1071 --reverse-geocode --format=grafana

    """

    # Parse command line arguments
    options = docopt(run.__doc__, version=__appname__ + ' ' + __version__)
    #print 'options: {}'.format(options)

    debug = options.get('--debug')

    # Setup logging
    log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG
    setup_logging(log_level)

    # Optionally, apply filters by sensor id and location id
    filter = {}
    for filter_name in ['stations', 'sensors']:
        filter_option = '--' + filter_name
        if options[filter_option]:
            filter[filter_name] = list(map(int, options[filter_option].replace(' ', '').split(',')))

    mqtt_uri = options.get('--mqtt-uri')

    pump = LuftdatenPumpe(
        filter=filter,
        reverse_geocode=options['--reverse-geocode'],
        mqtt_uri=mqtt_uri,
        progressbar=options['--progress'],
        dry_run=options['--dry-run'],
    )

    if options['stations']:
        log.info('List of stations')
        if options['--format'] == 'grafana':
            stations = pump.get_stations_grafana()
        else:
            stations = pump.get_stations()

        print(json.dumps(stations, indent=4))

        #storage = RDBMSStorage()
        #storage.store_stations(stations)
        #storage.dump_tables()
        #storage.demo_query()

    elif options['forward']:

        if not mqtt_uri:
            log.critical('Parameter "--mqtt-uri" missing or empty')
            sys.exit(1)

        log.info('Will publish to MQTT at {}'.format(mqtt_uri))

        pump.forward_to_mqtt()
