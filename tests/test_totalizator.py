import unittest
from aio_bot.aio_bot_functions import BetTime


class TestBetTime(unittest.TestCase, BetTime):
    tguser = "test_user"

    def test_receive_integer(self):
        tguser = "test_user"
        bet1 = BetTime(tguser, 10)
        self.assertEqual(bet1.bet_time_ms, 10)
        bet1.bet_time_ms = 20
        self.assertEqual(bet1.bet_time_ms, 20)

    def test_receive_string(self):
        tguser = "test_user"
        bet1 = BetTime(tguser, "10")
        self.assertEqual(bet1.bet_time_ms, 10)
        bet1.bet_time_ms = "20"
        self.assertEqual(bet1.bet_time_ms, 20)

    def test_receive_bellow_zero(self):
        tguser = "test_user"
        bet1 = BetTime(tguser, 10)
        with self.assertRaises(ValueError):
            bet1 = BetTime(tguser, "-10")
        with self.assertRaises(ValueError):
            bet1 = BetTime(tguser, -10)
        with self.assertRaises(ValueError):
            bet1.bet_time_ms = -10
        with self.assertRaises(ValueError):
            bet1.bet_time_ms = "-10"

    def test_receive_not_to_int(self):
        tguser = "test_user"
        bet1 = BetTime(tguser, "10")
        with self.assertRaises(TypeError):
            bet1.bet_time_ms = []
            bet1.bet_time_ms = {}
            bet1.bet_time_ms = "asd"
        with self.assertRaises(TypeError):
            bet1 = BetTime(tguser, [])
            bet1 = BetTime(tguser, {})
            bet1 = BetTime(tguser, "asdq")




