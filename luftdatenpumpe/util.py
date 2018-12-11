# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import sys
import logging
import traceback
from six import StringIO


def setup_logging(level=logging.INFO):
    log_format = '%(asctime)-15s [%(name)-25s] %(levelname)-7s: %(message)s'
    logging.basicConfig(
        format=log_format,
        stream=sys.stderr,
        level=level)

    # TODO: Control debug logging of HTTP requests through yet another commandline option "--debug-http" or "--debug-requests"
    requests_log = logging.getLogger('requests')
    requests_log.setLevel(logging.WARN)


def normalize_options(options):
    normalized = {}
    for key, value in options.items():
        key = key.strip('--<>')
        normalized[key] = value
    return normalized


def read_list(data, separator=u','):
    if data is None:
        return []
    result = list(map(lambda x: x.strip(), data.split(separator)))
    if len(result) == 1 and not result[0]:
        result = []
    return result


def exception_traceback(exc_info=None):
    """
    Return a string containing a traceback message for the given
    exc_info tuple (as returned by sys.exc_info()).

    from setuptools.tests.doctest
    """

    if not exc_info:
        exc_info = sys.exc_info()

    # Get a traceback message.
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    return excout.getvalue()


def to_list(obj):
    """Convert an object to a list if it is not already one"""
    if not isinstance(obj, (list, tuple)):
        obj = [obj, ]
    return obj
