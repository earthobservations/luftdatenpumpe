#################
Python virtualenv
#################

About
=====
virtualenv_ is a tool to create isolated Python environments.
We recommend it for installing the software and its dependencies
independently of your Python distribution.


Install
=======

Create Python3 virtualenv::

    virtualenv --no-site-packages --python python3 .venv3

Install::

    # Activate virtualenv
    source .venv3/bin/activate

    # Install Python package
    pip install $program

.. note::

    Don't forget to activate the virtualenv again when trying to use the
    program. Alternatively, use the full path to `/path/to/.venv3/bin/$program`.

.. _virtualenv: https://virtualenv.pypa.io/
