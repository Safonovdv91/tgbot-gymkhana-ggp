import random
import unittest
from DB.models import StageSportsmanResult
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


# class TestDbTgUsers(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # cls.db = DbTgUsers()
#         cls.db = Mock()
#         cls.test_user_id = random.randint(1, 10000000)
#
#     def test_add_tg_subscriber(self):
#         # Проверяем добавление нового подписчика
#         result = self.db.add_tg_subscriber(self.test_user_id)
#         self.assertTrue(result)
#
#         # Проверяем повторное добавление существующего подписчика
#         result = self.db.add_tg_subscriber(self.test_user_id)
#         self.assertFalse(result)
#
#     def test_get_tg_subscriber(self):
#         # Проверяем получение существующего подписчика
#         self.db.add_tg_subscriber(self.test_user_id)
#         subscriber = self.db.get_tg_subscriber(self.test_user_id)
#
#         self.assertIsNotNone(subscriber)
#         self.assertEqual(subscriber["_id"], self.test_user_id)
#
#         # Проверяем получение несуществующего подписчика
#         subscriber = self.db.get_tg_subscriber(1234)
#         self.assertIsNone(subscriber)


# class TestDbStageResults(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         # cls.db = DbStageResults()
#         cls.db = MockDbStage()
#         cls.test_result = {
#             "userId": 2,
#             "userFullName": "2",
#             "motorcycle": "3",
#             "userCity": "city",
#             "userCountry": "country",
#             "athleteClass": "class",
#             "resultTimeSeconds": "resTime",
#             "resultTime": 124,
#             "fine": 0,  # пенальти
#             "video": "href"
#         }
#         cls.sportsman_result = StageSportsmanResult(123, "name", "moto", "city", "count", "C1", 556, "1244", 21,
#                                                     "video")
#
#     def test_add(self):
#         " Проверяем добавление результата"
#         result = self.db.add(self.sportsman_result)
#         self.assertTrue(result)
#
#     def test_del_result(self):
#         "Проверяем удаление существующего результата"
#         result = self.db.del_result(self.test_result["userId"])
#         self.assertTrue(result)
#
#         # Проверяем удаление несуществующего результата
#         result = self.db.del_result(1234)
#         self.assertTrue(result)  # Удаление несуществующего результата также считается успешным
#
#     def test_get(self):
#         " Проверяем получение существующего результата"
#         user = self.sportsman_result
#         self.db.add(user)
#         fx = user.sportsman_id
#         self.assertEqual(self.db.get(fx), {'_id': 123,
#                                            'athleteClass': 'C1',
#                                            'fine': 21,
#                                            'motorcycle': 'moto',
#                                            'resultTime': '1244',
#                                            'resultTimeSeconds': 556,
#                                            'userCity': 'city',
#                                            'userCountry': 'count',
#                                            'userFullName': 'name',
#                                            'video': 'video'})
#
#         # Проверяем получение несуществующего результата
#         result = self.db.get(1234)
#         self.assertIsNone(result)


# class TestDbStageBestTime(unittest.TestCase, DbStageResults):
#     # Функция, которая будет создавать подключение к базе данных
#
#     def testGetTrueResult(self):
#         # arrange настраиваем класс, создаем тестовые данные
#         client = MockMonkClient()
#         db = client['ggp']
#         self.collection = db["stage_40"]
#         self.collection.insert_one({"_id": "1", "resultTimeSeconds": 100, "userFullName": "Tester1"})
#         self.collection.insert_one({"_id": "2", "resultTimeSeconds": 60, "userFullName": "Tester2"})
#         self.collection.insert_one({"_id": "3", "resultTimeSeconds": 80, "userFullName": "Tester3"})
#
#         # act производим действие
#         test_col = self.get_bestStage_time()
#         # assert производим проверку
#         self.assertEqual(test_col, 60)
#
#     def testGetTrueResult_None_Results(self):
#         # act проводим проверку
#         test_result = self.get_bestStage_time()
#         # assert производим проверку
#         self.assertIsNone(test_result)


# class TestDbSubsClass(unittest.TestCase, DbSubsAtheleteClass):
#     @classmethod
#     def setUpClass(cls):
#         cls.client = DbSubsAtheleteClass()
#         # cls.client = Mock()
#
#     def test_get_subscriber(self):
#         self.assertEqual(self.client.get_subscriber("B"), [189085044])
#
#     def test_get_subscriber_empty_list(self):
#         self.assertEqual(self.client.get_subscriber("D4"), [])
#
#     def test_get_subscriber_unknown_athelete_class(self):
#         with self.assertRaises(AttributeError):
#             self.client.get_subscriber("66")
#
#     def test_add_subscriber_to_class(self):
#         self.client.add_subscriber("C3", 666)
#         self.assertEqual(self.client.get_subscriber("C3"), [666])
#         self.client.remove_subscriber("C3", 666)
#
#     def test_add_subscriber_new_unknown_class(self):
#         with self.assertRaises(AttributeError):
#             self.client.add_subscriber("C33", 123)
#
#     def test_add_subscriber_new_class(self):
#         self.client.add_subscriber("A", 1)
#         self.assertEqual(self.client.get_subscriber("A"), [1])
#         self.client.remove_subscriber("A", 1)


if __name__ == "__main__":
    unittest.main()
