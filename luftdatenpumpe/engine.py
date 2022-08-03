# -*- coding: utf-8 -*-
# (c) 2018-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
from urllib.parse import urlparse

from munch import Munch
from tqdm import tqdm

from luftdatenpumpe.target.influxdb import InfluxDBStorage
from luftdatenpumpe.target.json import (
    JsonFlexFormatter,
    json_formatter,
    json_grafana_formatter_kn,
    json_grafana_formatter_vt,
)
from luftdatenpumpe.target.mqtt import MQTTAdapter
from luftdatenpumpe.target.rdbms import RDBMSStorage
from luftdatenpumpe.target.stream import StreamTarget

log = logging.getLogger(__name__)


class LuftdatenEngine:
    def __init__(self, network, domain, targets, fieldmap=None, batch_size=None, progressbar=False, dry_run=False):
        self.network = network
        self.domain = domain
        self.targets = targets
        self.fieldmap = fieldmap
        self.batch_size = batch_size or 1
        self.progressbar = progressbar
        self.dry_run = dry_run

    def process(self, data):

        # Configure target subsystems.
        targets = []
        for target_expression in self.targets:
            log.info(f'Configuring data sink "{target_expression}" with domain "{self.domain}"')

            try:
                target = self.resolve_target_handler(target_expression, dry_run=self.dry_run)

            except Exception as ex:
                log.exception(f'Resolving data sink "{target_expression}" failed. Reason: {ex}', exc_info=False)
                continue

            if target is None:
                log.error(f"Could not resolve data sink {target_expression}")
                continue

            if self.domain not in target.capabilities:
                log.warning(f'Data sink {target_expression} does not handle domain "{self.domain}"')
                continue

            targets.append(target)

        # Sanity checks.
        if not targets:
            raise ValueError("No data sinks enabled, please check the log file for errors")

        # Emit to active target subsystems.
        log.info("Emitting to target data sinks, this might take some time")

        if self.progressbar:
            data = tqdm(data)

        item_count = 0
        for item in data:

            for target in targets:
                target.emit(item)
            item_count += 1

            # Preliminary flush each $batch_size items.
            if item_count % self.batch_size == 0:
                for target in targets:
                    # Don't flush STDOUT targets preliminary, otherwise JSON output breaks.
                    if isinstance(target, StreamTarget):
                        continue
                    target.flush()

        # Signal final readiness to each target subsystem.
        for target in targets:
            target.flush(final=True)

        log.info("Processed {} records".format(item_count))

    def resolve_target_handler(self, target, dry_run=False):
        handler = None

        url = Munch(urlparse(target)._asdict())
        log.debug("Resolving target: %s", json.dumps(url))

        formatter = json_formatter
        if "+" in url.scheme:
            format, scheme = url.scheme.split("+")
            url.scheme = scheme

            if format.startswith("json.grafana.vt"):
                formatter = json_grafana_formatter_vt
            elif format.startswith("json.grafana.kn"):
                formatter = json_grafana_formatter_kn
            elif format.startswith("json.flex"):
                formatter = JsonFlexFormatter(self.fieldmap).formatter
            elif format.startswith("json"):
                formatter = json_formatter

            # Do we need this anymore?
            # formatter.format = format

        # effective_url = urlunparse(url.values())

        if url.scheme == "stream":

            # FIXME: There might be dragons?
            import sys  # noqa:F401

            stream = eval(url.netloc)

            handler = StreamTarget(stream, formatter)

        elif url.scheme in RDBMSStorage.get_dialects():
            handler = RDBMSStorage(target, network=self.network, dry_run=dry_run)

        elif url.scheme == "mqtt":
            handler = MQTTAdapter(target, dry_run=dry_run)

        elif url.scheme == "influxdb":
            handler = InfluxDBStorage(target, network=self.network, dry_run=dry_run)

        return handler
