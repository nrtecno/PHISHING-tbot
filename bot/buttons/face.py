def handle_face_callback(bot, call):
    user_id = call.message.chat.id
    bot.answer_callback_query(call.id, "⏳ Facebook coming soon!")
    bot.edit_message_text(
        "⏳ *Facebook* is coming soon!",
        chat_id=user_id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
