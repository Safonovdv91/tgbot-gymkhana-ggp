import math


class BotFunction:

    def convert_to_milliseconds(self, mmssms: [float, str]) -> int:
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


    def milliseconds_to_mmssms(self, milliseconds):
        # Проверка milliseconds на верный вход данных
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

    def make_calculate_text(self, best_time_ms):
        # Генерируем исходящее сообщение
        text = f'🟦 🇧: {self.milliseconds_to_mmssms(best_time_ms)} - {self.milliseconds_to_mmssms(best_time_ms*1.05 - 1)} \n'\
        f'🟩 С1: {self.milliseconds_to_mmssms(best_time_ms*1.05)} - {self.milliseconds_to_mmssms(best_time_ms * 1.10 - 1)} \n' \
        f'🟩 С2: {self.milliseconds_to_mmssms(best_time_ms * 1.10)} - {self.milliseconds_to_mmssms(best_time_ms * 1.15 - 1)} \n' \
        f'🟩 С3: {self.milliseconds_to_mmssms(best_time_ms*1.15)} - {self.milliseconds_to_mmssms(best_time_ms * 1.20 - 1)} \n' \
        f'🟨 D1: {self.milliseconds_to_mmssms(best_time_ms*1.20)} - {self.milliseconds_to_mmssms(best_time_ms * 1.30 - 1)} \n' \
        f'🟨 D2: {self.milliseconds_to_mmssms(best_time_ms * 1.30)} - {self.milliseconds_to_mmssms(best_time_ms * 1.40 - 1)} \n' \
        f'🟨 D3: {self.milliseconds_to_mmssms(best_time_ms * 1.40)} - {self.milliseconds_to_mmssms(best_time_ms * 1.50 - 1)} \n' \
        f'🟨 D4: {self.milliseconds_to_mmssms(best_time_ms * 1.50)} - {self.milliseconds_to_mmssms(best_time_ms * 1.60 - 1)} '
        return text


def main():
    pass

if __name__ == "__main__":
    main()
