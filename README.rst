=======================
pytest-intercept-remote
=======================

|versions|

|license| |build| |coverage| |status|


This package provides a plugin for ``pytest`` framework for intercepting outgoing connection requests during test runs.

Installation
------------

The ``pytest-intercept-remote`` plugin can be installed by using:

.. code-block:: bash
    
    $ pip install pytest-intercept-remote

or by:

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-intercept-remote
    $ cd pytest-intercept-remote
    $ pip install .

The plugin will register automatically with ``pytest`` framework and will be ready to use.

Configuration
-------------

The default dump file is ``.intercepted`` which can be overridden by:

- either specifing ``intercept_dump_file`` in the ini file
- or by adding ``-o intercept_dump_file=[dump file]`` option

.. code-block:: bash

    $ pytest --intercept-remote -o intercept_dump_file=urls.json

Usage
-----

Intercepting requests
*********************

The urls can be intercepted using ``--intercept-remote`` option;

.. code-block:: bash

    $ pytest --intercept-remote


The tests trying to connect to internet will ``xfail``.


Remote status
*************

Once the requests are intercepted, they can be pinged for their status by using ``--remote-status=[show/only/no]`` option.

- ``--remote-status=show`` will append the ping functions to pytest run;

- ``--remote-status=only`` will only ping the requests and deselect all other tests;

.. code-block:: bash

    $ pytest --remote-status=show
    $ pytest --remote-status=only

Testing
-------

Use ``tox`` to make sure the plugin is working:

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-intercept-remote
    $ cd pytest-intercept-remote
    $ tox -e py38

See `tox <https://github.com/tox-dev/tox>`_ for more info.


Licence
-------
This plugin is licenced under a 3-clause BSD style licence - see the ``LICENCE`` file.

.. |build| image:: https://github.com/devanshshukla99/pytest-intercept-remote/actions/workflows/main.yml/badge.svg

.. |coverage| image:: https://codecov.io/gh/devanshshukla99/pytest-intercept-remote/branch/main/graph/badge.svg?token=81U29FC82V
    :target: https://codecov.io/gh/devanshshukla99/pytest-intercept-remote
    :alt: Code coverage

.. |status| image:: https://img.shields.io/pypi/status/pytest-intercept-remote.svg
    :target: https://pypi.org/project/pytest-intercept-remote/
    :alt: Package stability

.. |versions| image:: https://img.shields.io/pypi/pyversions/pytest-intercept-remote.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/coverage/
    :alt: Python versions supported

.. |license| image:: https://img.shields.io/pypi/l/pytest-intercept-remote.svg
    :target: https://pypi.org/project/pytest-intercept-remote/
    :alt: License
