======================
pytest-remote-response
======================

|versions|

|license| |build| |coverage| |status| |codestyle|


This package provides a plugin for ``pytest`` framework for capturing and mocking connection requests during the test run.

Installation
------------

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-response
    $ cd pytest-response
    $ pip install .

The plugin will register automatically with ``pytest`` framework and will be ready to use.

Usage
-----

Pytest plugin
*************

The plugin works by using interceptors of different libraries which can be checked by ``response.available()`` method; these interceptors have to be applied for each pytest run using ``--remote={INTERCEPTOR}``.

.. code-block:: bash

    $ pytest --remote="urllib_quick|requests_quick|aiohttp_quick"

Handling requests:

- Prevent remote requests:
    all requests are allowed by default; one can disable them using `--remote-blocked` flag.

.. code-block:: bash

    $ pytest --remote={INTERCEPTORS} --remote-blocked

- Capture remote requests:
    the requests can be captured in a ``json`` file using ``--remote-capture`` arg.

.. code-block:: bash

    $ pytest --remote={INTERCEPTORS} --remote-capture

- Mock remote requests:
    the requests can be mocked using ``--remote-response`` flag.
    
    NOTE: Due to certain limitations, it is advised to not use this plugin in an offline environment.

.. code-block:: bash

    $ pytest --remote={INTERCEPTORS} --remote-response


Standlone package
*****************

The tools implemented in this package can be easily ported to any other application, with mimial config required.

Configuration:

.. code-block:: python

    from pytest_response import response

    response.setup_database({DUMP FILE})
    response.post({INTERCEPTOR})
    ...
    response.unpost()


Testing
-------

Use ``tox`` to make sure the plugin is working:

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-response
    $ cd pytest-response
    $ tox -e py38

See `tox <https://github.com/tox-dev/tox>`_ for more info.


Licence
-------
This plugin is licenced under a 3-clause BSD style licence - see the ``LICENCE`` file.

.. |build| image:: https://github.com/devanshshukla99/pytest-remote-response/actions/workflows/main.yml/badge.svg

.. |coverage| image:: https://codecov.io/gh/devanshshukla99/pytest-remote-response/branch/main/graph/badge.svg?token=NQMZKNZOB2
    :target: https://codecov.io/gh/devanshshukla99/pytest-remote-response
    :alt: Code coverage

.. |status| image:: https://img.shields.io/pypi/status/pytest-remote-response.svg
    :target: https://pypi.org/project/pytest-remote-response/
    :alt: Package stability

.. |versions| image:: https://img.shields.io/pypi/pyversions/pytest-remote-response.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/coverage/
    :alt: Python versions supported

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg 
    :target: https://pypi.org/project/pytest-remote-response/
    :alt: License

.. |codestyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
