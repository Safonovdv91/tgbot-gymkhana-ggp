from pymongo import MongoClient
from aio_bot import config_bot
import DB.db_obj

IP_ADRESS_MONGO_DB = config_bot.config["ip_mongo_database"]


# необходимо сделать название колекции по id_stage, а спорсменов добавлять с _id

def add_stage_result(stage_id: int, result) -> bool:
    """Функция добавления нового результата спортсмена"""
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    current_db = db_client["ggp"]
    collection = current_db[f"stage_{stage_id}"]
    print("Добавляем", result)
    collection.insert_one({
        "_id": result["userId"],
        "userFullName": result["userFullName"],
        "motorcycle": result["motorcycle"],
        "userCity": result["userCity"],
        "userCountry": result["userCountry"],
        "athleteClass": result["athleteClass"],
        "resultTimeSeconds": result["resultTimeSeconds"],
        "resultTime": result["resultTime"],
        "fine": result["fine"],  # пенальти
        "video": result["video"]
    })
    db_client.close()
    return True


def update_stage_result(stage_id: int, result) -> bool:
    """Функция добавления нового результата спортсмена"""
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    current_db = db_client["ggp"]
    collection = current_db[f"stage_{stage_id}"]
    print("Удаляем", result)
    collection.delete_one({"_id": result["userId"]})
    db_client.close()
    add_stage_result(stage_id, result)
    return True


def find_one_sportsman_from_stage(stage_id: int, userId: int):
    """Получениеданных спортсмена из этапа"""
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    current_db = db_client["ggp"]
    collection = current_db[f"stage_{stage_id}"].find_one({"_id": userId})
    db_client.close()
    return collection


def add_subscriber(user_id: int):
    """
    добавление пользователя бота в базу данных со стандартными данными
    :param user_id:
    :return:
    """
    db = DB.db_obj.DbTgUsers()
    db.add_tg_subscriber(user_id)
    db.close()


def update_subscriber(user_id: int, field: str, status):
    """
    Обновление статуса поля подпиcчика
    """
    db = DB.db_obj.DbTgUsers()
    db.update(user_id=user_id, key=field, value=status)
    db.close()

    # db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    # curent_db = db_client["users_bot"]
    # collection = curent_db["users"]
    # collection.update_one({"_id": user_id}, {"$set": {field: status}})
    # db_client.close()


def update_user_subs(user_id: int, sport_class, user_sub: str):
    """
    Функция обнавляющая список на какой подписан пользователь
    :param user_id:
    :param sport_class:
    :param user_sub:
    :return:
    """
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    curent_db = db_client["users_bot"]
    collection = curent_db["users"]
    try:
        user = collection.find_one({"_id": user_id})
        old_user_sub = user["sub_stage_cat"]
    except TypeError:
        print("Подписчик новый =)")
        add_subscriber(user_id)
        user = collection.find_one({"_id": user_id})
        old_user_sub = user["sub_stage_cat"]
    # сравниваем на какие классы подписан пользователь и действуем
    if user_sub in old_user_sub:
        old_user_sub.remove(user_sub)
        collection.update_one({
            "_id": user_id}, {"$set": {"sub_stage_cat": old_user_sub}}
        )
        del_idtg_from_subs(user_id, user_sub)
        return f"Вы успешно ОТПИСАЛИСЬ от {sport_class}"
    old_user_sub.append(user_sub)
    collection.update_one({
        "_id": user_id}, {"$set": {"sub_stage_cat": old_user_sub}}
    )

    # добавляем в список подпищщиков класса пользователя
    append_idtg_to_subs(user_id, user_sub)
    db_client.close()
    return f"Вы успешно ПОДПИСАЛИСЬ на {sport_class}"


def get_subscribers():
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    curent_db = db_client["users_bot"]
    collection = curent_db["users"]
    collection.find("")
    db_client.close()


def append_idtg_to_subs(user_tg_id: int, authleteClass: str):
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    current_db = db_client["users_bot"]
    collection = current_db["subs_class"]
    subs_ls = collection.find_one({"_id": authleteClass})
    print(f"subs_ls - {subs_ls}")
    if subs_ls is None:
        collection.insert_one({"_id": authleteClass, "id_tg_users": [user_tg_id]})
    else:
        subs_ls["id_tg_users"].append(user_tg_id)
        collection.update_one({"_id": authleteClass}, {"$set": {"id_tg_users": subs_ls["id_tg_users"]}})
    db_client.close()


def del_idtg_from_subs(user_tg_id: int, authleteClass: str):
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    current_db = db_client["users_bot"]
    collection = current_db["subs_class"]
    subs_ls = collection.find_one({"_id": authleteClass})
    print(f"subs_ls - {subs_ls}")
    subs_ls["id_tg_users"].remove(user_tg_id)
    collection.update_one({"_id": authleteClass}, {"$set": {"id_tg_users": subs_ls["id_tg_users"]}})
    db_client.close()


def get_tg_subs(authleteClass: str):
    db_client = MongoClient(IP_ADRESS_MONGO_DB, 27017)
    current_db = db_client["users_bot"]
    collection = current_db["subs_class"]
    subs_ls = collection.find_one({"_id": authleteClass})
    if subs_ls == None:
        print("NOOONE")
    subs_ls = collection.find_one({"_id": authleteClass})["id_tg_users"]
    db_client.close()
    return subs_ls


if __name__ == "__main__":
    pass
    # add_subscriber(156546)
    # get_from_stage()
    # update_user_subs(1888, "sdd", "C1")
    # append_idtg_to_subs(53, "N")
    # del_idtg_from_subs(53, "N")
    # print(get_tg_subs("C2"))
    # add_stage_result(30, {"_id": 2, "name": "test"})
    # update_stage_result(30, {"_id": 2, "name": "test2"})
