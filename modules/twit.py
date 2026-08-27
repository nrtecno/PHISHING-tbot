def handle_twit_callback(bot, call):
    user_id = call.message.chat.id
    bot.answer_callback_query(call.id, "⏳ Twitter coming soon!")
    bot.edit_message_text(
        "⏳ *Twitter* is coming soon!",
        chat_id=user_id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
