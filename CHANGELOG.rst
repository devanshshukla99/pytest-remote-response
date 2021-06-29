0.2.2.dev21+g57963d9 (2021-06-27)
=================================

Backwards Incompatible Changes
------------------------------

- Renamed package from `pytest-response` to `pytest-remote-response`. (`#9 <https://github.com/devanshshukla99/pytest-remote-response/pull/9>`__)
- Renamed interceptors to a more clear norm. (`#15 <https://github.com/devanshshukla99/pytest-remote-response/pull/15>`__)


Features
--------

- Instead of moving through entire pipleline, now the interceptors will return a `pytest_response.app.BaseMockResponse` directly. (`#1 <https://github.com/devanshshukla99/pytest-remote-response/pull/1>`__)
- Added a `pytest_response.app.Response.configure` method for setting values of remote, capture and response. (`#3 <https://github.com/devanshshukla99/pytest-remote-response/pull/3>`__)
- Added interceptor for `aiohttp` library. (`#4 <https://github.com/devanshshukla99/pytest-remote-response/pull/4>`__)


Trivial/Internal Changes
------------------------

- Similified `pytest_response.logger.log` use. (`#3 <https://github.com/devanshshukla99/pytest-remote-response/pull/3>`__)
- Now the `pytest_response.database.ResponseDB.get` method will automatically rstrip "/", useful in comparing URLs. (`#4 <https://github.com/devanshshukla99/pytest-remote-response/pull/4>`__)
- Now `status` code will also be dumped/responded with along with `data` and `headers`. (`#6 <https://github.com/devanshshukla99/pytest-remote-response/pull/6>`__)
- Simplified GitHub actions as a two step process. (`#8 <https://github.com/devanshshukla99/pytest-remote-response/pull/8>`__)
