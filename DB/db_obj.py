import logging

from pymongo import MongoClient
from pymongo import errors
from pymongo.results import DeleteResult
from aio_bot import config_bot
from DB.models import StageSportsmanResult, BetTimeTelegramUser, TelegramUser
from dataclasses import asdict

# from aio_bot.aio_bot_functions import BotFunction

logger = logging.getLogger("app.DB.db_obj")


class DbMongo:
    """
    Класс работы и подключения к базе данных MONGO
    """
    ipaddress = config_bot.config["ip_mongo_database"]
    port = config_bot.config["port_mongo_database"]

    def __init__(self):
        try:
            self.connection = MongoClient(self.ipaddress, self.port)
        except errors.ServerSelectionTimeoutError:
            print("catch exeption")
            raise Exception("MongoDB is TimeOut")

    def close(self):
        self.connection.close()


class DbTgUsers(DbMongo):
    """
    Класс работы с базой данных телеграмм подписчиков
    """
    __db_name = "users_bot"
    __collection_name = "users"

    def __init__(self):
        super().__init__()
        current_db = self.connection[self.__db_name]
        self.collection = current_db[self.__collection_name]

    def add_tg_subscriber(self, tg_user_id, subs_stage=None):
        if subs_stage is None:
            subs_stage = []
        if self.get_tg_subscriber(tg_user_id) is None:
            self.collection.insert_one({
                "_id": tg_user_id,
                "sub_stage": False,
                "sub_stage_cat": subs_stage
            })
            return True
        return False

    def get_tg_subscriber(self, tg_user_id) -> dict:
        return self.collection.find_one({"_id": tg_user_id})

    def get_all_subscribers(self):
        cursor = self.collection.find()
        return cursor

    def update(self, user_id, key: str, value: str):
        """ Обновление статуса подписчика
        """
        if self.get_tg_subscriber(user_id) is None:
            return False
        self.collection.update_one({"_id": user_id}, {"$set": {key: value}})

    def remove_tg_subscriber(self, tg_user_id) -> DeleteResult:
        return self.collection.delete_one({"_id": tg_user_id})


class DbStageResults(DbMongo):
    DB_NAME = "ggp"

    def __init__(self):
        super().__init__()
        self.current_db = self.connection[self.DB_NAME]
        self.collection = self.current_db[f"stage_{config_bot.config_gymchana_cup['id_stage_now']}"]

    def add(self, result: StageSportsmanResult):
        """
        Функция добавления новогого результата
        :param result:
        :return:
        """
        if self.collection.find_one({"_id": result.sportsman_id}):
            return False
        self.collection.insert_one({
            "_id": result.sportsman_id,
            "userFullName": result.user_full_name,
            "motorcycle": result.motorcycle,
            "userCity": result.user_city,
            "userCountry": result.user_country,
            "athleteClass": result.athlete_class,
            "resultTimeSeconds": result.result_time_seconds,
            "resultTime": result.result_time,
            "fine": result.fine,  # пенальти
            "video": result.video
        })
        return True

    def del_result(self, id_result: int):
        """
        Удаляет результат по id спортсмена
        :param id_result:
        :return:
        """
        self.collection.delete_one({"_id": id_result})
        return True

    def get(self, user_id: int):
        return self.collection.find_one({"_id": user_id})

    def update(self, result: dict, new_result):
        """
        Функция обновления результата
        :param result:
        :param new_result:
        :return:
        """
        if self.get(result["userId"]):
            self.del_result(result["userId"])
        self.add(new_result)

    def get_bestStage_time(self) -> int | None:
        try:
            return self.collection.find().sort("resultTimeSeconds").limit(1)[0]["resultTimeSeconds"]
        except IndexError:
            return None
        except errors.ServerSelectionTimeoutError:
            logger.exception(f"get_best_stage: MongoDB TIMEOUT ")
        except Exception as e:
            logger.exception(f"get_best_stage: {e}")


