#########################
Luftdaten-Viewer Cron Job
#########################


*****
Setup
*****
Create "workbench" user::

    useradd --shell=/bin/bash --create-home workbench

Install cron file::

    curl --silent https://raw.githubusercontent.com/earthobservations/luftdatenpumpe/main/etc/luftdaten-viewer.cron > /etc/cron.d/luftdaten-viewer
    curl --silent https://raw.githubusercontent.com/earthobservations/luftdatenpumpe/main/tools/pflock > /usr/local/bin/pflock
    curl --silent https://raw.githubusercontent.com/earthobservations/luftdatenpumpe/main/tools/safewrite > /usr/local/bin/safewrite
    chmod +x /usr/local/bin/pflock /usr/local/bin/safewrite


*****
Notes
*****

``pflock``
==========
Please modify ``/usr/local/bin/pflock`` on CentOS systems as ``/var/lock`` does
not yield appropriate permissions by default to use the ``/tmp`` directory::

    /tmp/program-${name}.pflock

Data acquisition rate
=====================
Also, you might want to increase the data acquisition rate in ``/etc/cron.d/luftdaten-viewer``::

    # Run data import each 5 minutes
    */5     *	* * *   workbench	pflock luftdatenpumpe readings --country=BE --target=${tsdb_uri} >/dev/null 2>&1

