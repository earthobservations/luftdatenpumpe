# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = [

    # Core
    'six==1.12.0',
    'appdirs==1.4.3',
    'docopt==0.6.2',
    'munch==2.3.2',
    'tqdm==4.31.1',

    # Acquisition
    'requests==2.21.0',
    'tablib==0.13.0',

    # Caching
    'requests-cache==0.5.0',
    'dogpile.cache==0.7.1',
    'redis==3.2.1',

    # Adapters
    'paho-mqtt==1.4.0',
    'dataset==1.1.2',
    'psycopg2-binary==2.8.2',
    'GeoAlchemy2==0.6.1',
    'influxdb==5.2.2',
    'SQLAlchemy-Utils==0.33.11',

    # Date/Time
    'rfc3339==6.0',

    # Geospatial
    'geohash2==1.1',
    'geopy==1.19.0',

    # Grafana
    'Jinja2==2.10.1',
]

extras = {
    'test': [
        'pytest==4.0.1',
        'pytest-cov==2.6.0',
    ],
}

setup(name='luftdatenpumpe',
      version='0.11.0',
      description='Process live and historical data from luftdaten.info. Filter by station-id, '
                  'sensor-id and sensor-type, apply reverse geocoding, store into TSDB and '
                  'RDBMS databases, publish to MQTT or just output as JSON.',
      long_description=README,
      license="AGPL 3, EUPL 1.2",
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications",
        "Topic :: Database",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Archiving",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS"
        ],
      author='Andreas Motl',
      author_email='andreas@hiveeyes.org',
      url='https://github.com/hiveeyes/luftdatenpumpe',
      keywords='luftdaten.info irceline '
               'air quality particulate matter pollution '
               'feinstaub luftdaten '
               'ogc sos '
               'sensor network observation '
               'opendata data acquisition transformation export '
               'geospatial temporal timeseries '
               'http rest json api '
               'rdbms sql mysql '
               'mosquitto mqtt '
               'openstreetmap nominatim '
               'postgis postgresql influxdb grafana 52north',
      packages=find_packages(),
      include_package_data=True,
      package_data={
      },
      zip_safe=False,
      test_suite='luftdatenpumpe.test',
      install_requires=requires,
      extras_require = extras,
      tests_require=extras['test'],
      dependency_links=[
      ],
      entry_points={
          'console_scripts': [
              'luftdatenpumpe = luftdatenpumpe.commands:run',
          ],
      },
)
