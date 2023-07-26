from pymongo import MongoClient
from pymongo import errors
from aio_bot import config_bot
from DB.models import StageSportsmanResult


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
            pass

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

    def add_tg_subscriber(self, tg_user_id):
        if self.get_tg_subscriber(tg_user_id) is None:
            self.collection.insert_one({
                "_id": tg_user_id,
                "sub_stage": False,
                "sub_stage_cat": []
            })
            return True
        return False

    def get_tg_subscriber(self, tg_user_id):
        return self.collection.find_one({"_id": tg_user_id})

    def update(self, user_id, key: str, value: str):
        """ Обновление статуса подписчика
        """
        if self.get_tg_subscriber(user_id) is None:
            return False
        self.collection.update_one({"_id": user_id}, {"$set": {key: value}})


class DbStageResults(DbMongo):
    DB_NAME = "ggp"

    def __init__(self):

        super().__init__()
        self.current_db = self.connection[self.DB_NAME]
        self.collection = self.current_db[f"stage_{config_bot.config_gymchana_cup['id_stage_now']}"]

    def add(self, result: StageSportsmanResult):
        """
        функция добалвения  новгого результата
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

    def get_bestStage_time(self):
        try:
            return self.collection.find().sort("resultTimeSeconds").limit(1)[0]["resultTimeSeconds"]
        except IndexError:
            return None
        except Exception as e:
            print(e)


class DbSubsAtheleteClass(DbMongo):
    __db_name = "users_bot"
    __collection_name = "subs_class"

    def __init__(self):
        super().__init__()
        current_db = self.connection[self.__db_name]
        self.collection = current_db[self.__collection_name]

    def get_subscriber(self, athelete_class: str):
        connect = self.collection.find_one({"_id": athelete_class})
        if connect is None:
            raise AttributeError(f"Вызване несуществующий ключ - {athelete_class}")
        return connect["id_tg_users"]

    def add_subscriber(self, athlete_class: str, tg_id: int):
        pass


def main():
    connect = DbSubsAtheleteClass()
    print(connect.get_subscriber("B"))


if __name__ == "__main__":
    main()
