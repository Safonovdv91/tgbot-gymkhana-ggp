import logging
from datetime import datetime

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
from aio_bot import aio_bot_functions
from aio_bot.aio_markups import btnBackToMenu
from app.bot_states import BotStates
from app.constants import HELP_MESSAGE, BAD_MESSAGE, START_MESSAGE

router = Router()
logger = logging.getLogger(__name__)


# Инициализация меню по нажатию старт
@router.message(CommandStart())
async def start_bot(message: types.Message):
    logger.info(f"Запустил /start {message.from_user.username}")
    await message.answer(START_MESSAGE, reply_markup=nav.mainMenu)


@router.message(Command("help"))
async def help_bot(message: types.Message):
    await message.answer(HELP_MESSAGE)


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
                await message.answer("Сейчас межсезонье мэн, покатай базовую фигуру")
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
    date_end = config_bot.config_gymchana_cup["end_bet_time"]
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
        if datetime.now() > date_end:
            await message.answer(
                "Приём ставок окончен:\nТвои данные:\n{}".format(text),
                reply_markup=nav.mainMenu,
            )
            return

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
        if datetime.now() > date_end:
            await message.answer(
                "Приём ставок окончен, к сожалению ты не успел, попробуй на следующем этапе, "
                "приём ставки на время длится 1 неделю с момента начала этапа.",
                reply_markup=nav.mainMenu,
            )
            return
        await message.answer(
            "Напишите время за которое вы ожиадаете что проедет лучший спортсмен\nПриём результата до {}".format(
                date_end
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[btnBackToMenu]],
                resize_keyboard=True,
                input_field_placeholder="45.67 или 01:02.34",
            ),
        )
        await state.set_state(BotStates.Get_betting_time)


@router.message(F.text == "Подписаться")
async def subscribe_ggp_class(message: types.Message, state: FSMContext):
    logger.info(f"Начал подписываться на классы: {message.from_user.username}")
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
                    BAD_MESSAGE,
                    reply_markup=nav.mainMenu,
                )
        except TypeError:
            logger.warning(
                "User: %s [%s] прислал не число.",
                message.from_user.username,
                message.from_user.id,
            )
            await message.answer(
                BAD_MESSAGE,
                reply_markup=nav.mainMenu,
            )
        except Exception as e:
            logger.exception(f"Common error: {e}", exc_info=True)
            await message.answer(
                BAD_MESSAGE,
                reply_markup=nav.mainMenu,
            )
