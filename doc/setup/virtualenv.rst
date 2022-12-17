.. _python-virtualenv:

#################
Python virtualenv
#################

About
=====

`virtualenv`_ is a tool to create isolated Python environments.
We recommend it for installing the software and its dependencies
independently of your Python distribution.


Install
=======

Create Python3 virtualenv::

    python3 -m venv .venv

Install::

    # Activate virtualenv
    source .venv/bin/activate

    # Install Python package
    pip install $program

.. note::

    Don't forget to activate the virtualenv again when trying to use the
    program. Alternatively, use the full path to `/path/to/.venv/bin/$program`.

.. _virtualenv: https://virtualenv.pypa.io/
