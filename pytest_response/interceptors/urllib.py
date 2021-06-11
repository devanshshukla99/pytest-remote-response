import io
import http
import errno
import urllib.request
from ssl import SSLSocket, SSLContext
from socket import SocketIO
from urllib.parse import urljoin

import _socket

from pytest_response import response
from pytest_response.logger import log

EBADF = getattr(errno, "EBADF", 9)
EAGAIN = getattr(errno, "EAGAIN", 11)
EWOULDBLOCK = getattr(errno, "EWOULDBLOCK", 11)
_blocking_errnos = {EAGAIN, EWOULDBLOCK}


CONFIG = {"url": None, "host": None, "https": None, "headers": None}


def _build_url(host, url, headers, https=False):
    """
    Internal controller method for building urls.
    """
    global CONFIG
    _scheme = "https://" if https else "http://"
    _url = "".join([_scheme, host])
    CONFIG["url"] = urljoin(_url, url)
    CONFIG["https"] = https
    CONFIG["headers"] = headers
    return


class ResponseSocketIO(SocketIO):
    """
    Provides a method to write the value of the buffer into another var for dumping.
    Wrapper for `~socket.SocketIO`.
    """

    def __init__(self, sock, mode):
        if mode not in ("r", "w", "rw", "rb", "wb", "rwb"):
            raise ValueError("invalid mode: %r" % mode)
        self.output = io.BytesIO()  # internal buffer
        super().__init__(sock, mode)

    def readinto(self, b):
        """
        Wrapper function for `socket.SocketIO.readinto`
        """
        _ = super().readinto(b)
        self.output.write(b.tobytes())
        return _

    def __del__(self):
        if response.capture and response.remote:
            global CONFIG
            url = CONFIG.get("url")
            log.debug(f"dumped {url}")
            response.insert(url=url, response=self.output.getvalue())


class ResponseSocket(_socket.socket):
    """
    Socket implementation of Pytest-Response

    Provides `ResponseSocket.makefile` method to return a buffer built with `ResponseSocketIO`
    """

    def __init__(self, host, port, *args, **kwargs):
        self.host = host
        self.port = port
        self._io_refs = 0
        self._closed = False
        super().__init__()
        self.connect()

    def connect(self, *args, **kwargs):
        """
        Connects to host in capturing mode otherwise passes.

        Wrapper for `_socket.socket.connect`
        """
        if not response.remote:
            log.error(f"remote:{response.remote}")
            raise RemoteBlockedError

        if not response.response:
            log.debug(
                f"Connecting...to {self.host}:{self.port} response:{response.response}"
            )
            super().connect((self.host, self.port), *args, **kwargs)

    def close(self):
        pass

    def makefile(
        self,
        mode="r",
        buffering=None,
        encoding=None,
        errors=None,
        newline=None,
        *args,
        **kwargs,
    ):
        """
        Provides makefile() method which returns a Buffered IO built with `ResponseSocketIO`
        """
        # if response.capture:
        writing = "w" in mode
        reading = "r" in mode or not writing
        binary = "b" in mode
        rawmode = ""
        if reading:
            rawmode += "r"
        if writing:
            rawmode += "w"
        raw = ResponseSocketIO(self, rawmode)
        if not buffering:
            buffering = io.DEFAULT_BUFFER_SIZE
        if buffering == 0:
            if not binary:
                raise ValueError("unbuffered streams must be binary")
            return raw
        if reading and writing:
            buffer = io.BufferedRWPair(raw, raw, buffering)
        elif reading:
            buffer = io.BufferedReader(raw, buffering)
        else:
            assert writing
            buffer = io.BufferedWriter(raw, buffering)
        if binary:
            return buffer
        text = io.TextIOWrapper(buffer, encoding, errors, newline)
        text.mode = mode
        return text

    def _decref_socketios(self):
        if self._io_refs > 0:
            self._io_refs -= 1
        if self._closed:
            self.close()

    def sendall(self, data, *args, **kwargs):
        """
        Wrapper for `_socket.socket.sendall`
        """
        if type(data) is not bytes:
            data = data.encode("utf-8")
        if response.remote and not response.response:
            super().sendall(data, *args, **kwargs)


class Response_SSLSocket(SSLSocket):
    """
    SSLSocket implementation of Pytest-Response

    Provides a wrapper `recv_into` for capturing the response.
    """

    output = io.BytesIO()

    def recv_into(self, buffer, nbytes=None, flags=0):
        """
        Wrapper for `SSLSocket.recv_into`

        Provides a way to capture the response.
        """
        _ = super().recv_into(buffer, nbytes, flags)
        self.output.write(buffer.tobytes().rstrip(b"\x00").lstrip(b"\x00"))
        return _

    def __del__(self):
        if response.capture and response.remote:
            global CONFIG
            url = CONFIG.get("url")
            log.debug(f"dumped {url}")
            response.insert(url=url, response=self.output.getvalue())

    pass


