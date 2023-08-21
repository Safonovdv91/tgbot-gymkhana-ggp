from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.utils.exceptions import BotBlocked
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aio_bot.aio_bot_functions import BotInterface
from aio_bot import config_bot
from aio_bot import aio_markups as nav
from DB import database as DBM
from DB.db_obj import DbStageResults, DbSubsAtheleteClass
from DB.models import StageSportsmanResult, TelegramUser

# import os
import logger.my_logger
import logging.handlers
import asyncio
import get_info_api
from aio_bot import aio_bot_functions

API_bot = config_bot.config['API_token']
admin_id = config_bot.config['admin_id']

logger.my_logger.init_logger("app", sh_level=10, fh_level=30)
logger = logging.getLogger("app.app")
logger.info("Server is starting...")

# инициализируем бота
bot = Bot(token=API_bot, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# Инициализация меню по нажатию старт
@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    text = "Олоха мой джимхо друг, я бот созданный немного помочь тебе в мотоджимхане, не будем " \
           "затягивать вот что я умею: \n" \
           "'✒Подписаться' - здесь ты можешь подписаться на результаты спортсменов " \
           "катающих этап GGP 2023. Просто нажимай 'Подписаться' и выбирай классы которые" \
           " тебя интересуют, как только " \
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
    logger.info(f"User unsub - {message.from_user.id}. Delete him.")
    BotInterface.unsub_tguser(message.from_user.id)
    await message.answer("Прощай друг 😿")


@dp.message_handler(commands=["random"])
async def cmd_random(message: types.Message):
    button = InlineKeyboardButton("Да", callback_data="Yes")
    button2 = InlineKeyboardButton("Нет", callback_data="NO")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(button)
    keyboard.add(button2)
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data == 'Yes')
async def process_callback_button(callback_query: types.CallbackQuery):
    await callback_query.answer("Вы нажали на кнопку!")


@dp.message_handler(commands=["bet"])
async def betting_time(message: types.Message):
    """ Делаем ставку
    """
    logger.info(f"Пользователь {message.from_user.full_name} сделал ставку {message.text}")
    await message.answer(aio_bot_functions.DoBet.do_bet(message, message.text))


@dp.message_handler(commands=["my_bet"])
async def betting_time(message: types.Message):
    """ Получить ставку пользователя
    """
    logger.info(f"Пользователь {message.from_user.full_name} запросил ставку: {message.text}")
    await message.answer(aio_bot_functions.DoBet.get_my_bet(message))


