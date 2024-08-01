import json
import logging
import aiohttp

from aio_bot import config_bot
from datetime import datetime

API_GYMKHANA = config_bot.config_gymchana_cup["API"]
SITE = config_bot.config_gymchana_cup["site"]

logger = logging.getLogger("app.get_info_api")


async def get_sportsmans_from_ggp_stage(site=SITE, api_gymkhana=API_GYMKHANA):
    """Функция получения данных спортсменов участвующих в действующем этапе
    и возвращающая списка всех спортсменов с использованием GET API
    """
    # получаем действующий ЧЕМПИОНАТ
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{site}championships/list?signature={api_gymkhana}&types=gp&fromYear={datetime.now().year}"
                f"&toYear={datetime.now().year}"
            ) as resp:
                status_code = resp.status
                get_api = await resp.text()
                logger.debug(f"Получаем чампионаты:\n status: {status_code}")
    except ConnectionError:
        logger.error("Пропало соединение с интернетом")
        return {}
    if not status_code == 200:
        logger.error("Server or API-key is invalid")
        raise Exception(
            "get_sportsmans_from_ggp_stage [Responce 500] API or Server invalid"
        )
    resp_json = json.loads(get_api)
    championship_id = resp_json[0]["id"]

    # взяв ID действующего чемпионата получаем его этапы и после проходим по ним пока не найдем действующий
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{site}/championships/get?signature={api_gymkhana}&id={championship_id}&type=gp"
        ) as resp:
            status_code = resp.status
            get_api = await resp.text()
            logger.debug(f"Получаем этапы:\n status: {status_code}")
            if status_code == 200:
                resp_json = json.loads(get_api)

    stages = resp_json["stages"]
    for stage in stages:
        # поиск действующего этапа, если его нет - значит этап не идет
        if stage["status"] in (
            "Приём результатов",
            "Подведение итогов",
        ):
            now_stage = stage
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{site}/stages/get?signature={api_gymkhana}&id={now_stage['id']}&type=gp"
                ) as resp:
                    status_code = resp.status
                    get_api = await resp.text()
                    logger.debug(
                        f"Получаем данные одного этапа:\n status: {status_code}"
                    )
                    if status_code == 200:
                        resp_json = json.loads(get_api)
                        logger.debug(f"{resp_json["title"]} {resp_json["id"]}")

            # выставляем более частую проверку и выставляем id этапа ! ПОТОМ ВЫНЕСТИ В ДРУГУЮ ФУНКЦИЮ
            config_bot.config_gymchana_cup["GET_TIME_OUT"] = 60 * 5
            config_bot.config_gymchana_cup["id_stage_now"] = now_stage["id"]
            config_bot.config_gymchana_cup["trackUrl"] = now_stage["trackUrl"]
            return resp_json

    # задержка проверки результатов бота в секундах
    logger.info("Сейчас нет приема результатов, устанавливаем повышенный таймаут")
    config_bot.config_gymchana_cup["trackUrl"] = None
    config_bot.config_gymchana_cup["GET_TIME_OUT"] = 60 * 60 * 3
    logger.info(f"Таймаут = {config_bot.config_gymchana_cup['GET_TIME_OUT']}с")
    config_bot.config_gymchana_cup["trackUrl"] = False
