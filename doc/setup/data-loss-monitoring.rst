#####################################
Luftdaten-Viewer data loss monitoring
#####################################


*******
Install
*******
Install "monitoring-check-grafana".

Monitor a Grafana datasource against data becoming stale
to detect data loss or other dropout conditions.

-- https://github.com/daq-tools/monitoring-check-grafana


*********
Configure
*********

Introduction
============
Use this Icinga configuration object to monitor your data source. You will
need to find out about your Grafana data source index. Here, it is "10", see
``https://daq.example.org/grafana/api/datasources/proxy/10/query``.

It has probably on the output of the command when creating the respective data source in Grafana::

    # Create data source object for "luftdaten_info @ InfluxDB".
    luftdatenpumpe grafana --kind=datasource --name=luftdaten_info \
        | http --session=grafana POST $GRAFANA_URL/api/datasources


Icinga configuration object
===========================
::

    // Monitor "Luftdaten-Viewer" data feed for data loss
    object Service "Luftdaten-Viewer data freshness" {
      import "baseline-service"

      check_command         = "check-grafana-datasource-stale"

      host_name             = "slartibartfast.example.org"
      vars.sla              = "24x7"

      vars.grafana_uri      = "https://daq.example.org/grafana/api/datasources/proxy/10/query"
      vars.grafana_database = "luftdaten_info"
      vars.grafana_table    = "ldi_readings"
      vars.grafana_warning  = "20m"
      vars.grafana_critical = "1d"

      vars.notification.mail.groups = [ ]
      vars.notification.mail.users  = [ "john-doe", "max-mustermann" ]

    }
