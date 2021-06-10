import io
import sys
import http
import urllib.request
from socket import SocketIO
from ssl import SSLContext, SSLSocket

import _socket

from pytest_response.app import control
from pytest_response.logger import log
import errno

EBADF = getattr(errno, "EBADF", 9)
EAGAIN = getattr(errno, "EAGAIN", 11)
EWOULDBLOCK = getattr(errno, "EWOULDBLOCK", 11)
_blocking_errnos = {EAGAIN, EWOULDBLOCK}


class ResponseSocketIO(SocketIO):
    """Raw I/O implementation for stream sockets.

    This class supports the makefile() method on sockets.  It provides
    the raw I/O interface on top of a socket object.
    """

    def __init__(self, sock, mode):
        if mode not in ("r", "w", "rw", "rb", "wb", "rwb"):
            raise ValueError("invalid mode: %r" % mode)
        self.output = io.BytesIO()  # internal buffer
        super().__init__(sock, mode)

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.

        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
                _ = self._sock.recv_into(b)
                self.output.write(b.tobytes())
                return _

            except _socket.timeout:
                self._timeout_occurred = True
                raise
            except OSError as e:
                if e.args[0] in _blocking_errnos:
                    return None
                raise

    def __del__(self):
        if control.capture:
            log.debug(f"Dumped {control.url}")
            url = control.url
            control.insert(url=url, response=self.output.getvalue())


class Response_Socket(_socket.socket):
    def __init__(self, host, port, *args, **kwargs):
        self.host = host
        self.port = port
        self._capture = control.capture
        self.input = io.BytesIO()
        self._io_refs = 0
        self._closed = False
        super().__init__()
        self.connect()

    def connect(self, *args, **kwargs):
        if self._capture:
            log.debug(f"Connecting...to {self.host}:{self.port}")
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
        1. build response
        2. build a stream/input file
        3. build a (request, response) tuple from the input file
        """
        """
        Read the response from the data base and construct a Response
        """
        if self._capture:
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
        if type(data) is not bytes:
            data = data.encode("utf-8")
        self.input.write(data)

        if self._capture:
            super().sendall(data, *args, **kwargs)


class Response_SSLSocket(SSLSocket):
    output = io.BytesIO()

    def recv_into(self, buffer, nbytes=None, flags=0):
        _ = super().recv_into(buffer, nbytes, flags)
        self.output.write(buffer.tobytes().rstrip(b"\x00").lstrip(b"\x00"))
        return _

    def __del__(self):
        if control.capture:
            log.debug(f"Dumped {control.url}")
            url = control.url
            control.insert(url=url, response=self.output.getvalue())

    pass


class Response_HTTPResponse(http.client.HTTPResponse):
    def __init__(self, sock, debuglevel=0, method=None, headers=None):

        self.sock = sock
        self._capture = control.capture
        self.output = io.BytesIO()
        super().__init__(sock=sock, debuglevel=debuglevel, method=method)

    def begin(self, *args, **kwargs):
        log.debug(f"begin response fetching/framing capture:{self._capture}")
        if not self._capture:
            self.fp = io.BytesIO()
            data, headers = control.get(url=control.url)
            if not data:
                self.code = self.status = 404
                self.reason = "Response Not Found (pytest-response)"
                self.will_close = True
                log.error(f"Response not found {control.url}")
                return
            # self.output.write(b"HTTP/1.0 " + status.encode("ISO-8859-1") + b"\n")
            self.output.write(data)
            self.will_close = False
            self.fp = self.output
            self.fp.seek(0)

        super().begin(*args, **kwargs)

    pass


class ResponseHTTPConnection(http.client.HTTPConnection):
    response_class = Response_HTTPResponse

    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        """Send a complete request to the server."""
        control.headers = headers
        control.build_url(self.host, url)
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        """
        Override the connect() function to intercept calls to certain
        host/ports.
        """
        try:
            log.debug("Intercepting call to %s:%s\n" % (self.host, self.port))
            self.sock = Response_Socket(self.host, self.port)
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
    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        """Send a complete request to the server."""
        control.headers = headers
        control.build_url(self.host, url, True)
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        log.info("Intercepting call to %s:%s\n" % (self.host, self.port))

        self.sock = Response_Socket(
            host=self.host,
            port=self.port,
            https=True,
            timeout=self.timeout,
            source_address=self.source_address,
        )
        self.sock.setsockopt(_socket.IPPROTO_TCP, _socket.TCP_NODELAY, 1)

        if control.capture:
            if self._tunnel_host:
                self._tunnel()

            if self._tunnel_host:
                server_hostname = self._tunnel_host
            else:
                server_hostname = self.host
            SSLContext.sslsocket_class = Response_SSLSocket
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
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


install = install_opener
uninstall = uninstall_opener
