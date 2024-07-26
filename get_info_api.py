import logging
import requests

from aio_bot import config_bot
from datetime import datetime

API_GYMKHANA = config_bot.config_gymchana_cup["API"]
SITE = config_bot.config_gymchana_cup["site"]

logger = logging.getLogger("app.get_info_api")


def get_sportsmans_from_ggp_stage(site=SITE, api_gymkhana=API_GYMKHANA):
    """Функция получения данных спортсменов участвующих в действующем этапе
    и возвращающая списка всех спортсменов с использованием GET API
    """
    # получаем действующий ЧЕМПИОНАТ
    try:
        get_api = requests.get(
            f"{site}championships/list?signature={api_gymkhana}&types=gp&fromYear={datetime.now().year}"
            f"&toYear={datetime.now().year}"
        )
    except ConnectionError:
        logger.error("Пропало соединение с интернетом")
        return {}
    if not get_api.ok:
        logger.error("Server or API-key is invalid")
        raise Exception(
            "get_sportsmans_from_ggp_stage [Responce 500] API or Server invalid"
        )
    championship_id = get_api.json()[0]["id"]

    # взяв ID действующего чемпионата получаем его этапы и после проходим по ним пока не найдем действующий
    get_api = requests.get(
        f"{site}/championships/get?signature={api_gymkhana}&id={championship_id}&type=gp"
    )
    stages = get_api.json()["stages"]
    logger.info("Проверяем сайт ")

    for stage in stages:
        # поиск действующего этапа, если его нет - значит этап не идет
        if stage["status"] in ("Приём результатов", "Подведение итогов"):
            now_stage = stage
            get_api = requests.get(
                f"{site}/stages/get?signature={api_gymkhana}&id={now_stage['id']}&type=gp"
            )
            # выставляем более частую проверку и выставляем id этапа ! ПОТОМ ВЫНЕСТИ В ДРУГУЮ ФУНКЦИЮ
            config_bot.config_gymchana_cup["GET_TIME_OUT"] = 60 * 5
            config_bot.config_gymchana_cup["id_stage_now"] = now_stage["id"]
            config_bot.config_gymchana_cup["trackUrl"] = now_stage["trackUrl"]
            logger.info(f"Сейчас: stage[{now_stage['id']}]")
            return get_api.json()

    # задержка проверки результатов бота в секундах
    logger.info("Сейчас нет приема результатов, устанавливаем повышенный таймаут")
    config_bot.config_gymchana_cup["GET_TIME_OUT"] = 60 * 60 * 3
    logger.info(f"Таймаут = {config_bot.config_gymchana_cup['GET_TIME_OUT']}")
    config_bot.config_gymchana_cup["trackUrl"] = False
    return False


if __name__ == "__main__":
    get_sportsmans_from_ggp_stage()
    print(get_sportsmans_from_ggp_stage())
    print(f"Сейчас идет {get_sportsmans_from_ggp_stage()}")
