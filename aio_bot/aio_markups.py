from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from DB.db_obj import DbTgUsers

btnBackToMenu = KeyboardButton("⬅ НАЗАД")

# --- MAIN MENU ---
btnStageMap = KeyboardButton("Получить 🗺 этапа")
btnStageTime = KeyboardButton("Получить 🕗 этапа")
btnSubscribe = KeyboardButton("Подписаться")
btnSubscribeNews = KeyboardButton("Подписаться news")

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnSubscribe, btnStageMap, btnStageTime)

# --- Subscribe Menu ---
sub_B = KeyboardButton('🟦🇧')
sub_C1 = KeyboardButton('🟩 С1')
sub_C2 = KeyboardButton('🟩 С2')
sub_C3 = KeyboardButton('🟩 С3')
sub_D1 = KeyboardButton('🟨 D1')
sub_D2 = KeyboardButton('🟨 D2')
sub_D3 = KeyboardButton('🟨 D3')
sub_D4 = KeyboardButton('🟨 D4')

unsub_B = KeyboardButton('🔲 🇧')
unsub_C1 = KeyboardButton('🔲 С1')
unsub_C2 = KeyboardButton('🔲 С2')
unsub_C3 = KeyboardButton('🔲 С3')
unsub_D1 = KeyboardButton('🔲 D1')
unsub_D2 = KeyboardButton('🔲 D2')
unsub_D3 = KeyboardButton('🔲 D3')
unsub_D4 = KeyboardButton('🔲 D4')

subscribeMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(unsub_B, unsub_C1, unsub_C2, sub_C3, sub_D1, sub_D2,
                                                              sub_D3, sub_D4, btnBackToMenu)


class SubscriberMenu:
    @staticmethod
    def subscriber_menu_btn(tg_user_id):
        subs_ls = DbTgUsers().get_tg_subscriber(tg_user_id)
        subs_ls = [] if subs_ls is None else subs_ls["sub_stage_cat"]
        B = sub_B if "B" in subs_ls else unsub_B
        C1 = sub_C1 if "C1" in subs_ls else unsub_C1
        C2 = sub_C2 if "C2" in subs_ls else unsub_C2
        C3 = sub_C3 if "C3" in subs_ls else unsub_C3
        D1 = sub_D1 if "D1" in subs_ls else unsub_D1
        D2 = sub_D2 if "D2" in subs_ls else unsub_D2
        D3 = sub_D3 if "D3" in subs_ls else unsub_D3
        D4 = sub_D4 if "D4" in subs_ls else unsub_D4
        return ReplyKeyboardMarkup(resize_keyboard=True).add(B, C1, C2, C3, D1,
                                                             D2, D3, D4, btnBackToMenu)


# --- Subscribe to news ---

# btnSubscribeNews = InlineKeyboardMarkup(row_width=1)
# btn1 = InlineKeyboardButton(text="🟢 Подписаться на мировой рекорд", callback_data='fx1')
# btn2 = InlineKeyboardButton(text="🟢 Подписаться регистрацию этапа", callback_data='fx2')
# btn3 = InlineKeyboardButton(text="🟠 ОТПИСАТЬСЯ от мирового рекорда", callback_data='fx3')
# btn4 = InlineKeyboardButton(text="🟠 ОТПИСАТЬСЯ на регистрацию этапа", callback_data='fx4')
#
# btnSubscribeNews.add(btn1, btn2)
