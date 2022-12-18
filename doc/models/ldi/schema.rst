:orphan:

LDI data schema
===============
The data schema offered by `https://api.luftdaten.info/static/v1/data.json` looks like this.

Example for DHT22 sensor::

    {
        "id": 59625316,
        "location": {
            "id": 312,
            "latitude": "48.647",
            "longitude": "9.445"
        },
        "sampling_rate": null,
        "sensor": {
            "id": 660,
            "pin": "7",
            "sensor_type": {
                "id": 9,
                "manufacturer": "various",
                "name": "DHT22"
            }
        },
        "sensordatavalues": [
            {
                "id": 169745466,
                "value": "44.30",
                "value_type": "humidity"
            },
            {
                "id": 169745465,
                "value": "15.80",
                "value_type": "temperature"
            }
        ],
        "timestamp": "2017-03-30T19:24:02"
    }

Example for SDS011 sensor::

    {
        "id": 59625314,
        "location": {
            "id": 220,
            "latitude": "48.741",
            "longitude": "9.317"
        },
        "sampling_rate": null,
        "sensor": {
            "id": 467,
            "pin": "1",
            "sensor_type": {
                "id": 14,
                "manufacturer": "Nova Fitness",
                "name": "SDS011"
            }
        },
        "sensordatavalues": [
            {
                "id": 169745461,
                "value": "6.73",
                "value_type": "P1"
            },
            {
                "id": 169745462,
                "value": "4.48",
                "value_type": "P2"
            }
        ],
        "timestamp": "2017-03-30T19:24:02"
    }

