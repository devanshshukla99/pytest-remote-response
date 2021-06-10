import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\033[38;21m"
    yellow = "\033[33;21m"
    red = "\033[31;21m"
    bold_red = "\033[31;1m"
    reset = "\033[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def _init_log(level="info"):

    log = logging.getLogger("pytest_response")
    log.setLevel(getattr(logging, level.upper()))
    fh = logging.FileHandler(".pytest_response.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(CustomFormatter())
    ch.setFormatter(CustomFormatter())
    log.addHandler(fh)
    log.addHandler(ch)
    return log


log = _init_log()
