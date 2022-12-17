######################
Install Luftdatenpumpe
######################


*****
Setup
*****

Install prerequisites::

    apt install build-essential python3-dev libicu-dev

Install Luftdatenpumpe::

    pip install luftdatenpumpe

.. note::

    - We recommend to use a :ref:`python-virtualenv` to install and operate this
      software independently from your local system-wide Python installation.

    - In order to make the ``luftdatenpumpe`` command available system-wide, just place a
      symlink into ``/usr/local/bin``, like::

        ln -s /opt/luftdatenpumpe/.venv/bin/luftdatenpumpe /usr/local/bin/luftdatenpumpe


***************
Troubleshooting
***************

.. note::

    ``luftdatenpumpe`` depends on the PyICU package.
    Sometimes, ``pkg-config`` is not able to find the appropriate ICU installation, like::

        RuntimeError:
        Please set the ICU_VERSION environment variable to the version of
        ICU you have installed.

    So, you might try to do things like::

        $ export PKG_CONFIG_PATH="/usr/local/opt/icu4c/lib/pkgconfig"
        $ pkg-config --modversion icu-i18n
        63.1

