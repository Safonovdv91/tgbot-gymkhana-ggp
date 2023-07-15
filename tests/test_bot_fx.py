import unittest
import sys, os

sys.path.append(os.getcwd())
print(os.getcwd())

from aio_bot.aio_bot_functions import *

class TestBotFunctionsSpendBestTime(unittest.TestCase):

    def test_time_to_string_milliSeconds(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(100), "00:00.100")
        self.assertEqual(test.milliseconds_to_mmssms(500), "00:00.500")
        self.assertEqual(test.milliseconds_to_mmssms(150), "00:00.150")
        self.assertEqual(test.milliseconds_to_mmssms(600), "00:00.600")
        self.assertEqual(test.milliseconds_to_mmssms(990), "00:00.990")
        self.assertEqual(test.milliseconds_to_mmssms(2), "00:00.002")

    def test_time_to_string_Seconds(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(1000), "00:01.000")
        self.assertEqual(test.milliseconds_to_mmssms(5000), "00:05.000")
        self.assertEqual(test.milliseconds_to_mmssms(10000), "00:10.000")
        self.assertEqual(test.milliseconds_to_mmssms(20000), "00:20.000")
        self.assertEqual(test.milliseconds_to_mmssms(50000), "00:50.000")
        self.assertEqual(test.milliseconds_to_mmssms(55000), "00:55.000")

    def test_time_to_string_Seconds_and_milliSeconds(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(50_010), "00:50.010")
        self.assertEqual(test.milliseconds_to_mmssms(30_050), "00:30.050")
        self.assertEqual(test.milliseconds_to_mmssms(30_002), "00:30.002")


    def test_time_to_string_Minutes(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(60_000), "01:00.000")
        self.assertEqual(test.milliseconds_to_mmssms(120_000), "02:00.000")

    def test_time_to_string_Minutes_and_MilliSeconds(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(60_010), "01:00.010")
        self.assertEqual(test.milliseconds_to_mmssms(120_050), "02:00.050")

    def test_time_to_string_Minutes_and_Seconds_MilliSeconds(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(61_010), "01:01.010")
        self.assertEqual(test.milliseconds_to_mmssms(75_010), "01:15.010")
        self.assertEqual(test.milliseconds_to_mmssms(85_050), "01:25.050")
        self.assertEqual(test.milliseconds_to_mmssms(85_005), "01:25.005")

class TestMilliSecondsMmssmsIntoWrongType(unittest.TestCase):

    def test_input_string(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms('61010'), "01:01.010")
        self.assertEqual(test.milliseconds_to_mmssms('75010'), "01:15.010")

    def test_input_alphastring(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms("446sa"), None)

    def test_input_tuple(self):
        test = BotFunction()
        self.assertEqual(test.milliseconds_to_mmssms(('__', 'sda', 123)), None)
        self.assertEqual(test.milliseconds_to_mmssms([123, 223]), None)
        self.assertEqual(test.milliseconds_to_mmssms({123: 223}), None)


class TestMMSSMsToMilliseconds(unittest.TestCase):

    def test_right_result(self):
        botfx = BotFunction()

        self.assertEqual(botfx.convert_to_milliseconds("00:45.567"), 45567)
        self.assertEqual(botfx.convert_to_milliseconds("01:05.567"), 65567)
        self.assertEqual(botfx.convert_to_milliseconds("01:05.560"), 65560)
        self.assertEqual(botfx.convert_to_milliseconds("01:05.56"), 65560)
        self.assertEqual(botfx.convert_to_milliseconds("00:45.56"), 45560)

    def test_receive_only_seconds_and_ms(self):
        botfx = BotFunction()

        self.assertEqual(botfx.convert_to_milliseconds("45.567"), 45567)
        self.assertEqual(botfx.convert_to_milliseconds("30.567"), 30567)
        self.assertEqual(botfx.convert_to_milliseconds("30.56"), 30560)
        self.assertEqual(botfx.convert_to_milliseconds("30.506"), 30506)
        self.assertEqual(botfx.convert_to_milliseconds("3.506"), 3506)

    def test_receive_only_seconds(self):
        botfx = BotFunction()

        self.assertEqual(botfx.convert_to_milliseconds("45"), 45000)
        self.assertEqual(botfx.convert_to_milliseconds("30"), 30000)
        self.assertEqual(botfx.convert_to_milliseconds("05"), 5000)
        self.assertEqual(botfx.convert_to_milliseconds("5"), 5000)

    def test_receive_char(self):
        botfx = BotFunction()

        self.assertEqual(botfx.convert_to_milliseconds("4sd"), None)
        self.assertEqual(botfx.convert_to_milliseconds("45.s23"), None)
        self.assertEqual(botfx.convert_to_milliseconds("c2:245.12"), None)

    def test_receive_float(self):
        botfx = BotFunction()

        self.assertEqual(botfx.convert_to_milliseconds(45.56), 45560)
        self.assertEqual(botfx.convert_to_milliseconds(45), 45000)