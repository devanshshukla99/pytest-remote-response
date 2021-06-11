===============
pytest-response
===============

|license| |build| |codestyle|


This package provides a plugin for ``pytest`` framework for capturing and mocking connection requests during the test run.

Installation
------------

::
    The ``pytest-response`` plugin can be installed by using:

    .. code-block:: bash
        
        $ pip install pytest-response

or by:

.. code-block:: bash

    $ git clone https://github.com/devanshshukla99/pytest-response
    $ cd pytest-response
    $ pip install .

The plugin will register automatically with ``pytest`` framework and will be ready to use.


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

.. |build| image:: https://github.com/devanshshukla99/pytest-response/actions/workflows/main.yml/badge.svg

.. |coverage| image:: https://codecov.io/gh/devanshshukla99/pytest-response/branch/main/graph/badge.svg?token=81U29FC82V
    :target: https://codecov.io/gh/devanshshukla99/pytest-response
    :alt: Code coverage

.. |status| image:: https://img.shields.io/pypi/status/pytest-response.svg
    :target: https://pypi.org/project/pytest-response/
    :alt: Package stability

.. |versions| image:: https://img.shields.io/pypi/pyversions/pytest-response.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/coverage/
    :alt: Python versions supported

.. |license| image:: https://img.shields.io/pypi/l/pytest-response.svg
    :target: https://pypi.org/project/pytest-response/
    :alt: License

.. |codestyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black