import logging

from DB.db_obj import DbTgUsers, DbStageResults, DbSubsAtheleteClass
from aio_bot import config_bot
from DB.models import Subscriber

# IP_ADDRESS_MONGO_DB = config_bot.config["ip_mongo_database"]

# необходимо сделать название колекции по id_stage, а спорсменов добавлять с _id

def add_stage_result(result) -> bool:
    """Функция добавления нового результата спортсмена"""
    client = DbStageResults()
    client.add(result)
    return result


def update_stage_result(result):
    """Функция добавления нового результата спортсмена"""
    client = DbStageResults()
    client.del_result(result.sportsman_id)
    add_stage_result(result)
    return result


def find_one_sportsman_from_stage(user_id: int):
    """Получение данных спортсмена из этапа"""
    db_client = DbStageResults()
    return db_client.get(user_id)


def add_subscriber(user_id: int):
    """ Добавление пользователя бота в базу данных со стандартными данными
    """
    db = DbTgUsers()
    db.add_tg_subscriber(user_id)
    db.close()


def update_subscriber(user_id: int, field: str, status):
    """ Обновление статуса поля подпиcчика
    ""
    db = DbTgUsers()
    db.update(user_id=user_id, key=field, value=status)
    db.close()


def update_user_subs(user_id: int, sport_class, user_sub: str):
    """ Функция обнавляющая список на какой подписан пользователь
    """
    client = DbTgUsers()
    tg_client = client.get_tg_subscriber(user_id)
    subs_athelete = DbSubsAtheleteClass()

    if tg_client is None:
        """ ебанутая логика, надо чтобы пользователь был и 2 таблицах
        ---- Add ----
        """
        client.add_tg_subscriber(user_id)
        tg_client = client.get_tg_subscriber(user_id)
        if tg_client is None:
            DbTgUsers().add_tg_subscriber(user_id)
        tg_subscriber = Subscriber(tg_client["_id"], tg_client["sub_stage"], tg_client["sub_stage_cat"])

        client.add_tg_subscriber(tg_subscriber.subscriber_id,  # добавляем во вторую таблицу
                                 tg_subscriber.sub_stage_categories)
        try:
            subs_athelete.add_subscriber(user_sub, tg_subscriber.subscriber_id)     # Добавляем пользователя в рассылку
        except ValueError:
            logging.info("Не добавили т.к. уже есть")
        logging.info(f"New subscriber id: {tg_subscriber.subscriber_id} {sport_class}")
        """ --- recursion --- """
        update_user_subs(user_id, sport_class, user_sub)
        return "You are welcome"
    else:
        tg_subscriber = Subscriber(tg_client["_id"], tg_client["sub_stage"], tg_client["sub_stage_cat"])
        if user_sub in tg_subscriber.sub_stage_categories:
            """Sub OFF"""
            tg_subscriber.sub_stage_categories.remove(user_sub)
            client.update(tg_subscriber.subscriber_id, "sub_stage_cat", tg_subscriber.sub_stage_categories)
            try:
                subs_athelete.remove_subscriber(user_sub, tg_subscriber.subscriber_id)
            except ValueError:
                logging.exception("Нехуй удалять")
            return f"Вы успешно ОТПИСАЛИСЬ от {sport_class}"

        else:
            """SUB ON"""
            tg_subscriber.sub_stage_categories.append(user_sub)
            client.update(tg_subscriber.subscriber_id, "sub_stage_cat", tg_subscriber.sub_stage_categories)
            try:
                subs_athelete.add_subscriber(user_sub, tg_subscriber.subscriber_id)
            except ValueError:
                logging.info("Нехуй добавлять")
            return f"Вы успешно ПОДПИСАЛИСЬ на {sport_class}"


if __name__ == "__main__":
    pass