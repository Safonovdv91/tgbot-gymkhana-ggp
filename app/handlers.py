import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from aio_bot import aio_bot_functions, aio_markups as nav, config_bot
from aio_bot.aio_bot_functions import BotFunction, BotInterface, DoBet
from aio_bot.aio_markups import btnBackToMenu
from app.betting.sender import BettingMessageSender
from app.bot_states import BotStates
from app.constants import BAD_MESSAGE, HELP_MESSAGE, START_MESSAGE
from DB import database as DBM
from DB.db_obj import DbBetTime, DbStageResults, DbTgUsers
from DB.models import BetTimeTelegramUser, TelegramUser

router = Router()
logger = logging.getLogger(__name__)


# Инициализация меню по нажатию старт
@router.message(CommandStart())
async def start_bot(message: types.Message):
    logger.info("Запустил /start %s", message.from_user.username)
    await message.answer(START_MESSAGE, reply_markup=nav.main_menu)


@router.message(Command("help"))
async def help_bot(message: types.Message):
    await message.answer(HELP_MESSAGE)


@router.message(Command("unsub"))
async def unsubscribe_bot(message: types.Message):
    """Удаляем все подписки у пользователя"""
    logger.info(
        "User unsub. Delete him.",
        extra={
            "id": message.from_user.id,
            "username": message.from_user.username,
        },
    )
    BotInterface.unsub_tguser(message.from_user.id)
    await message.answer("Прощай друг 😿")


@router.message(Command("broadcast"))
async def broadcast_message_to_all_users(message: types.Message, state: FSMContext):
    logger.info("Начал массовую рассылку %s", message.from_user.id)
    if message.from_user.id != config_bot.config["admin_id"]:
        logger.warning(
            "Несанкционированная попытка броадкаста от пользователя %s | [%s]",
            message.from_user.full_name,
            message.from_user.id,
        )
        await message.answer("Вы не являетесь админом, и не имеете возможности броадкаста")
        return
    await state.set_state(BotStates.Broadcasting)
    await message.answer("Напишите сообщение которое планируете разослать:")


@router.message(Command("list_all_users"))
async def get_all_users(message: types.Message):
    logger.info("Запросил всех пользователей %s", message.from_user.full_name)
    if message.from_user.id != config_bot.config["admin_id"]:
        logger.warning(
            "Несанкционированная попытка получения всех пользователей от ользователя %s | [%s]",
            message.from_user.full_name,
            message.from_user.id,
        )
        await message.answer("Вы не являетесь админом, и не имеете возможности броадкаста")
        return
    users = DbTgUsers().get_all_subscribers()
    text = "Все пользователи бота:\n"
    count = 0
    for user in users:
        count += 1
        text += f"{user["_id"]} "
    text += f"\nВсего {count} пользователей"
    await message.answer(text)


@router.message(BotStates.Broadcasting)
async def send_message_to_all_users(message: types.Message, state: FSMContext):
    users = DbTgUsers().get_all_subscribers()
    for user in users:
        await BotMessageSender().send_msg(
            user_id=user["_id"], message=message.text, nav_menu=nav.main_menu
        )
    await state.clear()


@router.message(F.text == "Получить 🗺 этапа")
async def send_map(message: types.Message):
    if message.text == "Получить 🗺 этапа":
        logger.info(
            "Пришел запрос карты %s",
            message.from_user.full_name,
        )
        try:
            if config_bot.config_gymchana_cup["trackUrl"]:
                track_url = (
                    f"https://gymkhana-cup.ru/competitions/special-stage?"
                    f"id={config_bot.config_gymchana_cup['id_stage_now']}"
                )
                await message.answer_photo(
                    photo=config_bot.config_gymchana_cup["trackUrl"],
                    caption=track_url,
                )
            else:
                await message.answer("Сейчас межсезонье мэн, покатай базовую фигуру")
        except Exception as e:
            logger.exception(
                "Поймано исключение при отправке карты этапа" " %s",
                message.from_user.id,
            )
            await message.answer(
                "Бро, что-то пошло не так 8'(- скорее всего сервак лежит,"
                " запроси карту попозже..."
            )
            await message.answer(
                "❗ Поймано исключение при отправке карты этапа от" " {} \n{}".format(
                    message.from_user.id, e
                )
            )


