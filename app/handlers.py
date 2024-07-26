from aiogram import Router, types
from aio_bot import aio_markups as nav
from aiogram.filters import CommandStart, Command
from aiogram.types import InputFile

from aio_bot.aio_bot_functions import BotInterface
from aio_bot import config_bot
from DB import database as DBM
from DB.db_obj import DbStageResults

# import os
import logger.my_logger
import logging.handlers
from aio_bot import aio_bot_functions

router = Router()
logger = logging.getLogger("app")


# Инициализация меню по нажатию старт
@router.message(CommandStart())
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
    await message.answer(text, reply_markup=nav.mainMenu)


@router.message(Command("help"))
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


@router.message(Command("unsub"))
async def unsubscribe_bot(message: types.Message):
    """Удаляем все подписки у пользователя"""
    logger.info(f"User unsub - {message.from_user.id}. Delete him.")
    BotInterface.unsub_tguser(message.from_user.id)
    await message.answer("Прощай друг 😿")


@router.message()
async def subscribe_results(message: types.Message):
    """ Анализ сообщения для подписки
    """
    if message.text == "Подписаться":
        await message.answer("Выбери на какой класс подписаться",
                               reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟥 🅰️", "🔲 🅰️"):
        await message.answer(DBM.update_user_subs(message.from_user.id, "🟥A", "A"),
                             reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id))
    elif message.text in ("🟦 🇧", "🔲 🇧"):
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
        await message.answer("Главное меню", reply_markup=nav.mainMenu)

    elif message.text == "Получить 🗺 этапа":
        logger.info(f"Пришел запрос карты от {message.from_user.id}")
        try:
            if config_bot.config_gymchana_cup["trackUrl"]:
                url = f"https://gymkhana-cup.ru/competitions/special-stage?id={config_bot.config_gymchana_cup['id_stage_now']}"
                await message.answer(url)
                photo = InputFile("DB/stage.jpg")
                await message.answer(photo=photo)
            else:
                await message.answer(" Сейчас межсезонье мэн, покатай базовую фигуру")
        except Exception as e:
            logger.exception(f"Поймано исключение при отправке карты этапа {message.from_user.id} : -", e)
            await message.answer("Бро, что-то пошло не так 8'(- скорее всего сервак лежит, запроси карту попозже...")
            # await message.answer(f'❗ Поймано исключение при отправке карты этапа от {message.from_user.id}:'
            #                                  f'\n {e}')

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
