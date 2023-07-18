import random
import unittest
from unittest.mock import patch
from DB.db_obj import DbTgUsers, DbStageResults
from mongomock import MongoClient as MockMonkClient


class Mock(DbTgUsers):
    def __init__(self):
        super().__init__()
        self.connection = MockMonkClient()
        current_db = self.connection["test_db"]
        self.collection = current_db["test_collection"]


class MockDbStage(DbStageResults):
    def __init__(self):
        super().__init__()
        self.connection = MockMonkClient()
        current_db = self.connection["test_db"]
        self.collection = current_db["test_collection"]


class TestDbTgUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.db = DbTgUsers()
        cls.db = Mock()
        cls.test_user_id = random.randint(1, 10000000)

    def test_add_tg_subscriber(self):
        # Проверяем добавление нового подписчика
        result = self.db.add_tg_subscriber(self.test_user_id)
        self.assertTrue(result)

        # Проверяем повторное добавление существующего подписчика
        result = self.db.add_tg_subscriber(self.test_user_id)
        self.assertFalse(result)

    def test_get_tg_subscriber(self):
        # Проверяем получение существующего подписчика
        self.db.add_tg_subscriber(self.test_user_id)
        subscriber = self.db.get_tg_subscriber(self.test_user_id)

        self.assertIsNotNone(subscriber)
        self.assertEqual(subscriber["_id"], self.test_user_id)

        # Проверяем получение несуществующего подписчика
        subscriber = self.db.get_tg_subscriber(1234)
        self.assertIsNone(subscriber)


class TestDbStageResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # cls.db = DbStageResults()
        cls.db = MockDbStage()
        cls.test_result = {
            "userId": 2,
            "userFullName": "2",
            "motorcycle": "3",
            "userCity": "city",
            "userCountry": "country",
            "athleteClass": "class",
            "resultTimeSeconds": "resTime",
            "resultTime": 124,
            "fine": "fine",  # пенальти
            "video": "href"
        }

    def test_add(self):
        " Проверяем добавление результата"
        result = self.db.add(self.test_result)
        self.assertTrue(result)

    def test_del_result(self):
        "Проверяем удаление существующего результата"
        result = self.db.del_result(self.test_result["userId"])
        self.assertTrue(result)

        # Проверяем удаление несуществующего результата
        result = self.db.del_result(1234)
        self.assertTrue(result)  # Удаление несуществующего результата также считается успешным

    def test_get(self):
        " Проверяем получение существующего результата"
        user = self.test_result
        self.db.add(user)
        self.assertEqual(self.db.get(user["userId"])["_id"], user["userId"])

        # Проверяем получение несуществующего результата
        result = self.db.get(1234)
        self.assertIsNone(result)

    def test_update(self):
        " Обновление результата"
        user = self.test_result
        self.db.add(user)

        new_result = {
            "userId": 2,
            "userFullName": "20",
            "motorcycle": "30",
            "userCity": "city0",
            "userCountry": "country0",
            "athleteClass": "class0",
            "resultTimeSeconds": "resTime0",
            "resultTime": "time0",
            "fine": "fine0",  # пенальти
            "video": "href0"
        }
        self.db.update(self.test_result, new_result)
        result = self.db.get(new_result["userId"])
        self.assertIsNotNone(result)

        self.assertEqual(result["_id"], new_result["userId"])
        self.assertEqual(result["resultTime"], new_result["resultTime"])


class TestDbStageBestTime(unittest.TestCase, DbStageResults):
    # Функция, которая будет создавать подключение к базе данных

    def testGetTrueResult(self):
        # arrange настраиваем класс, создаем тестовые данные
        client = MockMonkClient()
        db = client['ggp']
        self.collection = db["stage_40"]
        self.collection.insert_one({"_id": "1", "resultTimeSeconds": 100, "userFullName": "Tester1"})
        self.collection.insert_one({"_id": "2", "resultTimeSeconds": 60, "userFullName": "Tester2"})
        self.collection.insert_one({"_id": "3", "resultTimeSeconds": 80, "userFullName": "Tester3"})

        # act производим действие
        test_col = self.get_bestStage_time()
        # assert производим проверку
        self.assertEqual(test_col, 60)

    def testGetTrueResult_None_Results(self):
        # arrange настраиваем класс, создаем тестовые данные
        client = MockMonkClient()
        db = client['ggp']
        self.collection = db["stage_40"]
        # act проводим проверку
        test_result = self.get_bestStage_time()
        # assert производим проверку
        self.assertIsNone(test_result)


if __name__ == "__main__":
    unittest.main()
