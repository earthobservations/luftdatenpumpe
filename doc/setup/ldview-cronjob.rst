#########################
Luftdaten-Viewer Cron Job
#########################

Create "workbench" user::

    useradd --shell=/bin/bash --create-home workbench

Install cron file::

    curl --silent https://raw.githubusercontent.com/hiveeyes/luftdatenpumpe/master/etc/luftdaten-viewer.cron > /etc/cron.d/luftdaten-viewer
    curl --silent https://raw.githubusercontent.com/hiveeyes/luftdatenpumpe/master/tools/pflock > /usr/local/bin/pflock
    curl --silent https://raw.githubusercontent.com/hiveeyes/luftdatenpumpe/master/tools/safewrite > /usr/local/bin/safewrite
    chmod +x /usr/local/bin/pflock /usr/local/bin/safewrite