class DbSubsAtheleteClass(DbMongo):
    """ Работа с подписчиками для которых необходимо производить рассылку
    """
    __db_name = "users_bot"
    __collection_name = "subs_class"
    ATHELETE_CLASSES = ("A", "B", "C1", "C2", "C3", "D1", "D2", "D3", "D4", "N")

    def __init__(self):
        super().__init__()
        current_db = self.connection[self.__db_name]
        self.collection = current_db[self.__collection_name]

    def get_subscriber(self, athelete_class: str) -> list:
        """ Получение списка подписчика класса
        """
        try:
            connect = self.collection.find_one({"_id": athelete_class})
        except Exception as e:
            logger.exception(f"DbSubsAtheleteClass: get_subscriber При ПОЛУЧЕНИИ подписчиков произошла ошибка:\n {e}")
            raise e
        if connect is None:
            if athelete_class in self.ATHELETE_CLASSES:
                return []
            else:
                raise AttributeError(f"Вызван запрещенный ключ - {athelete_class}")
        return connect["id_tg_users"]

    def add_subscriber(self, athelete_class: str, tg_id: int) -> bool:
        """ Добавление нового подписчика
        """
        if athelete_class not in self.ATHELETE_CLASSES:
            logger.error("DbSubsAtheleteClass: add_subscriber Вызван запрещенный ключ")
            raise AttributeError("DbSubsAtheleteClass: add_subscriber Вызван запрещенный ключ")

        if tg_id in self.get_subscriber(athelete_class):
            raise ValueError("Пользователь уже существует")

        try:
            if self.collection.find_one({"_id": athelete_class}) is None:
                self.collection.insert_one({"_id": athelete_class, "id_tg_users": [tg_id]})
            else:
                self.collection.update_one({"_id": athelete_class}, {"$push": {"id_tg_users": tg_id}})
        except Exception as e:
            logger.exception(f"DbSubsAtheleteClass: add_subscriber При ДОБАВЛЕНИИ подписчика произошла ошибка:\n {e}")
            raise e
        return True

    def remove_subscriber(self, athelete_class: str, tg_id: int) -> bool:
        """ Отписка подписчика
        """
        if tg_id not in self.get_subscriber(athelete_class):
            raise ValueError(f"Пользователь {tg_id} и так не подписан на {athelete_class}")
        try:
            self.collection.update_one({"_id": athelete_class}, {"$pull": {"id_tg_users": tg_id}})
        except Exception as e:
            logger.exception(f"DbSubsAtheleteClass: add_subscriber При УДАЛЕНИИ подписчика произошла ошибка:\n {e}")
            raise e
        return True


class DbBetTime(DbMongo):
    DB_NAME = "ggp"

    def __init__(self):
        super().__init__()
        self.current_db = self.connection[self.DB_NAME]
        self.collection = self.current_db[f"bet_{config_bot.config_gymchana_cup['id_stage_now']}"]

    def add(self, bet_object: BetTimeTelegramUser):
        """ Добавление ставки в БД
        """
        if self.get(bet_object.tg_user.tg_id) is None:
            logger.info(f"Ставка user:{bet_object.tg_user.tg_id} на время {bet_object.bet_time1}")
            self.collection.insert_one(asdict(bet_object))
            return True
        logger.info("Ставка уже есть")
        return None

    def get(self, tg_id):
        if tg_id == "all":
            list_time = []
            for each in self.collection.find():
                list_time.append(each["bet_time1"])
            return list_time
        return self.collection.find_one({"tg_user.tg_id": tg_id})

    def remove(self, tg_id: int):
        return self.collection.delete_one({"tg_user.tg_id": tg_id})

    def get_closest_bet(self, bet_time1: int):
        ls = self.get("all")
        closest_time = BotFunction.find_closest_number(ls, bet_time1)
        return self.collection.find_one({"bet_time1": closest_time})


def main():
    # clients = DbTgUsers().get_all_subscribers()
    # for each in clients:
    #     if len(each["sub_stage_cat"]):
    #         print(each["_id"])

    user1 = TelegramUser(1120145735, 'novik0ff954', 'Pavel', 'Pavel Novikov', 'ru', '@novik0ff954')
    user2 = TelegramUser(987654321, 'johndoe', 'John', 'John Doe', 'en', '@johndoe')
    user3 = TelegramUser(123456789, 'alice', 'Alice', 'Alice Smith', 'en', '@alice')
    user4 = TelegramUser(555555555, 'bob', 'Bob', 'Bob Johnson', 'en', '@bob')
    user5 = TelegramUser(999999999, 'emma', 'Emma', 'Emma Thompson', 'en', '@emma')

    user1_bet = BetTimeTelegramUser(user1, 65_000)
    user2_bet = BetTimeTelegramUser(user2, 50_000)
    user3_bet = BetTimeTelegramUser(user3, 55_000)
    user4_bet = BetTimeTelegramUser(user4, 60_000)
    user5_bet = BetTimeTelegramUser(user5, 45_000)

    db_bet = DbBetTime()
    db_bet.add(user1_bet)
    db_bet.add(user2_bet)
    db_bet.add(user3_bet)
    db_bet.add(user4_bet)
    db_bet.add(user5_bet)

    print(f" winner - {db_bet.get_closest_bet(54204)}")
    print("----")
    db_bet.remove(user1_bet.tg_user.tg_id)
    db_bet.remove(user2_bet.tg_user.tg_id)
    db_bet.remove(user3_bet.tg_user.tg_id)
    db_bet.remove(user4_bet.tg_user.tg_id)
    db_bet.remove(user5_bet.tg_user.tg_id)


if __name__ == "__main__":
    main()
