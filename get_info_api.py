import logging

from aio_bot import config_bot

import requests

from datetime import datetime

API_GYMKHANA = config_bot.config_gymchana_cup["API"]
SITE = config_bot.config_gymchana_cup["site"]


def get_sportsmans_from_ggp_stage(site=SITE, api_gymkhana=API_GYMKHANA):
    """ Функция получения данных спортсменов участвующих в действующем этапе
    и возвращающая списка всех спортсменов с использованием GET API
    """
    # получаем действующий ЧЕМПИОНАТ
    get_api = requests.get(f"{site}championships/list?signature={api_gymkhana}&types=gp&fromYear={datetime.now().year}"
                           f"&toYear={datetime.now().year}")
    championship_id = get_api.json()[0]["id"]

    # взяв ID действующего чемпионата получаем его этапы и после проходим по ним пока не найдем действующий
    get_api = requests.get(f"{site}/championships/get?signature={api_gymkhana}&id={championship_id}&type=gp")
    stages = get_api.json()["stages"]

    for stage in stages:
        # поиск действующего этапа, если его нет - значит этап не идет
        if stage["status"] in ("Приём результатов", "Подведение итогов"):
            now_stage = stage
            get_api = requests.get(f"{site}/stages/get?signature={api_gymkhana}&id={now_stage['id']}&type=gp")
            # выставляем более частую проверку и выставляем id этапа ! ПОТОМ ВЫНЕСТИ В ДРУГУЮ ФУНКЦИЮ
            config_bot.config_gymchana_cup["GET_TIME_OUT"] = 60 * 5
            config_bot.config_gymchana_cup["id_stage_now"] = now_stage["id"]
            config_bot.config_gymchana_cup["trackUrl"] = now_stage["trackUrl"]
            return get_api.json()

    # сделать задержу проверки результатов бота в секундах
    logging.info("Сейчас нет приема результатов, устанавливаем повышенный таймаут")
    config_bot.config_gymchana_cup["GET_TIME_OUT"] = 3600 * 6
    logging.info(f"Таймаут = {config_bot.config_gymchana_cup['GET_TIME_OUT']}")
    config_bot.config_gymchana_cup["trackUrl"] = False
    return False


if __name__ == "__main__":
    get_sportsmans_from_ggp_stage()
    print(get_sportsmans_from_ggp_stage())
    print(f"Сейчас идет {get_sportsmans_from_ggp_stage()}")
