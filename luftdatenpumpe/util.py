# -*- coding: utf-8 -*-
# (c) 2017,2018 Andreas Motl <andreas@hiveeyes.org>
# (c) 2017,2018 Richard Pobering <richard@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import os
import re
import sys
import glob
import json
import logging
import traceback
import unicodedata
from itertools import zip_longest

from six import StringIO
from docopt import docopt
from munch import Munch, munchify
from collections import OrderedDict


log = logging.getLogger(__name__)


class Application:

    def __init__(self, name=None, version=None, docopt_recipe=None):

        self.name = name
        self.version = version
        self.docopt_recipe = docopt_recipe

        self.settings = Munch()
        self.options = Munch()

        self.initialize()

    def initialize(self):

        # Honor "LDA_" environment variables.
        argv = self.get_argv_with_environment()

        #print(argv)

        # Parse command line arguments.
        self.options = normalize_options(docopt(self.docopt_recipe, argv=argv, version=f'{self.name} {self.version}'))

        # Setup logging.
        self.setup_logging()

    def setup_logging(self):
        debug = self.options.get('debug')
        log_level = logging.INFO
        if debug:
            log_level = logging.DEBUG

        setup_logging(log_level)

    def log_options(self):
        # Debugging
        log.info('Options: {}'.format(json.dumps(self.options, indent=4)))

    def get_argv_with_environment(self):

        envvar_prefix = 'LDP_'

        argv = sys.argv[1:]

        def search_argv_option(barename):
            optname = '--' + barename
            for arg in argv:
                if optname in arg:
                    return True
            return False

        for name, value in os.environ.items():
            if name.startswith(envvar_prefix):
                optname = name.replace(envvar_prefix, '').lower()
                if not search_argv_option(optname):
                    option = f'--{optname}={value}'
                    argv.append(option)

        return argv


def setup_logging(level=logging.INFO):
    log_format = '%(asctime)-15s [%(name)-36s] %(levelname)-7s: %(message)s'
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
        #key = key.replace('--<>', '')
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


def sanitize_dbsymbol(symbol):
    return symbol.replace('-', '_')


def slugify(value):
    """
    Slugify function from django.utils.text, slightly modified.

    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.

    Update 2019-04-26.
    Account for strings like "wind speed (scalar)" being
    converted to things like "wind-speed-scalar-".
    So, also strip these leftovers.

    https://stackoverflow.com/questions/5574042/string-slugification-in-python/27264385#27264385
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '-', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    value = value.strip('-')
    return value


def is_nan(value):
    return value is None or str(value).lower() == 'nan'


def run_once(f):
    # https://stackoverflow.com/questions/4103773/efficient-way-of-having-a-function-only-execute-once-in-a-loop/4104188#4104188
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def remove_all(data, element):
    while True:
        try:
            data.remove(element)
        except ValueError:
            break
    return data


def chunks(iterable, chunksize):
    for group in grouper(iterable, chunksize):
        yield remove_all(list(group), None)
