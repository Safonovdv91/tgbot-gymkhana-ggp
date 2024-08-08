import logging

from dataclasses import dataclass
from typing import Any
from DB.db_obj import DbTgUsers, DbSubsAtheleteClass, DbBetTime
from DB.models import TelegramUser, BetTimeTelegramUser

logger = logging.getLogger("app.app_func")


class BotFunction:
    @staticmethod
    def convert_to_milliseconds(mmssms: [float, str]) -> int | None | Any:
        """Метод преобразования в миллисекунды
        получает форматы:
        01:02.563 = 62563
        02.563 = 2563
        45 = 45000
        """
        minutes: int
        seconds: float
        try:
            if type(mmssms) is float or type(mmssms) is int:
                return mmssms * 1_000
            mmssms = mmssms.split(":")
            if len(mmssms) == 1:
                minutes = 0
                seconds = float(mmssms[0])
            else:
                minutes = int(mmssms[0])
                seconds = float(mmssms[1])
        except ValueError:
            minutes = 0
            try:
                seconds = float(mmssms[0])
            except ValueError:
                return None
        return int(seconds * 1_000) + minutes * 60_000

    @staticmethod
    def msec_to_mmssms(milliseconds: int | str):
        """Проверка milliseconds на верный вход данных"""
        try:
            milliseconds = int(milliseconds)
        except ValueError:
            return None
        except TypeError:
            return None

        # Разделение миллисекунд на минуты, секунды и миллисекунды
        minutes, milliseconds = divmod(milliseconds, 60_000)
        seconds, milliseconds = divmod(milliseconds, 1_000)
        # Форматирование в строку в формате "минуты:секунды.миллисекунды"
        mmssms_format: str = "{:02d}:{:02d}.{:03d}".format(
            minutes, seconds, milliseconds
        )
        return mmssms_format

    def make_calculate_text(self, best_time_ms: (int, float)):
        """Генерируем исходящее сообщение"""
        text = (
            f"🟦 🇧: {self.msec_to_mmssms(best_time_ms)} - {self.msec_to_mmssms(best_time_ms * 1.05 - 1)} \n"
            f"🟩 С1: {self.msec_to_mmssms(best_time_ms * 1.05)} - {self.msec_to_mmssms(best_time_ms * 1.10 - 1)} \n"
            f"🟩 С2: {self.msec_to_mmssms(best_time_ms * 1.10)} - {self.msec_to_mmssms(best_time_ms * 1.15 - 1)} \n"
            f"🟩 С3: {self.msec_to_mmssms(best_time_ms * 1.15)} - {self.msec_to_mmssms(best_time_ms * 1.20 - 1)} \n"
            f"🟨 D1: {self.msec_to_mmssms(best_time_ms * 1.20)} - {self.msec_to_mmssms(best_time_ms * 1.30 - 1)} \n"
            f"🟨 D2: {self.msec_to_mmssms(best_time_ms * 1.30)} - {self.msec_to_mmssms(best_time_ms * 1.40 - 1)} \n"
            f"🟨 D3: {self.msec_to_mmssms(best_time_ms * 1.40)} - {self.msec_to_mmssms(best_time_ms * 1.50 - 1)} \n"
            f"🟨 D4: {self.msec_to_mmssms(best_time_ms * 1.50)} - {self.msec_to_mmssms(best_time_ms * 1.60 - 1)} "
        )
        return text

    @staticmethod
    def find_closest_number(numbers, bet):
        closest_number = None
        min_difference = float(
            "inf"
        )  # Инициализируем минимальную разницу как бесконечность

        for number in numbers:
            difference = abs(
                number - bet
            )  # Вычисляем разницу между числом из списка и bet
            if difference < min_difference:
                min_difference = difference
                closest_number = number
        return closest_number


class BotInterface:
    @staticmethod
    def unsub_tguser(tg_user_id):
        """Удаление подписчика из БД"""
        for athelete_class in DbSubsAtheleteClass.ATHELETE_CLASSES:
            try:
                DbSubsAtheleteClass().remove_subscriber(athelete_class, tg_user_id)
            except ValueError:
                pass
            except Exception as e:
                logging.exception(f"BotInterface: {e}")
        DbTgUsers().remove_tg_subscriber(tg_user_id)
        logging.info("Deleting success")


class BotTotalizator:
    pass


class DoBet:
    @staticmethod
    def do_bet(message, time):
        tg_user = TelegramUser(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.full_name,
            message.from_user.language_code,
        )
        try:
            time_ms = BotFunction.convert_to_milliseconds(time[4:])
            bet_ss = BetTimeTelegramUser(tg_user, time_ms)
        except (TypeError, ValueError):
            msg = "Пришли сообщение в формате:\n" "/bet 01:02.563 или /bet 42.563"
            return msg

        if DbBetTime().add(bet_ss) is None:
            msg = "А всё, ставка уже принята"
            msg = f"{msg}\n {DoBet.get_my_bet(message)}"
            return msg
        mmssmm = BotFunction.msec_to_mmssms(time_ms)
        msg = f"Ваша ставка {tg_user.full_name} на время принята: {mmssmm}"
        return msg

    @staticmethod
    def get_my_bet(message):
        db_object = DbBetTime().get(message.from_user.id)
        if db_object is None:
            return (
                "Вы ещё не сделали ставку, чтобы её сделать напиши /bet ваше время\n"
                "например: /bet 45.38, /bet 1:07.13 "
            )
        mmssmm = BotFunction.msec_to_mmssms(db_object["bet_time1"])
        date = db_object["date_bet1"]
        year = date.year
        month = date.month
        day = date.day
        h = date.hour
        m = date.minute
        msg = (
            f"Ваша ставка на лучшее время:\n"
            f" {year}-{month:02d}-{day} {h}:{m} - {mmssmm}"
        )
        return msg


@dataclass()
class BetTime:
    def __init__(self, tg_user: TelegramUser, bet_time_ms: int | str):
        self.bet_time_ms = bet_time_ms

    @property
    def bet_time_ms(
        self,
    ):
        return self._bet_time_ms

    @bet_time_ms.setter
    def bet_time_ms(self, bet_time: int):
        try:
            bet_time = int(bet_time)
        except TypeError:
            raise TypeError("Значение должно быть целым числом")
        if bet_time <= 0:
            raise ValueError("Значение должно быть больше нуля")
        self._bet_time_ms = bet_time


def main():
    pass


if __name__ == "__main__":
    main()