class ResponseHTTPResponse(http.client.HTTPResponse):
    """
    Provides a way to capture or respond with a saved response.
    """

    def __init__(self, sock, debuglevel=0, method=None, headers=None):
        self.sock = sock
        self.output = io.BytesIO()
        super().__init__(sock=sock, debuglevel=debuglevel, method=method)

    def begin(self, *args, **kwargs):
        if not response.remote:
            log.error(f"remote:{response.remote}")
            raise RemoteBlockedError

        log.debug(
            f"begin response fetching/framing capture:{response.capture} response:{response.response}"
        )

        if response.response:
            global CONFIG
            self.fp = io.BytesIO()
            data, headers = response.get(url=CONFIG.get("url", ""))
            if not data:
                self.code = self.status = 404
                self.reason = "Response Not Found (pytest-response)"
                self.will_close = True
                log.error(f"Response not found {CONFIG.get('url', '')}")
                raise ResponseNotFound
            # self.output.write(b"HTTP/1.0 " + status.encode("ISO-8859-1") + b"\n")
            self.output.write(data)
            self.will_close = False
            self.fp = self.output
            self.fp.seek(0)

        super().begin(*args, **kwargs)

    pass


class ResponseHTTPConnection(http.client.HTTPConnection):
    """
    Wrapper for `~http.client.HTTPConnection`
    """

    response_class = ResponseHTTPResponse

    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        """Send a complete request to the server."""
        _build_url(self.host, url, headers, False)
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        """
        Override the connect() function to intercept calls.
        """
        if not response.remote:
            log.error(f"Attempt to connect. remote:{response.remote}")
            raise RemoteBlockedError
        try:
            log.debug("Intercepting call to %s:%s\n" % (self.host, self.port))
            self.sock = ResponseSocket(self.host, self.port)
        except Exception:
            raise

    pass


class ResponseHTTPHandler(urllib.request.HTTPHandler):
    """
    Override the default HTTPHandler class with one that uses the
    ResponseHTTPConnection class to open HTTP URLs.
    """

    def http_open(self, req):
        return self.do_open(ResponseHTTPConnection, req)

    pass


class ResponseHTTPSConnection(http.client.HTTPSConnection, ResponseHTTPConnection):
    """
    Override the default `~HTTPSConnection` to use `~ResponseSocket`
    """

    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        """Send a complete request to the server."""
        _build_url(self.host, url, headers, True)
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        if not response.remote:
            log.error(f"Attempting to connect. remote:{response.remote}")
            raise RemoteBlockedError

        log.info("Intercepting call to %s:%s\n" % (self.host, self.port))
        self.sock = ResponseSocket(
            host=self.host,
            port=self.port,
            https=True,
            timeout=self.timeout,
            source_address=self.source_address,
        )
        self.sock.setsockopt(_socket.IPPROTO_TCP, _socket.TCP_NODELAY, 1)

        if response.capture:
            SSLContext.sslsocket_class = Response_SSLSocket

        if not response.response:
            if self._tunnel_host:
                self._tunnel()

            if self._tunnel_host:
                server_hostname = self._tunnel_host
            else:
                server_hostname = self.host
            self.sock = self._context.wrap_socket(
                self.sock, server_hostname=server_hostname
            )

    pass


class ResponseHTTPSHandler(urllib.request.HTTPSHandler):
    """
    Override the default HTTPSHandler class with one that uses the
    ResponseHTTPSConnection class to open HTTP URLs.
    """

    def https_open(self, req):
        return self.do_open(ResponseHTTPSConnection, req)


class MockResponse:
    def __init__(self, data, headers):
        self.code = 200
        self.status = 200
        self.msg = "OK"
        self.reason = "OK"
        self.headers = headers
        self.fp = io.BytesIO(data)
        self.will_close = True

    def flush(self):
        self.fp.flush()

    def info(self):
        return {}

    def read(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.read
        """
        return self.fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readline
        """
        return self.fp.readline(*args, **kwargs)

    def readinto(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readinto
        """
        return self.fp.readinto(*args, **kwargs)

    def __exit__(self):
        """
        Method for properly closing resources.
        """
        if hasattr(self, "fp"):
            self.fp.close()

    def close(self):
        if hasattr(self, "fp"):
            self.fp.close()

    def __del__(self):
        """
        Method for properly closing resources.
        """
        if hasattr(self, "fp"):
            self.fp.close()

    pass


def install_opener():
    handlers = [ResponseHTTPHandler(), ResponseHTTPSHandler()]
    opener = urllib.request.build_opener(*handlers)
    urllib.request.install_opener(opener)
    return opener


def uninstall_opener():
    urllib.request.install_opener(None)


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to connect to internet.")


class ResponseNotFound(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(ResponseNotFound, self).__init__(
            "Response is not available; try capturing first."
        )


install = install_opener
uninstall = uninstall_opener
