from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from DB.db_obj import DbTgUsers

btnBackToMenu = KeyboardButton(text="⬅ НАЗАД")
# --- buttons GGP classes ---
sub_a = KeyboardButton(text="🟥 🅰️")
sub_b = KeyboardButton(text="🟦 🇧")
sub_c1 = KeyboardButton(text="🟩 С1")
sub_c2 = KeyboardButton(text="🟩 С2")
sub_c3 = KeyboardButton(text="🟩 С3")
sub_d1 = KeyboardButton(text="🟨 D1")
sub_d2 = KeyboardButton(text="🟨 D2")
sub_d3 = KeyboardButton(text="🟨 D3")
sub_d4 = KeyboardButton(text="🟨 D4")

unsub_a = KeyboardButton(text="🔲 🅰️")
unsub_b = KeyboardButton(text="🔲 🇧")
unsub_c1 = KeyboardButton(text="🔲 С1")
unsub_c2 = KeyboardButton(text="🔲 С2")
unsub_c3 = KeyboardButton(text="🔲 С3")
unsub_d1 = KeyboardButton(text="🔲 D1")
unsub_d2 = KeyboardButton(text="🔲 D2")
unsub_d3 = KeyboardButton(text="🔲 D3")
unsub_d4 = KeyboardButton(text="🔲 D4")


# --- MAIN MENU ---
btn_stage_map = KeyboardButton(text="Получить 🗺 этапа")
btn_stage_time = KeyboardButton(text="Получить 🕗 этапа")
btn_subscribe = KeyboardButton(text="Подписаться")
btn_subscribe_news = KeyboardButton(text="Подписаться news")
btn_make_bet = KeyboardButton(text="⌚ Сделать ставку на лучшее время GGP")
main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[btn_subscribe, btn_stage_map, btn_stage_time], [btn_make_bet]],
)


class SubscriberMenu:
    @staticmethod
    def subscriber_menu_btn(tg_user_id):
        subs_ls = DbTgUsers().get_tg_subscriber(tg_user_id)
        subs_ls = [] if subs_ls is None else subs_ls["sub_stage_cat"]
        a = sub_a if "A" in subs_ls else unsub_a
        b = sub_b if "B" in subs_ls else unsub_b
        c1 = sub_c1 if "C1" in subs_ls else unsub_c1
        c2 = sub_c2 if "C2" in subs_ls else unsub_c2
        c3 = sub_c3 if "C3" in subs_ls else unsub_c3
        d1 = sub_d1 if "D1" in subs_ls else unsub_d1
        d2 = sub_d2 if "D2" in subs_ls else unsub_d2
        d3 = sub_d3 if "D3" in subs_ls else unsub_d3
        d4 = sub_d4 if "D4" in subs_ls else unsub_d4
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[a, b], [c1, c2, c3], [d1, d2, d3, d4], [btnBackToMenu]],
        )
