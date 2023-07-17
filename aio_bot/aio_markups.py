from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

btnBackToMenu = KeyboardButton("⬅ НАЗАД")

# --- MAIN MENU ---
btnStageMap = KeyboardButton("Получить 🗺 этапа")
btnStageTime = KeyboardButton("Получить 🕗 этапа")
btnSubscribe = KeyboardButton("Подписаться")
btnSubscribeNews1 = KeyboardButton("Подписаться news")

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnSubscribe, btnStageMap, btnStageTime, btnSubscribeNews1)

# --- Subscribe Menu ---
sub_B = KeyboardButton('🟦🇧')
sub_C1 = KeyboardButton('🟩 С1')
sub_C2 = KeyboardButton('🟩 С2')
sub_C3 = KeyboardButton('🟩 С3')
sub_D1 = KeyboardButton('🟨 D1')
sub_D2 = KeyboardButton('🟨 D2')
sub_D3 = KeyboardButton('🟨 D3')
sub_D4 = KeyboardButton('🟨 D4')

subscribeMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(sub_B, sub_C1, sub_C2, sub_C3, sub_D1, sub_D2,
                                                              sub_D3, sub_D4, btnBackToMenu)

# --- Subscribe to news ---

btnSubscribeNews = InlineKeyboardMarkup(row_width=1)
btn1 = InlineKeyboardButton(text="🟢 Подписаться на мировой рекорд", callback_data='fx1')
btn2 = InlineKeyboardButton(text="🟢 Подписаться регистрацию этапа", callback_data='fx2')
btn3 = InlineKeyboardButton(text="🟠 ОТПИСАТЬСЯ от мирового рекорда", callback_data='fx3')
btn4 = InlineKeyboardButton(text="🟠 ОТПИСАТЬСЯ на регистрацию этапа", callback_data='fx4')

btnSubscribeNews.add(btn1, btn2)
