import logging
from datetime import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from aio_bot import aio_markups as nav, config_bot
from aio_bot.aio_bot_functions import BotFunction
from aio_bot.aio_markups import btnBackToMenu
from app.betting.sender import BettingMessageSender
from app.bot_states import BotStates
from app.handlers import BotMessageSender
from DB.db_obj import DbBetTime
from DB.models import BetTimeTelegramUser, TelegramUser

router = Router()
logger = logging.getLogger(__name__)


@router.message(BotStates.Get_betting_time)
async def betting_take_time(message: types.Message, state: FSMContext):
    logger.debug("%s время ставки: %s", message.from_user.username, message.text)
    if message.text == "⬅ НАЗАД":
        await message.reply("Главное меню", reply_markup=nav.main_menu)
        await state.clear()
        return

    bet_time = BotFunction.convert_to_milliseconds(message.text)
    if bet_time is None:
        logger.info("%s прислал херню.", message.from_user.username)
        await message.reply(
            "Пришлите время в нормальном формате(mm:ss.ms или ss.ms) или нажмите кнопку 'назад'",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[btnBackToMenu]], resize_keyboard=True),
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
    bet = BetTimeTelegramUser(tg_user=user, bet_time1=bet_time, date_bet1=datetime.now())
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
        await message.reply("Главное меню", reply_markup=nav.main_menu)
        await state.clear()
        return

    if message.text.lower() == "да":
        await message.answer("Спасибо, ваши данные записаны")
        bet = await state.get_data()
        DbBetTime().remove(tg_id=bet["bet"].tg_user.tg_id)
        DbBetTime().add(bet["bet"])
        await state.clear()
        await message.answer("Главное меню", reply_markup=nav.main_menu)

    elif message.text.lower() == "нет":
        await message.reply(
            "Введите другое время:",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[btnBackToMenu]], resize_keyboard=True),
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


@router.message(BotStates.Doing_bet, F.text == "Поменять ставку")
async def subscribe_ggp_class(message: types.Message, state: FSMContext):
    logger.info("Запрос изменения ставки от: %s", message.from_user.username)
    await message.answer(
        "Напишите время за которое вы ожиадаете что проедет лучший спортсмен",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[btnBackToMenu]],
            resize_keyboard=True,
            input_field_placeholder="45.67 или 01:02.34",
        ),
    )
    await state.set_state(BotStates.Get_betting_time)


@router.message(BotStates.Doing_bet, F.text == "Отменить ставку")
async def cancel_bet_time(message: types.Message, state: FSMContext):
    logger.info("Пришла отмена ставки от: %s", message.from_user.username)
    DbBetTime().remove(tg_id=message.from_user.id)
    await state.clear()
    await message.answer("Ставка отменена", reply_markup=nav.main_menu)


@router.message(F.text == "Таблица ставок")
async def get_bet_time_table(message: types.Message, state: FSMContext):
    logger.info("Запрос таблицы ставок от: %s", message.from_user.username)
    text = await BettingMessageSender.get_all_bets()
    await message.answer(f"Все ставки {text}", reply_markup=nav.main_menu)


@router.message(F.text == "s")
async def broadcast_bet_message(message: types.Message):
    logger.info("Рассылка массовых уведомлений %s", message.from_user.username)
    if message.from_user.id == config_bot.config["admin_id"]:
        text = await BettingMessageSender.get_sorted_bets()
        users = DbBetTime().get(tg_id="all")
        users = await BettingMessageSender.sort_by_delta_time(users)
        for i in range(len(users)):
            if i < 3:
                delta_time = BotFunction.msec_to_mmssms(users[i].delta_bet_time1)
                msg = (
                    f"Поздравляю {users[i].tg_user.full_name} ты попал в тройку лидеров предсказателей времени!\n "
                    f"Твое место: {i+1} !\n "
                    f"Не угадал всего лишь на: {delta_time}\n"
                )
            else:
                delta_time = BotFunction.msec_to_mmssms(users[i].delta_bet_time1)
                msg = (
                    f"Поздравляю {users[i].tg_user.first_name} попытался угадать время и почти угадал:\n "
                    f"Твое место: {i+1}!\n "
                    f"Не угадал всего лишь на: {delta_time}\n"
                )
            await BotMessageSender().send_msg(users[i].tg_user.tg_id, msg)
            await BotMessageSender().send_msg(users[i].tg_user.tg_id, text)
        await message.answer(f"Сообщение разослано по {users}")
