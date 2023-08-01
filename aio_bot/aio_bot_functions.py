import logging
from typing import Any
from DB.db_obj import DbTgUsers, DbSubsAtheleteClass


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
    def msec_to_mmssms(milliseconds: int):
        """ Проверка milliseconds на верный вход данных
        """
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
        mmssms_format: str = "{:02d}:{:02d}.{:03d}".format(minutes, seconds, milliseconds)
        return mmssms_format

    def make_calculate_text(self, best_time_ms: (int, float)):
        """ Генерируем исходящее сообщение
        """
        text = f'🟦 🇧: {self.msec_to_mmssms(best_time_ms)} - {self.msec_to_mmssms(best_time_ms * 1.05 - 1)} \n' \
               f'🟩 С1: {self.msec_to_mmssms(best_time_ms * 1.05)} - {self.msec_to_mmssms(best_time_ms * 1.10 - 1)} \n' \
               f'🟩 С2: {self.msec_to_mmssms(best_time_ms * 1.10)} - {self.msec_to_mmssms(best_time_ms * 1.15 - 1)} \n' \
               f'🟩 С3: {self.msec_to_mmssms(best_time_ms * 1.15)} - {self.msec_to_mmssms(best_time_ms * 1.20 - 1)} \n' \
               f'🟨 D1: {self.msec_to_mmssms(best_time_ms * 1.20)} - {self.msec_to_mmssms(best_time_ms * 1.30 - 1)} \n' \
               f'🟨 D2: {self.msec_to_mmssms(best_time_ms * 1.30)} - {self.msec_to_mmssms(best_time_ms * 1.40 - 1)} \n' \
               f'🟨 D3: {self.msec_to_mmssms(best_time_ms * 1.40)} - {self.msec_to_mmssms(best_time_ms * 1.50 - 1)} \n' \
               f'🟨 D4: {self.msec_to_mmssms(best_time_ms * 1.50)} - {self.msec_to_mmssms(best_time_ms * 1.60 - 1)} '
        return text


class BotInterface:
    @staticmethod
    def unsub_tguser(tg_user_id):
        for athelete_class in DbSubsAtheleteClass.ATHELETE_CLASSES:
            try:
                DbSubsAtheleteClass().remove_subscriber(athelete_class, tg_user_id)
            except ValueError:
                pass
            except Exception as e:
                logging.exception(f"BotInterface: {e}")
        DbTgUsers().remove_tg_subscriber(tg_user_id)
        logging.info(f"Deleting success")


def main():
    pass


if __name__ == "__main__":
    main()
