import logging
from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from DB.db_obj import DbBetTime
from DB.models import BetTimeTelegramUser, TelegramUser
from aio_bot.aio_bot_functions import BotFunction
from aio_bot.aio_markups import btnBackToMenu
from app.bot_states import BotStates
from aio_bot import aio_markups as nav

router = Router()
logger = logging.getLogger("app.betting.handlers")


@router.message(BotStates.Get_betting_nickname)
async def betting_take_nickname(message: types.Message, state: FSMContext) -> None:
    nickname = message.text
    await state.update_data(nickname=nickname)
    await state.set_state(BotStates.Get_betting_time)
    await message.answer(
        "Напиши время за которые ты ожидаешь что будет проехан этап лучшим спортсменом!"
    )


@router.message(BotStates.Get_betting_time)
async def betting_take_time(message: types.Message, state: FSMContext):
    logger.info(f"{message.from_user.username} время ставки: {message.text}")
    if message.text == "⬅ НАЗАД":
        await message.reply("Главное меню", reply_markup=nav.mainMenu)
        await state.clear()
        return

    bet_time = BotFunction.convert_to_milliseconds(message.text)
    if bet_time is None:
        logger.info(f"{message.from_user.username} прислал херню.")
        await message.reply(
            "Пришлите время в нормальном формате(mm:ss.ms или ss.ms) или нажмите кнопку 'назад'",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[btnBackToMenu]]),
            input_field_placeholder="45.67 или 01:02.34",
        )
        return

    user = TelegramUser(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        full_name=message.from_user.full_name,
        language_code=message.from_user.language_code,
    )
    bet = BetTimeTelegramUser(
        tg_user=user, bet_time1=bet_time, date_bet1=datetime.now()
    )
    await state.update_data(bet=bet)
    await state.set_state(BotStates.Get_betting_sure)
    await message.reply("Это верные данные?")
    nickname = f"Nickname: {bet.tg_user.username}"
    bet_time = f"Bet time: {BotFunction.msec_to_mmssms(bet.bet_time1)}"
    bet_date = f"Bet date: {bet.date_bet1}"
    await message.answer(
        text=f"{nickname}\n{bet_time}\n{bet_date}",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ],
                [btnBackToMenu],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(BotStates.Get_betting_sure)
async def betting_r_u_sure(message: types.Message, state: FSMContext):
    if message.text == "⬅ НАЗАД":
        await message.reply("Главное меню", reply_markup=nav.mainMenu)
        await state.clear()
        return

    if message.text.lower() == "да":
        await message.answer("Спасибо, ваши данные записаны")
        bet = await state.get_data()
        DbBetTime().remove(tg_id=bet["bet"].tg_user.tg_id)
        DbBetTime().add(bet["bet"])
        await state.clear()
        await message.answer("Главное меню", reply_markup=nav.mainMenu)

    elif message.text.lower() == "нет":
        await message.reply(
            "Введите другое время:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[btnBackToMenu]], resize_keyboard=True
            ),
        )
        await state.set_state(BotStates.Get_betting_time)

    else:
        await message.answer(
            "Это верные данные? (да/нет)",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Да"),
                        KeyboardButton(text="Нет"),
                    ]
                ],
                resize_keyboard=True,
            ),
        )


@router.message(F.text == "Поменять ставку")
async def subscribe_ggp_class(message: types.Message, state: FSMContext):
    logger.info(f"Запрос изменения ставки от: {message.from_user.username}")
    await message.answer(
        "Напишите время за которое вы ожиадаете что проедет лучший спортсмен",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[btnBackToMenu]],
            resize_keyboard=True,
            input_field_placeholder="45.67 или 01:02.34",
        ),
    )
    await state.set_state(BotStates.Get_betting_time)


@router.message(F.text == "Отменить ставку")
async def cancel_bet_time(message: types.Message, state: FSMContext):
    logger.info(f"Пришла отмена ставки от: {message.from_user.username}")
    DbBetTime().remove(tg_id=message.from_user.id)
    await state.clear()
    await message.answer("Ставка отменена", reply_markup=nav.mainMenu)


@router.message(F.text == "Таблица ставок")
async def get_bet_time_table(message: types.Message, state: FSMContext):
    logger.info(f"Запрос таблицы ставок от: {message.from_user.username}")
    bet_users = DbBetTime().get(tg_id="all")
    text = "Все ставки:\n"
    for i in range(len(bet_users)):
        text += f"\t{i+1}) - {bet_users[i].tg_user.username} - {BotFunction.msec_to_mmssms(bet_users[i].bet_time1)}\n"
    await message.answer(f"Все ставки {text}", reply_markup=nav.mainMenu)
