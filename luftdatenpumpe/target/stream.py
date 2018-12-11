# -*- coding: utf-8 -*-
# (c) 2018 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
class StreamTarget:

    def __init__(self, handle, formatter):
        self.handle = handle
        self.formatter = formatter

    def emit(self, data):
        self.handle.write(self.formatter(data))
