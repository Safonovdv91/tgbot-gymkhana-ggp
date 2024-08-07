from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from DB.models import TelegramUser, BetTimeTelegramUser
from aio_bot import aio_markups as nav
from aiogram.filters import CommandStart, Command
from aiogram import F

from aio_bot.aio_bot_functions import BotInterface, BotFunction
from aio_bot import config_bot
from DB import database as DBM
from DB.db_obj import DbStageResults, DbBetTime

# import os
import logging
from aio_bot import aio_bot_functions
from aio_bot.aio_markups import btnBackToMenu
from app.bot_states import BotStates

router = Router()
logger = logging.getLogger("app.handlers")


# Инициализация меню по нажатию старт
@router.message(CommandStart())
async def start_bot(message: types.Message):
    logger.info(f"Запустил /start {message.from_user.username}")
    text = (
        "Олоха мой джимхо друг, я бот созданный немного помочь тебе в мотоджимхане, не будем "
        "затягивать вот что я умею: \n"
        "'✒Подписаться' - здесь ты можешь подписаться на результаты спортсменов "
        "катающих этап GGP 2023. Просто нажимай 'Подписаться' и выбирай классы которые"
        " тебя интересуют, как только "
        "их результат выложат - я пришлю тебе уведомление. \n "
        "Получить 🗺 этапа' - тут ты можешь получить текущий этап GGP 2023, если вдруг забыл куда ехать"
        " - нажимай и учи. \n"
        " 'Получить 🕗 этапа' - считай калькулятор - динамически обновляется как только спортсмены"
        " улучшат результат,"
        " что бы ты мог понимать на какой уровень катаешь.\n"
        " '⌚ Сделать ставку на лучшее время GGP' - попробуй отгадать лучше время спортсмена!\n\n"
        "🧮 А ещё ты можешь мне прислать время в формате mm:ss.ms или ss.ms и "
        "получишь быстрый расчёт рейтинга."
    )
    await message.answer(text, reply_markup=nav.mainMenu)


@router.message(Command("help"))
async def help_bot(message: types.Message):
    text = (
        "Ещё раз как пользоваться:\n"
        "Внизу имеется встроенное меню (где можно писать сообщения и 'прикреплять файлы📎') нажимаешь на меню и "
        "откроются кнопки с командами:\n"
        "'✒Подписаться' нажимаешь на неё, и там выбираешь от какого класса спортсменов хочешь получать уведомления, "
        "скорее всего тебя будет интересовать твой класс например (🟨 D1 и  🟦🇧) - смело нажимай на них,"
        " а когда ты с прогрессируешь и повысишь свой навык то смело нажми на кнопку 🟨 D1 и 🟩 С3 - и больше никаких "
        "уведомлений о результатах 🟨 D1 \n"
        "'Получить 🗺 этапа' - нажав на эту кнопку получишь карту текущего этапа в виде картинки и можешь вспомнить "
        "куда там ехать дальше то ;)\n"
        "'Получить 🕗 этапа' - отлично, ты проехал трассу показав хорошее время и тебе не терпится узнать "
        "свой класс! Эта кнопка выдаст таблицу с расчётом рейтинга (аналог калькулятора).\n"
        " '⌚ Сделать ставку на лучшее время GGP' - попробуй отгадать лучше время спортсмена!\n"
        "🧮 А ещё ты можешь мне прислать время в формате mm:ss.ms или ss.ms и получишь быстрый расчёт рейтинга."
    )
    await message.answer(text)


@router.message(Command("unsub"))
async def unsubscribe_bot(message: types.Message):
    """Удаляем все подписки у пользователя"""
    logger.info(f"User unsub - {message.from_user.id}. Delete him.")
    BotInterface.unsub_tguser(message.from_user.id)
    await message.answer("Прощай друг 😿")


@router.message(F.text == "Получить 🗺 этапа")
async def send_map(message: types.Message):
    if message.text == "Получить 🗺 этапа":
        logger.info(
            f"Пришел запрос карты от [{message.from_user.full_name}]:{message.from_user.id}"
        )
        try:
            if config_bot.config_gymchana_cup["trackUrl"]:
                track_url = f"https://gymkhana-cup.ru/competitions/special-stage?id={config_bot.config_gymchana_cup['id_stage_now']}"
                await message.answer_photo(
                    photo=config_bot.config_gymchana_cup["trackUrl"], caption=track_url
                )
            else:
                await message.answer(" Сейчас межсезонье мэн, покатай базовую фигуру")
        except Exception as e:
            logger.exception(
                f"Поймано исключение при отправке карты этапа {message.from_user.id} : -",
                e,
            )
            await message.answer(
                "Бро, что-то пошло не так 8'(- скорее всего сервак лежит, запроси карту попозже..."
            )
            # await message.answer(f'❗ Поймано исключение при отправке карты этапа от {message.from_user.id}:'
            #                                  f'\n {e}')


