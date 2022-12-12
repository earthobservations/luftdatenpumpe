# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

requires = [
    # Core
    "appdirs<2",
    "docopt<1",
    "munch<3",
    "tqdm<5",
    # Acquisition
    "requests<3",
    "tablib[pandas]<4",
    "py-openaq<2",
    # Caching
    "requests-cache<1",
    "dogpile.cache<2",
    "redis<5",
    # Adapters
    "paho-mqtt<2",
    "dataset<2",
    "psycopg2-binary<3",
    "GeoAlchemy2<1",
    "influxdb<6",
    "SQLAlchemy<1.4",
    "SQLAlchemy-Utils<1",
    # Date/Time
    "rfc3339<7",
    # Geospatial
    "geohash2<2",
    "geopy<2",
    # Grafana
    "Jinja2<3",
    "MarkupSafe<2.1",
]

extras = {
    "test": [
        "pytest>=7,<8",
        "attrs",
        "pytest-cov<4",
    ],
}

setup(
    name="luftdatenpumpe",
    version="0.21.1",
    description="Process live and historical data from luftdaten.info, IRCELINE and OpenAQ. Filter by "
    "station-id, sensor-id and sensor-type, apply reverse geocoding, store into time-series "
    "and RDBMS databases, publish to MQTT, output as JSON, or visualize in Grafana.",
    long_description=README,
    license="AGPL 3, EUPL 1.2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
    ],
    author="Andreas Motl",
    author_email="andreas.motl@panodata.org",
    url="https://github.com/earthobservations/luftdatenpumpe",
    # https://github.com/pypi/warehouse/blob/01f87cfd/warehouse/templates/packaging/detail.html#L20-L58
    project_urls={
        "Changelog": "https://github.com/earthobservations/luftdatenpumpe/blob/main/CHANGES.rst",
        "Documentation": "https://github.com/earthobservations/luftdatenpumpe/tree/main/doc",
        "Download": "https://pypi.org/project/luftdatenpumpe/#files",
        "Homepage": "https://community.panodata.org/t/luftdatenpumpe/21",
        "Issues": "https://github.com/earthobservations/luftdatenpumpe/issues",
        "Releases": "https://github.com/earthobservations/luftdatenpumpe/releases",
        "Repository": "https://github.com/earthobservations/luftdatenpumpe",
    },
    keywords="luftdaten.info irceline openaq "
    "air quality particulate matter pollution "
    "feinstaub luftdaten "
    "ogc sos "
    "sensor network observation "
    "opendata data acquisition transformation export "
    "geospatial temporal timeseries "
    "http rest json api "
    "rdbms sql mysql "
    "mosquitto mqtt "
    "openstreetmap nominatim "
    "postgis postgresql influxdb grafana 52north",
    packages=find_packages(),
    include_package_data=True,
    package_data={},
    zip_safe=False,
    test_suite="luftdatenpumpe.test",
    install_requires=requires,
    extras_require=extras,
    tests_require=extras["test"],
    dependency_links=[],
    entry_points={
        "console_scripts": [
            "luftdatenpumpe = luftdatenpumpe.commands:run",
        ],
    },
)
