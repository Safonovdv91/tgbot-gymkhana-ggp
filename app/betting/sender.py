from aio_bot.aio_bot_functions import BotFunction
from DB.db_obj import DbBetTime, DbStageResults
from DB.models import BetTimeTelegramUser


class BettingMessageSender:
    @staticmethod
    async def make_msg(username: str, place: int, delta_time: str) -> str:
        return f"Поздравляю {username} ты занял {place} место \n твоя разница {delta_time}"

    @staticmethod
    async def sort_by_delta_time(
        bet_users: list[BetTimeTelegramUser],
    ) -> list[BetTimeTelegramUser]:
        """Функция получаюoщая список ставок на время и сортирующая их
        по разнице времени ставки и лучшего времени
        """
        ms = DbStageResults().get_best_stage_time()

        def time_differense(user: BetTimeTelegramUser):
            user.delta_bet_time1 = abs(user.bet_time1 - ms)
            return user.delta_bet_time1

        return sorted(bet_users, key=time_differense)

    @staticmethod
    async def get_all_bets() -> str:
        bet_users = DbBetTime().get(tg_id="all")
        text = "Все ставки:\n"
        for i in range(len(bet_users)):
            text += (
                f"\t{i + 1}) - {bet_users[i].tg_user.username}"
                f" - {BotFunction.msec_to_mmssms(bet_users[i].bet_time1)}\n"
            )
        return text

    @staticmethod
    async def get_sorted_bets() -> str:
        bet_users = DbBetTime().get(tg_id="all")
        bet_users = await BettingMessageSender.sort_by_delta_time(bet_users)
        text = "Таблица ставок на время:\n"
        for i in range(len(bet_users)):
            delta_time = BotFunction.msec_to_mmssms(bet_users[i].delta_bet_time1)
            text += (
                f"\t{i + 1}) {bet_users[i].tg_user.full_name}"
                f" - {BotFunction.msec_to_mmssms(bet_users[i].bet_time1)} "
                f"[{delta_time}] | {bet_users[i].date_bet1.strftime("%Y-%m-%d %H:%M:%S")}\n"
            )
        return text