@router.message(F.text == "⌚ Сделать ставку на лучшее время GGP")
async def make_bet(message: types.Message, state: FSMContext):
    db_bet = DbBetTime().get(tg_id=message.from_user.id)
    logger.info("Начал делать ставку: %s", message.from_user.username)

    # Считываем данные о юзере
    if db_bet:
        logger.info("%s - уже есть в базе", message.from_user.username)
        user = TelegramUser(
            tg_id=db_bet["tg_user"]["tg_id"],
            username=db_bet["tg_user"]["username"],
            first_name=db_bet["tg_user"]["first_name"],
            full_name=db_bet["tg_user"]["full_name"],
            language_code=db_bet["tg_user"]["language_code"],
        )
        bet = BetTimeTelegramUser(
            tg_user=user,
            bet_time1=db_bet["bet_time1"],
            date_bet1=db_bet["date_bet1"],
        )
        nickname = f"Nickname: {bet.tg_user.username}"
        bet_time = f"Bet time: {BotFunction.msec_to_mmssms(bet.bet_time1)}"
        bet_date = f"Bet date: {bet.date_bet1}"
        text = f"{nickname}\n{bet_time}\n{bet_date}"
        if not DoBet.is_can_bet():
            await message.answer(
                "Приём ставок окончен:\nТвои данные:\n{}".format(text),
                reply_markup=nav.main_menu,
            )
            text = await BettingMessageSender.get_sorted_bets()
            if text:
                await message.answer(text, reply_markup=nav.main_menu)
            await state.clear()
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
        await state.set_state(BotStates.Doing_bet)
    else:
        logger.info("Делает новую ставку %s", message.from_user.username)
        if not DoBet.is_can_bet():
            await message.answer(
                "Приём ставок окончен, к сожалению ты не успел, "
                "попробуй на следующем этапе, "
                "приём ставки на время длится 1 неделю с момента начала этапа.",
                reply_markup=nav.main_menu,
            )
            return
        await message.answer(
            "Напишите время за которое вы ожиадаете что проедет"
            " лучший спортсмен\n"
            "Приём результата до {}".format(config_bot.config_gymchana_cup["end_bet_time"]),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[btnBackToMenu]],
                resize_keyboard=True,
                input_field_placeholder="45.67 или 01:02.34",
            ),
        )
        await state.set_state(BotStates.Get_betting_time)


@router.message(F.text == "Подписаться")
async def subscribe_ggp_class(message: types.Message, state: FSMContext):
    logger.info("Начал подписываться на классы: %s", message.from_user.username)
    await state.set_state(BotStates.GGP_CLASS_SUBSCRIBE)
    await subscribe_ggp(message, state)
    await message.answer(
        "Выбери на какой класс подписаться",
        reply_markup=nav.SubscriberMenu().subscriber_menu_btn(message.from_user.id),
    )


@router.message(BotStates.GGP_CLASS_SUBSCRIBE)
async def subscribe_ggp(message: types.Message, state: FSMContext):
    if message.text == "⬅ НАЗАД":
        await message.answer(
            "Главное меню",
            reply_markup=nav.main_menu,
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
        await message.answer("Главное меню", reply_markup=nav.main_menu)

    elif message.text == "Получить 🕗 этапа":
        logger.info("Запросил карту %s", message.from_user.username)
        if config_bot.config_gymchana_cup["trackUrl"] is False:
            await message.answer("На данный момент ещё нет ни одного результата")
            return
        b_result = DbStageResults().get_best_stage_time()
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
                await message.answer(text, reply_markup=nav.main_menu)
            else:
                await message.answer(
                    BAD_MESSAGE,
                    reply_markup=nav.main_menu,
                )
        except TypeError:
            logger.warning(
                "User: %s [%s] прислал не число.",
                message.from_user.username,
                message.from_user.id,
            )
            await message.answer(
                BAD_MESSAGE,
                reply_markup=nav.main_menu,
            )
        except Exception:
            logger.exception("Common error:")
            await message.answer(
                BAD_MESSAGE,
                reply_markup=nav.main_menu,
            )


class BotMessageSender:
    def __init__(self):
        self.API_bot = config_bot.config["API_token"]
        self.bot = Bot(token=self.API_bot)

    async def send_msg(self, user_id: int, message: str, nav_menu=nav.main_menu):
        logger.info("Высылаем сообщение %s / %s", user_id, message)
        try:
            await self.bot.send_message(chat_id=user_id, text=message, reply_markup=nav_menu)
        except Exception:
            logger.exception("Ошибка при массовой рассылке сообщений")
        await self.close()

    async def broadcast_msg(self, users_id: list[int], message: str):
        for user_id in users_id:
            await self.send_msg(user_id, message)

    async def close(self):
        logger.debug("Закрываем содинение сессии aiogram")
        await self.bot.session.close()
