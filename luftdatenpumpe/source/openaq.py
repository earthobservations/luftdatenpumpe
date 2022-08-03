# -*- coding: utf-8 -*-
# (c) 2020 Andreas Motl <andreas.motl@panodata.org>
# (c) 2020 Richard Pobering <richard.pobering@panodata.org>
# (c) 2020 Matthias Mehldau <matthias.mehldau@panodata.org>
# License: GNU Affero General Public License, Version 3
import json
import logging
from datetime import datetime, timedelta
from operator import itemgetter

import openaq
from munch import Munch
from rfc3339 import rfc3339

from luftdatenpumpe.source.common import AbstractLuftdatenPumpe

log = logging.getLogger(__name__)


class OpenAQPumpe(AbstractLuftdatenPumpe):
    """
    Ingest air quality measurements from the OpenAQ platform.

    - https://openaq.org/
    - https://community.panodata.org/t/openaq/150
    - https://community.panodata.org/t/using-the-openaq-api-to-acquire-open-air-quality-information-from-python/151
    - http://dhhagan.github.io/py-openaq/tutorial/api.html
    """

    # Sensor network identifier.
    network = "openaq"
    uri = "data.openaq.org"

    def get_stations(self):

        stations = {}
        field_candidates = ["station_id", "name", "position", "location"]
        for reading in self.get_readings():

            # Location ID is "station_id" here.
            station_id = reading.station.station_id

            # New station found: Acquire its information from the reading itself.
            if station_id not in stations:
                station = Munch()
                for field in field_candidates:
                    if field in reading.station:
                        station[field] = reading.station[field]
                station.sensors = []

                # Record station.
                stations[station_id] = station

            # Use recorded station.
            station = stations[station_id]

            # Deduce sensor information from the reading itself.
            keys = set()
            for observation in reading.observations:

                for key in observation.data.keys():
                    keys.add(key)

            for key in keys:
                # Don't list sensors twice.
                # if any(map(lambda item: item.sensor_id == observation.meta.sensor_id, station['sensors'])):
                #    continue

                # Build and record sensor information.
                sensor_info = Munch(
                    {
                        # 'sensor_id': observation.meta.sensor_id,
                        "sensor_type_name": key,
                        # 'sensor_type_id': observation.meta.sensor_type_id,
                    }
                )
                station["sensors"].append(sensor_info)

        # List of stations sorted by station identifier.
        results = sorted(stations.values(), key=itemgetter("station_id"))
        return results

    def get_readings_from_api(self):
        # return self.get_latest_readings()
        return self.get_current_measurement_readings()

    @staticmethod
    def last_hour():
        now = datetime.now()
        now_aligned_to_hour = now - timedelta(
            hours=1, minutes=now.minute, seconds=now.second, microseconds=now.microsecond
        )
        return rfc3339(now_aligned_to_hour, utc=True)

    def get_current_measurement_readings(self):
        """
        Acquire data from the "measurements" API.
        https://docs.openaq.org/#api-Measurements
        """

        # Fetch data from remote API.
        log.info("Requesting measurement data from OpenAQ")

        api = openaq.OpenAQ()

        params = {}
        if self.filter and "country" in self.filter:
            params["country"] = self.filter["country"]

        # TODO: What to do with readings which do not have any geographic information?
        # TODO: Raise limit by introducing result paging.
        date_from = self.last_hour()
        status, response = api.measurements(
            date_from=date_from, has_geo=True, limit=10000, include_fields=["attribution"], **params
        )
        data = response["results"]

        if not data:
            log.warning("No records found beginning {} with filter {}".format(date_from, params))
            return

        # Mungle timestamp to be formally in ISO 8601 format (UTC).
        timestamp = data[0]["date"]["utc"]
        log.info("Timestamp of first record: {}".format(timestamp))

        # Apply data filter.
        # data = self.apply_filter(data)

        # Transform live API items to actual readings while optionally
        # applying a number of transformation and enrichment steps.
        readings = {}
        for item in self.wrap_progress(data):
            try:
                self.process_measurement(readings, item)

            except:  # noqa:E722
                log.exception(f"Could not use observation from item: {item}")

        for reading in readings.values():
            has_data = False
            for observation in reading.observations:
                if observation["data"]:
                    has_data = True
                    break
            if has_data:
                yield reading

    def process_measurement(self, readings, item):
        """
        {
          "location": "Karve Road, Pune - MPCB",
          "parameter": "pm25",
          "date": {
            "utc": "2020-01-08T04:15:00.000Z",
            "local": "2020-01-08T09:45:00+05:30"
          },
          "value": 77.4,
          "unit": "µg/m³",
          "coordinates": {
            "latitude": 18.5011743,
            "longitude": 73.8165527
          },
          "country": "IN",
          "city": "Pune"
        }

        :param readings:
        :param item:
        :return:
        """

        log.debug("Making reading from item: %s", item)

        location = item["location"]

        # TODO: Enrich location by requesting...
        # https://api.openaq.org/v1/locations/?location[]=CRRI%20Mathura%20Road,%20Delhi%20-%20IMD

        if location in readings:
            entry = readings[location]
        else:
            entry = Munch(
                station=Munch(),
                observations=[],
            )

            # Set station metadata.
            entry.station.station_id = "[{}] {}".format(item["country"], item["location"])

            # Collect position information.
            entry.station.position = Munch()
            entry.station.position["country"] = item["country"]
            entry.station.position["city"] = item["city"]
            if "coordinates" in item and isinstance(item["coordinates"], dict):
                entry.station.position["latitude"] = item["coordinates"]["latitude"]
                entry.station.position["longitude"] = item["coordinates"]["longitude"]

            # Add more detailed location information.
            self.enrich_station(entry.station)

            readings[location] = entry

        # readings.setdefault(location, {})
        # readings[location].setdefault(timestamp, [])

        # Decode item.
        timestamp = item["date"]["utc"]

        # Find observation.
        observation = None
        for ob in entry.observations:
            if ob.meta.timestamp == timestamp:
                observation = ob
                break

        if observation is None:
            observation = Munch(
                meta=Munch(),
                data=Munch(),
            )

            # Set observation metadata.
            observation.meta.timestamp = timestamp
            observation.meta.sensor_type_name = "unknown"
            # observation.meta.sensor_type_id = 'aq'

            entry.observations.append(observation)

        # Set observation data.
        value = float(item["value"])
        if value >= 0:
            parameter = item["parameter"]
            observation.data[parameter] = value

        # log.debug('Observation: %s', json.dumps(observation))

        # Debugging.
        # break

    def get_latest_readings(self):
        """
        Acquire data from the "latest" API.
        https://docs.openaq.org/#api-Latest
        """

        # Fetch data from remote API.
        log.info("Requesting latest data from OpenAQ")

        api = openaq.OpenAQ()

        # Example.
        # res = api.latest(city='Delhi', parameter='pm25', df=True)
        # print(res.columns)

        params = {}
        if self.filter and "country" in self.filter:
            params["country"] = self.filter["country"]

        # TODO: What to do with readings which do not have any geographic information?
        # TODO: Raise limit by introducing result paging.
        status, response = api.latest(
            has_geo=True, limit=10000, include_fields=["attribution", "averagingPeriod", "sourceName"], **params
        )
        data = response["results"]

        # Mungle timestamp to be formally in ISO 8601 format (UTC).
        timestamp = data[0]["measurements"][0]["lastUpdated"]
        log.info("Timestamp of first record: {}".format(timestamp))

        # Apply data filter.
        # data = self.apply_filter(data)

        # Transform live API items to actual readings while optionally
        # applying a number of transformation and enrichment steps.
        for item in self.wrap_progress(data):
            try:
                reading = self.make_reading_from_latest(item)
                if reading is None:
                    continue

                log.debug(f"API reading:\n{json.dumps(reading, indent=2)}")

                yield reading

            except:  # noqa:E722
                log.exception(f"Could not make reading from item: {item}")

    def make_reading_from_latest(self, item):
        """
        {
          "location": "Aachen Wilhelmstraße",
          "city": "Jürgen Friesel",
          "country": "DE",
          "distance": 1934563.6160492557,
          "measurements": [
            {
              "parameter": "no2",
              "value": 53.836,
              "lastUpdated": "2017-01-06T09:00:00.000Z",
              "unit": "µg/m³",
              "sourceName": "EEA Germany",
              "averagingPeriod": {
                "value": 1,
                "unit": "hours"
              }
            }
          ],
          "coordinates": {
            "latitude": 50.773132,
            "longitude": 6.095775
          }
        }

        :param item:
        :return:
        """

        log.debug("Making reading from item: %s", item)

        # Decode item.
        entry = Munch(
            station=Munch(),
            observations=[],
        )

        # Set station metadata.
        entry.station.station_id = "{}:{}:{}".format(item["country"], item["city"], item["location"])

        # Collect position information.
        entry.station.position = Munch()
        entry.station.position["country"] = item["country"]
        entry.station.position["city"] = item["city"]
        if "coordinates" in item:
            entry.station.position["latitude"] = item["coordinates"]["latitude"]
            entry.station.position["longitude"] = item["coordinates"]["longitude"]

        # Add more detailed location information.
        self.enrich_station(entry.station)

        observations_seen = {}
        for measurement in item["measurements"]:

            timestamp = measurement["lastUpdated"]

            # Build new observation.
            if timestamp not in observations_seen:

                observation = Munch(
                    meta=Munch(),
                    data=Munch(),
                )

                # Set observation metadata.
                observation.meta.timestamp = timestamp
                observation.meta.sensor_type_name = "aq"
                observation.meta.sensor_type_id = "aq"
                observation.meta.source = measurement["sourceName"]

                entry.observations.append(observation)
                observations_seen[timestamp] = observation

            # Reuse observation.
            else:
                observation = observations_seen[timestamp]

            # Set observation data.
            value = float(item["value"])
            if value >= 0:
                parameter = measurement["parameter"]
                observation.data[parameter] = value

            # log.debug('Observation: %s', json.dumps(observation))

            # Debugging.
            # break

        return entry
