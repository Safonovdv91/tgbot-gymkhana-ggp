import logging
from dataclasses import asdict

from pymongo import MongoClient, errors
from pymongo.results import DeleteResult

from aio_bot import config_bot
from DB.models import BetTimeTelegramUser, StageSportsmanResult, TelegramUser

logger = logging.getLogger(__name__)


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
            logger.exception("Инициалищзация соединения")
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

    def add_tg_subscriber(self, tg_user: TelegramUser, subs_stage=None):
        if subs_stage is None:
            subs_stage = []

        if self.get_tg_subscriber(tg_user.tg_id) is None:
            self.collection.insert_one(
                {
                    "_id": tg_user.tg_id,
                    "sub_stage": False,
                    "sub_stage_cat": subs_stage,
                    "username": tg_user.username,
                    "first_name": tg_user.first_name,
                    "full_name": tg_user.full_name,
                    "language_code": tg_user.language_code,
                }
            )

            return True
        return False

    def get_tg_subscriber(self, tg_user_id) -> dict:
        return self.collection.find_one({"_id": tg_user_id})

    def get_all_subscribers(self):
        cursor = self.collection.find()
        return cursor

    def update(self, user_id, key: str, value: str):
        """Обновление статуса подписчика"""
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
        # todo убрать хардкод!
        self.collection = self.current_db[
            f"stage_{config_bot.config_gymchana_cup['id_stage_now']}"
        ]

    def add(self, result: StageSportsmanResult):
        """
        Функция добавления новогого результата
        :param result:
        :return:
        """
        if self.collection.find_one({"_id": result.sportsman_id}):
            return False
        self.collection.insert_one(
            {
                "_id": result.sportsman_id,
                "userFullName": result.user_full_name,
                "motorcycle": result.motorcycle,
                "userCity": result.user_city,
                "userCountry": result.user_country,
                "athleteClass": result.athlete_class,
                "resultTimeSeconds": result.result_time_seconds,
                "resultTime": result.result_time,
                "fine": result.fine,  # пенальти
                "video": result.video,
            }
        )
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

    def get_best_stage_time(self) -> int | None:
        try:
            return (
                self.collection.find().sort("resultTimeSeconds").limit(1)[0]["resultTimeSeconds"]
            )
        except IndexError:
            return None
        except errors.ServerSelectionTimeoutError:
            logger.exception("get_best_stage: MongoDB TIMEOUT ")
        except Exception as e:
            logger.exception(f"get_best_stage: {e}")


class DbSubsAtheleteClass(DbMongo):
    """Работа с подписчиками для которых необходимо производить рассылку"""

    __db_name = "users_bot"
    __collection_name = "subs_class"
    ATHELETE_CLASSES = ("A", "B", "C1", "C2", "C3", "D1", "D2", "D3", "D4", "N")

    def __init__(self):
        super().__init__()
        current_db = self.connection[self.__db_name]
        self.collection = current_db[self.__collection_name]

    def get_subscriber(self, athelete_class: str) -> list:
        """Получение списка подписчика класса"""
        try:
            connect = self.collection.find_one({"_id": athelete_class})
        except Exception as e:
            logger.exception(
                f"DbSubsAtheleteClass: get_subscriber При ПОЛУЧЕНИИ подписчиков произошла ошибка:\n {e}"
            )
            raise e
        if connect is None:
            if athelete_class in self.ATHELETE_CLASSES:
                return []
            else:
                raise AttributeError(f"Вызван запрещенный ключ - {athelete_class}")
        return connect["id_tg_users"]

    def add_subscriber(self, athelete_class: str, tg_id: int) -> bool:
        """Добавление нового подписчика"""
        if athelete_class not in self.ATHELETE_CLASSES:
            logger.error("DbSubsAtheleteClass: add_subscriber Вызван запрещенный ключ")
            raise AttributeError("DbSubsAtheleteClass: add_subscriber Вызван запрещенный ключ")

        if tg_id in self.get_subscriber(athelete_class):
            raise ValueError("Пользователь уже существует")

        try:
            if self.collection.find_one({"_id": athelete_class}) is None:
                self.collection.insert_one({"_id": athelete_class, "id_tg_users": [tg_id]})
            else:
                self.collection.update_one(
                    {"_id": athelete_class}, {"$push": {"id_tg_users": tg_id}}
                )
        except Exception as e:
            logger.exception(
                f"DbSubsAtheleteClass: add_subscriber При ДОБАВЛЕНИИ подписчика произошла ошибка:\n {e}"
            )
            raise e
        return True

    def remove_subscriber(self, athelete_class: str, tg_id: int) -> bool:
        """Отписка подписчика"""
        if tg_id not in self.get_subscriber(athelete_class):
            raise ValueError(f"Пользователь {tg_id} и так не подписан на {athelete_class}")
        try:
            self.collection.update_one({"_id": athelete_class}, {"$pull": {"id_tg_users": tg_id}})
        except Exception as e:
            logger.exception(
                f"DbSubsAtheleteClass: add_subscriber При УДАЛЕНИИ подписчика произошла ошибка:\n {e}"
            )
            raise e
        return True


class DbBetTime(DbMongo):
    DB_NAME = "ggp"

    def __init__(self):
        super().__init__()
        self.current_db = self.connection[self.DB_NAME]
        # todo убрать хардкод!
        id_stage = config_bot.config_gymchana_cup["id_stage_now"]
        self.collection = self.current_db[f"bet_{id_stage}"]

    def add(self, bet_object: BetTimeTelegramUser):
        """Добавление ставки в БД"""
        if self.get(bet_object.tg_user.tg_id) is None:
            logger.info(
                "Добавляем ставку: %s[%s] на время: %s [%s]{bet_object.bet_time1}",
                bet_object.tg_user.tg_id,
                bet_object.tg_user.username,
                bet_object.bet_time1,
                bet_object.date_bet1,
            )
            self.collection.insert_one(asdict(bet_object))
            return True
        logger.info("Ставка уже есть")
        return None

    def get(self, tg_id):
        if tg_id == "all":
            list_time = []
            for db_bet in self.collection.find():
                user = TelegramUser(
                    tg_id=db_bet["tg_user"]["tg_id"],
                    username=db_bet["tg_user"]["username"],
                    first_name=db_bet["tg_user"]["first_name"],
                    full_name=db_bet["tg_user"]["full_name"],
                    language_code=db_bet["tg_user"]["language_code"],
                )
                bet = BetTimeTelegramUser(
                    tg_user=user,
                    bet_time1=db_bet["bet_time1"],
                    date_bet1=db_bet["date_bet1"],
                )
                list_time.append(bet)
            return list_time
        return self.collection.find_one({"tg_user.tg_id": tg_id})

    def remove(self, tg_id: int):
        return self.collection.delete_one({"tg_user.tg_id": tg_id})

    def get_closest_bet(self, bet_time1: int):
        from aio_bot.aio_bot_functions import BotFunction

        ls = self.get("all")
        closest_time = BotFunction.find_closest_number(ls, bet_time1)
        return self.collection.find_one({"bet_time1": closest_time})
