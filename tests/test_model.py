import unittest
from DB.models import Subscriber, StageSubscribers, StageSportsmanResult


class TestModelSportsmanStage(unittest.TestCase):
    test_result = StageSportsmanResult(123, "Pavukov", "Raptor", "Smolensk",
                                       "Russia", "C2", 66666, "01:01.66", 666, "https:/666.com")

    def test_good_setter(self):
        test_result = StageSportsmanResult(123, "Pavukov", "Raptor", "Smolensk",
                                           "Russia", "C2", 66666, "01:01.66", 666,  "https:/666.com")

        self.assertEqual(test_result.sportsman_id, 123)
        self.assertEqual(test_result.user_full_name, "Pavukov")
        self.assertEqual(test_result.motorcycle, "Raptor")
        self.assertEqual(test_result.user_city, "Smolensk")
        self.assertEqual(test_result.user_country, "Russia")
        self.assertEqual(test_result.athlete_class, "C2")
        self.assertEqual(test_result.result_time_seconds, 66666)
        self.assertEqual(test_result.result_time, "01:01.66")
        self.assertEqual(test_result.fine, 666)
        self.assertEqual(test_result.video, "https:/666.com")

    def test_raise_bad_id(self):
        " Плохой id"
        test_result = StageSportsmanResult(123, "Pavukov", "Raptor", "Smolensk",
                                           "Russia", "C2", 66666, "01:01.66", 666,  "https:/666.com")
        with self.assertRaises(TypeError):
            test_result.sportsman_id = "123"

        with self.assertRaises(TypeError):
            test_result = StageSportsmanResult("123", "Pavukov", "Raptor", "Smolensk",
                                               "Russia", "C2", 66666, "01:01.66", 666, "https:/666.com")
        with self.assertRaises(AttributeError):
            test_result.sportsman_id = -66666

        with self.assertRaises(AttributeError):
            test_result = StageSportsmanResult(-112, "Pavukov", "Raptor", "Smolensk",
                                               "Russia", "C2", 66666, "01:01.66", 666, "https:/666.com")

    def test_raise_bad_time(self):
        " Плохое время"
        test_result = self.test_result

        with self.assertRaises(TypeError):
            test_result.result_time_seconds = "66666"

        with self.assertRaises(TypeError):
            test_result = StageSportsmanResult(123, "Pavukov", "Raptor", "Smolensk",
                                               "Russia", "C2", "66666", "01:01.66", 666, "https:/666.com")
        with self.assertRaises(AttributeError):
            test_result.result_time_seconds = -66666

        with self.assertRaises(AttributeError):
            test_result = StageSportsmanResult(123, "Pavukov", "Raptor", "Smolensk",
                                               "Russia", "C2", -66666, "01:01.66", 666, "https:/666.com")

    def test_raise_bad_fine(self):
        " Не цифра пенальти"
        test_result = self.test_result

        with self.assertRaises(TypeError):
            test_result.result_time_seconds = "666"

        with self.assertRaises(TypeError):
            test_result = StageSportsmanResult("123", "Pavukov", "Raptor", "Smolensk",
                                               "Russia", "C2", 66666, "01:01.66", "666", "https:/666.com")

        with self.assertRaises(AttributeError):
            test_result.fine = -66666

        with self.assertRaises(AttributeError):
            test_result = StageSportsmanResult(123, "Pavukov", "Raptor", "Smolensk",
                                               "Russia", "C2", 66666, "01:01.66", -666, "https:/666.com")


class TestModelSubscriber(unittest.TestCase):
    tester = Subscriber(123, False, set())

    def test_good_setter(self):
        tester = self.tester

        self.assertEqual(tester.subscriber_id, 123)
        tester.subscriber_id = 100

        self.assertEqual(tester.subscriber_id, 100)

    def test_bad_id_setter(self):
        tester = self.tester

        with self.assertRaises(AttributeError):
            tester.subscriber_id = -123
            self.assertEqual(tester.subscriber_id, -123)

        with self.assertRaises(AttributeError):
            tester.subscriber_id = -100

    def test_good_stage_setter(self):
        tester = self.tester

        tester.sub_stage_categories = {"C1", "C2"}
        self.assertEqual(tester.sub_stage_categories, {"C1", "C2"})


class TestStageSubscribers(unittest.TestCase):

    def test_create_athelete_class(self):
        test_stage = StageSubscribers("C1", {124512})

        test_stage.athlete_class = "C2"
        self.assertEqual(test_stage.athlete_class, "C2")

        test_stage.subscribers_id = {1234125, 1241512}
        self.assertEqual(test_stage.subscribers_id, {1234125, 1241512})

    def test_raises_bad_class(self):
        with self.assertRaises(TypeError):
            test_stage = StageSubscribers([], {124512})

        with self.assertRaises(TypeError):
            test_stage = StageSubscribers("C1", "512")

        test_stage = StageSubscribers("C1", {124512})

        with self.assertRaises(TypeError):
            test_stage.subscribers_id = "sda"

        with self.assertRaises(TypeError):
            test_stage.athlete_class = 123

    def test_add_new_subscriber(self):
        test_stage = StageSubscribers("C1", {12345})
        test_stage.add_subscriber(1112)
        test_stage.add_subscriber(1111)
        self.assertEqual(test_stage.subscribers_id, {12345, 1111, 1112})

    def test_add_new_subscriber_LongId(self):
        test_stage = StageSubscribers("C1", {12345123451234512345})
        test_stage.add_subscriber(11122222222414124152412312312312512)
        self.assertEqual(test_stage.subscribers_id, {12345123451234512345, 11122222222414124152412312312312512})

    def test_remove_subscriber(self):
        test_stage = StageSubscribers("C1", {12345})
        test_stage.add_subscriber(1111)
        self.assertEqual(test_stage.subscribers_id, {12345, 1111})
        test_stage.removed_subscriber(12345)
        self.assertEqual(test_stage.subscribers_id, {1111})
        test_stage.removed_subscriber(1111)
        self.assertEqual(test_stage.subscribers_id, set())

    def test_unknown_subscriber(self):
        test_stage = StageSubscribers("C1", {12345})
        with self.assertRaises(AttributeError):
            test_stage.removed_subscriber(124151)

