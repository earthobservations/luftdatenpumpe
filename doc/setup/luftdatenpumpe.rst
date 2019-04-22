######################
Install Luftdatenpumpe
######################


*************
Prerequisites
*************

Install Luftdatenpumpe
======================
::

    apt install build-essential python3-dev libicu-dev

::

    pip install luftdatenpumpe

*****
Notes
*****

.. note::

    We recommend to use a Python `virtualenv <doc-virtualenv_>`_ to install and operate this
    software independently from your local system-wide Python installation.


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
