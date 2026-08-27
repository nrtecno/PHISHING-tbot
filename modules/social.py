from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def handle_social(bot, message):
    user_id = message.chat.id
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Instagram", callback_data="ig_menu"),
        InlineKeyboardButton("📘 Facebook", callback_data="fb_menu"),
        InlineKeyboardButton("🐦 Twitter", callback_data="tw_menu"),
        InlineKeyboardButton("👻 Snapchat", callback_data="snap_menu"),
        InlineKeyboardButton("⬅ Back", callback_data="back")
    )
    bot.send_message(
        user_id,
        "Choose platform:",
        reply_markup=markup
    )

def handle_social_back(bot, call):
    user_id = call.message.chat.id
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📸 Instagram", callback_data="ig_menu"),
        InlineKeyboardButton("📘 Facebook", callback_data="fb_menu"),
        InlineKeyboardButton("🐦 Twitter", callback_data="tw_menu"),
        InlineKeyboardButton("👻 Snapchat", callback_data="snap_menu"),
        InlineKeyboardButton("⬅ Back", callback_data="back")
    )
    bot.edit_message_text(
        "Choose platform:",
        chat_id=user_id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
