import sys
import http
import urllib
from io import BytesIO
from urllib.parse import urljoin

from pytest_response.database import db

socket_req = []
socket_res = []


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


class ResponseApp:
    def __init__(self):
        self.requests = {}
        self.responses = {}


class ResponseHTTPHandler(urllib.request.HTTPHandler):
    """
    Override the default HTTPHandler class with one that uses the
    ResponseHTTPConnection class to open HTTP URLs.
    """

    def http_open(self, req):
        return self.do_open(ResponseHTTPConnection, req)

    pass


class ResponseHTTPConnection(http.client.HTTPConnection):
    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        """Send a complete request to the server."""
        self._url = url
        self._send_request(method, url, body, headers, encode_chunked)

    def connect(self):
        """
        Override the connect() function to intercept calls to certain
        host/ports.
        """
        sys.stderr.write(
            "connect: %s, %s\n"
            % (
                self.host,
                self.port,
            )
        )
        try:
            sys.stderr.write("INTERCEPTING call to %s:%s\n" % (self.host, self.port))
            self.sock = Response_FakeSocket(self.host, self.port, self._url)
        except Exception:
            raise

    pass


class Response_HTTPResponse:
    def __init__(self, data, headers):
        self.code = 200
        self.status = 200
        self.msg = "OK"
        self.reason = "OK"
        self.headers = headers
        self.data = data
        self.fp = BytesIO(data)

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


class ResponseHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(ResponseHTTPSConnection, req)


class ResponseHTTPSConnection(http.client.HTTPSConnection, ResponseHTTPConnection):
    def connect(self):
        """
        Override the connect() function to intercept calls to certain
        host/ports.

        If no app at host/port has been registered for interception then
        a normal HTTPSConnection is made.
        """
        sys.stderr.write(
            "connect: %s, %s\n"
            % (
                self.host,
                self.port,
            )
        )

        sys.stderr.write(
            "INTERCEPTING call to %s:%s\n"
            % (
                self.host,
                self.port,
            )
        )
        self.sock = Response_FakeSocket(self.host, self.port, self._url, https=True)

        # super().connect()
        # import ssl
        # if hasattr(self, '_context'):
        #     self._context.check_hostname = self.assert_hostname
        #     self._check_hostname = self.assert_hostname     # Py3.6
        #     if hasattr(ssl, 'VerifyMode'):
        #         # Support for Python3.6 and higher
        #         if isinstance(self.cert_reqs, ssl.VerifyMode):
        #             self._context.verify_mode = self.cert_reqs
        #         else:
        #             self._context.verify_mode = ssl.VerifyMode[
        #                 self.cert_reqs]
        #     elif isinstance(self.cert_reqs, six.string_types):
        #         # Support for Python3.5 and below
        #         self._context.verify_mode = getattr(ssl,
        #                 self.cert_reqs,
        #                 self._context.verify_mode)
        #     else:
        #         self._context.verify_mode = self.cert_reqs

        # if not hasattr(self, 'key_file'):
        #     self.key_file = None
        # if not hasattr(self, 'cert_file'):
        #     self.cert_file = None
        # if not hasattr(self, '_context'):
        #     try:
        #         self._context = ssl.create_default_context()
        #     except AttributeError:
        #         self._context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        #         self._context.options |= ssl.OP_NO_SSLv2
        #         if not hasattr(self, 'check_hostname'):
        #             self._check_hostname = (
        #                 self._context.verify_mode != ssl.CERT_NONE
        #             )
        #         else:
        #             self._check_hostname = self.check_hostname

    pass


class Response_FakeSocket:
    def __init__(self, host, port, url, https=False):
        self.host = host
        self.port = port
        self._url = url
        self._https = https
        self.input = BytesIO()
        self.output = BytesIO()
        self.headers = []
        self.requests = []
        self.responses = []

    def settimeout(self, timeout):
        pass

    def flush(self):
        pass

    def _build_url(self):
        _scheme = "https://" if self._https else "http://"
        _url = "".join([_scheme, self.host])
        return urljoin(_url, self._url)

    def makefile(self, *args, **kwargs):
        """
        1. build response
        2. build a stream/input file
        3. build a (request, response) tuple from the input file
        """
        """
        Read the response from the data base and construct a Response
        """
        full_url = self._build_url()
        data, headers = db.get(url=full_url)
        print(full_url)
        status = "404"
        if data:
            status = "200"
        self.output.write(b"HTTP/1.0 " + status.encode("ISO-8859-1") + b"\n")
        self.output.write(data)
        return Response_HTTPResponse(data=self.output.getvalue(), headers=headers)

    def sendall(self, data, *args, **kwargs):
        if type(data) is not bytes:
            data = data.encode("utf-8")
        self.input.write(data)

    def close(self):
        """
        NotImplementedYet
        """
        pass


def install_opener():
    handlers = [ResponseHTTPHandler(), ResponseHTTPSHandler()]
    opener = urllib.request.build_opener(*handlers)
    urllib.request.install_opener(opener)
    return opener


def uninstall_opener():
    urllib.request.install_opener(None)


install = install_opener
uninstall = uninstall_opener
