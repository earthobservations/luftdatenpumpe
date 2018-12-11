# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

requires = [
    # Core
    'six==1.11.0',
    'appdirs==1.4.3',
    'docopt==0.6.2',
    'requests==2.20.1',
    'munch==2.3.2',
    'tqdm==4.28.1',

    # Caching
    'requests-cache==0.4.13',
    'dogpile.cache==0.6.8',
    'redis==3.0.1',

    # Adapters
    'paho-mqtt==1.4.0',
    'dataset==1.1.0',
    'psycopg2-binary==2.7.6.1',

    # Geospatial
    'Geohash==1.0',
    'geopy==1.18.0',
]

extras = {
    'test': [
        'pytest==4.0.1',
        'pytest-cov==2.6.0',
    ],
}

setup(name='luftdatenpumpe',
      version='0.4.1',
      description='Process data from live API of luftdaten.info',
      long_description='Request data from live API of luftdaten.info, enrich with geospatial information and publish to MQTT bus.',
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
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Archiving",
        "Topic :: System :: Networking :: Monitoring",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS"
        ],
      author='Andreas Motl',
      author_email='andreas@hiveeyes.org',
      url='https://hiveeyes.org/',
      keywords='luftdaten.info opendata data acquisition ' +
               'mqtt http rest sql ' +
               'influxdb mosquitto grafana',
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
          # This fork makes the package install on Python 3.x
          'https://github.com/webartifex/geohash/raw/master/dist/Geohash-1.0-py3.6.egg#egg=Geohash-1.0',
      ],
      entry_points={
          'console_scripts': [
              'luftdatenpumpe = luftdatenpumpe.commands:run',
          ],
      },
)
