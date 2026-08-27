def handle_snap_callback(bot, call):
    user_id = call.message.chat.id
    bot.answer_callback_query(call.id, "⏳ Snapchat coming soon!")
    bot.edit_message_text(
        "⏳ *Snapchat* is coming soon!",
        chat_id=user_id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
