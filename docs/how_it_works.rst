How it works?
=============

`pytest-remote-response` works on top of interceptors specific for each library.

In a nutshell, interceptors wrap the library calls, thereby attaching additional mock/capture logic.

.. note::

    For some nerds, interceptors uses :class:`~pytest.MonkeyPatch` to monkey patch the original library with a wrapped one.

This approach certainly has some benefits and limitations; for instance, it's surprisingly easy to write new interceptors as it's only a wrapper method but it's only applicable when that method is called explicitly;
for countering this, `pytest-remote-response` ships with two more deep interceptors :mod:`~pytest_response.interceptors.urllib_full` and :mod:`~pytest_response.interceptors.urllib3_full`. 

.. warning::
    :mod:`~pytest_response.interceptors.urllib_full` and :mod:`~pytest_response.interceptors.urllib3_full` are more low-level but are plagued with threading issues; use them carefully!


Custom interceptor
******************

.. note::

    Any custom intercept must have at-least ``install`` and ``uninstall`` methods and should return a :class:`~pytest_response.app.BaseMockResponse`

Example
-------

.. code-block:: python

    from functools import warps

    # Import `response` instance to get access to :class:`~pytest.MonkeyPatch` and
    # :class:`~pytest_response.database.ResponseDB`
    from pytest_response import response

    # Library wrapper
    def wrapper(func):
        @wraps(func)
        def inner_func(url, *args, **kwargs):
            # Check if response is `True`, if `True` spoof the request from the database
            if response.response:
                status, data, headers = response.get(url=url)
                return MockResponse(status, data, headers)

            # Actual library call
            lib_response = func(url, *args, **kwargs)

            # Check if capture is `True`, if `True` then extract and dump the response into the database.
            if not response.capture:
                return _

            # Extract data, headers and status from `lib_response`

            response.insert(url=url, response=data, headers=dict(headers), status=_.status)
            return _
        return inner_func

    class MockResponse(BaseMockResponse):
        # A basic Mock Response for spoofing data, headers and status
        def __init__(self, status, data, headers={}):
            super().__init__(status, data, headers)
        pass


    def install():
        # A basic install method for Monkey Patching the library
        lib_call = library.call
        wrapped_lib_call = urlopen_wrapper(lib_call)
        response.mpatch.setattr("library.call", wrapped_lib_call)
        return


    def uninstall():
        # A basic uninstall method
        response.mpatch.undo()
