# -*- coding: utf-8 -*-
# (c) 2019 Andreas Motl <andreas@hiveeyes.org>
# (c) 2019 Richard Pobering <richard@hiveeyes.org>
# (c) 2019 Matthias Mehldau <wetter@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import logging
from operator import itemgetter
from urllib.parse import urljoin

from munch import munchify
from tablib import Dataset

from luftdatenpumpe.source.common import AbstractLuftdatenPumpe

log = logging.getLogger(__name__)


class EEAAirQualityPumpe(AbstractLuftdatenPumpe):
    """
    Ingest air quality measurements from the
    European Environment Agency (EEA).

    - http://discomap.eea.europa.eu/map/fme/AirQualityExport.htm
    - http://ftp.eea.europa.eu/www/aqereporting-3/AQeReporting_products_2018_v1.pdf
    - http://dd.eionet.europa.eu/vocabulary/aq/pollutant

    - http://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm (discontinued)
    """

    # Sensor network identifier.
    network = "eea"

    # Download service REST API URI
    uri = "https://ereporting.blob.core.windows.net/downloadservice/"

    timeout = 60

    def get_index(self):
        return self.send_request()

    def send_request(self, endpoint=None, params=None):
        url = urljoin(self.uri, endpoint)
        log.info(f"Requesting EEA at {url}")
        params = params or {}

        response = self.session.get(url, params=params, timeout=self.timeout)
        if response.status_code != 200:
            try:
                reason = response.json()
            except:  # noqa:E722
                reason = "unknown"
            message = f"Request failed: {reason}"
            log.error(message)
            response.raise_for_status()

        return response.text

    def get_stations(self):
        """
        https://ereporting.blob.core.windows.net/downloadservice/metadata.csv

        Example ingress record::

            {
              "Countrycode": "CZ",
              "Namespace": "CZ.CHMI-Prague-Komorany.AQ",
              "AirQualityNetwork": "NET-CZ001A",
              "AirQualityStation": "STA.CZ_TOPO",
              "AirQualityStationNatCode": "TOPO",
              "AirQualityStationEoICode": "CZ0TOPO",
              "AirQualityStationArea": "suburban",
              "SamplingPoint": "SPO.CZ_TOPOP_BaP_40079",
              "SamplingProcess": "SPP.CZ_TOPOP_40079",
              "Sample": "SAM.CZ_TOPOP_BaP_40079",
              "BuildingDistance": "-999",
              "EquivalenceDemonstrated": "no",
              "InletHeight": "2",
              "KerbDistance": "-999",
              "MeasurementEquipment": "",
              "MeasurementType": "active",
              "MeasurementMethod": "",
              "AirPollutantCode": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5015",
              "AirPollutant": "Ni in PM10",
              "AirQualityStationType": "background",
              "Projection": "EPSG:4979",
              "Longitude": "18.15927505493164",
              "Latitude": "49.825294494628906",
              "Altitude": "242"
            }
        """

        payload = self.send_request("metadata.csv")

        # Read CSV file into tablib's Dataset and cast to dictionary representation.
        try:
            data = Dataset().load(payload, format="csv", delimiter=",")
        except:  # noqa:E722
            log.exception("Error reading or decoding station CSV")
            return

        # Apply data filter.
        data = self.apply_filter(data)

        df_grouped = data.df.groupby(["Countrycode", "AirQualityNetwork", "AirQualityStationEoICode"], as_index=False)

        stations = []
        for name, group in self.wrap_progress(df_grouped):
            first_sensor = group.head(1)
            data = first_sensor.to_dict(orient="records")[0]
            log.debug("Ingress data: %s", data)

            station_eoi_code = data.pop("AirQualityStationEoICode")
            station_info = munchify(
                {
                    "station_id": station_eoi_code,
                    "station_namespace": data.pop("Namespace"),
                    "station_network_code": data.pop("AirQualityNetwork"),
                    "station_code": data.pop("AirQualityStation"),
                    "station_nat_code": data.pop("AirQualityStationNatCode"),
                    "station_eoi_code": station_eoi_code,
                    "station_type": data.pop("AirQualityStationType"),
                    "station_area": data.pop("AirQualityStationArea"),
                    "position": {
                        "country": data.pop("Countrycode"),
                        "latitude": float(data.pop("Latitude")),
                        "longitude": float(data.pop("Longitude")),
                        "altitude": float(data.pop("Altitude")),
                        "projection": data.pop("Projection"),
                        "building_distance": float(data.pop("BuildingDistance")),
                        "kerb_distance": float(data.pop("KerbDistance")),
                    },
                }
            )
            # print(data)

            # Transfer all other stuff.
            # for key, value in data.items():
            #    station_info[key] = value

            # print('station_info:', station_info)
            # continue

            self.enrich_station(station_info)

            # FIXME: Add sensors.
            sensors = []
            for measurement in group.to_dict(orient="records"):
                # print('measurement:', measurement)
                # data = measurement.to_dict(orient='records')[0]
                # log.info('Sensor data: %s', json.dumps(measurement, indent=2))
                sensor_info = munchify(
                    {
                        "sensor_type": measurement.pop("AirPollutant"),
                        "sensor_type_uri": measurement.pop("AirPollutantCode"),
                        "sensor_measurement_type": measurement.pop("MeasurementType"),
                        "sensor_measurement_method": measurement.pop("MeasurementMethod"),
                        "sensor_measurement_equipment": measurement.pop("MeasurementEquipment"),
                        "sensor_inlet_height": float(measurement.pop("InletHeight")),
                        "sensor_equivalence_demonstrated": measurement.pop("EquivalenceDemonstrated"),
                        "sensor_sampling_process": measurement.pop("SamplingProcess"),
                        "sensor_sampling_id": measurement.pop("Sample"),
                        "sensor_sampling_point": measurement.pop("SamplingPoint"),
                    }
                )
                sensors.append(sensor_info)

            station_info.sensors = sensors

            stations.append(station_info)

        # List of stations sorted by station identifier.
        stations = sorted(stations, key=itemgetter("station_id"))

        return stations

    def filter_rule(self, data):
        df_filtered = data.df
        if self.filter and "country" in self.filter:
            df_filtered = df_filtered[df_filtered["Countrycode"].isin(self.filter.country)]

        data.df = df_filtered
        return data
