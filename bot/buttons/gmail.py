def handle_gmail(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "⏳ *Gmail* is coming soon!",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )
