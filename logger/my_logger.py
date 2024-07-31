import logging
import logging.handlers


def init_logger(name, sh_level: int = 30, fh_level: int = 30):
    """Инициализация логгера
    sh_level - уровень логгера на отображение в экране
    fh_level: int = 30 - уровень логгера

    """
    logger = logging.getLogger(name)
    FORMAT = "%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s"
    logger.setLevel(10)

    sh = logging.StreamHandler()  # отображение в экран
    sh.setLevel(sh_level)
    sh.setFormatter(logging.Formatter(FORMAT))

    fh = logging.handlers.RotatingFileHandler(
        filename="logger/err_log.log"
    )  # Использование прокаченного логгр-хэндлера
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(fh_level)

    full_log = logging.handlers.RotatingFileHandler(filename="logger/app_log.log")
    full_log.setFormatter(logging.Formatter(FORMAT))
    full_log.setLevel(10)

    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.addHandler(full_log)

    logger.debug("Logger was initialized")


if __name__ == "__main__":
    pass
