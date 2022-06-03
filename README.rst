======================
pytest-remote-response
======================

|versions| |license|

|build| |docs| |coverage| |status| |codestyle|


This package provides a plugin for `pytest`_ framework for capturing and mocking connection requests during the test run.

Inspired by `pook`_ and `pytest-responses`_.

Get started using the `documentation`_ and `getting-started`_.

🔌Installation
---------------

.. code-block:: console

    $ pip install pytest-remote-response
    
or

.. code-block:: console

    $ git clone https://github.com/devanshshukla99/pytest-remote-response
    $ cd pytest-remote-response
    $ pip install .

The plugin will register automatically with ``pytest`` framework and will be ready to use.

💁🏻‍♀️Supported Clients
------------------------

Currently, `pytest-remote-response` supports,

- ✔ `urllib`_
- ✔ `urllib3`_
- ✔ `requests`_
- ✔ `aiohttp`_

💨Usage
--------

🐍🧪Pytest plugin
******************

The plugin works by applying monkeypatches of interceptors for different libraries using a wrapper ``response.activate``.
The interceptors when applied can capture, prevent or mock the connection request. 

The available interceptors are listed in ``response.avaiable`` method.

Example of activating interceptor:

.. literalinclude:: ../examples/response_decorator_urllib3.py

Handling requests:

- Block remote requests:
    all requests are allowed by default; one can disable them using `--remote-block` flag.

.. code-block:: console

    $ pytest --remote-block

- Capture remote requests:
    the requests can be captured in a ``json`` file using ``--remote-capture`` arg.

.. code-block:: console

    $ pytest --remote-capture

- Mock remote requests:
    the requests can be mocked using ``--remote-response`` flag.
    
    NOTE: Due to certain limitations, it is advised to not use this plugin in an offline environment.

.. code-block:: console

    $ pytest --remote-response


🐱‍👤Standalone package
***********************

The tools implemented in this package can be easily ported to any other application, with mimial config required.

Configuration:
^^^^^^^^^^^^^^

.. code-block:: python

    from pytest_response import response

    response.setup_database({DUMP FILE})
    response.post({INTERCEPTOR})
    ...
    response.unpost()


🧪 Testing
-----------

Use ``tox`` to make sure the plugin is working:

.. code-block:: console

    $ git clone https://github.com/devanshshukla99/pytest-remote-response
    $ cd pytest-remote-response
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
    :target: https://pypi.org/project/pytest-remote-response/
    :alt: Python versions supported

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg 
    :target: https://pypi.org/project/pytest-remote-response/
    :alt: License

.. |codestyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black

.. |docs| image:: https://readthedocs.org/projects/pytest-remote-response/badge/?version=latest
    :target: https://pytest-remote-response.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
    
   
.. _pytest: https://github.com/pytest-dev/pytest
.. _urllib: https://docs.python.org/3/library/urllib.html
.. _requests: https://github.com/psf/requests
.. _aiohttp: https://github.com/aio-libs/aiohttp
.. _urllib3: https://github.com/urllib3/urllib3
.. _pytest-responses: https://github.com/getsentry/pytest-responses
.. _pook: https://github.com/h2non/pook
.. _documentation: https://pytest-remote-response.readthedocs.io/en/latest/
.. _getting-started: https://pytest-remote-response.readthedocs.io/en/latest/user_guide.html
