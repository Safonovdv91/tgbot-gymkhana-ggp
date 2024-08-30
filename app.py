import asyncio
import logging

from aiogram import Bot, Dispatcher, exceptions

import get_info_api
from aio_bot import config_bot
from aio_bot.aio_bot_functions import BotInterface
from app.betting.handlers import router as bet_router
from app.handlers import router
from DB import database as DBM
from DB.db_obj import DbStageResults, DbSubsAtheleteClass
from DB.models import StageSportsmanResult

API_bot = config_bot.config["API_token"]
admin_id = config_bot.config["admin_id"]


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M.%S",
        format="[%(asctime)s.%(msecs)03d] %(module)15s:%(lineno)-4d %(levelname)7s - %(message)s",
    )


logger = logging.getLogger(__name__)
configure_logging(level=logging.INFO)

# инициализируем бота
bot = Bot(token=API_bot)
dp = Dispatcher()


async def scheduled():
    """Запланированная периодическая задача отвечающая за сравнение и раcсылку новых результатов"""
    while True:
        try:
            logger.debug("Тик бота")
            await asyncio.sleep(config_bot.config_gymchana_cup["GET_TIME_OUT"])
            data_dic = await get_info_api.get_sportsmans_from_ggp_stage()
            logger.debug("timeout: %s.", config_bot.config_gymchana_cup["GET_TIME_OUT"])
            if not data_dic:
                continue
            get_results_from_stage = data_dic["results"]

            for each in get_results_from_stage:
                b_result = DbStageResults().get_best_stage_time()
                msg_text = False
                sportsman_result = StageSportsmanResult(
                    each["userId"],
                    each["userFullName"],
                    each["motorcycle"],
                    each["userCity"],
                    each["userCountry"],
                    each["athleteClass"],
                    each["resultTimeSeconds"],
                    each["resultTime"],
                    each["fine"],
                    each["video"],
                )

                db_sportsman = DBM.find_one_sportsman_from_stage(each["userId"])

                if db_sportsman is None:
                    if b_result is None:
                        persents = 100
                    else:
                        persents = round(each["resultTimeSeconds"] / b_result * 100, 2)
                    msg_text = (
                        f" {each['athleteClass']}: {each['userFullName']} \n "
                        f"{persents}% |   {each['resultTime']}\n"
                        f"{each['video']}"
                    )

                    msg_text = f"⚡ Новый результат\n{msg_text}"

                    # Добавляем новый результат спортсмена в базу данных
                    DBM.add_stage_result(sportsman_result)

                else:
                    if each["resultTimeSeconds"] < db_sportsman["resultTimeSeconds"]:
                        if b_result is None:
                            persents = 100
                        else:
                            persents = round(each["resultTimeSeconds"] / b_result * 100, 2)

                        msg_text = (
                            f" {each['athleteClass']}: {each['userFullName']} \n "
                            f"{persents}% |   {each['resultTime']}\n"
                            f"было:   |   [{db_sportsman['resultTime']}] \n {each['video']} "
                        )
                        msg_text = f"💥 Улучшил время\n {msg_text}"

                        # Обновляем новый результат спортсмена в базе данных
                        DBM.update_stage_result(sportsman_result)

                # Раcсылаем сообщения
                if msg_text:
                    tg_clients = DbSubsAtheleteClass().get_subscriber(each["athleteClass"])

                    for tg_client in tg_clients:
                        try:
                            await bot.send_message(tg_client, msg_text, disable_notification=True)

                        except exceptions.TelegramBadRequest:
                            """ Бот заблокирован, значит удаляем из подписок"""
                            logger.info(
                                "Bot is blocked user - %s." " Delete him.",
                                tg_client,
                            )
                            BotInterface.unsub_tguser(tg_client)
                        except Exception:
                            logger.exception("Поймано исключение:")

        except Exception as e:
            logger.exception("aio_bot_start")
            await bot.send_message(admin_id, f"Exception {e}")


# Запускаем лонг поллинг
async def main():
    dp.include_router(bet_router)
    dp.include_router(router)
    asyncio.create_task(scheduled())  # Запуск периодической задачи
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logger.info("Server is starting...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