@router.message(F.text == "⌚ Сделать ставку на лучшее время GGP")
async def make_bet(message: types.Message, state: FSMContext):
    db_bet = DbBetTime().get(tg_id=message.from_user.id)
    logger.info(f"Начал делать ставку: {message.from_user.username}")

    # Считываем данные о юзере
    if db_bet:
        logger.info(f"{message.from_user.username} - уже есть в базе")

        user = TelegramUser(
            tg_id=db_bet["tg_user"]["tg_id"],
            username=db_bet["tg_user"]["username"],
            first_name=db_bet["tg_user"]["first_name"],
            full_name=db_bet["tg_user"]["full_name"],
            language_code=db_bet["tg_user"]["language_code"],
        )
        bet = BetTimeTelegramUser(
            tg_user=user, bet_time1=db_bet["bet_time1"], date_bet1=db_bet["date_bet1"]
        )
        nickname = f"Nickname: {bet.tg_user.username}"
        bet_time = f"Bet time: {BotFunction.msec_to_mmssms(bet.bet_time1)}"
        bet_date = f"Bet date: {bet.date_bet1}"
        text = f"{nickname}\n{bet_time}\n{bet_date}"
        await message.answer(
            f"Твои текущие данные:\n{text}",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Отменить ставку"),
                        KeyboardButton(text="Поменять ставку"),
                    ],
                    [btnBackToMenu],
                ],
                resize_keyboard=True,
            ),
        )
    else:
        logger.info(f"делает новую ставку {message.from_user.username}")
        await message.answer(
            "Напишите время за которое вы ожиадаете что проедет лучший спортсмен",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[btnBackToMenu]],
                resize_keyboard=True,
                input_field_placeholder="45.67 или 01:02.34",
            ),
        )
        await state.set_state(BotStates.Get_betting_time)


@router.message(F.text == "Подписаться")
async def subscribe_ggp_class(message: types.Message, state: FSMContext):
    logger.info(f"Начал подписываться на классы{message.from_user.username}")
    await state.set_state(BotStates.GGP_CLASS_SUBSCRIBE)
    await subscribe_results(message, state)
    await message.answer(
        "Выбери на какой класс подписаться",
        reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
    )


@router.message(BotStates.GGP_CLASS_SUBSCRIBE)
async def subscribe_results(message: types.Message, state: FSMContext):
    if message.text == "⬅ НАЗАД":
        await message.answer(
            "Главное меню",
            reply_markup=nav.mainMenu,
        )
        await state.clear()
    elif message.text in ("🟥 🅰️", "🔲 🅰️"):
        await message.answer(
            DBM.update_user_subs(message, "🟥A", "A"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟦 🇧", "🔲 🇧"):
        await message.answer(
            DBM.update_user_subs(message, "🟦🇧", "B"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟩 С1", "🔲 С1"):
        await message.answer(
            DBM.update_user_subs(message, "🟩 С1", "C1"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟩 С2", "🔲 С2"):
        await message.answer(
            DBM.update_user_subs(message, "🟩 С2", "C2"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟩 С3", "🔲 С3"):
        await message.answer(
            DBM.update_user_subs(message, "🟩 С3", "C3"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟨 D1", "🔲 D1"):
        await message.answer(
            DBM.update_user_subs(message, "🟨 D1", "D1"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟨 D2", "🔲 D2"):
        await message.answer(
            DBM.update_user_subs(message, "🟨 D2", "D2"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟨 D3", "🔲 D3"):
        await message.answer(
            DBM.update_user_subs(message, "🟨 D3", "D3"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )
    elif message.text in ("🟨 D4", "🔲 D4"):
        await message.answer(
            DBM.update_user_subs(message, "🟨 D4", "D4"),
            reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
        )


@router.message()
async def get_time_stage(message: types.Message):
    if message.text == "⬅ НАЗАД":
        await message.answer("Главное меню", reply_markup=nav.mainMenu)

    elif message.text == "Получить 🕗 этапа":
        logger.info(f"Запросил карту {message.from_user.username}")
        if config_bot.config_gymchana_cup["trackUrl"] is False:
            await message.answer("На данный момент ещё нет ни одного результата")
            return
        b_result = DbStageResults().get_bestStage_time()
        if b_result is None:
            await message.answer("На данный момент ещё нет ни одного результата")
        else:
            text = aio_bot_functions.BotFunction().make_calculate_text(b_result)
            await message.answer(text)

    else:
        try:
            best_time_ms = aio_bot_functions.BotFunction().convert_to_milliseconds(
                message.text
            )
            if best_time_ms > 0:
                text = aio_bot_functions.BotFunction().make_calculate_text(best_time_ms)
                mmssms = aio_bot_functions.BotFunction().msec_to_mmssms(best_time_ms)
                text = f"Для времени: {mmssms} \n{text}"
                await message.answer(text, reply_markup=nav.mainMenu)
            else:
                await message.answer(
                    "Братишка, не надо просто так писать,"
                    " воспользуйся встроенным меню ;)↘ или напиши /help",
                    reply_markup=nav.mainMenu,
                )
        except Exception as e:
            logger.exception(f"Common error: {e}", exc_info=True)
            await message.answer(
                "Братишка, не надо просто так писать,"
                " воспользуйся встроенным меню ;)↘ или напиши /help",
                reply_markup=nav.mainMenu,
            )
