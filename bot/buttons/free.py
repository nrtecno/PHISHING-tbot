def handle_free_fire(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "⏳ *Free Fire* is coming soon!",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )
