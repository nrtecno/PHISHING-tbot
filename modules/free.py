def handle_free_fire(bot, message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "⏳ *Free Fire* coming soon!",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

def get_bottom_buttons():
    from bot import get_bottom_buttons
    return get_bottom_buttons()
