# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import os
import sys
import glob
import logging
import traceback
from six import StringIO
from munch import munchify
from collections import OrderedDict


def setup_logging(level=logging.INFO):
    log_format = '%(asctime)-15s [%(name)-30s] %(levelname)-7s: %(message)s'
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
    return munchify(normalized)


def read_list(data, separator=u','):
    if data is None:
        return []
    result = list(map(lambda x: x.strip(), data.split(separator)))
    if len(result) == 1 and not result[0]:
        result = []
    return result


def read_pairs(data, listsep=u',', pairsep=u'='):
    if data is None:
        return {}
    pairs = list(map(lambda x: x.strip(), data.split(listsep)))
    if len(pairs) == 1 and not pairs[0]:
        return {}
    result = OrderedDict()
    for pair in pairs:
        key, value = pair.split(pairsep)
        result[key] = value
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


def invalidate_dogpile_cache(cache_instance, hard=True):
    """
    The default invalidation system works by setting
    a current timestamp (using ``time.time()``)
    representing the "minimum creation time" for
    a value.  Any retrieved value whose creation
    time is prior to this timestamp
    is considered to be stale.  It does not
    affect the data in the cache in any way, and is
    **local to this instance of :class:`.CacheRegion`.**

    .. warning::

        The :meth:`.CacheRegion.invalidate` method's default mode of
        operation is to set a timestamp **local to this CacheRegion
        in this Python process only**.   It does not impact other Python
        processes or regions as the timestamp is **only stored locally in
        memory**.  To implement invalidation where the
        timestamp is stored in the cache or similar so that all Python
        processes can be affected by an invalidation timestamp, implement a
        custom :class:`.RegionInvalidationStrategy`.

    The method supports both "hard" and "soft" invalidation
    options.  With "hard" invalidation,
    :meth:`.CacheRegion.get_or_create` will force an immediate
    regeneration of the value which all getters will wait for.
    With "soft" invalidation, subsequent getters will return the
    "old" value until the new one is available.
    """
    cache_instance.invalidate(hard=hard)


def find_files_glob(pattern):
    return sorted(glob.glob(pattern, recursive=True))


def find_files_walk(path, suffix):
    for root, subdirs, files in os.walk(path):
        # https://python-forum.io/Thread-why-i-don-t-like-os-walk?pid=35718#pid35718
        subdirs[:] = sorted(subdirs)  # sorts the subdirs
        for name in sorted(files):
            realname = os.path.join(root, name)
            if realname.endswith(suffix):
                yield realname

find_files = find_files_glob
