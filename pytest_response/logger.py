import logging


class Formatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\033[38;1m"
    cyan = "\033[36m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"
    bold_red = "\033[31;1m"
    reset = "\033[0m"
    format = "%(asctime)s - %(module)s.%(funcName)s() - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: "".join([cyan, format, reset]),
        logging.INFO: "".join([green, format, reset]),
        logging.WARNING: "".join([yellow, format, reset]),
        logging.ERROR: "".join([red, format, reset]),
        logging.CRITICAL: "".join([bold_red, format, reset]),
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
    fh.setFormatter(Formatter())
    ch.setFormatter(Formatter())
    log.addHandler(fh)
    log.addHandler(ch)
    return log


log = _init_log()
