import logging
import logging.handlers


def init_logger(name, sh_level: int = 30, fh_level: int = 30):
    logger = logging.getLogger(name)
    FORMAT = "%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s"
    logger.setLevel(10)

    sh = logging.StreamHandler()    # hand
    sh.setLevel(sh_level)
    sh.setFormatter(logging.Formatter(FORMAT))

    fh = logging.handlers.RotatingFileHandler(filename=f"logger/app_log.log")   # Использование прокаченного логгр-хэндлера
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(fh_level)

    logger.addHandler(sh)
    logger.addHandler(fh)

    logger.debug("Logger was initialized")


if __name__ == "__main__":
    pass
