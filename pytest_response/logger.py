import logging

def _init_log(level="info"):
    log = logging.getLogger('pytest_response')
    log.setLevel(getattr(logging, level))
    handler = logging.handlers.RotatingFileHandler(".pytest_response.log", maxBytes=1024*1024 , backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log
