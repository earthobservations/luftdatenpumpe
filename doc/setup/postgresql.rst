.. _postgresql-authentication:

#####################################
Notes about PostgreSQL authentication
#####################################


************
Introduction
************

When configuring and operating Luftdatenpumpe on a production machine, you
may want to look into configuring `Trust Authentication`_ for PostgreSQL.

    When ``trust`` authentication is specified, PostgreSQL assumes that anyone
    who can connect to the server is authorized to access the database with
    whatever database user name they specify (even superuser names).

    Of course, restrictions made in the ``database`` and ``user`` columns still
    apply. This method should only be used when there is adequate
    operating-system-level protection on connections to the server.

    ``trust`` authentication is appropriate and very convenient for local
    connections on a single-user workstation.


*************
Configuration
*************

To configure ``trust`` authentication for the users ``luftdatenpumpe`` and
``grafana``, please add those lines to your ``pg_hba.conf``::

    host    weatherbase       luftdatenpumpe  127.0.0.1/32      trust
    host    weatherbase       luftdatenpumpe  ::1/128           trust
    local   weatherbase       luftdatenpumpe                    trust

    host    weatherbase       grafana         127.0.0.1/32      trust
    host    weatherbase       grafana         ::1/128           trust
    local   weatherbase       grafana                           trust


.. _Trust Authentication: https://www.postgresql.org/docs/current/auth-trust.html
