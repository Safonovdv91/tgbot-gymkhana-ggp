import logging

from DB.db_obj import DbTgUsers, DbStageResults, DbSubsAtheleteClass
from DB.models import Subscriber, TelegramUser

logger = logging.getLogger("app.DB.database")


def add_stage_result(result) -> bool:
    """Функция добавления нового результата спортсмена"""
    logger.info(f"Добавляем результат {result}")
    client = DbStageResults()
    client.add(result)
    return result


def update_stage_result(result):
    """Функция добавления нового результата спортсмена"""
    logger.info(f"Обновляем результат {result}")
    client = DbStageResults()
    client.del_result(result.sportsman_id)
    add_stage_result(result)
    return result


def find_one_sportsman_from_stage(user_id: int):
    """Получение данных спортсмена из этапа"""
    db_client = DbStageResults()
    return db_client.get(user_id)


def add_subscriber(user_id: int):
    """Добавление пользователя бота в базу данных со стандартными данными"""
    db = DbTgUsers()
    db.add_tg_subscriber(user_id)
    db.close()

def update_user_subs(message, sport_class, user_sub: str):
    """ Функция обновляющая список на какой подписан пользователь
    """
    tg_user = TelegramUser(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.full_name,
        message.from_user.language_code,
        message.from_user.mention
    )

    logger.info(f"update {tg_user.tg_id} : {sport_class}")
    client = DbTgUsers()
    tg_client = client.get_tg_subscriber(tg_user.tg_id)

    subs_athelete = DbSubsAtheleteClass()

    if tg_client is None:
        """ ебанутая логика, надо чтобы пользователь был и 2 таблицах
        ---- Add ----
        """
        client.add_tg_subscriber(tg_user)
        tg_client = client.get_tg_subscriber(tg_user.tg_id)
        """ 
         продумать что юзер другого класса, либо создать общий датакласс, либо как-то объеденить их
         или вообще переделать бизнес логику
        """
        if tg_client is None:

            DbTgUsers().add_tg_subscriber(tg_user)
        tg_subscriber = Subscriber(tg_client["_id"], tg_client["sub_stage"], tg_client["sub_stage_cat"])

        client.add_tg_subscriber(tg_user,  # добавляем во вторую таблицу
                                 tg_subscriber.sub_stage_categories)
        try:
            subs_athelete.add_subscriber(
                user_sub, tg_subscriber.subscriber_id
            )  # Добавляем пользователя в рассылку
        except ValueError:
            logger.info("Не добавили т.к. уже есть")
        logger.info(f"New subscriber id: {tg_subscriber.subscriber_id} {sport_class}")
        """ --- recursion --- """
        update_user_subs(message, sport_class, user_sub)
        return "😸 You are welcome 😸"
    else:
        tg_subscriber = Subscriber(
            tg_client["_id"], tg_client["sub_stage"], tg_client["sub_stage_cat"]
        )
        if user_sub in tg_subscriber.sub_stage_categories:
            """Sub OFF"""
            tg_subscriber.sub_stage_categories.remove(user_sub)
            client.update(
                tg_subscriber.subscriber_id,
                "sub_stage_cat",
                tg_subscriber.sub_stage_categories,
            )
            try:
                subs_athelete.remove_subscriber(user_sub, tg_subscriber.subscriber_id)
            except ValueError:
                logger.error("Не удалили пользователя т.к. его нет")
            return f"Вы успешно ОТПИСАЛИСЬ от {sport_class}"

        else:
            """SUB ON"""
            tg_subscriber.sub_stage_categories.append(user_sub)
            client.update(
                tg_subscriber.subscriber_id,
                "sub_stage_cat",
                tg_subscriber.sub_stage_categories,
            )
            try:
                subs_athelete.add_subscriber(user_sub, tg_subscriber.subscriber_id)
            except ValueError:
                logger.info("Не добавили такак не добавлен")
            return f"Вы успешно ПОДПИСАЛИСЬ на {sport_class}"


if __name__ == "__main__":
    pass