@dp.message_handler()
async def subscribe_results(message: types.Message):
    """ Анализ сообщения для подписки
    """
    if message.text == "Подписаться":
        await bot.send_message(message.from_user.id, "Выбери на какой класс подписаться",
                               reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟦🇧", "🔲 🇧"):
        await message.answer(DBM.update_user_subs(message, "🟦🇧", "B"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟩 С1", "🔲 С1"):
        await message.answer(DBM.update_user_subs(message, "🟩 С1", "C1"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟩 С2", "🔲 С2"):
        await message.answer(DBM.update_user_subs(message, "🟩 С2", "C2"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟩 С3", "🔲 С3"):
        await message.answer(DBM.update_user_subs(message, "🟩 С3", "C3"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D1", "🔲 D1"):
        await message.answer(DBM.update_user_subs(message, "🟨 D1", "D1"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D2", "🔲 D2"):
        await message.answer(DBM.update_user_subs(message, "🟨 D2", "D2"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D3", "🔲 D3"):
        await message.answer(DBM.update_user_subs(message, "🟨 D3", "D3"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟨 D4", "🔲 D4"):
        await message.answer(DBM.update_user_subs(message, "🟨 D4", "D4"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text == "⬅ НАЗАД":
        await bot.send_message(message.from_user.id, "Главное меню", reply_markup=nav.mainMenu)

    elif message.text == "Получить 🗺 этапа":
        logger.info(f"Пришел запрос карты от {message.from_user.id}")
        try:
            if config_bot.config_gymchana_cup["trackUrl"]:
                url = f"https://gymkhana-cup.ru/competitions/special-stage?id={config_bot.config_gymchana_cup['id_stage_now']}"
                await bot.send_message(message.from_user.id, url)
                photo = InputFile("DB/stage.jpg")
                await bot.send_photo(chat_id=message.chat.id, photo=photo)
            else:
                await bot.send_message(message.from_user.id, " Сейчас межсезонье мэн, покатай базовую фигуру")
        except Exception as e:
            logger.exception(f"Поймано исключение при отправке карты этапа {message.from_user.id} : -", e)
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
            logger.exception(f"Common error: {e}", exc_info=True)
            await message.answer('Братишка, не надо просто так писать,'
                                 ' воспользуйся встроенным меню ;)↘ или напиши /help',
                                 reply_markup=nav.mainMenu)


#
# --- Периодическое обновление участников этапа ---
async def scheduled():
    """ Запланированная периодическая задача отвечающая за сравнение и раcсылку новых результатов
    """
    while True:
        try:
            await asyncio.sleep(config_bot.config_gymchana_cup["GET_TIME_OUT"])
            id_stage_now = config_bot.config_gymchana_cup["id_stage_now"]
            data_dic = get_info_api.get_sportsmans_from_ggp_stage()
            logger.debug(f"id_stage = {id_stage_now}, timeout = {config_bot.config_gymchana_cup['GET_TIME_OUT']/ 60 } min")
            if not data_dic:
                return False
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
                sportsman_result = StageSportsmanResult(each["userId"], each["userFullName"],
                                                        each["motorcycle"],
                                                        each["userCity"], each["userCountry"],
                                                        each["athleteClass"],
                                                        each["resultTimeSeconds"], each["resultTime"],
                                                        each["fine"],
                                                        each["video"])

                db_sportsman = DBM.find_one_sportsman_from_stage(each["userId"])
                if db_sportsman is None:
                    if b_result is None:
                        persents = 100
                    else:
                        persents = round(each["resultTimeSeconds"] / b_result * 100, 2)
                    msg_text = f" {each['athleteClass']}: {each['userFullName']} \n " \
                               f"{persents}% |   {each['resultTime']}\n" \
                               f"{each['video']}"
                    msg_text = f"⚡ Новый результат\n{msg_text}"

                    # Добавляем новый результат спортсмена в базу данных
                    DBM.add_stage_result(sportsman_result)

                else:
                    if each["resultTimeSeconds"] < db_sportsman["resultTimeSeconds"]:
                        if b_result is None:
                            persents = 100
                        else:
                            persents = round(each["resultTimeSeconds"] / b_result * 100, 2)
                        msg_text = f" {each['athleteClass']}: {each['userFullName']} \n " \
                                   f"  {persents}% |   {each['resultTime']}\n" \
                                   f"было:   |   [{db_sportsman['resultTime']}] \n {each['video']} "
                        msg_text = f"💥 Улучшил время\n {msg_text}"

                        # Обновляем новый результат спортсмена в базе данных
                        DBM.update_stage_result(sportsman_result)

                # Раcсылаем сообщения
                if msg_text:
                    tg_clients = DbSubsAtheleteClass().get_subscriber(each["athleteClass"])
                    for tg_client in tg_clients:
                        try:
                            await bot.send_message(tg_client, msg_text, disable_notification=True)
                        except BotBlocked:
                            """ Бот заблокирован, значит удаляем из подписок"""
                            logger.info(f"Bot is blocked user - {tg_client}. Delete him.")
                            BotInterface.unsub_tguser(tg_client)
        except Exception as e:
            logger.exception(f"aio_bot_start: {e}")
            await bot.send_message(admin_id, f"Exception {e}")


# Запускаем лонг поллинг
def main():
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled())
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
