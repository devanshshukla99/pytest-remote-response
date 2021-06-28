User Guide
============

Installation
************

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


Usage
*****

Available interceptors,


+-------------+------------------+
| **Library** | **Interceptors** |
+-------------+------------------+
| `urllib`_   | `urllib`         |
|             |                  |
|             | `urllib_full`    |
+-------------+------------------+
| `urllib3`_  | `urllib3`        |
|             |                  |
|             | `urllib3_full`   |
+-------------+------------------+
| `requests`_ | `requests`       |
+-------------+------------------+
| `aiohttp`_  | `aiohttp`        |
+-------------+------------------+


pytest plugin
-------------

Once, installed the plugin will register automatically with pytest with its configuration options available via ``pytest --help``.

.. code-block:: console

    $ pytest --remote={{INTERCEPTOR}}

``--remote`` supports regex expressions for applying multiple interceptors.


Handling connection requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Block remote connections:**

.. code-block:: console

    $ pytest --remote={INTERCEPTOR} --remote-blocked


- **Capture remote requests:**

.. code-block:: console

    $ pytest --remote={INTERCEPTOR} --remote-capture

- **Mock remote requests:**

.. code-block:: console

    $ pytest --remote={INTERCEPTOR} --remote-response


Examples
^^^^^^^^

.. code-block:: console

    $ pytest --remote="urllib|urllib3|requests"
    $ pytest --remote="urllib|urllib3|requests" --remote-blocked
    $ pytest --remote="urllib|urllib3|requests" --remote-capture
    $ pytest --remote="urllib|urllib3|requests" --remote-response


Standalone Package
------------------

The tools implemented in this package can be easily ported to any other application, with mimial config required:

.. code-block:: python

    from pytest_response import response

    # Setup the database file
    response.setup_database("basedata.json")
    
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



Examples
^^^^^^^^

Block connections in `urllib`_
""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/block_urllib.py

Capture connections in `requests`_
""""""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/capture_requests.py

Mock connections in `urllib3`_
""""""""""""""""""""""""""""""""

.. literalinclude:: ../examples/response_urllib3.py


.. _urllib: https://docs.python.org/3/library/urllib.html
.. _requests: https://github.com/psf/requests
.. _aiohttp: https://github.com/aio-libs/aiohttp
.. _urllib3: https://github.com/urllib3/urllib3
