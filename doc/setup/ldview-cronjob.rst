#########################
Luftdaten-Viewer Cron Job
#########################

Create "workbench" user::

    useradd --shell=/bin/bash --create-home workbench

Install cron file::

    cp etc/luftdaten-viewer.cron /etc/cron.d/luftdaten-viewer
