import asyncio
import logging

from aiogram import Bot, exceptions

from aio_bot import aio_bot_functions, aio_markups as nav, config_bot

logger = logging.getLogger(__name__)


class BotMessageSender:
    def __init__(self):
        self.API_bot = config_bot.config["API_token"]
        self.bot = Bot(token=self.API_bot)

    async def send_msg(self, user_id: int, message: str, nav_menu=nav.main_menu):
        logger.info("Высылаем сообщение %s / %s", user_id, message)
        try:
            await asyncio.sleep(10)
            await self.bot.send_message(chat_id=user_id, text=message, reply_markup=nav_menu)
        except exceptions.TelegramForbiddenError:
            logger.warning("Пользователь %s заблокировал бота", user_id)
        except exceptions.TelegramBadRequest:
            logger.warning("Пользователь %s удалил бота", user_id)
        except exceptions.TelegramNotFound:
            logger.error(f"Target [ID:{user_id}]: invalid user ID")
        except exceptions.TelegramRetryAfter as e:
            logger.warning(
                "Сработала антиспам защита, потовряем запрос через %s секунд", e.retry_after
            )
            await asyncio.sleep(e.retry_after)
            await self.send_msg(user_id, message, nav_menu)

        await self.close()

    async def broadcast_msg(self, users_id: list[int], message: str):
        for user_id in users_id:
            await self.send_msg(user_id, message)

    async def close(self):
        logger.debug("Закрываем содинение сессии aiogram")
        await self.bot.session.close()
