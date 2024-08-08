import unittest

from DB.models import TelegramUser, BetTimeTelegramUser
from aio_bot.aio_bot_functions import BetTime, BotFunction
from DB.db_obj import DbBetTime


class TestBetTime(unittest.TestCase, BetTime):
    tguser = TelegramUser(
        1120145735, "novik0ff954", "Pavel", "Pavel Novikov", "ru", "@novik0ff954"
    )

    def test_receive_integer(self):
        bet1 = BetTime(self.tguser, 10)
        self.assertEqual(bet1.bet_time_ms, 10)
        bet1.bet_time_ms = 20
        self.assertEqual(bet1.bet_time_ms, 20)

    def test_receive_string(self):
        bet1 = BetTime(self.tguser, "10")
        self.assertEqual(bet1.bet_time_ms, 10)
        bet1.bet_time_ms = "20"
        self.assertEqual(bet1.bet_time_ms, 20)

    def test_receive_bellow_zero(self):
        bet1 = BetTime(self.tguser, 10)
        with self.assertRaises(ValueError):
            bet1 = BetTime(self.tguser, "-10")
        with self.assertRaises(ValueError):
            bet1 = BetTime(self.tguser, -10)
        with self.assertRaises(ValueError):
            bet1.bet_time_ms = -10
        with self.assertRaises(ValueError):
            bet1.bet_time_ms = "-10"

    def test_receive_not_to_int(self):
        bet1 = BetTime(self.tguser, "10")
        with self.assertRaises(TypeError):
            bet1.bet_time_ms = []
            bet1.bet_time_ms = {}
            bet1.bet_time_ms = "asd"
        with self.assertRaises(TypeError):
            BetTime(self.tguser, [])
            BetTime(self.tguser, {})
            BetTime(self.tguser, "asdq")


class TestTotalizator(unittest.TestCase, DbBetTime):
    user1 = TelegramUser(
        1120145735, "novik0ff954", "Pavel", "Pavel Novikov", "ru", "@novik0ff954"
    )
    user2 = TelegramUser(987654321, "johndoe", "John", "John Doe", "en", "@johndoe")
    user3 = TelegramUser(123456789, "alice", "Alice", "Alice Smith", "en", "@alice")
    user4 = TelegramUser(555555555, "bob", "Bob", "Bob Johnson", "en", "@bob")
    user5 = TelegramUser(999999999, "emma", "Emma", "Emma Thompson", "en", "@emma")

    user1_bet = BetTimeTelegramUser(user1, 45_000)
    user2_bet = BetTimeTelegramUser(user2, 50_000)
    user3_bet = BetTimeTelegramUser(user3, 55_000)
    user4_bet = BetTimeTelegramUser(user4, 60_000)
    user5_bet = BetTimeTelegramUser(user5, 65_000)

    def test_closest_number(self):
        numbers = [10, 20, 30, 40, 50]
        bet = 35
        closest = BotFunction.find_closest_number(numbers, bet)
        self.assertEqual(closest, 30)
