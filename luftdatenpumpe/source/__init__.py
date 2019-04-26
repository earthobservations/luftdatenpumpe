# -*- coding: utf-8 -*-
# (c) 2018-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging

from munch import Munch

from luftdatenpumpe.geo import disable_nominatim_cache
from luftdatenpumpe.source.luftdaten_info import LuftdatenPumpe
from luftdatenpumpe.source.irceline import IrcelinePumpe
from luftdatenpumpe.util import read_list

log = logging.getLogger(__name__)


def resolve_source_handler(options, dry_run=False):
    handler = None

    # TODO: Add more data sources.
    if options.network == 'ldi':
        datapump_class = LuftdatenPumpe

    elif options.network == 'irceline':
        datapump_class = IrcelinePumpe

    else:
        message = f'Network "{options.network}" not implemented'
        log.error(message)
        raise NotImplementedError(message)


    # B. Data processing targets

    # Optionally apply filters by country code, station id and/or sensor id
    filter = Munch()

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

    if options.timespan:
        filter.timespan = options.timespan

    if filter:
        log.info('Applying filter: {}'.format(filter))

    # Default output target is STDOUT.
    if not options['target']:
        options['target'] = ['json+stream://sys.stdout']

    # Optionally disable Nominatim cache.
    if options['disable-nominatim-cache']:
        # Invalidate the Nominatim cache; this applies only for this session, it will _not_ _purge_ all data at once.
        disable_nominatim_cache()

    # The main workhorse.
    pump = datapump_class(
        source=options['source'],
        filter=filter,
        reverse_geocode=options['reverse-geocode'],
        progressbar=options['progress'],
        dry_run=options['dry-run'],
    )

    return pump
