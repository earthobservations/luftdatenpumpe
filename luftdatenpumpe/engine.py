# -*- coding: utf-8 -*-
# (c) 2018-2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging

from tqdm import tqdm

from luftdatenpumpe.target import resolve_target_handler

log = logging.getLogger(__name__)


class LuftdatenEngine:

    def __init__(self, kind, targets, batch_size=2500, progressbar=False, dry_run=False):
        self.kind = kind
        self.targets = targets
        self.batch_size = batch_size
        self.progressbar = progressbar
        self.dry_run = dry_run

    def process(self, data):

        # Configure target subsystems.
        targets = []
        for target_expression in self.targets:
            log.info(f'Configuring data sink "{target_expression}"" with kind "{self.kind}"')

            try:
                target = resolve_target_handler(target_expression, dry_run=self.dry_run)

            except Exception as ex:
                log.exception(f'Resolving data sink "{target_expression}" failed. Reason: {ex}', exc_info=False)
                continue

            if target is None:
                log.error(f'Could not resolve data sink {target_expression}')
                continue

            if self.kind not in target.capabilities:
                log.warning(f'Data sink {target_expression} does not handle kind "{self.kind}"')
                continue

            targets.append(target)

        # Sanity checks.
        if not targets:
            raise ValueError('No data sinks enabled, please check the log file for errors')

        # Emit to active target subsystems.
        log.info('Emitting to target data sinks, this might take some time')

        if self.progressbar:
            data = tqdm(list(data))

        item_count = 0
        for item in data:

            for target in targets:
                target.emit(item)
            item_count += 1

            # Preliminary flush each $batch_size items.
            if item_count % self.batch_size == 0:
                for target in targets:
                    target.flush()

        # Signal readyness to each target subsystem.
        for target in targets:
            target.flush(final=True)

        log.info('Processed {} records'.format(item_count))
