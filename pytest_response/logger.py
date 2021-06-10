import logging


def _init_log(level="info"):
    log = logging.getLogger('pytest_response')
    log.setLevel(getattr(logging, level.upper()))
    fh = logging.FileHandler(".pytest_response.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    log.addHandler(fh)
    log.addHandler(ch)
    return log


log = _init_log()
