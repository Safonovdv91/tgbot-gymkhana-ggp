from aiogram import exceptions
from aiogram import Bot, Dispatcher
from aio_bot import config_bot
from DB import database as DBM
from DB.db_obj import DbStageResults, DbSubsAtheleteClass
from DB.models import StageSportsmanResult

# import os
import logger.my_logger
import logging.handlers
import asyncio
import get_info_api
from aio_bot.aio_bot_functions import BotInterface
from app.handlers import router

API_bot = config_bot.config["API_token"]
admin_id = config_bot.config["admin_id"]

logger.my_logger.init_logger("app", sh_level=10, fh_level=30)
logger = logging.getLogger("app")
logger.info("Server is starting...")
# инициализируем бота
bot = Bot(token=API_bot)
dp = Dispatcher()


#
# --- Периодическое обновление участников этапа ---
async def scheduled():
    """Запланированная периодическая задача отвечающая за сравнение и раcсылку новых результатов"""
    while True:
        try:
            logger.info("Тик бота")
            await asyncio.sleep(config_bot.config_gymchana_cup["GET_TIME_OUT"])
            data_dic = await get_info_api.get_sportsmans_from_ggp_stage()
            logger.debug(f" timeout = {config_bot.config_gymchana_cup['GET_TIME_OUT']}")
            if not data_dic:
                continue
            """--- New stage! ---
            if id_stage_now != config_bot.config_gymchana_cup["id_stage_now"]:
                for each in DbTgUsers().get_all_subscribers():
                    if len(each["sub_stage_cat"]):
                        !!! download_stage_map !!!
                        new_stage_msg = f"Ура, начался новый этап! Надеюсь погода будет благоволить тебе ️☀️☀️," \
                                        f" а результат вызывать восхищение 🤩! Помни что первым можно быть не только " \
                                        f"по времени проезда!\n Но и первым кто выложит результат!😉 " \
                                        f"{config_bot.config_gymchana_cup['trackUrl']}"
                        await bot.send_message(each["_id"], new_stage_msg)
            --- New stage ---"""
            get_results_from_stage = data_dic["results"]

            for each in get_results_from_stage:
                b_result = DbStageResults().get_bestStage_time()
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
                            persents = round(
                                each["resultTimeSeconds"] / b_result * 100, 2
                            )

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
                    tg_clients = DbSubsAtheleteClass().get_subscriber(
                        each["athleteClass"]
                    )

                    for tg_client in tg_clients:
                        try:
                            await bot.send_message(
                                tg_client, msg_text, disable_notification=True
                            )

                        except exceptions.TelegramBadRequest:
                            """ Бот заблокирован, значит удаляем из подписок"""
                            logger.info(
                                f"Bot is blocked user - {tg_client}. Delete him."
                            )
                            BotInterface.unsub_tguser(tg_client)
                        except Exception as e:
                            logger.exception(f"Поймано исключение: {e}")

        except Exception as e:
            logger.exception(f"aio_bot_start: {e}")
            await bot.send_message(admin_id, f"Exception {e}")


# Запускаем лонг поллинг
async def main():
    logger.info("Запускаем бота")
    dp.include_router(router)
    asyncio.create_task(scheduled())  # Запуск периодической задачи
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
