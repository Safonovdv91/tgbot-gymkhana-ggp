import logging
import logging.handlers


def init_logger(name, level: int = 30):
    logger = logging.getLogger(name)
    FORMAT = "%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s"
    logger.setLevel(level)

    sh = logging.StreamHandler()    # hand
    sh.setLevel(level)
    sh.setFormatter(logging.Formatter(FORMAT))

    fh = logging.handlers.RotatingFileHandler(filename=f"logger/app_log.log")   # Использование прокаченного логгр-хэндлера
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(level)

    logger.addHandler(sh)
    logger.addHandler(fh)

    logger.debug("Logger was initialized")


if __name__ == "__main__":
    pass
