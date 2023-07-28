from aiogram import Bot, Dispatcher, executor, types
from aio_bot import config_bot
from aio_bot import aio_markups as nav
from DB import database as DBM
from DB.db_obj import DbStageResults, DbSubsAtheleteClass
from DB.models import StageSportsmanResult

# import os
import logging
import asyncio
import get_info_api
from aio_bot import aio_bot_functions


API_bot = config_bot.config['API_token']
admin_id = config_bot.config['admin_id']

# Получение данных из докеркомпоза
# BOT_TOKEN = os.environ.get("BOT_TOKEN")
# MONGO_HOST = os.environ.get("MONGO_HOST")
# MONGO_PORT = os.environ.get("MONGO_PORT")
# MONGO_DB = os.environ.get("MONGO_DB")


# задаем логирование
logging.basicConfig(level=logging.INFO, filename="aio_bot/logs/bot_log.log",
                    filemode="w", format="%(asctime)s %(levelname)s %(message)s")

# инициализируем бота
bot = Bot(token=API_bot, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# Инициализация меню по нажатию страрт
@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    text = "Олоха мой джимхо друг, я бот создаyный немного помочь тебе в мотоджимхане не будем " \
           "затягивать вот что я умею: \n" \
           "'✒Подписаться' - здесь ты можешь подписаться на результаты спортсменов " \
           "катающих этап GGP 2023. Просто нажимай 'Подписаться' и выбирай классы которые" \
           " тебя интересуют, как только "\
           "их результат выложат - я пришлю тебе уведомление. \n " \
           "Получить 🗺 этапа' - тут ты можешь получить текущий этап GGP 2023, если вдруг забыл куда ехать" \
           " - нажимай и учи. \n" \
           " 'Получить 🕗 этапа' - считай калькулятор - динамически обновляется как только спортсмены" \
           " улучшат результат," \
           " что бы ты мог понимать на какой уровень катаешь.\n\n" \
           "🧮 А ещё ты можешь мне прислать время в формате mm:ss.ms или ss.ms и " \
           "получишь быстрый расчёт рейтинга."
    await bot.send_message(message.from_user.id, text, reply_markup=nav.mainMenu)


@dp.message_handler(commands=["help"])
async def help_bot(message: types.Message):
    text = "Ещё раз как пользоваться:\n" \
           "Внизу имеется встроенное меню (где можно писать сообщения и 'прикреплять файлы📎') нажимаешь на меню и " \
           "откроются кнопки с командами:\n" \
           "'✒Подписаться' нажимаешь на неё, и там выбираешь от какого класса спортсменов хочешь получать уведомления, " \
           "скорее всего тебя будет интересовать твой класс например (🟨 D1 и  🟦🇧) - смело нажимай на них," \
           " а когда ты с прогрессируешь и повысишь свой навык то смело нажми на кнопку 🟨 D1 и 🟩 С3 - и больше никаких " \
           "уведомлений о результатах 🟨 D1 \n" \
           "'Получить 🗺 этапа' - нажав на эту кнопку получишь карту текущего этапа в виде картинки и можешь вспомнить " \
           "куда там ехать дальше то ;)\n" \
           "'Получить 🕗 этапа' - отлично, ты проехал трассу показав хорошее время и тебе не терпится узнать " \
           "свой класс! Эта кнопка выдаст таблицу с расчётом рейтинга (аналог калькулятора).\n" \
           "🧮 А ещё ты можешь мне прислать время в формате mm:ss.ms или ss.ms и получишь быстрый расчёт рейтинга."
    await message.answer(text)


@dp.message_handler(commands=["unsub"])
async def unsubscribe_bot(message: types.Message):
    """Удаляем все подписки у пользователя"""
    pass


@dp.message_handler()
async def subscribe_results(message: types.Message):
    """ Анализ сообщения для подписки
    """
    if message.text == "Подписаться":
        await bot.send_message(message.from_user.id, "Выбери на какой класс подписаться",
                               reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟦🇧", "🔲 🇧"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟦🇧", "B"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟩 С1", "🔲 С1"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟩 С1", "C1"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟩 С2", "🔲 С2"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟩 С2", "C2"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟩 С3", "🔲 С3"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟩 С3", "C3"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D1", "🔲 D1"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟨 D1", "D1"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D2", "🔲 D2"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟨 D2", "D2"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D3", "🔲 D3"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟨 D3", "D3"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D4", "🔲 D4"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟨 D4", "D4"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text == "⬅ НАЗАД":
        await bot.send_message(message.from_user.id, "Главное меню", reply_markup=nav.mainMenu)

    elif message.text == "Получить 🗺 этапа":
        try:
            if config_bot.config_gymchana_cup["trackUrl"]:
                await bot.send_message(message.from_user.id, config_bot.config_gymchana_cup["trackUrl"])
            else:
                await bot.send_message(message.from_user.id, " Сейчас межсезонье мэн, покатай базовую фигуру")
        except Exception as e:
            logging.exception("def subscribe result")
            logging.exception(e)
            print(f"Поймано исключение при отправке карты этапа {message.from_user.id} : -", e)
            await message.answer("Бро, что-то пошло не так 8'(- скорее всего сервак лежит, запроси карту попозже...")
            await bot.send_message(admin_id, f'❗ Поймано исключение при отправке карты этапа от {message.from_user.id}:'
                                             f'\n {e}')

    elif message.text == "Получить 🕗 этапа":
        b_result = DbStageResults().get_bestStage_time()
        if b_result is None:
            await message.answer("На данный момент ещё нет ни одного результата")
        else:
            text = aio_bot_functions.BotFunction().make_calculate_text(b_result)
            await message.answer(text)

    elif message.text == "Подписаться news":
        await bot.send_message(message.from_user.id, "функция находится в разработке, надо немного подождать",
                               reply_markup=nav.mainMenu)
    else:
        try:
            best_time_ms = aio_bot_functions.BotFunction().convert_to_milliseconds(message.text)
            if best_time_ms > 0:
                text = aio_bot_functions.BotFunction().make_calculate_text(best_time_ms)
                mmssms = aio_bot_functions.BotFunction().msec_to_mmssms(best_time_ms)
                text = f"Для времени: {mmssms} \n{text}"
                await message.answer(text, reply_markup=nav.mainMenu)
            else:
                await message.answer('Братишка, не надо просто так писать,'
                                     ' воспользуйся встроенным меню ;)↘ или напиши /help',
                                     reply_markup=nav.mainMenu)
        except Exception as e:
            print(e)
            logging.error(e)
            await message.answer('Братишка, не надо просто так писать,'
                                 ' воспользуйся встроенным меню ;)↘ или напиши /help',
                                 reply_markup=nav.mainMenu)


#
# --- Периодическое обновление участников этапа ---
async def scheduled():
    """ Запланированная периодическая задача отвечающая за сравнение и разсылку новых результатов
    """
    while True:
        try:
            print("_", end='')
            await asyncio.sleep(config_bot.config_gymchana_cup["GET_TIME_OUT"])
            data_dic = get_info_api.get_sportsmans_from_ggp_stage()
            if not data_dic:
                return False
            get_results_from_stage = data_dic["results"]
            for each in get_results_from_stage:
                msg_text = False
                sportsman_result = StageSportsmanResult(each["userId"], each["userFullName"],
                                                        each["motorcycle"],
                                                        each["userCity"], each["userCountry"],
                                                        each["athleteClass"],
                                                        each["resultTimeSeconds"], each["resultTime"],
                                                        each["fine"],
                                                        each["video"])

                db_sportsman = DBM.find_one_sportsman_from_stage(each["userId"])
                if db_sportsman is None:
                    msg_text = f"{each['athleteClass']}: {each['userFullName']} - {each['resultTime']}\n{each['video']}"
                    msg_text = f"⚡ Новый результат\n{msg_text}"

                    # Добавляем новый результат спортсмена в базу данных
                    DBM.add_stage_result(sportsman_result)

                else:
                    if each["resultTimeSeconds"] < db_sportsman["resultTimeSeconds"]:
                        msg_text = f"{each['athleteClass']}: {each['userFullName']} - {each['resultTime']} \n" \
                                   f"было: [{db_sportsman['resultTime']}] \n {each['video']} "
                        msg_text = f"💥 Улучшил время\n {msg_text}"

                        # Обновляем новый результат спортсмена в базе данных
                        DBM.update_stage_result(sportsman_result)

                # Разсылаем сообщения
                if msg_text:
                    tg_clients = DbSubsAtheleteClass().get_subscriber(each["athleteClass"])
                    for tg_client in tg_clients:
                        await bot.send_message(tg_client, msg_text, disable_notification=True)

        except Exception as e:
            logging.exception("aio_bot_start")
            logging.exception(e)
            await bot.send_message(admin_id, f"Exception{e}")


# Запускаем лонг поллинг
def main():
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled())
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
