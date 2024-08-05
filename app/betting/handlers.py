import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.bot_states import BotStates
from aio_bot import aio_markups as nav

router = Router()
logger = logging.getLogger("handlers")

# @router.message()
# async def take_bet(message: types.Message, state: FSMContext) -> None:
#     """Анализ сообщения для подписки"""
#     print("Пришла ставка")
#     await message.answer(text="Hello")
#     await state.set_state(BotStates.Wager)


# @router.message()
# async def take_bet2(state: BotStates.Wager) -> None:
#     """Анализ сообщения для подписки"""
#     print("Пришла ставка ещё")
#     await state.set_state(BotStates.Wager)

COMAND = "💰 Сделать ставку"


@router.message(BotStates.Get_betting_nickname)
async def betting_take_nickname(message: types.Message, state: FSMContext) -> None:
    nickname = message.text
    await state.update_data(nickname=nickname)
    await state.set_state(BotStates.Get_betting_time)
    await message.answer("Напиши время за которые ты ожидаешь что будет проехан этап!")


@router.message(BotStates.Get_betting_time)
async def betting_take_time(message: types.Message, state: FSMContext):
    time = message.text
    await state.update_data(time=time)
    await state.set_state(BotStates.Get_betting_sure)
    await message.reply("Это верные данные?")
    data = await state.get_data()
    await message.answer(
        text=f"{data}",
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


@router.message(BotStates.Get_betting_sure)
async def betting_r_u_sure(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await message.answer("Спасибо, ваши данные записаны")
        await state.clear()
        await message.answer("Главное меню", reply_markup=nav.mainMenu)
    elif message.text.lower() == "нет":
        await message.answer("Введите никнейм:")
        await state.set_state(BotStates.Get_betting_nickname)
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
