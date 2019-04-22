##############
InfluxDB notes
##############


*************************
High-performance InfluxDB
*************************
For high performance ingestion into InfluxDB, its UDP data sink is your friend.


Usage
=====
::

    # Acquire data from live API and store into InfluxDB, with UDP
    luftdatenpumpe readings --target=udp+influxdb://localhost:4445/luftdaten_info --progress


Configuration
=============
Configure UDP data sink with InfluxDB in ``influxdb.conf``::

    # High-traffic data feed for ingesting data from luftdaten.info
    # https://docs.influxdata.com/influxdb/v1.7/supported_protocols/udp/
    [[udp]]

      # UDP FTW
      enabled = true

      # UDP port we are listening to
      bind-address = ":4445"

      # Name of the database that will be written to
      database = "luftdaten_info"

      # Will flush after buffering this many points
      batch-size = 5000

      # Number of batches that may be pending in memory
      batch-pending = 100

      # Will flush each N seconds if batch-size is not reached
      batch-timeout = "15s"

      # UDP read buffer size: 8 MB (8*1024*1024)
      #read-buffer = 8388608
      read-buffer = 0
