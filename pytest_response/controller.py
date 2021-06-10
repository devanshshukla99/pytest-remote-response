from urllib.parse import urljoin, urlparse


class Controller:
    def __init__(self, capture=True, response=False):
        self.capture = capture
        self.response = response
        self.url = None
        self.host = None
        self.https = False

    def build_url(self, host, url, https=False):
        self.url = url
        self.host = host
        self.https = https
        _scheme = "https://" if https else "http://"
        _url = "".join([_scheme, host])
        self.url = urljoin(_url, url)
        if self._validate_url(_url):
            return self.url
        raise MalformedUrl(f"URL '{_url}' is invalid")

    def _validate_url(self, value):
        result = urlparse(value)
        return all([result.scheme, result.netloc])

    pass


class MalformedUrl(Exception):
    """
    Exception raised when a malformed URL is encountered.
    """

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

    pass


controller = Controller()
