# -*- coding: utf-8 -*-
# (c) 2018 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
class StreamTarget:

    capabilities = ['stations', 'readings']

    def __init__(self, handle, formatter):
        self.handle = handle
        self.formatter = formatter
        self.buffer = []

    def emit(self, data):
        self.buffer.append(data)

    def flush(self, final=False):
        if not final:
            return
        self.handle.write(self.formatter(self.buffer))
        self.buffer = []
