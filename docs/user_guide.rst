.. _getting-started:

⛷️Getting Started
==================

🔌Installation
***************

PyPI
----

.. code-block:: console

    $ pip install pytest-remote-response

GitHub
------

.. code-block:: console

    $ git clone https://github.com/devanshshukla99/pytest-remote-response
    $ cd pytest-remote-response
    $ pip install .

or 

.. code-block:: console

    $ pip install -e git+git://github.com/devanshshukla99/pytest-remote-response.git#egg=pytest-remote-response


💨Usage
********

.. table:: Supported interceptors:
    :widths: 10 15

    +-------------+------------------------------------------------------+
    | **Library** | **Interceptors**                                     |
    +-------------+------------------------------------------------------+
    | `urllib`_   | :mod:`~pytest_response.interceptors.urllib`          |
    |             |                                                      |
    |             | :mod:`~pytest_response.interceptors._urllib`         |
    +-------------+------------------------------------------------------+
    | `urllib3`_  | :mod:`~pytest_response.interceptors.urllib3`         |
    |             |                                                      |
    |             | :mod:`~pytest_response.interceptors._urllib3`        |
    +-------------+------------------------------------------------------+
    | `requests`_ | :mod:`~pytest_response.interceptors.requests`        |
    +-------------+------------------------------------------------------+
    | `aiohttp`_  | :mod:`~pytest_response.interceptors.aiohttp`         |
    +-------------+------------------------------------------------------+


🐍🧪pytest plugin
------------------

Once, installed the plugin will register automatically with pytest with its configuration options available via ``pytest --help``.

.. code-block:: console

    $ pytest --help

The plugin is only applicable to function wrapped with the :func:`pytest_response.app.Response.activate` decorator.

Handling connection requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Block remote connections:**

.. code-block:: console

    $ pytest --remote-block

- **Capture remote requests:**

.. code-block:: console

    $ pytest --remote-capture

- **Mock remote requests:**

.. code-block:: console

    $ pytest --remote-response

- **Database dump:**

The database dump file can be specified using the ``remote_response_database`` ini-config option with pytest.
These config options can be set through ``pytest.ini``, ``pyproject.toml``, ``tox.ini`` or ``setup.cfg``.
Follow the `pytest_config`_ docs for more info.


Examples
^^^^^^^^

.. code-block:: python
    from pytest_response import response

    @response.activate("urllib")
    def test_urllib():
        url = "https://www.python.org"
        res = urllib.request.urlopen(url)
        assert res.status == 200
        assert res.read()

.. code-block:: console

    $ pytest --remote-block
    $ pytest --remote-capture
    $ pytest --remote-response


🐱‍👤Standalone Package
-----------------------

The tools implemented in this package can be easily ported to any other application, with mimial config required:

Basic usage:
^^^^^^^^^^^^

.. code-block:: python

    from pytest_response import response

    # Setup the database file
    response.setup_database("database.json")
    
    # Block outgoing connections
    response.configure(remote=False, capture=False, response=False)

    # Capture outgoing connections
    response.configure(remote=True, capture=True, response=False)

    # Mock outgoing connections
    response.configure(remote=True, capture=False, response=True)
    
    # Applies the interceptor
    response.post({INTERCEPTOR})

    ...
    ...

    # Cleanup
    response.unpost()

.. note:: Here {INTERCEPTORS} can be `str` or `list`



Examples:
^^^^^^^^^

Block connections in `urllib`_
""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/block_urllib.py

Capture connections in `requests`_
""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/capture_requests.py

Mock connections in `urllib3`_
""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/response_urllib3.py

Mock connections in `urllib3`_ using decorator
""""""""""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/response_decorator_urllib3.py

Using :class:`~pytest_response.database.ResponseDB`
""""""""""""""""""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/insert_get_database.py


.. _urllib: https://docs.python.org/3/library/urllib.html
.. _requests: https://github.com/psf/requests
.. _aiohttp: https://github.com/aio-libs/aiohttp
.. _urllib3: https://github.com/urllib3/urllib3
.. _pytest_config: https://docs.pytest.org/en/6.2.x/customize.html#configuration-file-formats