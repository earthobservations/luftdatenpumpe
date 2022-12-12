################
PostgreSQL notes
################

Authentication
==============
To make the authentication work, please add these lines to your ``pg_hba.conf``::

    host    weatherbase       grafana         127.0.0.1/32      trust
    host    weatherbase       grafana         ::1/128           trust
    local   weatherbase       grafana                           trust

    host    weatherbase       luftdatenpumpe  127.0.0.1/32      trust
    host    weatherbase       luftdatenpumpe  ::1/128           trust
    local   weatherbase       luftdatenpumpe                    trust

