import io
import sys
import http
import urllib.request
from socket import SocketIO

import _socket

from pytest_response.controller import controller
from pytest_response.database import db


class Response_Socket(_socket.socket):
    def __init__(self, host, port, capture=controller.capture, *args, **kwargs):
        self.host = host
        self.port = port
        self._capture = capture
        self.input = io.BytesIO()
        self._io_refs = 0
        self._closed = False
        super().__init__()
        self.connect()

    def connect(self, *args, **kwargs):
        if self._capture:
            print("Connecting...")
            super().connect((self.host, self.port), *args, **kwargs)

    def settimeout(self, timeout):
        if self._capture:
            super().settimeout(timeout)
        pass

    def flush(self):
        if self._capture:
            super().flush()
        pass

    def makefile(
        self,
        mode="r",
        buffering=None,
        encoding=None,
        errors=None,
        newline=None,
        *args,
        **kwargs
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
            raw = SocketIO(self, rawmode)
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
            print("Sending...")
            super().sendall(data, *args, **kwargs)

    def close(self):
        """
        NotImplementedYet
        """
        if self._capture:
            super().close()
        pass


class Response_HTTPResponse(http.client.HTTPResponse):
    def __init__(
        self, sock, debuglevel=0, method=None, headers=None, capture=controller.capture
    ):
        self.sock = sock
        self._capture = capture
        self.output = io.BytesIO()
        super().__init__(sock=sock, debuglevel=debuglevel, method=method)

    def _dump_to_db(self):
        print("DUMPED?")
        url = controller.url  # self.headers.get('Location')
        db.insert(url=url, response=self.output.getvalue())
        return

    def _replace_buffer(self):
        self.output.write(self.fp.read())
        self.fp = self.output
        self.fp.seek(0)
        self._dump_to_db()

    def begin(self, *args, **kwargs):
        print("Beginning///...///")
        if not self._capture:
            self.fp = io.BytesIO()
            data, headers = db.get(url=controller.url)
            if not data:
                self.code = self.status = 404
                self.reason = "Response Not Found (pytest-response)"
                self.will_close = True
                return
            status = "200"
            self.output.write(b"HTTP/1.0 " + status.encode("ISO-8859-1") + b"\n")
            self.output.write(data)
            self.will_close = False
            self.fp = self.output
            self.fp.seek(0)
        super().begin(*args, **kwargs)
        # if self._capture:
        #     self._replace_buffer()

    def close(self, *args, **kwargs):
        if self._capture:
            self._replace_buffer()

    def read(self, *args, **kwargs):
        """
        Wrapper
        """
        if self._capture:
            return super().read(*args, **kwargs)
        return self.fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readline
        """
        if self._capture:
            return super().readline(*args, **kwargs)
        return self.fp.readline(*args, **kwargs)

    def readinto(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readinto
        """
        if self._capture:
            return super().readinto(*args, **kwargs)
        return self.fp.readinto(*args, **kwargs)

    pass


class ResponseHTTPConnection(http.client.HTTPConnection):
    response_class = Response_HTTPResponse

    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        """Send a complete request to the server."""
        controller.build_url(self.host, url)
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        """
        Override the connect() function to intercept calls to certain
        host/ports.
        """
        sys.stderr.write("connect: %s, %s\n" % (self.host, self.port))
        try:
            sys.stderr.write("INTERCEPTING call to %s:%s\n" % (self.host, self.port))
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
        controller.build_url(self.host, url, True)
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        sys.stderr.write("connect: %s, %s\n" % (self.host, self.port))
        sys.stderr.write("INTERCEPTING call to %s:%s\n" % (self.host, self.port))

        self.sock = Response_Socket(
            host=self.host,
            port=self.port,
            https=True,
            timeout=self.timeout,
            source_address=self.source_address,
        )
        self.sock.setsockopt(_socket.IPPROTO_TCP, _socket.TCP_NODELAY, 1)

        if controller.capture:
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
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


install = install_opener
uninstall = uninstall_opener
